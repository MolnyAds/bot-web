<template>
  <div class="container">
    <router-link to="/" class="back-btn">←</router-link>

    <div class="catalog-header">
      <h1 class="catalog-title">Каталог</h1>
      <div class="search-filters">
        <div class="search-bar">
          <span class="search-icon">🔍</span>
          <input type="text" class="search-input" placeholder="Поиск по названию" />
        </div>
        <div class="filter-row">
          <select class="filter-select">
            <option>Тематика</option>
            <option>Бизнес</option>
            <option>Новости</option>
            <option>Мемы</option>
            <option>IT</option>
          </select>
          <select class="filter-select">
            <option>(по умолчанию)</option>
            <option>По цене возрастанию</option>
            <option>По цене убыванию</option>
            <option>По подписчикам</option>
          </select>
        </div>
      </div>
    </div>

    <div class="channels-grid">
        <router-link to="channel"  v-for="(item, i) in 8" :key="i">
          <div class="channel-card">
            <div class="channel-card-icon business">💼</div>
            <div class="channel-name">Название канала</div>
            <div class="channel-category">Категория</div>
            <div class="channel-price">от 2 000 ₽</div>
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
  name: 'Catalog'
}
</script>