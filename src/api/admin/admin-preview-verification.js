(function () {
  "use strict";

  const VERSION = "v255.admin-preview-browser-verification";

  const SCENARIOS = [
    {
      id: "create-ready",
      label: "정상 Create Preview",
      description: "검증 오류 없이 생성 초안이 통과한 읽기 전용 예시입니다.",
      banner: { tone: "good", title: "Create Preview 통과", subtitle: "필수값과 관계 검사를 통과했습니다.", metrics: [{ label: "적용 가능 변경", value: 2, tone: "good" }, { label: "검증 오류", value: 0, tone: "good" }] },
      badges: [{ label: "createApplyReady", value: true, tone: "good" }, { label: "dryRun", value: true, tone: "warn" }, { label: "writeBlocked", value: true, tone: "good" }],
      note: "예시 화면만 렌더링하며 API와 DB를 호출하지 않습니다.",
      payload: { unifiedDiff: [{ path: "$.code", op: "add", before: null, after: "preview_test_item" }, { path: "$.name", op: "add", before: null, after: "Preview 테스트 아이템" }] },
    },
    {
      id: "create-blocked",
      label: "오류 Create Preview",
      description: "필수 code 누락과 중복 이름으로 생성이 차단된 예시입니다.",
      banner: { tone: "blocked", title: "Create Preview 차단", subtitle: "입력값 오류를 수정해야 합니다.", metrics: [{ label: "적용 가능 변경", value: 0, tone: "blocked" }, { label: "검증 오류", value: 2, tone: "blocked" }] },
      badges: [{ label: "createApplyReady", value: false, tone: "blocked" }, { label: "dryRun", value: true, tone: "warn" }],
      warnings: ["code 필수값 누락", "name 중복"],
      payload: { unifiedDiff: [] },
    },
    {
      id: "edit-ready",
      label: "정상 Edit Preview",
      description: "현재 DB 기준값과 편집 초안이 일치해 통과한 예시입니다.",
      banner: { tone: "good", title: "Edit Preview 통과", subtitle: "현재값 기준 검사를 통과했습니다.", metrics: [{ label: "변경", value: 2, tone: "good" }, { label: "차단", value: 0, tone: "good" }] },
      badges: [{ label: "editApplyReady", value: true, tone: "good" }, { label: "stale", value: false, tone: "good" }, { label: "dryRun", value: true, tone: "warn" }],
      payload: { unifiedDiff: [{ path: "$.name", op: "replace", before: "초보자 스태프", after: "견습 마법사 스태프" }, { path: "$.attack", op: "replace", before: 10, after: 12 }] },
    },
    {
      id: "edit-stale",
      label: "stale Edit Preview",
      description: "화면을 연 뒤 DB 값이 바뀌어 오래된 초안이 차단된 예시입니다.",
      banner: { tone: "blocked", title: "Edit Preview 차단", subtitle: "현재 DB 값이 초안 기준값과 다릅니다.", metrics: [{ label: "stale 필드", value: 1, tone: "blocked" }, { label: "변경", value: 1, tone: "warn" }] },
      badges: [{ label: "editApplyReady", value: false, tone: "blocked" }, { label: "stale", value: true, tone: "blocked" }, { label: "currentMatchesBase", value: false, tone: "blocked" }],
      warnings: ["attack 현재값 불일치"],
      note: "상세를 다시 불러온 뒤 새 초안을 작성해야 합니다.",
      payload: { unifiedDiff: [{ path: "$.attack", op: "replace", before: 10, after: 12 }] },
    },
    {
      id: "rollback-ready",
      label: "정상 Rollback Preview",
      description: "현재값과 변경 이력의 적용값이 일치하고 Snapshot도 정상인 예시입니다.",
      banner: { tone: "good", title: "Rollback Preview 통과", subtitle: "현재값과 이력 기준값이 일치합니다.", metrics: [{ label: "되돌릴 변경", value: 1, tone: "good" }, { label: "불일치", value: 0, tone: "good" }] },
      badges: [{ label: "rollbackReady", value: true, tone: "good" }, { label: "currentMatchesAfter", value: true, tone: "good" }, { label: "writeBlocked", value: true, tone: "good" }],
      payload: {
        unifiedDiff: [{ path: "$.hp", op: "replace", before: 1200, after: 1000 }],
        rollbackSnapshot: { schemaVersion: 1, domain: "bosses", targetId: 7, before: { hp: 1200 }, after: { hp: 1000 }, fingerprint: "a".repeat(64) },
      },
    },
    {
      id: "snapshot-mismatch",
      label: "Snapshot 불일치",
      description: "Snapshot 기준값과 Unified Diff가 달라 UI에서 불일치로 표시되는 예시입니다.",
      banner: { tone: "blocked", title: "Rollback Preview 차단", subtitle: "Snapshot 무결성 또는 Diff 일치 여부를 확인해야 합니다.", metrics: [{ label: "되돌릴 변경", value: 1, tone: "warn" }, { label: "Snapshot 불일치", value: 1, tone: "blocked" }] },
      badges: [{ label: "rollbackReady", value: false, tone: "blocked" }, { label: "snapshotConsistent", value: false, tone: "blocked" }],
      warnings: ["snapshot/diff mismatch"],
      payload: {
        unifiedDiff: [{ path: "$.hp", op: "replace", before: 1200, after: 1000 }],
        rollbackSnapshot: { schemaVersion: 1, domain: "bosses", targetId: 7, before: { hp: 1300 }, after: { hp: 1000 }, fingerprint: "b".repeat(64) },
      },
    },
    {
      id: "delete-dependency-blocked",
      label: "삭제 dependency 차단",
      description: "다른 데이터가 대상을 참조하고 있어 삭제 Preview가 차단된 예시입니다.",
      banner: { tone: "blocked", title: "삭제 Preview 차단", subtitle: "연결된 참조 데이터를 먼저 정리해야 합니다.", metrics: [{ label: "참조", value: 3, tone: "blocked" }, { label: "삭제 가능", value: 0, tone: "blocked" }] },
      badges: [{ label: "createDeleteReady", value: false, tone: "blocked" }, { label: "dependencyBlocked", value: true, tone: "blocked" }, { label: "dryRun", value: true, tone: "warn" }],
      warnings: ["dropTableItems 3건이 대상을 참조 중"],
      payload: { unifiedDiff: [] },
    },
    {
      id: "restore-conflict",
      label: "복원 ID/code 충돌",
      description: "삭제된 row의 ID 또는 code가 이미 사용 중이라 복원이 차단된 예시입니다.",
      banner: { tone: "blocked", title: "복원 Preview 차단", subtitle: "현재 데이터와 식별자 충돌이 있습니다.", metrics: [{ label: "ID 충돌", value: 1, tone: "blocked" }, { label: "code 충돌", value: 1, tone: "blocked" }] },
      badges: [{ label: "createDeleteRestoreReady", value: false, tone: "blocked" }, { label: "idConflict", value: true, tone: "blocked" }, { label: "codeConflict", value: true, tone: "blocked" }],
      warnings: ["id=27 이미 존재", "code=preview_test_item 이미 존재"],
      payload: { unifiedDiff: [] },
    },
  ];

  function getRenderer() {
    return window.RpgAdminPreviewDiff || null;
  }

  function renderScenario(id) {
    const renderer = getRenderer();
    const target = document.querySelector("[data-admin-preview-verification-result]");
    if (!target) return false;
    const scenario = SCENARIOS.find((item) => item.id === id) || SCENARIOS[0];
    if (!renderer || typeof renderer.renderPreviewResultSummary !== "function" || typeof renderer.renderUnifiedPreviewDiff !== "function") {
      target.innerHTML = '<div class="empty">공통 Preview 렌더러를 불러오지 못했습니다.</div>';
      return false;
    }
    target.innerHTML = `
      <div class="filter-help preview-verification-safety">읽기 전용 화면 예시 · API 호출 없음 · DB 수정 없음</div>
      ${renderer.renderPreviewResultSummary(scenario.payload, {
        banner: scenario.banner,
        badges: scenario.badges,
        warnings: scenario.warnings || [],
        note: scenario.note || scenario.description,
      })}
      ${renderer.renderUnifiedPreviewDiff(scenario.payload)}
    `;
    document.querySelectorAll("[data-admin-preview-verification-scenario]").forEach((button) => {
      button.classList.toggle("primary", button.getAttribute("data-admin-preview-verification-scenario") === scenario.id);
    });
    return true;
  }

  function renderScenarioButtons() {
    const target = document.querySelector("[data-admin-preview-verification-scenarios]");
    if (!target) return false;
    target.innerHTML = SCENARIOS.map((scenario) => `
      <button class="btn mini" type="button" data-admin-preview-verification-scenario="${scenario.id}" title="${scenario.description}">${scenario.label}</button>
    `).join("");
    return true;
  }

  function bindEvents() {
    document.addEventListener("click", (event) => {
      const button = event.target.closest("[data-admin-preview-verification-scenario]");
      if (!button) return;
      renderScenario(button.getAttribute("data-admin-preview-verification-scenario"));
    });
  }

  function init() {
    const buttonsReady = renderScenarioButtons();
    if (buttonsReady) renderScenario(SCENARIOS[0].id);
    bindEvents();
  }

  function getReadiness() {
    return {
      version: VERSION,
      ok: true,
      scenarioCount: SCENARIOS.length,
      readOnlyFixtures: true,
      apiCalls: 0,
      writeOperations: 0,
      rendererReady: !!getRenderer(),
      sourceFile: "src/api/admin/admin-preview-verification.js",
    };
  }

  window.RpgAdminPreviewVerification = { VERSION, SCENARIOS, renderScenario, getReadiness };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
