<template>
  <main class="vue-shell">
    <header class="vue-shell__header">
      <div>
        <p class="vue-shell__eyebrow">Upgrade RPG v281</p>
        <h1>Vue 전환 준비 Shell</h1>
      </div>
      <nav class="vue-shell__nav" aria-label="Vue shell navigation">
        <RouterLink to="/game">게임 Shell</RouterLink>
        <RouterLink to="/admin">관리자 Shell</RouterLink>
      </nav>
    </header>

    <RouterView />
  </main>
</template>
