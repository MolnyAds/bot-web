<template>
  <div class="container">
    <router-link to="/" class="back-btn">←</router-link>

    <div class="catalog-header">
      <h1 class="catalog-title">Каталог</h1>
      <div class="search-filters">
        <div class="search-bar">
          <span class="search-icon">🔍</span>
          <input
            type="text"
            class="search-input"
            placeholder="Поиск по названию"
            v-model="search"
          />
        </div>
        <div class="filter-row">
          <select class="filter-select" v-model="sortBy">
            <option value="price_desc">По цене (убыванию)</option>
            <option value="price_asc">По цене (возрастанию)</option>
            <option value="subs_desc">По подписчикам (убыванию)</option>
            <option value="subs_asc">По подписчикам (возрастанию)</option>
          </select>
        </div>
      </div>
    </div>

    <div class="channels-grid">
      <router-link
        v-for="item in items"
        :key="item.id"
        :to="`/channel/${item.id}`"
      >
        <div class="channel-card">
          <div class="channel-card-icon business">💼</div>
          <div class="channel-name">{{ item.username }}</div>
          <div class="channel-category">
            {{ item.subscribers }} подписчиков / {{ item.avg_views }} просмотров
          </div>
          <div class="channel-price">
            от {{ getMinPrice(item.ad_prices) }} ₽
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

const search = ref('')
const sortBy = ref('price_desc')
const page = ref(1)
const totalPages = ref(1)
const items = ref([])

const headers = () => ({
  Authorization: 'Telegram-Init-Data ' + appStore.tgInitDataRow
})

function getMinPrice(prices) {
  if (!prices) return 0   // если ad_prices null, сразу 0
  const vals = Object.values(prices)
  return vals.length ? Math.min(...vals) : 0
}

async function fetchCount() {
  const params = new URLSearchParams({ search: search.value })
  const res = await fetch(
    `${appStore.apiBaseUrl}/api/catalog/count?${params.toString()}`,
    { headers: headers(), mode: 'cors' }
  )
  const data = await res.json()
  totalPages.value = Math.ceil(data.count / limit) || 1
}

async function fetchItems() {
  const params = new URLSearchParams({
    page: page.value,
    limit,
    search: search.value,
    sort_by: sortBy.value
  })
  const res = await fetch(
    `${appStore.apiBaseUrl}/api/catalog?${params.toString()}`,
    { headers: headers(), mode: 'cors' }
  )
  items.value = await res.json()
}

onMounted(async () => {
  await appStore.initTelegram()
  await fetchCount()
  await fetchItems()
})

watch([search, sortBy], async () => {
  page.value = 1
  await fetchCount()
  await fetchItems()
})

watch(page, fetchItems)
</script>
