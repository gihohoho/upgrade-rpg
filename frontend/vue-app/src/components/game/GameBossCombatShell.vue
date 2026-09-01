<template>
  <div v-if="boss && town" class="boss-shell" data-zone="boss">
    <header class="boss-command-bar">
      <button type="button" @click="game.returnTown"><span aria-hidden="true">←</span> 마을로 돌아가기</button>
      <div>
        <span>보스 전투 UI</span>
        <strong>{{ boss.selectedBoss.name }}</strong>
      </div>
      <span class="boss-command-bar__status"><i aria-hidden="true" /> runtime 연결 대기</span>
    </header>

    <section class="boss-arena" :data-boss-type="boss.selectedBoss.bossType" aria-labelledby="boss-arena-title">
      <div class="boss-arena__embers" aria-hidden="true"><i /><i /><i /></div>
      <div class="boss-arena__content">
        <p>{{ boss.selectedBoss.tierLabel }} · display only</p>
        <h2 id="boss-arena-title">{{ boss.selectedBoss.name }}</h2>
        <span>{{ boss.selectedBoss.description }}</span>
        <div class="boss-arena__rules" aria-label="보스 소환 규칙 요약">
          <span><b>분류</b>{{ boss.selectedBoss.typeLabel }}</span>
          <span><b>입장 조건</b>{{ boss.selectedBoss.entryCondition }}</span>
          <span><b>재도전</b>{{ boss.selectedBoss.cooldownLabel }}</span>
        </div>
      </div>

      <div class="boss-enemy" aria-label="보스 상태">
        <span class="boss-enemy__badge">{{ boss.selectedBoss.typeLabel }}</span>
        <div class="boss-enemy__sigil" aria-hidden="true">
          <span>{{ boss.selectedBoss.sigilText }}</span><i /><i /><i />
        </div>
        <strong>{{ boss.selectedBoss.name }}</strong>
        <div
          class="boss-enemy__hp"
          role="progressbar"
          aria-label="보스 체력"
          :aria-valuenow="boss.bossHp"
          aria-valuemin="0"
          :aria-valuemax="boss.selectedBoss.hp"
        >
          <i :style="{ width: `${boss.bossHpPercent}%` }" />
          <span>{{ boss.bossHpLabel }}</span>
        </div>
      </div>
    </section>

    <section class="boss-browser" aria-labelledby="boss-browser-title">
      <div class="boss-section-heading">
        <div>
          <p>Master-data bosses</p>
          <h2 id="boss-browser-title">도전 보스 선택</h2>
        </div>
        <span>{{ activePosition + 1 }} / {{ filteredBosses.length }}</span>
      </div>
      <div class="boss-browser__tabs" role="group" aria-label="보스 종류">
        <button
          v-for="type in availableTypes"
          :key="type.key"
          type="button"
          :class="{ 'is-active': boss.selectedBoss.bossType === type.key }"
          :aria-pressed="boss.selectedBoss.bossType === type.key"
          @click="selectType(type.key)"
        >{{ type.label }} <small>{{ type.count }}</small></button>
      </div>
      <div class="boss-browser__controls">
        <button type="button" :disabled="activePosition === 0" @click="selectRelative(-1)">← 이전 보스</button>
        <button type="button" :disabled="activePosition === filteredBosses.length - 1" @click="selectRelative(1)">다음 보스 →</button>
      </div>
      <div class="boss-browser__rail" aria-label="보스 목록">
        <button
          v-for="item in visibleBosses"
          :key="item.code"
          type="button"
          :class="{ 'is-active': item.index === boss.selectedIndex }"
          :aria-pressed="item.index === boss.selectedIndex"
          @click="game.selectBossPreview(item.index)"
        >
          <span>{{ item.tierLabel }}</span>
          <strong>{{ item.name }}</strong>
          <small>HP {{ item.hpLabel }} · {{ item.cooldownLabel }}</small>
        </button>
      </div>
    </section>

    <section class="boss-dashboard" aria-label="보스전 준비 HUD">
      <div class="boss-fighter-card">
        <div class="boss-fighter-card__portrait" aria-hidden="true">{{ boss.avatarText }}</div>
        <div><span>{{ boss.characterLabel }}</span><strong>{{ boss.characterName }}</strong><small>{{ boss.levelLabel }} · {{ boss.goldLabel }} Gold</small></div>
        <dl>
          <div v-for="stat in boss.stats.slice(0, 3)" :key="stat.key"><dt>{{ stat.label }}</dt><dd>{{ stat.value }}</dd></div>
        </dl>
      </div>

      <div class="boss-drop-preview">
        <div><strong>드랍 규칙 미리보기</strong><span>난수 판정 없음</span></div>
        <p>{{ boss.selectedBoss.dropRuleLabel }}</p>
        <ul>
          <li>{{ boss.selectedBoss.skillDropRateLabel }}</li>
          <li v-if="boss.selectedBoss.equipmentSkillGuarantee">첫 장비 스킬 획득 보정 대상</li>
          <li v-for="drop in boss.selectedBoss.dropHighlights" :key="drop">{{ drop }}</li>
        </ul>
      </div>

      <div class="boss-action-preview" aria-live="polite">
        <div><strong>Action adapter</strong><span>HP·보상·쿨타임 변화 없음</span></div>
        <p v-for="log in boss.action.logs" :key="log.message">{{ log.message }}</p>
        <dl>
          <div><dt>master-data</dt><dd>연결됨</dd></div>
          <div><dt>server snapshot</dt><dd>미연결</dd></div>
          <div><dt>combat timer / random</dt><dd>정지</dd></div>
        </dl>
      </div>
    </section>

    <aside class="boss-data-boundary" aria-label="보스 미리보기 데이터 경계">
      <span aria-hidden="true">!</span>
      <div>
        <strong>보스를 눌러도 실제 소환·전투·보상 지급은 실행되지 않습니다.</strong>
        <p>보스 이름·타입·티어·HP·소환 규칙·쿨타임은 PostgreSQL master-data를 사용합니다. snapshot load/save·자동 저장·전투 timer·HP 감소·난수 드랍·보상·쿨타임 변경은 아직 연결하지 않습니다.</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { BossCombatType } from '@/game/adapters/bossCombat';
import { useGameStore } from '@/stores';

const game = useGameStore();
const boss = computed(() => game.bossModel);
const town = computed(() => game.model);
const filteredBosses = computed(() => {
  if (!boss.value) return [];
  return boss.value.bosses.filter((item) => item.bossType === boss.value?.selectedBoss.bossType);
});
const activePosition = computed(() => Math.max(0, filteredBosses.value.findIndex((item) => item.index === boss.value?.selectedIndex)));
const visibleBosses = computed(() => {
  const start = Math.floor(activePosition.value / 6) * 6;
  return filteredBosses.value.slice(start, start + 6);
});
const availableTypes = computed(() => {
  const bosses = boss.value?.bosses ?? [];
  return ([
    { key: 'normal', label: '일반 보스' },
    { key: 'special', label: '특수 보스' },
  ] as const).map((type) => ({ ...type, count: bosses.filter((item) => item.bossType === type.key).length })).filter((type) => type.count > 0);
});

function selectType(type: BossCombatType) {
  const first = boss.value?.bosses.find((item) => item.bossType === type);
  if (first) game.selectBossPreview(first.index);
}

function selectRelative(offset: number) {
  const target = filteredBosses.value[activePosition.value + offset];
  if (target) game.selectBossPreview(target.index);
}
</script>
