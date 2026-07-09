"""Local PostgreSQL schema + seed setup for the idle RPG backend.

Run from the `backend` folder:

    python scripts/setup_dev_db.py --reset --seed --verify

This script is for local development only. `--reset` drops the local public schema.

Why this script uses a sync DB connection:
- The FastAPI app itself uses the async SQLAlchemy/asyncpg connection.
- Local seed import is a command-line maintenance task, not a request handler.
- On Windows + Docker Desktop, asyncpg can occasionally close the connection during
  schema reset/seed operations. Using SQLAlchemy's sync psycopg driver here is more
  stable and easier to debug.
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.db.base import Base
from app.models import (  # noqa: F401 - importing registers SQLAlchemy metadata
    AdminChangeLog,
    AdminRole,
    AdminUserRole,
    Boss,
    Character,
    CharacterSkill,
    DropTable,
    DropTableItem,
    EnhancementGroup,
    EnhancementLevel,
    FieldZone,
    ItemInstance,
    ItemTemplate,
    Skill,
    SkillLevel,
    User,
    UserCharacterSkill,
    UserEquipmentSlot,
    UserInventorySlot,
    UserMailboxMessage,
    UserProfile,
    UserSaveSnapshot,
)

DEFAULT_SEED_DIR = BACKEND_DIR / "seeds" / "generated"


def to_sync_database_url(database_url: str) -> str:
    """Convert the app's async DB URL to a sync URL for CLI seed setup.

    The FastAPI app can keep using `postgresql+asyncpg://...`.
    This script uses `postgresql+psycopg://...` to avoid asyncpg connection resets
    during local schema reset and bulk seed import.
    """
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def load_json(seed_dir: Path, filename: str, default: Any) -> Any:
    path = seed_dir / filename
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def as_decimal(value: Any, default: str = "0") -> Decimal:
    if value is None:
        return Decimal(default)
    return Decimal(str(value))


def as_nullable_decimal(value: Any) -> Decimal | None:
    """Preserve missing numeric seed values as NULL instead of converting them to 0."""
    if value is None:
        return None
    return Decimal(str(value))


def seconds_from_ms(value: Any) -> int:
    if value is None:
        return 0
    return int(round(float(value) / 1000))


def upsert_stmt(table, rows: list[dict[str, Any]], index_elements: list[str]):
    """Build a PostgreSQL upsert statement for a SQLAlchemy table."""
    if not rows:
        return None
    stmt = pg_insert(table).values(rows)
    update_columns = {
        column.name: getattr(stmt.excluded, column.name)
        for column in table.columns
        if column.name not in {"id", "created_at", *index_elements}
    }
    if "updated_at" in table.columns:
        update_columns["updated_at"] = func.now()
    return stmt.on_conflict_do_update(index_elements=index_elements, set_=update_columns)


def execute_upsert(session: Session, table, rows: list[dict[str, Any]], index_elements: list[str]) -> int:
    stmt = upsert_stmt(table, rows, index_elements)
    if stmt is None:
        return 0
    session.execute(stmt)
    return len(rows)


def reset_schema(engine) -> None:
    """Drop/recreate the local public schema, then create SQLAlchemy tables."""
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
        connection.execute(text("GRANT ALL ON SCHEMA public TO public"))
        Base.metadata.create_all(bind=connection)


def create_schema(engine) -> None:
    """Create missing tables without deleting existing local data."""
    Base.metadata.create_all(bind=engine)


def build_character_rows(characters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "code": item["id"],
            "name": item.get("name") or item["id"],
            "description": item.get("description"),
            "image_url": item.get("image"),
            "is_enabled": True,
            "meta_json": {"source": "seed", "raw": item},
        }
        for item in characters
    ]


def build_skill_rows(skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in skills:
        rows.append(
            {
                "code": item["id"],
                "name": item.get("name") or item["id"],
                "slot_key": item.get("slotKey") or "",
                "description": item.get("description") or item.get("effectHtml"),
                "icon_url": item.get("img"),
                "proc_rate": as_nullable_decimal(item.get("baseProcRate")),
                "cooldown_seconds": seconds_from_ms(item.get("cooldownMs")),
                "options_json": {
                    "source": "seed",
                    "skillType": item.get("skillType"),
                    "effectHtml": item.get("effectHtml"),
                    "damageMultiplier": item.get("damageMultiplier"),
                    "bonusGroup": item.get("bonusGroup"),
                    "awakening": item.get("awakening"),
                    "raw": item,
                },
            }
        )
    return rows


def build_character_skill_rows(characters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for character in characters:
        for index, skill_code in enumerate(character.get("skillIds") or []):
            rows.append(
                {
                    "character_code": character["id"],
                    "skill_code": skill_code,
                    "sort_order": index,
                    "is_default": bool(character.get("isDefault", False)),
                }
            )
    return rows


def build_skill_level_rows(skills: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in skills:
        max_level = int(item.get("maxLevel") or 0)
        for level in range(0, max_level + 1):
            rows.append(
                {
                    "skill_code": item["id"],
                    "level": level,
                    "damage_multiplier": as_decimal(item.get("damageMultiplier")),
                    "proc_rate_bonus": Decimal("0"),
                    "options_json": {
                        "source": "seed",
                        "note": "현재 JS 구조는 레벨별 세부 계수 대신 스킬 공통 계수를 사용합니다.",
                        "level": level,
                    },
                }
            )
    return rows


def infer_enhance_group(item: dict[str, Any]) -> str | None:
    if item.get("isTalisman") or item.get("isEmblem"):
        return "talisman_emblem"
    if item.get("type") in {"normal", "abyss", "special", "avatar"}:
        return "normal_equipment"
    return None


def build_item_rows(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in items:
        item_type = item.get("type") or "unknown"
        rows.append(
            {
                "code": item["templateKey"],
                "name": item.get("name") or item["templateKey"],
                "item_type": item_type,
                "grade": str(item.get("tier")) if item.get("tier") is not None else item.get("grade"),
                "icon_url": item.get("img"),
                "description": item.get("equipText") or item.get("description"),
                "stackable": item_type in {"skillBook", "material", "consumable"},
                "equip_slot": item.get("equipGroup") or item.get("specialSlotIdx"),
                "enhance_group_code": infer_enhance_group(item),
                "base_stats_json": item.get("baseStats") or {},
                "options_json": {
                    "source": "seed",
                    "tier": item.get("tier"),
                    "equipGroup": item.get("equipGroup"),
                    "equipLimit": item.get("equipLimit"),
                    "specialSlotIdx": item.get("specialSlotIdx"),
                    "specialStats": item.get("specialStats"),
                    "sellPrice": item.get("sellPrice"),
                    "baseCost": item.get("baseCost"),
                    "baseIlv": item.get("baseIlv"),
                    "raw": item.get("raw") or item,
                },
                "admin_note": "Generated from current JS master data.",
            }
        )
    return rows


def build_boss_rows(bosses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in bosses:
        code = f"boss_{item['id']}"
        rows.append(
            {
                "code": code,
                "name": item.get("name") or code,
                "tier": int(item["id"]) if isinstance(item.get("id"), int) else None,
                "boss_type": "special" if item.get("isSpecial") else "normal",
                "hp": as_decimal(item.get("maxHp"), "1"),
                "image_url": item.get("img"),
                "description": item.get("title") or item.get("desc1"),
                "summon_rules_json": {
                    "source": "seed",
                    "title": item.get("title"),
                    "desc1": item.get("desc1"),
                    "desc2": item.get("desc2"),
                    "desc3": item.get("desc3"),
                    "reqLvl": item.get("reqLvl"),
                    "dropsList": item.get("dropsList") or [],
                    "dropRateDoubled": item.get("dropRateDoubled"),
                    "raw": item,
                },
                "cooldown_seconds": seconds_from_ms(item.get("cooldownMs")),
                "is_enabled": True,
            }
        )
    return rows


def build_field_rows(zones: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for zone in zones:
        level = int(zone.get("level") or len(rows) + 1)
        code = f"field_{level}"
        rows.append(
            {
                "code": code,
                "name": zone.get("name") or code,
                "sort_order": level,
                "enemy_hp": as_decimal(zone.get("maxHp"), "1"),
                "gold_reward": as_decimal(zone.get("goldReward")),
                "description": zone.get("enemyName") or zone.get("name"),
                "entry_rules_json": zone.get("req") or {},
                "farm_rules_json": zone.get("farm") or {},
                "is_enabled": True,
            }
        )
    return rows


def build_drop_table_rows(drop_tables: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in drop_tables:
        boss_code = f"boss_{item['bossId']}"
        rows.append(
            {
                "code": item["id"],
                "owner_type": "boss",
                "owner_code": boss_code,
                "description": item.get("title"),
                "rules_json": {"source": "seed", "raw": item},
                "is_enabled": True,
            }
        )
    return rows


def build_drop_item_rows(drop_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "drop_table_code": item["dropTableId"],
            "item_template_code": item["itemTemplateKey"],
            "rate": as_decimal(item.get("rate")),
            "min_quantity": int(item.get("quantityMin") or 1),
            "max_quantity": int(item.get("quantityMax") or item.get("quantityMin") or 1),
            "conditions_json": {
                "source": "seed",
                "bossId": item.get("bossId"),
                "sortOrder": item.get("sortOrder"),
                "raw": item.get("raw") or item,
            },
        }
        for item in drop_items
    ]


def build_enhancement_rows(rules: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups: list[dict[str, Any]] = []
    levels: list[dict[str, Any]] = []

    normal = rules.get("normalEquipment") or {}
    normal_max = int(normal.get("maxLevel") or 20)
    groups.append(
        {
            "code": "normal_equipment",
            "name": "일반 장비 강화",
            "description": "일반 장비/심연 장비 강화 규칙",
            "max_level": normal_max,
            "rules_json": {"source": "seed", "raw": normal},
            "is_enabled": True,
        }
    )
    for row in normal.get("successRatesByCurrentLevel") or []:
        level = int(row.get("level") or 0)
        if level >= normal_max:
            continue
        levels.append(
            {
                "group_code": "normal_equipment",
                "from_level": level,
                "to_level": level + 1,
                "success_rate": as_decimal(row.get("successRate")),
                "gold_cost": Decimal("0"),
                "material_rules_json": {},
                "result_stats_json": {
                    "statProgression": (normal.get("statProgression") or [None])[level + 1]
                    if level + 1 < len(normal.get("statProgression") or [])
                    else {},
                    "curveAtkInc": (normal.get("curveAtkInc") or [None])[level + 1]
                    if level + 1 < len(normal.get("curveAtkInc") or [])
                    else None,
                    "curveSmult": (normal.get("curveSmult") or [None])[level + 1]
                    if level + 1 < len(normal.get("curveSmult") or [])
                    else None,
                    "extraSmult": (normal.get("extraSmult") or [None])[level + 1]
                    if level + 1 < len(normal.get("extraSmult") or [])
                    else None,
                },
                "fail_rules_json": {"source": "seed", "note": "현재 실패 시 강화 레벨 하락 없음"},
            }
        )

    talisman = rules.get("talismanAndEmblem") or {}
    talisman_max = int(talisman.get("maxLevel") or 6)
    groups.append(
        {
            "code": "talisman_emblem",
            "name": "탈리스만/빛나는 휘장 강화",
            "description": "0강 동일 아이템 재료를 사용해 강화하는 규칙",
            "max_level": talisman_max,
            "rules_json": {"source": "seed", "raw": talisman},
            "is_enabled": True,
        }
    )
    for level in range(0, talisman_max):
        levels.append(
            {
                "group_code": "talisman_emblem",
                "from_level": level,
                "to_level": level + 1,
                "success_rate": Decimal("0"),
                "gold_cost": Decimal("0"),
                "material_rules_json": {
                    "rule": talisman.get("materialRule"),
                    "costFormula": talisman.get("materialCostFormula"),
                    "currentLevel": level,
                },
                "result_stats_json": {},
                "fail_rules_json": {"source": "seed", "note": "세부 확률은 다음 DB화 단계에서 확정"},
            }
        )
    return groups, levels


def build_admin_roles() -> list[dict[str, Any]]:
    return [
        {
            "code": "super_admin",
            "name": "최고 관리자",
            "permissions_json": {"domains": ["*"], "actions": ["read", "create", "update", "delete", "rollback"]},
            "is_enabled": True,
        },
        {
            "code": "balance_admin",
            "name": "밸런스 관리자",
            "permissions_json": {
                "domains": ["characters", "skills", "items", "bosses", "drop_tables", "field_zones", "enhancement_rules"],
                "actions": ["read", "create", "update"],
            },
            "is_enabled": True,
        },
    ]


def import_seed_data(session: Session, seed_dir: Path) -> dict[str, int]:
    characters = load_json(seed_dir, "characters.json", [])
    skills = load_json(seed_dir, "skills.json", [])
    items = load_json(seed_dir, "item_templates.json", [])
    bosses = load_json(seed_dir, "bosses.json", [])
    fields = load_json(seed_dir, "field_zones.json", [])
    drop_tables = load_json(seed_dir, "drop_tables.json", [])
    drop_items = load_json(seed_dir, "drop_table_items.json", [])
    enhancement = load_json(seed_dir, "enhancement_rules.json", {})

    enhancement_groups, enhancement_levels = build_enhancement_rows(enhancement)

    counts: dict[str, int] = {}
    counts["characters"] = execute_upsert(session, Character.__table__, build_character_rows(characters), ["code"])
    counts["skills"] = execute_upsert(session, Skill.__table__, build_skill_rows(skills), ["code"])
    counts["character_skills"] = execute_upsert(
        session, CharacterSkill.__table__, build_character_skill_rows(characters), ["character_code", "skill_code"]
    )
    counts["skill_levels"] = execute_upsert(session, SkillLevel.__table__, build_skill_level_rows(skills), ["skill_code", "level"])
    counts["enhancement_groups"] = execute_upsert(session, EnhancementGroup.__table__, enhancement_groups, ["code"])
    counts["enhancement_levels"] = execute_upsert(session, EnhancementLevel.__table__, enhancement_levels, ["group_code", "from_level"])
    counts["item_templates"] = execute_upsert(session, ItemTemplate.__table__, build_item_rows(items), ["code"])
    counts["bosses"] = execute_upsert(session, Boss.__table__, build_boss_rows(bosses), ["code"])
    counts["field_zones"] = execute_upsert(session, FieldZone.__table__, build_field_rows(fields), ["code"])
    counts["drop_tables"] = execute_upsert(session, DropTable.__table__, build_drop_table_rows(drop_tables), ["code"])

    # drop_table_items has no natural unique constraint in the first draft. For local setup, clear and reinsert.
    session.execute(text("DELETE FROM drop_table_items"))
    if drop_items:
        session.execute(DropTableItem.__table__.insert(), build_drop_item_rows(drop_items))
    counts["drop_table_items"] = len(drop_items)

    counts["admin_roles"] = execute_upsert(session, AdminRole.__table__, build_admin_roles(), ["code"])
    return counts


def verify_counts(session: Session) -> dict[str, int]:
    tables = {
        "characters": Character,
        "skills": Skill,
        "character_skills": CharacterSkill,
        "skill_levels": SkillLevel,
        "item_templates": ItemTemplate,
        "bosses": Boss,
        "field_zones": FieldZone,
        "drop_tables": DropTable,
        "drop_table_items": DropTableItem,
        "enhancement_groups": EnhancementGroup,
        "enhancement_levels": EnhancementLevel,
        "users": User,
        "user_save_snapshots": UserSaveSnapshot,
        "admin_roles": AdminRole,
        "admin_user_roles": AdminUserRole,
        "admin_change_logs": AdminChangeLog,
    }
    counts: dict[str, int] = {}
    for name, model in tables.items():
        result = session.execute(select(func.count()).select_from(model))
        counts[name] = int(result.scalar_one())
    return counts


def dry_run_summary(seed_dir: Path) -> dict[str, int]:
    summary = {
        "characters": len(load_json(seed_dir, "characters.json", [])),
        "skills": len(load_json(seed_dir, "skills.json", [])),
        "items": len(load_json(seed_dir, "item_templates.json", [])),
        "bosses": len(load_json(seed_dir, "bosses.json", [])),
        "field_zones": len(load_json(seed_dir, "field_zones.json", [])),
        "drop_tables": len(load_json(seed_dir, "drop_tables.json", [])),
        "drop_table_items": len(load_json(seed_dir, "drop_table_items.json", [])),
    }
    enhancement = load_json(seed_dir, "enhancement_rules.json", {})
    groups, levels = build_enhancement_rows(enhancement)
    summary["enhancement_groups"] = len(groups)
    summary["enhancement_levels"] = len(levels)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up local DB schema and import generated seed data.")
    parser.add_argument("--seed-dir", default=str(DEFAULT_SEED_DIR), help="Seed JSON directory")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate the local public schema")
    parser.add_argument("--create-schema", action="store_true", help="Create missing tables without dropping existing data")
    parser.add_argument("--seed", action="store_true", help="Import generated seed JSON into PostgreSQL")
    parser.add_argument("--verify", action="store_true", help="Print table counts after setup")
    parser.add_argument("--dry-run", action="store_true", help="Load seed JSON and print expected counts without DB access")
    parser.add_argument("--verbose-sql", action="store_true", help="Print raw SQL logs while running this script")
    args = parser.parse_args()

    seed_dir = Path(args.seed_dir).resolve()
    if args.dry_run:
        print(json.dumps({"seedDir": str(seed_dir), "counts": dry_run_summary(seed_dir)}, ensure_ascii=False, indent=2))
        return

    sync_database_url = to_sync_database_url(settings.database_url)
    # Keep SQL echo off by default. Seed rows can include very long SVG data URLs,
    # so raw SQL logs become huge and make the real error hard to read.
    engine = create_engine(sync_database_url, echo=args.verbose_sql, future=True, pool_pre_ping=True)

    try:
        if args.reset:
            print("Resetting local public schema...")
            reset_schema(engine)
        elif args.create_schema:
            print("Creating missing tables...")
            create_schema(engine)

        with Session(engine) as session:
            if args.seed:
                print(f"Importing seed data from {seed_dir} ...")
                with session.begin():
                    imported = import_seed_data(session, seed_dir)
                print(json.dumps({"imported": imported}, ensure_ascii=False, indent=2))
            if args.verify:
                counts = verify_counts(session)
                print(json.dumps({"tableCounts": counts}, ensure_ascii=False, indent=2))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
