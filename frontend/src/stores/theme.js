import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const saved = localStorage.getItem('theme')
  const dark = ref(saved ? saved === 'dark' : prefersDark)

  function apply() {
    document.documentElement.setAttribute('data-theme', dark.value ? 'dark' : 'light')
  }

  function toggle() {
    dark.value = !dark.value
  }

  watch(dark, (val) => {
    localStorage.setItem('theme', val ? 'dark' : 'light')
    apply()
  })

  apply()

  return { dark, toggle }
})
