import { reactive } from 'vue'

export const globalState = reactive({
    user: {
        authenticated: false,
        email: '',
    }
})
