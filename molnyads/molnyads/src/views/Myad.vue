<template>
  <div class="container">
    <router-link to="/" class="back-btn">←</router-link>

    <div class="purchase-header">
      <div class="purchase-title">Детали покупки</div>
      
      <div class="purchase-card">
        <div class="purchase-card-header">
          <div class="purchase-channel-icon">📢</div>
          <div class="purchase-channel-info">
            <div class="purchase-channel-name">Название канала</div>
            <div class="purchase-slot-info">1/24</div>
          </div>
          <div class="purchase-price">3 500 ₽</div>
        </div>
        
        <div class="purchase-details">
          <div class="purchase-detail-row">
            <div class="purchase-detail-label">Дата покупки:</div>
            <div class="purchase-detail-value">
              <span class="status-badge">Ожидает публикации</span>
            </div>
          </div>
          
          <div class="purchase-detail-row">
            <div class="purchase-detail-label">Плановая дата:</div>
            <div class="purchase-detail-value">12 июня 2025</div>
          </div>
        </div>
      </div>
    </div>

    <div class="purchase-actions">
      <button class="purchase-action-btn secondary">Посмотреть пост</button>
      <button class="purchase-action-btn primary">Контакт с поддержкой</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MyAd'
};
</script>