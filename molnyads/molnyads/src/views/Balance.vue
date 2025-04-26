<template>
  <div class="container">
    <router-link to="/" class="back-btn">←</router-link>

    <div class="balance-page-header">
      <div class="balance-page-title">Баланс</div>
      <div class="balance-card">
        <div class="balance-info-main">
          <div class="balance-label">Ваш баланс</div>
          <div class="balance-amount-main">7 500 ₽</div>
        </div>
        <button class="withdraw-btn">Вывести</button>
      </div>
    </div>

    <div class="history-section">
      <div class="history-title">История операций</div>

      <div class="transaction-list">
        <div class="transaction-item">
          <div class="transaction-icon income">+</div>
          <div class="transaction-details">
            <div class="transaction-title">Пополнение</div>
            <div class="transaction-date">21 апр. 2024, 14:30</div>
          </div>
          <div class="transaction-amount income">+4 000 ₽</div>
        </div>

        <div class="transaction-item">
          <div class="transaction-icon expense">−</div>
          <div class="transaction-details">
            <div class="transaction-title">Покупка рекламы</div>
            <div class="transaction-date">20 апр. 2024, 09:15</div>
          </div>
          <div class="transaction-amount expense">−2 500 ₽</div>
        </div>

        <div class="transaction-item">
          <div class="transaction-icon income">+</div>
          <div class="transaction-details">
            <div class="transaction-title">Зачисление от продажи</div>
            <div class="transaction-date">18 апр. 2024, 16:20</div>
          </div>
          <div class="transaction-amount income">6 000 ₽</div>
        </div>

        <div class="transaction-item">
          <div class="transaction-icon expense">−</div>
          <div class="transaction-details">
            <div class="transaction-title">Вывод средств</div>
            <div class="transaction-date">17 апр. 2024, 12:45</div>
          </div>
          <div class="transaction-amount expense">−1 200 ₽</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Balance'
};
</script>
