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

    <div class="topup-header">
      <router-link to="/" class="back-button">←</router-link>
      <h1>Пополнение баланса</h1>
    </div>

    <div class="form-section">
      <label for="amount">Сумма пополнения (₽)</label>
      <input
        v-model="amount"
        type="number"
        id="amount"
        placeholder="Введите сумму"
        min="10"
      />

      <div class="payment-methods">
        <label>
          <input type="radio" v-model="paymentMethod" value="ton" /> Оплата через TON
        </label>
        <label>
          <input type="radio" v-model="paymentMethod" value="sbp" /> Оплата через СБП
        </label>
      </div>

      <button class="top-up-btn" @click="topUp">Пополнить</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const amount = ref('')
const paymentMethod = ref('')

function topUp() {
  if (!amount.value || !paymentMethod.value) {
    alert('Пожалуйста, укажите сумму и способ оплаты')
    return
  }
  // логика обработки пополнения, отправка на сервер
  console.log(`Пополнение на ${amount.value} ₽ через ${paymentMethod.value}`)
  // Можно добавить редирект или визуальный отклик
}
</script>

<style scoped>
.container {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-family: 'Segoe UI', sans-serif;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}
.logo-text {
  font-weight: bold;
  font-size: 18px;
}
.profile-icon img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
}
.topup-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
}
.back-button {
  text-decoration: none;
  background: #eef2f7;
  border-radius: 50%;
  padding: 6px 12px;
  font-size: 20px;
  color: #333;
}
h1 {
  font-size: 20px;
  margin: 0;
}
.form-section {
  margin-top: 24px;
}
input[type="number"] {
  width: 100%;
  padding: 12px;
  border: 1px solid #d0d7e2;
  border-radius: 8px;
  font-size: 16px;
  margin-top: 8px;
}
.payment-methods {
  margin-top: 16px;
}
.payment-methods label {
  display: block;
  background: #f5f7fb;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 10px;
  border: 1px solid #d0d7e2;
}
.top-up-btn {
  margin-top: 20px;
  width: 100%;
  background: #347cff;
  color: white;
  padding: 14px;
  font-size: 16px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
}
</style>
