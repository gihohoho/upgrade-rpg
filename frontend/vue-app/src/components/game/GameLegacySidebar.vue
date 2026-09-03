<template>
  <aside
    class="game-side-window"
    :class="[`game-side-window--${variant}`, { 'game-side-window--compact': compact }]"
    :aria-label="variant === 'profile' ? '내 정보와 장비' : '가방 미리보기'"
  >
    <header class="game-side-window__titlebar">
      <div>
        <span aria-hidden="true">{{ variant === 'profile' ? '♟' : '▦' }}</span>
        <strong>{{ variant === 'profile' ? '내 정보' : '가방' }}</strong>
      </div>
      <small>legacy panel</small>
    </header>

    <template v-if="town && variant === 'profile'">
      <section class="game-side-profile">
        <div class="game-side-profile__portrait" aria-hidden="true">{{ town.avatarText }}</div>
        <div>
          <p>{{ town.characterLabel }}</p>
          <h2>{{ town.characterName }}</h2>
          <span>{{ town.levelLabel }} · {{ town.goldLabel }} Gold</span>
        </div>
      </section>

      <section class="game-side-section" aria-labelledby="game-side-equipment-title">
        <div class="game-side-section__heading">
          <strong id="game-side-equipment-title">장착 장비</strong>
          <span>표시용</span>
        </div>
        <div v-if="preview" class="game-side-equipment-grid">
          <button
            v-for="slot in preview.equipmentSlots"
            :key="slot.index"
            type="button"
            :data-frame="slot.item?.frameTone ?? 'empty'"
            :disabled="!slot.item"
            :title="slot.item ? `${slot.label}: ${slot.item.name}` : `${slot.label}: 빈 슬롯`"
            @click="slot.item && openInventory(slot.item.code)"
          >
            <span aria-hidden="true">{{ slot.item?.iconText ?? '·' }}</span>
            <small>{{ slot.label }}</small>
          </button>
        </div>
        <p v-else class="game-side-window__empty">아이템 master-data를 불러오면 장비 슬롯이 표시됩니다.</p>
      </section>

      <section class="game-side-section" aria-labelledby="game-side-stats-title">
        <div class="game-side-section__heading">
          <strong id="game-side-stats-title">능력치</strong>
          <span>기본 상태</span>
        </div>
        <dl class="game-side-stats">
          <div v-for="stat in town.stats" :key="stat.key" :data-tone="stat.tone">
            <dt>{{ stat.label }}</dt>
            <dd>{{ stat.value }}</dd>
          </div>
        </dl>
      </section>

      <section class="game-side-section" aria-labelledby="game-side-skills-title">
        <div class="game-side-section__heading">
          <strong id="game-side-skills-title">스킬</strong>
          <span>기본 레벨</span>
        </div>
        <div class="game-side-skill-grid">
          <span v-for="skill in town.skills" :key="skill.key" :data-tone="skill.tone" :title="skill.name">
            <b>{{ skill.slotKey }}</b><small>Lv.{{ skill.level }}</small>
          </span>
        </div>
      </section>
    </template>

    <template v-else-if="town">
      <div class="game-side-bag-summary">
        <div>
          <span>사용 중</span>
          <strong>{{ preview?.occupiedCount ?? 0 }} / 60</strong>
        </div>
        <button type="button" :disabled="!preview" @click="openInventory()">가방 크게 보기</button>
      </div>

      <section class="game-side-section game-side-section--bag" aria-labelledby="game-side-bag-title">
        <div class="game-side-section__heading">
          <strong id="game-side-bag-title">아이템 슬롯</strong>
          <span>master-data 미리보기</span>
        </div>
        <div v-if="preview" class="game-side-bag-grid">
          <button
            v-for="slot in preview.inventorySlots.slice(0, 20)"
            :key="slot.index"
            type="button"
            :data-frame="slot.item?.frameTone ?? 'empty'"
            :disabled="!slot.item"
            :aria-label="slot.item ? `${slot.number}번 칸: ${slot.item.name}` : `${slot.number}번 칸: 비어 있음`"
            @click="slot.item && openInventory(slot.item.code)"
          >
            <span v-if="slot.item" aria-hidden="true">{{ slot.item.iconText }}</span>
            <i v-else aria-hidden="true">{{ slot.number }}</i>
            <small v-if="slot.item">{{ slot.item.tierLabel }}</small>
          </button>
        </div>
        <p v-else class="game-side-window__empty">아이템 정보를 불러오는 중입니다.</p>
      </section>

      <footer class="game-side-bag-footer">
        <div><span>보유 Gold</span><strong>{{ town.goldLabel }}</strong></div>
        <div>
          <button type="button" :disabled="!preview" @click="openStorage">보관함·휴지통</button>
          <button type="button" :disabled="!preview" @click="openShop">상점·설정</button>
        </div>
      </footer>
    </template>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAccountStore, useGameStore } from '@/stores';
import { createInventoryEquipmentViewModel } from '@/game/adapters/inventoryEquipment';

const { variant, compact = false } = defineProps<{
  variant: 'profile' | 'inventory';
  compact?: boolean;
}>();

const account = useAccountStore();
const game = useGameStore();
const town = computed(() => game.model);
const preview = computed(() => {
  if (!game.model || !account.itemTemplates.length) return null;
  return createInventoryEquipmentViewModel({
    town: game.model,
    itemTemplates: account.itemTemplates,
    compactPreview: false,
    createdAt: 0,
  });
});

function openInventory(itemCode?: string) {
  if (!account.itemTemplates.length || !game.enterInventoryPreview(account.itemTemplates)) return;
  if (itemCode) game.selectInventoryPreview(itemCode);
}

function openStorage() {
  if (!account.itemTemplates.length || !game.enterInventoryPreview(account.itemTemplates)) return;
  game.enterStorageTrashPreview();
}

function openShop() {
  game.enterShopSettingsPreview(account.itemTemplates);
}
</script>
