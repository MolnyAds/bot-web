<template>
  <div class="container">
    <div class="header">
      <div class="logo">
        <div class="logo-icon">📢</div>
        <div class="logo-text">Molny ADS</div>
      </div>
      <div class="profile-icon">
      <img
        v-if="appStore.tgInitData?.tgWebAppData?.user?.photo_url"
        :src="appStore.tgInitData.tgWebAppData.user.photo_url"
        :alt="appStore.tgInitData.tgWebAppData.user.first_name || 'user'"
      />
      <span v-else>👤</span>
      </div>
    </div>

    <router-link to="/balance">
      <div class="balance-section">
        <div class="balance-info">
          <h3>Мой баланс:</h3>
          <div class="balance-amount">{{ appStore.balance }}₽</div>
        </div>
        <router-link to="/topup">
          <div>
            <button class="top-up-btn">Пополнить</button>
          </div>
        </router-link>
    </div>
    </router-link>

    <div class="menu-items">
      <router-link to="/mychannels" class="menu-item">
        <div class="menu-icon channels">📱</div>
        <div class="menu-text">Мои каналы</div>
        <div class="menu-arrow">›</div>
      </router-link>

      <router-link to="/catalog" class="menu-item">
        <div class="menu-icon ads">✈️</div>
        <div class="menu-text">Купить рекламу</div>
        <div class="menu-arrow">›</div>
      </router-link>

      <router-link to="/adcatalog" class="menu-item">
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
          <span class="notifications-count"></span>
      </div>
    </div>
  </div>
</template>

<script setup>

import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// Если хочешь сразу после монтирования, например, подтянуть баланс:
import { onMounted } from 'vue'


onMounted(() => {
  fetch(`${appStore.apiBaseUrl}/api/user`, {
    headers: {
      Authorization: 'Telegram-Init-Data ' + appStore.tgInitDataRow
    },
    mode: 'cors',               // явно указываем CORS‑режим
  })
  .then(res => res.ok ? res.json() : Promise.reject())
  .then(data => {
    // обработать data
  })
  .catch(() => {
    // ошибка
  })
})
</script>