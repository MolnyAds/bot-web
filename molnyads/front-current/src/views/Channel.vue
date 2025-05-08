<template>
  <div class="container">
    <router-link to="/catalog" class="back-btn">←</router-link>

    <div class="channel-header">
      <h1 class="channel-title">{{ group.username }}</h1>
      <div class="channel-info">
        <div class="info-row">
          <span class="info-icon">📁</span>
          <span>
            Тематика: <strong>{{ subjectNames }}</strong>
          </span>
        </div>
        <div class="info-row">
          <span class="info-icon">🌍</span>
          <span>
            Гео / Язык: <strong>{{ countryName }} / {{ languageName }}</strong>
          </span>
        </div>
      </div>
    </div>

    <div class="channel-visual">
      <div class="channel-logo">
        <div class="megaphone-icon">📢</div>
      </div>
      <div class="channel-links">
        <div class="link-item">
          <div class="link-icon telegram-icon">✈</div>
          <div class="link-text">
            <strong>t.me:</strong><br />
            <a :href="tgUrl" class="link-url">{{ tgUrl }}</a>
          </div>
        </div>
        <div class="link-item">
          <div class="link-icon tgstat-icon">📊</div>
          <div class="link-text">
            <strong>TGStat:</strong><br />
            <a :href="tgStatUrl" class="link-url">{{ tgStatUrl }}</a>
          </div>
        </div>
      </div>
    </div>

    <div class="pricing-section">
      <h2 class="pricing-title">Реклама:</h2>
      <div class="pricing-items">
        <div
          v-for="(label, idx) in pricingLabels"
          :key="idx"
          class="pricing-item"
        >
          <span class="pricing-label">{{ label }}:</span>
          <span class="pricing-value">{{ formatPrice(idx) }} ₽</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useRoute } from 'vue-router'

const appStore = useAppStore()
const route = useRoute()
const groupId = Number(route.params.id)

const group = reactive({
  username: '',
  subject_ids: [],
  country_id: null,
  language_id: null,
  ad_prices: {}
})
const subjectsList = ref([])
const countries = ref([])
const languages = ref([])
const pricingLabels = ['Пост', 'Закреплённый пост', 'Упоминание']

const headers = () => ({
  Authorization: 'Telegram-Init-Data ' + appStore.tgInitDataRow,
  'Content-Type': 'application/json'
})

async function fetchSubjects() {
  const res = await fetch(
    `${appStore.apiBaseUrl}/api/tables/subjects`,
    { headers: headers(), mode: 'cors' }
  )
  subjectsList.value = await res.json()
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

async function fetchGroup() {
  const res = await fetch(
    `${appStore.apiBaseUrl}/api/group/${groupId}`,
    { headers: headers(), mode: 'cors' }
  )
  const data = await res.json()
  Object.assign(group, data)
}

const subjectNames = computed(() =>
  group.subject_ids
    .map(id => subjectsList.value.find(s => s.id === id)?.name || id)
    .join(' / ')
)
const countryName = computed(() =>
  countries.value.find(c => c.id === group.country_id)?.name || '—'
)
const languageName = computed(() =>
  languages.value.find(l => l.id === group.language_id)?.name || '—'
)

const tgUrl = computed(() => `https://t.me/${group.username}`)
const tgStatUrl = computed(() => `https://tgstat.com/channel/@${group.username}`)

function formatPrice(idx) {
  const key = Object.keys(group.ad_prices)[idx]
  return group.ad_prices[key] || 0
}

onMounted(async () => {
  await appStore.initTelegram()
  await Promise.all([fetchSubjects(), fetchCountries(), fetchLanguages()])
  await fetchGroup()
})
</script>