import { createRouter, createWebHashHistory } from 'vue-router'
import Home         from '../views/Home.vue'
import Balance      from '../views/Balance.vue'
import Mychannels   from '../views/Mychannels.vue'
import Adcatalog    from '../views/Adcatalog.vue'
import Catalog      from '../views/Catalog.vue'
import Myad         from '../views/Myad.vue'
import Profile      from '../views/Profile.vue'
import Channel      from '../views/Channel.vue'
import Mychannel    from '../views/Mychannel.vue'
import Topup        from '../views/Topup.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/balance', component: Balance },
  { path: '/mychannels', component: Mychannels },
  { path: '/adcatalog', component: Adcatalog },
  { path: '/catalog', component: Catalog },
  { path: '/myad/:id', component: Myad, props: true },
  { path: '/profile', component: Profile },
  { path: '/channel/:id', component: Channel, props: true },
  { path: '/mychannel/:id', component: Mychannel, props: true },
  { path: '/topup', component: Topup }
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
