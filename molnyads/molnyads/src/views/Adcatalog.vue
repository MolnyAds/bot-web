<template>
  <div class="container">
    <router-link to="/" class="back-btn">←</router-link>

    <div class="catalog-header">
      <h1 class="catalog-title">Каталог реклам</h1>
      <div class="search-filters">
        <div class="filter-dropdown">
          <select class="filter-btn">
            <option>Сначала новые</option>
            <option>Сначала старые</option>
          </select>
          <select class="filter-btn">
            <option>Все статусы</option>
            <option>Опубликовано</option>
            <option>Ожидает</option>
            <option>Отменено</option>
          </select>
        </div>
      </div>
    </div>

    <div class="ads-grid">
      <router-link to="/myad" v-for="(ad, idx) in ads" :key="idx">
        <div class="ad-card">
          <div class="ad-type">{{ ad.slot }}</div>
          <div class="ad-icon">📢</div>
          <div class="ad-info">
            <div class="ad-title">Название канала</div>
            <div class="ad-date">{{ ad.date }}</div>
          </div>
          <div class="ad-price">{{ ad.price }} ₽</div>
          <div :class="['ad-status', ad.statusClass]">{{ ad.status }}</div>
        </div>
      </router-link>
    </div>

    <div class="pagination">
      <button class="page-btn active">1</button>
      <button class="page-btn">2</button>
      <button class="page-btn">3</button>
      <button class="page-btn">...</button>
      <button class="page-btn">10</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdCatalog',
  data() {
    return {
      ads: [
        { slot: '1/24', date: '24 апреля 2024', price: 1500, status: 'Опубликовано', statusClass: 'published' },
        { slot: '1/24', date: '22 апреля 2024', price: 1800, status: 'Ожидает', statusClass: 'waiting' },
        { slot: '1/24', date: '20 апреля 2024', price: 1200, status: 'Запланировано', statusClass: 'scheduled' },
        { slot: '1/24', date: '18 апреля 2024', price: 1500, status: 'Отменено', statusClass: 'cancelled' },
        { slot: '1/24', date: '16 апреля 2024', price: 2100, status: 'Опубликовано', statusClass: 'published' },
        { slot: '1/48', date: '15 апреля 2024', price: 3200, status: 'Ожидает', statusClass: 'waiting' }
      ]
    }
  }
}
</script>
