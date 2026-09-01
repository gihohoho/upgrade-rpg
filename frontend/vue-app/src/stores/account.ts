import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import { accountApi } from '@/api/accountApi';
import { authApi } from '@/api/authApi';
import { ApiRequestError } from '@/api/http';
import type { AccountCharacterSlot, AuthUser, BossOption, CharacterOption, FieldZoneOption } from '@/api/contracts';

const ACCESS_TOKEN_KEY = 'upgradeRpgAccountAccessToken';
const SELECTED_CHARACTER_KEY = 'upgradeRpgSelectedAccountCharacter';
const EMAIL_ACTION_TOKEN_PATTERN = /^[A-Za-z0-9_-]{32,256}$/;
const SESSION_INVALID_CODES = new Set([
  'bearer_token_required',
  'access_token_invalid',
  'account_not_found',
  'auth_version_stale',
  'account_suspended',
  'email_verification_required',
]);

export type AccountStage = 'checking' | 'anonymous' | 'verification' | 'characters' | 'ready' | 'retry';
export type NoticeTone = 'success' | 'error' | 'info' | '';

interface StoredCharacter {
  accountCharacterId: string;
  slotIndex: number;
  slotKey: string;
  name: string;
  characterCode: string;
}

function readStorage(storage: Storage, key: string): string {
  try {
    return storage.getItem(key) ?? '';
  } catch {
    return '';
  }
}

function writeStorage(storage: Storage, key: string, value: string): void {
  try {
    if (value) storage.setItem(key, value);
    else storage.removeItem(key);
  } catch {
    // 저장소 접근이 차단돼도 현재 탭의 계정 흐름은 계속 사용합니다.
  }
}

function friendlyError(error: unknown): string {
  if (!(error instanceof ApiRequestError)) return '요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.';
  if (error.status === 429 || error.code === 'auth_rate_limited') {
    return error.retryAfterSeconds
      ? `요청이 너무 많습니다. ${error.retryAfterSeconds}초 후 다시 시도해 주세요.`
      : '요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.';
  }
  if (error.status === 413 || error.code === 'request_body_too_large') {
    return '요청 데이터가 허용 크기를 넘었습니다. 입력 내용을 줄인 뒤 다시 시도해 주세요.';
  }
  return error.message;
}

function isSessionInvalid(error: unknown): boolean {
  return error instanceof ApiRequestError
    && (error.status === 401 || error.status === 403)
    && (!error.code || SESSION_INVALID_CODES.has(error.code));
}

function consumeVerificationToken(): { token: string; invalid: boolean } | null {
  const params = new URLSearchParams(window.location.hash.replace(/^#/, ''));
  if (params.get('auth') !== 'verify-email') return null;
  const token = String(params.get('token') ?? '').trim();
  window.history.replaceState(null, document.title, `${window.location.pathname}${window.location.search}`);
  return { token, invalid: !EMAIL_ACTION_TOKEN_PATTERN.test(token) };
}

export const useAccountStore = defineStore('account', () => {
  const stage = ref<AccountStage>('checking');
  const busy = ref(false);
  const initialized = ref(false);
  const token = ref('');
  const persistence = ref<'session' | 'local'>('session');
  const user = ref<AuthUser | null>(null);
  const slots = ref<AccountCharacterSlot[]>([]);
  const characterOptions = ref<CharacterOption[]>([
    { code: 'weapon_master', name: '검신', description: '검을 다루는 기본 캐릭터', isEnabled: true },
  ]);
  const fieldZones = ref<FieldZoneOption[]>([]);
  const bosses = ref<BossOption[]>([]);
  const selectedCharacter = ref<AccountCharacterSlot | null>(null);
  const pendingEmail = ref('');
  const notice = ref('');
  const noticeTone = ref<NoticeTone>('');

  const occupiedCount = computed(() => slots.value.filter((slot) => slot.occupied && !slot.unavailable).length);
  const hasReadyContext = computed(() => Boolean(token.value && user.value && selectedCharacter.value?.accountCharacterId));
  const accessToken = computed(() => token.value);
  const isAuthenticated = computed(() => Boolean(token.value && user.value));
  const isAdmin = computed(() => Boolean(user.value?.isAdmin));

  function setNotice(message = '', tone: NoticeTone = '') {
    notice.value = message;
    noticeTone.value = tone;
  }

  function restoreToken() {
    const localToken = readStorage(window.localStorage, ACCESS_TOKEN_KEY);
    const sessionToken = readStorage(window.sessionStorage, ACCESS_TOKEN_KEY);
    token.value = localToken || sessionToken;
    persistence.value = localToken ? 'local' : 'session';
    return token.value;
  }

  function storeToken(accessToken: string, keepLogin: boolean) {
    token.value = accessToken.trim();
    persistence.value = keepLogin ? 'local' : 'session';
    writeStorage(window.localStorage, ACCESS_TOKEN_KEY, keepLogin ? token.value : '');
    writeStorage(window.sessionStorage, ACCESS_TOKEN_KEY, keepLogin ? '' : token.value);
  }

  function clearSelectedCharacter() {
    selectedCharacter.value = null;
    writeStorage(window.localStorage, SELECTED_CHARACTER_KEY, '');
    writeStorage(window.sessionStorage, SELECTED_CHARACTER_KEY, '');
  }

  function clearSession() {
    token.value = '';
    user.value = null;
    slots.value = [];
    writeStorage(window.localStorage, ACCESS_TOKEN_KEY, '');
    writeStorage(window.sessionStorage, ACCESS_TOKEN_KEY, '');
    clearSelectedCharacter();
  }

  function invalidateSession(message = '로그인 정보가 만료되었습니다. 다시 로그인해 주세요.') {
    clearSession();
    stage.value = 'anonymous';
    setNotice(message, 'error');
  }

  function markAdminDenied() {
    if (user.value) user.value = { ...user.value, isAdmin: false };
  }

  function restoreSelectedCharacter() {
    const preferred = persistence.value === 'local' ? window.localStorage : window.sessionStorage;
    const raw = readStorage(preferred, SELECTED_CHARACTER_KEY)
      || readStorage(window.sessionStorage, SELECTED_CHARACTER_KEY)
      || readStorage(window.localStorage, SELECTED_CHARACTER_KEY);
    if (!raw) return null;
    try {
      const stored = JSON.parse(raw) as Partial<StoredCharacter>;
      return slots.value.find((slot) => (
        slot.occupied
        && slot.accountCharacterId === stored.accountCharacterId
        && slot.slotIndex === Number(stored.slotIndex)
      )) ?? null;
    } catch {
      return null;
    }
  }

  function selectCharacter(slot: AccountCharacterSlot) {
    if (!slot.occupied || slot.unavailable || !slot.accountCharacterId || !slot.accountCharacter) return;
    selectedCharacter.value = slot;
    const stored: StoredCharacter = {
      accountCharacterId: slot.accountCharacterId,
      slotIndex: slot.slotIndex,
      slotKey: slot.slotKey,
      name: slot.accountCharacter.name,
      characterCode: slot.accountCharacter.characterCode,
    };
    const storage = persistence.value === 'local' ? window.localStorage : window.sessionStorage;
    writeStorage(window.localStorage, SELECTED_CHARACTER_KEY, '');
    writeStorage(window.sessionStorage, SELECTED_CHARACTER_KEY, '');
    writeStorage(storage, SELECTED_CHARACTER_KEY, JSON.stringify(stored));
    stage.value = 'ready';
    setNotice(`${stored.name} 캐릭터를 선택했습니다.`, 'success');
  }

  async function loadCharacters(options: { restoreSelection?: boolean } = {}) {
    if (!token.value) {
      stage.value = 'anonymous';
      return;
    }
    busy.value = true;
    setNotice();
    try {
      const [charactersResult, optionsResult] = await Promise.allSettled([
        accountApi.listCharacters(token.value),
        accountApi.fetchCharacterOptions(),
      ]);
      if (charactersResult.status === 'rejected') throw charactersResult.reason;
      slots.value = charactersResult.value.payload.slots;
      if (optionsResult.status === 'fulfilled') {
        const enabled = optionsResult.value.payload.characters.filter((option) => option.isEnabled);
        if (enabled.length) characterOptions.value = enabled;
        fieldZones.value = (optionsResult.value.payload.fieldZones ?? [])
          .filter((zone) => zone.isEnabled)
          .sort((left, right) => left.sortOrder - right.sortOrder || left.code.localeCompare(right.code));
        bosses.value = (optionsResult.value.payload.bosses ?? [])
          .filter((boss) => boss.isEnabled)
          .sort((left, right) => (
            left.bossType.localeCompare(right.bossType)
            || (left.tier ?? Number.MAX_SAFE_INTEGER) - (right.tier ?? Number.MAX_SAFE_INTEGER)
            || left.code.localeCompare(right.code)
          ));
      }
      selectedCharacter.value = options.restoreSelection === false ? null : restoreSelectedCharacter();
      stage.value = selectedCharacter.value ? 'ready' : 'characters';
    } catch (error) {
      if (isSessionInvalid(error)) {
        clearSession();
        stage.value = 'anonymous';
        setNotice('로그인 정보가 만료되었습니다. 다시 로그인해 주세요.', 'error');
      } else {
        stage.value = 'retry';
        setNotice(friendlyError(error), 'error');
      }
    } finally {
      busy.value = false;
    }
  }

  async function initialize() {
    if (initialized.value) return;
    initialized.value = true;
    const verification = consumeVerificationToken();
    if (verification) {
      if (verification.invalid) {
        stage.value = 'anonymous';
        setNotice('이메일 인증 링크 형식이 올바르지 않습니다. 인증메일을 다시 요청해 주세요.', 'error');
        return;
      }
      busy.value = true;
      try {
        await authApi.verifyEmail(verification.token);
        stage.value = 'anonymous';
        setNotice('이메일 인증이 완료되었습니다. 이제 로그인할 수 있습니다.', 'success');
      } catch (error) {
        stage.value = 'anonymous';
        setNotice(friendlyError(error), 'error');
      } finally {
        busy.value = false;
      }
      return;
    }

    if (!restoreToken()) {
      stage.value = 'anonymous';
      return;
    }
    try {
      const response = await authApi.me(token.value);
      user.value = response.payload.user;
      await loadCharacters({ restoreSelection: true });
    } catch (error) {
      if (isSessionInvalid(error)) {
        clearSession();
        stage.value = 'anonymous';
        setNotice('로그인 정보가 만료되었습니다. 다시 로그인해 주세요.', 'error');
      } else {
        stage.value = 'retry';
        setNotice(friendlyError(error), 'error');
      }
    }
  }

  async function ensureSession() {
    if (token.value && user.value) return true;
    if (!token.value && !restoreToken()) {
      stage.value = 'anonymous';
      return false;
    }
    busy.value = true;
    setNotice();
    try {
      const response = await authApi.me(token.value);
      user.value = response.payload.user;
      return true;
    } catch (error) {
      if (isSessionInvalid(error)) {
        invalidateSession();
      } else {
        stage.value = 'retry';
        setNotice(friendlyError(error), 'error');
      }
      return false;
    } finally {
      busy.value = false;
    }
  }

  async function loginSession(identifier: string, password: string, keepLogin: boolean) {
    busy.value = true;
    setNotice();
    try {
      const response = await authApi.login({ identifier: identifier.trim(), password });
      storeToken(response.payload.accessToken, keepLogin);
      user.value = response.payload.user;
      return true;
    } catch (error) {
      const apiError = error instanceof ApiRequestError ? error : null;
      if (apiError?.code === 'email_verification_required') {
        pendingEmail.value = identifier.includes('@') ? identifier.trim().toLowerCase() : '';
        stage.value = 'verification';
      }
      setNotice(friendlyError(error), 'error');
      return false;
    } finally {
      busy.value = false;
    }
  }

  async function login(identifier: string, password: string, keepLogin: boolean) {
    const authenticated = await loginSession(identifier, password, keepLogin);
    if (authenticated) {
      await loadCharacters({ restoreSelection: true });
    }
  }

  async function register(username: string, email: string, password: string, passwordConfirm: string) {
    busy.value = true;
    setNotice();
    try {
      await authApi.register({ username: username.trim().toLowerCase(), email: email.trim(), password, passwordConfirm });
      pendingEmail.value = email.trim().toLowerCase();
      stage.value = 'verification';
      setNotice('가입 요청을 접수했습니다. 받은 메일에서 이메일 인증을 완료해 주세요.', 'success');
    } catch (error) {
      setNotice(friendlyError(error), 'error');
    } finally {
      busy.value = false;
    }
  }

  async function resendVerification(email: string) {
    busy.value = true;
    setNotice();
    try {
      const normalized = email.trim().toLowerCase();
      await authApi.resendVerification(normalized);
      pendingEmail.value = normalized;
      stage.value = 'verification';
      setNotice('인증메일 요청을 접수했습니다. 스팸함도 확인해 주세요.', 'success');
    } catch (error) {
      setNotice(friendlyError(error), 'error');
    } finally {
      busy.value = false;
    }
  }

  async function createCharacter(slotIndex: number, name: string, characterCode: string) {
    if (!token.value) return false;
    busy.value = true;
    setNotice();
    try {
      await accountApi.createCharacter(token.value, { slotIndex, name: name.trim(), characterCode });
      await loadCharacters({ restoreSelection: false });
      setNotice(`${slotIndex}번 슬롯에 캐릭터를 만들었습니다.`, 'success');
      return true;
    } catch (error) {
      if (isSessionInvalid(error)) {
        clearSession();
        stage.value = 'anonymous';
      }
      setNotice(friendlyError(error), 'error');
      return false;
    } finally {
      busy.value = false;
    }
  }

  async function deleteCharacter(slot: AccountCharacterSlot) {
    if (!token.value || !slot.accountCharacterId) return false;
    busy.value = true;
    setNotice();
    try {
      await accountApi.deleteCharacter(token.value, slot.accountCharacterId);
      if (selectedCharacter.value?.accountCharacterId === slot.accountCharacterId) clearSelectedCharacter();
      await loadCharacters({ restoreSelection: false });
      setNotice(`${slot.accountCharacter?.name ?? '캐릭터'}의 진행 데이터를 삭제했습니다.`, 'success');
      return true;
    } catch (error) {
      if (isSessionInvalid(error)) {
        clearSession();
        stage.value = 'anonymous';
      }
      setNotice(friendlyError(error), 'error');
      return false;
    } finally {
      busy.value = false;
    }
  }

  function changeCharacter() {
    clearSelectedCharacter();
    stage.value = 'characters';
    setNotice();
  }

  async function logout() {
    const currentToken = token.value;
    clearSession();
    stage.value = 'anonymous';
    setNotice('로그아웃했습니다.', 'success');
    if (currentToken) void authApi.logout(currentToken).catch(() => undefined);
  }

  function showLogin(message = '') {
    stage.value = 'anonymous';
    if (message) setNotice(message, 'info');
  }

  return {
    stage,
    busy,
    user,
    slots,
    characterOptions,
    fieldZones,
    bosses,
    selectedCharacter,
    pendingEmail,
    notice,
    noticeTone,
    occupiedCount,
    hasReadyContext,
    accessToken,
    isAuthenticated,
    isAdmin,
    initialize,
    ensureSession,
    loginSession,
    login,
    register,
    resendVerification,
    loadCharacters,
    createCharacter,
    deleteCharacter,
    selectCharacter,
    changeCharacter,
    logout,
    showLogin,
    invalidateSession,
    markAdminDenied,
  };
});
