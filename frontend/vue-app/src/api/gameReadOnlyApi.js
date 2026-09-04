import { requestReadOnly } from './readOnlyClient';
import { GAME_READONLY_ROUTES } from './readOnlyRoutes';

export const gameReadOnlyApi = Object.freeze({
  fetchMasterData({ includeAssets = false } = {}, options = {}) {
    return requestReadOnly(GAME_READONLY_ROUTES.masterData, {
      ...options,
      query: { includeAssets },
    });
  },

  fetchLoad({ slotKey = 'character-1', accountCharacterId = '' } = {}, options = {}) {
    return requestReadOnly(GAME_READONLY_ROUTES.load, {
      ...options,
      query: { slotKey, accountCharacterId },
    });
  },

  fetchSaveSlots(options) {
    return requestReadOnly(GAME_READONLY_ROUTES.saveSlots, options);
  },
});
