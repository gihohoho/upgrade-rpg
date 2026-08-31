<template>
  <section class="admin-preview-workspace" aria-labelledby="admin-preview-title">
    <div class="admin-preview-workspace__header">
      <div>
        <p class="admin-readonly-panel__eyebrow">v383 · guarded confirmation workspace</p>
        <h3 id="admin-preview-title">변경 전 안전 미리보기</h3>
        <p>
          생성·수정·되돌리기 요청을 <code>dryRun: true</code>로만 검사합니다.
          서버가 계산한 diff, stale 충돌과 차단 사유를 확인할 수 있지만 DB에는 적용되지 않습니다.
        </p>
      </div>
      <span class="admin-preview-lock"><i aria-hidden="true" /> Apply 쓰기 잠금</span>
    </div>

    <div class="admin-preview-boundary" role="note">
      <strong>안전 경계</strong>
      <span>최신 Preview 재검증과 확인 입력 경계만 준비했습니다. Apply endpoint와 dev key 헤더는 연결하지 않았고 모든 POST는 Preview 전용 경로로만 제한됩니다.</span>
    </div>

    <nav class="admin-preview-tabs" aria-label="관리자 Preview 종류">
      <button type="button" :class="{ 'is-active': activeTab === 'create' }" @click="setTab('create')">신규 생성</button>
      <button type="button" :class="{ 'is-active': activeTab === 'edit' }" @click="setTab('edit')">선택 row 수정</button>
      <button type="button" :class="{ 'is-active': activeTab === 'rollback' }" @click="setTab('rollback')">변경 이력 되돌리기</button>
    </nav>

    <form v-if="activeTab === 'create'" class="admin-preview-form" @submit.prevent="runCreatePreview">
      <div class="admin-preview-form__intro">
        <div>
          <strong>{{ domainLabel || domain || '도메인 미선택' }}</strong>
          <p>위 도메인 목록에서 대상을 고르면 서버의 생성 설계를 불러옵니다.</p>
        </div>
        <button type="button" class="admin-readonly-panel__button admin-readonly-panel__button--secondary" :disabled="!domain || blueprintStatus === 'loading'" @click="loadBlueprint">
          {{ blueprintStatus === 'loading' ? '설계 불러오는 중...' : '생성 설계 다시 불러오기' }}
        </button>
      </div>

      <div v-if="!domain" class="admin-readonly-panel__state" data-state="idle">먼저 위에서 마스터 데이터 도메인을 선택해 주세요.</div>
      <div v-else-if="blueprintStatus === 'loading'" class="admin-readonly-panel__state" data-state="loading">생성 필드와 관계 선택지를 불러오고 있습니다.</div>
      <div v-else-if="blueprintStatus === 'error'" class="admin-readonly-panel__state" data-state="error"><strong>생성 설계 조회 오류</strong><p>{{ blueprintError }}</p></div>
      <template v-else-if="blueprintStatus === 'success' && blueprint">
        <div class="admin-preview-summary-strip">
          <span>필드 {{ blueprintFields.length }}개</span>
          <span>필수 {{ blueprint.requiredFields?.length || 0 }}개</span>
          <span>고유값 {{ blueprint.uniqueFields?.length || 0 }}개</span>
          <span :data-tone="blueprint.createApplyUnlocked ? 'ready' : 'blocked'">{{ blueprint.createApplyUnlocked ? '서버 적용 허용 도메인' : '서버 적용 잠금 도메인' }}</span>
        </div>

        <div class="admin-preview-field-grid">
          <label v-for="field in blueprintFields" :key="field.key" class="admin-preview-field">
            <span>
              {{ field.label || field.key }}
              <small v-if="field.required">필수</small>
              <small v-if="field.unique">고유</small>
            </span>
            <select v-if="relationOptions(field).length" v-model="createDraft[field.key]" :required="field.required" :disabled="admin.previewBusy">
              <option v-for="option in relationOptions(field)" :key="String(option.value)" :value="option.value">{{ option.label || option.value }}</option>
            </select>
            <select v-else-if="isBooleanField(field)" v-model="createDraft[field.key]" :disabled="admin.previewBusy">
              <option :value="true">예</option>
              <option :value="false">아니오</option>
            </select>
            <input
              v-else
              v-model="createDraft[field.key]"
              :type="isNumberField(field) ? 'number' : 'text'"
              :step="isNumberField(field) ? 'any' : undefined"
              :required="field.required"
              :disabled="admin.previewBusy"
              :placeholder="field.note || field.key"
            />
            <small v-if="field.note">{{ field.note }}</small>
          </label>
        </div>

        <label class="admin-preview-reason">
          <span>검사 사유 <small>선택</small></span>
          <input v-model.trim="createReason" type="text" maxlength="500" placeholder="예: 신규 보스 데이터 사전 검증" :disabled="admin.previewBusy" />
        </label>
        <div class="admin-preview-actions">
          <button type="button" class="admin-readonly-panel__button admin-readonly-panel__button--secondary" :disabled="admin.previewBusy" @click="resetCreateDraft">기본값으로 되돌리기</button>
          <button type="submit" class="admin-readonly-panel__button" :disabled="admin.previewBusy || !blueprintFields.length">
            {{ admin.previewBusy ? '서버에서 검증 중...' : '생성 초안 Preview' }}
          </button>
        </div>
      </template>
    </form>

    <form v-else-if="activeTab === 'edit'" class="admin-preview-form" @submit.prevent="runEditPreview">
      <div class="admin-preview-form__intro">
        <div>
          <strong>{{ rowTitle || (rowId ? `#${rowId}` : 'row 미선택') }}</strong>
          <p>{{ domainLabel || domain || '도메인을 먼저 선택하세요.' }} · 체크한 필드만 stale 기준값과 함께 검사합니다.</p>
        </div>
        <button type="button" class="admin-readonly-panel__button admin-readonly-panel__button--secondary" :disabled="!domain || !rowId || editStatus === 'loading'" @click="loadEditBaseline">
          {{ editStatus === 'loading' ? '기준값 불러오는 중...' : '현재값 다시 불러오기' }}
        </button>
      </div>

      <div v-if="!domain || !rowId" class="admin-readonly-panel__state" data-state="idle">위 카탈로그에서 수정할 row의 <strong>상세 보기</strong>를 눌러 주세요.</div>
      <div v-else-if="editStatus === 'loading'" class="admin-readonly-panel__state" data-state="loading">서버의 현재값을 stale 비교 기준으로 불러오고 있습니다.</div>
      <div v-else-if="editStatus === 'error'" class="admin-readonly-panel__state" data-state="error"><strong>편집 기준 조회 오류</strong><p>{{ editError }}</p></div>
      <template v-else-if="editStatus === 'success' && editFields.length">
        <p class="admin-preview-help">변경할 필드를 체크한 뒤 새 값을 입력하세요. 허용 필드와 관계 무결성은 서버 Preview가 최종 판정합니다.</p>
        <div class="admin-preview-edit-list">
          <label v-for="field in editFields" :key="field.key" class="admin-preview-edit-row" :class="{ 'is-selected': editSelectedKeys.includes(field.key) }">
            <input v-model="editSelectedKeys" type="checkbox" :value="field.key" :disabled="admin.previewBusy" />
            <span class="admin-preview-edit-row__label"><strong>{{ field.label || field.key }}</strong><small>현재 {{ formatValue(field.value) }}</small></span>
            <select v-if="typeof field.value === 'boolean'" v-model="editDraft[field.key]" :disabled="admin.previewBusy || !editSelectedKeys.includes(field.key)">
              <option :value="true">예</option>
              <option :value="false">아니오</option>
            </select>
            <input
              v-else
              v-model="editDraft[field.key]"
              :type="typeof field.value === 'number' ? 'number' : 'text'"
              :step="typeof field.value === 'number' ? 'any' : undefined"
              :disabled="admin.previewBusy || !editSelectedKeys.includes(field.key)"
            />
          </label>
        </div>
        <label class="admin-preview-reason">
          <span>변경 사유 <small>선택</small></span>
          <input v-model.trim="editReason" type="text" maxlength="500" placeholder="예: 보스 체력 밸런스 조정 검토" :disabled="admin.previewBusy" />
        </label>
        <div class="admin-preview-actions">
          <span>{{ editSelectedKeys.length }}개 필드 선택</span>
          <button type="submit" class="admin-readonly-panel__button" :disabled="admin.previewBusy || !editSelectedKeys.length">
            {{ admin.previewBusy ? '서버에서 검증 중...' : '수정 초안 Preview' }}
          </button>
        </div>
      </template>
    </form>

    <form v-else class="admin-preview-form" @submit.prevent="runRollbackPreview">
      <div class="admin-preview-form__intro">
        <div>
          <strong>최근 관리자 변경 이력</strong>
          <p>이력의 현재 DB 일치 여부와 삭제·복원 의존성만 검사합니다.</p>
        </div>
        <button type="button" class="admin-readonly-panel__button admin-readonly-panel__button--secondary" :disabled="changeLogsStatus === 'loading'" @click="loadChangeLogs">
          {{ changeLogsStatus === 'loading' ? '이력 불러오는 중...' : '최근 이력 다시 불러오기' }}
        </button>
      </div>

      <div v-if="changeLogsStatus === 'error'" class="admin-readonly-panel__state" data-state="error"><strong>변경 이력 조회 오류</strong><p>{{ changeLogsError }}</p></div>
      <div v-else-if="changeLogsStatus === 'success' && changeLogs.length" class="admin-preview-log-list" aria-label="최근 변경 이력">
        <button
          v-for="log in changeLogs"
          :key="log.id"
          type="button"
          :class="{ 'is-selected': changeLogId === log.id }"
          @click="selectChangeLog(log)"
        >
          <span>#{{ log.id }} · {{ log.action }}</span>
          <strong>{{ log.targetType }} / {{ log.targetId }}</strong>
          <small>{{ log.changedKeyCount || 0 }}개 필드 · {{ formatDate(log.createdAt) }}</small>
        </button>
      </div>
      <div v-else-if="changeLogsStatus === 'success'" class="admin-readonly-panel__state" data-state="empty">표시할 관리자 변경 이력이 없습니다.</div>

      <div class="admin-preview-rollback-controls">
        <label class="admin-preview-field">
          <span>변경 이력 ID</span>
          <input v-model.number="changeLogId" type="number" min="1" step="1" required :disabled="admin.previewBusy" @change="loadChangeLogDetail" />
        </label>
        <fieldset>
          <legend>검사할 되돌리기 종류</legend>
          <label v-for="option in rollbackOptions" :key="option.kind" :data-available="option.available">
            <input v-model="rollbackKind" type="radio" name="rollback-kind" :value="option.kind" :disabled="admin.previewBusy || option.available === false" />
            <span><strong>{{ option.label }}</strong><small>{{ option.description }}</small></span>
            <em>{{ option.available === null ? '이력 선택 필요' : option.available ? '검사 가능' : '이력 종류 불일치' }}</em>
          </label>
        </fieldset>
      </div>

      <div v-if="changeLogDetailStatus === 'loading'" class="admin-readonly-panel__state" data-state="loading">선택한 이력의 안전 조건을 확인하고 있습니다.</div>
      <div v-else-if="changeLogDetailStatus === 'error'" class="admin-readonly-panel__state" data-state="error"><strong>이력 상세 조회 오류</strong><p>{{ changeLogDetailError }}</p></div>
      <label class="admin-preview-reason">
        <span>검사 사유 <small>선택</small></span>
        <input v-model.trim="rollbackReason" type="text" maxlength="500" placeholder="예: 최근 밸런스 변경 되돌리기 사전 검사" :disabled="admin.previewBusy" />
      </label>
      <div class="admin-preview-actions">
        <span>이 요청은 실제 삭제·복원·rollback을 실행하지 않습니다.</span>
        <button type="submit" class="admin-readonly-panel__button" :disabled="admin.previewBusy || !validChangeLogId || !rollbackKindAvailable">
          {{ admin.previewBusy ? '서버에서 검증 중...' : '되돌리기 Preview' }}
        </button>
      </div>
    </form>

    <section v-if="admin.previewError" class="admin-preview-result admin-preview-result--error" aria-live="polite">
      <strong>Preview 요청 오류</strong>
      <p>{{ admin.previewError }}</p>
    </section>

    <section v-else-if="previewPayload" class="admin-preview-result" :data-ready="previewReady" aria-live="polite">
      <div class="admin-preview-result__header">
        <div>
          <span>{{ previewReady ? '검증 통과' : '검증 차단 또는 변경 없음' }}</span>
          <h4>{{ previewTitle }}</h4>
          <p>{{ previewPayload.note || '서버 Preview 결과를 확인하세요.' }}</p>
        </div>
        <strong>{{ previewPayload.status || 'unknown' }}</strong>
      </div>

      <div class="admin-preview-safety-grid">
        <span :data-pass="previewPayload.dryRun === true"><b>dryRun</b>{{ previewPayload.dryRun === true ? 'true' : formatValue(previewPayload.dryRun) }}</span>
        <span :data-pass="previewPayload.writeBlocked === true"><b>DB write</b>{{ previewPayload.writeBlocked === true ? '차단됨' : '확인 필요' }}</span>
        <span v-for="stat in previewStats" :key="stat.label"><b>{{ stat.label }}</b>{{ stat.value }}</span>
      </div>

      <section v-if="previewChanges.length" class="admin-preview-result__section">
        <h5>변경 diff</h5>
        <div class="admin-preview-diff-table-wrap">
          <table class="admin-preview-diff-table">
            <thead><tr><th>필드</th><th>현재/이전</th><th>Preview 이후</th></tr></thead>
            <tbody>
              <tr v-for="(change, index) in previewChanges" :key="`${change.key || 'change'}-${index}`">
                <th>{{ change.label || change.key || `변경 ${index + 1}` }}</th>
                <td>{{ formatValue(change.before ?? change.current) }}</td>
                <td>{{ formatValue(change.after ?? change.rollbackTo) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="staleChanges.length" class="admin-preview-result__section admin-preview-result__section--stale">
        <h5>stale 충돌</h5>
        <p>화면을 연 뒤 서버 값이 달라졌습니다. 최신값을 다시 불러오기 전에는 적용 대상으로 사용할 수 없습니다.</p>
        <ul><li v-for="(item, index) in staleChanges" :key="`${item.key || 'stale'}-${index}`"><strong>{{ item.label || item.key }}</strong> 기준 {{ formatValue(item.base) }} · 현재 {{ formatValue(item.current) }} · 제안 {{ formatValue(item.after) }}</li></ul>
      </section>

      <section v-if="previewBlockers.length" class="admin-preview-result__section admin-preview-result__section--blocked">
        <h5>차단·검증 사유</h5>
        <ul><li v-for="(item, index) in previewBlockers" :key="`${item.key || 'blocker'}-${index}`"><strong>{{ item.label || item.key || `항목 ${index + 1}` }}</strong>{{ describeBlocker(item) }}</li></ul>
      </section>

      <section v-if="previewWarnings.length" class="admin-preview-result__section">
        <h5>서버 경고</h5>
        <ul class="admin-preview-warning-list"><li v-for="warning in previewWarnings" :key="warning">{{ translateReason(warning) }}</li></ul>
      </section>

      <div class="admin-preview-apply-preparation">
        <div>
          <strong>Apply 전 확인 절차</strong>
          <span v-if="previewReady && confirmationText">서버 확인 문구가 포함된 안전한 Preview입니다. 실제 쓰기 없이 마지막 확인 경계를 점검할 수 있습니다.</span>
          <span v-else-if="previewReady">Preview는 통과했지만 서버 확인 문구가 없어 준비 절차를 열 수 없습니다.</span>
          <span v-else>차단 사유를 해결하고 Preview를 다시 실행해야 확인 절차를 준비할 수 있습니다.</span>
        </div>
        <button
          type="button"
          class="admin-readonly-panel__button"
          :disabled="!applyGateAvailable"
          data-testid="admin-apply-gate-open"
          @click="openApplyGate"
        >
          Apply 확인 절차 준비
        </button>
      </div>
    </section>

    <AdminApplyConfirmationGate
      :open="applyGateOpen"
      :title="gatePreview?.title || previewTitle"
      :confirmation-text="gatePreview?.confirmationText || ''"
      :baseline-fingerprint="gatePreview?.baselineFingerprint || ''"
      :revalidation-state="revalidationState"
      :revalidation-message="revalidationMessage"
      @close="closeApplyGate"
      @revalidate="revalidateLatestPreview"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useAdminStore } from '@/stores';
import AdminApplyConfirmationGate from '@/components/admin/AdminApplyConfirmationGate.vue';
import type { AdminPreviewChange, AdminPreviewEnvelope, AdminPreviewKind, AdminPreviewPayload, JsonRecord } from '@/api/adminPreviewApi';

interface BlueprintOption { value: unknown; label?: string }
interface BlueprintField { key: string; label?: string; inputKind?: string; required?: boolean; unique?: boolean; futureEditable?: boolean; defaultValue?: unknown; note?: string; relation?: { options?: BlueprintOption[] } }
interface BlueprintPayload extends JsonRecord { status?: string; createApplyUnlocked?: boolean; requiredFields?: string[]; uniqueFields?: string[]; fields?: BlueprintField[]; defaultDraft?: JsonRecord }
interface DetailField { key: string; label?: string; value: unknown }
interface ChangeLogRow { id: number; action?: string; targetType?: string; targetId?: string; changedKeyCount?: number; createdAt?: string }
interface ChangeLogDetail extends JsonRecord { rollback?: { available?: boolean }; createDelete?: { available?: boolean }; createDeleteRestore?: { available?: boolean } }
type WorkspaceTab = 'create' | 'edit' | 'rollback';
type RollbackKind = Extract<AdminPreviewKind, 'rollback' | 'create-delete' | 'create-delete-restore'>;
type LoadStatus = 'idle' | 'loading' | 'success' | 'error';
type RevalidationState = 'idle' | 'checking' | 'success' | 'changed' | 'error';
type PreviewRequest =
  | { kind: 'create'; domain: string; draft: JsonRecord; reason: string }
  | { kind: 'edit'; domain: string; rowId: number; draft: JsonRecord; baseValues: JsonRecord; reason: string }
  | { kind: RollbackKind; changeLogId: number; reason: string };
interface GatePreview {
  title: string;
  confirmationText: string;
  baselineFingerprint: string;
}

const props = defineProps<{ domain: string; domainLabel?: string; rowId?: number; rowTitle?: string }>();
const admin = useAdminStore();
const activeTab = ref<WorkspaceTab>('create');

const blueprintStatus = ref<LoadStatus>('idle');
const blueprintError = ref('');
const blueprint = ref<BlueprintPayload | null>(null);
const createDraft = ref<JsonRecord>({});
const createReason = ref('');

const editStatus = ref<LoadStatus>('idle');
const editError = ref('');
const editFields = ref<DetailField[]>([]);
const editDraft = ref<JsonRecord>({});
const editBaseValues = ref<JsonRecord>({});
const editSelectedKeys = ref<string[]>([]);
const editReason = ref('');

const changeLogsStatus = ref<LoadStatus>('idle');
const changeLogsError = ref('');
const changeLogs = ref<ChangeLogRow[]>([]);
const changeLogDetailStatus = ref<LoadStatus>('idle');
const changeLogDetailError = ref('');
const changeLogDetail = ref<ChangeLogDetail | null>(null);
const changeLogId = ref<number | null>(null);
const rollbackKind = ref<RollbackKind>('rollback');
const rollbackReason = ref('');
const lastPreviewRequest = ref<PreviewRequest | null>(null);
const lastPreviewFingerprint = ref('');
const applyGateOpen = ref(false);
const gatePreview = ref<GatePreview | null>(null);
const revalidationState = ref<RevalidationState>('idle');
const revalidationMessage = ref('같은 초안을 최신 서버 상태로 다시 검증해 주세요.');

let blueprintController: AbortController | null = null;
let editController: AbortController | null = null;
let logController: AbortController | null = null;
let logDetailRequestId = 0;

const blueprintFields = computed(() => (blueprint.value?.fields || []).filter((field) => field?.key && field.futureEditable !== false));
const validChangeLogId = computed(() => Number.isInteger(Number(changeLogId.value)) && Number(changeLogId.value) > 0);
const previewPayload = computed<AdminPreviewPayload | null>(() => admin.previewResult?.payload || null);
const previewWarnings = computed(() => Array.isArray(previewPayload.value?.warnings) ? previewPayload.value!.warnings! : []);
const confirmationText = computed(() => String(previewPayload.value?.confirmTextRequired || '').trim());

const rollbackOptions = computed(() => [
  { kind: 'rollback' as const, label: '일반 수정 되돌리기', description: 'update 이력의 현재값이 변경 직후 값과 같은지 검사', available: availability('rollback') },
  { kind: 'create-delete' as const, label: '생성 row 삭제', description: 'create 이력의 row와 연결 데이터 차단 조건 검사', available: availability('createDelete') },
  { kind: 'create-delete-restore' as const, label: '삭제 row 복원', description: 'create_delete 이력의 id/code 충돌과 재검증', available: availability('createDeleteRestore') },
]);

const rollbackKindAvailable = computed(() => rollbackOptions.value.find((option) => option.kind === rollbackKind.value)?.available === true);
const previewReady = computed(() => {
  const payload = previewPayload.value;
  if (!payload) return false;
  if (admin.previewKind === 'create') return payload.createApplyReady === true;
  if (admin.previewKind === 'edit') return payload.applyReady === true || payload.editApplyReady === true;
  if (admin.previewKind === 'rollback') return payload.rollbackReady === true;
  if (admin.previewKind === 'create-delete') return payload.createDeleteReady === true;
  return payload.createDeleteRestoreReady === true;
});
const applyGateAvailable = computed(() => (
  previewReady.value
  && confirmationText.value.length > 0
  && Boolean(lastPreviewRequest.value)
  && lastPreviewFingerprint.value.length > 0
));

const previewTitle = computed(() => ({
  create: '신규 생성 초안', edit: '선택 row 수정 초안', rollback: '일반 수정 되돌리기',
  'create-delete': '생성 row 삭제', 'create-delete-restore': '삭제 row 복원',
}[admin.previewKind || 'create']));

const previewStats = computed(() => {
  const payload = previewPayload.value || {};
  const candidates = [
    ['diff', payload.diffCount], ['오류', payload.errorCount], ['stale', payload.staleCount],
    ['의존성 차단', payload.dependencyBlockerCount], ['검증 오류', payload.validationErrorCount],
  ];
  return candidates.filter((item) => item[1] !== undefined).map(([label, value]) => ({ label: String(label), value: formatValue(value) }));
});

const previewChanges = computed<AdminPreviewChange[]>(() => {
  const payload = previewPayload.value;
  if (!payload) return [];
  return firstArray(payload.acceptedFields, payload.acceptedChanges, payload.changes);
});

const staleChanges = computed<AdminPreviewChange[]>(() => firstArray(previewPayload.value?.staleChanges));
const previewBlockers = computed<AdminPreviewChange[]>(() => {
  const payload = previewPayload.value;
  if (!payload) return [];
  const dependencies = firstArray(payload.dependencyChecks).filter((item) => item && (item as JsonRecord).blocksDelete !== false);
  return [
    ...firstArray(payload.rejectedFields),
    ...firstArray(payload.rejectedChanges),
    ...firstArray(payload.currentMismatches),
    ...dependencies,
    ...firstArray(payload.validationErrors),
  ];
});

function firstArray(...values: unknown[]): AdminPreviewChange[] {
  return (values.find(Array.isArray) as AdminPreviewChange[] | undefined) || [];
}

function setTab(tab: WorkspaceTab) {
  activeTab.value = tab;
  invalidatePreview();
  if (tab === 'rollback' && changeLogsStatus.value === 'idle') void loadChangeLogs();
}

function relationOptions(field: BlueprintField) {
  return Array.isArray(field.relation?.options) ? field.relation!.options! : [];
}

function isBooleanField(field: BlueprintField) {
  return String(field.inputKind || '').includes('boolean') || typeof field.defaultValue === 'boolean';
}

function isNumberField(field: BlueprintField) {
  return /(number|integer|decimal|float)/.test(String(field.inputKind || '')) || typeof field.defaultValue === 'number';
}

function resetCreateDraft() {
  createDraft.value = { ...(blueprint.value?.defaultDraft || {}) };
  invalidatePreview();
}

async function loadBlueprint() {
  if (!props.domain) return;
  blueprintController?.abort();
  const controller = new AbortController();
  blueprintController = controller;
  blueprintStatus.value = 'loading';
  blueprintError.value = '';
  try {
    const response = await admin.fetchMasterCreateBlueprint(props.domain, { signal: controller.signal });
    if (controller.signal.aborted || blueprintController !== controller) return;
    const payload = response?.payload && typeof response.payload === 'object' ? response.payload as BlueprintPayload : null;
    blueprint.value = payload;
    blueprintStatus.value = payload?.status === 'loaded' ? 'success' : 'error';
    if (blueprintStatus.value === 'error') blueprintError.value = '선택한 도메인의 생성 설계를 불러오지 못했습니다.';
    resetCreateDraft();
  } catch (error) {
    if (controller.signal.aborted || blueprintController !== controller) return;
    blueprintStatus.value = 'error';
    blueprintError.value = formatError(error);
  }
}

async function runCreatePreview() {
  if (!props.domain || !blueprintFields.value.length) return;
  const request: PreviewRequest = { kind: 'create', domain: props.domain, draft: cloneRecord(createDraft.value), reason: createReason.value };
  await runAndRememberPreview(request);
}

async function loadEditBaseline() {
  if (!props.domain || !props.rowId) return;
  editController?.abort();
  const controller = new AbortController();
  editController = controller;
  editStatus.value = 'loading';
  editError.value = '';
  try {
    const response = await admin.fetchMasterDetail({ domain: props.domain, rowId: props.rowId }, { signal: controller.signal });
    if (controller.signal.aborted || editController !== controller) return;
    const payload = response?.payload && typeof response.payload === 'object' ? response.payload as { status?: string; fields?: DetailField[] } : null;
    const fields = Array.isArray(payload?.fields) ? payload!.fields!.filter((field) => field?.key && !isAlwaysReadOnlyField(field.key)) : [];
    editFields.value = fields;
    editDraft.value = Object.fromEntries(fields.map((field) => [field.key, field.value]));
    editBaseValues.value = Object.fromEntries(fields.map((field) => [field.key, field.value]));
    editSelectedKeys.value = [];
    editStatus.value = payload?.status === 'loaded' ? 'success' : 'error';
    if (editStatus.value === 'error') editError.value = '선택한 row의 현재값을 불러오지 못했습니다.';
    invalidatePreview();
  } catch (error) {
    if (controller.signal.aborted || editController !== controller) return;
    editStatus.value = 'error';
    editError.value = formatError(error);
  }
}

function isAlwaysReadOnlyField(key: string) {
  return new Set(['id', 'code', 'created_at', 'updated_at', 'createdAt', 'updatedAt']).has(key);
}

async function runEditPreview() {
  if (!props.domain || !props.rowId || !editSelectedKeys.value.length) return;
  const draft = Object.fromEntries(editSelectedKeys.value.map((key) => [key, editDraft.value[key]]));
  const baseValues = Object.fromEntries(editSelectedKeys.value.map((key) => [key, editBaseValues.value[key]]));
  const request: PreviewRequest = { kind: 'edit', domain: props.domain, rowId: props.rowId, draft: cloneRecord(draft), baseValues: cloneRecord(baseValues), reason: editReason.value };
  await runAndRememberPreview(request);
}

async function loadChangeLogs() {
  logController?.abort();
  const controller = new AbortController();
  logController = controller;
  changeLogsStatus.value = 'loading';
  changeLogsError.value = '';
  try {
    const response = await admin.fetchChangeLogs({ limit: 12, sort: 'created_desc', applied: true }, { signal: controller.signal });
    if (controller.signal.aborted || logController !== controller) return;
    const payload = response?.payload && typeof response.payload === 'object' ? response.payload as { rows?: ChangeLogRow[] } : null;
    changeLogs.value = Array.isArray(payload?.rows) ? payload!.rows!.filter((row) => Number(row?.id) > 0) : [];
    changeLogsStatus.value = 'success';
  } catch (error) {
    if (controller.signal.aborted || logController !== controller) return;
    changeLogsStatus.value = 'error';
    changeLogsError.value = formatError(error);
  }
}

function selectChangeLog(log: ChangeLogRow) {
  changeLogId.value = Number(log.id);
  void loadChangeLogDetail();
}

async function loadChangeLogDetail() {
  if (!validChangeLogId.value) return;
  const requestId = ++logDetailRequestId;
  changeLogDetailStatus.value = 'loading';
  changeLogDetailError.value = '';
  changeLogDetail.value = null;
  try {
    const response = await admin.fetchChangeLogDetail(Number(changeLogId.value));
    if (requestId !== logDetailRequestId) return;
    changeLogDetail.value = response?.payload && typeof response.payload === 'object' ? response.payload as ChangeLogDetail : null;
    changeLogDetailStatus.value = 'success';
    const firstAvailable = rollbackOptions.value.find((option) => option.available === true);
    if (firstAvailable) rollbackKind.value = firstAvailable.kind;
    invalidatePreview();
  } catch (error) {
    if (requestId !== logDetailRequestId) return;
    changeLogDetail.value = null;
    changeLogDetailStatus.value = 'error';
    changeLogDetailError.value = formatError(error);
  }
}

function availability(key: 'rollback' | 'createDelete' | 'createDeleteRestore'): boolean | null {
  if (!changeLogDetail.value) return null;
  return changeLogDetail.value[key]?.available === true;
}

async function runRollbackPreview() {
  if (!validChangeLogId.value || !rollbackKindAvailable.value) return;
  const request: PreviewRequest = { kind: rollbackKind.value, changeLogId: Number(changeLogId.value), reason: rollbackReason.value };
  await runAndRememberPreview(request);
}

async function executePreview(request: PreviewRequest): Promise<AdminPreviewEnvelope> {
  if (request.kind === 'create') return admin.previewCreate({ domain: request.domain, draft: cloneRecord(request.draft), reason: request.reason });
  if (request.kind === 'edit') return admin.previewEdit({ domain: request.domain, rowId: request.rowId, draft: cloneRecord(request.draft), baseValues: cloneRecord(request.baseValues), reason: request.reason });
  const payload = { changeLogId: request.changeLogId, reason: request.reason };
  if (request.kind === 'rollback') return admin.previewRollback(payload);
  if (request.kind === 'create-delete') return admin.previewCreateDelete(payload);
  return admin.previewCreateDeleteRestore(payload);
}

async function runAndRememberPreview(request: PreviewRequest) {
  closeApplyGate();
  try {
    const response = await executePreview(request);
    const fingerprint = await fingerprintPayload(response.payload);
    if (admin.previewResult !== response) return;
    lastPreviewRequest.value = clonePreviewRequest(request);
    lastPreviewFingerprint.value = fingerprint;
  } catch { /* store renders the error */ }
}

function openApplyGate() {
  if (!applyGateAvailable.value) return;
  gatePreview.value = {
    title: previewTitle.value,
    confirmationText: confirmationText.value,
    baselineFingerprint: lastPreviewFingerprint.value,
  };
  revalidationState.value = 'idle';
  revalidationMessage.value = '같은 초안을 최신 서버 상태로 다시 검증해 주세요.';
  applyGateOpen.value = true;
}

function closeApplyGate() {
  applyGateOpen.value = false;
  gatePreview.value = null;
  revalidationState.value = 'idle';
  revalidationMessage.value = '같은 초안을 최신 서버 상태로 다시 검증해 주세요.';
}

async function revalidateLatestPreview() {
  if (!lastPreviewRequest.value || !gatePreview.value) return;
  const activeGate = gatePreview.value;
  revalidationState.value = 'checking';
  revalidationMessage.value = '서버에서 같은 Preview를 다시 계산하고 있습니다.';
  try {
    const response = await executePreview(clonePreviewRequest(lastPreviewRequest.value));
    const latestFingerprint = await fingerprintPayload(response.payload);
    if (!applyGateOpen.value || gatePreview.value !== activeGate) return;
    const stillReady = previewReady.value;
    const sameConfirmation = String(response.payload.confirmTextRequired || '').trim() === activeGate.confirmationText;
    if (latestFingerprint === activeGate.baselineFingerprint && stillReady && sameConfirmation) {
      revalidationState.value = 'success';
      revalidationMessage.value = '최신 Preview가 직전 결과와 일치하고 적용 준비 상태도 유지됩니다.';
      return;
    }
    lastPreviewFingerprint.value = latestFingerprint;
    revalidationState.value = 'changed';
    revalidationMessage.value = '서버 상태 또는 Preview 결과가 달라졌습니다. 창을 닫고 새 결과를 처음부터 검토해 주세요.';
  } catch (error) {
    if (!applyGateOpen.value || gatePreview.value !== activeGate) return;
    revalidationState.value = 'error';
    revalidationMessage.value = formatError(error);
  }
}

function invalidatePreview() {
  admin.clearPreview();
  lastPreviewRequest.value = null;
  lastPreviewFingerprint.value = '';
  closeApplyGate();
}

function cloneRecord(value: JsonRecord): JsonRecord {
  return JSON.parse(JSON.stringify(value)) as JsonRecord;
}

function clonePreviewRequest(request: PreviewRequest): PreviewRequest {
  return JSON.parse(JSON.stringify(request)) as PreviewRequest;
}

function stableJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(',')}]`;
  if (value && typeof value === 'object') {
    const entries = Object.entries(value as JsonRecord)
      .filter(([, item]) => item !== undefined)
      .sort(([left], [right]) => left.localeCompare(right));
    return `{${entries.map(([key, item]) => `${JSON.stringify(key)}:${stableJson(item)}`).join(',')}}`;
  }
  return JSON.stringify(value) ?? 'null';
}

async function fingerprintPayload(payload: AdminPreviewPayload) {
  const bytes = new TextEncoder().encode(stableJson(payload));
  const digest = await window.crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('');
}

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === '') return '-';
  if (typeof value === 'boolean') return value ? '예' : '아니오';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

function formatDate(value?: string) {
  if (!value) return '-';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat('ko-KR', { dateStyle: 'short', timeStyle: 'short' }).format(date);
}

function formatError(error: unknown) {
  return String((error as { message?: string })?.message || '요청을 처리하지 못했습니다.');
}

const reasonLabels: Record<string, string> = {
  current_value_changed_since_form_loaded: '화면을 연 뒤 현재값이 변경되었습니다.',
  current_db_values_do_not_match_change_log_after_values: '현재 DB 값이 이력의 변경 직후 값과 다릅니다.',
  duplicate_unique_code: '이미 사용 중인 고유 코드입니다.',
  field_not_open_for_apply_yet: '아직 적용이 허용되지 않은 필드입니다.',
  read_only_field: '읽기 전용 필드입니다.',
  unknown_field: '서버가 알 수 없는 필드입니다.',
  target_row_not_found: '대상 row를 찾을 수 없습니다.',
  create_delete_restore_id_conflict: '같은 ID가 이미 존재합니다.',
  create_delete_restore_code_conflict: '같은 코드가 이미 존재합니다.',
};

function translateReason(value: unknown) {
  const reason = String(value || '검증 조건을 통과하지 못했습니다.');
  return reasonLabels[reason] || reason.replace(/_/g, ' ');
}

function describeBlocker(item: AdminPreviewChange) {
  const record = item as JsonRecord;
  const parts = [item.reason ? translateReason(item.reason) : '', record.target ? `대상 ${formatValue(record.target)}` : '', record.count !== undefined ? `연결 ${formatValue(record.count)}개` : ''].filter(Boolean);
  return parts.length ? ` · ${parts.join(' · ')}` : '';
}

watch(() => props.domain, () => {
  blueprint.value = null;
  blueprintStatus.value = props.domain ? 'loading' : 'idle';
  if (props.domain) void loadBlueprint();
  else createDraft.value = {};
}, { immediate: true });

watch(() => [props.domain, props.rowId], () => {
  editFields.value = [];
  editStatus.value = props.domain && props.rowId ? 'loading' : 'idle';
  if (props.domain && props.rowId) void loadEditBaseline();
});

watch(createDraft, () => {
  if (admin.previewKind === 'create') invalidatePreview();
}, { deep: true });

watch(createReason, () => {
  if (admin.previewKind === 'create') invalidatePreview();
});

watch([editDraft, editSelectedKeys], () => {
  if (admin.previewKind === 'edit') invalidatePreview();
}, { deep: true });

watch(editReason, () => {
  if (admin.previewKind === 'edit') invalidatePreview();
});

watch([changeLogId, rollbackKind, rollbackReason], () => {
  if (admin.previewKind && !['create', 'edit'].includes(admin.previewKind)) invalidatePreview();
});

onBeforeUnmount(() => {
  logDetailRequestId += 1;
  blueprintController?.abort();
  editController?.abort();
  logController?.abort();
  invalidatePreview();
});
</script>
