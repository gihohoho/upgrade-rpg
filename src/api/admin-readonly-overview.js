(function () {
	"use strict";

	const VERSION = "v113.admin-readonly-overview-url-helper";
	const DEFAULT_TIMEOUT_MS = 3000;
	const MODAL_ID = "admin-readonly-overview-modal";
	const STYLE_ID = "admin-readonly-overview-style";

	function escapeHtml(value) {
		return String(value === null || value === undefined ? "" : value)
			.replace(/&/g, "&amp;")
			.replace(/</g, "&lt;")
			.replace(/>/g, "&gt;")
			.replace(/\"/g, "&quot;")
			.replace(/'/g, "&#39;");
	}

	function formatValue(value) {
		if (value === null || value === undefined || value === "") return "-";
		if (typeof value === "number") return Number.isFinite(value) ? value.toLocaleString("ko-KR") : String(value);
		if (typeof value === "boolean") return value ? "true" : "false";
		return String(value);
	}

	function formatClock(value) {
		if (!value) return "-";
		try {
			const date = new Date(value);
			if (Number.isNaN(date.getTime())) return String(value);
			return date.toLocaleString("ko-KR", { hour12: false });
		} catch (error) {
			return String(value);
		}
	}

	function getTotal(item) {
		return item && item.total !== undefined ? item.total : 0;
	}

	async function fetchAdminReadOnlyOverview(options) {
		if (!window.RpgGameApi || typeof window.RpgGameApi.fetchAdminOverview !== "function") {
			throw new Error("RpgGameApi.fetchAdminOverview 함수를 찾을 수 없습니다.");
		}
		const opts = options || {};
		const response = await window.RpgGameApi.fetchAdminOverview({
			timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
		});
		if (opts.log !== false) {
			console.log("[Upgrade RPG] admin read-only overview loaded", response.payload);
		}
		return response;
	}

	async function listAdminReadOnlySaveSnapshots(options) {
		if (!window.RpgGameApi || typeof window.RpgGameApi.listAdminSaveSnapshots !== "function") {
			throw new Error("RpgGameApi.listAdminSaveSnapshots 함수를 찾을 수 없습니다.");
		}
		const opts = options || {};
		const response = await window.RpgGameApi.listAdminSaveSnapshots({
			limit: opts.limit || 20,
			timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
		});
		if (opts.log !== false) {
			const payload = response && response.payload ? response.payload : {};
			console.log("[Upgrade RPG] admin save snapshot summaries loaded", {
				status: payload.status || "unknown",
				count: Number(payload.count || 0),
			});
		}
		return response;
	}

	function ensureModalStyle() {
		if (document.getElementById(STYLE_ID)) return;
		const style = document.createElement("style");
		style.id = STYLE_ID;
		style.textContent = `
#${MODAL_ID} {
	position: fixed;
	inset: 0;
	z-index: 100190;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 20px;
	background: rgba(2, 6, 23, 0.72);
	backdrop-filter: blur(4px);
	box-sizing: border-box;
}
#${MODAL_ID}[data-hidden="true"] { display: none; }
#${MODAL_ID} .admin-overview-panel {
	width: min(860px, calc(100vw - 40px));
	max-height: min(720px, calc(100vh - 40px));
	overflow: auto;
	box-sizing: border-box;
	border: 1px solid rgba(148, 163, 184, 0.38);
	border-radius: 14px;
	background: rgba(10, 15, 28, 0.96);
	box-shadow: 0 24px 80px rgba(0, 0, 0, 0.55);
	color: #f8fafc;
	font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
#${MODAL_ID} .admin-overview-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 12px;
	padding: 16px 18px 12px;
	border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}
#${MODAL_ID} .admin-overview-title { font-size: 16px; font-weight: 800; }
#${MODAL_ID} .admin-overview-close {
	border: 1px solid rgba(255, 255, 255, 0.16);
	border-radius: 8px;
	background: rgba(255, 255, 255, 0.08);
	color: #f8fafc;
	font-weight: 800;
	cursor: pointer;
	padding: 5px 10px;
}
#${MODAL_ID} .admin-overview-body { padding: 16px 18px 18px; }
#${MODAL_ID} .admin-overview-note {
	margin-bottom: 12px;
	padding: 10px 12px;
	border-radius: 10px;
	background: rgba(59, 130, 246, 0.12);
	border: 1px solid rgba(59, 130, 246, 0.25);
	color: #bfdbfe;
	font-size: 13px;
	line-height: 1.45;
}
#${MODAL_ID} .admin-overview-warning {
	margin-bottom: 12px;
	padding: 10px 12px;
	border-radius: 10px;
	background: rgba(248, 113, 113, 0.13);
	border: 1px solid rgba(248, 113, 113, 0.30);
	color: #fecaca;
	font-size: 13px;
	line-height: 1.45;
}
#${MODAL_ID} .admin-overview-grid {
	display: grid;
	grid-template-columns: repeat(3, minmax(0, 1fr));
	gap: 10px;
	margin-bottom: 12px;
}
#${MODAL_ID} .admin-overview-card {
	border: 1px solid rgba(148, 163, 184, 0.22);
	border-radius: 10px;
	background: rgba(15, 23, 42, 0.58);
	padding: 10px 12px;
}
#${MODAL_ID} .admin-overview-card-label { color: #94a3b8; font-size: 12px; margin-bottom: 4px; }
#${MODAL_ID} .admin-overview-card-value { color: #f8fafc; font-weight: 800; font-size: 17px; }
#${MODAL_ID} .admin-overview-section-title { margin: 14px 0 8px; color: #e2e8f0; font-size: 13px; font-weight: 800; }
#${MODAL_ID} .admin-overview-table-wrap {
	border: 1px solid rgba(148, 163, 184, 0.22);
	border-radius: 10px;
	overflow: auto;
}
#${MODAL_ID} table { width: 100%; border-collapse: collapse; font-size: 12px; }
#${MODAL_ID} th,
#${MODAL_ID} td {
	padding: 7px 9px;
	border-bottom: 1px solid rgba(148, 163, 184, 0.16);
	text-align: left;
	vertical-align: top;
	white-space: nowrap;
}
#${MODAL_ID} th { background: rgba(15, 23, 42, 0.95); color: #cbd5e1; }
#${MODAL_ID} td { color: #e2e8f0; }
#${MODAL_ID} .admin-overview-actions {
	display: flex;
	flex-wrap: wrap;
	justify-content: flex-end;
	gap: 8px;
	margin-top: 14px;
}
#${MODAL_ID} .admin-overview-actions button {
	border: 1px solid rgba(255, 255, 255, 0.18);
	border-radius: 8px;
	background: rgba(255, 255, 255, 0.08);
	color: #f8fafc;
	font-weight: 800;
	cursor: pointer;
	padding: 8px 12px;
}
#${MODAL_ID} .admin-overview-actions button[data-primary="true"] {
	border-color: rgba(34, 197, 94, 0.65);
	background: rgba(34, 197, 94, 0.18);
	color: #bbf7d0;
}
#${MODAL_ID} .admin-overview-url-box {
	margin-bottom: 12px;
	padding: 10px 12px;
	border-radius: 10px;
	background: rgba(15, 23, 42, 0.72);
	border: 1px solid rgba(148, 163, 184, 0.22);
	color: #cbd5e1;
	font-size: 12px;
	line-height: 1.45;
}
#${MODAL_ID} .admin-overview-url-box code {
	display: block;
	margin-top: 5px;
	padding: 6px 8px;
	border-radius: 8px;
	background: rgba(2, 6, 23, 0.82);
	color: #bfdbfe;
	white-space: normal;
	word-break: break-all;
}
@media (max-width: 720px) {
	#${MODAL_ID} .admin-overview-grid { grid-template-columns: 1fr; }
}
`;
		document.head.appendChild(style);
	}

	function closeAdminReadOnlyOverviewModal() {
		const modal = document.getElementById(MODAL_ID);
		if (modal) modal.dataset.hidden = "true";
		return { ok: true, closed: true };
	}

	function getAdminReadOnlyPageUrl() {
		try {
			return new URL("admin.html", window.location.href).toString();
		} catch (error) {
			return "admin.html";
		}
	}

	async function copyAdminReadOnlyPageUrl() {
		const url = getAdminReadOnlyPageUrl();
		try {
			if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
				await navigator.clipboard.writeText(url);
				return { ok: true, url, copied: true, method: "clipboard" };
			}
		} catch (error) {
			// 브라우저 권한 때문에 clipboard API가 막히면 아래 fallback을 시도합니다.
		}

		try {
			const input = document.createElement("input");
			input.value = url;
			input.setAttribute("readonly", "readonly");
			input.style.position = "fixed";
			input.style.opacity = "0";
			document.body.appendChild(input);
			input.select();
			document.execCommand("copy");
			document.body.removeChild(input);
			return { ok: true, url, copied: true, method: "fallback" };
		} catch (error) {
			return { ok: false, url, copied: false, error: error && error.message ? error.message : String(error) };
		}
	}

	function openAdminReadOnlyPage() {
		const url = getAdminReadOnlyPageUrl();
		if (typeof window.open === "function") {
			const opened = window.open(url, "_blank", "noopener");
			if (opened) return { ok: true, url, opened: true };
		}
		window.location.href = url;
		return { ok: true, url, opened: false, navigated: true };
	}

	function renderMasterRows(masterData) {
		const entries = Object.entries(masterData || {}).filter(([key, value]) => key !== "summary" && value && typeof value === "object");
		if (!entries.length) return `<div class="admin-overview-warning">마스터 데이터 count를 찾지 못했습니다.</div>`;
		return `
			<div class="admin-overview-table-wrap">
				<table>
					<thead><tr><th>도메인</th><th>전체</th><th>활성</th><th>비활성</th></tr></thead>
					<tbody>
						${entries.map(([key, value]) => `
							<tr>
								<td>${escapeHtml(key)}</td>
								<td>${escapeHtml(formatValue(value.total))}</td>
								<td>${escapeHtml(formatValue(value.enabled))}</td>
								<td>${escapeHtml(formatValue(value.disabled))}</td>
							</tr>
						`).join("")}
					</tbody>
				</table>
			</div>
		`;
	}

	function renderSnapshotRows(snapshots) {
		const rows = Array.isArray(snapshots) ? snapshots : [];
		if (!rows.length) return `<div class="admin-overview-warning">최근 세이브 스냅샷이 없습니다.</div>`;
		return `
			<div class="admin-overview-table-wrap">
				<table>
					<thead><tr><th>유저</th><th>슬롯</th><th>버전</th><th>골드</th><th>레벨</th><th>인벤</th><th>출처</th><th>수정 시각</th></tr></thead>
					<tbody>
						${rows.map((row) => `
							<tr title="${escapeHtml(row.note || "")}">
								<td>${escapeHtml(formatValue(row.userId))}</td>
								<td>${escapeHtml(formatValue(row.slotKey))}${row.isDefault ? " <strong>(default)</strong>" : ""}</td>
								<td>${escapeHtml(formatValue(row.saveVersion))}</td>
								<td>${escapeHtml(formatValue(row.summary && row.summary.gold))}</td>
								<td>${escapeHtml(formatValue(row.summary && row.summary.level))}</td>
								<td>${escapeHtml(formatValue(row.counts && row.counts.inventoryItems))}</td>
								<td>${escapeHtml(formatValue(row.source))}</td>
								<td>${escapeHtml(formatClock(row.updatedAt))}</td>
							</tr>
						`).join("")}
					</tbody>
				</table>
			</div>
		`;
	}

	async function openAdminReadOnlyOverviewModal(options) {
		const opts = options || {};
		ensureModalStyle();
		let modal = document.getElementById(MODAL_ID);
		if (!modal) {
			modal = document.createElement("div");
			modal.id = MODAL_ID;
			document.body.appendChild(modal);
		}
		modal.dataset.hidden = "false";
		modal.innerHTML = `
			<div class="admin-overview-panel" role="dialog" aria-modal="true" aria-label="관리자 읽기 전용 overview">
				<div class="admin-overview-header">
					<div class="admin-overview-title">관리자 준비 overview</div>
					<button type="button" class="admin-overview-close" data-action="close">닫기</button>
				</div>
				<div class="admin-overview-body">
					<div class="admin-overview-note">관리자 페이지로 넘어가기 전 DB 상태를 조회만 합니다. 이 화면은 localStorage/DB를 수정하지 않습니다.</div>
					<div class="admin-overview-url-box">현재 게임 주소 기준 관리자 페이지 주소<code>${escapeHtml(getAdminReadOnlyPageUrl())}</code></div>
					<div>불러오는 중...</div>
				</div>
			</div>
		`;
		modal.onclick = async (event) => {
			const action = event.target && event.target.getAttribute ? event.target.getAttribute("data-action") : null;
			if (action === "close") closeAdminReadOnlyOverviewModal();
			if (action === "refresh") await openAdminReadOnlyOverviewModal(opts);
			if (action === "open-page") openAdminReadOnlyPage();
			if (action === "copy-page-url") {
				const result = await copyAdminReadOnlyPageUrl();
				console.log("[Upgrade RPG] admin page URL copy", result);
			}
		};

		let overviewResponse = null;
		let snapshotsResponse = null;
		let error = null;
		try {
			overviewResponse = await fetchAdminReadOnlyOverview({ timeoutMs: opts.timeoutMs, log: opts.log });
			snapshotsResponse = await listAdminReadOnlySaveSnapshots({ limit: opts.limit || 20, timeoutMs: opts.timeoutMs, log: opts.log });
		} catch (err) {
			error = err && err.message ? err.message : String(err);
		}

		const body = modal.querySelector(".admin-overview-body");
		if (!body) return { ok: false, error: "modal body missing" };
		if (error) {
			body.innerHTML = `
				<div class="admin-overview-warning">관리자 overview를 불러오지 못했습니다.</div>
				<div style="color:#fecaca; font-size:13px;">${escapeHtml(error)}</div>
				<div class="admin-overview-actions"><button type="button" data-action="close">닫기</button><button type="button" data-action="open-page" data-primary="true">관리자 페이지 열기</button></div>
			`;
			return { ok: false, error };
		}

		const overview = overviewResponse && overviewResponse.payload ? overviewResponse.payload : {};
		const snapshots = snapshotsResponse && snapshotsResponse.payload ? snapshotsResponse.payload.snapshots : [];
		// API 안전장치 확인용: 각 row는 rawSnapshotReturned=false이며 원본 snapshot JSON은 포함하지 않습니다.
		const master = overview.masterData || {};
		const save = overview.saveSnapshots || {};
		const readiness = overview.readiness || {};
		const warnings = Array.isArray(readiness.warnings) ? readiness.warnings : [];
		body.innerHTML = `
			<div class="admin-overview-note">
				읽기 전용 상태: ${escapeHtml(formatValue(overview.readOnly))} · 관리자 쓰기 UI: ${escapeHtml(formatValue(readiness.safeForAdminWriteUi))}<br>
				${escapeHtml(readiness.writeUiBlockedReason || "쓰기 기능은 아직 막혀 있습니다.")}
			</div>
			<div class="admin-overview-url-box">현재 게임 주소 기준 관리자 페이지 주소<code>${escapeHtml(getAdminReadOnlyPageUrl())}</code></div>
			${warnings.length ? `<div class="admin-overview-warning">경고: ${escapeHtml(warnings.join(", "))}</div>` : ""}
			<div class="admin-overview-grid">
				<div class="admin-overview-card"><div class="admin-overview-card-label">마스터 도메인</div><div class="admin-overview-card-value">${escapeHtml(formatValue(master.summary && master.summary.domains))}</div></div>
				<div class="admin-overview-card"><div class="admin-overview-card-label">마스터 행 수</div><div class="admin-overview-card-value">${escapeHtml(formatValue(master.summary && master.summary.totalRows))}</div></div>
				<div class="admin-overview-card"><div class="admin-overview-card-label">DB 세이브 슬롯</div><div class="admin-overview-card-value">${escapeHtml(formatValue(save.totalSlots))}</div></div>
				<div class="admin-overview-card"><div class="admin-overview-card-label">저장 유저 수</div><div class="admin-overview-card-value">${escapeHtml(formatValue(save.usersWithSaves))}</div></div>
				<div class="admin-overview-card"><div class="admin-overview-card-label">default 슬롯</div><div class="admin-overview-card-value">${escapeHtml(formatValue(save.defaultSlots))}</div></div>
				<div class="admin-overview-card"><div class="admin-overview-card-label">최근 저장</div><div class="admin-overview-card-value" style="font-size:13px;">${escapeHtml(formatClock(save.latestUpdatedAt))}</div></div>
			</div>
			<div class="admin-overview-section-title">마스터 데이터 counts</div>
			${renderMasterRows(master)}
			<div class="admin-overview-section-title">최근 세이브 스냅샷 요약</div>
			${renderSnapshotRows(snapshots)}
			<div class="admin-overview-actions">
				<button type="button" data-action="close">닫기</button>
				<button type="button" data-action="copy-page-url">주소 복사</button>
				<button type="button" data-action="open-page">관리자 페이지 열기</button>
				<button type="button" data-action="refresh" data-primary="true">새로고침</button>
			</div>
		`;
		return { ok: true, overview: overviewResponse, snapshots: snapshotsResponse };
	}

	async function checkAdminReadOnlyOverviewReady(options) {
		const apiReady = !!(window.RpgGameApi && typeof window.RpgGameApi.fetchAdminOverview === "function" && typeof window.RpgGameApi.listAdminSaveSnapshots === "function");
		const result = {
			ok: apiReady,
			version: VERSION,
			apiReady,
			modalReady: typeof document !== "undefined",
			readOnly: true,
			pageReady: true,
			adminPageUrl: getAdminReadOnlyPageUrl(),
		};
		if (!options || options.log !== false) console.log("[Upgrade RPG] admin read-only overview check", result);
		return result;
	}

	window.RpgAdminReadOnlyOverview = {
		VERSION,
		MODAL_ID,
		fetchAdminReadOnlyOverview,
		listAdminReadOnlySaveSnapshots,
		openAdminReadOnlyOverviewModal,
		closeAdminReadOnlyOverviewModal,
		checkAdminReadOnlyOverviewReady,
		getAdminReadOnlyPageUrl,
		copyAdminReadOnlyPageUrl,
		openAdminReadOnlyPage,
	};
	window.fetchAdminReadOnlyOverview = fetchAdminReadOnlyOverview;
	window.listAdminReadOnlySaveSnapshots = listAdminReadOnlySaveSnapshots;
	window.openAdminReadOnlyOverviewModal = openAdminReadOnlyOverviewModal;
	window.closeAdminReadOnlyOverviewModal = closeAdminReadOnlyOverviewModal;
	window.checkAdminReadOnlyOverviewReady = checkAdminReadOnlyOverviewReady;
	window.getAdminReadOnlyPageUrl = getAdminReadOnlyPageUrl;
	window.copyAdminReadOnlyPageUrl = copyAdminReadOnlyPageUrl;
	window.openAdminReadOnlyPage = openAdminReadOnlyPage;
})();
