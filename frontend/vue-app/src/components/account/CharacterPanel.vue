<template>
  <section class="account-card account-card--wide" aria-labelledby="character-gate-title">
    <header class="character-header">
      <div>
        <p class="account-card__eyebrow">Character slots · {{ account.occupiedCount }}/8</p>
        <h2 id="character-gate-title">접속할 캐릭터를 선택하세요</h2>
        <p><strong>{{ account.user?.username }}</strong> 계정의 캐릭터만 표시됩니다. 빈 슬롯에는 새 캐릭터를 만들 수 있습니다.</p>
      </div>
      <button class="account-button account-button--ghost" type="button" :disabled="account.busy" @click="account.logout">
        로그아웃
      </button>
    </header>

    <div class="character-grid" aria-label="캐릭터 슬롯 8개">
      <article
        v-for="slot in account.slots"
        :key="slot.slotKey"
        class="character-slot"
        :class="{ 'character-slot--empty': !slot.occupied, 'character-slot--unavailable': slot.unavailable }"
      >
        <div class="character-slot__number">Slot {{ slot.slotIndex }}</div>
        <template v-if="slot.occupied && slot.accountCharacter">
          <div class="character-slot__avatar" aria-hidden="true">{{ slot.accountCharacter.name.slice(0, 1) }}</div>
          <div class="character-slot__content">
            <h3>{{ slot.accountCharacter.name }}</h3>
            <p>{{ characterLabel(slot.accountCharacter.characterCode) }}</p>
            <dl>
              <div><dt>레벨</dt><dd>{{ slot.progress?.level ?? '새 캐릭터' }}</dd></div>
              <div><dt>최근 저장</dt><dd>{{ formatDate(slot.progress?.updatedAt) }}</dd></div>
            </dl>
          </div>
          <div class="character-slot__actions">
            <button class="account-button account-button--primary" type="button" :disabled="account.busy" @click="account.selectCharacter(slot)">
              이 캐릭터로 접속
            </button>
            <button class="account-button account-button--danger-text" type="button" :disabled="account.busy" @click="openDelete(slot)">
              삭제
            </button>
          </div>
        </template>
        <template v-else-if="slot.unavailable">
          <div class="character-slot__empty-mark" aria-hidden="true">!</div>
          <h3>확인이 필요한 슬롯</h3>
          <p>서버의 캐릭터 정보가 현재 계약과 일치하지 않습니다. 이 화면에서는 덮어쓰지 않습니다.</p>
        </template>
        <template v-else>
          <div class="character-slot__empty-mark" aria-hidden="true">＋</div>
          <h3>빈 캐릭터 슬롯</h3>
          <p>진행 데이터가 없는 새 슬롯입니다.</p>
          <button class="account-button account-button--ghost" type="button" :disabled="account.busy" @click="openCreate(slot.slotIndex)">
            새 캐릭터 만들기
          </button>
        </template>
      </article>
    </div>

    <p v-if="account.notice" class="account-notice" :data-tone="account.noticeTone" role="status" aria-live="polite">
      {{ account.notice }}
    </p>
  </section>

  <Teleport to="body">
    <div v-if="modal" class="account-modal-backdrop" @click.self="closeModal">
      <section class="account-modal" role="dialog" aria-modal="true" :aria-labelledby="`${modal}-modal-title`">
        <template v-if="modal === 'create'">
          <p class="account-card__eyebrow">Slot {{ createForm.slotIndex }}</p>
          <h2 id="create-modal-title">새 캐릭터 만들기</h2>
          <p>캐릭터 이름과 직업을 확인해 주세요. 생성 후 이 슬롯에 새 진행 데이터가 만들어집니다.</p>
          <form class="account-form" @submit.prevent="submitCreate">
            <label class="account-field">
              <span>캐릭터 이름</span>
              <input
                ref="modalInput"
                v-model.trim="createForm.name"
                name="name"
                minlength="1"
                maxlength="24"
                pattern="[가-힣A-Za-z0-9_. \-]+"
                required
                placeholder="한글·영문·숫자 24자 이내"
              />
            </label>
            <label class="account-field">
              <span>직업</span>
              <select v-model="createForm.characterCode" name="characterCode">
                <option v-for="option in account.characterOptions" :key="option.code" :value="option.code">
                  {{ option.name }}
                </option>
              </select>
            </label>
            <div class="account-form__actions">
              <button class="account-button account-button--ghost" type="button" :disabled="account.busy" @click="closeModal">취소</button>
              <button class="account-button account-button--primary" type="submit" :disabled="account.busy">
                {{ account.busy ? '생성 중…' : '캐릭터 만들기' }}
              </button>
            </div>
          </form>
        </template>

        <template v-else>
          <p class="account-card__eyebrow account-card__eyebrow--danger">Permanent delete</p>
          <h2 id="delete-modal-title">캐릭터 진행 데이터 삭제</h2>
          <p><strong>{{ deleteTarget?.accountCharacter?.name }}</strong> 캐릭터와 이 슬롯의 서버 저장 데이터가 영구적으로 삭제됩니다.</p>
          <div class="account-danger-callout">이 작업은 되돌릴 수 없습니다. 다른 캐릭터 슬롯에는 영향을 주지 않습니다.</div>
          <form class="account-form" @submit.prevent="submitDelete">
            <label class="account-field">
              <span>확인을 위해 캐릭터 이름 입력</span>
              <input ref="modalInput" v-model="deleteConfirm" autocomplete="off" required />
            </label>
            <div class="account-form__actions">
              <button class="account-button account-button--ghost" type="button" :disabled="account.busy" @click="closeModal">취소</button>
              <button
                class="account-button account-button--danger"
                type="submit"
                :disabled="account.busy || deleteConfirm !== deleteTarget?.accountCharacter?.name"
              >
                {{ account.busy ? '삭제 중…' : '캐릭터 영구 삭제' }}
              </button>
            </div>
          </form>
        </template>
      </section>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import { useAccountStore } from '@/stores';
import type { AccountCharacterSlot } from '@/api/contracts';

const account = useAccountStore();
const modal = ref<'create' | 'delete' | null>(null);
const modalInput = ref<HTMLInputElement | null>(null);
const deleteTarget = ref<AccountCharacterSlot | null>(null);
const deleteConfirm = ref('');
const createForm = reactive({ slotIndex: 1, name: '', characterCode: 'weapon_master' });

function characterLabel(code: string) {
  return account.characterOptions.find((option) => option.code === code)?.name ?? code;
}

function formatDate(value: string | null | undefined) {
  if (!value) return '저장 없음';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '확인 필요' : new Intl.DateTimeFormat('ko-KR', { dateStyle: 'short' }).format(date);
}

function focusModal() {
  void nextTick(() => modalInput.value?.focus());
}

function openCreate(slotIndex: number) {
  createForm.slotIndex = slotIndex;
  createForm.name = '';
  createForm.characterCode = account.characterOptions[0]?.code ?? 'weapon_master';
  modal.value = 'create';
  focusModal();
}

function openDelete(slot: AccountCharacterSlot) {
  deleteTarget.value = slot;
  deleteConfirm.value = '';
  modal.value = 'delete';
  focusModal();
}

function closeModal() {
  if (account.busy) return;
  modal.value = null;
  deleteTarget.value = null;
  deleteConfirm.value = '';
}

async function submitCreate() {
  const created = await account.createCharacter(createForm.slotIndex, createForm.name, createForm.characterCode);
  if (created) closeModal();
}

async function submitDelete() {
  if (!deleteTarget.value || deleteConfirm.value !== deleteTarget.value.accountCharacter?.name) return;
  const deleted = await account.deleteCharacter(deleteTarget.value);
  if (deleted) closeModal();
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && modal.value) closeModal();
}

onMounted(() => window.addEventListener('keydown', handleKeydown));
onBeforeUnmount(() => window.removeEventListener('keydown', handleKeydown));
</script>
