<template>
  <div v-if="inventory && town" class="inventory-shell" data-zone="inventory">
    <header class="inventory-command-bar">
      <button type="button" @click="game.returnTown"><span aria-hidden="true">←</span> 마을로 돌아가기</button>
      <div>
        <span>Inventory · equipment UI</span>
        <strong>{{ inventory.characterName }}의 장비 보관 화면</strong>
      </div>
      <span class="inventory-command-bar__status"><i aria-hidden="true" /> snapshot 연결 대기</span>
    </header>

    <section class="inventory-overview" aria-labelledby="inventory-overview-title">
      <div class="inventory-overview__identity">
        <div class="inventory-overview__portrait" aria-hidden="true">{{ inventory.avatarText }}</div>
        <div>
          <p>Master-data sample · display only</p>
          <h2 id="inventory-overview-title">{{ inventory.characterName }}</h2>
          <span>{{ inventory.characterLabel }} · {{ inventory.levelLabel }} · {{ inventory.goldLabel }} Gold</span>
        </div>
      </div>
      <dl class="inventory-overview__summary">
        <div><dt>가방 사용</dt><dd>{{ inventory.occupiedCount }} / {{ inventory.totalCapacity }}</dd></div>
        <div><dt>다음 획득</dt><dd>{{ inventory.nextEmptySlotNumber }}번 칸</dd></div>
        <div><dt>현재 배치</dt><dd>{{ inventory.compactPreview ? '정렬 결과 미리보기' : '빈 칸 보존 예시' }}</dd></div>
      </dl>
    </section>

    <section class="inventory-workspace" aria-label="인벤토리와 장비 미리보기">
      <div class="equipment-preview">
        <div class="inventory-section-heading">
          <div><p>Equipment slots</p><h2>장착 장비</h2></div>
          <span>6 일반 · 9 특수</span>
        </div>
        <div class="equipment-preview__avatar" aria-hidden="true"><i /><span>{{ inventory.avatarText }}</span><i /></div>
        <div class="equipment-preview__groups">
          <div>
            <strong>일반 장비</strong>
            <div class="equipment-slot-grid equipment-slot-grid--normal" aria-label="일반 장비 슬롯">
              <button
                v-for="slot in normalEquipmentSlots"
                :key="slot.index"
                type="button"
                :class="slotClass(slot.item?.frameTone, slot.item?.code)"
                :disabled="!slot.item"
                :aria-label="slot.item ? `${slot.label}: ${slot.item.name}` : `${slot.label}: 빈 슬롯`"
                @click="slot.item && game.selectInventoryPreview(slot.item.code)"
              >
                <span v-if="slot.item" aria-hidden="true">{{ slot.item.iconText }}</span>
                <small>{{ slot.label }}</small>
              </button>
            </div>
          </div>
          <div>
            <strong>특수 장비</strong>
            <div class="equipment-slot-grid equipment-slot-grid--special" aria-label="특수 장비 슬롯">
              <button
                v-for="slot in specialEquipmentSlots"
                :key="slot.index"
                type="button"
                :class="slotClass(slot.item?.frameTone, slot.item?.code)"
                :disabled="!slot.item"
                :aria-label="slot.item ? `${slot.label}: ${slot.item.name}` : `${slot.label}: 빈 슬롯`"
                @click="slot.item && game.selectInventoryPreview(slot.item.code)"
              >
                <span v-if="slot.item" aria-hidden="true">{{ slot.item.iconText }}</span>
                <small>{{ slot.label }}</small>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="inventory-preview">
        <div class="inventory-section-heading">
          <div><p>Inventory slots · {{ inventory.visibleSlotCount }} visible</p><h2>가방</h2></div>
          <span>{{ inventory.occupiedCount }} / {{ inventory.totalCapacity }}</span>
        </div>
        <div class="inventory-preview__actions">
          <div>
            <span>첫 빈 칸</span>
            <strong>{{ inventory.nextEmptySlotNumber }}번</strong>
          </div>
          <button
            type="button"
            :aria-pressed="inventory.compactPreview"
            title="아이템 상대 순서를 유지한 정렬 결과만 미리 봅니다"
            @click="game.toggleInventoryCompactPreview"
          >{{ inventory.compactPreview ? '원래 배치 보기' : '↑ 위로 정렬 미리보기' }}</button>
        </div>
        <div class="inventory-slot-grid" aria-label="가방 아이템 슬롯">
          <button
            v-for="slot in inventory.inventorySlots"
            :key="slot.index"
            type="button"
            :class="slotClass(slot.item?.frameTone, slot.item?.code)"
            :disabled="!slot.item"
            :aria-label="slot.item ? `${slot.number}번 칸: ${slot.item.name}` : `${slot.number}번 칸: 비어 있음`"
            @click="slot.item && game.selectInventoryPreview(slot.item.code)"
          >
            <span v-if="slot.item" aria-hidden="true">{{ slot.item.iconText }}</span>
            <small v-if="slot.item">{{ slot.item.tierLabel }}</small>
            <i v-else aria-hidden="true">{{ slot.number }}</i>
          </button>
        </div>
        <p class="inventory-preview__capacity">화면에는 24칸만 표시하며 실제 계약 용량은 60칸입니다. 빈 칸은 이동·사용 뒤에도 유지됩니다.</p>
      </div>

      <aside class="inventory-detail" aria-labelledby="inventory-detail-title">
        <div class="inventory-detail__icon" :data-frame="inventory.selectedItem.frameTone" aria-hidden="true">
          {{ inventory.selectedItem.iconText }}
        </div>
        <p>{{ inventory.selectedItem.typeLabel }} · {{ inventory.selectedItem.frameLabel }}</p>
        <h2 id="inventory-detail-title">{{ inventory.selectedItem.name }}</h2>
        <span>{{ inventory.selectedItem.description }}</span>
        <dl>
          <div><dt>선택 위치</dt><dd>{{ selectedLocationLabel }}</dd></div>
          <div><dt>등급</dt><dd>{{ inventory.selectedItem.tierLabel }}</dd></div>
          <div><dt>슬롯·효과</dt><dd>{{ inventory.selectedItem.statSummary }}</dd></div>
          <div><dt>보관 방식</dt><dd>{{ inventory.selectedItem.stackLabel }}</dd></div>
        </dl>
        <div class="inventory-detail__actions">
          <button type="button" disabled title="snapshot과 아이템 mutation 연결 뒤 활성화됩니다">장착·사용</button>
          <button type="button" disabled title="보관함 UI 단계에서 활성화됩니다">보관함 이동</button>
        </div>
      </aside>
    </section>

    <section class="inventory-action-preview" aria-live="polite">
      <div><strong>Action adapter</strong><span>아이템 배열·장착 상태·save 변화 없음</span></div>
      <p v-for="log in inventory.action.logs" :key="log.message">{{ log.message }}</p>
      <dl>
        <div><dt>master-data</dt><dd>연결됨</dd></div>
        <div><dt>server snapshot</dt><dd>미연결</dd></div>
        <div><dt>item mutation / save</dt><dd>잠김</dd></div>
      </dl>
    </section>

    <aside class="inventory-data-boundary" aria-label="인벤토리 미리보기 데이터 경계">
      <span aria-hidden="true">!</span>
      <div>
        <strong>현재 아이템은 실제 보유 목록이 아니라 master-data 샘플입니다.</strong>
        <p>선택과 `위로 정렬`은 표시 모델만 다시 만들며 원본 master-data와 server state를 바꾸지 않습니다. snapshot load/save·장착·사용·판매·강화·보관함 이동·휴지통 이동은 아직 연결하지 않습니다.</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { ItemFrameTone } from '@/game/adapters/inventoryEquipment';
import { useGameStore } from '@/stores';

const game = useGameStore();
const inventory = computed(() => game.inventoryModel);
const town = computed(() => game.model);
const normalEquipmentSlots = computed(() => inventory.value?.equipmentSlots.filter((slot) => slot.group === 'normal') ?? []);
const specialEquipmentSlots = computed(() => inventory.value?.equipmentSlots.filter((slot) => slot.group === 'special') ?? []);
const selectedLocationLabel = computed(() => {
  if (!inventory.value) return '';
  const container = inventory.value.selectedLocation === 'equipment' ? '장착 장비' : '가방';
  return `${container} ${inventory.value.selectedSlotNumber}번`;
});

function slotClass(frame: ItemFrameTone | undefined, itemCode: string | undefined) {
  return {
    'has-item': Boolean(itemCode),
    'is-selected': Boolean(itemCode && itemCode === inventory.value?.selectedItem.code),
    [`item-frame--${frame ?? 'empty'}`]: true,
  };
}
</script>
