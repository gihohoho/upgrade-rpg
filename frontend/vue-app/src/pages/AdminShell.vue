<template>
  <ShellCard
    label="Admin"
    title="관리자 페이지 Vue 이식 준비"
    description="현재 실제 관리자 도구는 아직 루트 admin.html에서 실행합니다. 이 화면은 나중에 카탈로그/상세/Preview를 옮기기 위한 빈 shell입니다."
  >
    <ul class="shell-list">
      <li>legacy 기준 진입점: <code>admin.html</code></li>
      <li>초기 이식 후보: 읽기 전용 카탈로그, 상세 조회, 안내 패널</li>
      <li>Preview/Apply/write 관련 기능은 계약과 요청 body를 다시 확인한 뒤 가장 나중에 옮깁니다.</li>
    </ul>
  </ShellCard>
</template>

<script setup>
import ShellCard from '@/components/ShellCard.vue';
</script>
