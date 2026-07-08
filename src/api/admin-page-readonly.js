(function () {
  "use strict";

  const VERSION = "v174.admin-collapsed-panel-style-fix";
  const LEGACY_SMOKE_VERSION_MARKERS = "v113.admin-readonly-overview-url-helper v165.admin-create-apply-limited v171.admin-create-delete-restore v172.admin-layout-navigation-shell v173.admin-layout-collapse-polish";
  const DEFAULT_TIMEOUT_MS = 3500;
  const DEFAULT_SNAPSHOT_LIMIT = 30;
  const DEFAULT_SNAPSHOT_SORT = "updated_desc";
  const DEFAULT_MASTER_DOMAIN = "itemTemplates";
  const DEFAULT_MASTER_LIMIT = 20;
  const DEFAULT_MASTER_SORT = "id_asc";
  const DEFAULT_CHANGE_LOG_LIMIT = 20;
  const DEFAULT_CHANGE_LOG_SORT = "created_desc";
  const ADMIN_EDIT_APPLY_CONFIRM_TEXT = "APPLY MASTER DATA EDIT";
  const ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT = "HIGH RISK EDIT";
  const ADMIN_ROLLBACK_CONFIRM_TEXT = "ROLLBACK MASTER DATA EDIT";
  const ADMIN_CREATE_APPLY_CONFIRM_TEXT = "CREATE MASTER DATA ROW";
  const ADMIN_CREATE_DELETE_CONFIRM_TEXT = "DELETE CREATED MASTER DATA ROW";
  const ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT = "RESTORE DELETED CREATED ROW";
  const ADMIN_EDIT_APPLY_TIMEOUT_MS = 5000;
  const ADMIN_WRITE_DEV_KEY_EXAMPLE = "local-admin-dev-key";
  const ADMIN_LAYOUT_COLLAPSE_STORAGE_KEY = "upgradeRpgAdminCollapsedSectionsV2";
  const ADMIN_DEFAULT_COLLAPSED_SECTION_KEYS = ["field-help", "create-blueprint", "change-logs"];

  const ADMIN_EDIT_ALLOWED_FIELDS = {
    itemTemplates: ["name", "item_type", "grade", "description", "stackable", "equip_slot", "enhance_group_code", "admin_note"],
    skills: ["slot_key", "name", "description", "proc_rate", "cooldown_seconds"],
    skillLevels: ["skill_code", "level", "damage_multiplier", "proc_rate_bonus"],
    bosses: ["name", "tier", "boss_type", "hp", "description", "cooldown_seconds", "is_enabled"],
    fieldZones: ["name", "sort_order", "enemy_hp", "gold_reward", "description", "is_enabled"],
    characters: ["name", "description", "is_enabled"],
    dropTables: ["owner_type", "owner_code", "description", "is_enabled"],
    dropTableItems: ["drop_table_code", "item_template_code", "rate", "min_quantity", "max_quantity"],
    enhancementGroups: ["name", "description", "max_level", "is_enabled"],
    enhancementLevels: ["group_code", "from_level", "to_level", "success_rate", "gold_cost"],
    characterSkills: ["character_code", "skill_code", "sort_order", "is_default"],
  };
  const ADMIN_DRAFT_BOOLEAN_FIELDS = new Set(["stackable", "is_enabled", "is_default"]);
  const ADMIN_DRAFT_NUMBER_FIELDS = new Set([
    "grade",
    "proc_rate",
    "cooldown_seconds",
    "level",
    "damage_multiplier",
    "proc_rate_bonus",
    "tier",
    "hp",
    "sort_order",
    "enemy_hp",
    "gold_reward",
    "rate",
    "min_quantity",
    "max_quantity",
    "max_level",
    "from_level",
    "to_level",
    "success_rate",
    "gold_cost",
  ]);
  const ADMIN_DRAFT_TEXTAREA_FIELDS = new Set(["description", "admin_note"]);
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
  const ADMIN_DRAFT_SELECT_FIELD_OPTIONS = {
    item_type: [
      { value: "normal", label: "normal · 일반 장비" },
      { value: "skill_book", label: "skill_book · 스킬강화권" },
      { value: "special_equip", label: "special_equip · 특수 장비" },
      { value: "abyss", label: "abyss · 심연 장비" },
      { value: "avatar", label: "avatar · 아바타" },
      { value: "material", label: "material · 재료" },
      { value: "consumable", label: "consumable · 소모품" },
      { value: "unknown", label: "unknown · 미분류" },
    ],
    equip_slot: [
      { value: "", label: "없음 · 장착 슬롯 없음" },
      { value: "skill_all", label: "skill_all · 일반장비 1 · 스킬피해+모든피해" },
      { value: "atk_inc", label: "atk_inc · 일반장비 2 · 공격력 추가" },
      { value: "normal_dmg", label: "normal_dmg · 일반장비 3 · 평타피해" },
      { value: "skill_chance", label: "skill_chance · 일반장비 4/5 · 추가 스킬피해" },
      { value: "normal_crit", label: "normal_crit · 일반장비 4/5 · 평타 치명타" },
      { value: "skill_dmg", label: "skill_dmg · 예비 슬롯 · 스킬피해" },
      { value: "all_dmg", label: "all_dmg · 예비 슬롯 · 모든피해" },
      { value: "6", label: "6 · 특수무기" },
      { value: "7", label: "7 · 특수목걸이" },
      { value: "8", label: "8 · 특수반지" },
      { value: "9", label: "9 · 무기아바타" },
      { value: "10", label: "10 · 오라아바타" },
      { value: "11", label: "11 · 클론 레어 아바타" },
      { value: "12", label: "12 · 탈리스만 A" },
      { value: "13", label: "13 · 탈리스만 B" },
      { value: "14", label: "14 · 휘장" },
    ],
    boss_type: [
      { value: "normal", label: "normal · 일반 보스" },
      { value: "special", label: "special · 특수 보스" },
    ],
    owner_type: [
      { value: "boss", label: "boss · 보스 드랍 테이블" },
      { value: "field", label: "field · 필드 드랍 테이블" },
    ],
    slot_key: [
      { value: "Q", label: "Q · 기본 1번 스킬" },
      { value: "W", label: "W · 기본 2번 스킬" },
      { value: "E", label: "E · 기본 3번 스킬" },
      { value: "R", label: "R · 기본 4번 스킬" },
      { value: "T", label: "T · 기본 5번 스킬" },
      { value: "F", label: "F · 기본 6번 스킬" },
      { value: "D", label: "D · 기본 7번 스킬" },
      { value: "M", label: "M · 기본 8번 스킬" },
      { value: "SQ", label: "SQ · Q 각성 스킬" },
      { value: "SW", label: "SW · W 각성 스킬" },
      { value: "SE", label: "SE · E 각성 스킬" },
      { value: "SR", label: "SR · R 각성 스킬" },
      { value: "ST", label: "ST · T 각성 스킬" },
      { value: "SF", label: "SF · F 각성 스킬" },
      { value: "SD", label: "SD · D 각성 스킬" },
      { value: "SM", label: "SM · M 각성 스킬" },
    ],
  };
  const ADMIN_DRAFT_VISIBLE_LOCKED_LIMIT = 18;

  let currentMasterDetailPayload = null;
  let currentAdminChangeLogDetailPayload = null;
  let currentAdminCreateBlueprintPayload = null;

  const ADMIN_TO_MASTER_API_FIELD_MAP = {
    itemTemplates: {
      code: "code",
      name: "name",
      item_type: "itemType",
      grade: "grade",
      description: "description",
      stackable: "stackable",
      equip_slot: "equipSlot",
      enhance_group_code: "enhanceGroupCode",
      admin_note: "adminNote",
    },
    skills: {
      code: "code",
      name: "name",
      slot_key: "slotKey",
      description: "description",
      proc_rate: "procRate",
      cooldown_seconds: "cooldownSeconds",
    },
    skillLevels: {
      skill_code: "skillCode",
      level: "level",
      damage_multiplier: "damageMultiplier",
      proc_rate_bonus: "procRateBonus",
    },
    bosses: {
      code: "code",
      name: "name",
      tier: "tier",
      boss_type: "bossType",
      hp: "hp",
      description: "description",
      cooldown_seconds: "cooldownSeconds",
      is_enabled: "isEnabled",
    },
    fieldZones: {
      code: "code",
      name: "name",
      sort_order: "sortOrder",
      enemy_hp: "enemyHp",
      gold_reward: "goldReward",
      description: "description",
      is_enabled: "isEnabled",
    },
    characters: {
      code: "code",
      name: "name",
      description: "description",
      is_enabled: "isEnabled",
    },
    dropTables: {
      code: "code",
      owner_type: "ownerType",
      owner_code: "ownerCode",
      description: "description",
      is_enabled: "isEnabled",
    },
    dropTableItems: {
      id: "id",
      drop_table_code: "dropTableCode",
      item_template_code: "itemTemplateCode",
      rate: "rate",
      min_quantity: "minQuantity",
      max_quantity: "maxQuantity",
    },
    enhancementGroups: {
      code: "code",
      name: "name",
      description: "description",
      max_level: "maxLevel",
      is_enabled: "isEnabled",
    },
    enhancementLevels: {
      group_code: "groupCode",
      from_level: "fromLevel",
      to_level: "toLevel",
      success_rate: "successRate",
      gold_cost: "goldCost",
    },
    characterSkills: {
      character_code: "characterCode",
      skill_code: "skillCode",
      sort_order: "sortOrder",
      is_default: "isDefault",
    },
  };


  function $(selector) {
    return document.querySelector(selector);
  }

  function escapeHtml(value) {
    return String(value === null || value === undefined ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function formatValue(value) {
    if (value === null || value === undefined || value === "") return "-";
    if (typeof value === "number") return Number.isFinite(value) ? value.toLocaleString("ko-KR") : String(value);
    if (typeof value === "boolean") return value ? "true" : "false";
    return String(value);
  }

  function formatClock(value) {
    if (!value) return "-";
    try {
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return String(value);
      return date.toLocaleString("ko-KR", { hour12: false });
    } catch (error) {
      return String(value);
    }
  }


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
  };

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
    return `<div class="field-value-hint"><strong>${escapeHtml(hint.label)}</strong> — ${escapeHtml(hint.body)}</div>`;
  }

  function formatValueWithFieldHint(key, value) {
    return `${escapeHtml(formatValue(value))}${renderFieldValueHintInline(key, value)}`;
  }

  function setStatus(message, kind) {
    const el = $("[data-admin-status]");
    if (!el) return;
    el.textContent = message;
    el.dataset.kind = kind || "info";
  }

  function getApiInput() {
    return $("[data-admin-api-base-url]");
  }

  function buildSiblingPageUrl(fileName) {
    try {
      return new URL(fileName, window.location.href).toString();
    } catch (error) {
      return String(fileName || "");
    }
  }

  function getCurrentAdminPageUrl() {
    try {
      return window.location.href;
    } catch (error) {
      return "admin.html";
    }
  }

  function getGamePageUrl() {
    return buildSiblingPageUrl("index.html");
  }

  function syncLocationHints() {
    const currentUrl = getCurrentAdminPageUrl();
    const currentTarget = $("[data-admin-current-url]");
    const gameLink = $("[data-admin-game-url]");
    if (currentTarget) currentTarget.textContent = currentUrl;
    if (gameLink) gameLink.href = getGamePageUrl();
  }

  async function copyCurrentAdminPageUrl() {
    const url = getCurrentAdminPageUrl();
    try {
      if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
        await navigator.clipboard.writeText(url);
        setStatus(`관리자 페이지 주소 복사됨: ${url}`, "ok");
        return { ok: true, url, copied: true, method: "clipboard" };
      }
    } catch (error) {
      // clipboard 권한이 막힌 브라우저에서는 아래 fallback을 사용합니다.
    }

    try {
      const input = document.createElement("input");
      input.value = url;
      input.setAttribute("readonly", "readonly");
      input.style.position = "fixed";
      input.style.opacity = "0";
      document.body.appendChild(input);
      input.select();
      document.execCommand("copy");
      document.body.removeChild(input);
      setStatus(`관리자 페이지 주소 복사됨: ${url}`, "ok");
      return { ok: true, url, copied: true, method: "fallback" };
    } catch (error) {
      setStatus(`주소 복사 실패: ${url}`, "error");
      return { ok: false, url, copied: false, error: error && error.message ? error.message : String(error) };
    }
  }

  function syncApiInput() {
    const input = getApiInput();
    if (!input || !window.RpgGameApi) return;
    input.value = window.RpgGameApi.getApiBaseUrl();
  }

  function getAdminWriteKeyInput() {
    return $(`[data-admin-write-dev-key]`);
  }

  function hasAdminWriteDevKey() {
    return !!(window.RpgGameApi && window.RpgGameApi.hasAdminWriteDevKey && window.RpgGameApi.hasAdminWriteDevKey());
  }

  function renderAdminWriteKeyStatus() {
    const target = $(`[data-admin-write-key-status]`);
    if (!target || !window.RpgGameApi) return;
    const ready = hasAdminWriteDevKey();
    target.innerHTML = ready
      ? `<span class="pill good">write key set</span>`
      : `<span class="pill blocked">write key missing</span>`;
  }

  function syncAdminWriteDevKeyInput() {
    const input = getAdminWriteKeyInput();
    if (input && window.RpgGameApi && window.RpgGameApi.getAdminWriteDevKey) input.value = window.RpgGameApi.getAdminWriteDevKey();
    renderAdminWriteKeyStatus();
  }

  function saveAdminWriteDevKeyFromInput() {
    ensureApi();
    const input = getAdminWriteKeyInput();
    const value = input ? input.value.trim() : "";
    if (!value) {
      const error = new Error(`관리자 쓰기 dev key를 입력해 주세요. 로컬 기본 예시는 ${ADMIN_WRITE_DEV_KEY_EXAMPLE} 입니다.`);
      setStatus(error.message, "error");
      renderAdminWriteKeyStatus();
      throw error;
    }
    window.RpgGameApi.setAdminWriteDevKey(value);
    syncAdminWriteDevKeyInput();
    setStatus("관리자 쓰기 dev key가 이 브라우저 탭에 저장됐습니다.", "ok");
    return value;
  }

  function clearAdminWriteDevKey() {
    ensureApi();
    window.RpgGameApi.clearAdminWriteDevKey();
    syncAdminWriteDevKeyInput();
    setStatus("관리자 쓰기 dev key를 지웠습니다. 실제 적용/되돌리기는 다시 잠깁니다.", "info");
    return "";
  }

  function requireAdminWriteDevKeyForUi(actionLabel) {
    if (hasAdminWriteDevKey()) return true;
    const message = `${actionLabel || "관리자 쓰기 작업"} 전에 관리자 쓰기 dev key를 먼저 설정해 주세요.`;
    setStatus(message, "error");
    const target = $(`[data-admin-edit-draft-result]`) || $(`[data-admin-rollback-result]`);
    if (target) target.innerHTML = `<div class="error">${escapeHtml(message)}<br>관리자 페이지의 <strong>쓰기 잠금</strong> 영역에서 dev key를 저장한 뒤 다시 시도하세요.</div>`;
    throw new Error(message);
  }

  function ensureApi() {
    if (!window.RpgGameApi) throw new Error("RpgGameApi를 찾을 수 없습니다. game-api-client.js 로딩 순서를 확인하세요.");
    if (typeof window.RpgGameApi.fetchAdminOverview !== "function") throw new Error("fetchAdminOverview 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.listAdminSaveSnapshots !== "function") throw new Error("listAdminSaveSnapshots 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.listAdminMasterCatalogDomains !== "function") throw new Error("listAdminMasterCatalogDomains 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.listAdminMasterCatalogRows !== "function") throw new Error("listAdminMasterCatalogRows 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.fetchAdminMasterCreateBlueprint !== "function") throw new Error("fetchAdminMasterCreateBlueprint 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.fetchAdminMasterDataDetail !== "function") throw new Error("fetchAdminMasterDataDetail 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.fetchAdminMasterDataRelations !== "function") throw new Error("fetchAdminMasterDataRelations 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.applyAdminMasterDataEdit !== "function") throw new Error("applyAdminMasterDataEdit 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.listAdminChangeLogs !== "function") throw new Error("listAdminChangeLogs 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.fetchAdminChangeLogDetail !== "function") throw new Error("fetchAdminChangeLogDetail 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.previewAdminChangeLogRollback !== "function") throw new Error("previewAdminChangeLogRollback 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.applyAdminChangeLogRollback !== "function") throw new Error("applyAdminChangeLogRollback 함수를 찾을 수 없습니다.");
    if (typeof window.RpgGameApi.fetchMasterData !== "function") throw new Error("fetchMasterData 함수를 찾을 수 없습니다.");
  }

  function readSnapshotFiltersFromDom() {
    const limitEl = $("[data-admin-filter-limit]");
    const userIdEl = $("[data-admin-filter-user-id]");
    const slotKeyEl = $("[data-admin-filter-slot-key]");
    const sourceEl = $("[data-admin-filter-source]");
    const defaultOnlyEl = $("[data-admin-filter-default-only]");
    const sortEl = $("[data-admin-filter-sort]");
    const userId = userIdEl && userIdEl.value.trim() ? Number(userIdEl.value.trim()) : undefined;
    return {
      limit: limitEl && limitEl.value ? Number(limitEl.value) : DEFAULT_SNAPSHOT_LIMIT,
      userId: Number.isFinite(userId) ? userId : undefined,
      slotKey: slotKeyEl ? slotKeyEl.value.trim() : "",
      source: sourceEl ? sourceEl.value.trim() : "",
      defaultOnly: !!(defaultOnlyEl && defaultOnlyEl.checked),
      sort: sortEl && sortEl.value ? sortEl.value : DEFAULT_SNAPSHOT_SORT,
    };
  }

  function resetSnapshotFilters(options) {
    const opts = options || {};
    const limitEl = $("[data-admin-filter-limit]");
    const userIdEl = $("[data-admin-filter-user-id]");
    const slotKeyEl = $("[data-admin-filter-slot-key]");
    const sourceEl = $("[data-admin-filter-source]");
    const defaultOnlyEl = $("[data-admin-filter-default-only]");
    const sortEl = $("[data-admin-filter-sort]");
    if (limitEl) limitEl.value = String(DEFAULT_SNAPSHOT_LIMIT);
    if (userIdEl) userIdEl.value = "";
    if (slotKeyEl) slotKeyEl.value = "";
    if (sourceEl) sourceEl.value = "";
    if (defaultOnlyEl) defaultOnlyEl.checked = false;
    if (sortEl) sortEl.value = DEFAULT_SNAPSHOT_SORT;
    if (!opts.silent) setStatus("세이브 스냅샷 필터 초기화", "info");
    return readSnapshotFiltersFromDom();
  }

  function describeSnapshotFilters(filters) {
    const f = filters || {};
    const parts = [];
    if (f.userId) parts.push(`userId=${f.userId}`);
    if (f.slotKey) parts.push(`slotKey=${f.slotKey}`);
    if (f.source) parts.push(`source=${f.source}`);
    if (f.defaultOnly) parts.push("defaultOnly=true");
    if (f.sort && f.sort !== DEFAULT_SNAPSHOT_SORT) parts.push(`sort=${f.sort}`);
    return parts.length ? parts.join(", ") : "필터 없음";
  }


  function readChangeLogFiltersFromDom() {
    const limitEl = $("[data-admin-change-log-filter-limit]");
    const targetTypeEl = $("[data-admin-change-log-filter-target-type]");
    const targetIdEl = $("[data-admin-change-log-filter-target-id]");
    const actionEl = $("[data-admin-change-log-filter-action]");
    const changedKeyEl = $("[data-admin-change-log-filter-changed-key]");
    const appliedEl = $("[data-admin-change-log-filter-applied]");
    const sortEl = $("[data-admin-change-log-filter-sort]");
    const appliedValue = appliedEl && appliedEl.value ? appliedEl.value : "all";
    return {
      limit: limitEl && limitEl.value ? Number(limitEl.value) : DEFAULT_CHANGE_LOG_LIMIT,
      targetType: targetTypeEl ? targetTypeEl.value.trim() : "",
      targetId: targetIdEl ? targetIdEl.value.trim() : "",
      action: actionEl ? actionEl.value.trim() : "",
      changedKey: changedKeyEl ? changedKeyEl.value.trim() : "",
      applied: appliedValue === "all" ? undefined : appliedValue === "true",
      sort: sortEl && sortEl.value ? sortEl.value : DEFAULT_CHANGE_LOG_SORT,
    };
  }

  function resetChangeLogFilters(options) {
    const opts = options || {};
    const limitEl = $("[data-admin-change-log-filter-limit]");
    const targetTypeEl = $("[data-admin-change-log-filter-target-type]");
    const targetIdEl = $("[data-admin-change-log-filter-target-id]");
    const actionEl = $("[data-admin-change-log-filter-action]");
    const changedKeyEl = $("[data-admin-change-log-filter-changed-key]");
    const appliedEl = $("[data-admin-change-log-filter-applied]");
    const sortEl = $("[data-admin-change-log-filter-sort]");
    if (limitEl) limitEl.value = String(DEFAULT_CHANGE_LOG_LIMIT);
    if (targetTypeEl) targetTypeEl.value = "";
    if (targetIdEl) targetIdEl.value = "";
    if (actionEl) actionEl.value = "";
    if (changedKeyEl) changedKeyEl.value = "";
    if (appliedEl) appliedEl.value = "all";
    if (sortEl) sortEl.value = DEFAULT_CHANGE_LOG_SORT;
    if (!opts.silent) setStatus("관리자 변경 이력 필터 초기화", "info");
    return readChangeLogFiltersFromDom();
  }

  function describeChangeLogFilters(filters) {
    const f = filters || {};
    const parts = [];
    if (f.targetType) parts.push(`targetType=${f.targetType}`);
    if (f.targetId) parts.push(`targetId=${f.targetId}`);
    if (f.action) parts.push(`action=${f.action}`);
    if (f.changedKey) parts.push(`changedKey=${f.changedKey}`);
    if (f.applied !== undefined && f.applied !== null) parts.push(`applied=${f.applied}`);
    if (f.sort && f.sort !== DEFAULT_CHANGE_LOG_SORT) parts.push(`sort=${f.sort}`);
    return parts.length ? parts.join(", ") : "필터 없음";
  }



  function readMasterCatalogFiltersFromDom() {
    const domainEl = $("[data-admin-master-domain]");
    const limitEl = $("[data-admin-master-limit]");
    const queryEl = $("[data-admin-master-query]");
    const enabledEl = $("[data-admin-master-enabled]");
    const sortEl = $("[data-admin-master-sort]");
    const pageEl = $("[data-admin-master-page]");
    const pageValue = pageEl && pageEl.value ? Number(pageEl.value) : 1;
    return {
      domain: domainEl && domainEl.value ? domainEl.value : DEFAULT_MASTER_DOMAIN,
      limit: limitEl && limitEl.value ? Number(limitEl.value) : DEFAULT_MASTER_LIMIT,
      page: Number.isFinite(pageValue) && pageValue > 0 ? Math.floor(pageValue) : 1,
      query: queryEl ? queryEl.value.trim() : "",
      enabled: enabledEl && enabledEl.value ? enabledEl.value : "all",
      sort: sortEl && sortEl.value ? sortEl.value : DEFAULT_MASTER_SORT,
    };
  }

  function resetMasterCatalogFilters(options) {
    const opts = options || {};
    const domainEl = $("[data-admin-master-domain]");
    const limitEl = $("[data-admin-master-limit]");
    const queryEl = $("[data-admin-master-query]");
    const enabledEl = $("[data-admin-master-enabled]");
    const sortEl = $("[data-admin-master-sort]");
    const pageEl = $("[data-admin-master-page]");
    if (domainEl) domainEl.value = DEFAULT_MASTER_DOMAIN;
    if (limitEl) limitEl.value = String(DEFAULT_MASTER_LIMIT);
    if (pageEl) pageEl.value = "1";
    if (queryEl) queryEl.value = "";
    if (enabledEl) enabledEl.value = "all";
    if (sortEl) sortEl.value = DEFAULT_MASTER_SORT;
    if (!opts.silent) setStatus("마스터 데이터 카탈로그 필터 초기화", "info");
    return readMasterCatalogFiltersFromDom();
  }

  function describeMasterCatalogFilters(filters) {
    const f = filters || {};
    const parts = [];
    if (f.domain) parts.push(`domain=${f.domain}`);
    if (f.query) parts.push(`query=${f.query}`);
    if (f.enabled && f.enabled !== "all") parts.push(`enabled=${f.enabled}`);
    if (f.sort && f.sort !== DEFAULT_MASTER_SORT) parts.push(`sort=${f.sort}`);
    if (f.page && Number(f.page) > 1) parts.push(`page=${f.page}`);
    return parts.length ? parts.join(", ") : "마스터 필터 없음";
  }

  function syncMasterDomainOptions(domainsPayload) {
    const select = $("[data-admin-master-domain]");
    const meta = $("[data-admin-master-domain-meta]");
    if (!select) return;
    const current = select.value || DEFAULT_MASTER_DOMAIN;
    const domains = Array.isArray(domainsPayload && domainsPayload.domains) ? domainsPayload.domains : [];
    if (!domains.length) return;
    select.innerHTML = domains.map((domain) => `
      <option value="${escapeHtml(domain.key)}">${escapeHtml(domain.label || domain.key)} (${escapeHtml(formatValue(domain.total))})</option>
    `).join("");
    const nextValue = domains.some((domain) => domain.key === current) ? current : (domainsPayload.defaultDomain || DEFAULT_MASTER_DOMAIN);
    select.value = nextValue;
    if (meta) meta.textContent = `${formatValue(domains.length)} domains · raw JSON hidden · assets hidden`;
    syncAdminCreateDomainOptions(domainsPayload);
  }


  function readAdminCreateBlueprintFiltersFromDom() {
    const domainEl = $("[data-admin-create-domain]");
    const masterDomainEl = $("[data-admin-master-domain]");
    return {
      domain: domainEl && domainEl.value ? domainEl.value : (masterDomainEl && masterDomainEl.value ? masterDomainEl.value : DEFAULT_MASTER_DOMAIN),
    };
  }

  function syncAdminCreateDomainOptions(domainsPayload) {
    const select = $("[data-admin-create-domain]");
    if (!select) return;
    const current = select.value || DEFAULT_MASTER_DOMAIN;
    const domains = Array.isArray(domainsPayload && domainsPayload.domains) ? domainsPayload.domains : [];
    if (!domains.length) return;
    select.innerHTML = domains.map((domain) => `
      <option value="${escapeHtml(domain.key)}">${escapeHtml(domain.label || domain.key)} (${escapeHtml(formatValue(domain.total))})</option>
    `).join("");
    select.value = domains.some((domain) => domain.key === current) ? current : (domainsPayload.defaultDomain || DEFAULT_MASTER_DOMAIN);
  }

  function syncAdminCreateDomainFromCatalog() {
    const createDomainEl = $("[data-admin-create-domain]");
    const masterDomainEl = $("[data-admin-master-domain]");
    if (createDomainEl && masterDomainEl && masterDomainEl.value) createDomainEl.value = masterDomainEl.value;
    return readAdminCreateBlueprintFiltersFromDom();
  }

  async function fetchAdminReadOnlyPageData(options) {
    ensureApi();
    const opts = options || {};
    const timeoutMs = opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS;
    const filters = opts.snapshotFilters || readSnapshotFiltersFromDom();
    const masterCatalogFilters = opts.masterCatalogFilters || readMasterCatalogFiltersFromDom();
    const changeLogFilters = opts.changeLogFilters || readChangeLogFiltersFromDom();
    const createBlueprintFilters = opts.createBlueprintFilters || readAdminCreateBlueprintFiltersFromDom();
    const [overview, snapshots, masterDomains, masterCatalog, changeLogs, createBlueprint] = await Promise.all([
      window.RpgGameApi.fetchAdminOverview({ timeoutMs }),
      window.RpgGameApi.listAdminSaveSnapshots({ timeoutMs, ...filters }),
      window.RpgGameApi.listAdminMasterCatalogDomains({ timeoutMs }),
      window.RpgGameApi.listAdminMasterCatalogRows({ timeoutMs, ...masterCatalogFilters }),
      window.RpgGameApi.listAdminChangeLogs({ timeoutMs, ...changeLogFilters }),
      window.RpgGameApi.fetchAdminMasterCreateBlueprint({ timeoutMs, ...createBlueprintFilters }),
    ]);
    return { overview, snapshots, masterDomains, masterCatalog, changeLogs, createBlueprint, snapshotFilters: filters, masterCatalogFilters, changeLogFilters, createBlueprintFilters };
  }

  function renderCards(overviewPayload) {
    const master = overviewPayload.masterData || {};
    const save = overviewPayload.saveSnapshots || {};
    const users = overviewPayload.users || {};
    const readiness = overviewPayload.readiness || {};
    const target = $("[data-admin-cards]");
    if (!target) return;
    const writeLocked = readiness.safeForAdminWriteUi === false;
    target.innerHTML = `
      <div class="card"><div class="label">읽기 전용</div><div class="value small"><span class="pill good">${escapeHtml(formatValue(overviewPayload.readOnly))}</span></div></div>
      <div class="card"><div class="label">마스터 행 수</div><div class="value">${escapeHtml(formatValue(master.summary && master.summary.totalRows))}</div></div>
      <div class="card"><div class="label">DB 세이브 슬롯</div><div class="value">${escapeHtml(formatValue(save.totalSlots))}</div></div>
      <div class="card"><div class="label">저장 유저 수</div><div class="value">${escapeHtml(formatValue(save.usersWithSaves))}</div></div>
      <div class="card"><div class="label">전체 유저</div><div class="value">${escapeHtml(formatValue(users.total))}</div></div>
      <div class="card"><div class="label">관리자 수</div><div class="value">${escapeHtml(formatValue(users.admins))}</div></div>
      <div class="card"><div class="label">최근 저장</div><div class="value small">${escapeHtml(formatClock(save.latestUpdatedAt))}</div></div>
      <div class="card"><div class="label">전체 쓰기 UI</div><div class="value small"><span class="pill ${writeLocked ? "blocked" : "warn"}">${writeLocked ? "blocked" : "check"}</span></div></div>
      <div class="card"><div class="label">마스터 편집 적용</div><div class="value small"><span class="pill ${readiness.guardedMasterEditApplyReady ? "good" : "blocked"}">${readiness.guardedMasterEditApplyReady ? "guarded" : "blocked"}</span></div></div>
      <div class="card"><div class="label">변경 이력 되돌리기</div><div class="value small"><span class="pill ${readiness.guardedRollbackReady ? "good" : "blocked"}">${readiness.guardedRollbackReady ? "guarded" : "blocked"}</span></div></div>
    `;
  }

  function renderMasterTable(masterData) {
    const target = $("[data-admin-master-table]");
    const meta = $("[data-admin-master-meta]");
    if (!target) return;
    const entries = Object.entries(masterData || {}).filter(([key, value]) => key !== "summary" && value && typeof value === "object");
    if (meta) meta.textContent = `${formatValue(masterData && masterData.summary && masterData.summary.domains)} domains`;
    if (!entries.length) {
      target.innerHTML = `<div class="empty">마스터 데이터 count가 없습니다.</div>`;
      return;
    }
    target.innerHTML = `
      <table>
        <thead><tr><th>도메인</th><th>전체</th><th>활성</th><th>비활성</th></tr></thead>
        <tbody>
          ${entries.map(([key, value]) => `
            <tr>
              <td>${escapeHtml(key)}</td>
              <td>${escapeHtml(formatValue(value.total))}</td>
              <td>${escapeHtml(formatValue(value.enabled))}</td>
              <td>${escapeHtml(formatValue(value.disabled))}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }



  function syncMasterCatalogPageInput(page) {
    const pageEl = $("[data-admin-master-page]");
    if (pageEl) pageEl.value = String(Math.max(1, Number(page) || 1));
  }

  function renderMasterCatalogPagination(catalogPayload) {
    const target = $("[data-admin-master-catalog-pagination]");
    if (!target) return;
    const page = Math.max(1, Number(catalogPayload.page) || 1);
    const totalPages = Math.max(1, Number(catalogPayload.totalPages) || 1);
    const total = Number(catalogPayload.total) || 0;
    const limit = Math.max(1, Number(catalogPayload.limit) || DEFAULT_MASTER_LIMIT);
    const start = total ? ((page - 1) * limit) + 1 : 0;
    const end = total ? Math.min(page * limit, total) : 0;
    syncMasterCatalogPageInput(page);
    target.innerHTML = `
      <div class="catalog-pagination-meta">${escapeHtml(formatValue(start))}~${escapeHtml(formatValue(end))} / ${escapeHtml(formatValue(total))} · ${escapeHtml(formatValue(page))}/${escapeHtml(formatValue(totalPages))} 페이지</div>
      <div class="catalog-pagination-actions">
        <button class="btn mini" type="button" data-admin-action="master-catalog-first-page" ${page <= 1 ? "disabled" : ""}>처음</button>
        <button class="btn mini" type="button" data-admin-action="master-catalog-prev-page" ${page <= 1 ? "disabled" : ""}>이전</button>
        <button class="btn mini" type="button" data-admin-action="master-catalog-next-page" ${page >= totalPages ? "disabled" : ""}>다음</button>
        <button class="btn mini" type="button" data-admin-action="master-catalog-last-page" ${page >= totalPages ? "disabled" : ""} data-admin-master-total-pages="${escapeHtml(totalPages)}">끝</button>
      </div>
    `;
  }

  function markSelectedMasterCatalogRow(domain, id) {
    const safeDomain = String(domain || "");
    const safeId = String(id || "");
    Array.from(document.querySelectorAll("[data-admin-master-row-id]")).forEach((row) => {
      const matches = row.getAttribute("data-admin-master-row-domain") === safeDomain && row.getAttribute("data-admin-master-row-id") === safeId;
      row.classList.toggle("catalog-row-selected", matches);
      const marker = row.querySelector("[data-admin-master-row-selected]");
      if (marker) marker.innerHTML = matches ? `<span class="pill good">선택됨</span>` : "";
    });
  }

  async function refreshMasterCatalogWithPage(page) {
    syncMasterCatalogPageInput(page);
    return refreshAdminReadOnlyPage({
      snapshotFilters: readSnapshotFiltersFromDom(),
      masterCatalogFilters: readMasterCatalogFiltersFromDom(),
      changeLogFilters: readChangeLogFiltersFromDom(),
    });
  }

  function renderMasterCatalogTable(catalogPayload) {
    const target = $("[data-admin-master-catalog-table]");
    const meta = $("[data-admin-master-catalog-meta]");
    if (!target) return;
    const rows = Array.isArray(catalogPayload.rows) ? catalogPayload.rows : [];
    const columns = Array.isArray(catalogPayload.columns) ? catalogPayload.columns : [];
    const filters = catalogPayload.filters || {};
    const totalAllNote = catalogPayload.totalAll !== undefined ? ` / 전체 ${formatValue(catalogPayload.totalAll)}` : "";
    const page = Number(catalogPayload.page) || 1;
    const totalPages = Number(catalogPayload.totalPages) || 1;
    const filterNote = filters.hasActiveFilters ? ` · ${describeMasterCatalogFilters(filters)}` : "";
    if (meta) meta.textContent = `${escapeHtml(catalogPayload.domainLabel || catalogPayload.domain || "-")} · ${formatValue(rows.length)} / ${formatValue(catalogPayload.total)} shown · page ${formatValue(page)} / ${formatValue(totalPages)}${totalAllNote}${filterNote}`;
    renderMasterCatalogPagination(catalogPayload);
    if (!rows.length || !columns.length) {
      target.innerHTML = `<div class="empty">마스터 데이터 카탈로그 결과가 없습니다.</div>`;
      return;
    }
    target.innerHTML = `
      <table>
        <thead><tr><th>상세</th>${columns.map((column) => `<th title="${escapeHtml((getAdminFieldHelp(column.key) && getAdminFieldHelp(column.key).body) || column.key)}">${escapeHtml(column.label || column.key)}${renderFieldHelpBadge(column.key)}</th>`).join("")}<th>원본 JSON</th><th>이미지</th></tr></thead>
        <tbody>
          ${rows.map((row) => {
            const cells = row.cells || {};
            return `
              <tr data-admin-master-row-domain="${escapeHtml(row.domain || catalogPayload.domain || "")}" data-admin-master-row-id="${escapeHtml(row.id)}">
                <td><button class="btn mini" type="button" data-admin-action="open-master-detail" data-admin-detail-domain="${escapeHtml(row.domain || catalogPayload.domain || "")}" data-admin-detail-id="${escapeHtml(row.id)}">보기</button><span data-admin-master-row-selected></span></td>
                ${columns.map((column) => `<td>${formatValueWithFieldHint(column.key, cells[column.key])}</td>`).join("")}
                <td><span class="pill ${row.rawJsonReturned ? "blocked" : "good"}">${row.rawJsonReturned ? "returned" : "hidden"}</span></td>
                <td><span class="pill ${row.assetsReturned ? "blocked" : "good"}">${row.assetsReturned ? "returned" : "hidden"}</span></td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>
    `;
    if (currentMasterDetailPayload && currentMasterDetailPayload.domain && currentMasterDetailPayload.id) {
      markSelectedMasterCatalogRow(currentMasterDetailPayload.domain, currentMasterDetailPayload.id);
    }
  }




  function getAdminCreateBlueprintFieldInputKind(field) {
    return String((field && field.inputKind) || "text");
  }

  function getAdminCreateBlueprintRequiredKeys(domain, blueprint) {
    const payload = blueprint || currentAdminCreateBlueprintPayload || {};
    if (domain && payload.domain && payload.domain !== domain) return [];
    return Array.isArray(payload.requiredFields) ? payload.requiredFields.slice() : [];
  }

  function getAdminCreateBlueprintDefaultDraft(domain, blueprint) {
    const payload = blueprint || currentAdminCreateBlueprintPayload || {};
    if (domain && payload.domain && payload.domain !== domain) return {};
    return payload.defaultDraft && typeof payload.defaultDraft === "object" ? { ...payload.defaultDraft } : {};
  }

  function getAdminCreateBlueprintRelationOptionCount(field) {
    const relation = field && field.relation ? field.relation : null;
    if (!relation) return 0;
    if (relation.optionGroups && typeof relation.optionGroups === "object") {
      return Object.values(relation.optionGroups).reduce((sum, options) => sum + (Array.isArray(options) ? options.length : 0), 0);
    }
    return Array.isArray(relation.options) ? relation.options.length : 0;
  }

  function renderAdminCreateBlueprintRelationCell(field) {
    const relation = field && field.relation ? field.relation : null;
    if (!relation) return "-";
    const target = relation.targetLabel || relation.targetDomain || field.targetDomain || "relation";
    const count = getAdminCreateBlueprintRelationOptionCount(field);
    const guard = Array.isArray(field.comboGuard) && field.comboGuard.length ? ` · 중복검사 ${field.comboGuard.join(" + ")}` : "";
    const depends = field.dependsOn ? ` · ${field.dependsOn} 연동` : "";
    return `${escapeHtml(target)} <span class="pill warn">후보 ${escapeHtml(formatValue(count))}</span>${escapeHtml(depends + guard)}`;
  }

  function getAdminCreateFieldDefinition(key) {
    const payload = currentAdminCreateBlueprintPayload || {};
    const fields = Array.isArray(payload.fields) ? payload.fields : [];
    const normalized = normalizeAdminDraftFieldKey(key);
    return fields.find((field) => normalizeAdminDraftFieldKey(field && field.key) === normalized) || null;
  }

  function getAdminCreateRelationDefinition(key) {
    const field = getAdminCreateFieldDefinition(key);
    return field && field.relation ? { ...field.relation, field: field.key, dependsOn: field.dependsOn || (field.relation && field.relation.dependsOn) } : null;
  }

  function getAdminCreateRelationOptionsForValues(definition, values) {
    if (!definition) return null;
    if (definition.optionGroups && definition.dependsOn) {
      const dependencyKey = String(definition.dependsOn || "");
      const groupKey = values && Object.prototype.hasOwnProperty.call(values, dependencyKey) ? String(values[dependencyKey] || "").trim() : "";
      const grouped = definition.optionGroups[groupKey];
      if (Array.isArray(grouped)) return grouped.slice();
    }
    return Array.isArray(definition.options) ? definition.options.slice() : null;
  }

  function getAdminCreateDraftCurrentValues() {
    const draft = $(`[data-admin-create-draft]`);
    const values = {};
    if (!draft) return values;
    Array.from(draft.querySelectorAll("[data-admin-create-draft-field]")).forEach((field) => {
      const key = field.getAttribute("data-admin-create-draft-field");
      if (!key) return;
      const type = field.getAttribute("data-admin-create-draft-value-type") || "text";
      values[key] = type === "boolean" ? field.value === "true" : field.value;
    });
    return values;
  }

  function getAdminCreateDraftSelectOptions(field, value, values) {
    const key = field ? field.key : "";
    const normalized = normalizeAdminDraftFieldKey(key);
    const definition = getAdminCreateRelationDefinition(normalized);
    const relationOptions = getAdminCreateRelationOptionsForValues(definition, values || getAdminCreateDraftCurrentValues());
    const baseOptions = relationOptions ? relationOptions.slice() : (ADMIN_DRAFT_SELECT_FIELD_OPTIONS[normalized] || []).slice();
    const valueText = value === null || value === undefined ? "" : String(value);
    if (valueText && !baseOptions.some((option) => String(option.value) === valueText)) {
      const currentLabel = normalized === "equip_slot" ? `${valueText} · ${getAdminEquipSlotDisplayName(valueText)} · 현재 초안 값` : `${valueText} · 현재 초안 값`;
      baseOptions.unshift({ value: valueText, label: currentLabel, current: true });
    }
    return baseOptions;
  }

  function getAdminCreateRelationSelectMetaText(key, query) {
    const definition = getAdminCreateRelationDefinition(key);
    if (!definition) return "";
    const allOptions = getAdminCreateRelationOptionsForValues(definition, getAdminCreateDraftCurrentValues()) || [];
    const filtered = filterAdminDraftSelectOptions(allOptions, query, "");
    const target = definition.targetLabel || definition.targetDomain || "관계 대상";
    const queryText = normalizeAdminRelationSearchText(query);
    return queryText ? `${target} ${filtered.length}/${allOptions.length}개 표시` : `${target} ${allOptions.length}개 중 선택`;
  }

  function updateAdminCreateRelationOptionMeta(meta, key, query) {
    if (!meta) return;
    const text = getAdminCreateRelationSelectMetaText(key, query);
    meta.textContent = text;
    meta.classList.toggle("warn", !!query && text.includes("0/"));
  }

  function renderAdminCreateDraftControl(field, values) {
    const key = field ? field.key : "";
    const kind = getAdminCreateBlueprintFieldInputKind(field);
    const value = values && Object.prototype.hasOwnProperty.call(values, key) ? values[key] : field.defaultValue;
    const valueText = value === null || value === undefined ? "" : String(value);
    const original = makeDraftOriginalValue(value);
    const commonAttrs = `data-admin-create-draft-field="${escapeHtml(key)}" data-admin-create-draft-original="${escapeHtml(original)}"`;
    if (kind === "boolean-select") {
      const normalized = value === true || String(value).toLowerCase() === "true" ? "true" : "false";
      return `
        <select ${commonAttrs} data-admin-create-draft-value-type="boolean" aria-label="${escapeHtml(field.label || key)} true false 선택">
          <option value="true" ${normalized === "true" ? "selected" : ""}>true · 켜짐</option>
          <option value="false" ${normalized === "false" ? "selected" : ""}>false · 꺼짐</option>
        </select>
      `;
    }
    if (kind === "preset-select") {
      const options = getAdminCreateDraftSelectOptions(field, value, values);
      return `
        <select ${commonAttrs} data-admin-create-draft-value-type="text" aria-label="${escapeHtml(field.label || key)} 선택">
          ${renderAdminDraftSelectOptionsHtml(options, valueText)}
        </select>
      `;
    }
    if (kind === "relation-select") {
      const options = getAdminCreateDraftSelectOptions(field, value, values);
      const definition = getAdminCreateRelationDefinition(key) || {};
      const metaText = getAdminCreateRelationSelectMetaText(key, "");
      return `
        <div class="relation-select-tools" data-admin-create-relation-select-tools>
          <input class="relation-option-filter" data-admin-create-relation-option-filter data-admin-create-relation-option-filter-for="${escapeHtml(key)}" type="text" placeholder="코드/이름으로 후보 검색" autocomplete="off" aria-label="${escapeHtml(field.label || key)} 후보 검색" />
          <select ${commonAttrs} data-admin-create-draft-value-type="text" aria-label="${escapeHtml(field.label || key)} 선택">
            ${renderAdminDraftSelectOptionsHtml(options, valueText)}
          </select>
          <div class="relation-option-meta" data-admin-create-relation-option-meta>${escapeHtml(metaText || (definition.targetLabel ? `${definition.targetLabel} 후보` : "관계 후보"))}</div>
        </div>
      `;
    }
    if (kind === "number") {
      return `<input type="number" inputmode="decimal" step="any" value="${escapeHtml(valueText)}" ${commonAttrs} data-admin-create-draft-value-type="number" />`;
    }
    if (kind === "textarea") {
      const rows = ADMIN_DRAFT_TEXTAREA_FIELDS.has(normalizeAdminDraftFieldKey(key)) ? 4 : 3;
      return `<textarea rows="${rows}" ${commonAttrs} data-admin-create-draft-value-type="text">${escapeHtml(valueText)}</textarea>`;
    }
    return `<input type="text" value="${escapeHtml(valueText)}" ${commonAttrs} data-admin-create-draft-value-type="text" />`;
  }

  function applyAdminCreateRelationOptionFilter(input) {
    if (!input) return false;
    const draft = input.closest("[data-admin-create-draft]");
    const wrapper = input.closest("[data-admin-create-relation-select-tools]");
    if (!draft || !wrapper) return false;
    const key = input.getAttribute("data-admin-create-relation-option-filter-for") || "";
    const field = getAdminCreateFieldDefinition(key);
    const select = wrapper.querySelector(`[data-admin-create-draft-field="${key}"]`);
    if (!field || !select) return false;
    const selectedValue = select.value;
    const options = getAdminCreateDraftSelectOptions(field, selectedValue, getAdminCreateDraftCurrentValues());
    const filtered = filterAdminDraftSelectOptions(options, input.value, selectedValue);
    select.innerHTML = renderAdminDraftSelectOptionsHtml(filtered, selectedValue);
    select.value = selectedValue;
    updateAdminCreateRelationOptionMeta(wrapper.querySelector("[data-admin-create-relation-option-meta]"), key, input.value);
    return true;
  }

  function refreshDependentAdminCreateRelationSelects(changedKey) {
    const draft = document.querySelector("[data-admin-create-draft]");
    if (!draft) return false;
    const changed = normalizeAdminDraftFieldKey(changedKey);
    let touched = false;
    const fields = Array.isArray(currentAdminCreateBlueprintPayload && currentAdminCreateBlueprintPayload.fields) ? currentAdminCreateBlueprintPayload.fields : [];
    fields.forEach((field) => {
      const definition = field && field.relation ? { ...field.relation, field: field.key, dependsOn: field.dependsOn || field.relation.dependsOn } : null;
      if (!definition || normalizeAdminDraftFieldKey(definition.dependsOn) !== changed) return;
      const target = draft.querySelector(`[data-admin-create-draft-field="${field.key}"]`);
      if (!target) return;
      const previousValue = target.value;
      const options = getAdminCreateRelationOptionsForValues(definition, getAdminCreateDraftCurrentValues()) || [];
      let nextValue = "";
      if (options.some((option) => String(option.value) === previousValue)) nextValue = previousValue;
      else if (options.length) nextValue = String(options[0].value ?? "");
      const wrapper = target.closest("[data-admin-create-relation-select-tools]");
      const filter = wrapper ? wrapper.querySelector("[data-admin-create-relation-option-filter]") : null;
      if (filter) filter.value = "";
      target.innerHTML = renderAdminDraftSelectOptionsHtml(options, nextValue);
      target.value = nextValue;
      updateAdminCreateRelationOptionMeta(wrapper && wrapper.querySelector("[data-admin-create-relation-option-meta]"), field.key, "");
      touched = true;
    });
    return touched;
  }

  function renderAdminCreateDraft(blueprintPayload) {
    const payload = blueprintPayload || currentAdminCreateBlueprintPayload || {};
    const fields = Array.isArray(payload.fields) ? payload.fields : [];
    const defaultDraft = payload.defaultDraft && typeof payload.defaultDraft === "object" ? payload.defaultDraft : {};
    const editableFields = fields.filter((field) => field && field.futureEditable !== false && getAdminCreateBlueprintFieldInputKind(field) !== "json-readonly");
    if (!editableFields.length) return `<div class="empty">이 도메인은 아직 생성 초안 입력 필드가 없습니다.</div>`;
    const rows = editableFields.map((field) => `
      <label class="draft-field draft-field-${escapeHtml(getAdminCreateBlueprintFieldInputKind(field))}">
        <span class="draft-field-heading">
          <span>${escapeHtml(field.label || field.key)}${renderFieldHelpBadge(field.key)}</span>
          <span class="draft-field-badges">${renderAdminDraftTypeBadge(getAdminCreateBlueprintFieldInputKind(field))}${field.required ? ` <span class="pill blocked">필수</span>` : ` <span class="pill good">선택</span>`}${field.unique ? ` <span class="pill warn">unique</span>` : ""}</span>
        </span>
        ${renderFieldHelpInline(field.key)}
        ${renderFieldValueHintInline(field.key, field.defaultValue)}
        ${renderAdminCreateDraftControl(field, defaultDraft)}
      </label>
    `).join("");
    return `
      <div class="detail-card edit-draft-card create-draft-card" data-admin-create-draft data-admin-create-draft-domain="${escapeHtml(payload.domain || DEFAULT_MASTER_DOMAIN)}">
        <div class="detail-title">신규 row 생성 초안 <span class="pill warn">preview first</span><span class="pill ${payload.createApplyUnlocked ? "warn" : "blocked"}">${payload.createApplyUnlocked ? "limited insert open" : "insert locked"}</span></div>
        <div class="filter-help">아래 입력칸은 새 row를 만들 때 필요한 값을 미리 넣어보는 화면입니다. 먼저 <strong>생성 초안 검증</strong>으로 unique/relation/combo 검사를 통과해야 합니다. 실제 생성은 characters/enhancementGroups만 dev key와 확인 문구로 제한 적용됩니다.</div>
        <div class="edit-draft-grid">${rows}</div>
        <div class="edit-draft-actions">
          <button class="btn mini primary" type="button" data-admin-action="preview-admin-create-draft">생성 초안 검증</button>
          <button class="btn mini" type="button" data-admin-action="reset-admin-create-draft">기본값으로 되돌리기</button>
          <label class="apply-confirm-field"><span>생성 사유</span><input type="text" data-admin-create-reason placeholder="예: 신규 강화 그룹 준비" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>생성 확인 문구</span><input type="text" data-admin-create-confirm placeholder="${escapeHtml(payload.confirmTextRequired || ADMIN_CREATE_APPLY_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <button class="btn mini danger" type="button" data-admin-action="apply-admin-create-draft" ${payload.createApplyUnlocked ? "" : "disabled"}>실제 생성 적용</button>
          <span class="pill ${payload.createApplyUnlocked ? "warn" : "blocked"}">${payload.createApplyUnlocked ? "제한 insert 가능" : "DB insert 잠금"}</span>
        </div>
        <div class="edit-draft-result" data-admin-create-draft-result><div class="empty">값을 입력한 뒤 <strong>생성 초안 검증</strong>을 누르세요. 생성 적용 전에도 백엔드가 같은 검증을 다시 실행합니다.</div></div>
      </div>
    `;
  }

  function renderAdminCreateBlueprint(blueprintPayload) {
    currentAdminCreateBlueprintPayload = blueprintPayload && blueprintPayload.status === "loaded" ? blueprintPayload : null;
    const target = $("[data-admin-create-blueprint]");
    if (!target) return;
    const payload = blueprintPayload || {};
    if (payload.status && payload.status !== "loaded") {
      target.innerHTML = `<div class="error">신규 row 생성 설계를 불러오지 못했습니다: ${escapeHtml(payload.status)}</div>`;
      return;
    }
    if (!payload.domain) {
      target.innerHTML = `<div class="empty">생성 설계를 불러오면 필수 필드, 기본값, relation 후보가 여기에 표시됩니다.</div>`;
      return;
    }
    const fields = Array.isArray(payload.fields) ? payload.fields : [];
    const requiredFields = Array.isArray(payload.requiredFields) ? payload.requiredFields : [];
    const uniqueFields = Array.isArray(payload.uniqueFields) ? payload.uniqueFields : [];
    const comboGuards = Array.isArray(payload.comboGuards) ? payload.comboGuards : [];
    const defaultDraft = payload.defaultDraft && typeof payload.defaultDraft === "object" ? payload.defaultDraft : {};
    const rows = fields.length ? fields.map((field) => {
      const inputKind = getAdminCreateBlueprintFieldInputKind(field);
      const relationText = renderAdminCreateBlueprintRelationCell(field);
      return `
        <tr>
          <td>${escapeHtml(field.label || field.key)}${renderFieldHelpBadge(field.key)}</td>
          <td>${field.required ? `<span class="pill blocked">필수</span>` : `<span class="pill good">선택</span>`}${field.unique ? ` <span class="pill warn">unique</span>` : ""}</td>
          <td><span class="pill">${escapeHtml(inputKind)}</span></td>
          <td>${formatValueWithFieldHint(field.key, field.defaultValue)}</td>
          <td>${relationText}</td>
          <td><span class="create-blueprint-locked">${field.futureEditable === false ? "잠금" : "초안 가능"}</span><div class="filter-help" style="margin-top:4px;">${escapeHtml(field.futureEditable === false ? (field.lockedReason || "read-only") : "preview-only 입력 UI에서 검증 가능")}</div></td>
        </tr>
      `;
    }).join("") : `<tr><td colspan="6">필드 설계가 없습니다.</td></tr>`;
    target.innerHTML = `
      <div class="create-blueprint-summary">
        <div class="create-blueprint-card"><strong>${escapeHtml(payload.domainLabel || payload.domain)}</strong><span>${escapeHtml(payload.description || "설명 없음")}</span></div>
        <div class="create-blueprint-card"><strong>필수 필드</strong><span>${escapeHtml(requiredFields.join(", ") || "없음")}</span></div>
        <div class="create-blueprint-card"><strong>고유/중복 검사</strong><span>unique: ${escapeHtml(uniqueFields.join(", ") || "없음")}<br>combo: ${escapeHtml(comboGuards.map((guard) => guard.join(" + ")).join(", ") || "없음")}</span></div>
        <div class="create-blueprint-card"><strong>적용 상태</strong><span><span class="pill ${payload.createApplyUnlocked ? "warn" : "blocked"}">${payload.createApplyUnlocked ? "limited insert open" : "insert API locked"}</span><br>${payload.createApplyUnlocked ? "dev key + 확인 문구 필요" : "preview-only 검증 가능 · DB 수정 없음"}</span></div>
      </div>
      <div class="table-wrap relation-table-wrap">
        <table>
          <thead><tr><th>필드</th><th>필수</th><th>입력 타입</th><th>기본값</th><th>관계 후보</th><th>현재 상태</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      <div class="create-blueprint-default">
        <pre>${escapeHtml(JSON.stringify(defaultDraft, null, 2))}</pre>
      </div>
      ${renderAdminCreateDraft(payload)}
      <div class="filter-help" style="padding:0 14px 12px;">relation 후보 반환=${escapeHtml(formatValue(payload.relationOptionsReturned))} · rawJsonReturned=${escapeHtml(formatValue(payload.rawJsonReturned))} · assetsReturned=${escapeHtml(formatValue(payload.assetsReturned))}</div>
    `;
  }

  async function refreshAdminCreateBlueprint(options) {
    ensureApi();
    const filters = options || readAdminCreateBlueprintFiltersFromDom();
    const response = await window.RpgGameApi.fetchAdminMasterCreateBlueprint({ timeoutMs: DEFAULT_TIMEOUT_MS, ...filters });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreateBlueprint(payload);
    setStatus(`신규 row 생성 설계 로드: ${formatValue(payload.domainLabel || payload.domain)} · ${formatValue(payload.fieldCount)} fields · ${payload.createApplyUnlocked ? "limited insert open" : "preview-only"}`, "ok");
    return payload;
  }

  function readAdminCreateDraftValues() {
    const draft = $(`[data-admin-create-draft]`);
    if (!draft) return { ok: false, reason: "create_draft_missing", draft: {} };
    const fields = Array.from(draft.querySelectorAll("[data-admin-create-draft-field]"));
    const values = {};
    fields.forEach((field) => {
      const key = field.getAttribute("data-admin-create-draft-field");
      if (!key) return;
      const type = field.getAttribute("data-admin-create-draft-value-type") || "text";
      values[key] = type === "boolean" ? field.value === "true" : field.value;
    });
    const reasonEl = $(`[data-admin-create-reason]`);
    const confirmEl = $(`[data-admin-create-confirm]`);
    return {
      ok: true,
      domain: draft.getAttribute("data-admin-create-draft-domain") || (currentAdminCreateBlueprintPayload && currentAdminCreateBlueprintPayload.domain) || DEFAULT_MASTER_DOMAIN,
      draft: values,
      reason: reasonEl ? reasonEl.value.trim() : "",
      confirmText: confirmEl ? confirmEl.value.trim() : "",
      fieldCount: fields.length,
    };
  }

  function resetAdminCreateDraft() {
    const draft = $(`[data-admin-create-draft]`);
    if (!draft) return false;
    Array.from(draft.querySelectorAll("[data-admin-create-draft-field]")).forEach((field) => {
      const type = field.getAttribute("data-admin-create-draft-value-type") || "text";
      const original = parseDraftOriginalValue(field.getAttribute("data-admin-create-draft-original"));
      if (type === "boolean") field.value = original ? "true" : "false";
      else field.value = original === null || original === undefined ? "" : String(original);
    });
    Array.from(draft.querySelectorAll("[data-admin-create-relation-option-filter]")).forEach((input) => { input.value = ""; applyAdminCreateRelationOptionFilter(input); });
    const confirmEl = $(`[data-admin-create-confirm]`);
    if (confirmEl) confirmEl.value = "";
    const result = $(`[data-admin-create-draft-result]`);
    if (result) result.innerHTML = `<div class="empty">기본값으로 되돌렸습니다. 값을 입력한 뒤 생성 초안 검증을 누르세요.</div>`;
    setStatus("생성 초안을 기본값으로 되돌렸습니다.", "ok");
    return true;
  }

  function renderAdminCreatePreviewValueCell(field) {
    const rawValue = field ? field.after : undefined;
    const relationText = formatAdminRelationInfoText(field && field.relation, rawValue);
    const text = relationText !== null ? relationText : formatValue(rawValue);
    const relation = field && field.relation ? field.relation : null;
    const target = relation && relation.targetDomain && !String(relation.targetDomain).includes("/") && relation.targetCode ? { domain: String(relation.targetDomain), code: String(relation.targetCode) } : null;
    return `<div class="relation-value-cell"><span>${escapeHtml(text)}</span>${renderAdminRelationOpenTargetButton(target)}</div>`;
  }

  function renderAdminCreatePreviewResult(preview) {
    const target = $(`[data-admin-create-draft-result]`);
    if (!target) return;
    const payload = preview || {};
    const accepted = Array.isArray(payload.acceptedFields) ? payload.acceptedFields : [];
    const rejected = Array.isArray(payload.rejectedFields) ? payload.rejectedFields : [];
    const acceptedRows = accepted.length ? accepted.map((field) => `
      <tr><td>${escapeHtml(field.label || field.key)}${field.relation ? ` <span class="pill warn">relation</span>` : ""}</td><td>${renderAdminCreatePreviewValueCell(field)}</td><td>${escapeHtml(field.type || field.inputKind || "-")}</td><td>${field.required ? `<span class="pill blocked">필수</span>` : `<span class="pill good">선택</span>`}${field.unique ? ` <span class="pill warn">unique</span>` : ""}</td></tr>
    `).join("") : `<tr><td colspan="4">검증 통과 필드 없음</td></tr>`;
    const rejectedRows = rejected.length ? rejected.map((field) => `
      <tr><td>${escapeHtml(field.label || field.key)}</td><td>${escapeHtml(formatValue(field.after))}</td><td>${escapeHtml(field.reason || "rejected")}</td></tr>
    `).join("") : `<tr><td colspan="3">오류 없음</td></tr>`;
    target.innerHTML = `
      <div class="draft-preview-summary">
        <span class="pill ${payload.wouldBeValid ? "good" : "blocked"}">valid: ${escapeHtml(formatValue(payload.wouldBeValid))}</span>
        <span class="pill ${payload.dryRun ? "warn" : "good"}">dryRun: ${escapeHtml(formatValue(payload.dryRun))}</span>
        <span class="pill ${payload.writeBlocked ? "blocked" : "good"}">writeBlocked: ${escapeHtml(formatValue(payload.writeBlocked))}</span>
        <span class="pill ${payload.createApplyReady ? "warn" : "blocked"}">createApplyReady: ${escapeHtml(formatValue(payload.createApplyReady))}</span>
        ${payload.created ? `<span class="pill good">created #${escapeHtml(formatValue(payload.id))}</span>` : ""}
        ${payload.changeLogId ? `<span class="pill good">changeLog #${escapeHtml(formatValue(payload.changeLogId))}</span>` : ""}
        <span class="pill">fields ${escapeHtml(formatValue(payload.fieldCount || accepted.length))}</span>
        <span class="pill ${rejected.length ? "blocked" : "good"}">errors ${escapeHtml(formatValue(payload.errorCount || rejected.length))}</span>
        <span class="pill ${payload.relationFieldCount ? "warn" : "good"}">relation ${escapeHtml(formatValue(payload.relationFieldCount || 0))}</span>
        <span class="pill ${payload.comboGuardCount ? "warn" : "good"}">combo ${escapeHtml(formatValue(payload.comboGuardCount || 0))}</span>
      </div>
      ${payload.comboGuardLabels && payload.comboGuardLabels.length ? `<div class="filter-help">중복 조합 검사: ${escapeHtml(payload.comboGuardLabels.join(", "))}</div>` : ""}
      ${payload.note ? `<div class="filter-help">${escapeHtml(payload.note)}</div>` : ""}
      <details class="json-detail" open>
        <summary>검증 통과 필드 <span class="pill good">${escapeHtml(formatValue(accepted.length))}</span></summary>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>초안 값</th><th>타입</th><th>속성</th></tr></thead><tbody>${acceptedRows}</tbody></table></div>
      </details>
      <details class="json-detail" ${rejected.length ? "open" : ""}>
        <summary>검증 오류 <span class="pill ${rejected.length ? "blocked" : "good"}">${escapeHtml(formatValue(rejected.length))}</span></summary>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>초안 값</th><th>사유</th></tr></thead><tbody>${rejectedRows}</tbody></table></div>
      </details>
      ${payload.createdRow ? `<div class="filter-help">생성됨: ${escapeHtml(payload.createdRow.domain)} #${escapeHtml(formatValue(payload.createdRow.id))} · ${escapeHtml(formatValue(payload.createdRow.code || payload.createdRow.title))}</div>` : ""}
      <div class="filter-help">${payload.created ? "DB insert와 create change log가 완료되었습니다. create rollback/delete는 아직 잠겨 있습니다." : "검증 통과 후 제한 도메인은 dev key와 생성 확인 문구로 실제 생성 적용할 수 있습니다."}</div>
    `;
  }

  async function previewAdminCreateDraft(options) {
    ensureApi();
    const values = readAdminCreateDraftValues();
    if (!values.ok) {
      const error = new Error("검증할 생성 초안이 없습니다. 먼저 생성 설계를 불러와 주세요.");
      setStatus(error.message, "error");
      throw error;
    }
    const target = $(`[data-admin-create-draft-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에서 생성 초안을 검증하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.previewAdminMasterDataCreate({
      domain: values.domain,
      draft: values.draft,
      reason: values.reason || undefined,
      dryRun: true,
      timeoutMs,
    });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreatePreviewResult(payload);
    setStatus(`생성 초안 검증 완료: fields ${formatValue(payload.fieldCount)} · errors ${formatValue(payload.errorCount)} · createApplyReady ${formatValue(payload.createApplyReady)}`, payload.errorCount ? "error" : "ok");
    return response;
  }

  async function applyAdminCreateDraft(options) {
    ensureApi();
    const values = readAdminCreateDraftValues();
    if (!values.ok) {
      const error = new Error("생성 적용할 초안이 없습니다. 먼저 생성 설계를 불러와 주세요.");
      setStatus(error.message, "error");
      throw error;
    }
    if (!values.confirmText) {
      const error = new Error(`생성 확인 문구를 입력해야 합니다: ${ADMIN_CREATE_APPLY_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      throw error;
    }
    const target = $(`[data-admin-create-draft-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에서 생성 초안을 재검증하고 실제 생성 적용 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : ADMIN_EDIT_APPLY_TIMEOUT_MS;
    const response = await window.RpgGameApi.applyAdminMasterDataCreate({
      domain: values.domain,
      draft: values.draft,
      reason: values.reason || undefined,
      confirmText: values.confirmText,
      dryRun: false,
      timeoutMs,
    });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreatePreviewResult(payload);
    if (payload.created) {
      setStatus(`신규 row 생성 완료: ${formatValue(payload.domain)} #${formatValue(payload.id)} · changeLog #${formatValue(payload.changeLogId)}`, "ok");
      await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      await refreshAdminReadOnlyPage({
        snapshotFilters: readSnapshotFiltersFromDom(),
        masterCatalogFilters: { ...readMasterCatalogFiltersFromDom(), domain: values.domain, page: 1 },
        changeLogFilters: readChangeLogFiltersFromDom(),
        createBlueprintFilters: { domain: values.domain },
      });
    } else {
      setStatus(`신규 row 생성 차단: ${formatValue(payload.status)} · errors ${formatValue(payload.errorCount)}`, "error");
    }
    return response;
  }

  function getAdminCreateBlueprintReadiness() {
    const target = $("[data-admin-create-blueprint]");
    const draft = $(`[data-admin-create-draft]`);
    const filters = readAdminCreateBlueprintFiltersFromDom();
    const payload = currentAdminCreateBlueprintPayload || {};
    const fields = draft ? Array.from(draft.querySelectorAll("[data-admin-create-draft-field]")) : [];
    return {
      ready: !!target,
      readOnly: !payload.createApplyUnlocked,
      createApplyReady: !!payload.createApplyReady,
      createApplyUnlocked: !!payload.createApplyUnlocked,
      insertLocked: payload.insertLocked !== false,
      confirmTextRequired: payload.confirmTextRequired || ADMIN_CREATE_APPLY_CONFIRM_TEXT,
      allowedCreateApplyDomains: Array.isArray(payload.allowedCreateApplyDomains) ? payload.allowedCreateApplyDomains.slice() : [],
      previewReady: typeof previewAdminCreateDraft === "function" && !!window.RpgGameApi && typeof window.RpgGameApi.previewAdminMasterDataCreate === "function",
      applyReady: typeof applyAdminCreateDraft === "function" && !!window.RpgGameApi && typeof window.RpgGameApi.applyAdminMasterDataCreate === "function",
      domain: filters.domain,
      loadedDomain: payload.domain || null,
      fieldCount: Number(payload.fieldCount || 0),
      draftFieldCount: fields.length,
      requiredFields: getAdminCreateBlueprintRequiredKeys(payload.domain, payload),
      defaultDraft: getAdminCreateBlueprintDefaultDraft(payload.domain, payload),
      relationOptionsReturned: !!payload.relationOptionsReturned,
    };
  }

  function getAdminRelationEditOptionDefinitions(domain) {
    const detail = currentMasterDetailPayload && currentMasterDetailPayload.domain === domain ? currentMasterDetailPayload : {};
    return Array.isArray(detail.relationEditOptions) ? detail.relationEditOptions : [];
  }

  function getAdminRelationEditOptionDefinition(domain, key) {
    const normalized = normalizeAdminDraftFieldKey(key);
    return getAdminRelationEditOptionDefinitions(domain).find((definition) => normalizeAdminDraftFieldKey(definition && definition.field) === normalized) || null;
  }

  function isAdminRelationEditField(domain, key) {
    return !!getAdminRelationEditOptionDefinition(domain, key);
  }

  function fieldKeyLooksReadOnly(domain, key) {
    const normalized = String(key || "").toLowerCase();
    if (isAdminRelationEditField(domain, normalized)) return false;
    return normalized === "id" || normalized === "code" || normalized.endsWith("_id") || normalized.endsWith("_code") || normalized.endsWith("_json") || normalized === "created_at" || normalized === "updated_at" || normalized === "createdat" || normalized === "updatedat";
  }

  function isAdminEditApplyAllowedField(domain, key) {
    const allowed = ADMIN_EDIT_ALLOWED_FIELDS[domain] || [];
    return allowed.includes(String(key || ""));
  }

  function getAdminEditAllowedFields(domain) {
    return (ADMIN_EDIT_ALLOWED_FIELDS[domain] || []).slice();
  }

  function normalizeAdminDraftFieldKey(key) {
    return String(key || "").trim().toLowerCase();
  }

  function getAdminEquipSlotDisplayName(value) {
    const key = value === null || value === undefined ? "" : String(value);
    return ADMIN_EQUIP_SLOT_PRESET_LABELS[key] || key || "장착 슬롯 없음";
  }

  function getAdminDraftRelationOptionGroupKey(definition) {
    if (!definition || !definition.dependsOn) return "";
    const dependencyField = document.querySelector(`[data-admin-edit-draft-field="${definition.dependsOn}"]`);
    const dependencyValue = dependencyField ? dependencyField.value : "";
    return String(dependencyValue || "").trim();
  }

  function getAdminDraftRelationOptionsForValues(definition, values) {
    if (!definition) return null;
    if (definition.optionGroups && definition.dependsOn) {
      const dependencyKey = String(definition.dependsOn || "");
      const groupKey = values && Object.prototype.hasOwnProperty.call(values, dependencyKey) ? String(values[dependencyKey] || "").trim() : getAdminDraftRelationOptionGroupKey(definition);
      const grouped = definition.optionGroups[groupKey];
      if (Array.isArray(grouped)) return grouped.slice();
    }
    return Array.isArray(definition.options) ? definition.options.slice() : null;
  }

  function getAdminDraftRelationOptions(definition) {
    return getAdminDraftRelationOptionsForValues(definition, null);
  }

  function getAdminDraftSelectOptions(key, value, domain) {
    const normalized = normalizeAdminDraftFieldKey(key);
    const relationDefinition = getAdminRelationEditOptionDefinition(domain, normalized);
    const relationOptions = getAdminDraftRelationOptions(relationDefinition);
    const baseOptions = relationOptions ? relationOptions.slice() : (ADMIN_DRAFT_SELECT_FIELD_OPTIONS[normalized] || []).slice();
    const valueText = value === null || value === undefined ? "" : String(value);
    if (valueText && !baseOptions.some((option) => String(option.value) === valueText)) {
      const currentLabel = normalized === "equip_slot" ? `${valueText} · ${getAdminEquipSlotDisplayName(valueText)} · 현재 DB 값` : `${valueText} · 현재 DB 값`;
      baseOptions.unshift({ value: valueText, label: currentLabel, current: true });
    }
    return baseOptions;
  }

  function normalizeAdminRelationSearchText(value) {
    return String(value === null || value === undefined ? "" : value).trim().toLowerCase();
  }

  function getAdminRelationOptionText(option) {
    if (!option) return "";
    return [option.value, option.label, option.targetLabel, option.targetDomain].filter((value) => value !== null && value !== undefined).join(" ");
  }

  function filterAdminDraftSelectOptions(options, query, selectedValue) {
    const safeOptions = Array.isArray(options) ? options.slice() : [];
    const normalizedQuery = normalizeAdminRelationSearchText(query);
    const selectedText = selectedValue === null || selectedValue === undefined ? "" : String(selectedValue);
    const filtered = normalizedQuery
      ? safeOptions.filter((option) => normalizeAdminRelationSearchText(getAdminRelationOptionText(option)).includes(normalizedQuery))
      : safeOptions;
    if (selectedText && !filtered.some((option) => String(option.value) === selectedText)) {
      const selectedOption = safeOptions.find((option) => String(option.value) === selectedText);
      if (selectedOption) filtered.unshift({ ...selectedOption, keepSelected: true });
    }
    return filtered;
  }

  function renderAdminDraftSelectOptionsHtml(options, selectedValue) {
    const selectedText = selectedValue === null || selectedValue === undefined ? "" : String(selectedValue);
    const safeOptions = Array.isArray(options) ? options : [];
    if (!safeOptions.length) {
      return `<option value="${escapeHtml(selectedText)}" selected>${escapeHtml(selectedText ? `${selectedText} · 검색 결과 없음` : "검색 결과 없음")}</option>`;
    }
    return safeOptions.map((option) => {
      const optionValue = option && option.value !== undefined && option.value !== null ? String(option.value) : "";
      const optionLabel = option && option.label ? option.label : optionValue;
      const suffix = option && option.keepSelected ? " · 현재 선택값" : "";
      return `<option value="${escapeHtml(optionValue)}" ${optionValue === selectedText ? "selected" : ""}>${escapeHtml(optionLabel + suffix)}</option>`;
    }).join("");
  }

  function getAdminRelationSelectMetaText(key, domain, query) {
    const definition = getAdminRelationEditOptionDefinition(domain, key);
    if (!definition) return "";
    const allOptions = getAdminDraftRelationOptions(definition) || [];
    const filtered = filterAdminDraftSelectOptions(allOptions, query, "");
    const target = definition.targetLabel || definition.targetDomain || "관계 대상";
    const queryText = normalizeAdminRelationSearchText(query);
    return queryText ? `${target} ${filtered.length}/${allOptions.length}개 표시` : `${target} ${allOptions.length}개 중 선택`;
  }

  function updateAdminRelationOptionMeta(meta, key, domain, query) {
    if (!meta) return;
    const text = getAdminRelationSelectMetaText(key, domain, query);
    meta.textContent = text;
    meta.classList.toggle("warn", !!query && text.includes("0/"));
  }

  function applyAdminRelationOptionFilter(input) {
    if (!input) return false;
    const draft = input.closest("[data-admin-edit-draft]");
    const wrapper = input.closest("[data-admin-relation-select-tools]");
    if (!draft || !wrapper) return false;
    const domain = draft.getAttribute("data-admin-edit-draft-domain") || DEFAULT_MASTER_DOMAIN;
    const key = input.getAttribute("data-admin-relation-option-filter-for") || "";
    const select = wrapper.querySelector(`[data-admin-edit-draft-field="${key}"]`);
    if (!select) return false;
    const selectedValue = select.value;
    const original = parseDraftOriginalValue(select.getAttribute("data-admin-edit-draft-original"));
    const options = getAdminDraftSelectOptions(key, original, domain);
    const filtered = filterAdminDraftSelectOptions(options, input.value, selectedValue);
    select.innerHTML = renderAdminDraftSelectOptionsHtml(filtered, selectedValue);
    select.value = selectedValue;
    updateAdminRelationOptionMeta(wrapper.querySelector("[data-admin-relation-option-meta]"), key, domain, input.value);
    return true;
  }

  function clearAdminRelationOptionFilter(key) {
    const filter = document.querySelector(`[data-admin-relation-option-filter-for="${key}"]`);
    if (!filter) return false;
    filter.value = "";
    return applyAdminRelationOptionFilter(filter);
  }

  function refreshDependentAdminRelationSelects(changedKey) {
    const draft = document.querySelector("[data-admin-edit-draft]");
    if (!draft) return false;
    const domain = draft.getAttribute("data-admin-edit-draft-domain") || DEFAULT_MASTER_DOMAIN;
    const changed = normalizeAdminDraftFieldKey(changedKey);
    let touched = false;
    getAdminRelationEditOptionDefinitions(domain).forEach((definition) => {
      if (!definition || normalizeAdminDraftFieldKey(definition.dependsOn) !== changed) return;
      const fieldName = definition.field;
      const field = draft.querySelector(`[data-admin-edit-draft-field="${fieldName}"]`);
      if (!field) return;
      const previousValue = field.value;
      const options = getAdminDraftRelationOptions(definition) || [];
      let nextValue = "";
      if (options.some((option) => String(option.value) === previousValue)) {
        nextValue = previousValue;
      } else if (options.length) {
        nextValue = String(options[0].value ?? "");
      }
      const wrapper = field.closest("[data-admin-relation-select-tools]");
      const filter = wrapper ? wrapper.querySelector("[data-admin-relation-option-filter]") : null;
      if (filter) filter.value = "";
      field.innerHTML = renderAdminDraftSelectOptionsHtml(options, nextValue);
      field.value = nextValue;
      updateAdminRelationOptionMeta(wrapper && wrapper.querySelector("[data-admin-relation-option-meta]"), fieldName, domain, "");
      touched = true;
    });
    return touched;
  }

  function getAdminDraftFieldInputKind(field, domain) {
    const key = normalizeAdminDraftFieldKey(field && field.key);
    const value = field ? field.value : null;
    const valueText = value === null || value === undefined ? "" : String(value);
    const isLongText = valueText.length > 90 || valueText.includes("\n");
    if (isAdminRelationEditField(domain, key)) return "relation-select";
    if (ADMIN_DRAFT_SELECT_FIELD_OPTIONS[key]) return "preset-select";
    if (ADMIN_DRAFT_BOOLEAN_FIELDS.has(key) || typeof value === "boolean") return "boolean-select";
    if (ADMIN_DRAFT_NUMBER_FIELDS.has(key) || typeof value === "number") return "number";
    if (ADMIN_DRAFT_TEXTAREA_FIELDS.has(key) || isLongText) return "textarea";
    return "text";
  }

  function getAdminDraftFieldTypeLabel(kind) {
    if (kind === "boolean-select") return "true/false select";
    if (kind === "preset-select") return "preset select";
    if (kind === "relation-select") return "relation select";
    if (kind === "number") return "number input";
    if (kind === "textarea") return "textarea";
    return "text input";
  }

  function getAdminDraftLockedReason(key) {
    const normalized = normalizeAdminDraftFieldKey(key);
    if (normalized === "id" || normalized === "code") return "식별자 필드라 잠금";
    if (normalized.endsWith("_id") || normalized.endsWith("_code")) return "관계/연결 필드라 잠금";
    if (normalized.endsWith("_json")) return "JSON 원본 필드는 아직 편집 막음";
    if (normalized === "created_at" || normalized === "updated_at" || normalized === "createdat" || normalized === "updatedat") return "자동 시간 필드라 잠금";
    return "allow-list 밖이라 잠금";
  }

  function renderAdminDraftTypeBadge(kind) {
    const label = getAdminDraftFieldTypeLabel(kind);
    const tone = kind === "boolean-select" || kind === "preset-select" ? "good" : (kind === "relation-select" || kind === "number" ? "warn" : "");
    return `<span class="pill ${escapeHtml(tone)}">${escapeHtml(label)}</span>`;
  }

  function getAdminDraftFieldRisk(domain, key) {
    const rawDomain = String(domain || "");
    const normalized = normalizeAdminDraftFieldKey(key).replace(/_/g, "");
    if (rawDomain === "itemTemplates" && ["stackable", "itemtype", "equipslot", "enhancegroupcode"].includes(normalized)) return "high";
    if (rawDomain === "bosses" && ["hp", "isenabled"].includes(normalized)) return "high";
    if (rawDomain === "skills" && ["slotkey", "procrate", "cooldownseconds"].includes(normalized)) return "high";
    if (rawDomain === "skillLevels" && ["skillcode", "level", "damagemultiplier", "procratebonus"].includes(normalized)) return "high";
    if (rawDomain === "dropTables" && ["ownertype", "ownercode"].includes(normalized)) return "high";
    if (rawDomain === "dropTableItems" && ["droptablecode", "itemtemplatecode", "rate", "minquantity", "maxquantity"].includes(normalized)) return "high";
    if (rawDomain === "enhancementLevels" && ["groupcode", "fromlevel", "successrate", "goldcost"].includes(normalized)) return "high";
    if (rawDomain === "characterSkills" && ["charactercode", "skillcode"].includes(normalized)) return "high";
    if (["grade", "bosstype", "ownertype", "tier", "sortorder", "enemyhp", "goldreward", "maxlevel", "tolevel", "isdefault"].includes(normalized)) return "medium";
    if (["adminnote", "description"].includes(normalized)) return "low";
    return "medium";
  }

  function renderAdminDraftRiskBadge(domain, key) {
    const risk = getAdminDraftFieldRisk(domain, key);
    const tone = risk === "high" ? "blocked" : (risk === "medium" ? "warn" : "good");
    return `<span class="pill ${escapeHtml(tone)}">risk ${escapeHtml(risk)}</span>`;
  }

  function renderAdminDraftLockedFields(lockedFields) {
    const safeFields = Array.isArray(lockedFields) ? lockedFields : [];
    if (!safeFields.length) return "";
    const visibleFields = safeFields.slice(0, ADMIN_DRAFT_VISIBLE_LOCKED_LIMIT);
    const hiddenCount = Math.max(0, safeFields.length - visibleFields.length);
    return `
      <div class="locked-field-panel" data-admin-edit-locked-fields>
        <div class="locked-field-title">
          <span>읽기 전용/잠금 필드</span>
          <span class="pill blocked">수정 불가 ${escapeHtml(formatValue(safeFields.length))}</span>
        </div>
        <div class="filter-help">아래 필드는 화면에 보이지만 실수 방지를 위해 입력칸을 만들지 않았습니다. 코드/연결값/JSON/시간값은 아직 관리자에서 직접 수정하지 않는 쪽이 안전합니다.</div>
        <div class="locked-field-grid">
          ${visibleFields.map((field) => {
            const reason = getAdminDraftLockedReason(field.key);
            return `
              <div class="locked-field-card">
                <strong>${escapeHtml(field.label || field.key)}</strong>
                <span>${escapeHtml(formatValue(field.value))}</span>
                <em>${escapeHtml(reason)}</em>
              </div>
            `;
          }).join("")}
        </div>
        ${hiddenCount ? `<div class="filter-help">잠금 필드 ${escapeHtml(formatValue(hiddenCount))}개는 너무 많아서 일부만 표시했습니다.</div>` : ""}
      </div>
    `;
  }

  function makeDraftOriginalValue(value) {
    try {
      return JSON.stringify(value);
    } catch (error) {
      return JSON.stringify(formatValue(value));
    }
  }

  function parseDraftOriginalValue(value) {
    try {
      return JSON.parse(value || "null");
    } catch (error) {
      return value;
    }
  }

  function renderAdminDraftControl(field, kind, domain) {
    const value = field ? field.value : null;
    const valueText = value === null || value === undefined ? "" : String(value);
    const original = makeDraftOriginalValue(value);
    const key = field ? field.key : "";
    const commonAttrs = `data-admin-edit-draft-field="${escapeHtml(key)}" data-admin-edit-draft-original="${escapeHtml(original)}"`;
    if (kind === "boolean-select") {
      const normalized = value === true || String(value).toLowerCase() === "true" ? "true" : "false";
      return `
        <select ${commonAttrs} data-admin-edit-draft-value-type="boolean" aria-label="${escapeHtml(field.label || key)} true false 선택">
          <option value="true" ${normalized === "true" ? "selected" : ""}>true · 켜짐</option>
          <option value="false" ${normalized === "false" ? "selected" : ""}>false · 꺼짐</option>
        </select>
      `;
    }
    if (kind === "preset-select") {
      const options = getAdminDraftSelectOptions(key, value, domain);
      return `
        <select ${commonAttrs} data-admin-edit-draft-value-type="text" aria-label="${escapeHtml(field.label || key)} 선택">
          ${renderAdminDraftSelectOptionsHtml(options, valueText)}
        </select>
      `;
    }
    if (kind === "relation-select") {
      const options = getAdminDraftSelectOptions(key, value, domain);
      const definition = getAdminRelationEditOptionDefinition(domain, key) || {};
      const metaText = getAdminRelationSelectMetaText(key, domain, "");
      return `
        <div class="relation-select-tools" data-admin-relation-select-tools>
          <input class="relation-option-filter" data-admin-relation-option-filter data-admin-relation-option-filter-for="${escapeHtml(key)}" type="text" placeholder="코드/이름으로 후보 검색" autocomplete="off" aria-label="${escapeHtml(field.label || key)} 후보 검색" />
          <select ${commonAttrs} data-admin-edit-draft-value-type="text" aria-label="${escapeHtml(field.label || key)} 선택">
            ${renderAdminDraftSelectOptionsHtml(options, valueText)}
          </select>
          <div class="relation-option-meta" data-admin-relation-option-meta>${escapeHtml(metaText || (definition.targetLabel ? `${definition.targetLabel} 후보` : "관계 후보"))}</div>
        </div>
      `;
    }
    if (kind === "number") {
      return `<input type="number" inputmode="decimal" step="any" value="${escapeHtml(valueText)}" ${commonAttrs} data-admin-edit-draft-value-type="number" />`;
    }
    if (kind === "textarea") {
      const rows = ADMIN_DRAFT_TEXTAREA_FIELDS.has(normalizeAdminDraftFieldKey(key)) ? 4 : 3;
      return `<textarea rows="${rows}" ${commonAttrs} data-admin-edit-draft-value-type="text">${escapeHtml(valueText)}</textarea>`;
    }
    return `<input type="text" value="${escapeHtml(valueText)}" ${commonAttrs} data-admin-edit-draft-value-type="text" />`;
  }

  function getAdminRelationComboGuardLabels(domain) {
    return getAdminRelationEditOptionDefinitions(domain)
      .filter((definition) => definition && definition.allowApply && Array.isArray(definition.comboGuard) && definition.comboGuard.length)
      .map((definition) => definition.comboGuard.join(" + "))
      .filter((value, index, list) => value && list.indexOf(value) === index);
  }

  function renderAdminRelationEditOptionsNote(domain) {
    const definitions = getAdminRelationEditOptionDefinitions(domain).filter((definition) => definition && definition.allowApply);
    if (!definitions.length) return "";
    const labels = definitions.map((definition) => `${definition.field} → ${definition.targetLabel || definition.targetDomain || "대상"}`).join(", ");
    const comboLabels = getAdminRelationComboGuardLabels(domain);
    const comboLine = comboLabels.length ? `<br><span><strong>중복 조합 검사:</strong> ${escapeHtml(comboLabels.join(", "))}</span>` : "";
    return `<div class="relation-edit-note"><span class="pill warn">relation select</span> ${escapeHtml(labels)}<br><span>${escapeHtml("관계 필드는 직접 텍스트 입력이 아니라 실제 존재하는 대상 목록에서 선택하고, 백엔드가 적용 직전에 대상 존재 여부를 다시 검사합니다.")}</span>${comboLine}</div>`;
  }

  function renderMasterEditDraft(detail, fields) {
    const safeFields = Array.isArray(fields) ? fields : [];
    const domain = detail && detail.domain ? detail.domain : DEFAULT_MASTER_DOMAIN;
    const candidateFields = safeFields.filter((field) => !fieldKeyLooksReadOnly(domain, field.key));
    const editableCandidateFields = candidateFields.filter((field) => isAdminEditApplyAllowedField(domain, field.key));
    const editableFields = editableCandidateFields.slice(0, 14);
    const lockedFields = candidateFields.filter((field) => !isAdminEditApplyAllowedField(domain, field.key));
    const editableOverflowCount = Math.max(0, editableCandidateFields.length - editableFields.length);
    const rows = editableFields.length ? editableFields.map((field) => {
      const value = field.value;
      const kind = getAdminDraftFieldInputKind(field, domain);
      const label = field.label || field.key;
      return `
        <label class="draft-field draft-field-${escapeHtml(kind)}">
          <span class="draft-field-heading">
            <span>${escapeHtml(label)}${renderFieldHelpBadge(field.key)}</span>
            <span class="draft-field-badges">${renderAdminDraftTypeBadge(kind)}${renderAdminDraftRiskBadge(domain, field.key)}</span>
          </span>
          ${renderFieldHelpInline(field.key)}
          ${renderFieldValueHintInline(field.key, value)}
          ${renderAdminDraftControl(field, kind, domain)}
        </label>
      `;
    }).join("") : `<div class="empty">이 도메인에서 실제 적용까지 열어둔 일반 필드가 없습니다.</div>`;

    return `
      <div class="detail-card edit-draft-card" data-admin-edit-draft data-admin-edit-draft-domain="${escapeHtml(domain || "")}" data-admin-edit-draft-id="${escapeHtml(detail.id || "")}">
        <div class="detail-title">관리자 편집 초안 <span class="pill warn">guarded apply</span><span class="pill good">typed inputs</span><span class="pill good">change log</span></div>
        <div class="filter-help">allow-list 필드는 실제 DB 적용까지 가능합니다. 입력 실수를 줄이기 위해 boolean은 <strong>true/false select</strong>, enum 성격 필드는 <strong>preset select</strong>, number는 <strong>number input</strong>, description/admin_note는 <strong>textarea</strong>로 표시합니다.</div>
        <div class="filter-help">먼저 <strong>초안 검증</strong>으로 오류가 없는지 확인한 뒤, dev key와 확인 문구 <code>${escapeHtml(ADMIN_EDIT_APPLY_CONFIRM_TEXT)}</code>를 정확히 입력해야 적용됩니다. 적용 직전에는 편집 화면을 열었을 때의 기준값과 현재 DB 값이 같은지도 한 번 더 검사합니다.</div>
        <div class="filter-help">실제 적용 가능 필드: ${escapeHtml(getAdminEditAllowedFields(domain).join(", ") || "없음")}</div>
        ${renderAdminRelationEditOptionsNote(domain)}
        <div class="edit-draft-grid">${rows}</div>
        ${editableOverflowCount ? `<div class="filter-help">표시 제한으로 실제 적용 가능 필드 ${escapeHtml(formatValue(editableOverflowCount))}개는 편집 초안에서 제외했습니다.</div>` : ""}
        ${renderAdminDraftLockedFields(lockedFields)}
        <div class="edit-draft-review" data-admin-edit-review>
          <div class="draft-review-banner draft-review-empty">
            <span class="pill good">변경 0</span>
            <span>값을 바꾸면 적용 직전 비교표가 여기에 표시됩니다.</span>
          </div>
        </div>
        <div class="edit-draft-impact" data-admin-edit-impact><div class="empty">값을 바꾸면 여기에 <strong>인게임 영향 안내</strong>가 표시됩니다.</div></div>
        <div class="edit-draft-actions">
          <button class="btn mini primary" type="button" data-admin-action="preview-admin-edit-draft">초안 검증</button>
          <button class="btn mini" type="button" data-admin-action="reset-admin-edit-draft">원래 값으로 되돌리기</button>
          <label class="apply-confirm-field"><span>확인 문구</span><input type="text" data-admin-edit-apply-confirm placeholder="${escapeHtml(ADMIN_EDIT_APPLY_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>고위험 확인</span><input type="text" data-admin-edit-risk-confirm placeholder="${escapeHtml(ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>변경 사유</span><input type="text" data-admin-edit-apply-reason placeholder="예: 보스 HP 밸런스 조정" autocomplete="off" /></label>
          <button class="btn mini danger" type="button" data-admin-action="apply-admin-edit-draft">검증 후 실제 적용</button>
          <span class="pill warn">DB write: dev-key guarded</span>
          <span class="pill good">stale guard</span>
        </div>
        <div class="edit-draft-result" data-admin-edit-draft-result><div class="empty">값을 바꾼 뒤 <strong>초안 검증</strong>을 누르세요. 실제 적용은 확인 문구가 맞고 검증 오류가 없을 때만 됩니다.</div></div>
      </div>
    `;
  }

  function readAdminEditDraftValues() {
    const draft = $(`[data-admin-edit-draft]`);
    if (!draft) return { ok: false, reason: "draft_missing", draft: {} };
    const fields = Array.from(draft.querySelectorAll("[data-admin-edit-draft-field]"));
    const values = {};
    const originals = {};
    fields.forEach((field) => {
      const key = field.getAttribute("data-admin-edit-draft-field");
      if (!key) return;
      const type = field.getAttribute("data-admin-edit-draft-value-type") || "text";
      const original = parseDraftOriginalValue(field.getAttribute("data-admin-edit-draft-original"));
      originals[key] = original;
      if (type === "boolean") values[key] = field.value === "true";
      else values[key] = field.value;
    });
    return {
      ok: true,
      domain: draft.getAttribute("data-admin-edit-draft-domain") || DEFAULT_MASTER_DOMAIN,
      id: Number(draft.getAttribute("data-admin-edit-draft-id") || 0),
      draft: values,
      originals,
      fieldCount: fields.length,
    };
  }

  function resetAdminEditDraft() {
    const draft = $(`[data-admin-edit-draft]`);
    if (!draft) return false;
    Array.from(draft.querySelectorAll("[data-admin-edit-draft-field]")).forEach((field) => {
      const type = field.getAttribute("data-admin-edit-draft-value-type") || "text";
      const original = parseDraftOriginalValue(field.getAttribute("data-admin-edit-draft-original"));
      if (type === "boolean") field.value = original ? "true" : "false";
      else field.value = original === null || original === undefined ? "" : String(original);
    });
    const riskConfirm = $(`[data-admin-edit-risk-confirm]`);
    if (riskConfirm) riskConfirm.value = "";
    const result = $(`[data-admin-edit-draft-result]`);
    if (result) result.innerHTML = `<div class="empty">원래 값으로 되돌렸습니다. 값을 바꾼 뒤 초안 검증을 누르세요.</div>`;
    refreshAdminEditReviewAndImpact();
    setStatus("편집 초안을 원래 값으로 되돌렸습니다.", "ok");
    return true;
  }

  function valuesEqualForImpact(before, after) {
    if (before === after) return true;
    if (before === null || before === undefined) return after === "" || after === null || after === undefined;
    if (typeof before === "number") return Number(after) === before;
    if (typeof before === "boolean") return after === before || String(after).toLowerCase() === String(before);
    return String(before) === String(after);
  }

  function collectLocalDraftChangesForImpact(values) {
    const result = values || readAdminEditDraftValues();
    if (!result || !result.ok) return [];
    return Object.keys(result.draft || {}).filter((key) => !valuesEqualForImpact(result.originals[key], result.draft[key])).map((key) => ({
      key,
      label: key,
      before: result.originals[key],
      after: result.draft[key],
      domain: result.domain,
    }));
  }

  function getAdminRiskSortWeight(risk) {
    if (risk === "high") return 0;
    if (risk === "medium") return 1;
    if (risk === "low") return 2;
    return 3;
  }

  function sortAdminChangesByRisk(domain, changes) {
    return (Array.isArray(changes) ? changes.slice() : []).sort((a, b) => {
      const riskA = getAdminDraftFieldRisk(domain || a.domain, a.key);
      const riskB = getAdminDraftFieldRisk(domain || b.domain, b.key);
      const riskDiff = getAdminRiskSortWeight(riskA) - getAdminRiskSortWeight(riskB);
      if (riskDiff) return riskDiff;
      return String(a.key || "").localeCompare(String(b.key || ""));
    });
  }

  function getAdminRelationOptionDisplayText(option, value) {
    const valueText = value === null || value === undefined ? "" : String(value);
    if (!option) return formatValue(value);
    const label = String(option.label || option.targetLabel || option.value || valueText || "");
    if (!valueText) return label || "-";
    if (label === valueText || label.startsWith(`${valueText} ·`)) return label;
    return `${valueText} · ${label}`;
  }

  function getAdminRelationValueDisplay(domain, key, value, contextValues) {
    const definition = getAdminRelationEditOptionDefinition(domain, key);
    if (!definition) return formatValue(value);
    const valueText = value === null || value === undefined ? "" : String(value);
    const options = getAdminDraftRelationOptionsForValues(definition, contextValues || {}) || [];
    const option = options.find((candidate) => String(candidate.value ?? "") === valueText);
    return getAdminRelationOptionDisplayText(option, value);
  }

  function getAdminRelationOpenTarget(domain, key, value, contextValues) {
    const definition = getAdminRelationEditOptionDefinition(domain, key);
    if (!definition) return null;
    const valueText = value === null || value === undefined ? "" : String(value).trim();
    if (!valueText) return null;
    if (domain === "dropTables" && key === "owner_type") return null;
    let targetDomain = definition.targetDomain || "";
    if (definition.optionGroups && definition.dependsOn) {
      const dependencyValue = contextValues && Object.prototype.hasOwnProperty.call(contextValues, definition.dependsOn) ? String(contextValues[definition.dependsOn] || "") : getAdminDraftRelationOptionGroupKey(definition);
      if (domain === "dropTables" && key === "owner_code") targetDomain = dependencyValue === "field" ? "fieldZones" : "bosses";
    }
    if (!targetDomain || targetDomain.includes("/")) return null;
    return { domain: targetDomain, code: valueText };
  }

  function renderAdminRelationOpenButton(domain, key, value, contextValues) {
    const target = getAdminRelationOpenTarget(domain, key, value, contextValues);
    if (!target) return "";
    return `<button class="btn mini relation-jump-btn" type="button" data-admin-action="open-master-detail-by-code" data-admin-detail-domain="${escapeHtml(target.domain)}" data-admin-detail-code="${escapeHtml(target.code)}">대상 열기</button>`;
  }

  function getAdminChangeRelationInfo(change, side) {
    const relation = change && change.relation ? change.relation : null;
    if (!relation) return null;
    if (side && relation[side]) return relation[side];
    if (side === "after" && (relation.targetLabel || relation.targetDomain || relation.targetCode)) return relation;
    return null;
  }

  function formatAdminRelationInfoText(info, rawValue) {
    if (!info) return null;
    if (info.displayText !== undefined && info.displayText !== null && String(info.displayText) !== "") return String(info.displayText);
    const valueText = formatValue(rawValue);
    const label = info.targetLabel !== undefined && info.targetLabel !== null ? String(info.targetLabel) : "";
    if (!label || label === valueText) return valueText;
    return `${valueText} · ${label}`;
  }

  function getAdminRelationOpenTargetFromChange(domain, key, rawValue, contextValues, change, side) {
    if (domain === "dropTables" && key === "owner_type") return null;
    const info = getAdminChangeRelationInfo(change, side);
    if (info && info.targetDomain && !String(info.targetDomain).includes("/")) {
      const code = info.targetCode !== undefined && info.targetCode !== null ? String(info.targetCode).trim() : String(rawValue || "").trim();
      if (code) return { domain: String(info.targetDomain), code };
    }
    return isAdminRelationEditField(domain, key) ? getAdminRelationOpenTarget(domain, key, rawValue, contextValues) : null;
  }

  function renderAdminRelationOpenTargetButton(target) {
    if (!target) return "";
    return `<button class="btn mini relation-jump-btn" type="button" data-admin-action="open-master-detail-by-code" data-admin-detail-domain="${escapeHtml(target.domain)}" data-admin-detail-code="${escapeHtml(target.code)}">대상 열기</button>`;
  }

  function formatAdminChangeValueText(domain, change, side, contextValues) {
    const key = change && change.key;
    const rawValue = side === "before" ? change && change.before : change && change.after;
    const relationText = formatAdminRelationInfoText(getAdminChangeRelationInfo(change, side), rawValue);
    if (relationText !== null) return relationText;
    if (isAdminRelationEditField(domain, key)) return getAdminRelationValueDisplay(domain, key, rawValue, contextValues);
    return formatValue(rawValue);
  }

  function renderAdminChangeValueCell(domain, change, side, contextValues) {
    const text = formatAdminChangeValueText(domain, change, side, contextValues);
    const key = change && change.key;
    const rawValue = side === "before" ? change && change.before : change && change.after;
    const target = getAdminRelationOpenTargetFromChange(domain, key, rawValue, contextValues, change, side);
    const button = renderAdminRelationOpenTargetButton(target);
    return `<div class="relation-value-cell"><span>${escapeHtml(text)}</span>${button}</div>`;
  }

  function renderAdminRollbackMismatchValueCell(domain, item, valueKey) {
    const relation = item && item.relation ? item.relation : null;
    const rawValue = item ? item[valueKey] : undefined;
    const info = relation && relation[valueKey] ? relation[valueKey] : null;
    const text = formatAdminRelationInfoText(info, rawValue) || formatValue(rawValue);
    const target = info && info.targetDomain && !String(info.targetDomain).includes("/") && info.targetCode ? { domain: String(info.targetDomain), code: String(info.targetCode) } : null;
    return `<div class="relation-value-cell"><span>${escapeHtml(text)}</span>${renderAdminRelationOpenTargetButton(target)}</div>`;
  }

  function formatAdminChangeAfterValue(change) {
    return formatAdminChangeValueText(change && change.domain, change, "after", change || {});
  }


  function buildAdminEditDraftReview(values) {
    const result = values || readAdminEditDraftValues();
    if (!result || !result.ok) {
      return { ok: false, domain: DEFAULT_MASTER_DOMAIN, changes: [], changeCount: 0, highCount: 0, mediumCount: 0, lowCount: 0 };
    }
    const changes = sortAdminChangesByRisk(result.domain, collectLocalDraftChangesForImpact(result)).map((change) => {
      const risk = getAdminDraftFieldRisk(result.domain, change.key);
      const relation = isAdminRelationEditField(result.domain, change.key);
      return { ...change, risk, relation };
    });
    return {
      ok: true,
      version: VERSION,
      domain: result.domain,
      id: result.id,
      changes,
      changeCount: changes.length,
      relationCount: changes.filter((change) => change.relation).length,
      highCount: changes.filter((change) => change.risk === "high").length,
      mediumCount: changes.filter((change) => change.risk === "medium").length,
      lowCount: changes.filter((change) => change.risk === "low").length,
    };
  }

  function renderAdminEditDraftReview(review) {
    const target = $(`[data-admin-edit-review]`);
    if (!target) return;
    const info = review || buildAdminEditDraftReview();
    if (!info.changeCount) {
      target.innerHTML = `
        <div class="draft-review-banner draft-review-empty">
          <span class="pill good">변경 0</span>
          <span>값을 바꾸면 적용 직전 비교표가 여기에 표시됩니다.</span>
        </div>
      `;
      return;
    }
    const rows = info.changes.map((change) => {
      const beforeContext = { ...Object.fromEntries(info.changes.map((item) => [item.key, item.before])), [change.key]: change.before };
      const afterContext = { ...Object.fromEntries(info.changes.map((item) => [item.key, item.after])), [change.key]: change.after };
      return `
        <tr class="draft-review-row-${escapeHtml(change.risk)}">
          <td>${escapeHtml(change.label || change.key)}${change.relation ? ` <span class="pill warn">relation</span>` : ""}</td>
          <td><span class="pill ${change.risk === "high" ? "blocked" : (change.risk === "medium" ? "warn" : "good")}">${escapeHtml(change.risk)}</span></td>
          <td>${renderAdminChangeValueCell(info.domain, change, "before", beforeContext)}</td>
          <td>${renderAdminChangeValueCell(info.domain, change, "after", afterContext)}</td>
        </tr>
      `;
    }).join("");
    target.innerHTML = `
      <div class="draft-review-banner ${info.highCount ? "draft-review-danger" : ""}">
        <span class="pill ${info.highCount ? "blocked" : "good"}">변경 ${escapeHtml(formatValue(info.changeCount))}</span>
        <span class="pill ${info.highCount ? "blocked" : "good"}">high ${escapeHtml(formatValue(info.highCount))}</span>
        <span class="pill ${info.mediumCount ? "warn" : "good"}">medium ${escapeHtml(formatValue(info.mediumCount))}</span>
        <span class="pill good">low ${escapeHtml(formatValue(info.lowCount))}</span>
        <span class="pill ${info.relationCount ? "warn" : "good"}">relation ${escapeHtml(formatValue(info.relationCount || 0))}</span>
        ${info.highCount ? `<span class="pill blocked">고위험 변경은 ${escapeHtml(ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT)} 추가 입력 필요</span>` : ""}
      </div>
      <div class="table-wrap relation-table-wrap draft-review-table-wrap">
        <table>
          <thead><tr><th>필드</th><th>위험도</th><th>현재 기준값</th><th>초안 값</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
  }

  function refreshAdminEditReviewAndImpact() {
    const values = readAdminEditDraftValues();
    if (!values.ok) return null;
    const review = buildAdminEditDraftReview(values);
    renderAdminEditDraftReview(review);
    const guide = buildAdminEditImpactGuide(values.domain, review.changes);
    renderAdminEditImpactGuide(guide);
    return { review, guide };
  }

  function normalizeImpactKey(key) {
    return String(key || "").replace(/[^a-zA-Z0-9]/g, "").toLowerCase();
  }

  function getAdminEditImpactHint(domain, change) {
    const key = normalizeImpactKey(change && change.key);
    const rawDomain = String(domain || (change && change.domain) || "");
    const before = change ? change.before : undefined;
    const after = change ? change.after : undefined;
    if (!key) return null;

    if (rawDomain === "itemTemplates" && key === "stackable") {
      return {
        severity: "high",
        title: "인벤토리 겹치기 동작 변경",
        body: `stackable ${formatValue(before)} → ${formatValue(after)} 변경은 새로 획득하는 같은 +0 아이템의 겹치기 여부에 영향을 줍니다. 기존 세이브에 이미 따로 들어간 아이템은 자동 병합하지 않습니다. 겹친 장비를 강화할 때는 1개 분리용 빈 칸이 필요합니다.`,
        reload: true,
      };
    }
    if (rawDomain === "itemTemplates" && ["itemtype", "equipslot"].includes(key)) {
      return {
        severity: "high",
        title: "아이템 분류/장착 슬롯 변경",
        body: `${change.label || change.key} 변경은 인벤토리 분류, 장착 위치, 드랍 표시, 향후 강화/필터 규칙에 영향을 줄 수 있습니다. 변경 후 신규 획득/장착/툴팁을 꼭 확인하세요.`,
        reload: true,
      };
    }
    if (rawDomain === "itemTemplates" && key === "enhancegroupcode") {
      return {
        severity: "high",
        title: "아이템 강화 그룹 연결 변경",
        body: `enhance_group_code ${formatValue(before)} → ${formatValue(after)} 변경은 이 아이템이 사용하는 강화 확률/비용/결과 단계에 직접 영향을 줍니다. 적용 전 연결 항목에서 강화 그룹과 단계를 확인하세요.`,
        reload: true,
      };
    }
    if (rawDomain === "itemTemplates" && ["name", "description", "grade"].includes(key)) {
      return {
        severity: "medium",
        title: "아이템 표시/구간 정보 변경",
        body: `${change.label || change.key} 변경은 드랍 목록, 툴팁, 관리자 목록, 일부 정렬/구간 판단에 영향을 줄 수 있습니다. 게임 화면은 새로고침 후 최신 master-data를 다시 읽습니다.`,
        reload: true,
      };
    }
    if (rawDomain === "itemTemplates" && key === "adminnote") {
      return {
        severity: "low",
        title: "관리자 메모만 변경",
        body: "admin_note는 게임 화면에는 표시되지 않는 내부 메모입니다. 인게임 밸런스에는 직접 영향이 없습니다.",
        reload: false,
      };
    }

    if (rawDomain === "bosses" && key === "hp") {
      return {
        severity: "high",
        title: "보스 체력 변경",
        body: `보스 HP ${formatValue(before)} → ${formatValue(after)} 변경은 보스 전투의 최대 체력에 직접 반영됩니다. 이미 떠 있는 게임 화면은 새로고침 후 최신 값을 읽습니다.`,
        reload: true,
      };
    }
    if (rawDomain === "bosses" && ["name", "description", "boss_type", "tier", "cooldown_seconds"].includes(key)) {
      return {
        severity: "medium",
        title: "보스 표시/소환 규칙 변경",
        body: `${change.label || change.key} 변경은 보스 카드, 전투 표시, 쿨타임/구간 정보에 영향을 줄 수 있습니다. 적용 후 게임 새로고침을 권장합니다.`,
        reload: true,
      };
    }
    if (rawDomain === "bosses" && key === "isenabled") {
      return {
        severity: "high",
        title: "보스 활성 상태 변경",
        body: "is_enabled 변경은 보스가 게임 기준 데이터에 포함되는지 여부에 영향을 줄 수 있습니다. 비활성화 전에는 드랍/퀘스트 연결 상태를 확인하는 편이 안전합니다.",
        reload: true,
      };
    }

    if (rawDomain === "fieldZones" && ["enemyhp", "goldreward"].includes(key)) {
      return {
        severity: "high",
        title: "필드 사냥 보상/난이도 변경",
        body: `${change.label || change.key} 변경은 필드 몬스터 체력 또는 골드 보상에 직접 영향을 줍니다. 게임 새로고침 후 적용됩니다.`,
        reload: true,
      };
    }
    if (rawDomain === "fieldZones" && ["name", "description", "sortorder", "isenabled"].includes(key)) {
      return {
        severity: "medium",
        title: "필드 표시/노출 변경",
        body: `${change.label || change.key} 변경은 필드 목록 표시와 진입 가능 상태에 영향을 줄 수 있습니다.`,
        reload: true,
      };
    }

    if (rawDomain === "skills" && key === "slotkey") {
      return {
        severity: "high",
        title: "스킬 슬롯 배치 변경",
        body: "slot_key 변경은 Q/W/E/R/T/F/D/M 또는 각성 슬롯 배치에 영향을 줍니다. 같은 슬롯이 중복되지 않는지, 게임 화면에서 스킬 버튼이 의도대로 보이는지 확인해야 합니다.",
        reload: true,
      };
    }
    if (rawDomain === "skills" && ["procrate", "cooldownseconds"].includes(key)) {
      return {
        severity: "high",
        title: "스킬 발동/쿨타임 변경",
        body: `${change.label || change.key} 변경은 전투 스킬 발동 확률 또는 쿨타임에 영향을 줍니다. 게임 새로고침 후 최신 master-data가 적용됩니다.`,
        reload: true,
      };
    }
    if (rawDomain === "skillLevels" && ["skillcode", "level"].includes(key)) {
      return {
        severity: "high",
        title: "스킬 레벨 조합 변경",
        body: `${change.label || change.key} 변경은 어떤 스킬의 몇 레벨 규칙인지 바꿉니다. 백엔드가 skill_code + level 중복을 차단하지만, 적용 후 스킬 강화 화면을 확인하세요.`,
        reload: true,
      };
    }
    if (rawDomain === "skillLevels" && ["damagemultiplier", "procratebonus"].includes(key)) {
      return {
        severity: "high",
        title: "스킬 레벨 효과 변경",
        body: `${change.label || change.key} 변경은 스킬 레벨별 피해량/발동 보너스에 영향을 줍니다.`,
        reload: true,
      };
    }
    if (rawDomain === "dropTableItems" && key === "droptablecode") {
      return {
        severity: "high",
        title: "드랍 테이블 연결 변경",
        body: `drop_table_code ${formatValue(before)} → ${formatValue(after)} 변경은 이 드랍 아이템 행이 어느 보스/필드 드랍 묶음에 속하는지 바꿉니다.`,
        reload: true,
      };
    }
    if (rawDomain === "dropTableItems" && key === "itemtemplatecode") {
      return {
        severity: "high",
        title: "드랍 아이템 연결 변경",
        body: `item_template_code ${formatValue(before)} → ${formatValue(after)} 변경은 해당 드랍 테이블에서 실제로 떨어지는 아이템을 바꿉니다. 확률/수량과 함께 게임 드랍 결과를 꼭 확인하세요.`,
        reload: true,
      };
    }
    if (rawDomain === "dropTableItems" && ["rate", "minquantity", "maxquantity"].includes(key)) {
      return {
        severity: "high",
        title: "드랍 확률/수량 변경",
        body: `${change.label || change.key} 변경은 보스/필드 드랍 결과에 직접 영향을 줍니다. 너무 높은 rate나 수량은 밸런스가 크게 바뀔 수 있습니다.`,
        reload: true,
      };
    }
    if (rawDomain === "dropTables" && key === "ownertype") {
      return {
        severity: "high",
        title: "드랍 테이블 대상 종류 변경",
        body: "owner_type 변경은 같은 owner_code를 보스 코드로 볼지 필드 코드로 볼지 바꿉니다. owner_code 후보 목록이 타입에 맞게 자동 전환되고, 백엔드가 존재 여부를 다시 검사합니다.",
        reload: true,
      };
    }
    if (rawDomain === "dropTables" && key === "ownercode") {
      return {
        severity: "high",
        title: "드랍 테이블 소유자 변경",
        body: "owner_code를 바꾸면 이 드랍 테이블이 연결되는 보스/필드가 바뀝니다. 적용 후 관계 보기에서 대상 보스/필드를 확인하세요.",
        reload: true,
      };
    }
    if (rawDomain === "enhancementLevels" && ["groupcode", "fromlevel"].includes(key)) {
      return {
        severity: "high",
        title: "강화 단계 조합 변경",
        body: `${change.label || change.key} 변경은 어떤 강화 그룹의 어느 단계 규칙인지 바꿉니다. 백엔드가 group_code + from_level 중복을 차단하지만, 적용 후 강화 단계 관계를 확인하세요.`,
        reload: true,
      };
    }
    if (rawDomain === "enhancementLevels" && ["successrate", "goldcost"].includes(key)) {
      return {
        severity: "high",
        title: "강화 확률/비용 변경",
        body: `${change.label || change.key} 변경은 강화 난이도와 골드 소모량에 직접 영향을 줍니다.`,
        reload: true,
      };
    }
    if (rawDomain === "characterSkills" && ["charactercode", "skillcode"].includes(key)) {
      return {
        severity: "high",
        title: "캐릭터 스킬 연결 변경",
        body: `${change.label || change.key} 변경은 캐릭터가 어떤 스킬을 기본 연결로 갖는지 바꿉니다. 백엔드가 character_code + skill_code 중복을 차단합니다.`,
        reload: true,
      };
    }
    if (rawDomain === "enhancementGroups" && ["name", "description", "maxlevel", "isenabled"].includes(key)) {
      return {
        severity: "medium",
        title: "강화 그룹 설정 변경",
        body: `${change.label || change.key} 변경은 해당 그룹을 쓰는 장비들의 강화 표시/최대 단계에 영향을 줄 수 있습니다.`,
        reload: true,
      };
    }
    if (["name", "description", "isenabled"].includes(key)) {
      return {
        severity: key === "isenabled" ? "medium" : "low",
        title: "표시/활성 상태 변경",
        body: `${change.label || change.key} 변경은 화면 표시 또는 데이터 활성 상태에 영향을 줄 수 있습니다.`,
        reload: key === "isenabled",
      };
    }
    return {
      severity: "low",
      title: "일반 마스터 데이터 변경",
      body: `${change.label || change.key} 값이 변경됩니다. 인게임 반영은 이 필드를 사용하는 화면/시스템에서 새로고침 후 확인하세요.`,
      reload: true,
    };
  }

  function buildAdminEditImpactGuide(domain, changes, options) {
    const safeChanges = Array.isArray(changes) ? changes : [];
    const hints = safeChanges.map((change) => getAdminEditImpactHint(domain, change)).filter(Boolean);
    const requiresGameReload = hints.some((hint) => hint.reload);
    const highCount = hints.filter((hint) => hint.severity === "high").length;
    const mediumCount = hints.filter((hint) => hint.severity === "medium").length;
    return {
      ok: true,
      version: VERSION,
      domain: domain || DEFAULT_MASTER_DOMAIN,
      changeCount: safeChanges.length,
      hintCount: hints.length,
      highCount,
      mediumCount,
      requiresGameReload,
      applied: !!(options && options.applied),
      hints,
    };
  }

  function renderAdminEditImpactGuide(guide) {
    const target = $(`[data-admin-edit-impact]`);
    if (!target) return;
    const info = guide || buildAdminEditImpactGuide(DEFAULT_MASTER_DOMAIN, []);
    if (!info.changeCount) {
      target.innerHTML = `<div class="empty">값을 바꾸면 여기에 <strong>인게임 영향 안내</strong>가 표시됩니다.</div>`;
      return;
    }
    const rows = info.hints.map((hint) => `
      <div class="impact-row impact-${escapeHtml(hint.severity)}">
        <span class="pill ${hint.severity === "high" ? "blocked" : (hint.severity === "medium" ? "warn" : "good")}">${escapeHtml(hint.severity)}</span>
        <div><strong>${escapeHtml(hint.title)}</strong><br><span>${escapeHtml(hint.body)}</span></div>
      </div>
    `).join("");
    target.innerHTML = `
      <div class="impact-summary">
        <span class="pill ${info.requiresGameReload ? "warn" : "good"}">게임 새로고침 ${info.requiresGameReload ? "필요" : "불필요"}</span>
        <span class="pill">변경 ${escapeHtml(formatValue(info.changeCount))}</span>
        <span class="pill ${info.highCount ? "blocked" : "good"}">high ${escapeHtml(formatValue(info.highCount))}</span>
        <span class="pill ${info.mediumCount ? "warn" : "good"}">medium ${escapeHtml(formatValue(info.mediumCount))}</span>
      </div>
      ${rows}
      <div class="filter-help">이 안내는 저장 전 이해를 돕는 가이드입니다. 실제 저장 여부는 백엔드 검증과 확인 문구로 한 번 더 막습니다.</div>
    `;
  }

  function refreshAdminEditImpactGuide() {
    const state = refreshAdminEditReviewAndImpact();
    return state ? state.guide : null;
  }

  function renderAdminEditPreviewResult(preview) {
    const target = $(`[data-admin-edit-draft-result]`);
    if (!target) return;
    const payload = preview || {};
    const accepted = Array.isArray(payload.acceptedChanges) ? payload.acceptedChanges : [];
    const rejected = Array.isArray(payload.rejectedChanges) ? payload.rejectedChanges : [];
    const unchanged = Array.isArray(payload.unchangedChanges) ? payload.unchangedChanges : [];
    const stale = Array.isArray(payload.staleChanges) ? payload.staleChanges : [];
    const warnings = Array.isArray(payload.warnings) ? payload.warnings : [];
    const draftValuesForImpact = readAdminEditDraftValues();
    const acceptedForDisplay = sortAdminChangesByRisk(draftValuesForImpact.domain, accepted);
    const acceptedRows = acceptedForDisplay.length ? acceptedForDisplay.map((change) => {
      const risk = getAdminDraftFieldRisk(draftValuesForImpact.domain, change.key);
      const beforeContext = { ...(draftValuesForImpact.originals || {}), [change.key]: change.before };
      const afterContext = { ...(draftValuesForImpact.draft || {}), [change.key]: change.after };
      const relationBadge = isAdminRelationEditField(draftValuesForImpact.domain, change.key) ? ` <span class="pill warn">relation</span>` : "";
      return `
        <tr class="draft-review-row-${escapeHtml(risk)}"><td>${escapeHtml(change.label || change.key)}${relationBadge}</td><td><span class="pill ${risk === "high" ? "blocked" : (risk === "medium" ? "warn" : "good")}">${escapeHtml(risk)}</span></td><td>${renderAdminChangeValueCell(draftValuesForImpact.domain, change, "before", beforeContext)}</td><td>${renderAdminChangeValueCell(draftValuesForImpact.domain, change, "after", afterContext)}</td><td>${escapeHtml(change.type || "-")}</td></tr>
      `;
    }).join("") : `<tr><td colspan="5">변경된 값 없음</td></tr>`;
    const rejectedRows = rejected.length ? rejected.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}</td><td>${escapeHtml(formatValue(change.after))}</td><td>${escapeHtml(change.reason || "rejected")}</td></tr>
    `).join("") : `<tr><td colspan="3">오류 없음</td></tr>`;
    const staleRows = stale.length ? stale.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}</td><td>${escapeHtml(formatValue(change.base))}</td><td>${escapeHtml(formatValue(change.current))}</td><td>${escapeHtml(formatValue(change.after))}</td></tr>
    `).join("") : `<tr><td colspan="4">오래된 초안 아님</td></tr>`;
    const applied = payload.applied === true;
    const modeLabel = applied ? "applied" : (payload.dryRun ? "preview only" : "apply result");
    const impactChanges = accepted.length ? accepted.map((change) => ({ ...change, domain: draftValuesForImpact.domain })) : collectLocalDraftChangesForImpact(draftValuesForImpact);
    renderAdminEditDraftReview(buildAdminEditDraftReview(draftValuesForImpact));
    renderAdminEditImpactGuide(buildAdminEditImpactGuide(draftValuesForImpact.domain, impactChanges, { applied }));
    target.innerHTML = `
      <div class="draft-preview-summary">
        <span class="pill ${payload.wouldBeValid ? "good" : "blocked"}">valid: ${escapeHtml(formatValue(payload.wouldBeValid))}</span>
        <span class="pill ${payload.dryRun ? "warn" : "good"}">dryRun: ${escapeHtml(formatValue(payload.dryRun))}</span>
        <span class="pill ${payload.writeBlocked ? "blocked" : "good"}">writeBlocked: ${escapeHtml(formatValue(payload.writeBlocked))}</span>
        <span class="pill ${applied ? "good" : "warn"}">applied: ${escapeHtml(formatValue(applied))}</span>
        <span class="pill">diff ${escapeHtml(formatValue(payload.diffCount))}</span>
        <span class="pill">errors ${escapeHtml(formatValue(payload.errorCount))}</span>
        <span class="pill">unchanged ${escapeHtml(formatValue(payload.unchangedCount || unchanged.length))}</span>
        <span class="pill ${payload.staleGuardEnabled === false ? "warn" : "good"}">stale guard: ${escapeHtml(payload.staleGuardEnabled === false ? "off" : "on")}</span>
        <span class="pill ${stale.length ? "blocked" : "good"}">stale ${escapeHtml(formatValue(payload.staleCount || stale.length))}</span>
        ${payload.changeLogId ? `<span class="pill good">change log #${escapeHtml(formatValue(payload.changeLogId))}</span>` : ""}
      </div>
      ${warnings.length ? `<div class="filter-help">warnings: ${escapeHtml(warnings.join(", "))}</div>` : ""}
      ${payload.note ? `<div class="filter-help">${escapeHtml(payload.note)}</div>` : ""}
      <details class="json-detail" open>
        <summary>변경 값 <span class="pill good">${escapeHtml(modeLabel)}</span></summary>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>위험도</th><th>이전 DB 값</th><th>적용/초안 값</th><th>타입</th></tr></thead><tbody>${acceptedRows}</tbody></table></div>
      </details>
      <details class="json-detail" ${stale.length ? "open" : ""}>
        <summary>오래된 초안 검사 <span class="pill ${stale.length ? "blocked" : "good"}">${escapeHtml(formatValue(stale.length))}</span></summary>
        <div class="filter-help">편집 화면을 연 뒤 다른 변경이 먼저 적용됐다면, 이 초안은 최신 DB 값을 덮어쓸 수 있어서 차단됩니다. 이 경우 상세를 다시 열고 새 기준값으로 수정하세요.</div>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>화면 열 때 값</th><th>현재 DB 값</th><th>내 초안 값</th></tr></thead><tbody>${staleRows}</tbody></table></div>
      </details>
      <details class="json-detail" ${rejected.length ? "open" : ""}>
        <summary>검증 오류 <span class="pill ${rejected.length ? "blocked" : "good"}">${escapeHtml(formatValue(rejected.length))}</span></summary>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>초안 값</th><th>사유</th></tr></thead><tbody>${rejectedRows}</tbody></table></div>
      </details>
      <div class="filter-help">${applied ? "DB에 적용했습니다. 게임 화면은 새로고침 후 최신 master-data를 다시 읽습니다." : "검증 결과입니다. 실제 적용은 확인 문구가 맞고 오류가 없을 때만 됩니다."}</div>
    `;
  }

  function readAdminEditApplyControls() {
    const confirmEl = $(`[data-admin-edit-apply-confirm]`);
    const riskConfirmEl = $(`[data-admin-edit-risk-confirm]`);
    const reasonEl = $(`[data-admin-edit-apply-reason]`);
    return {
      confirmText: confirmEl ? confirmEl.value.trim() : "",
      riskConfirmText: riskConfirmEl ? riskConfirmEl.value.trim() : "",
      reason: reasonEl ? reasonEl.value.trim() : "",
      confirmMatches: !!confirmEl && confirmEl.value.trim() === ADMIN_EDIT_APPLY_CONFIRM_TEXT,
      highRiskConfirmRequired: buildAdminEditDraftReview().highCount > 0,
      highRiskConfirmMatches: !!riskConfirmEl && riskConfirmEl.value.trim() === ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT,
    };
  }

  async function previewAdminEditDraft(options) {
    ensureApi();
    const values = readAdminEditDraftValues();
    if (!values.ok || !values.id) {
      const error = new Error("검증할 편집 초안이 없습니다. 먼저 마스터 데이터 상세를 열어주세요.");
      setStatus(error.message, "error");
      throw error;
    }
    const target = $(`[data-admin-edit-draft-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에서 초안을 검증하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const applyControls = readAdminEditApplyControls();
    const response = await window.RpgGameApi.previewAdminMasterDataEdit({
      domain: values.domain,
      id: values.id,
      draft: values.draft,
      baseValues: values.originals,
      reason: applyControls.reason || undefined,
      dryRun: true,
      timeoutMs,
    });
    const payload = response && response.payload ? response.payload : {};
    renderAdminEditPreviewResult(payload);
    setStatus(`초안 검증 완료: diff ${formatValue(payload.diffCount)} · errors ${formatValue(payload.errorCount)} · DB 저장 없음`, payload.errorCount ? "error" : "ok");
    return response;
  }

  async function applyAdminEditDraft(options) {
    ensureApi();
    const values = readAdminEditDraftValues();
    const controls = readAdminEditApplyControls();
    if (!values.ok || !values.id) {
      const error = new Error("적용할 편집 초안이 없습니다. 먼저 마스터 데이터 상세를 열어주세요.");
      setStatus(error.message, "error");
      throw error;
    }
    requireAdminWriteDevKeyForUi("마스터 데이터 실제 적용");
    if (!controls.confirmMatches) {
      const error = new Error(`확인 문구를 정확히 입력해야 합니다: ${ADMIN_EDIT_APPLY_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      const target = $(`[data-admin-edit-draft-result]`);
      if (target) target.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
      throw error;
    }
    const review = buildAdminEditDraftReview(values);
    if (review.highCount > 0 && !controls.highRiskConfirmMatches) {
      const error = new Error(`고위험 변경이 있어서 추가 확인 문구를 정확히 입력해야 합니다: ${ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      const target = $(`[data-admin-edit-draft-result]`);
      if (target) target.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
      throw error;
    }
    const confirmed = window.confirm(`정말 DB 마스터 데이터를 수정할까요? 변경 ${review.changeCount}개, high ${review.highCount}개입니다. 적용 후 게임은 새로고침해야 최신 master-data를 읽습니다.`);
    if (!confirmed) {
      setStatus("관리자 변경 적용을 취소했습니다.", "info");
      return { ok: false, canceled: true };
    }
    const target = $(`[data-admin-edit-draft-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에 변경을 적용하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : ADMIN_EDIT_APPLY_TIMEOUT_MS;
    const response = await window.RpgGameApi.applyAdminMasterDataEdit({
      domain: values.domain,
      id: values.id,
      draft: values.draft,
      baseValues: values.originals,
      reason: controls.reason || undefined,
      confirmText: controls.confirmText,
      timeoutMs,
    });
    const payload = response && response.payload ? response.payload : {};
    renderAdminEditPreviewResult(payload);
    if (payload.applied) {
      await runPostWriteMasterApiVerification(values.domain, values.id, {
        label: "DB 적용",
        contextLabel: `change log #${formatValue(payload.changeLogId)} 적용 후 자동 확인`,
      });
      await refreshAdminChangeLogs({ filters: { ...readChangeLogFiltersFromDom(), targetType: `master_data.${values.domain}`, targetId: String(values.id), limit: 10 } });
    } else {
      setStatus(`DB 적용 실패/차단: ${formatValue(payload.status)} · errors ${formatValue(payload.errorCount)}`, "error");
    }
    return response;
  }

  function getAdminEditDraftReadiness(options) {
    const draft = $(`[data-admin-edit-draft]`);
    const fields = draft ? Array.from(draft.querySelectorAll("[data-admin-edit-draft-field]")) : [];
    const validateButton = draft ? draft.querySelector('[data-admin-action="preview-admin-edit-draft"]') : null;
    const applyButton = draft ? draft.querySelector('[data-admin-action="apply-admin-edit-draft"]') : null;
    const controls = readAdminEditApplyControls();
    const result = {
      ok: !!draft && fields.length >= 0 && !!validateButton && validateButton.disabled === false && !!applyButton,
      version: VERSION,
      readOnly: false,
      dryRun: false,
      writeLocked: !hasAdminWriteDevKey(),
      guardedApply: true,
      adminWriteDevKeySet: hasAdminWriteDevKey(),
      confirmTextRequired: ADMIN_EDIT_APPLY_CONFIRM_TEXT,
      highRiskConfirmTextRequired: ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT,
      confirmMatches: controls.confirmMatches,
      highRiskConfirmRequired: controls.highRiskConfirmRequired,
      highRiskConfirmMatches: controls.highRiskConfirmMatches,
      fieldsEditable: fields.every((field) => field.disabled === false),
      hasDraft: !!draft,
      fieldCount: fields.length,
      validateButtonEnabled: !!validateButton && validateButton.disabled === false,
      applyButtonReady: !!applyButton,
      currentDraft: readAdminEditDraftValues(),
      applyControls: controls,
      draftReview: buildAdminEditDraftReview(),
    };
    if (!options || options.log !== false) console.log("[Upgrade RPG] admin edit draft readiness", result);
    return result;
  }

  function makeAdminDetailFieldMap(detailPayload) {
    const fields = Array.isArray(detailPayload && detailPayload.fields) ? detailPayload.fields : [];
    const map = {};
    fields.forEach((field) => {
      if (!field || !field.key) return;
      map[field.key] = field.value;
    });
    return map;
  }

  function valuesEqualForApiVerify(expected, actual) {
    if (expected === actual) return true;
    if ((expected === null || expected === undefined || expected === "") && (actual === null || actual === undefined || actual === "")) return true;
    if (typeof expected === "boolean" || typeof actual === "boolean") {
      return (expected === true || String(expected).toLowerCase() === "true") === (actual === true || String(actual).toLowerCase() === "true");
    }
    const expectedNumber = Number(expected);
    const actualNumber = Number(actual);
    if (expected !== "" && actual !== "" && Number.isFinite(expectedNumber) && Number.isFinite(actualNumber)) {
      return expectedNumber === actualNumber;
    }
    return String(expected) === String(actual);
  }

  function findMasterApiRow(domain, detailPayload, masterPayload) {
    const rows = Array.isArray(masterPayload && masterPayload[domain]) ? masterPayload[domain] : [];
    const fields = makeAdminDetailFieldMap(detailPayload);
    if (!rows.length) return null;

    if (fields.id !== undefined) {
      const byId = rows.find((row) => valuesEqualForApiVerify(fields.id, row && row.id));
      if (byId) return byId;
    }
    if (fields.code !== undefined) {
      const byCode = rows.find((row) => valuesEqualForApiVerify(fields.code, row && row.code));
      if (byCode) return byCode;
    }

    if (domain === "skillLevels") {
      return rows.find((row) => valuesEqualForApiVerify(fields.skill_code, row && row.skillCode) && valuesEqualForApiVerify(fields.level, row && row.level)) || null;
    }
    if (domain === "dropTableItems") {
      return rows.find((row) => valuesEqualForApiVerify(fields.id, row && row.id) || (
        valuesEqualForApiVerify(fields.drop_table_code, row && row.dropTableCode) &&
        valuesEqualForApiVerify(fields.item_template_code, row && row.itemTemplateCode)
      )) || null;
    }
    if (domain === "enhancementLevels") {
      return rows.find((row) =>
        valuesEqualForApiVerify(fields.group_code, row && row.groupCode) &&
        valuesEqualForApiVerify(fields.from_level, row && row.fromLevel) &&
        valuesEqualForApiVerify(fields.to_level, row && row.toLevel)
      ) || null;
    }
    if (domain === "characterSkills") {
      return rows.find((row) =>
        valuesEqualForApiVerify(fields.character_code, row && row.characterCode) &&
        valuesEqualForApiVerify(fields.skill_code, row && row.skillCode)
      ) || null;
    }
    return null;
  }

  function buildMasterApiVerifyComparisons(domain, detailPayload, apiRow) {
    const fieldMap = ADMIN_TO_MASTER_API_FIELD_MAP[domain] || {};
    const detailFields = makeAdminDetailFieldMap(detailPayload);
    return Object.entries(fieldMap)
      .filter(([adminKey, apiKey]) => detailFields[adminKey] !== undefined && apiRow && Object.prototype.hasOwnProperty.call(apiRow, apiKey))
      .map(([adminKey, apiKey]) => {
        const expected = detailFields[adminKey];
        const actual = apiRow ? apiRow[apiKey] : undefined;
        return {
          adminKey,
          apiKey,
          expected,
          actual,
          same: valuesEqualForApiVerify(expected, actual),
        };
      });
  }

  function renderMasterApiVerifyResult(result) {
    const target = $(`[data-admin-master-api-verify-result]`);
    if (!target) return;
    const info = result || {};
    if (!info.checked) {
      target.innerHTML = `<div class="empty">버튼을 누르면 현재 선택한 상세 항목이 <strong>/game/master-data</strong> 응답에도 같은 값으로 보이는지 확인합니다.</div>`;
      return;
    }
    if (!info.found) {
      target.innerHTML = `
        <div class="error">master-data API에서 선택한 항목을 찾지 못했습니다.</div>
        <div class="filter-help">domain=${escapeHtml(formatValue(info.domain))} · id=${escapeHtml(formatValue(info.id))} · rows=${escapeHtml(formatValue(info.rowCount))}</div>
      `;
      return;
    }
    const rows = (info.comparisons || []).map((row) => `
      <tr>
        <td>${escapeHtml(row.adminKey)}</td>
        <td>${escapeHtml(row.apiKey)}</td>
        <td>${escapeHtml(formatValue(row.expected))}</td>
        <td>${escapeHtml(formatValue(row.actual))}</td>
        <td><span class="pill ${row.same ? "good" : "blocked"}">${row.same ? "same" : "diff"}</span></td>
      </tr>
    `).join("") || `<tr><td colspan="5">비교 가능한 스칼라 필드가 없습니다.</td></tr>`;
    target.innerHTML = `
      <div class="draft-preview-summary">
        <span class="pill ${info.ok ? "good" : "blocked"}">API 반영 ${info.ok ? "정상" : "차이 있음"}</span>
        <span class="pill">domain ${escapeHtml(formatValue(info.domain))}</span>
        <span class="pill">비교 ${escapeHtml(formatValue(info.comparisonCount))}</span>
        <span class="pill ${info.diffCount ? "blocked" : "good"}">diff ${escapeHtml(formatValue(info.diffCount))}</span>
        <span class="pill">checked ${escapeHtml(formatClock(info.checkedAt))}</span>
        ${info.contextLabel ? `<span class="pill warn">${escapeHtml(info.contextLabel)}</span>` : ""}
      </div>
      <div class="table-wrap relation-table-wrap"><table><thead><tr><th>관리자 필드</th><th>master-data API 필드</th><th>관리자 상세 값</th><th>API 값</th><th>상태</th></tr></thead><tbody>${rows}</tbody></table></div>
      <div class="filter-help">이 검사는 DB → FastAPI <code>/game/master-data</code> 응답까지 반영됐는지 확인합니다. 이미 열려 있던 게임 화면은 새로고침해야 새 master-data를 다시 읽습니다.</div>
    `;
  }

  async function verifySelectedMasterDataApi(options) {
    ensureApi();
    const detail = currentMasterDetailPayload;
    if (!detail || !detail.id || !detail.domain) {
      const error = new Error("먼저 마스터 데이터 상세를 열어주세요.");
      setStatus(error.message, "error");
      throw error;
    }
    const target = $(`[data-admin-master-api-verify-result]`);
    if (target) target.innerHTML = `<div class="empty">/game/master-data 응답에서 선택 항목을 확인하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.fetchMasterData({ timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    const domain = detail.domain;
    const rows = Array.isArray(payload[domain]) ? payload[domain] : [];
    const apiRow = findMasterApiRow(domain, detail, payload);
    const comparisons = apiRow ? buildMasterApiVerifyComparisons(domain, detail, apiRow) : [];
    const diffCount = comparisons.filter((row) => !row.same).length;
    const result = {
      checked: true,
      ok: !!apiRow && diffCount === 0,
      found: !!apiRow,
      domain,
      id: detail.id,
      title: detail.title,
      rowCount: rows.length,
      comparisonCount: comparisons.length,
      diffCount,
      comparisons,
      apiRowPreview: apiRow || null,
      counts: payload.counts || {},
      contextLabel: options && options.contextLabel ? String(options.contextLabel) : "",
      autoAfterWrite: !!(options && options.autoAfterWrite),
      checkedAt: new Date().toISOString(),
    };
    renderMasterApiVerifyResult(result);
    setStatus(result.ok ? `master-data API 반영 확인 완료: ${formatValue(domain)} #${formatValue(detail.id)}` : `master-data API 확인 필요: diff ${formatValue(diffCount)}`, result.ok ? "ok" : "error");
    return result;
  }

  async function runPostWriteMasterApiVerification(domain, id, options) {
    const opts = options || {};
    const label = opts.label || "DB 적용";
    const result = {
      ok: false,
      status: "not_started",
      domain,
      id,
      label,
      verification: null,
      error: null,
    };
    if (!domain || !id) {
      result.status = "skipped_missing_target";
      setStatus(`${label} 완료 · API 자동 확인은 대상 정보가 없어 건너뜀`, "error");
      return result;
    }
    try {
      setStatus(`${label} 완료 · 상세 다시 불러오기 및 master-data API 자동 확인 중...`, "info");
      await openAdminMasterDataDetail(domain, id, { timeoutMs: DEFAULT_TIMEOUT_MS });
      const verification = await verifySelectedMasterDataApi({
        timeoutMs: DEFAULT_TIMEOUT_MS,
        contextLabel: opts.contextLabel || `${label} 후 자동 확인`,
        autoAfterWrite: true,
      });
      result.verification = verification;
      result.ok = !!(verification && verification.ok);
      result.status = result.ok ? "verified" : "diff_or_missing";
      setStatus(
        result.ok
          ? `${label} 완료 · master-data API 자동 확인 정상 · 게임은 새로고침 후 반영`
          : `${label} 완료 · master-data API 자동 확인 필요: diff ${formatValue(verification && verification.diffCount)}`,
        result.ok ? "ok" : "error"
      );
      return result;
    } catch (error) {
      result.status = "verify_failed";
      result.error = error;
      const target = $(`[data-admin-master-api-verify-result]`);
      if (target) {
        target.innerHTML = `<div class="error">${escapeHtml(label)} 후 master-data API 자동 확인 실패: ${escapeHtml(error && error.message ? error.message : error)}</div>`;
      }
      setStatus(`${label} 완료 · master-data API 자동 확인 실패: ${error && error.message ? error.message : error}`, "error");
      return result;
    }
  }

  function renderMasterDetail(detailPayload) {
    currentMasterDetailPayload = detailPayload && detailPayload.status === "loaded" ? detailPayload : null;
    const target = $("[data-admin-master-detail]");
    const meta = $("[data-admin-master-detail-meta]");
    if (!target) return;
    const detail = detailPayload || {};
    const fields = Array.isArray(detail.fields) ? detail.fields : [];
    const jsonFields = Array.isArray(detail.jsonFields) ? detail.jsonFields : [];
    const assetFields = Array.isArray(detail.assetFields) ? detail.assetFields : [];
    const relationHints = Array.isArray(detail.relationHints) ? detail.relationHints : [];
    if (meta) meta.textContent = detail.status === "loaded" ? `${formatValue(detail.domainLabel || detail.domain)} · #${formatValue(detail.id)} · ${formatValue(detail.title)}` : formatValue(detail.status || "선택 없음");
    if (detail.status && detail.status !== "loaded") {
      target.innerHTML = `<div class="error">상세 정보를 불러오지 못했습니다: ${escapeHtml(detail.status)}</div>`;
      return;
    }
    if (!detail.id) {
      target.innerHTML = `<div class="empty">마스터 데이터 카탈로그에서 행의 <strong>보기</strong> 버튼을 누르면 상세 정보가 여기에 표시됩니다.</div>`;
      return;
    }

    const fieldRows = fields.map((field) => `
      <tr><th>${escapeHtml(field.label || field.key)}${renderFieldHelpBadge(field.key)}</th><td>${formatValueWithFieldHint(field.key, field.value)}${renderFieldHelpInline(field.key)}</td></tr>
    `).join("");
    const relationRows = relationHints.length ? relationHints.map((hint) => `
      <span class="pill">${escapeHtml(hint.label)}: ${escapeHtml(formatValue(hint.value))}</span>
    `).join(" ") : `<span class="pill">연결 요약 없음</span>`;
    const assetRows = assetFields.length ? assetFields.map((asset) => `
      <tr><th>${escapeHtml(asset.label || asset.key)}</th><td><span class="pill ${asset.hidden ? "good" : ""}">${asset.hidden ? "hidden" : "empty"}</span> ${escapeHtml(formatValue(asset.kind))} · ${escapeHtml(formatValue(asset.length))} chars</td></tr>
    `).join("") : `<tr><td colspan="2">숨길 이미지/아이콘 필드 없음</td></tr>`;
    const jsonBlocks = jsonFields.length ? jsonFields.map((field) => {
      const previewText = JSON.stringify(field.preview, null, 2);
      const keyText = Array.isArray(field.keys) && field.keys.length ? field.keys.join(", ") : "-";
      return `
        <details class="json-detail" open>
          <summary>${escapeHtml(field.label || field.key)} <span class="pill good">sanitized</span> <span class="pill">keys: ${escapeHtml(keyText)}</span></summary>
          <div class="json-meta">hidden assets ${escapeHtml(formatValue(field.hiddenAssetCount))} · truncated ${escapeHtml(formatValue(field.truncatedCount))} · raw JSON ${field.rawJsonReturned ? "returned" : "hidden"}</div>
          <pre class="json-preview">${escapeHtml(previewText)}</pre>
        </details>
      `;
    }).join("") : `<div class="empty">JSON 필드 없음</div>`;

    target.innerHTML = `
      <div class="detail-grid">
        <div class="detail-card">
          <div class="detail-title">기본 필드</div>
          <table class="detail-table"><tbody>${fieldRows}</tbody></table>
        </div>
        <div class="detail-card">
          <div class="detail-title">연결 요약</div>
          <div class="relation-list">${relationRows}</div>
          <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;">
            <button class="btn mini" type="button" data-admin-action="open-master-relations" data-admin-relation-domain="${escapeHtml(detail.domain || "")}" data-admin-relation-id="${escapeHtml(detail.id)}">연결 항목 불러오기</button>
            <span class="pill good">read-only</span>
          </div>
          <div class="detail-title" style="margin-top:14px;">에셋 필드</div>
          <table class="detail-table"><tbody>${assetRows}</tbody></table>
        </div>
      </div>
      <div style="margin:0 14px 12px;">${renderMasterEditDraft(detail, fields)}</div>
      <div class="detail-card" style="margin:0 14px 12px;">
        <div class="detail-title">인게임 master-data API 반영 확인 <span class="pill good">diagnostic</span></div>
        <div class="filter-help">관리자 상세 값이 게임이 읽는 <code>/game/master-data</code> 응답에도 같은 값으로 보이는지 확인합니다. DB 적용 직후 게임 새로고침 전 점검용입니다.</div>
        <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;">
          <button class="btn mini primary" type="button" data-admin-action="verify-master-api-target">선택 항목 API 반영 확인</button>
          <span class="pill warn">게임 화면은 새로고침 필요</span>
        </div>
        <div class="edit-draft-result" data-admin-master-api-verify-result><div class="empty">버튼을 누르면 현재 선택한 상세 항목이 <strong>/game/master-data</strong> 응답에도 같은 값으로 보이는지 확인합니다.</div></div>
      </div>
      <div class="detail-card" style="margin:0 14px 12px;">
        <div class="detail-title">실제 연결 항목</div>
        <div class="filter-help">관련 마스터 데이터를 축약된 목록으로 보여줍니다. 행의 보기 버튼을 누르면 해당 항목 상세로 이동합니다.</div>
        <div data-admin-master-relations><div class="empty">연결 항목을 불러오지 않았습니다.</div></div>
      </div>
      <div class="detail-card" style="margin-top:12px;">
        <div class="detail-title">JSON 미리보기</div>
        <div class="filter-help">원본 JSON 통째로가 아니라, data URL 이미지/긴 문자열을 숨긴 안전 미리보기입니다.</div>
        ${jsonBlocks}
      </div>
      <div class="filter-help">readOnly=${escapeHtml(formatValue(detail.readOnly))} · write UI=${escapeHtml(formatValue(detail.safeForAdminWriteUi))} · rawJsonReturned=${escapeHtml(formatValue(detail.rawJsonReturned))} · assetsReturned=${escapeHtml(formatValue(detail.assetsReturned))}</div>
    `;
  }

  function renderMasterRelations(relationsPayload) {
    const target = $("[data-admin-master-relations]");
    if (!target) return;
    const relations = relationsPayload || {};
    const groups = Array.isArray(relations.groups) ? relations.groups : [];
    if (relations.status && relations.status !== "loaded") {
      target.innerHTML = `<div class="error">연결 항목을 불러오지 못했습니다: ${escapeHtml(relations.status)}</div>`;
      return;
    }
    if (!groups.length) {
      target.innerHTML = `<div class="empty">연결된 마스터 데이터가 없습니다.</div>`;
      return;
    }
    target.innerHTML = groups.map((group) => {
      const rows = Array.isArray(group.rows) ? group.rows : [];
      const columns = Array.isArray(group.columns) ? group.columns.slice(0, 6) : [];
      const limited = group.limited ? ` · ${escapeHtml(formatValue(group.count))}개 중 ${escapeHtml(formatValue(group.shown))}개 표시` : ` · ${escapeHtml(formatValue(group.count))}개`;
      return `
        <details class="json-detail" open>
          <summary>${escapeHtml(group.label || group.domainLabel || group.domain)} <span class="pill">${escapeHtml(group.domainLabel || group.domain)}</span><span class="pill good">read-only</span><span class="pill">${limited}</span></summary>
          ${rows.length ? `
            <div class="table-wrap relation-table-wrap">
              <table>
                <thead><tr><th>상세</th><th>ID</th><th>제목</th>${columns.map((column) => `<th title="${escapeHtml((getAdminFieldHelp(column.key) && getAdminFieldHelp(column.key).body) || column.key)}">${escapeHtml(column.label || column.key)}${renderFieldHelpBadge(column.key)}</th>`).join("")}</tr></thead>
                <tbody>
                  ${rows.map((row) => {
                    const cells = row.cells || {};
                    return `
                      <tr>
                        <td><button class="btn mini" type="button" data-admin-action="open-master-detail" data-admin-detail-domain="${escapeHtml(row.domain || group.domain || "")}" data-admin-detail-id="${escapeHtml(row.id)}">보기</button></td>
                        <td>${escapeHtml(formatValue(row.id))}</td>
                        <td>${escapeHtml(formatValue(row.title))}</td>
                        ${columns.map((column) => `<td>${formatValueWithFieldHint(column.key, cells[column.key])}</td>`).join("")}
                      </tr>
                    `;
                  }).join("")}
                </tbody>
              </table>
            </div>
          ` : `<div class="empty">표시할 연결 행이 없습니다.</div>`}
        </details>
      `;
    }).join("");
  }

  async function openAdminMasterDataRelations(domain, id, options) {
    ensureApi();
    const target = $("[data-admin-master-relations]");
    const safeDomain = domain || (readMasterCatalogFiltersFromDom().domain || DEFAULT_MASTER_DOMAIN);
    const safeId = Number(id);
    if (!Number.isFinite(safeId) || safeId <= 0) {
      const error = new Error("연결 항목 조회 ID가 올바르지 않습니다.");
      renderMasterRelations({ status: "invalid_id", id, domain: safeDomain });
      setStatus(error.message, "error");
      throw error;
    }
    if (target) target.innerHTML = `<div class="empty">연결 항목을 불러오는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const limit = options && options.limit !== undefined ? options.limit : 20;
    const response = await window.RpgGameApi.fetchAdminMasterDataRelations({ domain: safeDomain, id: safeId, limit, timeoutMs });
    const relationsPayload = response && response.payload ? response.payload : {};
    renderMasterRelations(relationsPayload);
    setStatus(`연결 항목 로드: ${formatValue(relationsPayload.domainLabel || relationsPayload.domain)} #${formatValue(relationsPayload.id)} · ${formatValue(relationsPayload.totalRelatedRows)}개`, "ok");
    return response;
  }

  async function openAdminMasterDataDetailByCode(domain, code) {
    ensureApi();
    const safeDomain = domain || DEFAULT_MASTER_DOMAIN;
    const safeCode = String(code || "").trim();
    if (!safeCode) throw new Error("열 relation code가 없습니다.");
    setStatus(`관계 대상 찾는 중: ${safeDomain} · ${safeCode}`);
    const response = await window.RpgGameApi.listAdminMasterCatalogRows({ domain: safeDomain, q: safeCode, limit: 20, page: 1, sort: "id_asc" });
    const payload = response && response.payload ? response.payload : {};
    const rows = Array.isArray(payload.rows) ? payload.rows : [];
    const row = rows.find((candidate) => {
      const cells = candidate && candidate.cells ? candidate.cells : {};
      return String(cells.code || candidate.code || "") === safeCode;
    }) || rows[0];
    if (!row || !row.id) throw new Error(`관계 대상을 찾지 못했습니다: ${safeDomain} · ${safeCode}`);
    return openAdminMasterDataDetail(safeDomain, row.id);
  }

  async function openAdminMasterDataDetail(domain, id, options) {
    ensureApi();
    const target = $("[data-admin-master-detail]");
    const meta = $("[data-admin-master-detail-meta]");
    const safeDomain = domain || (readMasterCatalogFiltersFromDom().domain || DEFAULT_MASTER_DOMAIN);
    const safeId = Number(id);
    if (!Number.isFinite(safeId) || safeId <= 0) {
      const error = new Error("상세 조회 ID가 올바르지 않습니다.");
      renderMasterDetail({ status: "invalid_id", id, domain: safeDomain });
      setStatus(error.message, "error");
      throw error;
    }
    if (target) target.innerHTML = `<div class="empty">상세 정보를 불러오는 중...</div>`;
    if (meta) meta.textContent = `${safeDomain} · #${safeId}`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.fetchAdminMasterDataDetail({ domain: safeDomain, id: safeId, timeoutMs });
    const detailPayload = response && response.payload ? response.payload : {};
    renderMasterDetail(detailPayload);
    markSelectedMasterCatalogRow(safeDomain, safeId);
    if (!options || options.loadRelations !== false) {
      try {
        await openAdminMasterDataRelations(safeDomain, safeId, { timeoutMs, limit: 20 });
      } catch (error) {
        // 상세 정보는 이미 표시됐으므로, 연결 항목 실패는 상태 메시지만 남깁니다.
        console.warn("[Upgrade RPG] admin relations load failed", error);
      }
    }
    setStatus(`상세 로드: ${formatValue(detailPayload.domainLabel || detailPayload.domain)} #${formatValue(detailPayload.id)} · ${formatValue(detailPayload.title)}`, "ok");
    return response;
  }

  function renderSnapshotTable(snapshotPayload) {
    const target = $("[data-admin-snapshot-table]");
    const meta = $("[data-admin-snapshot-meta]");
    if (!target) return;
    const rows = Array.isArray(snapshotPayload.snapshots) ? snapshotPayload.snapshots : [];
    const filters = snapshotPayload.filters || {};
    const filterNote = filters.hasActiveFilters ? ` · ${describeSnapshotFilters(filters)}` : "";
    const totalAllNote = snapshotPayload.totalAll !== undefined ? ` / 전체 ${formatValue(snapshotPayload.totalAll)}` : "";
    if (meta) meta.textContent = `${formatValue(rows.length)} / ${formatValue(snapshotPayload.total)} shown${totalAllNote}${filterNote}`;
    if (!rows.length) {
      target.innerHTML = `<div class="empty">최근 세이브 스냅샷이 없습니다.</div>`;
      return;
    }
    target.innerHTML = `
      <table>
        <thead><tr><th>ID</th><th>유저</th><th>슬롯</th><th>버전</th><th>골드</th><th>레벨</th><th>인벤</th><th>창고</th><th>출처</th><th>원본 JSON</th><th>수정 시각</th></tr></thead>
        <tbody>
          ${rows.map((row) => {
            const summary = row.summary || {};
            const counts = row.counts || {};
            return `
              <tr title="${escapeHtml(row.note || "")}">
                <td>${escapeHtml(formatValue(row.id))}</td>
                <td>${escapeHtml(formatValue(row.userId))}</td>
                <td>${escapeHtml(formatValue(row.slotKey))} ${row.isDefault ? `<span class="pill good">default</span>` : ""}</td>
                <td>${escapeHtml(formatValue(row.saveVersion))}</td>
                <td>${escapeHtml(formatValue(summary.gold))}</td>
                <td>${escapeHtml(formatValue(summary.level))}</td>
                <td>${escapeHtml(formatValue(counts.inventoryItems))}</td>
                <td>${escapeHtml(formatValue(counts.storageItems))}</td>
                <td>${escapeHtml(formatValue(row.source))}</td>
                <td><span class="pill ${row.rawSnapshotReturned ? "blocked" : "good"}">${row.rawSnapshotReturned ? "returned" : "hidden"}</span></td>
                <td>${escapeHtml(formatClock(row.updatedAt))}</td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>
    `;
  }

  function renderAdminChangeLogs(logsPayload) {
    const target = $(`[data-admin-change-log-table]`);
    const meta = $(`[data-admin-change-log-meta]`);
    if (!target) return;
    const payload = logsPayload || {};
    const rows = Array.isArray(payload.rows) ? payload.rows : [];
    if (meta) meta.textContent = `${formatValue(rows.length)} / ${formatValue(payload.total)} logs · ${describeChangeLogFilters(payload.filters || {})} · before/after raw JSON hidden`;
    if (!rows.length) {
      target.innerHTML = `<div class="empty">아직 관리자 변경 이력이 없습니다.</div>`;
      return;
    }
    target.innerHTML = `
      <table>
        <thead><tr><th>상세</th><th>ID</th><th>대상</th><th>행</th><th>액션</th><th>변경 필드</th><th>사유</th><th>적용</th><th>시각</th></tr></thead>
        <tbody>
          ${rows.map((row) => `
            <tr>
              <td><button class="btn mini" type="button" data-admin-action="open-admin-change-log-detail" data-admin-change-log-id="${escapeHtml(row.id)}">보기</button></td>
              <td>${escapeHtml(formatValue(row.id))}</td>
              <td>${escapeHtml(formatValue(row.targetType))}</td>
              <td>${escapeHtml(formatValue(row.targetId))}</td>
              <td>${escapeHtml(formatValue(row.action))}</td>
              <td>${escapeHtml((row.changedKeys || []).join(", ") || "-")}${row.relationChangeCount ? ` <span class="pill warn">relation ${escapeHtml(formatValue(row.relationChangeCount))}</span>` : ""}</td>
              <td>${escapeHtml(formatValue(row.reason))}</td>
              <td><span class="pill ${row.applied ? "good" : "blocked"}">${escapeHtml(formatValue(row.applied))}</span></td>
              <td>${escapeHtml(formatClock(row.createdAt))}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }


  function renderAdminChangeLogDetail(detailPayload) {
    currentAdminChangeLogDetailPayload = detailPayload && detailPayload.status === "loaded" ? detailPayload : null;
    const target = $(`[data-admin-change-log-detail]`);
    if (!target) return;
    const payload = detailPayload || {};
    if (!payload.id || payload.status !== "loaded") {
      target.innerHTML = `<div class="empty">변경 이력의 <strong>보기</strong> 버튼을 누르면 상세/되돌리기 미리보기가 여기에 표시됩니다.</div>`;
      return;
    }
    const changes = Array.isArray(payload.changes) ? payload.changes : [];
    const rollback = payload.rollback || {};
    const createDelete = payload.createDelete || {};
    const createDeleteRestore = payload.createDeleteRestore || {};
    const rows = changes.length ? changes.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}${change.relation ? ` <span class="pill warn">relation</span>` : ""}</td><td>${renderAdminChangeValueCell(payload.rollback && payload.rollback.domain, change, "before", {})}</td><td>${renderAdminChangeValueCell(payload.rollback && payload.rollback.domain, change, "after", {})}</td></tr>
    `).join("") : `<tr><td colspan="3">변경 필드 없음</td></tr>`;
    const relationCount = payload.relationChangeCount || changes.filter((change) => change.relation).length;
    target.innerHTML = `
      <div class="detail-card" data-admin-change-log-detail-card data-admin-change-log-id="${escapeHtml(payload.id)}">
        <div class="detail-title">변경 이력 #${escapeHtml(formatValue(payload.id))} <span class="pill ${rollback.available ? "good" : "blocked"}">rollback ${rollback.available ? "ready" : "blocked"}</span> <span class="pill ${createDelete.available ? "warn" : "blocked"}">create delete ${createDelete.available ? "ready" : "blocked"}</span> <span class="pill ${createDeleteRestore.available ? "good" : "blocked"}">restore ${createDeleteRestore.available ? "ready" : "blocked"}</span>${relationCount ? ` <span class="pill warn">relation ${escapeHtml(formatValue(relationCount))}</span>` : ""}</div>
        <div class="filter-help">대상: ${escapeHtml(formatValue(payload.targetType))} / 행 ${escapeHtml(formatValue(payload.targetId))} · action=${escapeHtml(formatValue(payload.action))} · applied=${escapeHtml(formatValue(payload.applied))}</div>
        <div class="filter-help">사유: ${escapeHtml(formatValue(payload.reason))} · 시각: ${escapeHtml(formatClock(payload.createdAt))}</div>
        <div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>이전 값</th><th>적용 값</th></tr></thead><tbody>${rows}</tbody></table></div>
        <div class="edit-draft-actions">
          <button class="btn mini primary" type="button" data-admin-action="preview-admin-change-log-rollback">되돌리기 미리보기</button>
          <label class="apply-confirm-field"><span>되돌리기 확인 문구</span><input type="text" data-admin-rollback-confirm placeholder="${escapeHtml(ADMIN_ROLLBACK_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>되돌리기 사유</span><input type="text" data-admin-rollback-reason placeholder="예: 보스 HP 변경 되돌림" autocomplete="off" /></label>
          <button class="btn mini danger" type="button" data-admin-action="apply-admin-change-log-rollback">검사 후 되돌리기</button>
          <span class="pill warn">DB rollback: dev-key guarded</span>
        </div>
        <div class="edit-draft-result" data-admin-rollback-result><div class="empty">먼저 <strong>되돌리기 미리보기</strong>를 눌러 현재 DB 값이 이 변경 이력의 적용 값과 일치하는지 확인하세요.</div></div>
        <div class="edit-draft-actions">
          <button class="btn mini primary" type="button" data-admin-action="preview-admin-create-delete" ${createDelete.available ? "" : "disabled"}>생성 row 삭제 미리보기</button>
          <label class="apply-confirm-field"><span>생성 row 삭제 확인 문구</span><input type="text" data-admin-create-delete-confirm placeholder="${escapeHtml(ADMIN_CREATE_DELETE_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>생성 row 삭제 사유</span><input type="text" data-admin-create-delete-reason placeholder="예: 테스트 생성 row 삭제" autocomplete="off" /></label>
          <button class="btn mini danger" type="button" data-admin-action="apply-admin-create-delete" ${createDelete.available ? "" : "disabled"}>검사 후 생성 row 삭제</button>
          <span class="pill ${createDelete.available ? "warn" : "blocked"}">${createDelete.available ? "create-delete guarded" : "create-delete locked"}</span>
        </div>
        <div class="edit-draft-result" data-admin-create-delete-result><div class="empty">create action으로 생성된 제한 도메인 row만 삭제 되돌리기를 미리보기할 수 있습니다.</div></div>
        <div class="edit-draft-actions">
          <button class="btn mini primary" type="button" data-admin-action="preview-admin-create-delete-restore" ${createDeleteRestore.available ? "" : "disabled"}>삭제 row 복원 미리보기</button>
          <label class="apply-confirm-field"><span>삭제 row 복원 확인 문구</span><input type="text" data-admin-create-delete-restore-confirm placeholder="${escapeHtml(ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT)}" autocomplete="off" /></label>
          <label class="apply-confirm-field"><span>삭제 row 복원 사유</span><input type="text" data-admin-create-delete-restore-reason placeholder="예: 실수로 삭제한 생성 row 복원" autocomplete="off" /></label>
          <button class="btn mini danger" type="button" data-admin-action="apply-admin-create-delete-restore" ${createDeleteRestore.available ? "" : "disabled"}>검사 후 삭제 row 복원</button>
          <span class="pill ${createDeleteRestore.available ? "good" : "blocked"}">${createDeleteRestore.available ? "create-delete restore guarded" : "restore locked"}</span>
        </div>
        <div class="edit-draft-result" data-admin-create-delete-restore-result><div class="empty">create_delete action으로 삭제된 제한 도메인 row만 복원 미리보기를 할 수 있습니다.</div></div>
      </div>
    `;
  }

  function readAdminRollbackControls() {
    const card = $(`[data-admin-change-log-detail-card]`);
    const confirmEl = $(`[data-admin-rollback-confirm]`);
    const reasonEl = $(`[data-admin-rollback-reason]`);
    return {
      changeLogId: card ? Number(card.getAttribute("data-admin-change-log-id") || 0) : 0,
      confirmText: confirmEl ? confirmEl.value.trim() : "",
      reason: reasonEl ? reasonEl.value.trim() : "",
      confirmMatches: !!confirmEl && confirmEl.value.trim() === ADMIN_ROLLBACK_CONFIRM_TEXT,
    };
  }

  function renderAdminRollbackResult(payload) {
    const target = $(`[data-admin-rollback-result]`);
    if (!target) return;
    const result = payload || {};
    const changes = Array.isArray(result.acceptedChanges) && result.acceptedChanges.length ? result.acceptedChanges : (Array.isArray(result.changes) ? result.changes : []);
    const mismatches = Array.isArray(result.currentMismatches) ? result.currentMismatches : [];
    const warnings = Array.isArray(result.warnings) ? result.warnings : [];
    const rows = changes.length ? changes.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}${change.relation ? ` <span class="pill warn">relation</span>` : ""}</td><td>${renderAdminChangeValueCell(result.domain, change, "after", {})}</td><td>${renderAdminChangeValueCell(result.domain, change, "before", {})}</td></tr>
    `).join("") : `<tr><td colspan="3">되돌릴 변경 없음</td></tr>`;
    const relationCount = result.relationChangeCount || changes.filter((change) => change.relation).length;
    const mismatchRows = mismatches.length ? mismatches.map((item) => `
      <tr><td>${escapeHtml(item.label || item.key)}${item.relation ? ` <span class="pill warn">relation</span>` : ""}</td><td>${renderAdminRollbackMismatchValueCell(result.domain, item, "current")}</td><td>${renderAdminRollbackMismatchValueCell(result.domain, item, "expectedAfter")}</td><td>${renderAdminRollbackMismatchValueCell(result.domain, item, "rollbackTo")}</td></tr>
    `).join("") : `<tr><td colspan="4">현재 DB 값 일치</td></tr>`;
    target.innerHTML = `
      <div class="draft-preview-summary">
        <span class="pill ${result.rollbackReady ? "good" : "blocked"}">rollbackReady: ${escapeHtml(formatValue(result.rollbackReady))}</span>
        <span class="pill ${result.currentMatchesAfter ? "good" : "blocked"}">currentMatchesAfter: ${escapeHtml(formatValue(result.currentMatchesAfter))}</span>
        <span class="pill ${result.dryRun ? "warn" : "good"}">dryRun: ${escapeHtml(formatValue(result.dryRun))}</span>
        <span class="pill ${result.writeBlocked ? "blocked" : "good"}">writeBlocked: ${escapeHtml(formatValue(result.writeBlocked))}</span>
        <span class="pill ${result.rolledBack ? "good" : "warn"}">rolledBack: ${escapeHtml(formatValue(result.rolledBack === true))}</span>
        <span class="pill ${relationCount ? "warn" : "good"}">relation ${escapeHtml(formatValue(relationCount || 0))}</span>
        ${result.rollbackChangeLogId ? `<span class="pill good">rollback log #${escapeHtml(formatValue(result.rollbackChangeLogId))}</span>` : ""}
      </div>
      ${warnings.length ? `<div class="filter-help">warnings: ${escapeHtml(warnings.join(", "))}</div>` : ""}
      ${result.note ? `<div class="filter-help">${escapeHtml(result.note)}</div>` : ""}
      <details class="json-detail" open><summary>되돌릴 값</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>현재/적용 값</th><th>되돌릴 값</th></tr></thead><tbody>${rows}</tbody></table></div></details>
      <details class="json-detail" ${mismatches.length ? "open" : ""}><summary>현재값 안전 검사</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>현재 DB 값</th><th>이력의 적용 값</th><th>되돌릴 값</th></tr></thead><tbody>${mismatchRows}</tbody></table></div></details>
    `;
  }

  async function openAdminChangeLogDetail(changeLogId, options) {
    ensureApi();
    const id = Number(changeLogId || 0);
    if (!id) throw new Error("변경 이력 ID가 올바르지 않습니다.");
    const target = $(`[data-admin-change-log-detail]`);
    if (target) target.innerHTML = `<div class="empty">변경 이력 상세 불러오는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.fetchAdminChangeLogDetail({ id, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminChangeLogDetail(payload);
    setStatus(`변경 이력 #${formatValue(id)} 상세 로드`, "ok");
    return response;
  }

  async function previewAdminChangeLogRollback(options) {
    ensureApi();
    const controls = readAdminRollbackControls();
    if (!controls.changeLogId) throw new Error("되돌릴 변경 이력 상세를 먼저 열어주세요.");
    const target = $(`[data-admin-rollback-result]`);
    if (target) target.innerHTML = `<div class="empty">되돌리기 안전 검사 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.previewAdminChangeLogRollback({ id: controls.changeLogId, reason: controls.reason || undefined, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminRollbackResult(payload);
    setStatus(`되돌리기 미리보기: ${formatValue(payload.status)} · ready ${formatValue(payload.rollbackReady)}`, payload.rollbackReady ? "ok" : "error");
    return response;
  }

  async function applyAdminChangeLogRollback(options) {
    ensureApi();
    const controls = readAdminRollbackControls();
    if (!controls.changeLogId) throw new Error("되돌릴 변경 이력 상세를 먼저 열어주세요.");
    requireAdminWriteDevKeyForUi("변경 이력 되돌리기 적용");
    if (!controls.confirmMatches) {
      const error = new Error(`되돌리기 확인 문구를 정확히 입력해야 합니다: ${ADMIN_ROLLBACK_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      const target = $(`[data-admin-rollback-result]`);
      if (target) target.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
      throw error;
    }
    const confirmed = window.confirm("정말 이 변경 이력을 기준으로 DB 값을 이전 값으로 되돌릴까요? 현재값 안전 검사를 통과해야 적용됩니다.");
    if (!confirmed) {
      setStatus("관리자 되돌리기를 취소했습니다.", "info");
      return { ok: false, canceled: true };
    }
    const target = $(`[data-admin-rollback-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에서 되돌리기를 적용하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : ADMIN_EDIT_APPLY_TIMEOUT_MS;
    const response = await window.RpgGameApi.applyAdminChangeLogRollback({ id: controls.changeLogId, confirmText: controls.confirmText, reason: controls.reason || undefined, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminRollbackResult(payload);
    if (payload.rolledBack) {
      const rollbackTarget = currentAdminChangeLogDetailPayload && currentAdminChangeLogDetailPayload.rollback ? currentAdminChangeLogDetailPayload.rollback : {};
      await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      await runPostWriteMasterApiVerification(rollbackTarget.domain, rollbackTarget.id, {
        label: "되돌리기",
        contextLabel: `rollback log #${formatValue(payload.rollbackChangeLogId)} 적용 후 자동 확인`,
      });
    } else {
      setStatus(`되돌리기 실패/차단: ${formatValue(payload.status)}`, "error");
    }
    return response;
  }


  function readAdminCreateDeleteControls() {
    const card = $(`[data-admin-change-log-detail-card]`);
    const confirmEl = $(`[data-admin-create-delete-confirm]`);
    const reasonEl = $(`[data-admin-create-delete-reason]`);
    return {
      changeLogId: card ? Number(card.getAttribute("data-admin-change-log-id") || 0) : 0,
      confirmText: confirmEl ? confirmEl.value.trim() : "",
      reason: reasonEl ? reasonEl.value.trim() : "",
      confirmMatches: !!confirmEl && confirmEl.value.trim() === ADMIN_CREATE_DELETE_CONFIRM_TEXT,
    };
  }

  function renderAdminCreateDeleteResult(payload) {
    const target = $(`[data-admin-create-delete-result]`);
    if (!target) return;
    const result = payload || {};
    const changes = Array.isArray(result.changes) ? result.changes : [];
    const mismatches = Array.isArray(result.currentMismatches) ? result.currentMismatches : [];
    const dependencyChecks = Array.isArray(result.dependencyChecks) ? result.dependencyChecks : [];
    const warnings = Array.isArray(result.warnings) ? result.warnings : [];
    const rows = changes.length ? changes.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}${change.relation ? ` <span class="pill warn">relation</span>` : ""}</td><td>${renderAdminChangeValueCell(result.domain, change, "after", {})}</td><td><span class="pill blocked">삭제 후 없음</span></td></tr>
    `).join("") : `<tr><td colspan="3">삭제 대상 필드 없음</td></tr>`;
    const mismatchRows = mismatches.length ? mismatches.map((item) => `
      <tr><td>${escapeHtml(item.label || item.key)}</td><td>${escapeHtml(formatValue(item.current))}</td><td>${escapeHtml(formatValue(item.expectedAfter))}</td><td>${escapeHtml(formatValue(item.deleteEffect || "blocked"))}</td></tr>
    `).join("") : `<tr><td colspan="4">현재 DB 값이 생성 당시 값과 일치</td></tr>`;
    const dependencyRows = dependencyChecks.length ? dependencyChecks.map((item) => `
      <tr><td>${escapeHtml(formatValue(item.label))}</td><td>${escapeHtml(formatValue(item.target))}</td><td>${escapeHtml(formatValue(item.count))}</td><td><span class="pill ${item.blocksDelete ? "blocked" : "good"}">${item.blocksDelete ? "차단" : "통과"}</span><div class="filter-help">${escapeHtml(formatValue(item.note))}</div></td></tr>
    `).join("") : `<tr><td colspan="4">연결 검사 없음</td></tr>`;
    target.innerHTML = `
      <div class="draft-preview-summary">
        <span class="pill ${result.createDeleteReady ? "good" : "blocked"}">createDeleteReady: ${escapeHtml(formatValue(result.createDeleteReady))}</span>
        <span class="pill ${result.currentMatchesCreateValues ? "good" : "blocked"}">currentMatchesCreateValues: ${escapeHtml(formatValue(result.currentMatchesCreateValues))}</span>
        <span class="pill ${Number(result.dependencyBlockerCount || 0) ? "blocked" : "good"}">dependency blockers: ${escapeHtml(formatValue(result.dependencyBlockerCount || 0))}</span>
        <span class="pill ${result.dryRun ? "warn" : "good"}">dryRun: ${escapeHtml(formatValue(result.dryRun))}</span>
        <span class="pill ${result.writeBlocked ? "blocked" : "good"}">writeBlocked: ${escapeHtml(formatValue(result.writeBlocked))}</span>
        <span class="pill ${result.deleted ? "good" : "warn"}">deleted: ${escapeHtml(formatValue(result.deleted === true))}</span>
        ${result.deleteChangeLogId ? `<span class="pill good">delete log #${escapeHtml(formatValue(result.deleteChangeLogId))}</span>` : ""}
      </div>
      ${warnings.length ? `<div class="filter-help">warnings: ${escapeHtml(warnings.join(", "))}</div>` : ""}
      ${result.note ? `<div class="filter-help">${escapeHtml(result.note)}</div>` : ""}
      <details class="json-detail" open><summary>삭제될 생성 값</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>생성 값</th><th>삭제 후</th></tr></thead><tbody>${rows}</tbody></table></div></details>
      <details class="json-detail" ${mismatches.length ? "open" : ""}><summary>현재값 안전 검사</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>현재 DB 값</th><th>생성 당시 값</th><th>판정</th></tr></thead><tbody>${mismatchRows}</tbody></table></div></details>
      <details class="json-detail" open><summary>연결 데이터 삭제 차단 검사</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>검사</th><th>대상</th><th>개수</th><th>판정</th></tr></thead><tbody>${dependencyRows}</tbody></table></div></details>
    `;
  }

  async function previewAdminCreateDeleteRollback(options) {
    ensureApi();
    const controls = readAdminCreateDeleteControls();
    if (!controls.changeLogId) throw new Error("생성 row 삭제를 검사할 변경 이력 상세를 먼저 열어주세요.");
    const target = $(`[data-admin-create-delete-result]`);
    if (target) target.innerHTML = `<div class="empty">생성 row 삭제 안전 검사 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.previewAdminCreateDeleteRollback({ id: controls.changeLogId, reason: controls.reason || undefined, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreateDeleteResult(payload);
    setStatus(`생성 row 삭제 미리보기: ${formatValue(payload.status)} · ready ${formatValue(payload.createDeleteReady)}`, payload.createDeleteReady ? "ok" : "error");
    return response;
  }

  async function applyAdminCreateDeleteRollback(options) {
    ensureApi();
    const controls = readAdminCreateDeleteControls();
    if (!controls.changeLogId) throw new Error("생성 row 삭제를 적용할 변경 이력 상세를 먼저 열어주세요.");
    requireAdminWriteDevKeyForUi("생성 row 삭제 적용");
    if (!controls.confirmMatches) {
      const error = new Error(`생성 row 삭제 확인 문구를 정확히 입력해야 합니다: ${ADMIN_CREATE_DELETE_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      const target = $(`[data-admin-create-delete-result]`);
      if (target) target.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
      throw error;
    }
    const confirmed = window.confirm("정말 create 이력으로 생성된 row를 DB에서 삭제할까요? 현재값/연결 데이터 안전 검사를 통과해야 적용됩니다.");
    if (!confirmed) {
      setStatus("생성 row 삭제 적용을 취소했습니다.", "info");
      return { ok: false, canceled: true };
    }
    const target = $(`[data-admin-create-delete-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에서 생성 row 삭제를 적용하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : ADMIN_EDIT_APPLY_TIMEOUT_MS;
    const response = await window.RpgGameApi.applyAdminCreateDeleteRollback({ id: controls.changeLogId, confirmText: controls.confirmText, reason: controls.reason || undefined, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreateDeleteResult(payload);
    if (payload.deleted) {
      await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      await refreshAdminMasterCatalog({ filters: readMasterCatalogFiltersFromDom() });
      setStatus(`생성 row 삭제 완료: delete log #${formatValue(payload.deleteChangeLogId)}`, "ok");
    } else {
      setStatus(`생성 row 삭제 실패/차단: ${formatValue(payload.status)}`, "error");
    }
    return response;
  }


  function readAdminCreateDeleteRestoreControls() {
    const card = $(`[data-admin-change-log-detail-card]`);
    const confirmEl = $(`[data-admin-create-delete-restore-confirm]`);
    const reasonEl = $(`[data-admin-create-delete-restore-reason]`);
    return {
      changeLogId: card ? Number(card.getAttribute("data-admin-change-log-id") || 0) : 0,
      confirmText: confirmEl ? confirmEl.value.trim() : "",
      reason: reasonEl ? reasonEl.value.trim() : "",
      confirmMatches: !!confirmEl && confirmEl.value.trim() === ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT,
    };
  }

  function renderAdminCreateDeleteRestoreResult(payload) {
    const target = $(`[data-admin-create-delete-restore-result]`);
    if (!target) return;
    const result = payload || {};
    const changes = Array.isArray(result.changes) ? result.changes : [];
    const validationErrors = Array.isArray(result.validationErrors) ? result.validationErrors : [];
    const warnings = Array.isArray(result.warnings) ? result.warnings : [];
    const rows = changes.length ? changes.map((change) => `
      <tr><td>${escapeHtml(change.label || change.key)}${change.relation ? ` <span class="pill warn">relation</span>` : ""}</td><td><span class="pill blocked">복원 전 없음</span></td><td>${renderAdminChangeValueCell(result.domain, change, "after", {})}</td></tr>
    `).join("") : `<tr><td colspan="3">복원 대상 필드 없음</td></tr>`;
    const errorRows = validationErrors.length ? validationErrors.map((item) => `
      <tr><td>${escapeHtml(item.label || item.key)}</td><td>${escapeHtml(formatValue(item.after))}</td><td>${escapeHtml(formatValue(item.reason || "blocked"))}</td></tr>
    `).join("") : `<tr><td colspan="3">복원 검증 오류 없음</td></tr>`;
    target.innerHTML = `
      <div class="draft-preview-summary">
        <span class="pill ${result.createDeleteRestoreReady ? "good" : "blocked"}">createDeleteRestoreReady: ${escapeHtml(formatValue(result.createDeleteRestoreReady))}</span>
        <span class="pill ${result.targetRowMissing ? "good" : "blocked"}">targetRowMissing: ${escapeHtml(formatValue(result.targetRowMissing))}</span>
        <span class="pill ${result.idConflict ? "blocked" : "good"}">idConflict: ${escapeHtml(formatValue(result.idConflict === true))}</span>
        <span class="pill ${result.codeConflict ? "blocked" : "good"}">codeConflict: ${escapeHtml(formatValue(result.codeConflict === true))}</span>
        <span class="pill ${Number(result.validationErrorCount || 0) ? "blocked" : "good"}">validation errors: ${escapeHtml(formatValue(result.validationErrorCount || 0))}</span>
        <span class="pill ${result.dryRun ? "warn" : "good"}">dryRun: ${escapeHtml(formatValue(result.dryRun))}</span>
        <span class="pill ${result.writeBlocked ? "blocked" : "good"}">writeBlocked: ${escapeHtml(formatValue(result.writeBlocked))}</span>
        <span class="pill ${result.restored ? "good" : "warn"}">restored: ${escapeHtml(formatValue(result.restored === true))}</span>
        ${result.restoreChangeLogId ? `<span class="pill good">restore log #${escapeHtml(formatValue(result.restoreChangeLogId))}</span>` : ""}
      </div>
      ${warnings.length ? `<div class="filter-help">warnings: ${escapeHtml(warnings.join(", "))}</div>` : ""}
      ${result.note ? `<div class="filter-help">${escapeHtml(result.note)}</div>` : ""}
      <details class="json-detail" open><summary>복원될 값</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>복원 전</th><th>복원 후</th></tr></thead><tbody>${rows}</tbody></table></div></details>
      <details class="json-detail" ${validationErrors.length ? "open" : ""}><summary>복원 검증 오류</summary><div class="table-wrap relation-table-wrap"><table><thead><tr><th>필드</th><th>값</th><th>사유</th></tr></thead><tbody>${errorRows}</tbody></table></div></details>
    `;
  }

  async function previewAdminCreateDeleteRestore(options) {
    ensureApi();
    const controls = readAdminCreateDeleteRestoreControls();
    if (!controls.changeLogId) throw new Error("복원할 create_delete 변경 이력 상세를 먼저 열어주세요.");
    const target = $(`[data-admin-create-delete-restore-result]`);
    if (target) target.innerHTML = `<div class="empty">삭제 row 복원 안전 검사 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : DEFAULT_TIMEOUT_MS;
    const response = await window.RpgGameApi.previewAdminCreateDeleteRestore({ id: controls.changeLogId, reason: controls.reason || undefined, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreateDeleteRestoreResult(payload);
    setStatus(`삭제 row 복원 미리보기: ${formatValue(payload.status)} · ready ${formatValue(payload.createDeleteRestoreReady)}`, payload.createDeleteRestoreReady ? "ok" : "error");
    return response;
  }

  async function applyAdminCreateDeleteRestore(options) {
    ensureApi();
    const controls = readAdminCreateDeleteRestoreControls();
    if (!controls.changeLogId) throw new Error("복원할 create_delete 변경 이력 상세를 먼저 열어주세요.");
    requireAdminWriteDevKeyForUi("삭제 row 복원 적용");
    if (!controls.confirmMatches) {
      const error = new Error(`삭제 row 복원 확인 문구를 정확히 입력해야 합니다: ${ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT}`);
      setStatus(error.message, "error");
      const target = $(`[data-admin-create-delete-restore-result]`);
      if (target) target.innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
      throw error;
    }
    const confirmed = window.confirm("정말 create_delete 이력으로 삭제된 row를 DB에 다시 복원할까요? id/code 충돌 검사를 통과해야 적용됩니다.");
    if (!confirmed) {
      setStatus("삭제 row 복원 적용을 취소했습니다.", "info");
      return { ok: false, canceled: true };
    }
    const target = $(`[data-admin-create-delete-restore-result]`);
    if (target) target.innerHTML = `<div class="empty">백엔드에서 삭제 row 복원을 적용하는 중...</div>`;
    const timeoutMs = options && options.timeoutMs !== undefined ? options.timeoutMs : ADMIN_EDIT_APPLY_TIMEOUT_MS;
    const response = await window.RpgGameApi.applyAdminCreateDeleteRestore({ id: controls.changeLogId, confirmText: controls.confirmText, reason: controls.reason || undefined, timeoutMs });
    const payload = response && response.payload ? response.payload : {};
    renderAdminCreateDeleteRestoreResult(payload);
    if (payload.restored) {
      await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      await refreshAdminMasterCatalog({ filters: readMasterCatalogFiltersFromDom() });
      await runPostWriteMasterApiVerification(payload.domain, payload.id, {
        label: "생성 row 복원",
        contextLabel: `restore log #${formatValue(payload.restoreChangeLogId)} 적용 후 자동 확인`,
      });
      setStatus(`삭제 row 복원 완료: restore log #${formatValue(payload.restoreChangeLogId)}`, "ok");
    } else {
      setStatus(`삭제 row 복원 실패/차단: ${formatValue(payload.status)}`, "error");
    }
    return response;
  }

  async function refreshAdminChangeLogs(options) {
    ensureApi();
    const opts = options || {};
    const filters = opts.filters || readChangeLogFiltersFromDom();
    const target = $(`[data-admin-change-log-table]`);
    if (target) target.innerHTML = `<div class="empty">변경 이력 불러오는 중...</div>`;
    const response = await window.RpgGameApi.listAdminChangeLogs({
      ...filters,
      timeoutMs: opts.timeoutMs !== undefined ? opts.timeoutMs : DEFAULT_TIMEOUT_MS,
    });
    const payload = response && response.payload ? response.payload : {};
    renderAdminChangeLogs(payload);
    setStatus(`변경 이력 로드 · ${describeChangeLogFilters(filters)}`, "ok");
    return response;
  }

  function renderReadiness(readiness) {
    const target = $("[data-admin-readiness]");
    if (!target) return;
    const warnings = Array.isArray(readiness.warnings) ? readiness.warnings : [];
    target.innerHTML = `
      <div style="padding:14px; display:grid; gap:10px;">
        <div><span class="pill ${readiness.safeForAdminReadOnlyUi ? "good" : "warn"}">read-only UI: ${escapeHtml(formatValue(readiness.safeForAdminReadOnlyUi))}</span></div>
        <div><span class="pill ${readiness.safeForAdminWriteUi ? "warn" : "blocked"}">general write UI: ${escapeHtml(formatValue(readiness.safeForAdminWriteUi))}</span></div>
        <div><span class="pill ${readiness.guardedMasterEditApplyReady ? "good" : "blocked"}">guarded master edit apply: ${escapeHtml(formatValue(readiness.guardedMasterEditApplyReady))}</span></div>
        <div><span class="pill ${readiness.guardedRollbackReady ? "good" : "blocked"}">guarded rollback: ${escapeHtml(formatValue(readiness.guardedRollbackReady))}</span></div>
        <div><span class="pill ${hasAdminWriteDevKey() ? "good" : "blocked"}">admin write dev key: ${escapeHtml(hasAdminWriteDevKey() ? "set" : "missing")}</span></div>
        <div style="color:#cbd5e1; font-size:13px;">${escapeHtml(readiness.writeUiBlockedReason || "일반 쓰기 기능은 아직 막혀 있습니다.")}</div>
        ${warnings.length ? `<div class="error">경고: ${escapeHtml(warnings.join(", "))}</div>` : `<div style="color:#86efac; font-size:13px;">현재 read-only overview 기준 경고 없음</div>`}
      </div>
    `;
  }

  function renderError(error) {
    const message = error && error.message ? error.message : String(error);
    const cards = $("[data-admin-cards]");
    const master = $("[data-admin-master-table]");
    const snapshots = $("[data-admin-snapshot-table]");
    const catalog = $("[data-admin-master-catalog-table]");
    const detail = $("[data-admin-master-detail]");
    const readiness = $("[data-admin-readiness]");
    if (cards) cards.innerHTML = `<div class="card"><div class="label">오류</div><div class="value small">API 연결 실패</div></div>`;
    if (master) master.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
    if (snapshots) snapshots.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
    if (catalog) catalog.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
    if (detail) detail.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
    if (readiness) readiness.innerHTML = `<div class="error">백엔드가 켜져 있는지, API URL이 맞는지 확인하세요.</div>`;
    setStatus(`불러오기 실패: ${message}`, "error");
  }

  async function refreshAdminReadOnlyPage(options) {
    syncApiInput();
    setStatus("불러오는 중...", "loading");
    try {
      const result = await fetchAdminReadOnlyPageData(options || {});
      const overviewPayload = result.overview && result.overview.payload ? result.overview.payload : {};
      const snapshotPayload = result.snapshots && result.snapshots.payload ? result.snapshots.payload : {};
      const masterDomainsPayload = result.masterDomains && result.masterDomains.payload ? result.masterDomains.payload : {};
      const masterCatalogPayload = result.masterCatalog && result.masterCatalog.payload ? result.masterCatalog.payload : {};
      const changeLogPayload = result.changeLogs && result.changeLogs.payload ? result.changeLogs.payload : {};
      const createBlueprintPayload = result.createBlueprint && result.createBlueprint.payload ? result.createBlueprint.payload : {};
      renderCards(overviewPayload);
      renderMasterTable(overviewPayload.masterData || {});
      syncMasterDomainOptions(masterDomainsPayload);
      renderMasterCatalogTable(masterCatalogPayload);
      renderAdminCreateBlueprint(createBlueprintPayload);
      renderSnapshotTable(snapshotPayload);
      renderAdminChangeLogs(changeLogPayload);
      renderReadiness(overviewPayload.readiness || {});
      const filterText = describeSnapshotFilters(result.snapshotFilters || (snapshotPayload && snapshotPayload.filters));
      const masterFilterText = describeMasterCatalogFilters(result.masterCatalogFilters || (masterCatalogPayload && masterCatalogPayload.filters));
      const changeFilterText = describeChangeLogFilters(result.changeLogFilters || (changeLogPayload && changeLogPayload.filters));
      const createFilterText = result.createBlueprintFilters && result.createBlueprintFilters.domain ? ` · 생성설계 domain=${result.createBlueprintFilters.domain}` : "";
      setStatus(`정상 로드 · ${formatClock(new Date().toISOString())} · 세이브 ${filterText} · 마스터 ${masterFilterText} · 이력 ${changeFilterText}${createFilterText} · API ${window.RpgGameApi.getApiBaseUrl()}`, "ok");
      return { ok: true, ...result };
    } catch (error) {
      renderError(error);
      return { ok: false, error };
    }
  }

  function saveApiBaseUrlFromInput() {
    ensureApi();
    const input = getApiInput();
    const value = input ? input.value.trim() : "";
    const next = window.RpgGameApi.setApiBaseUrl(value);
    syncApiInput();
    setStatus(`API URL 저장됨: ${next}`, "ok");
    return next;
  }

  function resetApiBaseUrl() {
    ensureApi();
    const next = window.RpgGameApi.setApiBaseUrl(window.RpgGameApi.DEFAULT_API_BASE_URL);
    syncApiInput();
    setStatus(`API URL 기본값 복구: ${next}`, "ok");
    return next;
  }


  function getAdminDefaultCollapsedSectionSet() {
    return new Set(ADMIN_DEFAULT_COLLAPSED_SECTION_KEYS.map(String));
  }

  function readAdminCollapsedSectionSet() {
    try {
      const raw = window.localStorage ? window.localStorage.getItem(ADMIN_LAYOUT_COLLAPSE_STORAGE_KEY) : null;
      if (!raw) return getAdminDefaultCollapsedSectionSet();
      const values = JSON.parse(raw);
      return new Set(Array.isArray(values) ? values.map(String) : []);
    } catch (_) {
      return getAdminDefaultCollapsedSectionSet();
    }
  }

  function writeAdminCollapsedSectionSet(keys) {
    try {
      if (!window.localStorage) return false;
      window.localStorage.setItem(ADMIN_LAYOUT_COLLAPSE_STORAGE_KEY, JSON.stringify(Array.from(keys || [])));
      return true;
    } catch (_) {
      return false;
    }
  }

  function getAdminCollapsibleSectionKey(section) {
    if (!section) return "";
    return section.getAttribute("data-admin-section-key") || section.id || "";
  }

  function setAdminSectionCollapsed(section, collapsed, options) {
    if (!section) return false;
    const key = getAdminCollapsibleSectionKey(section);
    const button = section.querySelector("[data-admin-layout-collapse-toggle]");
    section.classList.toggle("admin-section-collapsed", !!collapsed);
    section.setAttribute("data-admin-section-collapsed", collapsed ? "true" : "false");
    if (button) {
      button.textContent = collapsed ? "펼치기" : "접기";
      button.setAttribute("aria-expanded", collapsed ? "false" : "true");
      button.setAttribute("aria-label", `${key || "section"} ${collapsed ? "펼치기" : "접기"}`);
    }
    if (!options || !options.silent) {
      const collapsedSet = readAdminCollapsedSectionSet();
      if (collapsed) collapsedSet.add(key);
      else collapsedSet.delete(key);
      writeAdminCollapsedSectionSet(collapsedSet);
    }
    return true;
  }

  function ensureAdminSectionCollapseControl(section, collapsedSet) {
    if (!section || section.querySelector("[data-admin-layout-collapse-toggle]")) return false;
    const key = getAdminCollapsibleSectionKey(section);
    const header = section.querySelector(":scope > .section-header") || section.querySelector(":scope > .filter-title");
    if (!header) return false;
    header.classList.add("admin-collapse-header");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn mini admin-collapse-toggle";
    button.setAttribute("data-admin-layout-collapse-toggle", key);
    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      setAdminSectionCollapsed(section, !section.classList.contains("admin-section-collapsed"));
    });
    header.appendChild(button);
    setAdminSectionCollapsed(section, collapsedSet && collapsedSet.has(key), { silent: true });
    return true;
  }

  function setAdminActiveSidebarLink(hash) {
    const links = Array.from(document.querySelectorAll(".admin-jump-nav a[href^='#']"));
    const nextHash = hash || window.location.hash || "#section-overview";
    links.forEach((link) => {
      const active = link.getAttribute("href") === nextHash;
      link.classList.toggle("active", active);
      if (active) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
    return nextHash;
  }

  function updateAdminStickyLayoutOffsets() {
    const header = document.querySelector("[data-admin-sticky-header]") || document.querySelector(".topbar");
    const height = header && header.getBoundingClientRect ? Math.ceil(header.getBoundingClientRect().height) : 112;
    const stickyTop = Math.max(96, height + 18);
    const scrollMargin = stickyTop + 18;
    document.documentElement.style.setProperty("--admin-sticky-top", `${stickyTop}px`);
    document.documentElement.style.setProperty("--admin-scroll-margin-top", `${scrollMargin}px`);
    return { height, stickyTop, scrollMargin };
  }

  function initializeAdminLayoutShell() {
    const stickyOffsets = updateAdminStickyLayoutOffsets();
    const collapsedSet = readAdminCollapsedSectionSet();
    const sections = Array.from(document.querySelectorAll("[data-admin-collapsible]"));
    sections.forEach((section) => ensureAdminSectionCollapseControl(section, collapsedSet));
    setAdminActiveSidebarLink(window.location.hash || "#section-overview");
    if (!window.__upgradeRpgAdminLayoutHashBound) {
      window.__upgradeRpgAdminLayoutHashBound = true;
      window.addEventListener("hashchange", () => setAdminActiveSidebarLink(window.location.hash || "#section-overview"));
      window.addEventListener("resize", () => updateAdminStickyLayoutOffsets());
      document.addEventListener("click", (event) => {
        const link = event.target && event.target.closest ? event.target.closest(".admin-jump-nav a[href^='#']") : null;
        if (!link) return;
        setTimeout(() => setAdminActiveSidebarLink(link.getAttribute("href")), 0);
      });
    }
    const readiness = getAdminLayoutShellReadiness();
    readiness.stickyOffsets = stickyOffsets;
    return readiness;
  }

  function getAdminLayoutShellReadiness() {
    const collapsibleCount = document.querySelectorAll("[data-admin-collapsible]").length;
    const collapseToggleCount = document.querySelectorAll("[data-admin-layout-collapse-toggle]").length;
    const defaultCollapsedKeys = Array.from(getAdminDefaultCollapsedSectionSet());
    const defaultCollapsedReady = defaultCollapsedKeys.every((key) => {
      const section = document.querySelector(`[data-admin-section-key="${key}"]`);
      return !!section && section.classList.contains("admin-section-collapsed");
    });
    const stickyTop = getComputedStyle(document.documentElement).getPropertyValue("--admin-sticky-top").trim();
    const collapsedPanelHeaderCount = document.querySelectorAll(".filter-panel[data-admin-collapsible] > .filter-title.admin-collapse-header, .field-help-panel[data-admin-collapsible] > .filter-title.admin-collapse-header").length;
    const collapsedPanelStyleReady = collapsedPanelHeaderCount >= document.querySelectorAll(".filter-panel[data-admin-collapsible], .field-help-panel[data-admin-collapsible]").length;
    const result = {
      layoutReady: !!document.querySelector("[data-admin-layout-shell]"),
      sidebarReady: !!document.querySelector("[data-admin-sidebar]"),
      mainContentReady: !!document.querySelector("[data-admin-main-content]"),
      footerReady: !!document.querySelector("[data-admin-footer]"),
      collapsibleCount,
      collapseToggleCount,
      collapseReady: collapsibleCount > 0 && collapseToggleCount >= collapsibleCount,
      collapsedPanelHeaderCount,
      collapsedPanelStyleReady,
      activeNavReady: !!document.querySelector(".admin-jump-nav a.active, .admin-jump-nav a[aria-current='location']"),
      defaultCollapsedKeys,
      defaultCollapsedReady,
      stickyTop,
      stickyOffsetReady: !!stickyTop && stickyTop !== "92px",
    };
    result.ok = result.layoutReady && result.sidebarReady && result.mainContentReady && result.footerReady && result.collapseReady && result.collapsedPanelStyleReady && result.stickyOffsetReady;
    return result;
  }

  function bindEvents() {
    document.addEventListener("input", (event) => {
      if (event.target && event.target.matches && event.target.matches("[data-admin-create-relation-option-filter]")) {
        applyAdminCreateRelationOptionFilter(event.target);
        return;
      }
      if (event.target && event.target.matches && event.target.matches("[data-admin-relation-option-filter]")) {
        applyAdminRelationOptionFilter(event.target);
        return;
      }
      if (event.target && event.target.closest && event.target.closest("[data-admin-edit-draft]") && event.target.getAttribute && event.target.getAttribute("data-admin-edit-draft-field")) {
        refreshAdminEditImpactGuide();
      }
      if (event.target && event.target.closest && event.target.closest("[data-admin-create-draft]") && event.target.getAttribute && event.target.getAttribute("data-admin-create-draft-field")) {
        const result = $(`[data-admin-create-draft-result]`);
        if (result) result.innerHTML = `<div class="empty">초안 값이 바뀌었습니다. 다시 생성 초안 검증을 누르세요.</div>`;
      }
      if (event.target && event.target.matches && event.target.matches("[data-admin-master-query]")) {
        syncMasterCatalogPageInput(1);
      }
    });
    document.addEventListener("keydown", async (event) => {
      if (event.key !== "Enter" || !(event.target && event.target.matches)) return;
      if (event.target.matches("[data-admin-master-query], [data-admin-master-page]")) {
        event.preventDefault();
        await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom() });
      }
    });
    document.addEventListener("change", (event) => {
      if (event.target && event.target.matches && event.target.matches("[data-admin-master-domain], [data-admin-master-limit], [data-admin-master-enabled], [data-admin-master-sort]")) {
        syncMasterCatalogPageInput(1);
      }
      if (event.target && event.target.closest && event.target.closest("[data-admin-edit-draft]") && event.target.getAttribute && event.target.getAttribute("data-admin-edit-draft-field")) {
        const changedKey = event.target.getAttribute("data-admin-edit-draft-field");
        if (changedKey) refreshDependentAdminRelationSelects(changedKey);
        refreshAdminEditImpactGuide();
      }
      if (event.target && event.target.closest && event.target.closest("[data-admin-create-draft]") && event.target.getAttribute && event.target.getAttribute("data-admin-create-draft-field")) {
        const changedKey = event.target.getAttribute("data-admin-create-draft-field");
        if (changedKey) refreshDependentAdminCreateRelationSelects(changedKey);
      }
    });
    document.addEventListener("click", async (event) => {
      const button = event.target && event.target.closest ? event.target.closest("[data-admin-action]") : null;
      if (!button) return;
      const action = button.getAttribute("data-admin-action");
      if (action === "refresh") await refreshAdminReadOnlyPage();
      if (action === "apply-snapshot-filters") await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom() });
      if (action === "apply-master-catalog-filters") await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom(), createBlueprintFilters: readAdminCreateBlueprintFiltersFromDom() });
      if (action === "load-create-blueprint") {
        try {
          await refreshAdminCreateBlueprint(readAdminCreateBlueprintFiltersFromDom());
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "sync-create-domain-from-catalog") {
        try {
          const filters = syncAdminCreateDomainFromCatalog();
          await refreshAdminCreateBlueprint(filters);
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "preview-admin-create-draft") {
        try {
          await previewAdminCreateDraft();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "reset-admin-create-draft") {
        resetAdminCreateDraft();
      }
      if (action === "apply-admin-create-draft") {
        try {
          await applyAdminCreateDraft();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "master-catalog-first-page") await refreshMasterCatalogWithPage(1);
      if (action === "master-catalog-prev-page") {
        const current = readMasterCatalogFiltersFromDom().page || 1;
        await refreshMasterCatalogWithPage(Math.max(1, current - 1));
      }
      if (action === "master-catalog-next-page") {
        const current = readMasterCatalogFiltersFromDom().page || 1;
        await refreshMasterCatalogWithPage(current + 1);
      }
      if (action === "master-catalog-last-page") {
        const totalPages = Number(button.getAttribute("data-admin-master-total-pages")) || 1;
        await refreshMasterCatalogWithPage(totalPages);
      }
      if (action === "apply-change-log-filters") await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      if (action === "open-master-detail") {
        const domain = button.getAttribute("data-admin-detail-domain");
        const id = button.getAttribute("data-admin-detail-id");
        try {
          await openAdminMasterDataDetail(domain, id);
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "open-master-detail-by-code") {
        const domain = button.getAttribute("data-admin-detail-domain");
        const code = button.getAttribute("data-admin-detail-code");
        try {
          await openAdminMasterDataDetailByCode(domain, code);
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "open-master-relations") {
        const domain = button.getAttribute("data-admin-relation-domain");
        const id = button.getAttribute("data-admin-relation-id");
        try {
          await openAdminMasterDataRelations(domain, id);
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "preview-admin-edit-draft") {
        try {
          await previewAdminEditDraft();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "apply-admin-edit-draft") {
        try {
          await applyAdminEditDraft();
        } catch (error) {
          // applyAdminEditDraft already renders user-facing validation errors.
          if (!(error && (String(error.message || "").includes("확인 문구") || String(error.message || "").includes("dev key")))) renderError(error);
        }
      }
      if (action === "refresh-admin-change-logs") {
        try {
          await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "open-admin-change-log-detail") {
        try {
          await openAdminChangeLogDetail(button.getAttribute("data-admin-change-log-id"));
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "preview-admin-change-log-rollback") {
        try {
          await previewAdminChangeLogRollback();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "apply-admin-change-log-rollback") {
        try {
          await applyAdminChangeLogRollback();
        } catch (error) {
          if (!(error && (String(error.message || "").includes("확인 문구") || String(error.message || "").includes("dev key")))) renderError(error);
        }
      }
      if (action === "preview-admin-create-delete") {
        try {
          await previewAdminCreateDeleteRollback();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "apply-admin-create-delete") {
        try {
          await applyAdminCreateDeleteRollback();
        } catch (error) {
          if (!(error && (String(error.message || "").includes("확인 문구") || String(error.message || "").includes("dev key")))) renderError(error);
        }
      }
      if (action === "preview-admin-create-delete-restore") {
        try {
          await previewAdminCreateDeleteRestore();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "apply-admin-create-delete-restore") {
        try {
          await applyAdminCreateDeleteRestore();
        } catch (error) {
          if (!(error && (String(error.message || "").includes("확인 문구") || String(error.message || "").includes("dev key")))) renderError(error);
        }
      }
      if (action === "verify-master-api-target") {
        try {
          await verifySelectedMasterDataApi();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "reset-admin-edit-draft") {
        resetAdminEditDraft();
      }
      if (action === "reset-master-catalog-filters") {
        resetMasterCatalogFilters();
        await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom() });
      }
      if (action === "reset-snapshot-filters") {
        resetSnapshotFilters();
        await refreshAdminReadOnlyPage({ snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom() });
      }
      if (action === "reset-change-log-filters") {
        resetChangeLogFilters();
        await refreshAdminChangeLogs({ filters: readChangeLogFiltersFromDom() });
      }
      if (action === "save-admin-write-dev-key") {
        try {
          saveAdminWriteDevKeyFromInput();
        } catch (error) {
          renderAdminWriteKeyStatus();
        }
      }
      if (action === "clear-admin-write-dev-key") {
        clearAdminWriteDevKey();
      }
      if (action === "save-api-base-url") {
        try {
          saveApiBaseUrlFromInput();
          await refreshAdminReadOnlyPage();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "reset-api-base-url") {
        try {
          resetApiBaseUrl();
          await refreshAdminReadOnlyPage();
        } catch (error) {
          renderError(error);
        }
      }
      if (action === "copy-admin-url") {
        await copyCurrentAdminPageUrl();
      }
    });
  }

  function bootAdminReadOnlyPage() {
    bindEvents();
    initializeAdminLayoutShell();
    syncLocationHints();
    syncApiInput();
    syncAdminWriteDevKeyInput();
    resetSnapshotFilters({ silent: true });
    resetMasterCatalogFilters({ silent: true });
    resetChangeLogFilters({ silent: true });
    renderMasterDetail({});
    renderAdminCreateBlueprint({});
    refreshAdminReadOnlyPage();
  }

  function checkAdminReadOnlyPageReady(options) {
    const apiReady = !!(window.RpgGameApi && typeof window.RpgGameApi.fetchAdminOverview === "function" && typeof window.RpgGameApi.listAdminSaveSnapshots === "function" && typeof window.RpgGameApi.listAdminMasterCatalogRows === "function" && typeof window.RpgGameApi.fetchAdminMasterCreateBlueprint === "function" && typeof window.RpgGameApi.previewAdminMasterDataCreate === "function" && typeof window.RpgGameApi.applyAdminMasterDataCreate === "function" && typeof window.RpgGameApi.fetchAdminMasterDataDetail === "function" && typeof window.RpgGameApi.fetchAdminMasterDataRelations === "function" && typeof window.RpgGameApi.previewAdminMasterDataEdit === "function" && typeof window.RpgGameApi.applyAdminMasterDataEdit === "function" && typeof window.RpgGameApi.listAdminChangeLogs === "function" && typeof window.RpgGameApi.fetchAdminChangeLogDetail === "function" && typeof window.RpgGameApi.previewAdminChangeLogRollback === "function" && typeof window.RpgGameApi.applyAdminChangeLogRollback === "function" && typeof window.RpgGameApi.previewAdminCreateDeleteRollback === "function" && typeof window.RpgGameApi.applyAdminCreateDeleteRollback === "function" && typeof window.RpgGameApi.previewAdminCreateDeleteRestore === "function" && typeof window.RpgGameApi.applyAdminCreateDeleteRestore === "function" && typeof window.RpgGameApi.setAdminWriteDevKey === "function" && typeof window.RpgGameApi.hasAdminWriteDevKey === "function");
    const domReady = !!document.querySelector("[data-admin-cards]");
    const locationHintReady = !!document.querySelector("[data-admin-current-url]");
    const snapshotFilterReady = !!document.querySelector("[data-admin-filter-slot-key]");
    const masterCatalogReady = !!document.querySelector("[data-admin-master-domain]");
    const createBlueprintReady = !!document.querySelector("[data-admin-create-blueprint]") && typeof renderAdminCreateBlueprint === "function" && typeof getAdminCreateBlueprintReadiness === "function";
    const createDraftPreviewReady = typeof previewAdminCreateDraft === "function" && !!(window.RpgGameApi && typeof window.RpgGameApi.previewAdminMasterDataCreate === "function");
    const createApplyReady = typeof applyAdminCreateDraft === "function" && !!(window.RpgGameApi && typeof window.RpgGameApi.applyAdminMasterDataCreate === "function");
    const masterDetailReady = !!document.querySelector("[data-admin-master-detail]");
    const masterRelationsReady = true;
    const editDraftReady = !!document.querySelector("[data-admin-edit-draft]");
    const fieldHelpReady = !!document.querySelector("[data-admin-field-help]");
    const adminChangeLogReady = !!document.querySelector("[data-admin-change-log-table]");
    const adminChangeLogDetailReady = !!document.querySelector("[data-admin-change-log-detail]");
    const adminChangeLogFilterReady = !!document.querySelector("[data-admin-change-log-filter-changed-key]");
    const masterApiVerifyReady = typeof verifySelectedMasterDataApi === "function";
    const postWriteApiVerifyReady = typeof runPostWriteMasterApiVerification === "function";
    const adminWriteGuardReady = !!document.querySelector("[data-admin-write-dev-key]") && !!document.querySelector("[data-admin-write-key-status]");
    const relationSearchReady = typeof applyAdminRelationOptionFilter === "function" && typeof filterAdminDraftSelectOptions === "function";
    const relationPreviewReady = typeof formatAdminChangeValueText === "function" && typeof getAdminRelationValueDisplay === "function" && typeof openAdminMasterDataDetailByCode === "function";
    const changeLogRelationReady = typeof getAdminChangeRelationInfo === "function" && typeof renderAdminRollbackMismatchValueCell === "function" && typeof getAdminRelationOpenTargetFromChange === "function";
    const createDeleteRollbackReady = typeof previewAdminCreateDeleteRollback === "function" && typeof applyAdminCreateDeleteRollback === "function" && !!(window.RpgGameApi && typeof window.RpgGameApi.previewAdminCreateDeleteRollback === "function");
    const createDeleteRestoreReady = typeof previewAdminCreateDeleteRestore === "function" && typeof applyAdminCreateDeleteRestore === "function" && !!(window.RpgGameApi && typeof window.RpgGameApi.previewAdminCreateDeleteRestore === "function");
    const layoutShell = getAdminLayoutShellReadiness();
    const result = { ok: apiReady && domReady && snapshotFilterReady && masterCatalogReady && masterDetailReady && adminChangeLogFilterReady && masterApiVerifyReady && adminWriteGuardReady && layoutShell.ok, version: VERSION, apiReady, domReady, locationHintReady, snapshotFilterReady, masterCatalogReady, masterDetailReady, masterRelationsReady, editDraftReady, fieldHelpReady, adminChangeLogReady, adminChangeLogDetailReady, adminChangeLogFilterReady, masterApiVerifyReady, postWriteApiVerifyReady, adminWriteGuardReady, relationSearchReady, relationPreviewReady, changeLogRelationReady, createBlueprintReady, createDraftPreviewReady, createApplyReady, createDeleteRollbackReady, createDeleteRestoreReady, layoutShellReady: layoutShell.ok, layoutShell, createBlueprint: getAdminCreateBlueprintReadiness(), adminWriteDevKeySet: hasAdminWriteDevKey(), readOnly: false, writeLocked: !hasAdminWriteDevKey(), guardedApply: true, adminPageUrl: getCurrentAdminPageUrl(), gamePageUrl: getGamePageUrl(), snapshotFilters: readSnapshotFiltersFromDom(), masterCatalogFilters: readMasterCatalogFiltersFromDom(), changeLogFilters: readChangeLogFiltersFromDom(), editDraft: getAdminEditDraftReadiness({ log: false }) };
    if (!options || options.log !== false) console.log("[Upgrade RPG] admin read-only page check", result);
    return result;
  }

  window.RpgAdminReadOnlyPage = {
    VERSION,
    refreshAdminReadOnlyPage,
    fetchAdminReadOnlyPageData,
    saveApiBaseUrlFromInput,
    resetApiBaseUrl,
    getCurrentAdminPageUrl,
    getGamePageUrl,
    syncLocationHints,
    copyCurrentAdminPageUrl,
    readSnapshotFiltersFromDom,
    resetSnapshotFilters,
    describeSnapshotFilters,
    readMasterCatalogFiltersFromDom,
    resetMasterCatalogFilters,
    describeMasterCatalogFilters,
    readChangeLogFiltersFromDom,
    resetChangeLogFilters,
    describeChangeLogFilters,
    readAdminCreateBlueprintFiltersFromDom,
    syncAdminCreateDomainFromCatalog,
    refreshAdminCreateBlueprint,
    renderAdminCreateBlueprint,
    getAdminCreateBlueprintFieldInputKind,
    getAdminCreateBlueprintRequiredKeys,
    getAdminCreateBlueprintDefaultDraft,
    getAdminCreateBlueprintReadiness,
    readAdminCreateDraftValues,
    resetAdminCreateDraft,
    previewAdminCreateDraft,
    applyAdminCreateDraft,
    renderAdminCreatePreviewResult,
    getAdminCreateFieldDefinition,
    getAdminCreateRelationDefinition,
    applyAdminCreateRelationOptionFilter,
    refreshDependentAdminCreateRelationSelects,
    openAdminMasterDataDetail,
    openAdminMasterDataDetailByCode,
    openAdminMasterDataRelations,
    renderMasterDetail,
    renderMasterRelations,
    renderMasterEditDraft,
    readAdminEditDraftValues,
    resetAdminEditDraft,
    previewAdminEditDraft,
    applyAdminEditDraft,
    renderAdminEditPreviewResult,
    readAdminEditApplyControls,
    buildAdminEditImpactGuide,
    renderAdminEditDraftReview,
    buildAdminEditDraftReview,
    sortAdminChangesByRisk,
    renderAdminEditImpactGuide,
    refreshAdminEditImpactGuide,
    getAdminEditDraftReadiness,
    refreshAdminChangeLogs,
    renderAdminChangeLogs,
    openAdminChangeLogDetail,
    renderAdminChangeLogDetail,
    previewAdminChangeLogRollback,
    applyAdminChangeLogRollback,
    readAdminRollbackControls,
    renderAdminRollbackResult,
    previewAdminCreateDeleteRollback,
    applyAdminCreateDeleteRollback,
    readAdminCreateDeleteControls,
    renderAdminCreateDeleteResult,
    previewAdminCreateDeleteRestore,
    applyAdminCreateDeleteRestore,
    readAdminCreateDeleteRestoreControls,
    renderAdminCreateDeleteRestoreResult,
    syncAdminWriteDevKeyInput,
    saveAdminWriteDevKeyFromInput,
    clearAdminWriteDevKey,
    hasAdminWriteDevKey,
    verifySelectedMasterDataApi,
    runPostWriteMasterApiVerification,
    renderMasterApiVerifyResult,
    findMasterApiRow,
    buildMasterApiVerifyComparisons,
    getAdminFieldHelp,
    listAdminFieldHelp,
    getAdminFieldValueHint,
    renderFieldValueHintInline,
    isAdminEditApplyAllowedField,
    getAdminEditAllowedFields,
    getAdminDraftFieldInputKind,
    getAdminDraftSelectOptions,
    getAdminRelationEditOptionDefinitions,
    getAdminRelationEditOptionDefinition,
    isAdminRelationEditField,
    getAdminRelationComboGuardLabels,
    refreshDependentAdminRelationSelects,
    applyAdminRelationOptionFilter,
    clearAdminRelationOptionFilter,
    filterAdminDraftSelectOptions,
    renderAdminDraftSelectOptionsHtml,
    getAdminRelationSelectMetaText,
    renderAdminRelationEditOptionsNote,
    getAdminEquipSlotDisplayName,
    getAdminDraftFieldRisk,
    getAdminRelationOpenTarget,
    getAdminChangeRelationInfo,
    getAdminRelationOpenTargetFromChange,
    renderAdminRollbackMismatchValueCell,
    getAdminDraftLockedReason,
    initializeAdminLayoutShell,
    getAdminLayoutShellReadiness,
    setAdminSectionCollapsed,
    setAdminActiveSidebarLink,
    checkAdminReadOnlyPageReady,
  };
  window.refreshAdminReadOnlyPage = refreshAdminReadOnlyPage;
  window.fetchAdminReadOnlyPageData = fetchAdminReadOnlyPageData;
  window.readAdminSnapshotFilters = readSnapshotFiltersFromDom;
  window.resetAdminSnapshotFilters = resetSnapshotFilters;
  window.readAdminMasterCatalogFilters = readMasterCatalogFiltersFromDom;
  window.resetAdminMasterCatalogFilters = resetMasterCatalogFilters;
  window.readAdminChangeLogFilters = readChangeLogFiltersFromDom;
  window.resetAdminChangeLogFilters = resetChangeLogFilters;
  window.readAdminCreateBlueprintFilters = readAdminCreateBlueprintFiltersFromDom;
  window.syncAdminCreateDomainFromCatalog = syncAdminCreateDomainFromCatalog;
  window.refreshAdminCreateBlueprint = refreshAdminCreateBlueprint;
  window.getAdminCreateBlueprintFieldInputKind = getAdminCreateBlueprintFieldInputKind;
  window.getAdminCreateBlueprintRequiredKeys = getAdminCreateBlueprintRequiredKeys;
  window.getAdminCreateBlueprintDefaultDraft = getAdminCreateBlueprintDefaultDraft;
  window.getAdminCreateBlueprintReadiness = getAdminCreateBlueprintReadiness;
  window.readAdminCreateDraftValues = readAdminCreateDraftValues;
  window.resetAdminCreateDraft = resetAdminCreateDraft;
  window.previewAdminCreateDraft = previewAdminCreateDraft;
  window.applyAdminCreateDraft = applyAdminCreateDraft;
  window.getAdminCreateFieldDefinition = getAdminCreateFieldDefinition;
  window.getAdminCreateRelationDefinition = getAdminCreateRelationDefinition;
  window.applyAdminCreateRelationOptionFilter = applyAdminCreateRelationOptionFilter;
  window.refreshDependentAdminCreateRelationSelects = refreshDependentAdminCreateRelationSelects;
  window.refreshAdminChangeLogs = refreshAdminChangeLogs;
  window.openAdminMasterDataDetail = openAdminMasterDataDetail;
  window.openAdminMasterDataDetailByCode = openAdminMasterDataDetailByCode;
  window.openAdminMasterDataRelations = openAdminMasterDataRelations;
  window.checkAdminReadOnlyPageReady = checkAdminReadOnlyPageReady;
  window.initializeAdminLayoutShell = initializeAdminLayoutShell;
  window.getAdminLayoutShellReadiness = getAdminLayoutShellReadiness;
  window.getAdminDefaultCollapsedSectionKeys = () => Array.from(getAdminDefaultCollapsedSectionSet());
  window.updateAdminStickyLayoutOffsets = updateAdminStickyLayoutOffsets;
  window.setAdminSectionCollapsed = setAdminSectionCollapsed;
  window.setAdminActiveSidebarLink = setAdminActiveSidebarLink;
  window.getAdminEditDraftReadiness = getAdminEditDraftReadiness;
  window.syncAdminWriteDevKeyInput = syncAdminWriteDevKeyInput;
  window.saveAdminWriteDevKeyFromInput = saveAdminWriteDevKeyFromInput;
  window.clearAdminWriteDevKey = clearAdminWriteDevKey;
  window.hasAdminWriteDevKey = hasAdminWriteDevKey;
  window.readAdminEditDraftValues = readAdminEditDraftValues;
  window.resetAdminEditDraft = resetAdminEditDraft;
  window.previewAdminEditDraft = previewAdminEditDraft;
  window.buildAdminEditImpactGuide = buildAdminEditImpactGuide;
  window.refreshAdminEditImpactGuide = refreshAdminEditImpactGuide;
  window.getAdminFieldHelp = getAdminFieldHelp;
  window.listAdminFieldHelp = listAdminFieldHelp;
  window.getAdminFieldValueHint = getAdminFieldValueHint;
  window.getAdminDraftFieldInputKind = getAdminDraftFieldInputKind;
  window.getAdminDraftSelectOptions = getAdminDraftSelectOptions;
  window.getAdminRelationEditOptionDefinitions = getAdminRelationEditOptionDefinitions;
  window.getAdminRelationEditOptionDefinition = getAdminRelationEditOptionDefinition;
  window.isAdminRelationEditField = isAdminRelationEditField;
  window.getAdminEquipSlotDisplayName = getAdminEquipSlotDisplayName;
  window.markSelectedMasterCatalogRow = markSelectedMasterCatalogRow;
  window.getAdminDraftFieldRisk = getAdminDraftFieldRisk;
  window.refreshDependentAdminRelationSelects = refreshDependentAdminRelationSelects;
  window.applyAdminRelationOptionFilter = applyAdminRelationOptionFilter;
  window.clearAdminRelationOptionFilter = clearAdminRelationOptionFilter;
  window.filterAdminDraftSelectOptions = filterAdminDraftSelectOptions;
  window.getAdminRelationSelectMetaText = getAdminRelationSelectMetaText;
  window.getAdminRelationComboGuardLabels = getAdminRelationComboGuardLabels;
  window.getAdminDraftLockedReason = getAdminDraftLockedReason;
  window.buildAdminEditDraftReview = buildAdminEditDraftReview;
  window.sortAdminChangesByRisk = sortAdminChangesByRisk;
  window.formatAdminChangeAfterValue = formatAdminChangeAfterValue;
  window.formatAdminChangeValueText = formatAdminChangeValueText;
  window.getAdminRelationValueDisplay = getAdminRelationValueDisplay;
  window.getAdminRelationOpenTarget = getAdminRelationOpenTarget;
  window.getAdminChangeRelationInfo = getAdminChangeRelationInfo;
  window.getAdminRelationOpenTargetFromChange = getAdminRelationOpenTargetFromChange;
  window.renderAdminRollbackMismatchValueCell = renderAdminRollbackMismatchValueCell;
  window.getCurrentAdminPageUrl = getCurrentAdminPageUrl;
  window.copyCurrentAdminPageUrl = copyCurrentAdminPageUrl;
  window.openAdminChangeLogDetail = openAdminChangeLogDetail;
  window.previewAdminChangeLogRollback = previewAdminChangeLogRollback;
  window.applyAdminChangeLogRollback = applyAdminChangeLogRollback;
  window.readAdminRollbackControls = readAdminRollbackControls;
  window.previewAdminCreateDeleteRollback = previewAdminCreateDeleteRollback;
  window.applyAdminCreateDeleteRollback = applyAdminCreateDeleteRollback;
  window.readAdminCreateDeleteControls = readAdminCreateDeleteControls;
  window.previewAdminCreateDeleteRestore = previewAdminCreateDeleteRestore;
  window.applyAdminCreateDeleteRestore = applyAdminCreateDeleteRestore;
  window.readAdminCreateDeleteRestoreControls = readAdminCreateDeleteRestoreControls;
  window.renderAdminCreateDeleteRestoreResult = renderAdminCreateDeleteRestoreResult;
  window.verifySelectedMasterDataApi = verifySelectedMasterDataApi;
  window.runPostWriteMasterApiVerification = runPostWriteMasterApiVerification;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootAdminReadOnlyPage, { once: true });
  } else {
    bootAdminReadOnlyPage();
  }
})();
