import { requestApi } from './http';
import type { GameLoadData, GameLoadPayload } from './contracts';

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
};
