import { defineStore } from 'pinia'
import { retrieveLaunchParams } from '@telegram-apps/sdk'

export const useAppStore = defineStore('app', {
  state: () => ({
    tgInitData: null,
    apiBaseUrl: 'https://tough-rivers-vanish.loca.lt', // <-- сюда свой URL
  }),
  actions: {
    async initTelegram() {
      // если ещё не инициализировано
      if (!this.tgInitData) {
        // Optional: инициализировать сам WebApp, если нужен
        const tg = window.Telegram?.WebApp
        if (tg) {
          tg.ready()
          tg.expand()
        }

        try {
          // retrieveLaunchParams распарсит строку launchParams в объект
          const params = await retrieveLaunchParams()
          this.tgInitData = params
          console.log('Telegram launch params:', this.tgInitData)
        } catch (e) {
          console.error('Cannot retrieve Telegram launch params', e)
        }
      }
    }
  }
})