<template>
  <div v-if="field && town" class="field-shell" data-zone="field">
    <header class="field-command-bar">
      <button type="button" @click="game.returnTown"><span aria-hidden="true">←</span> 마을로 돌아가기</button>
      <div>
        <span>필드 전투 UI</span>
        <strong>{{ field.selectedZone.name }}</strong>
      </div>
      <span class="field-command-bar__status"><i aria-hidden="true" /> runtime 연결 대기</span>
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
          :aria-valuenow="field.enemyHp"
          aria-valuemin="0"
          :aria-valuemax="field.selectedZone.enemyHp"
        >
          <i :style="{ width: `${field.enemyHpPercent}%` }" />
          <span>{{ field.enemyHpLabel }}</span>
        </div>
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
        <div><strong>Action adapter</strong><span>HP·Gold 변화 없음</span></div>
        <p v-for="log in field.action.logs" :key="log.message">{{ log.message }}</p>
        <dl>
          <div><dt>master-data</dt><dd>연결됨</dd></div>
          <div><dt>server snapshot</dt><dd>미연결</dd></div>
          <div><dt>combat timer</dt><dd>정지</dd></div>
        </dl>
      </div>
    </section>

    <aside class="field-data-boundary" aria-label="필드 미리보기 데이터 경계">
      <span aria-hidden="true">!</span>
      <div>
        <strong>구역을 눌러도 실제 전투나 저장은 시작되지 않습니다.</strong>
        <p>필드 이름·HP·보상은 PostgreSQL master-data, 캐릭터 계산은 기본 typed domain을 사용합니다. snapshot load/save·자동 저장·전투 timer·난수 판정은 아직 연결하지 않습니다.</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useGameStore } from '@/stores';

const game = useGameStore();
const field = computed(() => game.fieldModel);
const town = computed(() => game.model);
const visibleZones = computed(() => {
  if (!field.value) return [];
  const start = Math.floor(field.value.selectedIndex / 4) * 4;
  return field.value.zones.slice(start, start + 4);
});

function selectRelative(offset: number) {
  if (!field.value) return;
  game.selectFieldPreview(field.value.selectedIndex + offset);
}
</script>
