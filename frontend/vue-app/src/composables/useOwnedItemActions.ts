import { computed } from 'vue';
import { useAccountStore, useGameStore } from '@/stores';
import type { OwnedItemAction } from '@/stores/game';

export function useOwnedItemActions() {
  const account = useAccountStore();
  const game = useGameStore();
  const canMutate = computed(() => game.canMutateItems && Boolean(account.accessToken && account.selectedCharacter));

  async function run(action?: OwnedItemAction) {
    const token = account.accessToken;
    const userId = account.user?.id;
    const slot = account.selectedCharacter;
    if (!token || userId === undefined || !slot) return;
    const outcome = action
      ? await game.mutateOwnedItems({ token, userId, slot, action })
      : await game.enqueueSelectedCharacterSave({ token, userId, slot, reason: 'manual' });
    if (account.accessToken !== token || account.user?.id !== userId || account.selectedCharacter?.accountCharacterId !== slot.accountCharacterId) return;
    if (outcome === 'session-invalid') account.invalidateSession('아이템 변경 복구본을 보존했습니다. 다시 로그인해 주세요.');
  }

  return {
    canMutate,
    move: (container: 'inventory' | 'storage', selectionKey: string) => run({ type: 'move', container, selectionKey }),
    sort: (container: 'inventory' | 'storage') => run({ type: 'sort', container }),
    retry: () => run(),
  };
}
