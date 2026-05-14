<template>
  <div class="star-rating">
    <span v-for="star in 5" :key="star" class="star"
          :class="{ active: star <= modelValue }"
          @click="$emit('update:modelValue', star)">★</span>
  </div>
</template>
<script>
export default {
  name: 'StarRating',
  props: { modelValue: { type: Number, default: 0 } },
  emits: ['update:modelValue']
}
</script>
<style scoped>
.star { font-size: 24px; color: #ddd; cursor: pointer; }
.star.active { color: #ffc107; }
</style>
