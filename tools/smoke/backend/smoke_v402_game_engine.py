# ruff: noqa: E402
"""Trusted engine regression: real combat rules, slot priorities, and atomic commands.

Optional argument: a saved public master-data response. No DB or network writes.
"""

import copy
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
os.environ["DEBUG"] = "false"
sys.path.insert(0, str(ROOT / "backend"))
from app.services.game_engine import simulate, _scripts, PRELUDE
import quickjs

MASTER = (
    json.loads(Path(sys.argv.pop(1)).read_text(encoding="utf-8-sig"))["payload"]
    if len(sys.argv) > 1 and sys.argv[1].endswith(".json")
    else None
)


class Game:
    def __init__(self, player=None):
        self.now = 1_800_000_000_000
        self.state = {
            "snapshot": {"player": player or {}},
            "runtime": {},
            "rngCursor": 0,
        }
        self.command("start")

    def advance(self, ms=0, kind=None, **args):
        self.now += ms
        self.state = simulate(
            self.state["snapshot"],
            self.state["runtime"],
            MASTER,
            now_ms=self.now,
            seed="ab" * 32,
            rng_cursor=self.state["rngCursor"],
            command={"kind": kind, "args": args} if kind else None,
        )
        return self.state

    def command(self, kind, **args):
        return self.advance(kind=kind, **args)

    @property
    def player(self):
        return self.state["snapshot"]["player"]

    def item(self, kind, index=0, slotType="inv", **args):
        array = {
            "inv": "inventory",
            "equip": "equipment",
            "storage": "storage",
            "trash": "trash",
        }[slotType]
        return self.command(
            kind,
            slotType=slotType,
            index=index,
            itemId=self.player[array][index]["id"],
            **args,
        )


def normal(group, identifier, level=0, base_ilv=10):
    return {
        "id": identifier,
        "name": group + " test",
        "type": "normal",
        "equipGroup": group,
        "level": level,
        "baseIlv": base_ilv,
        "baseCost": 350,
        "enhanceStats": [100] * 21,
    }


class EngineTest(unittest.TestCase):
    def test_beginner_replaced_in_first_three_slots(self):
        for index, group in enumerate(["skill_all", "atk_inc", "normal_dmg"]):
            game = Game()
            game.command("beginner")
            game.item("equip")
            beginner = copy.deepcopy(game.player["equipment"][0])
            game.player["equipment"] = [copy.deepcopy(beginner) for _ in range(5)] + [
                None
            ] * 10
            game.player["inventory"] = [normal(group, 88)]
            result = game.item("equip")
            self.assertEqual(game.player["equipment"][index]["id"], 88)
            self.assertTrue(
                any(
                    item and item["name"] == beginner["name"]
                    for item in game.player["inventory"]
                )
            )
            self.assertTrue(result["result"]["ok"])

    def test_staff_spear_priority_and_tie(self):
        for group, dedicated in [("skill_chance", 3), ("normal_crit", 5)]:
            for low_index in [dedicated, 4]:
                game = Game()
                game.player["equipment"][dedicated] = normal(group, 101, 10)
                game.player["equipment"][4] = normal(group, 102, 10)
                game.player["equipment"][low_index]["level"] = 1
                game.player["inventory"] = [normal(group, 200)]
                result = game.item("equip")
                self.assertEqual(result["result"]["data"]["targetSlotIndex"], low_index)
            game = Game()
            game.player["equipment"][dedicated] = normal(group, 101, 10)
            game.player["equipment"][4] = normal(group, 102, 10)
            game.player["inventory"] = [normal(group, 200)]
            self.assertEqual(
                game.item("equip")["result"]["data"]["targetSlotIndex"], dedicated
            )

    def test_repair_keeps_items_and_uses_mail_when_full(self):
        staff = normal("skill_chance", 1)
        spear = normal("normal_crit", 2)
        equipment = [None] * 15
        equipment[3] = spear
        equipment[5] = staff
        game = Game({"equipment": equipment})
        self.assertEqual(game.player["equipment"][3]["id"], 1)
        self.assertEqual(game.player["equipment"][5]["id"], 2)
        equipment[3] = staff
        equipment[4] = normal("skill_chance", 3)
        equipment[5] = copy.deepcopy(staff)
        equipment[5]["id"] = 4
        game = Game(
            {
                "equipment": equipment,
                "inventory": [normal("atk_inc", 700 + i) for i in range(60)],
            }
        )
        self.assertIsNone(game.player["equipment"][5])
        self.assertEqual(game.player["mailbox"][0]["item"]["id"], 4)

    def test_enhance_deterministic_and_no_client_result(self):
        first = Game({"gold": 1000000, "inventory": [normal("skill_all", 55)]})
        second = copy.deepcopy(first)
        a = first.item("enhance", times=20)
        b = second.item("enhance", times=20)
        self.assertEqual(a, b)
        self.assertLess(first.player["gold"], 1000000)
        self.assertGreater(a["rngCursor"], 0)
        self.assertIsNotNone(a["result"]["ui"]["enhanceResult"])
        with self.assertRaises(Exception):
            first.command("enhance", slotType="inv", index=0, itemId="stale", times=20)

    def test_split_stack_gets_distinct_identity(self):
        game = Game(
            {
                "inventory": [
                    {
                        "id": 12,
                        "name": "탈리스만",
                        "type": "special_equip",
                        "isTalisman": True,
                        "specialSlotIdx": 12,
                        "level": 0,
                        "count": 5,
                    }
                ]
            }
        )
        game.item("equip")
        self.assertNotEqual(
            game.player["inventory"][0]["id"], game.player["equipment"][12]["id"]
        )
        self.assertEqual(game.player["inventory"][0]["count"], 4)

    def test_enhancement_selection_follows_split_item(self):
        stacked = {"id": 44, "name": "탈리스만", "type": "special_equip", "isTalisman": True,
                   "specialSlotIdx": 12, "level": 0, "count": 5}
        game = Game({"inventory": [stacked], "gold": 1000000})
        result = game.item("enhance", times=1)["result"]
        selection = result["data"]["selection"]
        self.assertEqual(selection["type"], "inv")
        self.assertNotEqual(selection["index"], 0)
        enhanced = game.player["inventory"][selection["index"]]
        self.assertEqual(selection["itemId"], enhanced["id"])
        self.assertNotEqual(enhanced["id"], 44)
        self.assertEqual(game.player["inventory"][0]["count"], 3)
        self.assertEqual(enhanced["level"], 1)

    def test_bundle_partial_claim_does_not_duplicate(self):
        for kind in ["mail", "mail_all"]:
            game = Game(
                {
                    "inventory": [normal("atk_inc", 1000 + i) for i in range(59)],
                    "storage": [normal("atk_inc", 2000 + i) for i in range(60)],
                    "mailbox": [
                        {
                            "id": 100,
                            "type": "bundle",
                            "items": [normal("skill_all", 2), normal("normal_dmg", 3)],
                        }
                    ],
                }
            )
            args = {"index": 0, "mailId": 100} if kind == "mail" else {}
            game.command(kind, **args)
            self.assertEqual([i["id"] for i in game.player["mailbox"][0]["items"]], [3])
            game.command(kind, **args)
            self.assertEqual(game.player["inventory"][59]["id"], 2)
            self.assertEqual(len(game.player["mailbox"][0]["items"]), 1)

    def test_minute_settlement_matches_shorter_windows(self):
        first = Game({"farmAtkBonus": 1e12})
        first.command("boss_zone")
        first.command("summon", bossId=1, special=False)
        second = copy.deepcopy(first)
        first.advance(60000)
        for _ in range(6):
            second.advance(10000)
        for game in [first, second]:
            # Acquisition timestamps/IDs are generated at each settlement time.
            for item in game.player["inventory"]:
                if item:
                    item.pop("id", None)
            game.player["records"].pop("lastUpdatedAt", None)
        self.assertEqual(first.player["gold"], second.player["gold"])
        self.assertEqual(first.player["inventory"], second.player["inventory"])
        self.assertEqual(
            first.player["records"]["totalBossKills"],
            second.player["records"]["totalBossKills"],
        )
        self.assertEqual(first.state["rngCursor"], second.state["rngCursor"])

    def test_all_bosses_can_award_equipment(self):
        ctx = quickjs.Context()
        ctx.eval(PRELUDE)
        for script in _scripts():
            ctx.eval(script)
        bosses = json.loads(
            ctx.eval(
                "JSON.stringify([...bossList,...specialBossList].map(b=>({id:b.id,special:!!b.isSpecial})))"
            )
        )
        for boss in bosses:
            game = Game(
                {"farmAtkBonus": 1e100, "maxInventorySize": 100, "maxStorageSize": 100}
            )
            game.command("boss_zone")
            game.command("summon", bossId=boss["id"], special=boss["special"])
            if boss["special"]:
                game.command("auto_special", bossId=boss["id"])
            # Exercise the award branch deterministically, including rare specials.
            # Only this test patches the host RNG; production always uses HMAC draws.
            with patch("app.services.game_engine.hmac.digest", return_value=bytes(32)):
                game.advance(1000)
            self.assertGreater(game.player["records"]["totalBossKills"], 0, boss)
            items = [
                item
                for item in game.player["inventory"] + game.player["storage"]
                if item
            ]
            self.assertTrue(items, boss)
        print(f"all bosses exercised: {len(bosses)}")


if __name__ == "__main__":
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout, verbosity=2))
