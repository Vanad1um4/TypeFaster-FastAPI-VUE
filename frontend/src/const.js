export const chartOptions = {
    'responsive': true,
    'maintainAspectRatio': false,
    'stacked': false,
    'scales': {
        'y': {
            'type': 'linear',
            'display': true,
            'position': 'left',
        },
        'y1': {
            'type': 'linear',
            'display': true,
            'position': 'left',
            'grid': {
                'drawOnChartArea': false,
            },
        },
        'y2': {
            'type': 'linear',
            'display': true,
            'position': 'right',
            'grid': {
                'drawOnChartArea': false,
            },
        },
    },
}

export const chartColors = {
    'light': {
        'cpm': '#119311',
        'wpm': '#4848e3',
        'acc': '#d32d2d',
    },
    'night': {
        'cpm': '#5dd75d',
        'wpm': '#7d7dff',
        'acc': '#dd6060',
    },
}