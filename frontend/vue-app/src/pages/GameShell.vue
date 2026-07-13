<template>
  <ShellCard
    label="Game"
    title="게임 화면 Vue 이식 준비"
    description="현재 실제 게임은 아직 루트 index.html과 legacy src/에서 실행합니다. 이 화면은 나중에 HUD와 게임 UI를 옮기기 위한 빈 shell입니다."
  >
    <ul class="shell-list">
      <li>legacy 기준 진입점: <code>index.html</code></li>
      <li>나중에 이식할 후보: <code>src/state</code>, <code>src/systems</code>, <code>src/ui</code></li>
      <li>이번 단계에서는 장비/스킬/보스/필드 같은 게임 콘텐츠를 추가하지 않습니다.</li>
    </ul>
  </ShellCard>
</template>

<script setup>
import ShellCard from '@/components/ShellCard.vue';
</script>
