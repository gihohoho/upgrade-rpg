<template>
  <section class="shell-card" :aria-labelledby="headingId">
    <header class="shell-card__header">
      <p class="shell-card__label">{{ label }}</p>
      <h2 :id="headingId">{{ title }}</h2>
      <p class="shell-card__description">{{ description }}</p>
    </header>
    <div class="shell-card__body">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
import { useId } from 'vue';

defineProps<{
  label: string;
  title: string;
  description: string;
}>();

const headingId = `shell-card-${useId()}`;
</script>
