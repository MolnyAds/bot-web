<template>
  <div class="container">
    <router-link to="/channels" class="back-btn">←</router-link>

    <div class="channel-header">
      <div class="channel-title">Molny Channel</div>
      <div class="channel-info-grid">
        <div class="info-card">
          <div class="info-number">12.5K</div>
          <div class="info-label">Подписчики</div>
        </div>
        <div class="info-card">
          <div class="info-number">4.2K</div>
          <div class="info-label">Просмотры</div>
        </div>
      </div>
      <div class="channel-actions">
        <button class="action-btn secondary">Изменить</button>
        <button class="action-btn primary">Отключить канал</button>
      </div>
    </div>

    <div class="schedule-section">
      <div class="schedule-title">Расписание публикаций</div>
      <div class="schedule-grid" id="scheduleGrid">
        <!-- Ячейки будут инициализироваться скриптом -->
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Channel',
  mounted() {
    // Логика инициализации расписания аналогична оригиналу
    this.initSchedule()
  },
  methods: {
    initSchedule() {
      const grid = this.$el.querySelector('#scheduleGrid')
      const days = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс']
      const hours = Array.from({ length: 24 }, (_, i) => i)

      // Пустая ячейка
      const empty = document.createElement('div')
      empty.className = 'schedule-time-header'
      grid.appendChild(empty)

      // Заголовки дней
      days.forEach(day => {
        const el = document.createElement('div')
        el.className = 'schedule-day-header'
        el.textContent = day
        grid.appendChild(el)
      })

      hours.forEach(hour => {
        const label = document.createElement('div')
        label.className = 'schedule-time-label'
        label.textContent = hour
        grid.appendChild(label)

        days.forEach((_, i) => {
          const cell = document.createElement('div')
          cell.className = 'schedule-cell'
          cell.dataset.hour = hour
          cell.dataset.day = i
          cell.addEventListener('click', () => cell.classList.toggle('active'))
          grid.appendChild(cell)
        })
      })
    }
  }
}
</script>