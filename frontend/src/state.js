import { reactive } from 'vue'

export const globalState = reactive({
    'user': {
        'authenticated': false,
        'email': '',
    },
    'options': {
        'darkMode': {'val': false},
        'windowWidthInput': {'val': 1000},
        'windowWidthBtn': {'val': false},
        'showStatsBar': {'val': true},
        'showProgressBar': {'val': true},
        'showErrorHistory': {'val': true},

        'statsSliceLengthMinutes': {'val': 60},
        'useNLastMinutesForStats': {'val': 5},
    }
})
