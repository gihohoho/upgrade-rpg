<template>
  <div v-if="model" class="shop-settings-shell" data-zone="shop-settings">
    <header class="shop-settings-command-bar">
      <div class="shop-settings-command-bar__actions">
        <button type="button" @click="game.returnTown"><span aria-hidden="true">←</span> 마을로</button>
        <button type="button" @click="game.returnInventoryPreview"><span aria-hidden="true">囊</span> 인벤토리</button>
      </div>
      <div>
        <span>Shop · settings UI</span>
        <strong>{{ model.characterName }}의 거래·환경 준비실</strong>
      </div>
      <span class="shop-settings-command-bar__status"><i aria-hidden="true" /> 거래·저장 잠금</span>
    </header>

    <section class="shop-settings-overview" aria-labelledby="shop-settings-overview-title">
      <div>
        <p>Master-data catalog · local preview</p>
        <h2 id="shop-settings-overview-title">마을 상점과 게임 설정</h2>
        <span>{{ model.characterLabel }} · {{ model.levelLabel }} · {{ model.goldLabel }} Gold</span>
      </div>
      <dl>
        <div><dt>카탈로그</dt><dd>{{ model.catalogItems.length }}개</dd></div>
        <div><dt>비용 정보</dt><dd>{{ model.pricedReferenceCount }}개</dd></div>
        <div><dt>설정 변경</dt><dd>{{ model.changedSettingCount }}개</dd></div>
      </dl>
    </section>

    <section class="shop-workspace" aria-labelledby="shop-workspace-title">
      <div class="shop-settings-section-heading">
        <div><p>Catalog desk</p><h2 id="shop-workspace-title">아이템 카탈로그</h2></div>
        <span>구매가는 아직 없으며 <code>baseCost</code>는 강화 기준 비용입니다</span>
      </div>

      <nav class="shop-category-tabs" aria-label="카탈로그 분류">
        <button
          v-for="category in model.categories"
          :key="category.key"
          type="button"
          :class="{ 'is-selected': category.key === model.selectedCategory }"
          :aria-pressed="category.key === model.selectedCategory"
          @click="game.selectShopCategory(category.key)"
        >{{ category.label }} <span>{{ category.count }}</span></button>
      </nav>

      <div class="shop-catalog-layout">
        <div class="shop-catalog-grid" aria-label="아이템 선택">
          <button
            v-for="item in model.visibleItems"
            :key="item.code"
            type="button"
            :data-frame="item.frameTone"
            :class="{ 'is-selected': item.code === model.selectedItem.code }"
            :aria-pressed="item.code === model.selectedItem.code"
            @click="game.selectShopItem(item.code)"
          >
            <span aria-hidden="true">{{ item.iconText }}</span>
            <i><b>{{ item.name }}</b><small>{{ item.typeLabel }} · {{ item.tierLabel }}</small></i>
            <em>{{ item.baseCostLabel }}</em>
          </button>
        </div>

        <article class="shop-item-detail" aria-labelledby="shop-item-detail-title">
          <div class="shop-item-detail__identity">
            <span :data-frame="model.selectedItem.frameTone" aria-hidden="true">{{ model.selectedItem.iconText }}</span>
            <div><p>{{ model.selectedItem.frameLabel }} · {{ model.selectedItem.typeLabel }}</p><h2 id="shop-item-detail-title">{{ model.selectedItem.name }}</h2></div>
          </div>
          <p>{{ model.selectedItem.description }}</p>
          <dl>
            <div><dt>구매 가격</dt><dd>{{ model.selectedItem.purchasePriceLabel }}</dd></div>
            <div><dt>강화 기준 비용</dt><dd>{{ model.selectedItem.baseCostLabel }}</dd></div>
            <div><dt>판매 값</dt><dd>{{ model.selectedItem.sellPriceLabel }}</dd></div>
            <div><dt>아이템 정보</dt><dd>{{ model.selectedItem.statSummary }}</dd></div>
          </dl>
          <aside>
            <strong>기존 거래 계약 확인</strong>
            <span>legacy 화면의 “판매”는 Gold를 지급하지 않고 휴지통으로 이동합니다. 구매 규칙도 없으므로 두 기능 모두 잠갔습니다.</span>
          </aside>
          <div class="shop-item-detail__actions">
            <button type="button" disabled title="구매 가격과 서버 거래 계약을 정한 뒤 활성화됩니다">구매 준비 중</button>
            <button type="button" disabled title="현재 판매는 휴지통 이동이며 Gold 거래가 아닙니다">판매 준비 중</button>
          </div>
        </article>
      </div>
    </section>

    <section class="settings-workspace" aria-labelledby="settings-workspace-title">
      <div class="shop-settings-section-heading settings-workspace__heading">
        <div><p>Runtime options</p><h2 id="settings-workspace-title">게임 설정 미리보기</h2></div>
        <button type="button" :disabled="model.changedSettingCount === 0" @click="game.resetSettingPreview">기본값 복원</button>
      </div>

      <div class="settings-card-grid">
        <article v-for="setting in model.settings" :key="setting.key" :class="{ 'is-changed': setting.changed }">
          <div>
            <p>{{ setting.changed ? '미리보기 변경됨' : '기본값' }}</p>
            <h3>{{ setting.label }}</h3>
          </div>
          <button
            type="button"
            role="switch"
            :aria-checked="setting.enabled"
            :aria-label="`${setting.label} ${setting.enabled ? '끄기' : '켜기'}`"
            :class="{ 'is-on': setting.enabled }"
            @click="game.toggleSettingPreview(setting.key)"
          ><span>{{ setting.enabled ? 'ON' : 'OFF' }}</span><i aria-hidden="true" /></button>
          <p>{{ setting.description }}</p>
          <small>{{ setting.caution }}</small>
        </article>
      </div>

      <div class="settings-data-controls">
        <div><span aria-hidden="true">存</span><p><strong>수동 저장</strong><small>직렬 저장 queue와 revision 연결 뒤 제공</small></p><button type="button" disabled>잠김</button></div>
        <div><span aria-hidden="true">初</span><p><strong>캐릭터 데이터 초기화</strong><small>캐릭터 이름 재입력 확인 흐름과 함께 이식</small></p><button type="button" disabled>잠김</button></div>
      </div>
    </section>

    <section class="shop-settings-action-preview" aria-live="polite">
      <div><strong>Preview adapter</strong><span>선택과 임시 토글만 변경 · 게임 runtime 변화 없음</span></div>
      <p v-for="log in model.action.logs" :key="log.message">{{ log.message }}</p>
      <dl>
        <div><dt>master-data</dt><dd>읽기 연결</dd></div>
        <div><dt>commerce / Gold</dt><dd>미연결</dd></div>
        <div><dt>runtime / save</dt><dd>잠김</dd></div>
      </dl>
    </section>

    <aside class="shop-settings-data-boundary" aria-label="상점과 설정 미리보기 데이터 경계">
      <span aria-hidden="true">!</span>
      <div>
        <strong>새 거래 규칙이나 영구 설정을 만들지 않은 표시 전용 화면입니다.</strong>
        <p>아이템 master-data와 마을 요약만 읽습니다. 구매·판매·Gold/아이템 변경·설정 저장·snapshot load/save·자동 저장·전투 runtime은 실행하지 않습니다.</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useGameStore } from '@/stores';

const game = useGameStore();
const model = computed(() => game.shopSettingsModel);
</script>
