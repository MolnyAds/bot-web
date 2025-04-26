<template>
  <div class="container">
    <router-link to="/" class="back-btn">←</router-link>

    <div class="header">
      <div class="logo">
        <div class="logo-icon">📊</div>
        <div class="logo-text">Статистика</div>
      </div>
      <div class="profile-icon">👤</div>
    </div>

    <div class="stats-container">
      <!-- Общая активность -->
      <div class="stats-block">
        <div class="stats-block-title">Общая активность</div>
        <div class="stats-data">
          <div class="stat-item">
            <span class="stat-label">Размещено реклам:</span>
            <span class="stat-value">15</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Куплено реклам:</span>
            <span class="stat-value">7</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Активные заказы:</span>
            <span class="stat-value">4</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Отменены заказы:</span>
            <span class="stat-value">2</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Средняя цена размещения:</span>
            <span class="stat-value">700 ₽</span>
          </div>
        </div>
      </div>

      <!-- Покупка рекламы -->
      <div class="stats-block">
        <div class="stats-block-title">Покупка рекламы</div>
        <div class="stats-content">
          <div class="stats-data">
            <div class="stat-item"><span class="stat-label">1/24</span></div>
            <div class="stat-item"><span class="stat-label">1/48</span></div>
            <div class="stat-item"><span class="stat-label">Посты</span></div>
            <div class="stat-item"><span class="stat-label">Сторисы</span></div>
          </div>
          <div class="chart-container">
            <!-- SVG-код без изменений -->
            <svg class="donut-chart">
              <defs>
                <linearGradient id="postsGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#4299e1;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#3182ce;stop-opacity:1" />
                </linearGradient>
                <linearGradient id="storiesGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#b19cd9;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#9f7aea;stop-opacity:1" />
                </linearGradient>
              </defs>
              <circle cx="60" cy="60" r="40" class="donut-segment posts"
                      stroke="url(#postsGradient)"
                      stroke-dasharray="188.5 62.8"
                      stroke-dashoffset="0" />
              <circle cx="60" cy="60" r="40" class="donut-segment stories"
                      stroke="url(#storiesGradient)"
                      stroke-dasharray="62.8 188.5"
                      stroke-dashoffset="-188.5" />
            </svg>
            <div class="chart-legend">
              <div class="legend-item"><div class="legend-color posts"></div><span>Посты</span></div>
              <div class="legend-item"><div class="legend-color stories"></div><span>Сторисы</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- По каналам -->
      <div class="stats-block">
        <div class="stats-block-title">По каналам</div>
        <div class="stats-content">
          <div class="stats-data">
            <div class="stat-item">
              <span class="stat-label">Размещений:</span>
              <span class="stat-value large">0</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Заработок:</span>
              <span class="stat-value large">0</span>
            </div>
          </div>
          <div class="chart-container">
            <!-- SVG без изменений -->
            <svg class="line-chart" viewBox="0 0 100 60">
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style="stop-color:#4299e1;stop-opacity:0.5" />
                  <stop offset="100%" style="stop-color:#4299e1;stop-opacity:0" />
                </linearGradient>
              </defs>
              <path class="chart-area" d="M0,50 Q20,40 30,35 T50,30 T70,25 T90,20 L90,60 L0,60 Z" />
              <path class="line-path" d="M0,50 Q20,40 30,35 T50,30 T70,25 T90,20" />
            </svg>
            <div class="chart-footer">Последние 30 дней</div>
          </div>
        </div>
      </div>

      <!-- Продажа рекламы -->
      <div class="stats-block">
        <div class="stats-block-title">Продажа рекламы</div>
        <div class="channels-stats">
          <div class="channel-stat-item">
            <div class="stat-label">Размещений:</div>
            <div class="stat-value large">0</div>
          </div>
          <div class="channel-stat-item">
            <div class="stat-label">Заработок:</div>
            <div class="stat-value large">0</div>
          </div>
          <div class="channel-stat-item">
            <div class="stat-label">Средняя цена:</div>
            <div class="stat-value">200</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Profile'
}
</script>