from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    full = ROOT / path
    if not full.exists():
        raise AssertionError(f"missing file: {path}")
    return full.read_text(encoding="utf-8")


def assert_contains(path: str, patterns: list[str]) -> None:
    text = read(path)
    for pattern in patterns:
        if pattern not in text:
            raise AssertionError(f"{path}: missing pattern {pattern}")


assert_contains(
    "backend/app/api/routes/admin.py",
    [
        '@router.get("/master-data/create-blueprint")',
        '@router.post("/master-data/create-preview")',
        "get_admin_master_create_blueprint",
        "preview_admin_master_data_create",
        "AdminMasterDataCreatePreviewRequest",
        "admin.master_data.create_blueprint",
        "admin.master_data.create_preview",
        "createApplyReady",
        "DB를 수정하지 않습니다",
    ],
)

assert_contains(
    "backend/app/services/admin_service.py",
    [
        "MASTER_CREATE_BLUEPRINT_FIELDS",
        "get_master_create_blueprint",
        "preview_master_data_create",
        "_build_master_create_relation_options",
        "_validate_master_create_relations",
        "_describe_master_create_relation_value",
        "createApplyReady",
        "relationOptionsReturned",
        "defaultDraft",
        "comboGuards",
    ],
)

print("admin create blueprint API structure smoke test passed")
