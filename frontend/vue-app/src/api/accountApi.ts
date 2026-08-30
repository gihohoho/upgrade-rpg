import { requestApi } from './http';
import type {
  AccountCharacterSlot,
  AccountCharactersPayload,
  MasterDataCharacterPayload,
} from './contracts';

interface CharacterMutationPayload {
  status: 'created' | 'deleted';
  character: AccountCharacterSlot;
}

export const accountApi = {
  listCharacters(token: string) {
    return requestApi<AccountCharactersPayload>('/account/characters', { token });
  },
  createCharacter(token: string, payload: { slotIndex: number; name: string; characterCode: string }) {
    return requestApi<CharacterMutationPayload>('/account/characters', { method: 'POST', token, body: payload });
  },
  deleteCharacter(token: string, accountCharacterId: string) {
    return requestApi<CharacterMutationPayload>(`/account/characters/${encodeURIComponent(accountCharacterId)}`, {
      method: 'DELETE',
      token,
    });
  },
  fetchCharacterOptions() {
    return requestApi<MasterDataCharacterPayload>('/game/master-data');
  },
};
