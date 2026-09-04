<template>
  <div v-if="model" class="skill-enhancement-shell" data-zone="skill-enhancement">
    <header class="skill-enhancement-command-bar">
      <div class="skill-enhancement-command-bar__actions">
        <button type="button" @click="game.returnTown"><span aria-hidden="true">←</span> 마을로</button>
        <button type="button" @click="game.returnInventoryPreview"><span aria-hidden="true">囊</span> 인벤토리</button>
      </div>
      <div>
        <span>Skill · enhancement UI</span>
        <strong>{{ model.characterName }}의 성장 규칙 미리보기</strong>
      </div>
      <span class="skill-enhancement-command-bar__status"><i aria-hidden="true" /> 사용·강화 잠금</span>
    </header>

    <section class="skill-enhancement-overview" aria-labelledby="skill-enhancement-overview-title">
      <div>
        <p>Typed master-data · display only</p>
        <h2 id="skill-enhancement-overview-title">스킬 성장과 장비 강화</h2>
        <span>{{ model.characterLabel }} · {{ model.levelLabel }} · {{ model.goldLabel }} Gold</span>
      </div>
      <dl>
        <div><dt>스킬 계열</dt><dd>{{ model.skills.length }}개</dd></div>
        <div><dt>강화 그룹</dt><dd>{{ model.enhancementGroups.length }}개</dd></div>
        <div><dt>데이터 상태</dt><dd>규칙만 연결</dd></div>
      </dl>
    </section>

    <section class="skill-workspace" aria-label="스킬 성장 규칙 미리보기">
      <div class="skill-browser">
        <div class="skill-enhancement-section-heading">
          <div><p>Skill route</p><h2>스킬 계열</h2></div>
          <span>Q → W → E → R → T → F → D → SQ → SW → M</span>
        </div>
        <div class="skill-browser__grid" aria-label="스킬 선택">
          <button
            v-for="skill in model.skills"
            :key="skill.id"
            type="button"
            :data-tone="skill.tone"
            :class="{ 'is-selected': skill.id === model.selectedSkill.id, 'is-locked': skill.currentLevel === 0 }"
            :aria-pressed="skill.id === model.selectedSkill.id"
            @click="game.selectSkillEnhancementSkill(skill.id)"
          >
            <b>{{ skill.slotKey }}</b>
            <span>{{ skill.name }}</span>
            <small>Lv.{{ skill.effectiveLevel }} / {{ skill.maxLevel }}</small>
          </button>
        </div>
        <p class="skill-browser__note">현재 스킬 레벨은 서버 snapshot의 typed 상태입니다. 회색 표시는 아직 획득하지 않은 샘플입니다.</p>
      </div>

      <article class="skill-detail" :data-tone="model.selectedSkill.tone" aria-labelledby="skill-detail-title">
        <div class="skill-detail__icon" aria-hidden="true">{{ model.selectedSkill.slotKey }}</div>
        <div class="skill-detail__heading">
          <p>{{ model.selectedSkill.bookName }}</p>
          <h2 id="skill-detail-title">{{ model.selectedSkill.name }}</h2>
          <span>{{ model.selectedSkill.description }}</span>
        </div>
        <dl class="skill-detail__levels">
          <div><dt>현재 레벨</dt><dd>Lv.{{ model.selectedSkill.currentLevel }}</dd></div>
          <div><dt>장비 보너스</dt><dd>+{{ model.selectedSkill.bonusLevel }}</dd></div>
          <div><dt>표시 레벨</dt><dd>Lv.{{ model.selectedSkill.effectiveLevel }}</dd></div>
        </dl>
        <ul class="skill-detail__effects">
          <li v-for="line in model.selectedSkill.effectLines" :key="line">{{ line }}</li>
          <li v-if="!model.selectedSkill.effectLines.length">세부 효과가 아직 등록되지 않았습니다.</li>
        </ul>
        <dl class="skill-detail__metrics">
          <div><dt>기본 발동률</dt><dd>{{ model.selectedSkill.procRateLabel }}</dd></div>
          <div><dt>공격 계수</dt><dd>{{ model.selectedSkill.coefficientLabel }}</dd></div>
          <div><dt>쿨타임</dt><dd>{{ model.selectedSkill.cooldownLabel }}</dd></div>
          <div><dt>보너스 그룹</dt><dd>{{ model.selectedSkill.bonusGroup ?? '적용 안 함' }}</dd></div>
        </dl>
        <div class="skill-detail__rule" :data-awakening="model.selectedSkill.awakened">
          <strong>강화권 적용 규칙</strong>
          <span>{{ model.selectedSkill.firstUseRule }}</span>
          <small v-if="model.selectedSkill.slotKey === 'SQ' || model.selectedSkill.slotKey === 'SW'">탈리스만 A/B 레벨 보너스를 계승하지 않습니다.</small>
        </div>
        <button type="button" disabled title="실제 snapshot과 재료 소비 queue를 연결한 뒤 활성화됩니다">
          {{ model.selectedSkill.bookName }} 사용 · 예상 Lv.{{ model.selectedSkill.firstUseResultLevel }}
        </button>
      </article>
    </section>

    <section class="enhancement-workspace" aria-labelledby="enhancement-workspace-title">
      <div class="skill-enhancement-section-heading enhancement-workspace__heading">
        <div><p>Equipment rules</p><h2 id="enhancement-workspace-title">장비 강화 작업대</h2></div>
        <span>결과 난수·Gold·재료·아이템 변화 없음</span>
      </div>

      <div class="enhancement-layout">
        <div class="enhancement-items">
          <strong>강화 대상 샘플</strong>
          <div aria-label="강화 아이템 선택">
            <button
              v-for="item in model.enhancementItems"
              :key="item.code"
              type="button"
              :class="{ 'is-selected': item.code === model.selectedEnhancementItem.code }"
              :data-frame="item.frameTone"
              :aria-pressed="item.code === model.selectedEnhancementItem.code"
              @click="game.selectEnhancementItem(item.code)"
            >
              <span aria-hidden="true">{{ item.iconText }}</span>
              <i><b>{{ item.name }}</b><small>{{ item.typeLabel }} · {{ item.tierLabel }}</small></i>
            </button>
          </div>
        </div>

        <div class="enhancement-ladder">
          <div>
            <strong>{{ model.selectedEnhancementGroup.name }}</strong>
            <span>최대 +{{ model.selectedEnhancementGroup.maxLevel }} · {{ model.selectedEnhancementGroup.description }}</span>
          </div>
          <nav aria-label="강화 단계 선택">
            <button
              v-for="step in model.enhancementSteps"
              :key="step.fromLevel"
              type="button"
              :class="{ 'is-selected': step.fromLevel === model.selectedEnhancementStep.fromLevel }"
              :aria-pressed="step.fromLevel === model.selectedEnhancementStep.fromLevel"
              @click="game.selectEnhancementLevel(step.fromLevel)"
            >
              <b>{{ step.levelLabel }}</b><small>{{ step.successRateLabel }}</small>
            </button>
          </nav>
        </div>

        <article class="enhancement-detail" aria-labelledby="enhancement-detail-title">
          <div class="enhancement-detail__item">
            <span :data-frame="model.selectedEnhancementItem.frameTone" aria-hidden="true">{{ model.selectedEnhancementItem.iconText }}</span>
            <div><p>{{ model.selectedEnhancementGroup.name }}</p><h2 id="enhancement-detail-title">{{ model.selectedEnhancementItem.name }}</h2></div>
          </div>
          <div class="enhancement-detail__chance">
            <div><span>성공 확률</span><strong>{{ model.selectedEnhancementStep.successRateLabel }}</strong></div>
            <meter min="0" max="1" :value="model.selectedEnhancementStep.successRate">{{ model.selectedEnhancementStep.successRateLabel }}</meter>
            <small>기본 확률 {{ model.selectedEnhancementStep.successRateLabel }} + 미연결 보너스 0%</small>
          </div>
          <dl>
            <div><dt>선택 단계</dt><dd>{{ model.selectedEnhancementStep.levelLabel }}</dd></div>
            <div><dt>강화 비용</dt><dd>{{ model.selectedEnhancementStep.goldCostLabel }}</dd></div>
            <div><dt>비용 기준</dt><dd>{{ model.selectedEnhancementStep.costSourceLabel }}</dd></div>
            <div><dt>필요 재료</dt><dd>{{ model.selectedEnhancementStep.materialLabel }}</dd></div>
          </dl>
          <div class="enhancement-detail__stats">
            <span v-for="stat in model.selectedEnhancementStep.resultStats" :key="stat.label"><b>{{ stat.label }}</b>{{ stat.value }}</span>
          </div>
          <p>{{ model.selectedEnhancementStep.failureLabel }}</p>
          <div class="enhancement-detail__actions">
            <button type="button" disabled title="snapshot·Gold·재료 소비와 난수 결과를 연결한 뒤 활성화됩니다">강화 1회</button>
            <button type="button" disabled title="연속 강화 orchestration은 아직 연결하지 않습니다">강화 20회</button>
          </div>
        </article>
      </div>
    </section>

    <section class="skill-enhancement-action-preview" aria-live="polite">
      <div><strong>Action adapter</strong><span>선택만 변경 · runtime과 server state 변화 없음</span></div>
      <p v-for="log in model.action.logs" :key="log.message">{{ log.message }}</p>
      <dl>
        <div><dt>master-data</dt><dd>연결됨</dd></div>
        <div><dt>snapshot / inventory</dt><dd>스킬 읽기 연결 / 아이템 샘플</dd></div>
        <div><dt>random / save</dt><dd>잠김</dd></div>
      </dl>
    </section>

    <aside class="skill-enhancement-data-boundary" aria-label="스킬과 강화 미리보기 데이터 경계">
      <span aria-hidden="true">!</span>
      <div>
        <strong>현재 화면은 실제 보유 스킬·장비·재료가 아닌 규칙 미리보기입니다.</strong>
        <p>master-data와 서버 snapshot의 스킬 상태를 읽습니다. 스킬강화권 사용·장비 강화·Gold/재료 소비·난수 결과·snapshot 저장·자동 저장은 실행하지 않습니다.</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useGameStore } from '@/stores';

const game = useGameStore();
const model = computed(() => game.skillEnhancementModel);
</script>
