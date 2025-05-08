<template>
  <div class="container">
    <router-link to="/" class="back-btn">←</router-link>
    <div class="catalog-header">
      <h1 class="catalog-title">Профиль</h1>
    </div>

    <div class="stats-container">
      <!-- Общая активность -->
      <div class="stats-block">
        <div class="stats-block-title">Общая активность</div>
        <div class="stats-data">
          <div class="stat-item">
            <span class="stat-label">Всего объявлений:</span>
            <span class="stat-value">{{ stats.total_ads }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Куплено объявлений:</span>
            <span class="stat-value">{{ stats.bought_ads }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Активные заказы:</span>
            <span class="stat-value">{{ stats.active_orders }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Отменённые заказы:</span>
            <span class="stat-value">{{ stats.cancelled_orders }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Средняя цена размещения:</span>
            <span class="stat-value">{{ stats.average_price }} ₽</span>
          </div>
        </div>
      </div>

      <!-- Покупка рекламы по типам -->
      <div class="stats-block">
        <div class="stats-block-title">Покупка рекламы по типам</div>
        <div class="stats-data">
          <div
            v-for="(count, typeId) in stats.ad_type_purchases"
            :key="typeId"
            class="stat-item"
          >
            <span class="stat-label">Тип {{ typeId }}:</span>
            <span class="stat-value">{{ count }}</span>
          </div>
        </div>
      </div>

      <!-- Продажи и выручка -->
      <div class="stats-block">
        <div class="stats-block-title">Продажи</div>
        <div class="stats-data">
          <div class="stat-item">
            <span class="stat-label">Всего продаж:</span>
            <span class="stat-value">{{ stats.total_sales }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Выручка всего:</span>
            <span class="stat-value">{{ stats.total_revenue }} ₽</span>
          </div>
        </div>
      </div>

      <!-- Последние 30 дней -->
      <div class="stats-block">
        <div class="stats-block-title">За последние 30 дней</div>
        <div class="stats-data">
          <div class="stat-item">
            <span class="stat-label">Продаж:</span>
            <span class="stat-value">{{ stats.sales_last_30_days }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Выручка:</span>
            <span class="stat-value">{{ stats.revenue_last_30_days }} ₽</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// реактивный объект со всеми нужными полями
const stats = reactive({
  total_ads: 0,
  bought_ads: 0,
  active_orders: 0,
  cancelled_orders: 0,
  average_price: 0,
  ad_type_purchases: {},
  total_sales: 0,
  total_revenue: 0,
  sales_last_30_days: 0,
  revenue_last_30_days: 0
})

onMounted(async () => {
  const appStore = useAppStore()
  const headers = {
    Authorization: 'Telegram-Init-Data ' + appStore.tgInitDataRow
  }

  try {
    // 1) Получаем общую статистику
    const resStats = await fetch(
      `${appStore.apiBaseUrl}/api/my/stats`,
      { headers, mode: 'cors'}
    )
    const dataStats = await resStats.json()
    Object.assign(stats, dataStats)

    // 2) Получаем список типов рекламы
    const resTypes = await fetch(
      `${appStore.apiBaseUrl}/api/tables/ad_types`,
      { headers, mode: 'cors'}
    )
    const types = await resTypes.json()

    // инициализируем ad_type_purchases с учётом пришедших типов
    const purchases = {}
    types.forEach(type => {
      purchases[type.id] = stats.ad_type_purchases[type.id] || 0
    })
    stats.ad_type_purchases = purchases

  } catch (error) {
    console.error('Ошибка при загрузке статистики профиля:', error)
  }
})
</script>
