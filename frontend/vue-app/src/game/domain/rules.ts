export interface BossRuleInput {
  id: number;
  isSpecial?: boolean;
  skillDropRate?: number;
}

export interface AbyssFragmentSpecialStats {
  attack: number;
  skillDmgAmp?: number;
  basicAtkDmgAmp?: number;
  skillProcChanceInc?: number;
  skillCoefficientInc?: number;
  skillCooldownReductionInc?: number;
  allSkillDamageInc?: number;
  allBuffValueInc?: number;
  cloneCountInc?: number;
  cloneAttackSpeedInc?: number;
  maxAttackSpeedCapInc?: number;
}

export function getNormalBossSkillDropRate(boss: BossRuleInput | null | undefined): number {
  if (!boss || !boss.skillDropRate || boss.skillDropRate <= 0) return 0;
  if (boss.isSpecial) return boss.skillDropRate;
  const multiplier = boss.id >= 1 && boss.id <= 9 ? 0.25 : 0.5;
  return boss.skillDropRate * multiplier;
}

export function isFirstEquipSkillGuaranteeBoss(boss: BossRuleInput | null | undefined): boolean {
  return Boolean(boss && !boss.isSpecial && boss.id >= 2 && boss.id <= 7);
}

export function getAbyssFragmentSpecialStats(name: string | null | undefined): AbyssFragmentSpecialStats | null {
  if (!name) return null;
  if (name.includes('심연의 편린 반지')) return { attack: 3417, skillDmgAmp: 1.0 };
  if (name.includes('심연의 편린 목걸이')) return { attack: 3417, basicAtkDmgAmp: 1.0 };
  if (name.includes('심연의 편린 스태프')) {
    return {
      attack: 3417,
      skillProcChanceInc: 0.1,
      skillCoefficientInc: 0.1,
      skillCooldownReductionInc: 0.1,
      allSkillDamageInc: 0.1,
      allBuffValueInc: 0.1,
      cloneCountInc: 2,
      cloneAttackSpeedInc: 0.001,
      maxAttackSpeedCapInc: 1.0,
    };
  }
  return null;
}
