<template>
  <div v-if="model" class="storage-trash-shell" data-zone="storage-trash">
    <header class="storage-trash-command-bar">
      <div class="storage-trash-command-bar__actions">
        <button type="button" @click="game.returnInventoryPreview"><span aria-hidden="true">←</span> 가방·장비로</button>
        <button type="button" @click="game.returnTown"><span aria-hidden="true">⌂</span> 마을로</button>
      </div>
      <div>
        <span>Storage · recycle safety UI</span>
        <strong>{{ model.characterName }}의 보관 공간</strong>
      </div>
      <span class="storage-trash-command-bar__status"><i aria-hidden="true" /> 가방↔보관함 이동 · 삭제 잠금</span>
    </header>

    <section class="storage-trash-overview" aria-labelledby="storage-trash-overview-title">
      <div>
        <p>Owned items · safe transfer</p>
        <h2 id="storage-trash-overview-title">안전 보관과 복구 대기 공간</h2>
        <span>{{ model.characterLabel }} · {{ model.levelLabel }} · {{ model.goldLabel }} Gold</span>
      </div>
      <dl>
        <div><dt>보관함</dt><dd>{{ model.storage.occupiedCount }} / {{ model.storage.capacity }}</dd></div>
        <div><dt>휴지통</dt><dd>{{ model.trash.occupiedCount }} / {{ model.trash.capacity }}</dd></div>
        <div><dt>영구 삭제</dt><dd>잠김</dd></div>
      </dl>
    </section>

    <section class="storage-trash-workspace" aria-label="보관함과 휴지통 미리보기">
      <article class="container-preview container-preview--storage">
        <div class="storage-trash-section-heading">
          <div><p>Storage · {{ model.storage.visibleSlotCount }} visible</p><h2>보관함</h2></div>
          <span>{{ model.storage.occupiedCount }} / {{ model.storage.capacity }}</span>
        </div>
        <div class="container-preview__controls">
          <div><span>첫 빈 칸</span><strong>{{ model.storage.nextEmptySlotNumber ? `${model.storage.nextEmptySlotNumber}번` : '가득 참' }}</strong></div>
          <button
            type="button"
            :aria-pressed="model.storage.compactPreview"
            title="아이템 상대 순서를 유지한 정렬 결과만 미리 봅니다"
            @click="game.toggleStorageTrashCompactPreview('storage')"
          >{{ model.storage.compactPreview ? '원래 배치 보기' : '↑ 위로 정렬 미리보기' }}</button>
          <button type="button" :disabled="!canMutate || !model.storage.compactPreview || !model.storage.compactMovedCount" title="미리 본 순서로 보관함을 정렬하고 저장합니다" @click="sort('storage')">정렬 적용·저장</button>
        </div>
        <div class="container-slot-grid" aria-label="보관함 아이템 슬롯">
          <button
            v-for="slot in model.storage.slots"
            :key="slot.index"
            type="button"
            :class="slotClass(slot.item?.frameTone, slot.item?.selectionKey, 'storage')"
            :disabled="!slot.item"
            :aria-label="slot.item ? `보관함 ${slot.number}번 칸: ${slot.item.name}` : `보관함 ${slot.number}번 칸: 비어 있음`"
            @click="slot.item && game.selectStorageTrashPreview('storage', slot.item.selectionKey)"
          >
            <GameItemIcon v-if="slot.item" :item="slot.item" />
            <small v-if="slot.item">{{ slot.item.levelLabel }} {{ slot.item.quantityLabel }}</small>
            <i v-else aria-hidden="true">{{ slot.number }}</i>
          </button>
        </div>
        <p>가방이 가득 찼을 때 일부 보상은 보관함의 첫 빈 칸을 사용합니다. 현재 가방↔보관함 이동은 첫 빈 칸에 묶음을 그대로 옮깁니다.</p>
      </article>

      <article class="container-preview container-preview--trash">
        <div class="storage-trash-section-heading">
          <div><p>Trash · {{ model.trash.visibleSlotCount }} visible</p><h2>휴지통</h2></div>
          <span>{{ model.trash.occupiedCount }} / {{ model.trash.capacity }}</span>
        </div>
        <div class="container-preview__controls">
          <div><span>첫 빈 칸</span><strong>{{ model.trash.nextEmptySlotNumber ? `${model.trash.nextEmptySlotNumber}번` : '가득 참' }}</strong></div>
          <button
            type="button"
            :aria-pressed="model.trash.compactPreview"
            title="아이템 상대 순서를 유지한 정렬 결과만 미리 봅니다"
            @click="game.toggleStorageTrashCompactPreview('trash')"
          >{{ model.trash.compactPreview ? '원래 배치 보기' : '↑ 위로 정렬 미리보기' }}</button>
        </div>
        <div class="container-slot-grid" aria-label="휴지통 아이템 슬롯">
          <button
            v-for="slot in model.trash.slots"
            :key="slot.index"
            type="button"
            :class="slotClass(slot.item?.frameTone, slot.item?.selectionKey, 'trash')"
            :disabled="!slot.item"
            :aria-label="slot.item ? `휴지통 ${slot.number}번 칸: ${slot.item.name}` : `휴지통 ${slot.number}번 칸: 비어 있음`"
            @click="slot.item && game.selectStorageTrashPreview('trash', slot.item.selectionKey)"
          >
            <GameItemIcon v-if="slot.item" :item="slot.item" />
            <small v-if="slot.item">{{ slot.item.levelLabel }} {{ slot.item.quantityLabel }}</small>
            <i v-else aria-hidden="true">{{ slot.number }}</i>
          </button>
        </div>
        <div class="container-preview__trash-footer">
          <span>복구하기 전에는 사용·판매·강화할 수 없습니다.</span>
          <button type="button" disabled title="실제 snapshot과 파괴적 확인 modal 연결 뒤 활성화됩니다">휴지통 비우기</button>
        </div>
      </article>

      <aside v-if="model.selectedItem" class="storage-trash-detail" :data-container="model.selectedContainer" aria-labelledby="storage-trash-detail-title">
        <div class="storage-trash-detail__icon" :data-frame="model.selectedItem.frameTone" aria-hidden="true">
          <GameItemIcon :item="model.selectedItem" />
        </div>
        <p>{{ selectedContainerLabel }} · {{ model.selectedItem.frameLabel }}</p>
        <h2 id="storage-trash-detail-title">{{ model.selectedItem.name }}</h2>
        <span>{{ model.selectedItem.description }}</span>
        <dl>
          <div><dt>선택 위치</dt><dd>{{ selectedContainerLabel }} {{ model.selectedSlotNumber }}번</dd></div>
          <div><dt>강화·수량</dt><dd>{{ model.selectedItem.levelLabel }} {{ model.selectedItem.quantityLabel }}</dd></div>
          <div><dt>아이템 ID</dt><dd>{{ model.selectedItem.instanceId ?? '저장된 ID 없음' }}</dd></div>
          <div><dt>등급</dt><dd>{{ model.selectedItem.tierLabel }}</dd></div>
          <div><dt>슬롯·효과</dt><dd>{{ model.selectedItem.statSummary }}</dd></div>
          <div><dt>현재 제한</dt><dd>{{ selectedRestriction }}</dd></div>
        </dl>
        <button type="button" :disabled="!canMutate || model.selectedContainer !== 'storage'" :title="selectedActionTitle" @click="move('storage', model.selectedItem.selectionKey)">{{ selectedActionLabel }}</button>
      </aside>
      <aside v-else class="storage-trash-detail"><h2>보관된 아이템이 없습니다</h2><p>보관함과 휴지통이 비어 있습니다.</p></aside>
    </section>

    <section class="storage-trash-flow" aria-labelledby="storage-trash-flow-title">
      <div>
        <p>Transfer contract</p>
        <h2 id="storage-trash-flow-title">아이템 이동 경계</h2>
      </div>
      <ol>
        <li><span>가방</span><i aria-hidden="true">→</i><strong>보관함</strong><small>첫 빈 칸</small></li>
        <li><span>보관함</span><i aria-hidden="true">→</i><strong>가방</strong><small>꺼내기</small></li>
        <li><span>가방</span><i aria-hidden="true">→</i><strong>휴지통</strong><small>삭제 대기</small></li>
        <li><span>휴지통</span><i aria-hidden="true">→</i><strong>가방</strong><small>복구</small></li>
      </ol>
      <p>가방↔보관함 이동은 원래 빈 자리를 유지하고 도착 공간의 첫 빈 칸을 사용합니다. 휴지통 이동·복구는 후속 단계입니다.</p>
    </section>

    <section class="storage-trash-action-preview" aria-live="polite">
      <div><strong>Action adapter</strong><span>미리보기는 원본 유지 · 적용/이동은 직렬 저장</span></div>
      <p v-for="log in model.action.logs" :key="log.message">{{ log.message }}</p>
      <dl>
        <div><dt>server snapshot</dt><dd>보유 아이템 읽기 연결</dd></div>
        <div><dt>가방 이동 / 휴지통 복구</dt><dd>연결 / 잠김</dd></div>
        <div><dt>permanent delete / save</dt><dd>잠김</dd></div>
      </dl>
    </section>

    <aside class="storage-trash-data-boundary" aria-label="보관함과 휴지통 미리보기 데이터 경계">
      <span aria-hidden="true">!</span>
      <div>
        <strong>선택 캐릭터의 현재 보관함과 휴지통을 표시합니다.</strong>
        <p>정렬 미리보기는 원본을 유지합니다. 보관함 정렬 적용과 가방↔보관함 이동은 복구본을 기록하고 저장합니다. 자동 합치기·휴지통 정렬 저장·휴지통 이동·복구·영구 삭제는 잠겨 있습니다.</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import GameItemIcon from './GameItemIcon.vue';
import { useOwnedItemActions } from '@/composables/useOwnedItemActions';
import type { ItemFrameTone } from '@/game/adapters/inventoryEquipment';
import type { StorageTrashContainerKey } from '@/game/adapters/storageTrash';
import { useGameStore } from '@/stores';

const game = useGameStore();
const { canMutate, move, sort } = useOwnedItemActions();
const model = computed(() => game.storageTrashModel);
const selectedContainerLabel = computed(() => model.value?.selectedContainer === 'trash' ? '휴지통' : '보관함');
const selectedActionLabel = computed(() => model.value?.selectedContainer === 'trash' ? '가방으로 복구 · 잠김' : '가방으로 이동·저장');
const selectedActionTitle = computed(() => model.value?.selectedContainer === 'trash'
  ? 'snapshot과 복구 mutation 연결 뒤 활성화됩니다'
  : '묶음을 수량 그대로 가방 첫 빈 칸으로 옮기고 저장합니다. 자동 합치기는 하지 않습니다');
const selectedRestriction = computed(() => model.value?.selectedContainer === 'trash'
  ? '복구 전 사용·판매·강화 불가'
  : '가방으로 꺼낸 뒤 사용 가능');

function slotClass(
  frame: ItemFrameTone | undefined,
  itemCode: string | undefined,
  container: StorageTrashContainerKey,
) {
  return {
    'has-item': Boolean(itemCode),
    'is-selected': Boolean(
      itemCode
      && itemCode === model.value?.selectedItem?.selectionKey
      && container === model.value?.selectedContainer,
    ),
    [`item-frame--${frame ?? 'empty'}`]: true,
  };
}
</script>
