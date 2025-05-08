// src/stores/app.js
import { defineStore } from 'pinia'
import { retrieveLaunchParams, retrieveRawInitData } from '@telegram-apps/sdk'

export const useAppStore = defineStore('app', {
  state: () => ({
    tgInitData: null,
    tgInitDataRow: null,
    apiBaseUrl: 'https://molnyads.tech',
    balance: 0 // храним баланс
  }),
  actions: {
    async initTelegram() {
      // инициализируем WebApp один раз
      if (!this.tgInitData) {
        const tg = window.Telegram?.WebApp
        if (tg) {
          tg.ready()
          tg.expand()
        }
        try {
          // получаем initData и raw
          const params = await retrieveLaunchParams()
          const rawParams = await retrieveRawInitData()
          this.tgInitData = params
          this.tgInitDataRow = rawParams
          console.log('Telegram launch params:', this.tgInitData)
          console.log('Telegram raw initData:', this.tgInitDataRow)
          // сразу после инициализации фетчим баланс
          await this.fetchBalance()
        } catch (e) {
          console.error('Cannot retrieve Telegram launch params:', e)
        }
      }
    },

    async fetchBalance() {
      // Заголовки для запроса баланса
      const headers = {
        'Content-Type': 'application/json',
        Authorization: 'Telegram-Init-Data ' + this.tgInitDataRow
      }
      try {
        const res = await fetch(
          `${this.apiBaseUrl}/api/my/balance`,
          { headers, mode: 'cors' }
        )
        if (!res.ok) throw new Error(`Status ${res.status}`)
        const data = await res.json()
        this.balance = data.balance
      } catch (e) {
        console.error('Error fetching balance:', e)
      }
    }
  }
})
