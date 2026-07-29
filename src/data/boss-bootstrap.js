/*
 * boss-bootstrap.js
 *
 * 보스 원본 데이터에 필요한 후처리를 적용하는 진입점입니다.
 * index.html에서 bosses.js 이후, zones.js 이전에 로드됩니다.
 *
 * 후처리 순서:
 * 1. 심연의 편린 특수 능력치 적용
 * 2. 보스/드랍 아이콘 생성
 * 3. 드랍률 보정 및 드랍 목록 확률 문구 생성
 * 4. 보스 버튼 타이틀의 단축키 문구 제거
 */

applyAbyssFragmentStats();
applyGeneratedThumbnails();
applyBossDropRates();
if (typeof applyEquipmentIconAssets === "function") applyEquipmentIconAssets();
stripBossTitleShortcuts();
