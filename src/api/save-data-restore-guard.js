(function () {
	"use strict";

	const VERSION = "v106.backend-save-data-restore-guard";
	const LOCAL_SAVE_KEY = "idleRpgSaveV22";
	const DEFAULT_SLOT_KEY = "default";
	const DEFAULT_TIMEOUT_MS = 3000;
	const BACKUP_INDEX_KEY = "upgradeRpgBackendSaveRestoreBackups";
	const RESTORE_STATUS_KEY = "upgradeRpgBackendSaveRestoreStatus";
	const MAX_BACKUPS = 5;
	const MODAL_ID = "backend-save-restore-preview-modal";
	const STYLE_ID = "backend-save-restore-preview-style";

	function getLocalSaveKey(options) {
		return (options && options.saveKey) || window.UPGRADE_RPG_LOCAL_SAVE_KEY || LOCAL_SAVE_KEY;
	}

	function nowIso() {
		return new Date().toISOString();
	}

	function readStorage(key) {
		try {
			return window.localStorage ? window.localStorage.getItem(key) : null;
		} catch (error) {
			return null;
		}
	}

	function writeStorage(key, value) {
		try {
			if (window.localStorage) window.localStorage.setItem(key, value);
			return true;
		} catch (error) {
			console.warn("[Upgrade RPG] localStorage write failed", key, error);
			return false;
		}
	}

	function removeStorage(key) {
		try {
			if (window.localStorage) window.localStorage.removeItem(key);
		} catch (error) {
			// backup trim 실패는 복구 흐름을 막지 않습니다.
		}
	}

	function readJsonStorage(key, fallback) {
		const raw = readStorage(key);
		if (!raw) return fallback;
		try {
			return JSON.parse(raw);
		} catch (error) {
			return fallback;
		}
	}

	function writeJsonStorage(key, value) {
		return writeStorage(key, JSON.stringify(value));
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
		if (Array.isArray(value)) return value.join(", ") || "-";
		if (value === null || value === undefined || value === "") return "-";
		if (typeof value === "object") {
			try {
				return JSON.stringify(value);
			} catch (error) {
				return String(value);
			}
		}
		return String(value);
	}

	function summarizeForModal(summary) {
		const source = summary || {};
		return [
			["레벨", source.level],
			["골드", source.gold],
			["세이브 버전", source.saveVersion],
			["캐릭터", source.currentCharacterId],
			["필드", source.currentZoneIndex],
			["인벤토리", source.inventoryItems],
			["창고", source.storageItems],
			["장착", source.equippedSlots],
		];
	}

	function readBackupIndex() {
		const value = readJsonStorage(BACKUP_INDEX_KEY, []);
		return Array.isArray(value) ? value : [];
	}

	function writeBackupIndex(index) {
		return writeJsonStorage(BACKUP_INDEX_KEY, Array.isArray(index) ? index : []);
	}

	function trimBackupIndex(index) {
		const sorted = (Array.isArray(index) ? index : [])
			.filter((item) => item && item.key)
			.sort((a, b) => String(b.createdAt || "").localeCompare(String(a.createdAt || "")));
		const keep = sorted.slice(0, MAX_BACKUPS);
		const remove = sorted.slice(MAX_BACKUPS);
		remove.forEach((item) => removeStorage(item.key));
		writeBackupIndex(keep);
		return keep;
	}

	function createLocalSaveBackupBeforeRestore(options) {
		const opts = options || {};
		const saveKey = getLocalSaveKey(opts);
		const local = window.readLocalSaveSnapshot
			? window.readLocalSaveSnapshot(saveKey)
			: { exists: !!readStorage(saveKey), raw: readStorage(saveKey), snapshot: null, error: null };
		if (!local.exists || !local.raw) {
			return { ok: true, skipped: true, reason: "local_missing", saveKey };
		}
		const createdAt = nowIso();
		const safeStamp = createdAt.replace(/[:.]/g, "-");
		const backupKey = `${saveKey}.backup.beforeBackendRestore.${safeStamp}`;
		const backup = {
			version: VERSION,
			createdAt,
			reason: opts.reason || "before-backend-restore",
			saveKey,
			raw: local.raw,
			summary: window.summarizeSaveSnapshotForPreview ? window.summarizeSaveSnapshotForPreview(local.snapshot) : null,
		};
		if (!writeJsonStorage(backupKey, backup)) {
			return { ok: false, skipped: false, reason: "backup_write_failed", saveKey, backupKey };
		}
		const index = readBackupIndex();
		index.unshift({
			key: backupKey,
			createdAt,
			reason: backup.reason,
			saveKey,
			summary: backup.summary,
		});
		trimBackupIndex(index);
		return { ok: true, skipped: false, saveKey, backupKey, backup };
	}

	function listBackendSaveRestoreBackups() {
		return readBackupIndex().map((item) => ({ ...item }));
	}

	function getBackendSaveRestoreStatus() {
		return readJsonStorage(RESTORE_STATUS_KEY, {
			ok: null,
			state: "never_restored",
			updatedAt: null,
			backupKey: null,
			error: null,
		});
	}

	function setBackendSaveRestoreStatus(status) {
		const next = {
			ok: status.ok === undefined || status.ok === null ? null : !!status.ok,
			state: status.state || (status.ok ? "restored_needs_reload" : "failed"),
			updatedAt: nowIso(),
			backupKey: status.backupKey || null,
			saveKey: status.saveKey || getLocalSaveKey(),
			slotKey: status.slotKey || DEFAULT_SLOT_KEY,
			recommendation: status.recommendation || null,
			diffCount: status.diffCount !== undefined ? status.diffCount : null,
			error: status.error || null,
		};
		writeJsonStorage(RESTORE_STATUS_KEY, next);
		try {
			window.dispatchEvent(new CustomEvent("upgrade-rpg:backend-save-restore", { detail: next }));
		} catch (error) {
			// 자동 새로고침이 없는 환경에서는 상태 저장만 사용합니다.
		}
		return next;
	}

	function getBackendSnapshotFromPreview(preview) {
		const payload = preview && preview.backendResponse && preview.backendResponse.payload;
		if (payload && payload.snapshot) return payload.snapshot;
		const dataPayload = preview && preview.backendResponse && preview.backendResponse.data && preview.backendResponse.data.payload;
		if (dataPayload && dataPayload.snapshot) return dataPayload.snapshot;
		return null;
	}

	function shouldAskConfirm(options) {
		if (options && options.skipConfirm) return false;
		if (options && options.confirmText === "RESTORE") return false;
		return true;
	}

	function confirmRestore(preview, options) {
		if (!shouldAskConfirm(options)) return true;
		if (typeof window.confirm !== "function") return false;
		const diffCount = preview && preview.comparison ? preview.comparison.diffCount : "?";
		const sameRaw = preview && preview.comparison ? preview.comparison.sameRawSnapshot : false;
		return window.confirm(
			[
				"DB 세이브를 현재 브라우저 localStorage에 복구할까요?",
				"",
				`추천 상태: ${preview.recommendation}`,
				`차이 개수: ${diffCount}`,
				`원본 완전 동일: ${sameRaw}`,
				"",
				"현재 localStorage 세이브는 자동 백업한 뒤 DB 세이브로 교체됩니다.",
				"적용하려면 복구 후 새로고침이 필요합니다.",
			].join("\n"),
		);
	}

	async function restoreBackendSaveSnapshotToLocal(options) {
		const opts = options || {};
		const saveKey = getLocalSaveKey(opts);
		if (!window.previewBackendSaveSnapshot || typeof window.previewBackendSaveSnapshot !== "function") {
			throw new Error("previewBackendSaveSnapshot 함수를 찾을 수 없습니다.");
		}
		const preview = await window.previewBackendSaveSnapshot({
			saveKey,
			slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
			timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
			log: opts.log,
		});
		if (!preview.backend.exists) {
			const status = setBackendSaveRestoreStatus({
				ok: false,
				state: "failed_backend_empty",
				saveKey,
				slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
				recommendation: preview.recommendation,
				diffCount: preview.comparison ? preview.comparison.diffCount : null,
				error: "백엔드 DB에 복구할 세이브가 없습니다. 먼저 수동 저장 또는 sync DB를 실행하세요.",
			});
			return { ok: false, status, preview };
		}
		const backendSnapshot = getBackendSnapshotFromPreview(preview);
		if (!backendSnapshot || typeof backendSnapshot !== "object") {
			const status = setBackendSaveRestoreStatus({
				ok: false,
				state: "failed_invalid_backend_snapshot",
				saveKey,
				slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
				error: "백엔드 세이브 스냅샷을 읽을 수 없습니다.",
			});
			return { ok: false, status, preview };
		}
		if (!confirmRestore(preview, opts)) {
			const status = setBackendSaveRestoreStatus({
				ok: null,
				state: "cancelled_by_user",
				saveKey,
				slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
				recommendation: preview.recommendation,
				diffCount: preview.comparison ? preview.comparison.diffCount : null,
			});
			return { ok: false, cancelled: true, status, preview };
		}

		const backupResult = createLocalSaveBackupBeforeRestore({ saveKey, reason: "before-backend-restore" });
		if (backupResult.ok === false) {
			const status = setBackendSaveRestoreStatus({
				ok: false,
				state: "failed_backup_write",
				saveKey,
				slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
				error: "기존 localStorage 세이브 백업에 실패해서 복구를 중단했습니다.",
			});
			return { ok: false, status, preview, backupResult };
		}

		const raw = JSON.stringify(backendSnapshot);
		if (!writeStorage(saveKey, raw)) {
			const status = setBackendSaveRestoreStatus({
				ok: false,
				state: "failed_local_write",
				saveKey,
				slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
				backupKey: backupResult.backupKey,
				error: "DB 세이브를 localStorage에 쓰지 못했습니다.",
			});
			return { ok: false, status, preview, backupResult };
		}

		const status = setBackendSaveRestoreStatus({
			ok: true,
			state: "restored_needs_reload",
			saveKey,
			slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
			backupKey: backupResult.backupKey || null,
			recommendation: preview.recommendation,
			diffCount: preview.comparison ? preview.comparison.diffCount : null,
		});
		if (typeof addLog === "function") {
			addLog("[저장] DB 세이브를 브라우저 저장값으로 복구했습니다. 새로고침하면 게임에 적용됩니다.", true);
		}
		if (opts.reload) window.location.reload();
		return { ok: true, status, preview, backupResult, needsReload: !opts.reload };
	}

	function restoreBackendSaveBackupToLocal(backupKey, options) {
		const opts = options || {};
		const backups = readBackupIndex();
		const selectedKey = backupKey || (backups[0] && backups[0].key);
		if (!selectedKey) {
			return { ok: false, error: "복구할 백업이 없습니다." };
		}
		const backup = readJsonStorage(selectedKey, null);
		if (!backup || !backup.raw || !backup.saveKey) {
			return { ok: false, error: "백업 데이터를 읽을 수 없습니다.", backupKey: selectedKey };
		}
		if (!opts.skipConfirm && typeof window.confirm === "function") {
			const ok = window.confirm(`백업 세이브로 되돌릴까요?\n\n백업 시각: ${formatClock(backup.createdAt)}\n저장 키: ${backup.saveKey}\n\n되돌린 뒤 새로고침이 필요합니다.`);
			if (!ok) return { ok: false, cancelled: true, backupKey: selectedKey };
		}
		if (!writeStorage(backup.saveKey, backup.raw)) {
			return { ok: false, error: "백업을 localStorage에 쓰지 못했습니다.", backupKey: selectedKey };
		}
		const status = setBackendSaveRestoreStatus({
			ok: true,
			state: "backup_restored_needs_reload",
			backupKey: selectedKey,
			saveKey: backup.saveKey,
		});
		if (opts.reload) window.location.reload();
		return { ok: true, status, backupKey: selectedKey, backup, needsReload: !opts.reload };
	}

	function ensureModalStyle() {
		if (document.getElementById(STYLE_ID)) return;
		const style = document.createElement("style");
		style.id = STYLE_ID;
		style.textContent = `
#${MODAL_ID} {
	position: fixed;
	inset: 0;
	z-index: 100200;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 20px;
	background: rgba(2, 6, 23, 0.72);
	backdrop-filter: blur(4px);
	box-sizing: border-box;
}
#${MODAL_ID}[data-hidden="true"] { display: none; }
#${MODAL_ID} .save-restore-modal-panel {
	width: min(760px, calc(100vw - 40px));
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
#${MODAL_ID} .save-restore-modal-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 12px;
	padding: 16px 18px 12px;
	border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}
#${MODAL_ID} .save-restore-modal-title {
	font-size: 16px;
	font-weight: 800;
}
#${MODAL_ID} .save-restore-modal-close {
	border: 1px solid rgba(255, 255, 255, 0.16);
	border-radius: 8px;
	background: rgba(255, 255, 255, 0.08);
	color: #f8fafc;
	font-weight: 800;
	cursor: pointer;
	padding: 5px 10px;
}
#${MODAL_ID} .save-restore-modal-body { padding: 16px 18px 18px; }
#${MODAL_ID} .save-restore-modal-note {
	margin-bottom: 12px;
	padding: 10px 12px;
	border-radius: 10px;
	background: rgba(59, 130, 246, 0.12);
	border: 1px solid rgba(59, 130, 246, 0.25);
	color: #bfdbfe;
	font-size: 13px;
	line-height: 1.45;
}
#${MODAL_ID} .save-restore-modal-grid {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: 12px;
	margin-bottom: 12px;
}
#${MODAL_ID} .save-restore-modal-card {
	border: 1px solid rgba(148, 163, 184, 0.22);
	border-radius: 10px;
	background: rgba(15, 23, 42, 0.78);
	padding: 10px 12px;
}
#${MODAL_ID} .save-restore-modal-card h4 {
	margin: 0 0 8px;
	font-size: 13px;
	color: #e2e8f0;
}
#${MODAL_ID} .save-restore-modal-card dl {
	display: grid;
	grid-template-columns: 90px minmax(0, 1fr);
	gap: 4px 8px;
	margin: 0;
	font-size: 12px;
}
#${MODAL_ID} .save-restore-modal-card dt { color: #94a3b8; }
#${MODAL_ID} .save-restore-modal-card dd {
	margin: 0;
	color: #f8fafc;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}
#${MODAL_ID} .save-restore-modal-diffs {
	margin-top: 10px;
	border: 1px solid rgba(148, 163, 184, 0.22);
	border-radius: 10px;
	overflow: hidden;
}
#${MODAL_ID} .save-restore-modal-diffs table {
	width: 100%;
	border-collapse: collapse;
	font-size: 12px;
}
#${MODAL_ID} .save-restore-modal-diffs th,
#${MODAL_ID} .save-restore-modal-diffs td {
	padding: 7px 9px;
	border-bottom: 1px solid rgba(148, 163, 184, 0.16);
	text-align: left;
	vertical-align: top;
}
#${MODAL_ID} .save-restore-modal-diffs th {
	background: rgba(15, 23, 42, 0.95);
	color: #cbd5e1;
}
#${MODAL_ID} .save-restore-modal-diffs td { color: #e2e8f0; }
#${MODAL_ID} .save-restore-modal-empty {
	padding: 12px;
	color: #bbf7d0;
	font-size: 13px;
	background: rgba(34, 197, 94, 0.10);
}
#${MODAL_ID} .save-restore-modal-actions {
	display: flex;
	flex-wrap: wrap;
	justify-content: flex-end;
	gap: 8px;
	margin-top: 14px;
}
#${MODAL_ID} .save-restore-modal-actions button {
	border: 1px solid rgba(255, 255, 255, 0.18);
	border-radius: 8px;
	background: rgba(255, 255, 255, 0.08);
	color: #f8fafc;
	font-weight: 800;
	cursor: pointer;
	padding: 8px 12px;
}
#${MODAL_ID} .save-restore-modal-actions button[data-primary="true"] {
	border-color: rgba(34, 197, 94, 0.65);
	background: rgba(34, 197, 94, 0.18);
	color: #bbf7d0;
}
#${MODAL_ID} .save-restore-modal-actions button[data-danger="true"] {
	border-color: rgba(248, 113, 113, 0.62);
	background: rgba(248, 113, 113, 0.15);
	color: #fecaca;
}
#${MODAL_ID} .save-restore-modal-actions button:disabled {
	opacity: 0.45;
	cursor: not-allowed;
}
@media (max-width: 720px) {
	#${MODAL_ID} .save-restore-modal-grid { grid-template-columns: 1fr; }
}
`;
		document.head.appendChild(style);
	}

	function renderSummaryRows(summary) {
		return summarizeForModal(summary).map(([label, value]) => `<dt>${label}</dt><dd>${formatValue(value)}</dd>`).join("");
	}

	function renderDiffRows(diffs) {
		if (!diffs || !diffs.length) {
			return `<div class="save-restore-modal-empty">주요 요약 차이가 없습니다. 원본 JSON까지 같으면 완전히 같은 세이브입니다.</div>`;
		}
		return `
			<table>
				<thead><tr><th>항목</th><th>현재 localStorage</th><th>백엔드 DB</th></tr></thead>
				<tbody>
					${diffs.map((diff) => `<tr><td>${diff.label}</td><td>${formatValue(diff.local)}</td><td>${formatValue(diff.backend)}</td></tr>`).join("")}
				</tbody>
			</table>
		`;
	}

	function closeBackendSaveRestorePreviewModal() {
		const modal = document.getElementById(MODAL_ID);
		if (modal) modal.dataset.hidden = "true";
		return { ok: true, closed: true };
	}

	async function openBackendSaveRestorePreviewModal(options) {
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
			<div class="save-restore-modal-panel" role="dialog" aria-modal="true" aria-label="DB 세이브 복구 미리보기">
				<div class="save-restore-modal-header">
					<div class="save-restore-modal-title">DB 세이브 복구 미리보기</div>
					<button type="button" class="save-restore-modal-close" data-action="close">닫기</button>
				</div>
				<div class="save-restore-modal-body">
					<div class="save-restore-modal-note">DB 세이브를 게임에 바로 덮어쓰지 않고, 현재 localStorage와 먼저 비교하는 중입니다.</div>
					<div>불러오는 중...</div>
				</div>
			</div>
		`;
		modal.addEventListener("click", (event) => {
			const action = event.target && event.target.getAttribute ? event.target.getAttribute("data-action") : null;
			if (action === "close") closeBackendSaveRestorePreviewModal();
		}, { once: true });

		let preview = null;
		let error = null;
		try {
			preview = await window.previewBackendSaveSnapshot({
				saveKey: getLocalSaveKey(opts),
				slotKey: opts.slotKey || DEFAULT_SLOT_KEY,
				timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
				log: opts.log,
			});
		} catch (err) {
			error = err && err.message ? err.message : String(err);
		}

		if (error) {
			modal.querySelector(".save-restore-modal-body").innerHTML = `
				<div class="save-restore-modal-note">백엔드 세이브 미리보기를 불러오지 못했습니다.</div>
				<div style="color:#fecaca; font-size:13px;">${error}</div>
				<div class="save-restore-modal-actions"><button type="button" data-action="close">닫기</button></div>
			`;
			modal.addEventListener("click", (event) => {
				if (event.target && event.target.getAttribute && event.target.getAttribute("data-action") === "close") closeBackendSaveRestorePreviewModal();
			});
			return { ok: false, error };
		}

		const comparison = preview.comparison || {};
		const canRestore = !!preview.backend.exists;
		const note = canRestore
			? `추천 상태: ${preview.recommendation} / 차이 개수: ${comparison.diffCount} / 원본 완전 동일: ${comparison.sameRawSnapshot}`
			: "백엔드 DB에 복구할 세이브가 없습니다. 먼저 수동 저장 또는 sync DB를 실행하세요.";
		modal.querySelector(".save-restore-modal-body").innerHTML = `
			<div class="save-restore-modal-note">${note}<br>복구를 누르면 현재 localStorage를 자동 백업한 뒤 DB 세이브로 교체합니다. 실제 게임 적용은 새로고침 후 반영됩니다.</div>
			<div class="save-restore-modal-grid">
				<div class="save-restore-modal-card"><h4>현재 localStorage</h4><dl>${renderSummaryRows(preview.local.summary)}</dl></div>
				<div class="save-restore-modal-card"><h4>백엔드 DB</h4><dl>${renderSummaryRows(preview.backend.summary)}</dl></div>
			</div>
			<div class="save-restore-modal-diffs">${renderDiffRows(comparison.diffs)}</div>
			<div class="save-restore-modal-actions">
				<button type="button" data-action="close">닫기</button>
				<button type="button" data-action="reload">새로고침</button>
				<button type="button" data-action="restore" data-danger="true" ${canRestore ? "" : "disabled"}>DB 세이브로 복구</button>
			</div>
		`;
		modal.addEventListener("click", async (event) => {
			const action = event.target && event.target.getAttribute ? event.target.getAttribute("data-action") : null;
			if (!action) return;
			if (action === "close") closeBackendSaveRestorePreviewModal();
			if (action === "reload") window.location.reload();
			if (action === "restore") {
				const button = event.target;
				button.disabled = true;
				button.textContent = "복구 중...";
				const result = await restoreBackendSaveSnapshotToLocal({ ...opts, skipConfirm: true, log: false });
				button.textContent = result.ok ? "복구 완료" : "복구 실패";
				const body = modal.querySelector(".save-restore-modal-body");
				const message = result.ok
					? `복구 완료. 백업 키: ${result.backupResult && result.backupResult.backupKey ? result.backupResult.backupKey : "-"}. 새로고침하면 적용됩니다.`
					: `복구 실패: ${result.status && result.status.error ? result.status.error : result.error || "unknown"}`;
				const color = result.ok ? "#bbf7d0" : "#fecaca";
				body.insertAdjacentHTML("afterbegin", `<div class="save-restore-modal-note" style="color:${color};">${message}</div>`);
			}
		});
		return { ok: true, preview };
	}

	async function checkBackendSaveRestoreGuard(options) {
		const previewReady = typeof window.previewBackendSaveSnapshot === "function";
		const bridgeReady = typeof window.loadBackendSaveSnapshot === "function" && typeof window.readLocalSaveSnapshot === "function";
		const result = {
			ok: previewReady && bridgeReady,
			version: VERSION,
			previewReady,
			bridgeReady,
			backupCount: listBackendSaveRestoreBackups().length,
			status: getBackendSaveRestoreStatus(),
		};
		if (!options || options.log !== false) console.log("[Upgrade RPG] backend save restore guard check", result);
		return result;
	}

	window.RpgBackendSaveDataRestoreGuard = {
		VERSION,
		BACKUP_INDEX_KEY,
		RESTORE_STATUS_KEY,
		createLocalSaveBackupBeforeRestore,
		listBackendSaveRestoreBackups,
		getBackendSaveRestoreStatus,
		restoreBackendSaveSnapshotToLocal,
		restoreBackendSaveBackupToLocal,
		openBackendSaveRestorePreviewModal,
		closeBackendSaveRestorePreviewModal,
		checkBackendSaveRestoreGuard,
	};
	window.createLocalSaveBackupBeforeRestore = createLocalSaveBackupBeforeRestore;
	window.listBackendSaveRestoreBackups = listBackendSaveRestoreBackups;
	window.getBackendSaveRestoreStatus = getBackendSaveRestoreStatus;
	window.restoreBackendSaveSnapshotToLocal = restoreBackendSaveSnapshotToLocal;
	window.restoreBackendSaveBackupToLocal = restoreBackendSaveBackupToLocal;
	window.openBackendSaveRestorePreviewModal = openBackendSaveRestorePreviewModal;
	window.closeBackendSaveRestorePreviewModal = closeBackendSaveRestorePreviewModal;
	window.checkBackendSaveRestoreGuard = checkBackendSaveRestoreGuard;
})();
