import { requestApi } from './http';
import type {
  GameLoadData,
  GameLoadPayload,
  GameSaveData,
  GameSavePayload,
  GameSaveRequestBody,
} from './contracts';

export interface GameLoadRequest {
  slotKey: `character-${number}`;
  accountCharacterId: string;
}

export const gameApi = {
  loadSelectedCharacter(token: string, request: GameLoadRequest, signal?: AbortSignal) {
    const query = new URLSearchParams({
      slotKey: request.slotKey,
      accountCharacterId: request.accountCharacterId,
    });
    return requestApi<GameLoadPayload, GameLoadData>(`/game/load?${query.toString()}`, {
      token,
      signal,
    });
  },

  saveSelectedCharacter(token: string, request: GameSaveRequestBody) {
    return requestApi<GameSavePayload, GameSaveData>('/game/save', {
      method: 'POST',
      token,
      body: request,
      timeoutMs: 8_000,
    });
  },
};
