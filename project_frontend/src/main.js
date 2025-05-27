import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import './assets/depositcompare.css'
import './assets/login.css'
import './assets/signup.css'
import './assets/StockVoiceAnalysis.css'
import './assets/Board.css'
import './assets/SpotCompare.css'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faMagnifyingGlass, faPaperPlane } from '@fortawesome/free-solid-svg-icons'


library.add(faMagnifyingGlass, faPaperPlane)

const app = createApp(App)
app.component('font-awesome-icon', FontAwesomeIcon)
app.use(router)
app.mount('#app')

