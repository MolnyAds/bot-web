<template>
  <div class="container">
    <router-link to="/adcatalog" class="back-btn">←</router-link>

    <div class="purchase-header">
      <div class="purchase-title">Детали покупки</div>

      <div class="purchase-card" v-if="ad">
        <div class="purchase-card-header">
          <div class="purchase-channel-icon">📢</div>
          <div class="purchase-channel-info">
            <div class="purchase-channel-name">{{ ad.group_username }}</div>
            <div class="purchase-slot-info">{{ ad.schedule }}/24</div>
          </div>
          <div class="purchase-price">{{ ad.ad_cost }} ₽</div>
        </div>

        <div class="purchase-details">
          <div class="purchase-detail-row">
            <div class="purchase-detail-label">Дата покупки:</div>
            <div class="purchase-detail-value">
              <span :class="['status-badge', mapStatus(ad.status)]">
                {{ mapStatusLabel(ad.status) }}
              </span>
            </div>
          </div>

          <div class="purchase-detail-row">
            <div class="purchase-detail-label">Плановая дата:</div>
            <div class="purchase-detail-value">
              {{ formatDate(ad.placement_date) }}
            </div>
          </div>
        </div>
      </div>

    </div>

    <div class="purchase-actions">
      <button class="purchase-action-btn secondary" @click="viewPost">Посмотреть пост</button>
      <button class="purchase-action-btn primary" @click="contactSupport">Контакт с поддержкой</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useRoute } from 'vue-router'

const appStore = useAppStore()
const route = useRoute()
const id = route.params.id

const ad = ref(null)

const headers = () => ({
  Authorization: 'Telegram-Init-Data ' + appStore.tgInitDataRow
})

function formatDate(iso) {
  const d = new Date(iso)
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

function mapStatus(status) {
  switch (status) {
    case 'published': return 'published'
    case 'waiting': return 'waiting'
    case 'cancelled': return 'cancelled'
    default: return ''
  }
}

function mapStatusLabel(status) {
  switch (status) {
    case 'published': return 'Опубликовано'
    case 'waiting': return 'Ожидает'
    case 'cancelled': return 'Отменено'
    default: return status
  }
}

async function fetchAd() {
  const res = await fetch(
    `${appStore.apiBaseUrl}/api/my/purchases/${id}`,
    { headers: headers(), mode: 'cors' }
  )
  ad.value = await res.json()
}

function viewPost() {
  // TODO: перенаправить на пост
  console.log('View post for', ad.value.id)
}

function contactSupport() {
  // TODO: открыть чат поддержки
  console.log('Contact support')
}

onMounted(async () => {
  await appStore.initTelegram()
  await fetchAd()
})
</script>