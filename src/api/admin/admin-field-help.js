(function () {
  "use strict";

  const VERSION = "v196.admin-field-help-split";
  const LEGACY_SMOKE_VERSION_MARKERS = "v195.admin-thin-entry-cleanup v191.admin-edit-draft-split v165.admin-create-apply-limited";

  let configured = false;
  let escapeHtml = (value) => String(value === null || value === undefined ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
  let formatValue = (value) => {
    if (value === null || value === undefined || value === "") return "-";
    if (typeof value === "number") return Number.isFinite(value) ? value.toLocaleString("ko-KR") : String(value);
    if (typeof value === "boolean") return value ? "true" : "false";
    return String(value);
  };

  const ADMIN_EQUIP_SLOT_PRESET_LABELS = {
    skill_all: "일반장비 1 · 스킬피해+모든피해",
    atk_inc: "일반장비 2 · 공격력 추가",
    normal_dmg: "일반장비 3 · 평타피해",
    skill_chance: "일반장비 4/5 · 추가 스킬피해",
    normal_crit: "일반장비 4/5 · 평타 치명타",
    all_dmg: "예비 슬롯 · 모든피해",
    skill_dmg: "예비 슬롯 · 스킬피해",
    "6": "특수무기",
    "7": "특수목걸이",
    "8": "특수반지",
    "9": "무기아바타",
    "10": "오라아바타",
    "11": "클론 레어 아바타",
    "12": "탈리스만 A",
    "13": "탈리스만 B",
    "14": "휘장",
  };

  const ADMIN_FIELD_HELP_DEFINITIONS = {
    grade: {
      title: "grade / 등급 숫자",
      body: "현재 이 프로젝트의 itemTemplates.grade는 일반적인 normal/rare/epic 희귀도명이 아니라, 기존 JS 아이템의 tier 값을 옮겨 담은 숫자형 진행 등급입니다. 쉽게 말해 아이템이 어느 보스/장비 성장 구간에 속하는지 보는 값입니다.",
      example: "예: grade=1은 1티어/초반 구간, grade=12는 12티어/상위 구간처럼 해석합니다. 희귀도 이름이 필요하면 나중에 rarity 같은 별도 필드로 분리하는 편이 안전합니다.",
    },
    enhancegroupcode: {
      title: "enhance group code / 강화그룹 코드",
      body: "이 아이템이 어떤 강화 규칙 묶음을 사용할지 연결하는 코드입니다. 아이템의 enhance_group_code와 강화 그룹의 code가 같으면, 그 강화 그룹/강화 단계가 이 아이템에 적용됩니다.",
      example: "예: weapon_basic 아이템 → enhancementGroups.code=weapon_basic → enhancementLevels.group_code=weapon_basic 단계 적용",
    },
    groupcode: {
      title: "group code / 강화 단계 그룹 코드",
      body: "강화 단계가 어느 강화 그룹에 속하는지 나타내는 코드입니다. enhancementLevels의 group_code는 enhancementGroups의 code와 연결됩니다.",
      example: "같은 group_code를 가진 강화 단계들이 +0→+1, +1→+2 같은 단계 규칙 묶음이 됩니다.",
    },
    adminnote: {
      title: "admin note / 관리자 메모",
      body: "게임 플레이 화면에는 보여주지 않는 운영자용 메모입니다. 데이터 작업 이유, 주의사항, 임시 설명, 나중에 확인할 내용을 적어두는 내부 기록용 필드입니다.",
      example: "예: 밸런스 조정 예정, 이벤트 드랍 전용, 아직 미사용 데이터 등",
    },
    itemtype: {
      title: "item type / 아이템 분류",
      body: "아이템이 일반 장비인지, 스킬강화권인지, 특수 장비인지 같은 큰 분류를 정하는 값입니다. 드랍 목록, 겹치기 기본 판단, 향후 필터/정렬 기준에 영향을 줄 수 있습니다.",
      example: "예: normal=일반 장비, skill_book=스킬강화권, special_equip=특수 장비",
    },
    equipslot: {
      title: "equip slot / 장착 슬롯",
      body: "장비가 어떤 장착 그룹 또는 특수 슬롯에 들어가는지 나타내는 값입니다. 잘못 바꾸면 장착 위치나 장비 효과 분류가 어색해질 수 있으니 select 프리셋 안에서만 고르는 편이 안전합니다.",
      example: "예: skill_all=일반장비 1, atk_inc=일반장비 2, 6=특수무기, 12=탈리스만 A",
    },
    slotkey: {
      title: "slot key / 스킬 슬롯",
      body: "스킬이 Q/W/E/R/T/F/D/M 또는 각성 슬롯 중 어디에 배치되는지 나타내는 값입니다. 같은 슬롯이 중복되면 UI 배치가 헷갈릴 수 있으니 변경 후 게임 화면에서 꼭 확인해야 합니다.",
      example: "예: Q, W, E, R, T, F, D, M, SQ, SW 같은 슬롯 키",
    },
    skillcode: {
      title: "skill code / 스킬 연결 코드",
      body: "스킬 레벨 또는 캐릭터 스킬 연결이 어떤 skills.code를 바라볼지 정하는 관계 필드입니다. 실제 존재하는 스킬 목록에서만 선택할 수 있습니다.",
      example: "skillLevels에서는 skill_code + level 조합, characterSkills에서는 character_code + skill_code 조합이 중복되면 적용이 차단됩니다.",
    },
    level: {
      title: "level / 스킬 레벨",
      body: "스킬 강화 단계 숫자입니다. 같은 skill_code 안에서 같은 level이 이미 있으면 적용이 차단됩니다.",
      example: "예: q_skill + level 1은 하나만 존재해야 합니다.",
    },
    fromlevel: {
      title: "from level / 강화 시작 단계",
      body: "강화 단계 규칙의 시작 레벨입니다. 같은 group_code 안에서 같은 from_level이 이미 있으면 적용이 차단됩니다.",
      example: "예: weapon_basic +0→+1 규칙과 +1→+2 규칙처럼 시작 단계가 겹치면 안 됩니다.",
    },
    charactercode: {
      title: "character code / 캐릭터 연결 코드",
      body: "캐릭터 스킬 연결이 어떤 캐릭터에 속할지 정하는 관계 필드입니다. 실제 characters.code 목록에서만 선택할 수 있습니다.",
      example: "character_code + skill_code 조합이 이미 있으면 적용이 차단됩니다.",
    },
    droptablecode: {
      title: "drop table code / 드랍 테이블 연결 코드",
      body: "드랍 아이템이 어느 드랍 테이블에 속할지 정하는 관계 필드입니다. 실제 dropTables.code 목록에서만 선택할 수 있습니다.",
      example: "보스/필드 드랍 묶음 이동에 영향을 주므로 적용 후 관계 탭에서 연결을 확인하는 편이 안전합니다.",
    },
    bosstype: {
      title: "boss type / 보스 분류",
      body: "보스가 일반 보스인지 특수 보스인지 나누는 값입니다. 보스 목록 정렬, 소환/표시 그룹, 드랍 확인에 영향을 줄 수 있습니다.",
      example: "normal=일반 보스, special=특수 보스",
    },
    stackable: {
      title: "stackable / 겹치기 가능 여부",
      body: "인벤토리에서 같은 아이템을 한 칸에 수량으로 합칠 수 있는지 정하는 true/false 값입니다. true면 재료/강화권처럼 여러 개가 한 칸에 쌓이고, false면 장비처럼 각각 별도 칸을 차지합니다.",
      example: "예: 강화권/재료는 true, 무기/방어구/탈리스만처럼 개별 강화·옵션을 가진 장비는 보통 false가 안전합니다.",
    },
    sortorder: {
      title: "sort order / 정렬값",
      body: "화면이나 관리자 목록에서 어떤 순서로 보여줄지 정하는 숫자입니다. 보통 숫자가 작을수록 앞쪽에 배치합니다.",
      example: "예: 10, 20, 30처럼 간격을 두면 중간에 새 항목을 끼워 넣기 쉽습니다.",
    },
    isenabled: {
      title: "is enabled / 활성 상태",
      body: "이 마스터 데이터를 실제 게임 기준 데이터로 사용할지 여부입니다. false면 관리자에는 남아 있어도 게임 적용 대상에서 제외할 수 있습니다.",
      example: "테스트용/미사용 데이터는 false로 두는 식으로 활용합니다.",
    },
    id: {
      title: "id / 내부 숫자 ID",
      body: "DB row를 구분하는 내부 숫자입니다. 관리자가 직접 의미를 부여하기보다는 상세 조회, 변경 이력, relation 연결 확인용으로 봅니다.",
      example: "같은 도메인 안에서 id는 하나만 존재합니다.",
    },
    code: {
      title: "code / 연결 코드",
      body: "다른 마스터 데이터가 이 row를 찾을 때 쓰는 고유 문자열입니다. 이름보다 더 중요한 연결 기준이라 변경 시 relation과 드랍/스킬 연결을 함께 확인해야 합니다.",
      example: "dropTables.owner_code, itemTemplates.code, skills.code 같은 필드가 서로 연결됩니다.",
    },
    name: {
      title: "name / 표시 이름",
      body: "관리자와 게임 화면에서 사람이 읽는 이름입니다. code와 달리 표시용이지만, 드랍명/툴팁/목록 노출에 영향을 줄 수 있습니다.",
      example: "예: 초보자 스태프, 고블린 왕, 화염구",
    },
    description: {
      title: "description / 설명",
      body: "관리자 또는 게임 화면 설명으로 쓰는 문장입니다. 긴 안내문은 UI가 길어질 수 있으니 핵심만 유지하는 편이 좋습니다.",
      example: "보스/필드/스킬 설명에 사용합니다.",
    },
    tier: {
      title: "tier / 진행 티어",
      body: "보스나 아이템이 어느 진행 구간에 속하는지 나타내는 숫자입니다. 난이도와 보상 단계 조정 기준으로 봅니다.",
      example: "tier 1=초반, tier 10+=상위 구간",
    },
    hp: {
      title: "hp / 보스 체력",
      body: "보스의 체력 기준값입니다. 쿨타임, 드랍률, 보상과 함께 조정해야 체감 난이도가 안정적입니다.",
      example: "bosses.hp",
    },
    enemyhp: {
      title: "enemy hp / 필드 몬스터 체력",
      body: "필드 사냥 대상의 체력 기준값입니다. 골드 보상과 함께 성장 속도에 직접 영향을 줍니다.",
      example: "fieldZones.enemy_hp",
    },
    goldreward: {
      title: "gold reward / 골드 보상",
      body: "필드나 전투에서 얻는 골드 기준값입니다. 체력 대비 보상이 너무 높으면 성장 속도가 급격히 빨라질 수 있습니다.",
      example: "fieldZones.gold_reward",
    },
    procrate: {
      title: "proc rate / 발동 확률",
      body: "스킬이나 효과가 발동할 기본 확률입니다. 장비/스킬레벨 보너스와 합산되어 최종 발동률 표시로 이어질 수 있습니다.",
      example: "0.15라면 15% 계열 값으로 해석합니다.",
    },
    procratebonus: {
      title: "proc rate bonus / 발동 확률 추가값",
      body: "스킬 레벨이나 장비가 기본 발동률에 더해주는 추가 확률입니다. 최종 발동률 계산에 포함됩니다.",
      example: "기본 발동률 + 추가 발동률 형태로 표시할 때 사용합니다.",
    },
    cooldownseconds: {
      title: "cooldown seconds / 쿨타임 초",
      body: "스킬 사용 또는 보스 재등장에 필요한 대기 시간입니다. 단위는 초입니다.",
      example: "30이면 30초입니다.",
    },
    damagemultiplier: {
      title: "damage multiplier / 피해 배율",
      body: "스킬 레벨별 피해 배율입니다. 값이 커질수록 전투 밸런스에 직접 영향을 줍니다.",
      example: "1.25는 125% 계열 배율로 봅니다.",
    },
    isdefault: {
      title: "is default / 기본 장착 여부",
      body: "캐릭터가 해당 스킬을 기본으로 가지고 시작하는지 나타냅니다.",
      example: "characterSkills.is_default",
    },
    ownertype: {
      title: "owner type / 드랍 소유자 종류",
      body: "드랍 테이블이 보스 소유인지 필드 소유인지 구분합니다. owner_code가 어느 도메인의 code를 바라볼지 결정합니다.",
      example: "boss=보스 드랍, field=필드 드랍",
    },
    ownercode: {
      title: "owner code / 드랍 소유자 코드",
      body: "owner_type에 따라 bosses.code 또는 fieldZones.code를 바라보는 연결 코드입니다.",
      example: "owner_type=boss이면 boss code, field이면 field zone code",
    },
    itemtemplatecode: {
      title: "item template code / 드랍 아이템 코드",
      body: "드랍 테이블에서 실제로 떨어질 itemTemplates.code를 연결합니다.",
      example: "dropTableItems.item_template_code",
    },
    rate: {
      title: "rate / 드랍 또는 성공 확률",
      body: "확률 계열 숫자입니다. 도메인에 따라 드랍 확률이나 성공 확률로 쓰입니다.",
      example: "dropTableItems.rate, enhancementLevels.success_rate",
    },
    minquantity: {
      title: "min quantity / 최소 수량",
      body: "드랍 성공 시 최소로 지급되는 수량입니다. max_quantity보다 클 수 없습니다.",
      example: "강화권 1~3개 드랍이면 min=1",
    },
    maxquantity: {
      title: "max quantity / 최대 수량",
      body: "드랍 성공 시 최대로 지급되는 수량입니다. min_quantity와 함께 보상량을 결정합니다.",
      example: "강화권 1~3개 드랍이면 max=3",
    },
    maxlevel: {
      title: "max level / 최대 강화 단계",
      body: "강화 그룹에서 허용하는 최대 강화 단계입니다. enhancementLevels 규칙과 맞아야 합니다.",
      example: "max_level=10이면 +10까지 설계된 강화 그룹입니다.",
    },
    tolevel: {
      title: "to level / 강화 도착 단계",
      body: "강화 성공 시 도착하는 레벨입니다. from_level과 함께 +0→+1 같은 규칙을 만듭니다.",
      example: "from_level=0, to_level=1",
    },
    successrate: {
      title: "success rate / 강화 성공 확률",
      body: "강화 단계별 성공 확률입니다. 비용/재료/실패 규칙과 함께 조정해야 합니다.",
      example: "0.8이면 80% 계열 값으로 봅니다.",
    },
    goldcost: {
      title: "gold cost / 강화 비용",
      body: "강화를 시도할 때 필요한 골드입니다. 성공률과 함께 체감 난이도를 만듭니다.",
      example: "enhancementLevels.gold_cost",
    },
    updatedat: {
      title: "updated at / 수정 시각",
      body: "row가 마지막으로 바뀐 시각입니다. 카탈로그 목록에서는 일자까지만 짧게 보여주고, 값 옆 ? 도움말에서 초 단위 상세 시각을 확인합니다. stale guard나 변경 이력 확인 시 참고합니다.",
      example: "예: 목록 2026-07-06, ? tooltip 2026-07-06 13:24:51 UTC",

    },
    jsonkeys: {
      title: "json keys / JSON 요약 키",
      body: "원본 JSON 전체를 목록에 노출하지 않고 어떤 JSON 묶음이 있는지만 보여주는 안전 요약입니다. 카탈로그 목록에서는 앞 3개 키와 남은 개수만 짧게 표시하고, ? 도움말에서 전체 키를 확인합니다.",
      example: "baseStats, options, rules, conditions처럼 긴 키 목록은 칩 3개 + 외 N개로 축약합니다.",
    },
    basestats: {
      title: "base stats / 기본 능력치 JSON",
      body: "아이템의 기본 능력치 묶음입니다. 긴 JSON은 목록에서 숨기고 상세 미리보기에서만 축약 표시합니다.",
      example: "공격력, 모든피해, 스킬피해 같은 기본 옵션",
    },
    options: {
      title: "options / 추가 옵션 JSON",
      body: "아이템/스킬의 추가 동작이나 특수 옵션을 담는 JSON 묶음입니다. 직접 수정 전 Preview Diff를 반드시 확인합니다.",
      example: "스킬 발동률 증가, 특수 효과, 조건부 옵션 등",
    },
  };

  function configure(deps) {
    const d = deps || {};
    if (typeof d.escapeHtml === "function") escapeHtml = d.escapeHtml;
    if (typeof d.formatValue === "function") formatValue = d.formatValue;
    configured = true;
    return getReadiness({ log: false });
  }

  function normalizeAdminFieldKey(key) {
    return String(key || "").replace(/[^a-zA-Z0-9]/g, "").toLowerCase();
  }

  function getAdminFieldHelp(key) {
    const normalized = normalizeAdminFieldKey(key);
    return ADMIN_FIELD_HELP_DEFINITIONS[normalized] || null;
  }

  function listAdminFieldHelp() {
    return Object.entries(ADMIN_FIELD_HELP_DEFINITIONS).map(([key, help]) => ({ key, ...help }));
  }

  function renderFieldHelpBadge(key) {
    const help = getAdminFieldHelp(key);
    if (!help) return "";
    const titleText = `${help.title}\n${help.body}\n${help.example || ""}`;
    return ` <span class="field-help-badge" title="${escapeHtml(titleText)}">?</span>`;
  }

  function renderFieldHelpInline(key) {
    const help = getAdminFieldHelp(key);
    if (!help) return "";
    return `<div class="field-help-inline"><strong>${escapeHtml(help.title)}</strong> — ${escapeHtml(help.body)}${help.example ? `<br><span>${escapeHtml(help.example)}</span>` : ""}</div>`;
  }

  function getAdminEquipSlotDisplayName(value) {
    const key = value === null || value === undefined ? "" : String(value);
    return ADMIN_EQUIP_SLOT_PRESET_LABELS[key] || key || "장착 슬롯 없음";
  }

  function getAdminFieldValueHint(key, value) {
    const normalized = normalizeAdminFieldKey(key);
    if (normalized === "grade") {
      if (value === null || value === undefined || value === "") {
        return { label: "grade 없음", body: "이 항목은 아직 진행 티어/등급 숫자가 비어 있습니다." };
      }
      const numeric = Number(value);
      if (Number.isFinite(numeric)) {
        return {
          label: `tier ${numeric}`,
          body: `현재 값 ${numeric}은 희귀도명이 아니라 원본 아이템 tier ${numeric}입니다. 아이템/보스 성장 구간, 드랍 단계, 장비 진행도를 맞출 때 참고하는 숫자입니다.`,
        };
      }
      return {
        label: "text grade",
        body: "숫자가 아닌 grade 값입니다. 현재 DB seed 기준에서는 대부분 tier 숫자가 들어가므로, 이 값은 별도로 확인하는 편이 안전합니다.",
      };
    }
    if (normalized === "enhancegroupcode") {
      if (!value) return { label: "강화그룹 미연결", body: "이 항목은 아직 강화 규칙 묶음에 연결되어 있지 않습니다." };
      if (String(value) === "normal_equipment") return { label: "일반 장비 강화", body: "일반/심연/특수/avatar 계열 장비가 공유하는 기본 강화 규칙 묶음입니다." };
      if (String(value) === "talisman_emblem") return { label: "탈리스만/휘장 강화", body: "탈리스만과 빛나는 휘장처럼 같은 강화 방식을 쓰는 장비 묶음입니다." };
      return { label: String(value), body: `강화그룹 코드 ${value}와 같은 code/group_code를 가진 enhancementGroups/enhancementLevels가 연결됩니다.` };
    }
    if (normalized === "itemtype") {
      const text = String(value || "");
      if (text === "normal") return { label: "normal · 일반 장비", body: "일반 장비 분류입니다. 보통 개별 장비라 stackable=false가 안전합니다." };
      if (text === "skill_book") return { label: "skill_book · 스킬강화권", body: "스킬 강화권 분류입니다. 보통 수량 겹치기 대상입니다." };
      if (text === "special_equip") return { label: "special_equip · 특수 장비", body: "특수 슬롯 장비 분류입니다. 장착 슬롯 값과 함께 확인해야 합니다." };
      return text ? { label: text, body: "프리셋에 있는 아이템 분류 값입니다. 변경 후 드랍/인벤토리 표시를 확인하세요." } : { label: "분류 없음", body: "아이템 분류가 비어 있습니다." };
    }
    if (normalized === "equipslot") {
      const text = String(value || "");
      if (!text) return { label: "장착 슬롯 없음", body: "재료/강화권처럼 장착하지 않는 아이템에 어울립니다." };
      const displayName = getAdminEquipSlotDisplayName(text);
      if (/^\d+$/.test(text)) return { label: `${text} · ${displayName}`, body: "인게임 장비창 오른쪽 특수 장비 슬롯 이름입니다." };
      return { label: `${text} · ${displayName}`, body: "일반 장비 장착/효과 그룹입니다. 변경 후 장착 위치와 툴팁을 확인하세요." };
    }
    if (normalized === "slotkey") {
      const text = String(value || "");
      return text ? { label: `${text} 슬롯`, body: "스킬 버튼/각성 슬롯 배치에 영향을 줄 수 있습니다. 중복 슬롯이 생기지 않게 확인하세요." } : { label: "슬롯 없음", body: "스킬 슬롯이 비어 있습니다." };
    }
    if (normalized === "bosstype") {
      const text = String(value || "");
      if (text === "special") return { label: "special · 특수 보스", body: "특수 보스 그룹으로 표시/정렬될 수 있습니다." };
      if (text === "normal") return { label: "normal · 일반 보스", body: "일반 보스 그룹으로 표시/정렬됩니다." };
      return text ? { label: text, body: "보스 분류 값입니다. normal/special 프리셋 사용을 권장합니다." } : { label: "보스 분류 없음", body: "보스 분류가 비어 있습니다." };
    }
    if (normalized === "stackable") {
      const boolValue = value === true || String(value).toLowerCase() === "true";
      return boolValue
        ? { label: "true · 겹치기 가능", body: "같은 아이템을 인벤토리 한 칸에 수량으로 합칠 수 있습니다. 재료/강화권 계열에 적합합니다." }
        : { label: "false · 개별 칸 사용", body: "같은 이름이어도 각각 별도 칸을 차지합니다. 강화 수치/옵션/장착 상태가 따로 필요한 장비에 적합합니다." };
    }
    if (normalized === "adminnote") {
      return value ? { label: "관리자 메모 있음", body: "게임 화면에는 표시되지 않는 내부 메모가 들어 있습니다." } : { label: "관리자 메모 없음", body: "운영/밸런스 메모가 아직 비어 있습니다." };
    }
    return null;
  }

  function renderFieldValueHintInline(key, value) {
    const hint = getAdminFieldValueHint(key, value);
    if (!hint) return "";
    const titleText = `${hint.label}
${hint.body || ""}`;
    return `<div class="field-value-hint compact" title="${escapeHtml(titleText)}"><strong>${escapeHtml(hint.label)}</strong>${renderFieldHelpBadge(key)}</div>`;
  }

  function formatValueWithFieldHint(key, value) {
    return `${escapeHtml(formatValue(value))}${renderFieldValueHintInline(key, value)}`;
  }

  function getReadiness(options) {
    const fieldKeys = Object.keys(ADMIN_FIELD_HELP_DEFINITIONS);
    const equipSlotKeys = Object.keys(ADMIN_EQUIP_SLOT_PRESET_LABELS);
    const ok = fieldKeys.length >= 10 && equipSlotKeys.includes("6") && equipSlotKeys.includes("14") && typeof renderFieldHelpBadge === "function" && typeof getAdminFieldValueHint === "function";
    const result = {
      ok,
      version: VERSION,
      configured,
      fieldHelpCount: fieldKeys.length,
      equipSlotLabelCount: equipSlotKeys.length,
      hasGradeHelp: !!getAdminFieldHelp("grade"),
      hasAdminNoteHelp: !!getAdminFieldHelp("admin_note"),
      hasGradeHint: !!getAdminFieldValueHint("grade", 1),
      hasEquipSlotHint: !!getAdminFieldValueHint("equip_slot", "14"),
      hasSpecialWeaponLabel: getAdminEquipSlotDisplayName("6") === "특수무기",
      hasEmblemLabel: getAdminEquipSlotDisplayName("14") === "휘장",
      exportedFunctions: [
        "normalizeAdminFieldKey",
        "getAdminFieldHelp",
        "listAdminFieldHelp",
        "renderFieldHelpBadge",
        "renderFieldHelpInline",
        "getAdminFieldValueHint",
        "renderFieldValueHintInline",
        "formatValueWithFieldHint",
        "getAdminEquipSlotDisplayName",
      ],
    };
    if (!options || options.log !== false) console.log("[Upgrade RPG] admin field help check", result);
    return result;
  }

  window.RpgAdminFieldHelp = {
    VERSION,
    configure,
    getReadiness,
    normalizeAdminFieldKey,
    getAdminFieldHelp,
    listAdminFieldHelp,
    renderFieldHelpBadge,
    renderFieldHelpInline,
    getAdminFieldValueHint,
    renderFieldValueHintInline,
    formatValueWithFieldHint,
    getAdminEquipSlotDisplayName,
  };
})();
