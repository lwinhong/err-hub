import { createApp } from 'vue'
import { createPinia } from 'pinia'

/*********** element-plus ****************/
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import 'element-plus/theme-chalk/el-message.css'
import 'element-plus/theme-chalk/el-loading.css'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus';
/*********** element-plus ****************/

import './styles/main.scss'

import App from './App.vue'
import router from './router'
import i18n from './i18n'

const app = createApp(App)
app.use(ElMessage).use(ElNotification).use(ElMessageBox)
app.use(createPinia())
app.use(router)
app.use(i18n)
app.mount('#app')
