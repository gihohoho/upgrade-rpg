<template>
  <div v-if="boss && town" class="boss-shell" data-zone="boss">
    <header class="boss-command-bar">
      <button type="button" @click="game.returnTown"><span aria-hidden="true">←</span> 마을로 돌아가기</button>
      <div>
        <span>보스 전투 UI</span>
        <strong>{{ boss.selectedBoss.name }}</strong>
      </div>
      <span class="boss-command-bar__status" :data-state="runtime.status"><i aria-hidden="true" /> {{ runtimeStatusLabel }}</span>
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
          :aria-valuenow="bossHp"
          aria-valuemin="0"
          :aria-valuemax="bossMaxHp"
        >
          <i :style="{ width: `${bossHpPercent}%` }" />
          <span>{{ bossHpLabel }}</span>
        </div>
      </div>
    </section>

    <section class="combat-runtime-panel" data-tone="boss" aria-label="클라이언트 전투 실행 상태">
      <div class="combat-runtime-panel__heading">
        <div><span>Client combat runtime</span><strong>기본 공격 timer</strong></div>
        <span class="combat-runtime-panel__status" :data-state="runtime.status"><i aria-hidden="true" />{{ runtimeStatusLabel }}</span>
      </div>
      <dl>
        <div><dt>대상</dt><dd>{{ runtime.targetName || boss.selectedBoss.name }}</dd></div>
        <div><dt>공격 간격</dt><dd>{{ Math.round(runtime.intervalMs) }}ms</dd></div>
        <div><dt>공격 횟수</dt><dd>{{ runtime.attackCount }}회</dd></div>
        <div><dt>최근 피해</dt><dd>{{ formatCompactNumber(runtime.lastDamage) }}</dd></div>
      </dl>
      <div class="combat-runtime-panel__actions">
        <button type="button" @click="toggleCombatRuntime">{{ runtimeActionLabel }}</button>
        <span>이 화면의 HP만 변하며 저장·Gold·드랍·쿨타임은 연결되지 않습니다.</span>
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
        <div><strong>Action adapter</strong><span>client HP 미리보기만 실행</span></div>
        <p v-for="log in boss.action.logs" :key="log.message">{{ log.message }}</p>
        <dl>
          <div><dt>master-data</dt><dd>연결됨</dd></div>
          <div><dt>server snapshot</dt><dd>미연결</dd></div>
          <div><dt>combat timer</dt><dd>{{ runtimeStatusLabel }}</dd></div>
          <div><dt>random / rewards</dt><dd>미연결</dd></div>
        </dl>
      </div>
    </section>

    <aside class="boss-data-boundary" aria-label="보스 미리보기 데이터 경계">
      <span aria-hidden="true">!</span>
      <div>
        <strong>기본 공격 timer는 동작하지만 서버 캐릭터와 보상에는 반영되지 않습니다.</strong>
        <p>보스 이름·타입·티어·HP·소환 규칙·쿨타임은 PostgreSQL master-data를 사용합니다. 현재 HP는 이 화면 안에서만 감소하며 snapshot load/save·자동 저장·난수 드랍·보상·쿨타임 변경·자동 재소환은 아직 연결하지 않습니다.</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { BossCombatType } from '@/game/adapters/bossCombat';
import { formatCompactNumber } from '@/game/domain';
import { useGameStore } from '@/stores';

const game = useGameStore();
const boss = computed(() => game.bossModel);
const town = computed(() => game.model);
const runtime = computed(() => game.combatRuntime);
const runtimeMatchesTarget = computed(() => (
  runtime.value.targetType === 'boss'
  && runtime.value.targetKey === boss.value?.selectedBoss.code
));
const bossHp = computed(() => runtimeMatchesTarget.value ? runtime.value.currentHp : (boss.value?.bossHp ?? 0));
const bossMaxHp = computed(() => runtimeMatchesTarget.value ? runtime.value.maxHp : (boss.value?.selectedBoss.hp ?? 0));
const bossHpPercent = computed(() => runtimeMatchesTarget.value ? runtime.value.hpPercent : (boss.value?.bossHpPercent ?? 0));
const bossHpLabel = computed(() => `${formatCompactNumber(bossHp.value)} / ${formatCompactNumber(bossMaxHp.value)}`);
const runtimeStatusLabel = computed(() => {
  if (runtime.value.status === 'running') return '자동 전투 중';
  if (runtime.value.status === 'defeated') return '보스 격파 · 보상 없음';
  if (runtime.value.status === 'paused') {
    if (runtime.value.pauseReason === 'visibility') return '탭 비활성 · 일시정지';
    if (runtime.value.pauseReason === 'utility') return '게임 창 열림 · 일시정지';
    return '수동 일시정지';
  }
  return '전투 정지';
});
const runtimeActionLabel = computed(() => {
  if (runtime.value.status === 'running') return '전투 일시정지';
  if (runtime.value.status === 'paused') return '전투 재개';
  return '같은 보스 다시 시작';
});
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

function toggleCombatRuntime() {
  if (runtime.value.status === 'running') game.pauseCombatRuntime('manual');
  else if (runtime.value.status === 'paused') game.resumeCombatRuntime('manual');
  else game.restartCombatRuntime();
}
</script>
