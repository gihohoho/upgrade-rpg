(function () {
  "use strict";

  const VERSION = "v370.authenticated-admin-account-management";
  const DEFAULT_LIMIT = 20;
  const state = {
    authorized: false,
    currentUser: null,
    page: 1,
    userList: null,
    statusTarget: null,
    statusPreview: null,
    lastFocused: null,
  };

  const $ = (selector) => document.querySelector(selector);
  const escapeHtml = (value) => String(value === null || value === undefined ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

  function api() {
    if (!window.RpgGameApi || typeof window.RpgGameApi.request !== "function") {
      throw new Error("게임 API 연결을 찾을 수 없습니다. 페이지를 새로고침해 주세요.");
    }
    return window.RpgGameApi;
  }

  function apiErrorMessage(error) {
    const detail = error && error.response && error.response.error && error.response.error.message;
    return String(detail || (error && error.message) || "요청을 처리하지 못했습니다.");
  }

  function formatDate(value) {
    if (!value) return "-";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return new Intl.DateTimeFormat("ko-KR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  }

  function formatValue(value) {
    if (value === null || value === undefined || value === "") return "-";
    return String(value);
  }

  function getAdminWriteHeaders() {
    const client = api();
    return typeof client.getAdminWriteHeaders === "function" ? client.getAdminWriteHeaders() : {};
  }

  async function fetchBootstrapStatus() {
    const client = api();
    if (typeof client.fetchAccountBootstrapStatus === "function") {
      return client.fetchAccountBootstrapStatus({ timeoutMs: 5000 });
    }
    return client.request("/account-admin/bootstrap-status", { timeoutMs: 5000 });
  }

  async function applyBootstrap(reason) {
    const client = api();
    if (typeof client.bootstrapFirstAdmin === "function") {
      return client.bootstrapFirstAdmin(
        { reason: reason || undefined },
        { timeoutMs: 5000 },
      );
    }
    return client.request("/account-admin/bootstrap", {
      method: "POST",
      body: { reason: reason || undefined },
      headers: getAdminWriteHeaders(),
      timeoutMs: 5000,
    });
  }

  async function fetchUsers(options) {
    const client = api();
    if (typeof client.listAdminAccounts === "function") {
      return client.listAdminAccounts(options);
    }
    return client.request("/account-admin/users", {
      query: {
        page: options.page,
        limit: options.limit,
        query: options.query,
        status: options.status,
        sort: options.sort,
      },
      timeoutMs: 5000,
    });
  }

  async function fetchUserDetail(userId) {
    const client = api();
    if (typeof client.fetchAdminAccountDetail === "function") {
      return client.fetchAdminAccountDetail(userId, { timeoutMs: 5000 });
    }
    return client.request(`/account-admin/users/${Number(userId)}`, { timeoutMs: 5000 });
  }

  async function fetchStatusPreview(target, reason) {
    const client = api();
    const payload = {
      baseIsActive: target.baseIsActive,
      nextIsActive: target.nextIsActive,
      reason,
    };
    if (typeof client.previewAdminAccountStatus === "function") {
      return client.previewAdminAccountStatus(target.userId, payload, { timeoutMs: 5000 });
    }
    return client.request(`/account-admin/users/${Number(target.userId)}/status-preview`, {
      method: "POST",
      body: payload,
      timeoutMs: 5000,
    });
  }

  async function applyStatus(target, reason, confirmText) {
    const client = api();
    const payload = {
      baseIsActive: target.baseIsActive,
      nextIsActive: target.nextIsActive,
      reason,
      confirmText,
    };
    if (typeof client.applyAdminAccountStatus === "function") {
      return client.applyAdminAccountStatus(target.userId, payload, { timeoutMs: 5000 });
    }
    return client.request(`/account-admin/users/${Number(target.userId)}/status-apply`, {
      method: "POST",
      body: payload,
      headers: getAdminWriteHeaders(),
      timeoutMs: 5000,
    });
  }

  function setGateMessage(message) {
    const target = $("[data-account-admin-gate-message]");
    if (target) target.textContent = message;
  }

  function setPanelStatus(message, tone) {
    const target = $("[data-account-admin-status-line]");
    if (!target) return;
    target.textContent = message;
    target.classList.toggle("error", tone === "error");
    target.classList.toggle("good", tone === "good");
  }

  function lockAdminPage(message) {
    state.authorized = false;
    document.body.classList.add("account-admin-locked");
    const gate = $("[data-account-admin-gate]");
    const content = $("[data-account-admin-content]");
    if (gate) gate.hidden = false;
    if (content) content.setAttribute("aria-hidden", "true");
    if (message) setGateMessage(message);
  }

  async function unlockAdminPage(currentUser) {
    state.authorized = true;
    state.currentUser = currentUser;
    document.body.classList.remove("account-admin-locked");
    const gate = $("[data-account-admin-gate]");
    const content = $("[data-account-admin-content]");
    const bootstrap = $("[data-account-admin-bootstrap]");
    const badge = $("[data-account-admin-current-admin]");
    if (gate) gate.hidden = true;
    if (bootstrap) bootstrap.hidden = true;
    if (content) content.setAttribute("aria-hidden", "false");
    if (badge) badge.textContent = `${currentUser.username || "관리자"} · 로그인됨`;

    await refreshUsers(1);
    if (window.RpgAdminReadOnlyPage && typeof window.RpgAdminReadOnlyPage.bootAdminReadOnlyPage === "function") {
      window.RpgAdminReadOnlyPage.bootAdminReadOnlyPage();
    }
  }

  async function checkAdminGate() {
    lockAdminPage("로그인 정보와 관리자 권한을 안전하게 확인하는 중입니다.");
    const bootstrap = $("[data-account-admin-bootstrap]");
    if (bootstrap) bootstrap.hidden = true;
    try {
      const response = await fetchBootstrapStatus();
      const payload = response && response.payload ? response.payload : {};
      const currentUser = payload.currentUser || {};
      if (currentUser.isAdmin === true) {
        await unlockAdminPage(currentUser);
        return { ok: true, authorized: true, currentUser };
      }
      if (payload.canBootstrap === true) {
        setGateMessage(`${currentUser.username || "현재 계정"} 계정으로 로그인했습니다. 최초 관리자 설정을 완료해 주세요.`);
        if (bootstrap) bootstrap.hidden = false;
        const savedKey = api().getAdminWriteDevKey ? api().getAdminWriteDevKey() : "";
        const keyInput = $("[data-account-admin-bootstrap-dev-key]");
        if (keyInput && savedKey) keyInput.value = savedKey;
        return { ok: true, authorized: false, bootstrapReady: true, currentUser };
      }
      setGateMessage("로그인은 확인됐지만 관리자 권한이 없습니다. 관리자에게 계정 권한을 요청해 주세요.");
      return { ok: true, authorized: false, bootstrapReady: false, currentUser };
    } catch (error) {
      const status = Number(error && error.status);
      setGateMessage(status === 401
        ? "관리자 페이지를 보려면 먼저 게임 화면에서 로그인해 주세요."
        : `관리자 권한 확인 실패: ${apiErrorMessage(error)}`);
      return { ok: false, authorized: false, status, error };
    }
  }

  async function bootstrapCurrentUser() {
    const button = $("[data-account-admin-action='bootstrap']");
    const keyInput = $("[data-account-admin-bootstrap-dev-key]");
    const reasonInput = $("[data-account-admin-bootstrap-reason]");
    const key = keyInput ? keyInput.value.trim() : "";
    if (!key) {
      setGateMessage("최초 관리자 설정을 위해 backend에 설정된 dev key를 입력해 주세요.");
      if (keyInput) keyInput.focus();
      return;
    }
    if (api().setAdminWriteDevKey) api().setAdminWriteDevKey(key);
    if (button) button.disabled = true;
    setGateMessage("최초 관리자 조건을 다시 확인하고 있습니다.");
    try {
      const response = await applyBootstrap(reasonInput ? reasonInput.value.trim() : "");
      const payload = response && response.payload ? response.payload : {};
      if (!payload.applied) {
        setGateMessage(payload.reason || "최초 관리자 설정이 안전 조건에 의해 차단됐습니다.");
        return;
      }
      setGateMessage("최초 관리자 설정이 완료됐습니다. 권한을 다시 확인합니다.");
      await checkAdminGate();
    } catch (error) {
      setGateMessage(`최초 관리자 설정 실패: ${apiErrorMessage(error)}`);
    } finally {
      if (button) button.disabled = false;
    }
  }

  function readFilters() {
    return {
      page: state.page,
      limit: DEFAULT_LIMIT,
      query: $("[data-account-admin-query]") ? $("[data-account-admin-query]").value.trim() : "",
      status: $("[data-account-admin-status]") ? $("[data-account-admin-status]").value : "all",
      sort: $("[data-account-admin-sort]") ? $("[data-account-admin-sort]").value : "created_desc",
    };
  }

  async function refreshUsers(page) {
    if (!state.authorized) return { ok: false, reason: "admin-not-authorized" };
    state.page = Math.max(1, Number(page || state.page || 1));
    const filters = readFilters();
    filters.page = state.page;
    setPanelStatus("회원 계정과 캐릭터 슬롯 요약을 불러오는 중입니다.");
    try {
      const response = await fetchUsers(filters);
      const payload = response && response.payload ? response.payload : {};
      state.userList = payload;
      state.page = Number(payload.page || state.page);
      renderUserList(payload);
      setPanelStatus(`회원 ${payload.count || 0}명을 표시했습니다. 저장 원본과 인증 정보는 가져오지 않았습니다.`, "good");
      return { ok: true, payload };
    } catch (error) {
      const status = Number(error && error.status);
      if (status === 401 || status === 403) {
        lockAdminPage(status === 401
          ? "로그인이 만료됐습니다. 게임 로그인 화면에서 다시 로그인해 주세요."
          : "관리자 권한이 없어 회원 정보를 볼 수 없습니다.");
      }
      setPanelStatus(`회원 목록 조회 실패: ${apiErrorMessage(error)}`, "error");
      renderUserList({ users: [], total: 0, count: 0, page: 1, totalPages: 1 });
      return { ok: false, error };
    }
  }

  function renderUserList(payload) {
    const users = Array.isArray(payload.users) ? payload.users : [];
    const table = $("[data-account-admin-user-table]");
    const summary = $("[data-account-admin-summary]");
    const pagination = $("[data-account-admin-pagination]");
    const usedSlots = users.reduce((total, user) => total + Number(user.characterSlotsUsed || 0), 0);

    if (summary) {
      summary.innerHTML = `
        <div><span>전체 회원</span><strong>${escapeHtml(formatValue(payload.total || 0))}</strong></div>
        <div><span>현재 표시</span><strong>${escapeHtml(formatValue(users.length))}</strong></div>
        <div><span>사용 중 슬롯</span><strong>${escapeHtml(formatValue(usedSlots))}</strong></div>
      `;
    }
    if (table) {
      if (!users.length) {
        table.innerHTML = `<div class="account-admin-empty">조건에 맞는 회원이 없습니다.</div>`;
      } else {
        table.innerHTML = `
          <table class="account-admin-table">
            <thead><tr><th>ID</th><th>아이디</th><th>상태</th><th>권한</th><th>캐릭터 슬롯</th><th>가입일</th><th>관리</th></tr></thead>
            <tbody>${users.map(renderUserRow).join("")}</tbody>
          </table>
        `;
      }
    }
    if (pagination) {
      const current = Math.max(1, Number(payload.page || 1));
      const totalPages = Math.max(1, Number(payload.totalPages || 1));
      pagination.innerHTML = `
        <button type="button" data-account-admin-action="page-users" data-page="${current - 1}" ${current <= 1 ? "disabled" : ""}>이전</button>
        <span>${current} / ${totalPages} 페이지</span>
        <button type="button" data-account-admin-action="page-users" data-page="${current + 1}" ${current >= totalPages ? "disabled" : ""}>다음</button>
      `;
    }
  }

  function renderUserRow(user) {
    const isCurrent = !!(state.currentUser && Number(state.currentUser.id) === Number(user.id));
    const nextActive = !user.isActive;
    const statusActionClass = nextActive ? "activate" : "danger";
    const statusActionText = nextActive ? "정지 해제" : "계정 정지";
    return `
      <tr>
        <td data-label="ID">${escapeHtml(user.id)}</td>
        <td data-label="아이디"><span class="account-admin-user-name">${escapeHtml(user.username)}</span>${isCurrent ? " · 나" : ""}</td>
        <td data-label="상태"><span class="account-admin-state ${user.isActive ? "" : "suspended"}">${user.isActive ? "활성" : "정지"}</span></td>
        <td data-label="권한">${user.isAdmin ? `<span class="account-admin-state admin">관리자</span>` : "일반 회원"}</td>
        <td data-label="캐릭터 슬롯">${escapeHtml(user.characterSlotsUsed || 0)} / ${escapeHtml(user.characterSlotCapacity || 8)}</td>
        <td data-label="가입일">${escapeHtml(formatDate(user.createdAt))}</td>
        <td data-label="관리">
          <div class="account-admin-row-actions">
            <button type="button" data-account-admin-action="open-user" data-user-id="${Number(user.id)}">상세 보기</button>
            <button type="button" class="${statusActionClass}" data-account-admin-action="open-status" data-user-id="${Number(user.id)}" data-username="${escapeHtml(user.username)}" data-base-active="${user.isActive}" data-next-active="${nextActive}" ${isCurrent && !nextActive ? "disabled title=\"현재 로그인 계정은 정지할 수 없습니다\"" : ""}>${statusActionText}</button>
          </div>
        </td>
      </tr>
    `;
  }

  async function openUserDetail(userId, trigger) {
    if (!state.authorized) return;
    state.lastFocused = trigger || document.activeElement;
    const modal = $("[data-account-admin-detail-modal]");
    const body = $("[data-account-admin-detail-body]");
    if (modal) modal.setAttribute("aria-hidden", "false");
    if (body) body.innerHTML = `<div class="account-admin-empty">회원 상세를 불러오는 중입니다.</div>`;
    try {
      const response = await fetchUserDetail(userId);
      const payload = response && response.payload ? response.payload : {};
      renderUserDetail(payload);
    } catch (error) {
      if (body) body.innerHTML = `<div class="account-admin-status error">상세 조회 실패: ${escapeHtml(apiErrorMessage(error))}</div>`;
    }
    const close = modal && modal.querySelector("[data-account-admin-action='close-detail']");
    if (close) close.focus();
  }

  function renderUserDetail(payload) {
    const user = payload.user || {};
    const slots = Array.isArray(payload.characterSlots) ? payload.characterSlots : [];
    const title = $("[data-account-admin-detail-title]");
    const body = $("[data-account-admin-detail-body]");
    if (title) title.textContent = `${user.username || "회원"} 상세`;
    if (!body) return;
    body.innerHTML = `
      <div class="account-admin-profile-grid">
        <div><span>회원 ID</span><strong>${escapeHtml(formatValue(user.id))}</strong></div>
        <div><span>계정 상태</span><strong>${user.isActive ? "활성" : "정지"}</strong></div>
        <div><span>권한</span><strong>${user.isAdmin ? "관리자" : "일반 회원"}</strong></div>
        <div><span>가입일</span><strong>${escapeHtml(formatDate(user.createdAt))}</strong></div>
      </div>
      <h3 class="account-admin-slot-title">캐릭터 슬롯 · ${escapeHtml(user.characterSlotsUsed || 0)} / ${escapeHtml(user.characterSlotCapacity || 8)}</h3>
      <div class="account-admin-slots">${slots.map(renderCharacterSlot).join("")}</div>
      <div class="account-admin-status good">이 상세 화면은 accountCharacter 요약만 사용하며 게임 저장 원본과 인증 정보는 불러오지 않습니다.</div>
    `;
  }

  function renderCharacterSlot(slot) {
    if (!slot || slot.isEmpty) {
      return `<div class="account-admin-slot empty"><div><span class="account-admin-slot-index">SLOT ${escapeHtml(slot && slot.slotIndex)}</span><strong>빈 슬롯</strong></div></div>`;
    }
    return `
      <div class="account-admin-slot">
        <span class="account-admin-slot-index">SLOT ${escapeHtml(slot.slotIndex)}</span>
        <strong>${escapeHtml(slot.name || "이름 없는 캐릭터")}</strong>
        <small>직업: ${escapeHtml(formatValue(slot.characterCode))}</small>
        <small>레벨: ${escapeHtml(formatValue(slot.level))}</small>
        <small>최근 저장: ${escapeHtml(formatDate(slot.lastSavedAt))}</small>
      </div>
    `;
  }

  function closeModal(selector) {
    const modal = $(selector);
    if (modal) modal.setAttribute("aria-hidden", "true");
    if (state.lastFocused && typeof state.lastFocused.focus === "function") state.lastFocused.focus();
  }

  function openStatusModal(button) {
    if (!state.authorized) return;
    state.lastFocused = button || document.activeElement;
    state.statusTarget = {
      userId: Number(button.dataset.userId),
      username: String(button.dataset.username || "회원"),
      baseIsActive: button.dataset.baseActive === "true",
      nextIsActive: button.dataset.nextActive === "true",
    };
    state.statusPreview = null;
    const modal = $("[data-account-admin-status-modal]");
    const title = $("[data-account-admin-status-title]");
    const reason = $("[data-account-admin-status-reason]");
    const confirm = $("[data-account-admin-status-confirm]");
    const applyButton = $("[data-account-admin-action='apply-status']");
    if (title) title.textContent = state.statusTarget.nextIsActive ? "계정 정지 해제" : "계정 정지";
    if (reason) reason.value = "";
    if (confirm) {
      confirm.value = "";
      confirm.placeholder = "변경 내용 확인 후 문구가 표시됩니다";
    }
    if (applyButton) applyButton.disabled = true;
    renderStatusPreview({
      applyReady: false,
      message: `${state.statusTarget.username} 계정을 ${state.statusTarget.nextIsActive ? "다시 활성화" : "정지"}하려면 사유를 입력하고 변경 내용을 먼저 확인하세요.`,
    });
    if (modal) modal.setAttribute("aria-hidden", "false");
    if (reason) reason.focus();
  }

  function renderStatusPreview(preview) {
    const target = $("[data-account-admin-status-preview]");
    if (!target) return;
    const blockers = Array.isArray(preview.blockers) ? preview.blockers : [];
    const blockerLabels = {
      stale_account_status: "목록을 본 뒤 계정 상태가 바뀌었습니다. 새로고침 후 다시 시도하세요.",
      no_status_change: "현재 상태와 변경할 상태가 같습니다.",
      cannot_suspend_self: "현재 로그인한 관리자 계정은 스스로 정지할 수 없습니다.",
      cannot_suspend_last_active_admin: "마지막 활성 관리자 계정은 정지할 수 없습니다.",
    };
    target.innerHTML = `
      <div class="account-admin-preview-box ${preview.applyReady ? "" : "blocked"}">
        <strong>${preview.applyReady ? "변경 준비 완료" : "변경 전 확인"}</strong>
        <div>${escapeHtml(preview.message || (preview.applyReady ? "아래 확인 문구를 정확히 입력한 뒤 적용할 수 있습니다." : "사유를 입력하고 변경 내용을 확인해 주세요."))}</div>
        ${blockers.length ? `<ul>${blockers.map((item) => `<li>${escapeHtml(blockerLabels[item] || item)}</li>`).join("")}</ul>` : ""}
        ${preview.confirmationText ? `<div>정확한 확인 문구</div><div class="account-admin-confirm-phrase">${escapeHtml(preview.confirmationText)}</div>` : ""}
      </div>
    `;
  }

  async function previewStatusChange() {
    if (!state.statusTarget) return;
    const reasonInput = $("[data-account-admin-status-reason]");
    const reason = reasonInput ? reasonInput.value.trim() : "";
    if (reason.length < 2) {
      renderStatusPreview({ applyReady: false, message: "관리 기록에 남길 변경 사유를 2자 이상 입력해 주세요." });
      if (reasonInput) reasonInput.focus();
      return;
    }
    const applyButton = $("[data-account-admin-action='apply-status']");
    if (applyButton) applyButton.disabled = true;
    renderStatusPreview({ applyReady: false, message: "현재 계정 상태와 안전 조건을 확인하고 있습니다." });
    try {
      const response = await fetchStatusPreview(state.statusTarget, reason);
      const preview = response && response.payload ? response.payload : {};
      state.statusPreview = preview;
      renderStatusPreview(preview);
      const confirm = $("[data-account-admin-status-confirm]");
      if (confirm) confirm.placeholder = preview.confirmationText || "변경이 차단됐습니다";
      if (applyButton) applyButton.disabled = preview.applyReady !== true;
    } catch (error) {
      renderStatusPreview({ applyReady: false, message: `변경 내용 확인 실패: ${apiErrorMessage(error)}` });
    }
  }

  async function applyStatusChange() {
    if (!state.statusTarget || !state.statusPreview || state.statusPreview.applyReady !== true) return;
    const reason = $("[data-account-admin-status-reason]") ? $("[data-account-admin-status-reason]").value.trim() : "";
    const confirmText = $("[data-account-admin-status-confirm]") ? $("[data-account-admin-status-confirm]").value.trim() : "";
    const applyButton = $("[data-account-admin-action='apply-status']");
    if (applyButton) applyButton.disabled = true;
    try {
      const response = await applyStatus(state.statusTarget, reason, confirmText);
      const payload = response && response.payload ? response.payload : {};
      if (!payload.applied) {
        state.statusPreview = payload;
        renderStatusPreview(payload);
        if (applyButton) applyButton.disabled = payload.applyReady !== true;
        return;
      }
      closeModal("[data-account-admin-status-modal]");
      setPanelStatus(`${state.statusTarget.username} 계정 상태를 변경하고 감사 이력을 남겼습니다.`, "good");
      await refreshUsers(state.page);
    } catch (error) {
      renderStatusPreview({ applyReady: false, message: `상태 변경 실패: ${apiErrorMessage(error)}` });
    }
  }

  function resetUserFilters() {
    const query = $("[data-account-admin-query]");
    const status = $("[data-account-admin-status]");
    const sort = $("[data-account-admin-sort]");
    if (query) query.value = "";
    if (status) status.value = "all";
    if (sort) sort.value = "created_desc";
    refreshUsers(1);
  }

  async function handleAction(button) {
    const action = button.getAttribute("data-account-admin-action");
    if (action === "retry-gate") return checkAdminGate();
    if (action === "bootstrap") return bootstrapCurrentUser();
    if (action === "refresh-users" || action === "search-users") return refreshUsers(action === "search-users" ? 1 : state.page);
    if (action === "reset-users") return resetUserFilters();
    if (action === "page-users") return refreshUsers(Number(button.dataset.page || 1));
    if (action === "open-user") return openUserDetail(Number(button.dataset.userId), button);
    if (action === "close-detail") return closeModal("[data-account-admin-detail-modal]");
    if (action === "open-status") return openStatusModal(button);
    if (action === "close-status") return closeModal("[data-account-admin-status-modal]");
    if (action === "preview-status") return previewStatusChange();
    if (action === "apply-status") return applyStatusChange();
    return undefined;
  }

  function bindEvents() {
    document.addEventListener("click", (event) => {
      const button = event.target && event.target.closest ? event.target.closest("[data-account-admin-action]") : null;
      if (!button) return;
      event.preventDefault();
      Promise.resolve(handleAction(button)).catch((error) => setPanelStatus(apiErrorMessage(error), "error"));
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeModal("[data-account-admin-detail-modal]");
        closeModal("[data-account-admin-status-modal]");
      }
      if (event.key === "Enter" && event.target && event.target.matches("[data-account-admin-query]")) {
        event.preventDefault();
        refreshUsers(1);
      }
    });
    document.addEventListener("click", (event) => {
      if (event.target && event.target.matches("[data-account-admin-detail-modal]")) closeModal("[data-account-admin-detail-modal]");
      if (event.target && event.target.matches("[data-account-admin-status-modal]")) closeModal("[data-account-admin-status-modal]");
    });
  }

  function isAdminAuthorized() {
    return state.authorized === true;
  }

  function getReadiness() {
    const requiredDom = [
      "[data-account-admin-gate]",
      "[data-account-admin-content]",
      "[data-account-admin-user-table]",
      "[data-account-admin-detail-modal]",
      "[data-account-admin-status-modal]",
    ];
    const missingDom = requiredDom.filter((selector) => !$(selector));
    return {
      ok: missingDom.length === 0 && !!window.RpgGameApi,
      version: VERSION,
      authorized: state.authorized,
      missingDom,
      legacyAdminBootDeferred: true,
      rawSaveUsed: false,
    };
  }

  function initialize() {
    bindEvents();
    lockAdminPage();
    if (window.RpgAuthSession && typeof window.RpgAuthSession.restoreTokenFromStorage === "function") {
      window.RpgAuthSession.restoreTokenFromStorage();
    }
    return checkAdminGate();
  }

  window.RpgAdminAccountManagement = {
    VERSION,
    initialize,
    checkAdminGate,
    isAdminAuthorized,
    refreshUsers,
    openUserDetail,
    previewStatusChange,
    applyStatusChange,
    getReadiness,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
