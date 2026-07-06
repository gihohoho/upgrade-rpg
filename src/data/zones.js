const U_A = 1;
const U_B = Math.pow(10000, 1);
const U_C = Math.pow(10000, 2);
const U_D = Math.pow(10000, 3);
const U_E = Math.pow(10000, 4);
const U_F = Math.pow(10000, 5);
const U_G = Math.pow(10000, 6);
const U_H = Math.pow(10000, 7);
const GOLD_RATIO_AFTER_ABYSS = 190 / 117000;

const customZones = [
  // 1~3: 마그토늄
  {
    name: "마그토늄 노가다",
    maxHp: 5 * U_B,
    goldReward: 1500,
    req: { text: "순수공격력 1000 미만", minAtk: 0, maxAtk: 999 },
  },
  {
    name: "마그토늄 노가다 [5회]",
    maxHp: 25 * U_B,
    goldReward: 7500,
    req: { text: "순수공격력 1000 미만", minAtk: 0, maxAtk: 999 },
  },
  {
    name: "마그토늄 노가다 [20회]",
    maxHp: 100 * U_B,
    goldReward: 30000,
    req: { text: "순수공격력 1000 미만", minAtk: 0, maxAtk: 999 },
  },

  // 4~6: 이계 던전
  {
    name: "이계 던전 쩔 노가다",
    maxHp: 5000000,
    goldReward: 6 * U_B,
    req: { text: "순수공격력 5000 미만", minAtk: 0, maxAtk: 4999 },
  },
  {
    name: "이계 던전 쩔 노가다 [5회]",
    maxHp: 25000000,
    goldReward: 30 * U_B,
    req: { text: "순수공격력 5000 미만", minAtk: 0, maxAtk: 4999 },
  },
  {
    name: "이계 던전 쩔 노가다 [20회]",
    maxHp: 100000000,
    goldReward: 120 * U_B,
    req: { text: "순수공격력 5000 미만", minAtk: 0, maxAtk: 4999 },
  },

  // 7: 테라니움
  {
    name: "테라니움 노가다",
    maxHp: 10 * U_C,
    goldReward: 600 * U_B,
    req: { text: "순수공격력 1B 미만", minAtk: 0, maxAtk: 9999 },
  },

  // 8~11: 할렘
  {
    name: "할렘 던전 노가다",
    maxHp: 10000000000,
    goldReward: 44800000,
    req: { text: "순수공격력 24B 미만", minAtk: 0, maxAtk: 239999 },
    farm: { gain: 1, cap: 120000, capText: "12B", prob: 1.0 },
  },
  {
    name: "할렘 던전 노가다 [5회]",
    maxHp: 50000000000,
    goldReward: 224000000,
    req: { text: "순수공격력 24B 미만", minAtk: 0, maxAtk: 239999 },
    farm: { gain: 5, cap: 120000, capText: "12B", prob: 1.0 },
  },
  {
    name: "할렘 던전 노가다 [20회]",
    maxHp: 200000000000,
    goldReward: 896000000,
    req: { text: "순수공격력 24B 미만", minAtk: 0, maxAtk: 239999 },
    farm: { gain: 20, cap: 120000, capText: "12B", prob: 1.0 },
  },
  {
    name: "할렘 던전 노가다 [50회]",
    maxHp: 500000000000,
    goldReward: 2240000000,
    req: { text: "순수공격력 24B 미만", minAtk: 0, maxAtk: 239999 },
    farm: { gain: 50, cap: 120000, capText: "12B", prob: 1.0 },
  },

  // 12~15: 루크
  {
    name: "루크 쩔 노가다",
    maxHp: 1 * U_D,
    goldReward: 42 * U_C,
    req: { text: "순수공격력 9B~120B", minAtk: 90000, maxAtk: 1200000 },
    farm: {
      gain: 2,
      cap: 600000,
      capText: "60B",
      prob: 1.0,
      specialText: "※순수 공격력이 12B 이하면 상승치 40배 (80 증가)",
      specialThreshold: 120000,
      specialMult: 40,
    },
  },
  {
    name: "루크 쩔 노가다 [5회]",
    maxHp: 5 * U_D,
    goldReward: 210 * U_C,
    req: { text: "순수공격력 9B~120B", minAtk: 90000, maxAtk: 1200000 },
    farm: {
      gain: 10,
      cap: 600000,
      capText: "60B",
      prob: 1.0,
      specialText: "※순수 공격력이 12B 이하면 상승치 40배 (400 증가)",
      specialThreshold: 120000,
      specialMult: 40,
    },
  },
  {
    name: "루크 쩔 노가다 [20회]",
    maxHp: 20 * U_D,
    goldReward: 840 * U_C,
    req: { text: "순수공격력 9B~120B", minAtk: 90000, maxAtk: 1200000 },
    farm: {
      gain: 40,
      cap: 600000,
      capText: "60B",
      prob: 1.0,
      specialText: "※순수 공격력이 12B 이하면 상승치 40배 (1600 증가)",
      specialThreshold: 120000,
      specialMult: 40,
    },
  },
  {
    name: "루크 쩔 노가다 [100회]",
    maxHp: 100 * U_D,
    goldReward: 4200 * U_C,
    req: { text: "순수공격력 18B~120B", minAtk: 180000, maxAtk: 1200000 },
    farm: { gain: 200, cap: 600000, capText: "60B", prob: 1.0 },
  },

  // 16~18: 핀드 워
  {
    name: "핀드 워 쩔 노가다",
    maxHp: 300000000000000,
    goldReward: 5000000000000,
    req: { text: "순수공격력 50B~520B", minAtk: 500000, maxAtk: 5200000 },
    farm: {
      gain: 6,
      cap: 2600000,
      capText: "260B",
      prob: 1.0,
      specialText: "※순수 공격력이 60B 이하면 상승치 30배 (180 증가)",
      specialThreshold: 600000,
      specialMult: 30,
    },
  },
  {
    name: "핀드 워 쩔 노가다 [5회]",
    maxHp: 1500000000000000,
    goldReward: 25000000000000,
    req: { text: "순수공격력 50B~520B", minAtk: 500000, maxAtk: 5200000 },
    farm: {
      gain: 30,
      cap: 2600000,
      capText: "260B",
      prob: 1.0,
      specialText: "※순수 공격력이 60B 이하면 상승치 30배 (900 증가)",
      specialThreshold: 600000,
      specialMult: 30,
    },
  },
  {
    name: "핀드 워 쩔 노가다 [10회]",
    maxHp: 3000000000000000,
    goldReward: 50000000000000,
    req: { text: "순수공격력 65B~520B", minAtk: 650000, maxAtk: 5200000 },
    farm: { gain: 60, cap: 2600000, capText: "260B", prob: 1.0 },
  },

  // 19: 폭풍의 항로
  {
    name: "폭풍의 항로 노가다",
    maxHp: 9000000000000000,
    goldReward: 13000000000000,
    req: { text: "순수공격력 80B~520B", minAtk: 800000, maxAtk: 5200000 },
    farm: { gain: 120, cap: 2600000, capText: "260B", prob: 1.0 },
  },

  // 20: 심연의 폭풍의 항로
  {
    name: "심연의 폭풍의 항로 노가다",
    maxHp: 45000000000000000,
    goldReward: 65000000000000,
    req: { text: "순수공격력 120B~520B", minAtk: 1200000, maxAtk: 5200000 },
    farm: { gain: 600, cap: 2600000, capText: "260B", prob: 1.0 },
  },

  // 21~23: 아이올라이트
  {
    name: "아이올라이트 노가다",
    maxHp: 117000000000000000,
    goldReward: 190000000000000,
    req: { text: "순수공격력 200B~4000B", minAtk: 2000000, maxAtk: 40000000 },
    farm: {
      gain: 6,
      cap: 20000000,
      capText: "2000B",
      prob: 1.0,
      specialText: "※순수 공격력이 260B 이하면 상승치 50배 (300 증가)",
      specialThreshold: 2600000,
      specialMult: 50,
    },
  },
  {
    name: "아이올라이트 노가다 [5회]",
    maxHp: 585000000000000000,
    goldReward: 950000000000000,
    req: { text: "순수공격력 200B~4000B", minAtk: 2000000, maxAtk: 40000000 },
    farm: {
      gain: 30,
      cap: 20000000,
      capText: "2000B",
      prob: 1.0,
      specialText: "※순수 공격력이 260B 이하면 상승치 50배 (1500 증가)",
      specialThreshold: 2600000,
      specialMult: 50,
    },
  },
  {
    name: "아이올라이트 노가다 [20회]",
    maxHp: 2340000000000000000,
    goldReward: 3800000000000000,
    req: { text: "순수공격력 200B~4000B", minAtk: 2000000, maxAtk: 40000000 },
    farm: {
      gain: 120,
      cap: 20000000,
      capText: "2000B",
      prob: 1.0,
      specialText: "※순수 공격력이 260B 이하면 상승치 50배 (6000 증가)",
      specialThreshold: 2600000,
      specialMult: 50,
    },
  },

  // 24~26: 절망의 광석
  {
    name: "절망의 광석 노가다",
    maxHp: 11700000000000000000,
    goldReward: 19000000000000000,
    req: { text: "순수공격력 300B~4000B", minAtk: 3000000, maxAtk: 40000000 },
    farm: { gain: 600, cap: 20000000, capText: "2000B", prob: 1.0 },
  },
  {
    name: "절망의 광석 노가다 [5회]",
    maxHp: 58500000000000000000,
    goldReward: 95000000000000000,
    req: { text: "순수공격력 500B~4000B", minAtk: 5000000, maxAtk: 40000000 },
    farm: { gain: 3000, cap: 20000000, capText: "2000B", prob: 1.0 },
  },
  // 💡 여기서부터 상승량 5배 증폭 적용 시작
  {
    name: "절망의 광석 노가다 [20회]",
    maxHp: 234000000000000000000,
    goldReward: 380000000000000000,
    req: { text: "순수공격력 1000B~5C", minAtk: 10000000, maxAtk: 500000000 },
    farm: {
      gain: 60,
      cap: 250000000,
      capText: "2C 5000B",
      prob: 1.0,
      specialText: "※순수 공격력이 2000B 이하면 상승치 50배 (3000 증가)",
      specialThreshold: 20000000,
      specialMult: 50,
    },
  },

  // 27~30: 골든 베릴
  {
    name: "골든 베릴 노가다",
    maxHp: 9.36 * U_F,
    goldReward: Math.round(9.36 * U_F * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 1500B~5C", minAtk: 15000000, maxAtk: 500000000 },
    farm: {
      gain: 240,
      cap: 250000000,
      capText: "2C 5000B",
      prob: 1.0,
      specialText: "※순수 공격력이 2000B 이하면 상승치 50배 (12000 증가)",
      specialThreshold: 20000000,
      specialMult: 50,
    },
  },
  {
    name: "골든 베릴 노가다 [5회]",
    maxHp: 46.8 * U_F,
    goldReward: Math.round(46.8 * U_F * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 2000B~5C", minAtk: 20000000, maxAtk: 500000000 },
    farm: { gain: 1200, cap: 250000000, capText: "2C 5000B", prob: 1.0 },
  },
  {
    name: "골든 베릴 노가다 [20회]",
    maxHp: 187.2 * U_F,
    goldReward: Math.round(187.2 * U_F * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 3200B~5C", minAtk: 32000000, maxAtk: 500000000 },
    farm: { gain: 4800, cap: 250000000, capText: "2C 5000B", prob: 1.0 },
  },
  {
    name: "골든 베릴 노가다 [100회]",
    maxHp: 936 * U_F,
    goldReward: Math.round(936 * U_F * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 6500B~5C", minAtk: 65000000, maxAtk: 500000000 },
    farm: { gain: 24000, cap: 250000000, capText: "2C 5000B", prob: 1.0 },
  },

  // 31~35: 균열의 단편
  {
    name: "균열의 단편 노가다",
    maxHp: 3931 * U_F,
    goldReward: Math.round(3931 * U_F * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 1C~200C", minAtk: 100000000, maxAtk: 20000000000 },
    farm: {
      gain: 100,
      cap: 20000000000,
      capText: "200C",
      prob: 1.0,
      specialText: "※순수 공격력이 2C 5000B 이하면 상승치 50배 (5000 증가)",
      specialThreshold: 250000000,
      specialMult: 50,
    },
  },
  {
    name: "균열의 단편 노가다 [5회]",
    maxHp: 19655 * U_F,
    goldReward: Math.round(19655 * U_F * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 1C~200C", minAtk: 100000000, maxAtk: 20000000000 },
    farm: {
      gain: 500,
      cap: 20000000000,
      capText: "200C",
      prob: 1.0,
      specialText: "※순수 공격력이 2C 5000B 이하면 상승치 50배 (25000 증가)",
      specialThreshold: 250000000,
      specialMult: 50,
    },
  },
  {
    name: "균열의 단편 노가다 [20회]",
    maxHp: 78620 * U_F,
    goldReward: Math.round(78620 * U_F * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 1C~200C", minAtk: 100000000, maxAtk: 20000000000 },
    farm: { gain: 2000, cap: 20000000000, capText: "200C", prob: 1.0 },
  },
  {
    name: "균열의 단편 노가다 [100회]",
    maxHp: 39.31 * U_G,
    goldReward: Math.round(39.31 * U_G * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 1C~200C", minAtk: 100000000, maxAtk: 20000000000 },
    farm: { gain: 10000, cap: 20000000000, capText: "200C", prob: 1.0 },
  },
  {
    name: "균열의 단편 노가다 [500회]",
    maxHp: 196.55 * U_G,
    goldReward: Math.round(196.55 * U_G * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 5C~200C", minAtk: 500000000, maxAtk: 20000000000 },
    farm: { gain: 40000, cap: 20000000000, capText: "200C", prob: 1.0 },
  },

  // 36~40: 퀀텀 카지노
  {
    name: "퀀텀 카지노 노가다",
    maxHp: 600 * U_G,
    goldReward: Math.round(600 * U_G * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 50C~2000D", minAtk: 5000000000, maxAtk: 2000000000000000 },
    farm: {
      gain: 800,
      cap: 1000000000000,
      capText: "1D",
      prob: 1.0,
      specialText: "※순수 공격력이 40C 이하면 상승치 50배 (4B 증가)",
      specialThreshold: 4000000000,
      specialMult: 50,
    },
  },
  {
    name: "퀀텀 카지노 노가다 [5회]",
    maxHp: 3000 * U_G,
    goldReward: Math.round(3000 * U_G * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 50C~2000D", minAtk: 5000000000, maxAtk: 2000000000000000 },
    farm: {
      gain: 4000,
      cap: 1000000000000,
      capText: "1D",
      prob: 1.0,
      specialText: "※순수 공격력이 40C 이하면 상승치 50배 (20B 증가)",
      specialThreshold: 4000000000,
      specialMult: 50,
    },
  },
  {
    name: "퀀텀 카지노 노가다 [20회]",
    maxHp: 1.2 * U_H,
    goldReward: Math.round(1.2 * U_H * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 50C~2000D", minAtk: 5000000000, maxAtk: 2000000000000000 },
    farm: { gain: 16000, cap: 1000000000000, capText: "1D", prob: 1.0 },
  },
  {
    name: "퀀텀 카지노 노가다 [100회]",
    maxHp: 6 * U_H,
    goldReward: Math.round(6 * U_H * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 50C~2000D", minAtk: 5000000000, maxAtk: 2000000000000000 },
    farm: { gain: 80000, cap: 1000000000000, capText: "1D", prob: 1.0 },
  },
  {
    name: "퀀텀 카지노 노가다 [500회]",
    maxHp: 30 * U_H,
    goldReward: Math.round(30 * U_H * GOLD_RATIO_AFTER_ABYSS),
    req: { text: "순수공격력 500C~2000D", minAtk: 50000000000, maxAtk: 2000000000000000 },
    farm: { gain: 400000, cap: 1000000000000, capText: "0", prob: 1.0 },
  },
];

const zones = customZones.map((z, i) => ({
  level: i + 1,
  enemyName: "",
  img: `https://placehold.co/64x64/222/fff?text=Zone${i + 1}`,
  ...z,
}));
