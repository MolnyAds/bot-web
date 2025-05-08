<template>
  <div class="container">
    <router-link to="/" class="back-btn">←</router-link>

    <div class="catalog-header">
      <h1 class="catalog-title">Мои каналы</h1>
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
          <select class="filter-select" v-model="selectedSubjects">
            <option value="">Все тематики</option>
            <option
              v-for="subj in subjects"
              :key="subj.id"
              :value="subj.id"
            >
              {{ subj.name }}
            </option>
          </select>
          <select class="filter-select" v-model="sortBySales">
            <option value="desc">По количеству продаж (по убыванию)</option>
            <option value="asc">По количеству продаж (по возрастанию)</option>
          </select>
        </div>
      </div>
    </div>

    <div class="channels-grid">
      <router-link
        :to="`/mychannel/${channel.id}`"
        v-for="channel in channels"
        :key="channel.id"
      >
        <div class="channel-card">
          <div class="channel-card-icon business">💼</div>
          <div class="channel-name">{{ channel.username }}</div>
          <div class="channel-category">
            {{ getSubjectNames(channel.subject_ids) }}
          </div>
          <div class="channel-meta">
            {{ getCountryName(channel.country_id) }} / {{ getLanguageName(channel.language_id) }}
          </div>
          <div class="channel-sales">
            {{ channel.sales_count }} продаж
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

const subjects = ref([])
const countries = ref([])
const languages = ref([])
const selectedSubjects = ref([])
const search = ref('')
const sortBySales = ref('desc')

const page = ref(1)
const totalPages = ref(1)
const channels = ref([])

const headers = () => ({
  Authorization: 'Telegram-Init-Data ' + appStore.tgInitDataRow
})

const getSubjectNames = ids =>
  (ids || []).map(id => subjects.value.find(s => s.id === id)?.name).filter(Boolean).join(', ')

const getCountryName = id =>
  countries.value.find(c => c.id === id)?.name || '—'

const getLanguageName = id =>
  languages.value.find(l => l.id === id)?.name || '—'

async function fetchSubjects() {
  const res = await fetch(
    `${appStore.apiBaseUrl}/api/tables/subjects`,
    { headers: headers(), mode: 'cors' }
  )
  subjects.value = await res.json()
}
async function fetchCountries() {
  const res = await fetch(
    `${appStore.apiBaseUrl}/api/tables/countries`,
    { headers: headers(), mode: 'cors' }
  )
  countries.value = await res.json()
}
async function fetchLanguages() {
  const res = await fetch(
    `${appStore.apiBaseUrl}/api/tables/languages`,
    { headers: headers(), mode: 'cors' }
  )
  languages.value = await res.json()
}

async function fetchCount() {
  const params = new URLSearchParams()
  if (search.value) params.append('search', search.value)
  selectedSubjects.value.forEach(id => params.append('subject_ids', id))
  const res = await fetch(
    `${appStore.apiBaseUrl}/api/my/groups/count?${params.toString()}`,
    { headers: headers(), mode: 'cors' }
  )
  const data = await res.json()
  totalPages.value = Math.ceil(data.count / limit) || 1
}

async function fetchChannels() {
  const params = new URLSearchParams({
    page: page.value,
    limit,
    sort_by_sales: sortBySales.value
  })
  if (search.value) params.append('search', search.value)
  selectedSubjects.value.forEach(id => params.append('subject_ids', id))
  const res = await fetch(
    `${appStore.apiBaseUrl}/api/my/groups?${params.toString()}`,
    { headers: headers(), mode: 'cors' }
  )
  channels.value = await res.json()
}

onMounted(async () => {
  await appStore.initTelegram()
  await Promise.all([fetchSubjects(), fetchCountries(), fetchLanguages()])
  await fetchCount()
  await fetchChannels()
})

watch([search, selectedSubjects, sortBySales], async () => {
  page.value = 1
  await fetchCount()
  await fetchChannels()
})

watch(page, fetchChannels)
</script>