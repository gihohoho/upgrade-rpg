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
      <span class="storage-trash-command-bar__status"><i aria-hidden="true" /> 이동·삭제 잠금</span>
    </header>

    <section class="storage-trash-overview" aria-labelledby="storage-trash-overview-title">
      <div>
        <p>Master-data sample · display only</p>
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
          <div><span>첫 빈 칸</span><strong>{{ model.storage.nextEmptySlotNumber }}번</strong></div>
          <button
            type="button"
            :aria-pressed="model.storage.compactPreview"
            title="아이템 상대 순서를 유지한 정렬 결과만 미리 봅니다"
            @click="game.toggleStorageTrashCompactPreview('storage')"
          >{{ model.storage.compactPreview ? '원래 배치 보기' : '↑ 위로 정렬 미리보기' }}</button>
        </div>
        <div class="container-slot-grid" aria-label="보관함 아이템 슬롯">
          <button
            v-for="slot in model.storage.slots"
            :key="slot.index"
            type="button"
            :class="slotClass(slot.item?.frameTone, slot.item?.code, 'storage')"
            :disabled="!slot.item"
            :aria-label="slot.item ? `보관함 ${slot.number}번 칸: ${slot.item.name}` : `보관함 ${slot.number}번 칸: 비어 있음`"
            @click="slot.item && game.selectStorageTrashPreview('storage', slot.item.code)"
          >
            <span v-if="slot.item" aria-hidden="true">{{ slot.item.iconText }}</span>
            <small v-if="slot.item">{{ slot.item.tierLabel }}</small>
            <i v-else aria-hidden="true">{{ slot.number }}</i>
          </button>
        </div>
        <p>가방이 가득 찼을 때 일부 보상은 보관함의 첫 빈 칸을 사용합니다. 실제 이동은 아직 실행하지 않습니다.</p>
      </article>

      <article class="container-preview container-preview--trash">
        <div class="storage-trash-section-heading">
          <div><p>Trash · {{ model.trash.visibleSlotCount }} visible</p><h2>휴지통</h2></div>
          <span>{{ model.trash.occupiedCount }} / {{ model.trash.capacity }}</span>
        </div>
        <div class="container-preview__controls">
          <div><span>첫 빈 칸</span><strong>{{ model.trash.nextEmptySlotNumber }}번</strong></div>
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
            :class="slotClass(slot.item?.frameTone, slot.item?.code, 'trash')"
            :disabled="!slot.item"
            :aria-label="slot.item ? `휴지통 ${slot.number}번 칸: ${slot.item.name}` : `휴지통 ${slot.number}번 칸: 비어 있음`"
            @click="slot.item && game.selectStorageTrashPreview('trash', slot.item.code)"
          >
            <span v-if="slot.item" aria-hidden="true">{{ slot.item.iconText }}</span>
            <small v-if="slot.item">{{ slot.item.tierLabel }}</small>
            <i v-else aria-hidden="true">{{ slot.number }}</i>
          </button>
        </div>
        <div class="container-preview__trash-footer">
          <span>복구하기 전에는 사용·판매·강화할 수 없습니다.</span>
          <button type="button" disabled title="실제 snapshot과 파괴적 확인 modal 연결 뒤 활성화됩니다">휴지통 비우기</button>
        </div>
      </article>

      <aside class="storage-trash-detail" :data-container="model.selectedContainer" aria-labelledby="storage-trash-detail-title">
        <div class="storage-trash-detail__icon" :data-frame="model.selectedItem.frameTone" aria-hidden="true">
          {{ model.selectedItem.iconText }}
        </div>
        <p>{{ selectedContainerLabel }} · {{ model.selectedItem.frameLabel }}</p>
        <h2 id="storage-trash-detail-title">{{ model.selectedItem.name }}</h2>
        <span>{{ model.selectedItem.description }}</span>
        <dl>
          <div><dt>선택 위치</dt><dd>{{ selectedContainerLabel }} {{ model.selectedSlotNumber }}번</dd></div>
          <div><dt>등급</dt><dd>{{ model.selectedItem.tierLabel }}</dd></div>
          <div><dt>슬롯·효과</dt><dd>{{ model.selectedItem.statSummary }}</dd></div>
          <div><dt>현재 제한</dt><dd>{{ selectedRestriction }}</dd></div>
        </dl>
        <button type="button" disabled :title="selectedActionTitle">{{ selectedActionLabel }}</button>
      </aside>
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
      <p>모든 이동은 source의 빈 자리를 유지하고 destination의 첫 빈 칸을 사용합니다. 이번 화면에서는 흐름만 설명합니다.</p>
    </section>

    <section class="storage-trash-action-preview" aria-live="polite">
      <div><strong>Action adapter</strong><span>container 배열·선택·save 변화 없음</span></div>
      <p v-for="log in model.action.logs" :key="log.message">{{ log.message }}</p>
      <dl>
        <div><dt>server snapshot</dt><dd>미연결</dd></div>
        <div><dt>item move / restore</dt><dd>잠김</dd></div>
        <div><dt>permanent delete / save</dt><dd>잠김</dd></div>
      </dl>
    </section>

    <aside class="storage-trash-data-boundary" aria-label="보관함과 휴지통 미리보기 데이터 경계">
      <span aria-hidden="true">!</span>
      <div>
        <strong>현재 보관함과 휴지통은 실제 보유 목록이 아니라 master-data 샘플입니다.</strong>
        <p>선택과 `위로 정렬`은 표시 모델만 다시 만듭니다. snapshot load/save·가방/보관함 이동·휴지통 이동·복구·영구 삭제는 아직 연결하지 않았으며 원본 master-data와 server state는 바뀌지 않습니다.</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { ItemFrameTone } from '@/game/adapters/inventoryEquipment';
import type { StorageTrashContainerKey } from '@/game/adapters/storageTrash';
import { useGameStore } from '@/stores';

const game = useGameStore();
const model = computed(() => game.storageTrashModel);
const selectedContainerLabel = computed(() => model.value?.selectedContainer === 'trash' ? '휴지통' : '보관함');
const selectedActionLabel = computed(() => model.value?.selectedContainer === 'trash' ? '가방으로 복구' : '가방으로 꺼내기');
const selectedActionTitle = computed(() => model.value?.selectedContainer === 'trash'
  ? 'snapshot과 복구 mutation 연결 뒤 활성화됩니다'
  : 'snapshot과 보관함 이동 mutation 연결 뒤 활성화됩니다');
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
      && itemCode === model.value?.selectedItem.code
      && container === model.value?.selectedContainer,
    ),
    [`item-frame--${frame ?? 'empty'}`]: true,
  };
}
</script>
