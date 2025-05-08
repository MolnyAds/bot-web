<template>
  <div class="container">
    <div class="topup-header">
    <router-link to="/" class="back-btn">←</router-link>
      <h1>Пополнение баланса</h1>
    </div>

    <div class="form-section">
      <label for="amount">Сумма пополнения (₽)</label>
      <input
        v-model.number="amount"
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
const amount = ref(null)
const paymentMethod = ref('ton')

async function topUp() {
  if (!amount.value || amount.value < 10) {
    alert('Пожалуйста, укажите сумму не менее 10 ₽')
    return
  }
  if (!paymentMethod.value) {
    alert('Пожалуйста, выберите способ оплаты')
    return
  }

  try {
    const headers = {
      'Content-Type': 'application/json',
      Authorization: 'Telegram-Init-Data ' + appStore.tgInitDataRow
    }
    const body = JSON.stringify({ amount: amount.value })

    const res = await fetch(
      `${appStore.apiBaseUrl}/api/my/balance/deposit`,
      {
        method: 'POST',
        headers,
        body,
        mode: 'cors'
      }
    )

    if (!res.ok) {
      const err = await res.text()
      throw new Error(err || 'Ошибка пополнения')
    }

    alert('Баланс успешно пополнен на ' + amount.value + ' ₽')
    appStore.balance += amount.value
    amount.value = null
  } catch (e) {
    console.error('Ошибка при пополнении баланса:', e)
    alert('Не удалось пополнить баланс: ' + e.message)
  }
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
