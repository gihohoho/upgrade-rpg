(function () {
  "use strict";

  const VERSION = "v258.admin-workspace-navigation";
  const ADMIN_WORKSPACE_MODES = [
    {
      key: "lookup",
      label: "조회·상세 확인",
      badge: "가장 먼저",
      summary: "마스터 데이터 목록에서 원하는 도메인과 row를 찾고, 상세/관계/API 반영 상태를 확인합니다.",
      primarySectionId: "section-master-catalog",
      sections: ["section-overview", "section-master-counts", "section-master-catalog", "section-master-detail"],
      steps: [
        "API URL이 127.0.0.1:8000 또는 현재 백엔드 주소인지 확인합니다.",
        "마스터 데이터 카탈로그에서 도메인과 검색어를 선택합니다.",
        "행의 보기 버튼을 눌러 상세와 relation 정보를 확인합니다.",
        "필요하면 상세 영역의 API 확인 버튼으로 실제 master-data 반영 상태만 확인합니다."
      ],
      safety: ["조회 중심 모드입니다.", "저장/삭제/복원은 실행하지 않습니다.", "상세를 열어도 DB 값은 바뀌지 않습니다."],
      buttons: ["카탈로그 필터 적용", "보기", "API 확인"]
    },
    {
      key: "create",
      label: "신규 row 생성",
      badge: "Preview 먼저",
      summary: "새 row를 만들 때 필요한 필드와 relation 후보를 확인하고, Preview 결과를 본 뒤 제한 적용 여부를 판단합니다.",
      primarySectionId: "section-create-blueprint",
      sections: ["section-create-blueprint", "section-create-lifecycle-guide", "section-preview-verification"],
      steps: [
        "생성할 도메인을 고르고 생성 설계 불러오기를 누릅니다.",
        "필수 필드와 기본값, relation 후보를 먼저 확인합니다.",
        "Create Preview로 검증 오류와 Diff를 확인합니다.",
        "실제 적용은 dev key와 확인 문구가 필요한 제한 도메인에서만 진행합니다."
      ],
      safety: ["Preview만으로는 DB가 바뀌지 않습니다.", "지원하지 않는 도메인은 insert API locked 상태로 유지됩니다.", "확인 문구 없이 실제 적용되지 않습니다."],
      buttons: ["생성 설계 불러오기", "Create Preview", "제한 적용"]
    },
    {
      key: "edit",
      label: "편집·적용 검토",
      badge: "stale 확인",
      summary: "선택한 row의 허용 필드만 수정하고, stale guard와 Preview Diff를 거친 뒤 안전하게 적용합니다.",
      primarySectionId: "section-master-detail",
      sections: ["section-master-catalog", "section-master-detail", "section-field-help", "section-admin-write-guard"],
      steps: [
        "마스터 데이터 카탈로그에서 수정할 row를 보기로 엽니다.",
        "허용 필드만 입력하고 잠긴 필드는 변경하지 않습니다.",
        "Edit Preview로 변경 전/후 Diff와 stale 여부를 확인합니다.",
        "적용 전 dev key, reason, confirmText를 다시 확인합니다."
      ],
      safety: ["허용 필드 외 JSON/이미지/관계 변경은 계속 잠겨 있습니다.", "DB 값이 바뀐 stale 상태면 적용이 차단됩니다.", "Preview 단계에서는 write가 실행되지 않습니다."],
      buttons: ["보기", "Edit Preview", "제한 적용"]
    },
    {
      key: "preview",
      label: "Preview 화면 점검",
      badge: "DB 변경 없음",
      summary: "실제 작업 전에 성공·차단·stale·Snapshot 불일치 화면이 정상적으로 보이는지 확인합니다.",
      primarySectionId: "section-preview-verification",
      sections: ["section-preview-verification", "section-admin-js-split-readiness", "section-readiness"],
      steps: [
        "위쪽 8개 고정 예시 버튼으로 화면 표시 상태를 비교합니다.",
        "필요한 입력 화면을 연 뒤 실제 Preview API 버튼을 누릅니다.",
        "응답 JSON, 상태 배너, Diff, Snapshot 정보가 같은 공통 UI로 표시되는지 확인합니다.",
        "Network 탭에서 apply/save/delete/restore 요청이 없는지 확인할 수 있습니다."
      ],
      safety: ["fixture 버튼은 API 호출 0회입니다.", "Live 버튼도 Preview API만 호출합니다.", "apply 계열 함수와 confirmText를 사용하지 않습니다."],
      buttons: ["정상 Create Preview", "Rollback Preview API", "Snapshot 불일치"]
    },
    {
      key: "rollback",
      label: "변경 이력·Rollback",
      badge: "Snapshot 비교",
      summary: "적용된 변경 이력을 확인하고, 현재값과 Snapshot이 일치할 때만 되돌리기 Preview를 검토합니다.",
      primarySectionId: "section-change-logs",
      sections: ["section-change-logs", "section-preview-verification", "section-admin-write-guard"],
      steps: [
        "관리자 변경 이력에서 target/action/applied 필터로 이력을 좁힙니다.",
        "보기 버튼으로 before/after 스칼라 변경값을 확인합니다.",
        "Rollback Preview에서 currentMatchesAfter와 snapshot match를 확인합니다.",
        "실제 되돌리기는 dev key와 확인 문구가 있을 때만 가능합니다."
      ],
      safety: ["현재 DB 값이 이력의 after 값과 다르면 rollback은 차단됩니다.", "Snapshot fingerprint가 다르면 restore payload 생성이 차단됩니다.", "Preview는 DB를 변경하지 않습니다."],
      buttons: ["이력 필터 적용", "보기", "Rollback Preview"]
    }
  ];

  const SECONDARY_SECTION_IDS = [
    "section-field-help",
    "section-admin-write-guard",
    "section-admin-js-split-readiness",
    "section-save-snapshots",
    "section-save-snapshot-summary",
    "section-readiness"
  ];

  let activeModeKey = "";

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function getModeByKey(key) {
    return ADMIN_WORKSPACE_MODES.find((mode) => mode.key === key) || null;
  }

  function getSectionById(id) {
    return id ? document.getElementById(id) : null;
  }

  function setSectionCollapsedById(id, collapsed) {
    const section = getSectionById(id);
    if (!section) return false;
    if (typeof window.setAdminSectionCollapsed === "function" && section.hasAttribute("data-admin-collapsible")) {
      window.setAdminSectionCollapsed(section, !!collapsed);
      return true;
    }
    section.classList.toggle("admin-section-collapsed", !!collapsed);
    return true;
  }

  function clearModeTargets() {
    document.querySelectorAll(".admin-workspace-mode-target").forEach((section) => {
      section.classList.remove("admin-workspace-mode-target");
    });
  }

  function markModeTargets(mode) {
    clearModeTargets();
    (mode.sections || []).forEach((id) => {
      const section = getSectionById(id);
      if (section) section.classList.add("admin-workspace-mode-target");
    });
  }

  function updateActiveButtons(modeKey) {
    document.querySelectorAll("[data-admin-workspace-mode]").forEach((button) => {
      const active = button.getAttribute("data-admin-workspace-mode") === modeKey;
      button.classList.toggle("active", active);
      if (active) button.setAttribute("aria-current", "true");
      else button.removeAttribute("aria-current");
    });
  }

  function updateWorkspaceStatus(mode) {
    const target = document.querySelector("[data-admin-workspace-status]");
    if (!target) return false;
    if (!mode) {
      target.textContent = "전체 보기 · 모든 섹션을 직접 확인할 수 있습니다.";
      return true;
    }
    target.textContent = `${mode.label} 모드 · ${mode.sections.length}개 관련 섹션을 펼쳤습니다.`;
    return true;
  }

  function scrollToModePrimary(mode) {
    const section = getSectionById(mode && mode.primarySectionId);
    if (!section) return false;
    try {
      section.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (_) {
      window.location.hash = `#${mode.primarySectionId}`;
    }
    if (typeof window.setAdminActiveSidebarLink === "function") window.setAdminActiveSidebarLink(`#${mode.primarySectionId}`);
    return true;
  }

  function setWorkspaceMode(modeKey, options) {
    const mode = getModeByKey(modeKey);
    if (!mode) return false;
    activeModeKey = mode.key;
    const targetIds = new Set(mode.sections || []);
    document.body.classList.add("admin-workspace-focus-active");
    markModeTargets(mode);
    document.querySelectorAll("[data-admin-collapsible]").forEach((section) => {
      const id = section.id;
      setSectionCollapsedById(id, !targetIds.has(id));
    });
    updateActiveButtons(mode.key);
    updateWorkspaceStatus(mode);
    if (!options || options.scroll !== false) scrollToModePrimary(mode);
    if (!options || options.modal !== false) openWorkspaceModal(mode.key);
    return true;
  }

  function showAllWorkspaceSections() {
    activeModeKey = "";
    document.body.classList.remove("admin-workspace-focus-active");
    clearModeTargets();
    document.querySelectorAll("[data-admin-collapsible]").forEach((section) => setSectionCollapsedById(section.id, false));
    updateActiveButtons("");
    updateWorkspaceStatus(null);
    return true;
  }

  function collapseQuietSections() {
    SECONDARY_SECTION_IDS.forEach((id) => setSectionCollapsedById(id, true));
    const status = document.querySelector("[data-admin-workspace-status]");
    if (status) status.textContent = "보조 섹션 접힘 · 주요 작업 영역을 더 넓게 볼 수 있습니다.";
    return true;
  }

  function renderModeCards() {
    const grid = document.querySelector("[data-admin-workspace-mode-grid]");
    if (!grid) return false;
    grid.innerHTML = ADMIN_WORKSPACE_MODES.map((mode) => `
      <button class="admin-workspace-card" type="button" data-admin-workspace-mode="${escapeHtml(mode.key)}">
        <span class="admin-workspace-card-label">${escapeHtml(mode.badge)}</span>
        <strong>${escapeHtml(mode.label)}</strong>
        <span>${escapeHtml(mode.summary)}</span>
        <small>관련 섹션 ${escapeHtml(mode.sections.length)}개 열기 →</small>
      </button>
    `).join("");
    return true;
  }

  function renderSidebarModeButtons() {
    const target = document.querySelector("[data-admin-workspace-sidebar-actions]");
    if (!target) return false;
    target.innerHTML = ADMIN_WORKSPACE_MODES.map((mode) => `
      <button class="admin-workspace-sidebar-link" type="button" data-admin-workspace-mode="${escapeHtml(mode.key)}">
        <span>${escapeHtml(mode.label)}</span>
        <small>${escapeHtml(mode.badge)}</small>
      </button>
    `).join("");
    return true;
  }

  function renderList(items, ordered) {
    const tag = ordered ? "ol" : "ul";
    return `<${tag}>${(items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</${tag}>`;
  }

  function renderWorkspaceModalBody(mode) {
    if (!mode) return "";
    return `
      <div class="admin-workspace-safe-note">
        <strong>안전 기준:</strong> 이 모드는 화면 정리와 안내만 담당합니다. API route, 응답 body, DB, seed, env, 인증, 실제 write 로직은 변경하지 않습니다.
      </div>
      <div class="admin-workspace-guide-grid">
        <div class="admin-workspace-guide-card">
          <strong>확인 순서</strong>
          ${renderList(mode.steps, true)}
        </div>
        <div class="admin-workspace-guide-card">
          <strong>주의/차단 기준</strong>
          ${renderList(mode.safety, false)}
        </div>
        <div class="admin-workspace-guide-card">
          <strong>주로 보는 버튼</strong>
          ${renderList((mode.buttons || []).map((button) => `\`${button}\``), false)}
        </div>
        <div class="admin-workspace-guide-card">
          <strong>자동으로 펼쳐진 섹션</strong>
          ${renderList((mode.sections || []).map((id) => `#${id}`), false)}
        </div>
      </div>
    `;
  }

  function openWorkspaceModal(modeKey) {
    const mode = getModeByKey(modeKey);
    const modal = document.querySelector("[data-admin-workspace-modal]");
    if (!mode || !modal) return false;
    const title = modal.querySelector("[data-admin-workspace-modal-title]");
    const summary = modal.querySelector("[data-admin-workspace-modal-summary]");
    const kicker = modal.querySelector("[data-admin-workspace-modal-kicker]");
    const body = modal.querySelector("[data-admin-workspace-modal-body]");
    if (title) title.textContent = mode.label;
    if (summary) summary.textContent = mode.summary;
    if (kicker) kicker.textContent = `${mode.badge} · ${VERSION}`;
    if (body) body.innerHTML = renderWorkspaceModalBody(mode);
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
    const closeButton = modal.querySelector("[data-admin-workspace-action='close-modal']");
    if (closeButton && closeButton.focus) closeButton.focus();
    return true;
  }

  function closeWorkspaceModal() {
    const modal = document.querySelector("[data-admin-workspace-modal]");
    if (!modal) return false;
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    return true;
  }

  function handleWorkspaceClick(event) {
    const modeButton = event.target && event.target.closest ? event.target.closest("[data-admin-workspace-mode]") : null;
    if (modeButton) {
      event.preventDefault();
      setWorkspaceMode(modeButton.getAttribute("data-admin-workspace-mode"));
      return;
    }
    const actionButton = event.target && event.target.closest ? event.target.closest("[data-admin-workspace-action]") : null;
    if (!actionButton) return;
    const action = actionButton.getAttribute("data-admin-workspace-action");
    if (action === "show-all") {
      event.preventDefault();
      showAllWorkspaceSections();
    } else if (action === "collapse-quiet") {
      event.preventDefault();
      collapseQuietSections();
    } else if (action === "close-modal") {
      event.preventDefault();
      closeWorkspaceModal();
    }
  }

  function handleWorkspaceKeydown(event) {
    if (event.key === "Escape") closeWorkspaceModal();
  }

  function initializeAdminWorkspaceNavigation() {
    const hubReady = !!document.querySelector("[data-admin-workspace-hub]");
    renderModeCards();
    renderSidebarModeButtons();
    updateWorkspaceStatus(null);
    if (!window.__upgradeRpgAdminWorkspaceNavigationBound) {
      window.__upgradeRpgAdminWorkspaceNavigationBound = true;
      document.addEventListener("click", handleWorkspaceClick);
      document.addEventListener("keydown", handleWorkspaceKeydown);
      document.addEventListener("click", (event) => {
        const modal = document.querySelector("[data-admin-workspace-modal]");
        if (modal && event.target === modal) closeWorkspaceModal();
      });
    }
    return getAdminWorkspaceNavigationReadiness();
  }

  function getAdminWorkspaceNavigationReadiness() {
    const hubReady = !!document.querySelector("[data-admin-workspace-hub]");
    const cardCount = document.querySelectorAll("[data-admin-workspace-mode-grid] [data-admin-workspace-mode]").length;
    const sidebarModeCount = document.querySelectorAll("[data-admin-workspace-sidebar-actions] [data-admin-workspace-mode]").length;
    const modalReady = !!document.querySelector("[data-admin-workspace-modal]");
    const actionCount = document.querySelectorAll("[data-admin-workspace-action]").length;
    const modeSectionIds = Array.from(new Set(ADMIN_WORKSPACE_MODES.flatMap((mode) => mode.sections || [])));
    const sectionMapReady = modeSectionIds.every((id) => !!document.getElementById(id));
    const result = {
      workspaceNavigationVersion: VERSION,
      hubReady,
      cardCount,
      sidebarModeCount,
      modeCount: ADMIN_WORKSPACE_MODES.length,
      modalReady,
      actionCount,
      sectionMapReady,
      activeModeKey,
      routeChanges: 0,
      apiBodyChanges: 0,
      writeOperations: 0,
    };
    result.ok = result.hubReady && result.cardCount === result.modeCount && result.sidebarModeCount === result.modeCount && result.modalReady && result.actionCount >= 3 && result.sectionMapReady;
    return result;
  }

  window.RpgAdminWorkspaceNavigation = {
    VERSION,
    ADMIN_WORKSPACE_MODES: ADMIN_WORKSPACE_MODES.map((mode) => ({ ...mode, sections: mode.sections.slice(), steps: mode.steps.slice(), safety: mode.safety.slice(), buttons: mode.buttons.slice() })),
    initializeAdminWorkspaceNavigation,
    getAdminWorkspaceNavigationReadiness,
    setWorkspaceMode,
    showAllWorkspaceSections,
    collapseQuietSections,
    openWorkspaceModal,
    closeWorkspaceModal,
  };

  window.initializeAdminWorkspaceNavigation = initializeAdminWorkspaceNavigation;
  window.getAdminWorkspaceNavigationReadiness = getAdminWorkspaceNavigationReadiness;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeAdminWorkspaceNavigation, { once: true });
  } else {
    initializeAdminWorkspaceNavigation();
  }
})();
