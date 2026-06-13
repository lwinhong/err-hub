import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { getSettings } from '../api/settings'

export const useSettingsStore = defineStore('settings', () => {
  const data = ref({})
  const loaded = ref(false)

  const defaultPageSize = computed(() => data.value.default_page_size?.value ?? 20)
  const dataRetentionDays = computed(() => data.value.data_retention_days?.value ?? 90)
  const showUserColumn = computed(() => data.value.show_user_column?.value ?? false)

  async function fetchSettings() {
    try {
      const res = await getSettings()
      data.value = res.data
      loaded.value = true
    } catch {
      // keep defaults
    }
  }

  return { data, loaded, defaultPageSize, dataRetentionDays, showUserColumn, fetchSettings }
})
