-- PostgreSQL schema draft for Idle RPG backend migration.
-- This is a draft reference, not the final Alembic migration.

CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  password_hash VARCHAR(255),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  is_admin BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_profiles (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  gold BIGINT NOT NULL DEFAULT 0,
  farm_atk_bonus NUMERIC NOT NULL DEFAULT 0,
  add_attack_speed NUMERIC NOT NULL DEFAULT 0,
  current_character_id VARCHAR(80) NOT NULL DEFAULT 'weapon_master',
  current_zone_index INTEGER NOT NULL DEFAULT 0,
  current_zone_type VARCHAR(30) NOT NULL DEFAULT 'field',
  flags_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  records_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE characters (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(80) UNIQUE NOT NULL,
  name VARCHAR(120) NOT NULL,
  description TEXT,
  image_url VARCHAR(500),
  is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
  meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE skills (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(80) UNIQUE NOT NULL,
  name VARCHAR(120) NOT NULL,
  slot_key VARCHAR(20) NOT NULL,
  description TEXT,
  icon_url VARCHAR(500),
  proc_rate NUMERIC(8,4) NOT NULL DEFAULT 0,
  cooldown_seconds INTEGER NOT NULL DEFAULT 0,
  options_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE character_skills (
  id BIGSERIAL PRIMARY KEY,
  character_code VARCHAR(80) NOT NULL REFERENCES characters(code) ON DELETE CASCADE,
  skill_code VARCHAR(80) NOT NULL REFERENCES skills(code) ON DELETE CASCADE,
  sort_order INTEGER NOT NULL DEFAULT 0,
  is_default BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_character_skill UNIQUE (character_code, skill_code)
);

CREATE TABLE skill_levels (
  id BIGSERIAL PRIMARY KEY,
  skill_code VARCHAR(80) NOT NULL REFERENCES skills(code) ON DELETE CASCADE,
  level INTEGER NOT NULL,
  damage_multiplier NUMERIC(14,6) NOT NULL DEFAULT 0,
  proc_rate_bonus NUMERIC(8,4) NOT NULL DEFAULT 0,
  options_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_skill_level UNIQUE (skill_code, level)
);

CREATE TABLE item_templates (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(120) UNIQUE NOT NULL,
  name VARCHAR(160) NOT NULL,
  item_type VARCHAR(60) NOT NULL,
  grade VARCHAR(60),
  icon_url VARCHAR(500),
  description TEXT,
  stackable BOOLEAN NOT NULL DEFAULT FALSE,
  equip_slot VARCHAR(60),
  enhance_group_code VARCHAR(120),
  base_stats_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  options_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  admin_note TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE item_instances (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  template_code VARCHAR(120) NOT NULL REFERENCES item_templates(code) ON DELETE RESTRICT,
  quantity INTEGER NOT NULL DEFAULT 1,
  enhance_level INTEGER NOT NULL DEFAULT 0,
  bound_character_code VARCHAR(80),
  instance_stats_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  instance_options_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_inventory_slots (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  bag_type VARCHAR(30) NOT NULL DEFAULT 'inventory',
  slot_index INTEGER NOT NULL,
  item_instance_id BIGINT REFERENCES item_instances(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_user_bag_slot UNIQUE (user_id, bag_type, slot_index)
);

CREATE TABLE user_equipment_slots (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  character_code VARCHAR(80) NOT NULL DEFAULT 'weapon_master',
  slot_key VARCHAR(60) NOT NULL,
  item_instance_id BIGINT REFERENCES item_instances(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_user_character_equip_slot UNIQUE (user_id, character_code, slot_key)
);

CREATE TABLE bosses (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(120) UNIQUE NOT NULL,
  name VARCHAR(160) NOT NULL,
  tier INTEGER,
  boss_type VARCHAR(30) NOT NULL DEFAULT 'normal',
  hp INTEGER NOT NULL DEFAULT 1,
  image_url VARCHAR(500),
  description TEXT,
  summon_rules_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  cooldown_seconds INTEGER NOT NULL DEFAULT 0,
  is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE drop_tables (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(120) UNIQUE NOT NULL,
  owner_type VARCHAR(40) NOT NULL,
  owner_code VARCHAR(120) NOT NULL,
  description TEXT,
  rules_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE drop_table_items (
  id BIGSERIAL PRIMARY KEY,
  drop_table_code VARCHAR(120) NOT NULL REFERENCES drop_tables(code) ON DELETE CASCADE,
  item_template_code VARCHAR(120) NOT NULL REFERENCES item_templates(code) ON DELETE RESTRICT,
  rate NUMERIC(10,6) NOT NULL DEFAULT 0,
  min_quantity INTEGER NOT NULL DEFAULT 1,
  max_quantity INTEGER NOT NULL DEFAULT 1,
  conditions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE field_zones (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(120) UNIQUE NOT NULL,
  name VARCHAR(160) NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  enemy_hp INTEGER NOT NULL DEFAULT 1,
  gold_reward INTEGER NOT NULL DEFAULT 0,
  description TEXT,
  entry_rules_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  farm_rules_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE enhancement_groups (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(120) UNIQUE NOT NULL,
  name VARCHAR(160) NOT NULL,
  description TEXT,
  max_level INTEGER NOT NULL DEFAULT 0,
  rules_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE enhancement_levels (
  id BIGSERIAL PRIMARY KEY,
  group_code VARCHAR(120) NOT NULL REFERENCES enhancement_groups(code) ON DELETE CASCADE,
  from_level INTEGER NOT NULL,
  to_level INTEGER NOT NULL,
  success_rate NUMERIC(10,6) NOT NULL DEFAULT 0,
  gold_cost INTEGER NOT NULL DEFAULT 0,
  material_rules_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  result_stats_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  fail_rules_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_enhancement_step UNIQUE (group_code, from_level)
);

CREATE TABLE admin_roles (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(80) UNIQUE NOT NULL,
  name VARCHAR(120) NOT NULL,
  permissions_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE admin_user_roles (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_code VARCHAR(80) NOT NULL REFERENCES admin_roles(code) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE admin_change_logs (
  id BIGSERIAL PRIMARY KEY,
  admin_user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  target_type VARCHAR(80) NOT NULL,
  target_id VARCHAR(160) NOT NULL,
  action VARCHAR(40) NOT NULL,
  reason TEXT,
  before_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  after_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  rollback_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  applied BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
