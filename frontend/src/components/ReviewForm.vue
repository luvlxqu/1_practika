<template>
  <div class="review-form">
    <h4>Оставить отзыв</h4>
    <StarRating v-model="rating" />
    <textarea v-model="comment" rows="4" maxlength="1000" placeholder="Ваш отзыв..."></textarea>
    <button @click="$emit('submit', { rating, comment })" :disabled="!rating">Отправить</button>
  </div>
</template>
<script>
import StarRating from './StarRating.vue'
export default {
  name: 'ReviewForm',
  components: { StarRating },
  data() { return { rating: 0, comment: '' } },
  emits: ['submit']
}
</script>
