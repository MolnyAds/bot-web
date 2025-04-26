<template>
  <div class="container">
    <div class="header">
      <div class="logo">
        <div class="logo-icon">📢</div>
        <div class="logo-text">Molny ADS</div>
      </div>
      <div class="profile-icon">👤</div>
    </div>

    <div class="balance-section">
      <div class="balance-info">
        <h3>Мой баланс:</h3>
        <div class="balance-amount">1 350 ₽</div>
      </div>
      <router-link to="/balance">
        <button class="top-up-btn">Пополнить</button>
      </router-link>
    </div>

    <div class="menu-items">
      <router-link to="/channels" class="menu-item">
        <div class="menu-icon channels">📱</div>
        <div class="menu-text">Мои каналы</div>
        <div class="menu-arrow">›</div>
      </router-link>

      <router-link to="/ads" class="menu-item">
        <div class="menu-icon ads">✈️</div>
        <div class="menu-text">Купить рекламу</div>
        <div class="menu-arrow">›</div>
      </router-link>

      <router-link to="/purchases" class="menu-item">
        <div class="menu-icon purchases">🛒</div>
        <div class="menu-text">Мои покупки</div>
        <div class="menu-arrow">›</div>
      </router-link>

      <router-link to="/profile" class="menu-item">
        <div class="menu-icon profile">👤</div>
        <div class="menu-text">Профиль</div>
        <div class="menu-arrow">›</div>
      </router-link>
    </div>

    <div class="notifications">
      <div class="notifications-text">
        Новые заявки: <span class="notifications-count">2</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>