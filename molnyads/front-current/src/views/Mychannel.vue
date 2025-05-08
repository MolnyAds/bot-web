<template>
  <div class="container">
    <router-link to="/mychannels" class="back-btn">←</router-link>

    <div class="channel-header">
      <h1 class="channel-title">{{ group.username }}</h1>
      <div class="channel-info-grid">
        <div class="info-card">
          <div class="info-number">{{ group.subscribers }}</div>
          <div class="info-label">Подписчики</div>
        </div>
        <div class="info-card">
          <div class="info-number">{{ group.avg_views }}</div>
          <div class="info-label">Просмотры</div>
        </div>
      </div>
      <div class="channel-actions">
        <button class="action-btn secondary" @click="editGroup">Сохранить изменения</button>
        <button class="action-btn primary" @click="toggleCatalog">
          {{ inCatalog ? 'Убрать из каталога' : 'Добавить в каталог' }}
        </button>
      </div>
    </div>

    <div class="schedule-section">
      <div class="schedule-title">Расписание публикаций</div>
      <div class="schedule-grid" ref="grid">
        <!-- Генерация ячеек расписания -->
      </div>
      <button class="action-btn primary" @click="saveSchedule" style="margin-top: 16px;">
        Сохранить расписание
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
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
  ad_prices: {},
  subscribers: 0,
  avg_views: 0,
  all_slots_ids: [],
  busy_slots_ids: []
})

const inCatalog = ref(false)
const gridRef = ref(null)

const headers = () => ({
  'Content-Type': 'application/json',
  Authorization: 'Telegram-Init-Data ' + appStore.tgInitDataRow
})

function initSchedule() {
  const grid = gridRef.value
  grid.innerHTML = ''
  // Можно сгенерировать ячейки аналогично примеру
}

async function saveSchedule() {
  // собираем выбранные schedule_ids
  const scheduleIds = []
  gridRef.value.querySelectorAll('.schedule-cell.active').forEach(cell => {
    scheduleIds.push(cell.dataset.slotId)
  })
  try {
    await fetch(
      `${appStore.apiBaseUrl}/api/my/group/${groupId}/schedule`,
      {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({ schedule_ids: scheduleIds }),
        mode: 'cors'
      }
    )
    alert('Расписание сохранено')
  } catch (e) {
    console.error('Ошибка сохранения расписания:', e)
  }
}

async function editGroup() {
  try {
    await fetch(
      `${appStore.apiBaseUrl}/api/my/group/${groupId}/edit`,
      {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({
          subject_ids: group.subject_ids,
          country_id: group.country_id,
          language_id: group.language_id,
          ad_prices: group.ad_prices
        }),
        mode: 'cors'
      }
    )
    alert('Изменения сохранены')
  } catch (e) {
    console.error('Ошибка сохранения группы:', e)
  }
}

async function toggleCatalog() {
  try {
    inCatalog.value = !inCatalog.value
    await fetch(
      `${appStore.apiBaseUrl}/api/my/group/${groupId}/set_in_catalog`,
      {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({ in_catalog: inCatalog.value }),
        mode: 'cors'
      }
    )
  } catch (e) {
    console.error('Ошибка обновления каталога:', e)
  }
}

onMounted(async () => {
  await appStore.initTelegram()
  const res = await fetch(
    `${appStore.apiBaseUrl}/api/my/group/${groupId}`,
    { headers: headers(), mode: 'cors' }
  )
  Object.assign(group, await res.json())
  // установить начальный статус каталога, если есть
  initSchedule()
})
</script>