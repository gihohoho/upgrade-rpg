"""Compare generated JS seed data with the FastAPI master-data API.

Run from the `backend` folder while FastAPI is running:

    python scripts/check_master_data_parity.py

Before running this checker, make sure seed JSON has been generated from the
project root and imported into the local DB:

    # project root
    node tools/extract_seed_data.js

    # backend folder
    python scripts/setup_dev_db.py --reset --seed --verify

By default this script checks the lightweight master-data response where long
inline image assets are excluded. To also compare exact inline image strings:

    python scripts/check_master_data_parity.py --include-assets
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import urlopen

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
DEFAULT_SEED_DIR = BACKEND_DIR / "seeds" / "generated"
DEFAULT_URL = "http://127.0.0.1:8000/api/v1/game/master-data"
MAX_EXAMPLES = 10

REQUIRED_SEED_FILES = [
    "characters.json",
    "skills.json",
    "item_templates.json",
    "bosses.json",
    "field_zones.json",
    "drop_tables.json",
    "drop_table_items.json",
    "enhancement_rules.json",
]


def with_query_param(url: str, key: str, value: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query[key] = value
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_json(url: str) -> dict[str, Any]:
    with urlopen(url, timeout=10) as response:  # noqa: S310 - local dev checker only
        return json.loads(response.read().decode("utf-8"))


def to_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None



def canonical_decimal_text(value: Any) -> str | None:
    decimal_value = to_decimal(value)
    if decimal_value is None:
        return None
    if decimal_value == decimal_value.to_integral_value():
        return str(int(decimal_value))
    return format(decimal_value.normalize(), "f")

def num_equal(left: Any, right: Any) -> bool:
    left_decimal = to_decimal(left)
    right_decimal = to_decimal(right)
    if left_decimal is None or right_decimal is None:
        return left == right
    return left_decimal == right_decimal


def as_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def list_to_map(items: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {str(item.get(key)): item for item in items}


def infer_enhance_group(item: dict[str, Any]) -> str | None:
    if item.get("isTalisman") or item.get("isEmblem"):
        return "talisman_emblem"
    if item.get("type") in {"normal", "abyss", "special", "avatar"}:
        return "normal_equipment"
    return None


def compare_key_sets(report: dict[str, Any], label: str, expected: set[str], actual: set[str]) -> None:
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        report["ok"] = False
        report["failures"].append(
            {
                "area": label,
                "type": "key_set_mismatch",
                "missingInApi": missing[:MAX_EXAMPLES],
                "extraInApi": extra[:MAX_EXAMPLES],
                "missingCount": len(missing),
                "extraCount": len(extra),
            }
        )


def add_field_mismatch(
    report: dict[str, Any],
    area: str,
    code: str,
    field: str,
    expected: Any,
    actual: Any,
) -> None:
    bucket = report.setdefault("_fieldMismatchCount", Counter())
    bucket[(area, field)] += 1
    if len(report["failures"]) < 100:
        report["failures"].append(
            {
                "area": area,
                "type": "field_mismatch",
                "code": code,
                "field": field,
                "expected": expected,
                "actual": actual,
            }
        )
    report["ok"] = False


def compare_field(
    report: dict[str, Any],
    area: str,
    code: str,
    field: str,
    expected: Any,
    actual: Any,
    *,
    numeric: bool = False,
) -> None:
    if numeric:
        if not num_equal(expected, actual):
            add_field_mismatch(report, area, code, field, expected, actual)
        return
    if expected != actual:
        add_field_mismatch(report, area, code, field, expected, actual)


def expected_character_skills(characters: list[dict[str, Any]]) -> set[tuple[str, str, int]]:
    pairs: set[tuple[str, str, int]] = set()
    for character in characters:
        for index, skill_code in enumerate(character.get("skillIds") or []):
            pairs.add((character["id"], skill_code, index))
    return pairs


def expected_skill_levels(skills: list[dict[str, Any]]) -> set[tuple[str, int]]:
    rows: set[tuple[str, int]] = set()
    for skill in skills:
        max_level = int(skill.get("maxLevel") or 0)
        for level in range(0, max_level + 1):
            rows.add((skill["id"], level))
    return rows


def expected_enhancement_counts(rules: dict[str, Any]) -> tuple[int, int]:
    normal = rules.get("normalEquipment") or {}
    talisman = rules.get("talismanAndEmblem") or {}
    normal_max = int(normal.get("maxLevel") or 20)
    talisman_max = int(talisman.get("maxLevel") or 6)
    return 2, normal_max + talisman_max


def build_seed_snapshot(seed_dir: Path) -> dict[str, Any]:
    missing_files = [name for name in REQUIRED_SEED_FILES if not (seed_dir / name).exists()]
    if missing_files:
        raise FileNotFoundError(
            "Seed JSON 파일이 없습니다. 프로젝트 루트에서 먼저 `node tools/extract_seed_data.js`를 실행하세요. "
            f"missing={missing_files} seedDir={seed_dir}"
        )

    characters = load_json(seed_dir / "characters.json", [])
    skills = load_json(seed_dir / "skills.json", [])
    items = load_json(seed_dir / "item_templates.json", [])
    bosses = load_json(seed_dir / "bosses.json", [])
    field_zones = load_json(seed_dir / "field_zones.json", [])
    drop_tables = load_json(seed_dir / "drop_tables.json", [])
    drop_table_items = load_json(seed_dir / "drop_table_items.json", [])
    enhancement_rules = load_json(seed_dir / "enhancement_rules.json", {})

    enhancement_group_count, enhancement_level_count = expected_enhancement_counts(enhancement_rules)

    return {
        "characters": characters,
        "skills": skills,
        "itemTemplates": items,
        "bosses": bosses,
        "fieldZones": field_zones,
        "dropTables": drop_tables,
        "dropTableItems": drop_table_items,
        "enhancementRules": enhancement_rules,
        "counts": {
            "characters": len(characters),
            "skills": len(skills),
            "characterSkills": len(expected_character_skills(characters)),
            "skillLevels": len(expected_skill_levels(skills)),
            "itemTemplates": len(items),
            "bosses": len(bosses),
            "fieldZones": len(field_zones),
            "dropTables": len(drop_tables),
            "dropTableItems": len(drop_table_items),
            "enhancementGroups": enhancement_group_count,
            "enhancementLevels": enhancement_level_count,
        },
    }


def compare_counts(report: dict[str, Any], seed: dict[str, Any], payload: dict[str, Any]) -> None:
    api_counts = payload.get("counts") or {}
    for key, expected in seed["counts"].items():
        actual = int(api_counts.get(key) or 0)
        if actual != expected:
            report["ok"] = False
            report["failures"].append(
                {"area": "counts", "type": "count_mismatch", "key": key, "expected": expected, "actual": actual}
            )


def compare_characters(report: dict[str, Any], seed: dict[str, Any], payload: dict[str, Any], include_assets: bool) -> None:
    expected = list_to_map(seed["characters"], "id")
    actual = list_to_map(payload.get("characters") or [], "code")
    compare_key_sets(report, "characters", set(expected), set(actual))

    for code in sorted(set(expected) & set(actual)):
        left = expected[code]
        right = actual[code]
        compare_field(report, "characters", code, "name", left.get("name"), right.get("name"))
        compare_field(report, "characters", code, "description", left.get("description") or "", right.get("description"))
        compare_field(report, "characters", code, "hasImage", bool(left.get("image")), bool(right.get("hasImage")))
        if include_assets:
            compare_field(report, "characters", code, "imageUrl", left.get("image"), right.get("imageUrl"))


def compare_skills(report: dict[str, Any], seed: dict[str, Any], payload: dict[str, Any], include_assets: bool) -> None:
    expected = list_to_map(seed["skills"], "id")
    actual = list_to_map(payload.get("skills") or [], "code")
    compare_key_sets(report, "skills", set(expected), set(actual))

    for code in sorted(set(expected) & set(actual)):
        left = expected[code]
        right = actual[code]
        compare_field(report, "skills", code, "name", left.get("name"), right.get("name"))
        compare_field(report, "skills", code, "slotKey", left.get("slotKey"), right.get("slotKey"))
        compare_field(report, "skills", code, "procRate", left.get("baseProcRate"), right.get("procRate"), numeric=True)
        compare_field(report, "skills", code, "hasIcon", bool(left.get("img")), bool(right.get("hasIcon")))
        if include_assets:
            compare_field(report, "skills", code, "iconUrl", left.get("img"), right.get("iconUrl"))

    expected_levels = expected_skill_levels(seed["skills"])
    actual_levels = {(row.get("skillCode"), int(row.get("level") or 0)) for row in payload.get("skillLevels") or []}
    compare_key_sets(
        report,
        "skillLevels",
        {f"{skill_code}:{level}" for skill_code, level in expected_levels},
        {f"{skill_code}:{level}" for skill_code, level in actual_levels},
    )

    expected_pairs = expected_character_skills(seed["characters"])
    actual_pairs = {
        (row.get("characterCode"), row.get("skillCode"), int(row.get("sortOrder") or 0))
        for row in payload.get("characterSkills") or []
    }
    compare_key_sets(
        report,
        "characterSkills",
        {f"{character}:{skill}:{sort_order}" for character, skill, sort_order in expected_pairs},
        {f"{character}:{skill}:{sort_order}" for character, skill, sort_order in actual_pairs},
    )


def compare_items(report: dict[str, Any], seed: dict[str, Any], payload: dict[str, Any], include_assets: bool) -> None:
    expected = list_to_map(seed["itemTemplates"], "templateKey")
    actual = list_to_map(payload.get("itemTemplates") or [], "code")
    compare_key_sets(report, "itemTemplates", set(expected), set(actual))

    for code in sorted(set(expected) & set(actual)):
        left = expected[code]
        right = actual[code]
        item_type = left.get("type") or "unknown"
        grade = str(left.get("tier")) if left.get("tier") is not None else left.get("grade")
        equip_slot = left.get("equipGroup") or left.get("specialSlotIdx")
        compare_field(report, "itemTemplates", code, "name", left.get("name"), right.get("name"))
        compare_field(report, "itemTemplates", code, "itemType", item_type, right.get("itemType"))
        compare_field(report, "itemTemplates", code, "grade", as_string(grade), as_string(right.get("grade")))
        compare_field(report, "itemTemplates", code, "equipSlot", as_string(equip_slot), as_string(right.get("equipSlot")))
        compare_field(report, "itemTemplates", code, "enhanceGroupCode", infer_enhance_group(left), right.get("enhanceGroupCode"))
        compare_field(report, "itemTemplates", code, "hasIcon", bool(left.get("img")), bool(right.get("hasIcon")))
        if include_assets:
            compare_field(report, "itemTemplates", code, "iconUrl", left.get("img"), right.get("iconUrl"))


def compare_bosses(report: dict[str, Any], seed: dict[str, Any], payload: dict[str, Any], include_assets: bool) -> None:
    expected = {f"boss_{item['id']}": item for item in seed["bosses"]}
    actual = list_to_map(payload.get("bosses") or [], "code")
    compare_key_sets(report, "bosses", set(expected), set(actual))

    for code in sorted(set(expected) & set(actual)):
        left = expected[code]
        right = actual[code]
        compare_field(report, "bosses", code, "name", left.get("name"), right.get("name"))
        compare_field(report, "bosses", code, "bossType", "special" if left.get("isSpecial") else "normal", right.get("bossType"))
        compare_field(report, "bosses", code, "tier", left.get("id") if isinstance(left.get("id"), int) else None, right.get("tier"))
        compare_field(report, "bosses", code, "hp", left.get("maxHp"), right.get("hp"), numeric=True)
        compare_field(report, "bosses", code, "hasImage", bool(left.get("img")), bool(right.get("hasImage")))
        if include_assets:
            compare_field(report, "bosses", code, "imageUrl", left.get("img"), right.get("imageUrl"))


def compare_fields(report: dict[str, Any], seed: dict[str, Any], payload: dict[str, Any]) -> None:
    expected = {f"field_{int(item.get('level') or index + 1)}": item for index, item in enumerate(seed["fieldZones"])}
    actual = list_to_map(payload.get("fieldZones") or [], "code")
    compare_key_sets(report, "fieldZones", set(expected), set(actual))

    for code in sorted(set(expected) & set(actual)):
        left = expected[code]
        right = actual[code]
        compare_field(report, "fieldZones", code, "name", left.get("name"), right.get("name"))
        compare_field(report, "fieldZones", code, "sortOrder", int(left.get("level") or 0), int(right.get("sortOrder") or 0))
        compare_field(report, "fieldZones", code, "enemyHp", left.get("maxHp"), right.get("enemyHp"), numeric=True)
        compare_field(report, "fieldZones", code, "goldReward", left.get("goldReward"), right.get("goldReward"), numeric=True)


def compare_drop_tables(report: dict[str, Any], seed: dict[str, Any], payload: dict[str, Any]) -> None:
    expected_tables = list_to_map(seed["dropTables"], "id")
    actual_tables = list_to_map(payload.get("dropTables") or [], "code")
    compare_key_sets(report, "dropTables", set(expected_tables), set(actual_tables))

    for code in sorted(set(expected_tables) & set(actual_tables)):
        left = expected_tables[code]
        right = actual_tables[code]
        compare_field(report, "dropTables", code, "ownerCode", f"boss_{left.get('bossId')}", right.get("ownerCode"))

    expected_items = Counter(
        (
            item.get("dropTableId"),
            item.get("itemTemplateKey"),
            canonical_decimal_text(item.get("rate")),
            int(item.get("quantityMax") or item.get("quantityMin") or 1),
        )
        for item in seed["dropTableItems"]
    )
    actual_items = Counter(
        (
            item.get("dropTableCode"),
            item.get("itemTemplateCode"),
            canonical_decimal_text(item.get("rate")),
            int(item.get("maxQuantity") or item.get("minQuantity") or 1),
        )
        for item in payload.get("dropTableItems") or []
    )
    missing = list((expected_items - actual_items).elements())
    extra = list((actual_items - expected_items).elements())
    if missing or extra:
        report["ok"] = False
        report["failures"].append(
            {
                "area": "dropTableItems",
                "type": "multiset_mismatch",
                "missingInApi": missing[:MAX_EXAMPLES],
                "extraInApi": extra[:MAX_EXAMPLES],
                "missingCount": len(missing),
                "extraCount": len(extra),
            }
        )


def compare_enhancement(report: dict[str, Any], seed: dict[str, Any], payload: dict[str, Any]) -> None:
    expected_group_count, expected_level_count = expected_enhancement_counts(seed["enhancementRules"])
    actual_group_count = len(payload.get("enhancementGroups") or [])
    actual_level_count = len(payload.get("enhancementLevels") or [])
    if actual_group_count != expected_group_count:
        report["ok"] = False
        report["failures"].append(
            {
                "area": "enhancementGroups",
                "type": "count_mismatch",
                "expected": expected_group_count,
                "actual": actual_group_count,
            }
        )
    if actual_level_count != expected_level_count:
        report["ok"] = False
        report["failures"].append(
            {
                "area": "enhancementLevels",
                "type": "count_mismatch",
                "expected": expected_level_count,
                "actual": actual_level_count,
            }
        )


def finalize_report(report: dict[str, Any]) -> dict[str, Any]:
    mismatch_counter: Counter | None = report.pop("_fieldMismatchCount", None)
    if mismatch_counter:
        report["fieldMismatchSummary"] = [
            {"area": area, "field": field, "count": count}
            for (area, field), count in sorted(mismatch_counter.items())
        ]
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare generated JS seed data with FastAPI master-data API response.")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="master-data API URL")
    parser.add_argument("--seed-dir", default=str(DEFAULT_SEED_DIR), help="generated seed JSON directory")
    parser.add_argument("--include-assets", action="store_true", help="Compare the asset-included API response")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    seed_dir = Path(args.seed_dir).resolve()
    url = args.url
    if args.include_assets:
        url = with_query_param(url, "includeAssets", "true")

    try:
        seed = build_seed_snapshot(seed_dir)
    except FileNotFoundError as error:
        print(str(error))
        return 1

    try:
        response = fetch_json(url)
    except URLError as error:
        print("API 요청 실패")
        print(f"url: {url}")
        print(f"error: {error}")
        print("FastAPI 서버를 먼저 실행했는지 확인하세요: uvicorn app.main:app --reload")
        return 1

    if response.get("ok") is not True or response.get("type") != "game.master_data":
        print("master-data API 응답이 정상 형식이 아닙니다.")
        print(json.dumps(response, ensure_ascii=False, indent=2)[:5000])
        return 1

    payload = response.get("payload") or {}
    asset_policy = payload.get("assetPolicy") or {}
    if bool(asset_policy.get("includeAssets")) != bool(args.include_assets):
        print("assetPolicy.includeAssets 값이 요청 옵션과 다릅니다.")
        print(json.dumps({"url": url, "assetPolicy": asset_policy}, ensure_ascii=False, indent=2))
        return 1

    report: dict[str, Any] = {
        "ok": True,
        "url": url,
        "includeAssets": bool(args.include_assets),
        "seedDir": str(seed_dir),
        "seedCounts": seed["counts"],
        "apiCounts": payload.get("counts") or {},
        "failures": [],
    }

    compare_counts(report, seed, payload)
    compare_characters(report, seed, payload, args.include_assets)
    compare_skills(report, seed, payload, args.include_assets)
    compare_items(report, seed, payload, args.include_assets)
    compare_bosses(report, seed, payload, args.include_assets)
    compare_fields(report, seed, payload)
    compare_drop_tables(report, seed, payload)
    compare_enhancement(report, seed, payload)

    report = finalize_report(report)
    if not report["ok"]:
        print("master-data parity check failed")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    print("master-data parity check passed")
    print(json.dumps({k: report[k] for k in ["url", "includeAssets", "seedCounts", "apiCounts"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
