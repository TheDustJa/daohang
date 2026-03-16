import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createHead } from '@unhead/vue/client'
import './style.css'
import App from './App.vue'
import router from './router'

const pinia = createPinia()
const head = createHead()
const app = createApp(App)

app.use(pinia)
app.use(head)
app.use(router)

app.mount('#app')
