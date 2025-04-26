<template>
  <div class="container">
    <router-link to="/" class="back-btn">←</router-link>
    
    <div class="catalog-header">
      <h1 class="catalog-title">Мои каналы</h1>
      
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
            <option>По количеству продаж рекламы (по умолчанию)</option>
            <option>От мало продаж до много</option>
            <option>От много продаж до мало</option>
          </select>
        </div>
      </div>
    </div>

    <div class="channels-grid">
      <div class="channel-card" v-for="(channel, idx) in 8" :key="idx">
        <div class="channel-card-icon business">💼</div>
        <div class="channel-name">Название канала</div>
        <div class="channel-category">Категория</div>
        <div class="channel-sales">120 продаж</div>
      </div>
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
  name: 'MyChannels'
};
</script>