<template>
  <div class="container">
    <router-link to="/adcatalog" class="back-btn">←</router-link>

    <div class="channel-header">
      <h1 class="channel-title">Название канала</h1>
      <div class="channel-info">
        <div class="info-row"><span class="info-icon">📁</span><span>Тематика: <strong>Бизнес / IT</strong></span></div>
        <div class="info-row"><span class="info-icon">🌍</span><span>Гео / Язык: <strong>Россия / Русский</strong></span></div>
      </div>
    </div>

    <div class="channel-visual">
      <div class="channel-logo"><div class="megaphone-icon">📢</div></div>
      <div class="channel-links">
        <div class="link-item">
          <div class="link-icon telegram-icon">✈</div>
          <div class="link-text"><span class="text-bold">t.me:</span> <a href="#" class="link-url">t.me/channelname</a></div>
        </div>
        <div class="link-item">
          <div class="link-icon tgstat-icon">📊</div>
          <div class="link-text"><span class="text-bold">TGStat:</span> <a href="#" class="link-url">tgstat.com/channel/@channelname</a></div>
        </div>
      </div>
    </div>

    <div class="pricing-section">
      <h2 class="pricing-title">Реклама:</h2>
      <div class="pricing-items">
        <div class="pricing-item"><span class="pricing-label">Пост:</span><span class="pricing-value">1 500 ₽</span></div>
        <div class="pricing-item"><span class="pricing-label">Закреплённый пост:</span><span class="pricing-value">2 500 ₽</span></div>
        <div class="pricing-item"><span class="pricing-label">Упоминание:</span><span class="pricing-value">800 ₽</span></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ChannelDetail'
}
</script>