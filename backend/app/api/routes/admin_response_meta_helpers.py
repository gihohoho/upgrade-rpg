from __future__ import annotations

from typing import Any

_ADMIN_ROUTE_META: dict[str, dict[str, Any]] = {
    "overview": {
        "source": "postgresql",
        "note": "관리자 페이지 준비용 읽기 전용 overview API입니다. DB를 수정하지 않습니다.",
    },
    "master_domains": {
        "source": "postgresql",
        "note": "관리자 마스터 데이터 카탈로그 도메인 목록입니다. DB를 수정하지 않습니다.",
    },
    "master_catalog": {
        "source": "postgresql",
        "note": "관리자 마스터 데이터 카탈로그 조회 전용 목록입니다. 원본 JSON과 이미지 data URL은 내려주지 않습니다.",
    },
    "master_create_blueprint": {
        "source": "postgresql",
        "note": "관리자 신규 row 생성 준비용 blueprint입니다. 일부 제한 도메인만 dev key와 확인 문구로 생성 적용 가능합니다.",
    },
    "master_create_preview": {
        "source": "postgresql",
        "note": "관리자 신규 row 생성 초안 검증 전용입니다. 이 API 자체는 DB를 수정하지 않고, 제한 도메인의 apply 가능 여부만 알려줍니다.",
    },
    "master_create_apply": {
        "source": "postgresql",
        "note": "관리자 신규 row 생성 적용 API입니다. X-Admin-Dev-Key, 확인 문구, create allow-list를 통과한 제한 도메인만 DB에 insert합니다.",
    },
    "master_detail": {
        "source": "postgresql",
        "note": "관리자 마스터 데이터 상세 조회 전용입니다. DB를 수정하지 않고, 이미지 data URL은 숨깁니다.",
    },
    "master_relations": {
        "source": "postgresql",
        "note": "관리자 마스터 데이터 연결 항목 조회 전용입니다. 관련 행도 축약된 목록만 내려줍니다.",
    },
    "master_edit_preview": {
        "source": "postgresql",
        "note": "관리자 마스터 데이터 편집 초안 검증 전용입니다. DB를 수정하지 않습니다.",
    },
    "master_edit_apply": {
        "source": "postgresql",
        "note": "관리자 마스터 데이터 변경 적용 API입니다. X-Admin-Dev-Key, 확인 문구, allow-list를 통과한 스칼라 필드만 DB에 반영합니다.",
    },
    "change_logs": {
        "source": "postgresql",
        "note": "관리자 변경 이력 읽기 전용 목록입니다. before/after JSON 원본은 내려주지 않습니다.",
    },
    "change_log_detail": {
        "source": "postgresql",
        "note": "관리자 변경 이력 상세 조회입니다. before/after 전체 JSON 원본 대신 스칼라 변경 행만 내려줍니다.",
    },
    "create_delete_preview": {
        "source": "postgresql",
        "note": "관리자 create 이력의 생성 row 삭제 되돌리기 미리보기입니다. 현재값과 연결 데이터 검사를 통과해야만 apply가 가능합니다.",
    },
    "create_delete_apply": {
        "source": "postgresql",
        "note": "관리자 create 이력의 생성 row 삭제 적용 API입니다. X-Admin-Dev-Key, 확인 문구, 현재값/연결 데이터 검사를 통과한 경우에만 DB에서 삭제합니다.",
    },
    "create_delete_restore_preview": {
        "source": "postgresql",
        "note": "관리자 create_delete 이력의 삭제 row 복원 미리보기입니다. id/code 충돌과 생성 검증을 통과해야만 apply가 가능합니다.",
    },
    "create_delete_restore_apply": {
        "source": "postgresql",
        "note": "관리자 create_delete 이력의 삭제 row 복원 적용 API입니다. X-Admin-Dev-Key, 확인 문구, id/code 충돌 검사를 통과한 경우에만 DB에 다시 생성합니다.",
    },
    "rollback_preview": {
        "source": "postgresql",
        "note": "관리자 변경 이력 되돌리기 미리보기입니다. 현재 DB 값이 이력의 after 값과 일치할 때만 rollbackReady가 true가 됩니다.",
    },
    "rollback_apply": {
        "source": "postgresql",
        "note": "관리자 변경 이력 되돌리기 적용 API입니다. X-Admin-Dev-Key, 확인 문구, 현재값 검사를 통과한 경우에만 DB에 반영합니다.",
    },
    "save_snapshots": {
        "source": "postgresql",
        "note": "관리자 페이지 준비용 세이브 스냅샷 읽기 전용 목록입니다. snapshot_json 원본은 내려주지 않습니다.",
    },
    "change_preview": {
        "note": "관리자 변경 미리보기 API 초안입니다. 아직 DB를 수정하지 않습니다.",
    },
}


def admin_route_meta(key: str) -> dict[str, Any]:
    """Return a copy of stable admin route metadata by key."""
    try:
        return dict(_ADMIN_ROUTE_META[key])
    except KeyError as exc:  # pragma: no cover - static route key typo guard
        raise KeyError(f"unknown admin route meta key: {key}") from exc
