<template>
  <div class="container">
    <router-link to="/" class="back-btn">←</router-link>

    <div class="balance-page-header">
      <div class="balance-page-title">Баланс</div>
      <div class="balance-card">
        <div class="balance-info-main">
          <div class="balance-label">Ваш баланс</div>
          <div class="balance-amount-main">{{ appStore.balance }} ₽</div>
        </div>
        <button class="withdraw-btn">Вывести</button>
      </div>
    </div>

    <div class="history-section">
      <div class="history-title">История операций</div>

      <div class="transaction-list">
        <div
          class="transaction-item"
          v-for="tx in transactions"
          :key="tx.id"
        >
          <div :class="['transaction-icon', tx.amount >= 0 ? 'income' : 'expense']">
            {{ tx.amount >= 0 ? '+' : '−' }}
          </div>
          <div class="transaction-details">
            <div class="transaction-title">
              {{ tx.amount >= 0 ? 'Пополнение' : 'Списание' }}
            </div>
            <div class="transaction-date">
              {{ formatDate(tx.created_at) }}
            </div>
          </div>
          <div :class="['transaction-amount', tx.amount >= 0 ? 'income' : 'expense']">
            {{ formatAmount(tx.amount) }} ₽
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const transactions = ref([])

function formatDate(iso) {
  const date = new Date(iso)
  return date.toLocaleString('ru-RU', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function formatAmount(amount) {
  return Math.abs(amount).toLocaleString('ru-RU')
}

onMounted(async () => {
  await appStore.initTelegram()

  try {
    const resTx = await fetch(
      `${appStore.apiBaseUrl}/api/my/transactions?limit=30`,
      { headers: { Authorization: 'Telegram-Init-Data ' + appStore.tgInitDataRow }, mode: 'cors' }
    )
    transactions.value = await resTx.json()
  } catch (e) {
    console.error('Ошибка получения транзакций:', e)
  }
})
</script>
