<template>
  <div v-if="field && town" class="field-shell" data-zone="field">
    <header class="field-command-bar">
      <button type="button" @click="game.returnTown"><span aria-hidden="true">←</span> 마을로 돌아가기</button>
      <div>
        <span>필드 전투 UI</span>
        <strong>{{ field.selectedZone.name }}</strong>
      </div>
      <span class="field-command-bar__status" :data-state="runtime.status"><i aria-hidden="true" /> {{ runtimeStatusLabel }}</span>
    </header>

    <section class="field-arena" aria-labelledby="field-arena-title">
      <div class="field-arena__mist" aria-hidden="true" />
      <div class="field-arena__content">
        <p>Field {{ field.selectedZone.level }} · display only</p>
        <h2 id="field-arena-title">{{ field.selectedZone.name }}</h2>
        <span>{{ field.selectedZone.description }}</span>
        <div class="field-arena__rewards" aria-label="필드 보상 요약">
          <span><b>처치 골드</b>{{ field.selectedZone.goldRewardLabel }}</span>
          <span><b>입장 조건</b>{{ field.selectedZone.entryCondition }}</span>
          <span><b>순수공격력 보상</b>{{ field.selectedZone.farmReward }}</span>
        </div>
      </div>

      <div class="field-enemy" aria-label="필드 몬스터 상태">
        <span class="field-enemy__badge">FIELD TARGET</span>
        <div class="field-enemy__sigil" aria-hidden="true"><span>野</span><i /><i /></div>
        <strong>{{ field.selectedZone.name }} 몬스터</strong>
        <div
          class="field-enemy__hp"
          role="progressbar"
          aria-label="몬스터 체력"
          :aria-valuenow="enemyHp"
          aria-valuemin="0"
          :aria-valuemax="enemyMaxHp"
        >
          <i :style="{ width: `${enemyHpPercent}%` }" />
          <span>{{ enemyHpLabel }}</span>
        </div>
      </div>
    </section>

    <section class="combat-runtime-panel" data-tone="field" aria-label="클라이언트 전투 실행 상태">
      <div class="combat-runtime-panel__heading">
        <div><span>Client combat runtime</span><strong>기본 공격 timer</strong></div>
        <span class="combat-runtime-panel__status" :data-state="runtime.status"><i aria-hidden="true" />{{ runtimeStatusLabel }}</span>
      </div>
      <dl>
        <div><dt>대상</dt><dd>{{ runtime.targetName || field.selectedZone.name }}</dd></div>
        <div><dt>공격 간격</dt><dd>{{ Math.round(runtime.intervalMs) }}ms</dd></div>
        <div><dt>공격 횟수</dt><dd>{{ runtime.attackCount }}회</dd></div>
        <div><dt>최근 피해</dt><dd>{{ formatCompactNumber(runtime.lastDamage) }}</dd></div>
      </dl>
      <div class="combat-runtime-panel__actions">
        <button type="button" @click="toggleCombatRuntime">{{ runtimeActionLabel }}</button>
        <span>이 화면의 HP만 변하며 저장·Gold·보상·난수는 연결되지 않습니다.</span>
      </div>
    </section>

    <section class="field-zone-browser" aria-labelledby="field-zone-browser-title">
      <div class="field-section-heading">
        <div>
          <p>Master-data field zones</p>
          <h2 id="field-zone-browser-title">필드 선택</h2>
        </div>
        <span>{{ field.selectedIndex + 1 }} / {{ field.zones.length }}</span>
      </div>
      <div class="field-zone-browser__controls">
        <button type="button" :disabled="field.selectedIndex === 0" @click="selectRelative(-1)">← 이전 구역</button>
        <button type="button" :disabled="field.selectedIndex === field.zones.length - 1" @click="selectRelative(1)">다음 구역 →</button>
      </div>
      <div class="field-zone-browser__rail" aria-label="필드 구역 목록">
        <button
          v-for="zone in visibleZones"
          :key="zone.code"
          type="button"
          :class="{ 'is-active': zone.index === field.selectedIndex }"
          :aria-pressed="zone.index === field.selectedIndex"
          @click="game.selectFieldPreview(zone.index)"
        >
          <span>F{{ zone.level }}</span>
          <strong>{{ zone.name }}</strong>
          <small>HP {{ zone.enemyHpLabel }} · {{ zone.goldRewardLabel }} Gold</small>
        </button>
      </div>
    </section>

    <section class="field-combat-dashboard" aria-label="전투 준비 HUD">
      <div class="field-fighter-card">
        <div class="field-fighter-card__portrait" aria-hidden="true">{{ field.avatarText }}</div>
        <div>
          <span>{{ field.characterLabel }}</span>
          <strong>{{ field.characterName }}</strong>
          <small>{{ field.levelLabel }} · {{ field.goldLabel }} Gold</small>
        </div>
        <dl>
          <div><dt>기본 공격 예상</dt><dd>{{ field.basicAttackLabel }}</dd></div>
          <div><dt>치명타 예상</dt><dd>{{ field.criticalAttackLabel }}</dd></div>
          <div><dt>추가 공격속도</dt><dd>{{ field.attackSpeedLabel }}</dd></div>
        </dl>
      </div>

      <div class="field-skill-preview" aria-label="필드 스킬 미리보기">
        <div><strong>전투 스킬</strong><span>기본 domain 상태</span></div>
        <div class="field-skill-preview__grid">
          <span v-for="skill in field.skills" :key="skill.key" :data-tone="skill.tone" :title="skill.name">
            <b>{{ skill.slotKey }}</b><small>Lv.{{ skill.level }}</small>
          </span>
        </div>
      </div>

      <div class="field-action-preview" aria-live="polite">
        <div><strong>Action adapter</strong><span>client HP 미리보기만 실행</span></div>
        <p v-for="log in field.action.logs" :key="log.message">{{ log.message }}</p>
        <dl>
          <div><dt>master-data</dt><dd>연결됨</dd></div>
          <div><dt>server snapshot</dt><dd>미연결</dd></div>
          <div><dt>combat timer</dt><dd>{{ runtimeStatusLabel }}</dd></div>
        </dl>
      </div>
    </section>

    <aside class="field-data-boundary" aria-label="필드 미리보기 데이터 경계">
      <span aria-hidden="true">!</span>
      <div>
        <strong>기본 공격 timer는 동작하지만 서버 캐릭터와 보상에는 반영되지 않습니다.</strong>
        <p>필드 이름·HP·보상은 PostgreSQL master-data, 공격력 계산은 기본 typed domain을 사용합니다. 현재 HP는 이 화면 안에서만 감소하며 snapshot load/save·자동 저장·Gold·아이템 보상·난수 판정·자동 재등장은 아직 연결하지 않습니다.</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { formatCompactNumber } from '@/game/domain';
import { useGameStore } from '@/stores';

const game = useGameStore();
const field = computed(() => game.fieldModel);
const town = computed(() => game.model);
const runtime = computed(() => game.combatRuntime);
const runtimeMatchesTarget = computed(() => (
  runtime.value.targetType === 'field'
  && runtime.value.targetKey === field.value?.selectedZone.code
));
const enemyHp = computed(() => runtimeMatchesTarget.value ? runtime.value.currentHp : (field.value?.enemyHp ?? 0));
const enemyMaxHp = computed(() => runtimeMatchesTarget.value ? runtime.value.maxHp : (field.value?.selectedZone.enemyHp ?? 0));
const enemyHpPercent = computed(() => runtimeMatchesTarget.value ? runtime.value.hpPercent : (field.value?.enemyHpPercent ?? 0));
const enemyHpLabel = computed(() => `${formatCompactNumber(enemyHp.value)} / ${formatCompactNumber(enemyMaxHp.value)}`);
const runtimeStatusLabel = computed(() => {
  if (runtime.value.status === 'running') return '자동 전투 중';
  if (runtime.value.status === 'defeated') return '대상 처치 · 보상 없음';
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
  return '같은 대상 다시 시작';
});
const visibleZones = computed(() => {
  if (!field.value) return [];
  const start = Math.floor(field.value.selectedIndex / 4) * 4;
  return field.value.zones.slice(start, start + 4);
});

function selectRelative(offset: number) {
  if (!field.value) return;
  game.selectFieldPreview(field.value.selectedIndex + offset);
}

function toggleCombatRuntime() {
  if (runtime.value.status === 'running') game.pauseCombatRuntime('manual');
  else if (runtime.value.status === 'paused') game.resumeCombatRuntime('manual');
  else game.restartCombatRuntime();
}
</script>
