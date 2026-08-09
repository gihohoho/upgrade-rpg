(function () {
	"use strict";

	const VERSION = "v109.backend-save-data-slot-list";
	const DEFAULT_TIMEOUT_MS = 3000;
	const MODAL_ID = "backend-save-slots-modal";
	const STYLE_ID = "backend-save-slots-style";

	function getCurrentBackendSlotKey() {
		return typeof window.getCurrentAccountBackendSlotKey === "function"
			? window.getCurrentAccountBackendSlotKey()
			: (window.UPGRADE_RPG_BACKEND_SLOT_KEY || "default");
	}

	function formatClock(value) {
		if (!value) return "-";
		try {
			const date = new Date(value);
			if (Number.isNaN(date.getTime())) return "-";
			return date.toLocaleString("ko-KR", { hour12: false });
		} catch (error) {
			return String(value);
		}
	}

	function formatValue(value) {
		if (value === null || value === undefined || value === "") return "-";
		if (Array.isArray(value)) return value.join(", ") || "-";
		if (typeof value === "object") {
			try {
				return JSON.stringify(value);
			} catch (error) {
				return String(value);
			}
		}
		return String(value);
	}

	function escapeHtml(value) {
		return String(value)
			.replace(/&/g, "&amp;")
			.replace(/</g, "&lt;")
			.replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;")
			.replace(/'/g, "&#39;");
	}

	function getSummaryValue(slot, key) {
		const summary = slot && slot.summary && typeof slot.summary === "object" ? slot.summary : {};
		return summary[key];
	}

	function getSlotRows(slots) {
		const currentSlotKey = getCurrentBackendSlotKey();
		return (Array.isArray(slots) ? slots : []).map((slot) => ({
			slotKey: slot.slotKey || "-",
			isCurrent: slot.slotKey === currentSlotKey,
			saveVersion: slot.saveVersion !== undefined ? slot.saveVersion : "-",
			level: getSummaryValue(slot, "level"),
			gold: getSummaryValue(slot, "gold"),
			inventoryItems: getSummaryValue(slot, "inventoryItems"),
			storageItems: getSummaryValue(slot, "storageItems"),
			source: slot.source || "-",
			updatedAt: slot.updatedAt || null,
			note: slot.note || "",
		}));
	}

	async function listBackendSaveSlots(options) {
		if (!window.RpgGameApi || typeof window.RpgGameApi.listGameSaveSlots !== "function") {
			throw new Error("RpgGameApi.listGameSaveSlots 함수를 찾을 수 없습니다.");
		}
		const opts = options || {};
		const response = await window.RpgGameApi.listGameSaveSlots({
			timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
		});
		if (opts.log !== false) {
			const slots = response && response.payload ? response.payload.slots : [];
			console.log("[Upgrade RPG] backend save slots loaded", {
				count: response && response.payload ? response.payload.count : null,
				slots,
			});
			const rows = getSlotRows(slots);
			if (rows.length && console.table) console.table(rows);
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
	z-index: 100180;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 20px;
	background: rgba(2, 6, 23, 0.72);
	backdrop-filter: blur(4px);
	box-sizing: border-box;
}
#${MODAL_ID}[data-hidden="true"] { display: none; }
#${MODAL_ID} .save-slots-modal-panel {
	width: min(760px, calc(100vw - 40px));
	max-height: min(680px, calc(100vh - 40px));
	overflow: auto;
	box-sizing: border-box;
	border: 1px solid rgba(148, 163, 184, 0.38);
	border-radius: 14px;
	background: rgba(10, 15, 28, 0.96);
	box-shadow: 0 24px 80px rgba(0, 0, 0, 0.55);
	color: #f8fafc;
	font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
#${MODAL_ID} .save-slots-modal-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 12px;
	padding: 16px 18px 12px;
	border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}
#${MODAL_ID} .save-slots-modal-title { font-size: 16px; font-weight: 800; }
#${MODAL_ID} .save-slots-modal-close {
	border: 1px solid rgba(255, 255, 255, 0.16);
	border-radius: 8px;
	background: rgba(255, 255, 255, 0.08);
	color: #f8fafc;
	font-weight: 800;
	cursor: pointer;
	padding: 5px 10px;
}
#${MODAL_ID} .save-slots-modal-body { padding: 16px 18px 18px; }
#${MODAL_ID} .save-slots-modal-note {
	margin-bottom: 12px;
	padding: 10px 12px;
	border-radius: 10px;
	background: rgba(59, 130, 246, 0.12);
	border: 1px solid rgba(59, 130, 246, 0.25);
	color: #bfdbfe;
	font-size: 13px;
	line-height: 1.45;
}
#${MODAL_ID} .save-slots-modal-warning {
	margin-bottom: 12px;
	padding: 10px 12px;
	border-radius: 10px;
	background: rgba(248, 113, 113, 0.13);
	border: 1px solid rgba(248, 113, 113, 0.30);
	color: #fecaca;
	font-size: 13px;
	line-height: 1.45;
}
#${MODAL_ID} .save-slots-modal-table-wrap {
	border: 1px solid rgba(148, 163, 184, 0.22);
	border-radius: 10px;
	overflow: auto;
}
#${MODAL_ID} table {
	width: 100%;
	border-collapse: collapse;
	font-size: 12px;
}
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
#${MODAL_ID} .save-slots-modal-empty {
	padding: 12px;
	color: #fde68a;
	font-size: 13px;
	background: rgba(245, 158, 11, 0.10);
}
#${MODAL_ID} .save-slots-modal-actions {
	display: flex;
	flex-wrap: wrap;
	justify-content: flex-end;
	gap: 8px;
	margin-top: 14px;
}
#${MODAL_ID} .save-slots-modal-actions button {
	border: 1px solid rgba(255, 255, 255, 0.18);
	border-radius: 8px;
	background: rgba(255, 255, 255, 0.08);
	color: #f8fafc;
	font-weight: 800;
	cursor: pointer;
	padding: 8px 12px;
}
#${MODAL_ID} .save-slots-modal-actions button[data-primary="true"] {
	border-color: rgba(34, 197, 94, 0.65);
	background: rgba(34, 197, 94, 0.18);
	color: #bbf7d0;
}
`;
		document.head.appendChild(style);
	}

	function closeBackendSaveSlotsModal() {
		const modal = document.getElementById(MODAL_ID);
		if (modal) modal.dataset.hidden = "true";
		return { ok: true, closed: true };
	}

	function renderSlotRows(slots) {
		const rows = getSlotRows(slots);
		if (!rows.length) {
			return `<div class="save-slots-modal-empty">아직 DB에 저장된 세이브 슬롯이 없습니다. 성장/시스템 → 수동 저장 또는 SAVE DATA → sync DB를 먼저 실행하세요.</div>`;
		}
		return `
			<div class="save-slots-modal-table-wrap">
				<table>
					<thead>
						<tr><th>슬롯</th><th>버전</th><th>레벨</th><th>골드</th><th>인벤</th><th>창고</th><th>출처</th><th>수정 시각</th></tr>
					</thead>
					<tbody>
						${rows.map((row) => `
							<tr title="${escapeHtml(row.note)}">
								<td>${escapeHtml(row.slotKey)}${row.isCurrent ? " <strong>(현재 캐릭터)</strong>" : ""}</td>
								<td>${escapeHtml(formatValue(row.saveVersion))}</td>
								<td>${escapeHtml(formatValue(row.level))}</td>
								<td>${escapeHtml(formatValue(row.gold))}</td>
								<td>${escapeHtml(formatValue(row.inventoryItems))}</td>
								<td>${escapeHtml(formatValue(row.storageItems))}</td>
								<td>${escapeHtml(formatValue(row.source))}</td>
								<td>${escapeHtml(formatClock(row.updatedAt))}</td>
							</tr>
						`).join("")}
					</tbody>
				</table>
			</div>
		`;
	}

	async function openBackendSaveSlotsModal(options) {
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
			<div class="save-slots-modal-panel" role="dialog" aria-modal="true" aria-label="DB 세이브 슬롯 목록">
				<div class="save-slots-modal-header">
					<div class="save-slots-modal-title">DB 세이브 슬롯 목록</div>
					<button type="button" class="save-slots-modal-close" data-action="close">닫기</button>
				</div>
				<div class="save-slots-modal-body">
					<div class="save-slots-modal-note">DB에 저장된 세이브 슬롯 목록만 조회합니다. 게임 세이브를 바꾸거나 복구하지 않습니다.</div>
					<div>불러오는 중...</div>
				</div>
			</div>
		`;
		modal.onclick = async (event) => {
			const action = event.target && event.target.getAttribute ? event.target.getAttribute("data-action") : null;
			if (action === "close") closeBackendSaveSlotsModal();
			if (action === "refresh") await openBackendSaveSlotsModal(opts);
		};

		let response = null;
		let error = null;
		try {
			response = await listBackendSaveSlots({ timeoutMs: opts.timeoutMs, log: opts.log });
		} catch (err) {
			error = err && err.message ? err.message : String(err);
		}

		const body = modal.querySelector(".save-slots-modal-body");
		if (!body) return { ok: false, error: "modal body missing" };
		if (error) {
			body.innerHTML = `
				<div class="save-slots-modal-warning">DB 세이브 슬롯 목록을 불러오지 못했습니다.</div>
				<div style="color:#fecaca; font-size:13px;">${escapeHtml(error)}</div>
				<div class="save-slots-modal-actions"><button type="button" data-action="close">닫기</button></div>
			`;
			return { ok: false, error };
		}

		const payload = response && response.payload ? response.payload : { count: 0, slots: [] };
		body.innerHTML = `
			<div class="save-slots-modal-note">총 ${escapeHtml(formatValue(payload.count))}개 캐릭터 슬롯이 DB에 있습니다. 자동 저장은 현재 선택한 캐릭터(${escapeHtml(getCurrentBackendSlotKey())})에만 반영됩니다.</div>
			${renderSlotRows(payload.slots)}
			<div class="save-slots-modal-actions">
				<button type="button" data-action="close">닫기</button>
				<button type="button" data-action="refresh" data-primary="true">새로고침</button>
			</div>
		`;
		return { ok: true, response, slots: payload.slots || [] };
	}

	async function checkBackendSaveSlotsReady(options) {
		const apiReady = !!(window.RpgGameApi && typeof window.RpgGameApi.listGameSaveSlots === "function");
		const result = {
			ok: apiReady,
			version: VERSION,
			apiReady,
			modalReady: typeof document !== "undefined",
		};
		if (!options || options.log !== false) console.log("[Upgrade RPG] backend save slots check", result);
		return result;
	}

	window.RpgBackendSaveDataSlots = {
		VERSION,
		MODAL_ID,
		listBackendSaveSlots,
		openBackendSaveSlotsModal,
		closeBackendSaveSlotsModal,
		checkBackendSaveSlotsReady,
	};
	window.listBackendSaveSlots = listBackendSaveSlots;
	window.openBackendSaveSlotsModal = openBackendSaveSlotsModal;
	window.closeBackendSaveSlotsModal = closeBackendSaveSlotsModal;
	window.checkBackendSaveSlotsReady = checkBackendSaveSlotsReady;
})();
