<template>
  <div class="container">
    <router-link to="/" class="back-btn">←</router-link>

    <div class="catalog-header">
      <h1 class="catalog-title">Каталог реклам</h1>
      <div class="search-filters">
        <div class="filter-dropdown">
          <select class="filter-btn" v-model="sortBy">
            <option value="time_desc">Сначала новые</option>
            <option value="time_asc">Сначала старые</option>
          </select>
          <select class="filter-btn" v-model="statusFilter">
            <option value="">Все статусы</option>
            <option value="published">Опубликовано</option>
            <option value="waiting">Ожидает</option>
            <option value="cancelled">Отменено</option>
          </select>
        </div>
      </div>
    </div>

    <div class="ads-grid">
      <router-link
        v-for="ad in ads"
        :key="ad.id"
        :to="`/myad/${ad.id}`"
      >
        <div class="ad-card">
          <div class="ad-type">{{ ad.schedule }}/{{ ad.group_slots }}</div>
          <div class="ad-icon">📢</div>
          <div class="ad-info">
            <div class="ad-title">{{ ad.group_username }}</div>
            <div class="ad-date">{{ formatDate(ad.placement_date) }}</div>
          </div>
          <div class="ad-price">{{ ad.ad_cost }} ₽</div>
          <div :class="['ad-status', statusClass(ad.status)]">
            {{ statusLabel(ad.status) }}
          </div>
        </div>
      </router-link>
    </div>

    <div class="pagination">
      <button
        class="page-btn"
        :class="{ active: page === p }"
        v-for="p in totalPages"
        :key="p"
        @click="page = p"
      >
        {{ p }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const limit = 10

const sortBy = ref('time_desc')
const statusFilter = ref('')
const page = ref(1)
const totalPages = ref(1)
const ads = ref([])

const headers = () => ({
  Authorization: 'Telegram-Init-Data ' + appStore.tgInitDataRow
})

function formatDate(iso) {
  const d = new Date(iso)
  return d.toLocaleString('ru-RU', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function statusClass(status) {
  // нормализуем различные статусы
  if (status === 'completed') status = 'published'
  switch (status) {
    case 'published': return 'published'
    case 'waiting': return 'waiting'
    case 'cancelled': return 'cancelled'
    default: return ''
  }
}

function statusLabel(status) {
  if (status === 'completed') status = 'published'
  switch (status) {
    case 'published': return 'Опубликовано'
    case 'waiting': return 'Ожидает'
    case 'cancelled': return 'Отменено'
    default: return status
  }
}

async function fetchCount() {
  const params = new URLSearchParams({
    sort_by: sortBy.value,
    status: statusFilter.value
  })
  const res = await fetch(
    `${appStore.apiBaseUrl}/api/my/purchases/count?${params.toString()}`,
    { headers: headers(), mode: 'cors' }
  )
  const data = await res.json()
  totalPages.value = Math.ceil(data.count / limit) || 1
}

async function fetchAds() {
  const params = new URLSearchParams({
    page: page.value,
    limit,
    sort_by: sortBy.value
  })
  if (statusFilter.value) params.append('status', statusFilter.value)

  const res = await fetch(
    `${appStore.apiBaseUrl}/api/my/purchases?${params.toString()}`,
    { headers: headers(), mode: 'cors' }
  )
  ads.value = await res.json()
}

onMounted(async () => {
  await appStore.initTelegram()
  await fetchCount()
  await fetchAds()
})

watch([sortBy, statusFilter], async () => {
  page.value = 1
  await fetchCount()
  await fetchAds()
})

watch(page, fetchAds)
</script>