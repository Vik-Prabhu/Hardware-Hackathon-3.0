// https://vitepress.dev/guide/custom-theme
import Theme from 'vitepress/theme'
import './custom.css'
import HomePage from './HomePage.vue'

export default {
  ...Theme,
  enhanceApp({ app }) {
    app.component('HomePage', HomePage)
  }
}
