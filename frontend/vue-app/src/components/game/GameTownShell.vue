<template>
  <div
    v-if="game.model"
    class="town-shell"
    :class="{ 'town-shell--background': background }"
    data-zone="town"
    :aria-hidden="background || undefined"
    :inert="background"
  >
    <header v-if="game.isTown && !background" class="town-session-bar" aria-label="마을 접속 캐릭터">
      <div class="town-session-bar__identity">
        <span>접속 캐릭터</span>
        <strong>{{ game.model.characterName }}</strong>
        <small>{{ account.user?.username }} · {{ game.model.slotKey }}</small>
      </div>
      <div class="town-session-bar__state">
        <span><i aria-hidden="true" /> {{ game.model.zoneLabel }}</span>
        <small>{{ game.model.recentSaveZoneLabel }}</small>
      </div>
      <div class="town-session-bar__actions">
        <button type="button" @click="changeCharacter">캐릭터 변경</button>
        <button type="button" @click="logout">로그아웃</button>
      </div>
    </header>

    <section class="town-scene" aria-labelledby="town-scene-title">
      <div class="town-scene__glow" aria-hidden="true" />
      <div class="town-scene__skyline" aria-hidden="true">
        <span /><span /><span /><span /><span />
      </div>
      <div class="town-scene__content">
        <p class="town-scene__eyebrow">Safe zone · {{ game.model.levelLabel }}</p>
        <h2 id="town-scene-title">고요한 모험가의 마을</h2>
        <p>전투를 준비하고 성장 기록을 살펴보는 안전 구역입니다.</p>
        <div class="town-scene__summary" aria-label="캐릭터 요약">
          <span><b>직업</b>{{ game.model.characterLabel }}</span>
          <span><b>보유 골드</b>{{ game.model.goldLabel }}</span>
          <span><b>데이터</b>{{ game.model.snapshotStatusLabel }}</span>
        </div>
      </div>
      <div class="town-scene__crest" aria-hidden="true">
        <span>{{ game.model.avatarText }}</span>
        <i />
      </div>
    </section>

    <section class="town-hub" aria-labelledby="town-hub-title">
      <div class="town-section-heading">
        <div>
          <p>Town services</p>
          <h2 id="town-hub-title">마을 시설</h2>
        </div>
        <span>기능별 UI 이전 대기</span>
      </div>
      <p class="town-hub__notice">
        기록관은 최종 저장을, 도감은 획득한 아이템을 기준으로 열립니다. 현재는 데이터가 연결되지 않은 기능을 실행하지 않습니다.
      </p>
      <div class="town-hub__grid">
        <button
          v-for="feature in townFeatures"
          :key="feature.key"
          class="town-feature-card"
          type="button"
          aria-haspopup="dialog"
          @click="openFeature(feature.key, $event)"
        >
          <span class="town-feature-card__icon" aria-hidden="true">{{ feature.icon }}</span>
          <span><strong>{{ feature.label }}</strong><small>{{ feature.description }}</small></span>
          <i aria-hidden="true">→</i>
        </button>
      </div>
    </section>

    <section class="town-hud" aria-label="캐릭터 HUD">
      <nav class="town-hud__navigation" aria-label="이동과 시스템">
        <div class="town-hud__group">
          <strong>이동 / 진입</strong>
          <div>
            <button
              type="button"
              :disabled="!account.itemTemplates.length"
              :title="account.itemTemplates.length ? '인벤토리·장비 표시 화면으로 이동합니다' : '아이템 master-data를 불러오지 못했습니다'"
              @click="enterInventoryPreview"
            ><span aria-hidden="true">囊</span>인벤토리</button>
            <button class="is-active" type="button" aria-current="location"><span aria-hidden="true">里</span>마을</button>
            <button
              type="button"
              :disabled="!account.bosses.length"
              :title="account.bosses.length ? '보스 전투 표시 화면으로 이동합니다' : '보스 master-data를 불러오지 못했습니다'"
              @click="enterBossPreview"
            ><span aria-hidden="true">王</span>보스존</button>
            <button
              type="button"
              :disabled="!account.fieldZones.length"
              :title="account.fieldZones.length ? '필드 전투 표시 화면으로 이동합니다' : '필드 master-data를 불러오지 못했습니다'"
              @click="enterFieldPreview"
            ><span aria-hidden="true">野</span>필드존</button>
          </div>
        </div>
        <div class="town-hud__group">
          <strong>성장 / 시스템</strong>
          <div>
            <button type="button" aria-haspopup="dialog" @click="openFeature('save', $event)"><span aria-hidden="true">存</span>수동 저장</button>
            <button
              type="button"
              :disabled="!canEnterSkillEnhancement"
              :title="canEnterSkillEnhancement ? '스킬·강화 규칙 화면으로 이동합니다' : '스킬·강화 master-data를 불러오지 못했습니다'"
              @click="enterSkillEnhancementPreview"
            ><span aria-hidden="true">鍛</span>스킬·강화</button>
            <button
              type="button"
              :disabled="!account.itemTemplates.length"
              :title="account.itemTemplates.length ? '상점 카탈로그·설정 미리보기로 이동합니다' : '아이템 master-data를 불러오지 못했습니다'"
              @click="enterShopSettingsPreview"
            ><span aria-hidden="true">店</span>상점·설정</button>
            <button type="button" disabled title="전투 runtime 이전 뒤 활성화됩니다"><span aria-hidden="true">自</span>특보 자동</button>
          </div>
        </div>
      </nav>

      <div class="town-hud__character">
        <div class="town-hud__portrait" aria-hidden="true">
          <span>{{ game.model.avatarText }}</span>
          <i />
        </div>
        <div class="town-hud__identity">
          <small>{{ game.model.characterLabel }}</small>
          <strong>{{ game.model.characterName }}</strong>
          <span>{{ game.model.levelLabel }} · {{ game.model.goldLabel }} Gold</span>
        </div>
        <dl class="town-hud__stats">
          <div v-for="stat in game.model.stats" :key="stat.key" :data-tone="stat.tone">
            <dt>{{ stat.label }}</dt><dd>{{ stat.value }}</dd>
          </div>
        </dl>
      </div>

      <div class="town-hud__skills" aria-label="기본 스킬 슬롯 미리보기">
        <div class="town-hud__skills-heading">
          <strong>스킬 슬롯</strong>
          <span>{{ game.model.snapshotEmpty ? '신규 기본 상태' : '서버 snapshot 상태' }}</span>
        </div>
        <div class="town-hud__skill-grid">
          <div v-for="skill in game.model.skills" :key="skill.key" :data-tone="skill.tone" :title="skill.name">
            <b>{{ skill.slotKey }}</b>
            <span>Lv.{{ skill.level }}</span>
          </div>
        </div>
      </div>
    </section>

    <aside class="town-data-boundary" aria-label="현재 데이터 연결 범위">
      <span aria-hidden="true">i</span>
      <div>
        <strong>서버 저장을 읽어 typed 게임 상태에 적용했습니다.</strong>
        <p v-if="game.model.snapshotEmpty">신규 캐릭터의 빈 snapshot은 정상 상태로 처리해 기본 능력치로 시작합니다. 저장 요청·자동 저장·보상 변경은 아직 실행하지 않습니다.</p>
        <p v-else>골드·상세 능력치·스킬·최근 구역은 선택 캐릭터의 서버 snapshot을 사용합니다. 이번 단계는 읽기 전용이며 저장 요청과 보상 변경은 실행하지 않습니다.</p>
      </div>
    </aside>
  </div>

  <Teleport to="body">
    <div v-if="game.activeFeature" class="town-feature-modal-backdrop" @click.self="closeFeature">
      <section
        ref="modalPanel"
        class="town-feature-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="town-feature-modal-title"
        tabindex="-1"
      >
        <button ref="modalClose" class="town-feature-modal__close" type="button" aria-label="안내 닫기" @click="closeFeature">×</button>
        <span class="town-feature-modal__icon" aria-hidden="true">{{ game.activeFeature.icon }}</span>
        <p>기능 연결 안내</p>
        <h2 id="town-feature-modal-title">{{ game.activeFeature.label }}</h2>
        <p>{{ game.activeFeature.description }}</p>
        <div class="town-feature-modal__boundary">
          <strong>현재는 실행하지 않습니다</strong>
          <span>{{ game.activeFeature.nextStep }}</span>
        </div>
        <button class="account-button account-button--primary" type="button" @click="closeFeature">마을로 돌아가기</button>
      </section>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref } from 'vue';
import { useAccountStore, useGameStore } from '@/stores';
import { TOWN_FEATURES, type TownFeatureKey } from '@/game/adapters/townHud';

const account = useAccountStore();
const game = useGameStore();
const { background = false } = defineProps<{ background?: boolean }>();
const modalPanel = ref<HTMLElement | null>(null);
const modalClose = ref<HTMLButtonElement | null>(null);
const featureTrigger = ref<HTMLElement | null>(null);
const townFeatures = ['record', 'codex', 'ranking', 'mailbox'].map((key) => TOWN_FEATURES[key as TownFeatureKey]);
const canEnterSkillEnhancement = computed(() => (
  account.skills.length > 0
  && account.enhancementGroups.length > 0
  && account.enhancementLevels.length > 0
  && account.itemTemplates.some((item) => Boolean(item.enhanceGroupCode))
));

function openFeature(key: TownFeatureKey, event: Event) {
  featureTrigger.value = event.currentTarget as HTMLElement;
  game.openFeature(key);
  void nextTick(() => (modalClose.value ?? modalPanel.value)?.focus());
}

function closeFeature() {
  game.closeFeature();
  void nextTick(() => featureTrigger.value?.focus());
}

function enterFieldPreview() {
  game.enterFieldPreview(account.fieldZones);
}

function enterBossPreview() {
  game.enterBossPreview(account.bosses);
}

function enterInventoryPreview() {
  game.enterInventoryPreview(account.itemTemplates);
}

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

function enterShopSettingsPreview() {
  game.enterShopSettingsPreview(account.itemTemplates);
}

function changeCharacter() {
  account.changeCharacter();
}

function logout() {
  void account.logout();
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && game.activeFeature) closeFeature();
}

window.addEventListener('keydown', handleKeydown);
onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
  game.closeFeature();
});
</script>
