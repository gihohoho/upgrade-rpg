"""Check the local master-data API response.

Run from the `backend` folder while FastAPI is running:

    python scripts/check_master_data_api.py

Default check uses the lightweight response, where long SVG/data URL assets are
not included. To check the asset-included response:

    python scripts/check_master_data_api.py --include-assets

Optional custom URL:

    python scripts/check_master_data_api.py http://127.0.0.1:8000/api/v1/game/master-data
"""

from __future__ import annotations

import json
import sys
from typing import Any
from urllib.error import URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import urlopen

DEFAULT_URL = "http://127.0.0.1:8000/api/v1/game/master-data"
REQUIRED_PAYLOAD_KEYS = [
    "characters",
    "skills",
    "characterSkills",
    "skillLevels",
    "itemTemplates",
    "bosses",
    "fieldZones",
    "dropTables",
    "dropTableItems",
    "enhancementGroups",
    "enhancementLevels",
    "enhancementRules",
    "assetPolicy",
    "counts",
]
EXPECTED_MINIMUM_COUNTS = {
    "characters": 1,
    "skills": 8,
    "itemTemplates": 245,
    "bosses": 45,
    "fieldZones": 40,
    "dropTables": 45,
    "dropTableItems": 245,
    "enhancementGroups": 2,
    "enhancementLevels": 26,
}
ASSET_MARKERS = [
    "data:image/svg+xml",
    "data:image/png",
    "data:image/jpeg",
    "data:image/webp",
]


def with_query_param(url: str, key: str, value: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query[key] = value
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def parse_args(argv: list[str]) -> tuple[str, bool]:
    include_assets = False
    url = DEFAULT_URL
    for arg in argv[1:]:
        if arg == "--include-assets":
            include_assets = True
        elif arg in {"-h", "--help"}:
            print(__doc__)
            raise SystemExit(0)
        else:
            url = arg
    if include_assets:
        url = with_query_param(url, "includeAssets", "true")
    return url, include_assets


def fetch_json(url: str) -> tuple[dict[str, Any], str]:
    with urlopen(url, timeout=10) as response:  # noqa: S310 - local dev checker only
        raw = response.read().decode("utf-8")
    return json.loads(raw), raw


def main() -> int:
    url, include_assets = parse_args(sys.argv)
    try:
        response, raw_response = fetch_json(url)
    except URLError as error:
        print("API 요청 실패")
        print(f"url: {url}")
        print(f"error: {error}")
        print("FastAPI 서버를 먼저 실행했는지 확인하세요: uvicorn app.main:app --reload")
        return 1

    if response.get("ok") is not True:
        print("API 응답 ok 값이 true가 아닙니다.")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 1

    if response.get("type") != "game.master_data":
        print("API type이 game.master_data가 아닙니다.")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return 1

    payload = response.get("payload") or {}
    missing_keys = [key for key in REQUIRED_PAYLOAD_KEYS if key not in payload]
    if missing_keys:
        print("payload에 필요한 키가 없습니다.")
        print(json.dumps({"missingKeys": missing_keys}, ensure_ascii=False, indent=2))
        return 1

    asset_policy = payload.get("assetPolicy") or {}
    if bool(asset_policy.get("includeAssets")) != include_assets:
        print("assetPolicy.includeAssets 값이 요청 옵션과 다릅니다.")
        print(json.dumps({"requestedIncludeAssets": include_assets, "assetPolicy": asset_policy}, ensure_ascii=False, indent=2))
        return 1

    if not include_assets and any(marker in raw_response for marker in ASSET_MARKERS):
        print("기본 master-data 응답에 긴 data URL 이미지 문자열이 포함되어 있습니다.")
        print("백신 오탐을 줄이려면 기본 응답에서는 iconUrl/imageUrl이 null이어야 합니다.")
        return 1

    counts = payload.get("counts") or {}
    too_small = {
        key: {"actual": counts.get(key), "expectedMinimum": minimum}
        for key, minimum in EXPECTED_MINIMUM_COUNTS.items()
        if int(counts.get(key) or 0) < minimum
    }
    if too_small:
        print("마스터 데이터 개수가 예상보다 적습니다. seed import를 다시 확인하세요.")
        print(json.dumps(too_small, ensure_ascii=False, indent=2))
        return 1

    print("master-data API check passed")
    print(json.dumps({"url": url, "includeAssets": include_assets, "counts": counts}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
