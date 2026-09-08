<template>
  <div v-if="inventory && town" class="inventory-shell" data-zone="inventory">
    <header class="inventory-command-bar">
      <div class="inventory-command-bar__actions">
        <button type="button" @click="game.returnTown"><span aria-hidden="true">←</span> 마을로</button>
        <button type="button" @click="game.enterStorageTrashPreview"><span aria-hidden="true">▦</span> 보관함·휴지통</button>
        <button type="button" @click="game.enterShopSettingsPreview(account.itemTemplates)"><span aria-hidden="true">店</span> 상점·설정</button>
        <button
          type="button"
          :disabled="!canEnterSkillEnhancement"
          :title="canEnterSkillEnhancement ? '스킬·강화 규칙 화면으로 이동합니다' : '스킬·강화 master-data를 불러오지 못했습니다'"
          @click="enterSkillEnhancementPreview"
        ><span aria-hidden="true">鍛</span> 스킬·강화</button>
      </div>
      <div>
        <span>Inventory · equipment UI</span>
        <strong>{{ inventory.characterName }}의 장비 보관 화면</strong>
      </div>
      <span class="inventory-command-bar__status"><i aria-hidden="true" /> 보유 아이템 읽기 연결</span>
    </header>

    <section class="inventory-overview" aria-labelledby="inventory-overview-title">
      <div class="inventory-overview__identity">
        <div class="inventory-overview__portrait" aria-hidden="true">{{ inventory.avatarText }}</div>
        <div>
          <p>Owned items · safe transfer</p>
          <h2 id="inventory-overview-title">{{ inventory.characterName }}</h2>
          <span>{{ inventory.characterLabel }} · {{ inventory.levelLabel }} · {{ inventory.goldLabel }} Gold</span>
        </div>
      </div>
      <dl class="inventory-overview__summary">
        <div><dt>가방 사용</dt><dd>{{ inventory.occupiedCount }} / {{ inventory.totalCapacity }}</dd></div>
        <div><dt>다음 획득</dt><dd>{{ inventory.nextEmptySlotNumber ? `${inventory.nextEmptySlotNumber}번 칸` : '가득 참' }}</dd></div>
        <div><dt>현재 배치</dt><dd>{{ inventory.compactPreview ? '정렬 결과 미리보기' : '저장된 배치' }}</dd></div>
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
                :class="slotClass(slot.item?.frameTone, slot.item?.selectionKey)"
                :disabled="!slot.item"
                :aria-label="slot.item ? `${slot.label}: ${slot.item.name}` : `${slot.label}: 빈 슬롯`"
                @click="slot.item && game.selectInventoryPreview(slot.item.selectionKey)"
              >
                <GameItemIcon v-if="slot.item" :item="slot.item" />
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
                :class="slotClass(slot.item?.frameTone, slot.item?.selectionKey)"
                :disabled="!slot.item"
                :aria-label="slot.item ? `${slot.label}: ${slot.item.name}` : `${slot.label}: 빈 슬롯`"
                @click="slot.item && game.selectInventoryPreview(slot.item.selectionKey)"
              >
                <GameItemIcon v-if="slot.item" :item="slot.item" />
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
            <strong>{{ inventory.nextEmptySlotNumber ? `${inventory.nextEmptySlotNumber}번` : '가득 참' }}</strong>
          </div>
          <button
            type="button"
            :aria-pressed="inventory.compactPreview"
            title="아이템 상대 순서를 유지한 정렬 결과만 미리 봅니다"
            @click="game.toggleInventoryCompactPreview"
          >{{ inventory.compactPreview ? '원래 배치 보기' : '↑ 위로 정렬 미리보기' }}</button>
          <button type="button" :disabled="!canMutate || !inventory.compactPreview || !inventory.compactMovedCount" title="미리 본 순서로 가방을 정렬하고 저장합니다" @click="sort('inventory')">정렬 적용·저장</button>
        </div>
        <div class="inventory-slot-grid" aria-label="가방 아이템 슬롯">
          <button
            v-for="slot in inventory.inventorySlots"
            :key="slot.index"
            type="button"
            :class="slotClass(slot.item?.frameTone, slot.item?.selectionKey)"
            :disabled="!slot.item"
            :aria-label="slot.item ? `${slot.number}번 칸: ${slot.item.name}` : `${slot.number}번 칸: 비어 있음`"
            @click="slot.item && game.selectInventoryPreview(slot.item.selectionKey)"
          >
            <GameItemIcon v-if="slot.item" :item="slot.item" />
            <small v-if="slot.item">{{ slot.item.levelLabel }} {{ slot.item.quantityLabel }}</small>
            <i v-else aria-hidden="true">{{ slot.number }}</i>
          </button>
        </div>
        <p class="inventory-preview__capacity">전체 {{ inventory.visibleSlotCount }}칸을 표시합니다. 저장된 빈 칸과 아이템 순서를 유지하며 정렬 미리보기는 저장되지 않습니다.</p>
      </div>

      <aside v-if="inventory.selectedItem" class="inventory-detail" aria-labelledby="inventory-detail-title">
        <div class="inventory-detail__icon" :data-frame="inventory.selectedItem.frameTone" aria-hidden="true">
          <GameItemIcon :item="inventory.selectedItem" />
        </div>
        <p>{{ inventory.selectedItem.typeLabel }} · {{ inventory.selectedItem.frameLabel }}</p>
        <h2 id="inventory-detail-title">{{ inventory.selectedItem.name }}</h2>
        <span>{{ inventory.selectedItem.description }}</span>
        <dl>
          <div><dt>선택 위치</dt><dd>{{ selectedLocationLabel }}</dd></div>
          <div><dt>강화</dt><dd>{{ inventory.selectedItem.levelLabel || '정보 없음' }}</dd></div>
          <div><dt>아이템 ID</dt><dd>{{ inventory.selectedItem.instanceId ?? '저장된 ID 없음' }}</dd></div>
          <div><dt>등급</dt><dd>{{ inventory.selectedItem.tierLabel }}</dd></div>
          <div><dt>슬롯·효과</dt><dd>{{ inventory.selectedItem.statSummary }}</dd></div>
          <div><dt>보관 방식</dt><dd>{{ inventory.selectedItem.stackLabel }}</dd></div>
        </dl>
        <div class="inventory-detail__actions">
          <button type="button" disabled title="아이템 변경 기능 연결 뒤 활성화됩니다">장착·사용</button>
          <button type="button" :disabled="!canMutate || inventory.selectedLocation !== 'inventory'" title="선택한 묶음을 수량 그대로 보관함 첫 빈 칸에 옮기고 저장합니다. 자동 합치기는 하지 않습니다" @click="move('inventory', inventory.selectedItem.selectionKey)">보관함으로 이동·저장</button>
        </div>
      </aside>
      <aside v-else class="inventory-detail"><h2>보유 아이템이 없습니다</h2><p>장비나 가방에 아이템이 있으면 여기에서 상세 정보를 확인할 수 있습니다.</p></aside>
    </section>

    <section class="inventory-action-preview" aria-live="polite">
      <div><strong>Action adapter</strong><span>미리보기는 원본 유지 · 적용/이동은 직렬 저장</span></div>
      <p v-for="log in inventory.action.logs" :key="log.message">{{ log.message }}</p>
      <dl>
        <div><dt>master-data</dt><dd>{{ inventory.masterDataConnected ? '기준 정보 연결됨' : '저장된 정보로 표시' }}</dd></div>
        <div><dt>server snapshot</dt><dd>보유 아이템 읽기 연결</dd></div>
        <div><dt>이동·정렬 저장</dt><dd>가방↔보관함 연결</dd></div>
      </dl>
    </section>

    <aside class="inventory-data-boundary" aria-label="인벤토리 미리보기 데이터 경계">
      <span aria-hidden="true">!</span>
      <div>
        <strong>선택 캐릭터의 현재 저장 데이터를 표시합니다.</strong>
        <p>선택·정렬 미리보기는 원본을 유지합니다. 정렬 적용과 가방↔보관함 이동은 복구본을 먼저 기록한 뒤 저장합니다. 묶음은 통째로 이동하며 자동 합치기는 하지 않습니다. 장착·사용·판매·강화·휴지통 이동은 잠겨 있습니다.</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import GameItemIcon from './GameItemIcon.vue';
import { useOwnedItemActions } from '@/composables/useOwnedItemActions';
import type { ItemFrameTone } from '@/game/adapters/inventoryEquipment';
import { useAccountStore, useGameStore } from '@/stores';

const account = useAccountStore();
const game = useGameStore();
const { canMutate, move, sort } = useOwnedItemActions();
const inventory = computed(() => game.inventoryModel);
const town = computed(() => game.model);
const normalEquipmentSlots = computed(() => inventory.value?.equipmentSlots.filter((slot) => slot.group === 'normal') ?? []);
const specialEquipmentSlots = computed(() => inventory.value?.equipmentSlots.filter((slot) => slot.group === 'special') ?? []);
const selectedLocationLabel = computed(() => {
  if (!inventory.value) return '';
  const container = inventory.value.selectedLocation === 'equipment' ? '장착 장비' : '가방';
  return `${container} ${inventory.value.selectedSlotNumber}번`;
});
const canEnterSkillEnhancement = computed(() => (
  account.skills.length > 0
  && account.enhancementGroups.length > 0
  && account.enhancementLevels.length > 0
  && account.itemTemplates.some((item) => Boolean(item.enhanceGroupCode))
));

function enterSkillEnhancementPreview() {
  game.enterSkillEnhancementPreview({
    skills: account.skills,
    characterSkills: account.characterSkills,
    skillLevels: account.skillLevels,
    itemTemplates: account.itemTemplates,
    enhancementGroups: account.enhancementGroups,
    enhancementLevels: account.enhancementLevels,
  });
}

function slotClass(frame: ItemFrameTone | undefined, itemCode: string | undefined) {
  return {
    'has-item': Boolean(itemCode),
    'is-selected': Boolean(itemCode && itemCode === inventory.value?.selectedItem?.selectionKey),
    [`item-frame--${frame ?? 'empty'}`]: true,
  };
}
</script>
