// https://vitepress.dev/guide/custom-theme
import Theme from 'vitepress/theme'
import HomeLayout from './HomeLayout.vue'
import './custom.css'

export default {
  ...Theme,
  Layout: HomeLayout
}
