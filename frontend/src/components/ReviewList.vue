<template>
  <div class="review-list">
    <div v-if="!reviews.length">Нет отзывов</div>
    <div v-for="r in reviews" :key="r.id" class="review-card">
      <StarRating :model-value="r.rating" />
      <p>{{ r.comment }}</p>
      <small>{{ new Date(r.created_at).toLocaleDateString('ru') }}</small>
    </div>
  </div>
</template>
<script>
import StarRating from './StarRating.vue'
export default {
  name: 'ReviewList',
  components: { StarRating },
  props: { reviews: { type: Array, default: () => [] } }
}
</script>
