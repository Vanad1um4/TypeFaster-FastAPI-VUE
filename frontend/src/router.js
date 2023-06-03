import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router'
import Library from './components/library.vue'
import Type from './components/type.vue'
import Stats from './components/stats.vue'

const router = createRouter({
    history: createWebHashHistory(),
    // history: createWebHistory(),
    routes: [
        { path: '/library', name: 'library', component: Library, alias: '/' },
        { path: '/type/:book_id?', name: 'type', component: Type },
        { path: '/stats', name: 'stats', component: Stats },
    ]
})

export default router

// export default createRouter({
//     history: createWebHashHistory(),
//     // history: createWebHistory(),
//     routes: [
//         { path: '/library', name: 'library', component: Library, alias: '/' },
//         { path: '/type/:chapter_id?', name: 'type', component: Type },
//         { path: '/stats', name: 'stats', component: Stats },
//     ]
// })
