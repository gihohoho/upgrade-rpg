<template>
  <section class="shell-card">
    <p class="shell-card__label">{{ label }}</p>
    <h2>{{ title }}</h2>
    <p class="shell-card__description">{{ description }}</p>
    <slot />
  </section>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
});
</script>
