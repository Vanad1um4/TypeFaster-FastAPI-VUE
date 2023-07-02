<template>

<div class="menu inner-box">

    <div v-for="menu in menuButtonsArray" v-bind:class="[menu.btnClass, { 'primary-url': $route.name === menu.url }]">
        <a class="a-btn" v-on:click="$router.push({ name: menu.url })"> {{ menu.text }} </a>
    </div>

    <div class="menu-button options-drop-down">
        <a class="a-btn"> {{ globalState.user.authenticated ? 'Profile' : 'Login' }} </a>
        <div class="options-content-hide">

            <div class="options-content-auth-cont">
                <div
                    v-if="globalState.user.authenticated === false"
                    class="auth-btn auth-login-btn"
                    v-on:click="login"

                >
                    <div class="auth-btn-txt">🔓 Login via github</div>
                </div>
                <div
                    v-if="globalState.user.authenticated === true"
                    class="auth-header"
                >
                    Logged in as:
                </div>
                <div
                    v-if="globalState.user.authenticated === true"
                    class="auth-email"
                >
                    {{ globalState.user.email }}
                </div>
                <div
                    v-if="globalState.user.authenticated === true"
                    class="auth-btn auth-logout-btn"
                    v-on:click="logout"
                >
                    <div class="auth-btn-txt">🔓 Logout</div>
                </div>
            </div>

            <div
                v-if="globalState.user.authenticated === true"
                class="options-content-vis-settings-cont options-dd-content-grid"
            >

                <div class="site-options-header">
                    Visual settings
                </div>

                <div class="dark-mode-text">
                    Dark theme
                </div>

                <input
                    type="checkbox"
                    class="dark-mode-checkbox"
                    v-model="globalState.options.darkMode.val"
                    v-bind:disabled="localOptions.darkMode.disabled"
                    v-on:change="setOptionsFetch"
                >

                <div class="width-text" title="You can specify the maximum width of the main window">
                    Max page width (px)
                </div>

                <input
                    type="text"
                    class="width-input"
                    title="800 - 3840"
                    v-model="globalState.options.windowWidthInput.val"
                    v-bind:disabled="localOptions.windowWidthInput.disabled"
                    v-on:keydown.enter="setOptionsFetch"
                >

                <button
                    type="submit"
                    class="width-save"
                    v-bind:disabled="localOptions.windowWidthInput.disabled"
                    v-on:click="setOptionsFetch"
                >💾</button>

                <div class="show-stats-bar-text" title="Show statistics bar while typing">
                    Show stats bar
                </div>

                <input
                    type="checkbox"
                    class="show-stats-bar-checkbox"
                    v-model="globalState.options.showStatsBar.val"
                    v-bind:disabled="localOptions.showStatsBar.disabled"
                    v-on:change="setOptionsFetch"
                >

                <div class="show-progress-bar-text" title="Show progress bar while typing">
                    Show progress bar
                </div>

                <input
                    type="checkbox"
                    class="show-progress-bar-checkbox"
                    v-model="globalState.options.showProgressBar.val"
                    v-bind:disabled="localOptions.showProgressBar.disabled"
                    v-on:change="setOptionsFetch"
                >

                <div class="show-error-history-text" title="Show errors on finished texts while typing">
                    Show past errors
                </div>

                <input
                    type="checkbox"
                    class="show-error-history-checkbox"
                    v-model="globalState.options.showErrorHistory.val"
                    v-bind:disabled="localOptions.showErrorHistory.disabled"
                    v-on:change="setOptionsFetch"
                >

                <div class="line-height-text" title="You can specify the position of active line on the screen. For example: 0 - in the beginning, 50 - in the middle, 100 - in the end.">
                    Active line position (%)
                </div>

                <input
                    type="text"
                    class="line-height-input"
                    title="1 - 99"
                    v-model="globalState.options.activeLinePosition.val"
                    v-bind:disabled="localOptions.activeLinePosition.disabled"
                    v-on:keydown.enter="setOptionsFetch"
                >

                <button
                    type="submit"
                    class="line-height-save"
                    v-bind:disabled="localOptions.activeLinePosition.disabled"
                    v-on:click="setOptionsFetch"
                >💾</button>

                <div class="texts-gap-text" title="You can specify the gap between texts in pixels">
                    Gap between texts (px)
                </div>

                <input
                    type="text"
                    class="texts-gap-input"
                    title="0 - 9999"
                    v-model="globalState.options.gapBetweenTexts.val"
                    v-bind:disabled="localOptions.gapBetweenTexts.disabled"
                    v-on:keydown.enter="setOptionsFetch"
                >

                <button
                    type="submit"
                    class="texts-gap-save"
                    v-bind:disabled="localOptions.gapBetweenTexts.disabled"
                    v-on:click="setOptionsFetch"
                >💾</button>

            </div>

            <div
                v-if="globalState.user.authenticated === true"
                class="options-content-stats-settings-cont options-dd-content-grid"
            >

                <div class="stats-options-header">
                    Stats calc settings
                </div>

                <div class="stats-slice-len-text">
                    Stats slice length
                </div>

                <input
                    type="text"
                    class="stats-slice-len-input"
                    title="Duration of a stats slice. Expected positive number of minutes."
                    v-model="globalState.options.statsSliceLengthMinutes.val"
                    v-bind:disabled="localOptions.statsSliceLengthMinutes.disabled"
                    v-on:keydown.enter="setOptionsFetch"
                >

                <button
                    type="submit"
                    class="stats-slice-len-save"
                    v-on:click="setOptionsFetch"
                >💾</button>

                <div class="stats-use-n-slices-text">
                    Use stats slices
                </div>

                <input
                    type="text"
                    class="stats-use-n-slices-input"
                    title="How namy last stats slices will be used to calculate your CPM, WPM, ACC. Positive integer number expected."
                    v-model="globalState.options.useNLastMinutesForStats.val"
                    v-bind:disabled="localOptions.useNLastMinutesForStats.disabled"
                    v-on:keydown.enter="setOptionsFetch"
                >

                <button
                    type="submit"
                    class="stats-use-n-slices-save"
                    v-on:click="setOptionsFetch"
                >💾</button>

            </div>

        </div>
    </div>
</div>

<Modals ref="modalsRef"/>

</template>





<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import Modals from './modals.vue'
import { globalState } from '../state.js'

const modalsRef = ref()

const menuButtonsArray = [
    { 'text': 'Library', 'type': 'btn', 'url': 'library', 'btnClass': 'menu-button books'},
    { 'text': 'Type', 'type': 'btn', 'url': 'type', 'btnClass': 'menu-button type'},
    { 'text': 'Statistics', 'type': 'btn', 'url': 'stats' , 'btnClass': 'menu-button stats'},
    { 'text': '', 'type': 'divider', 'btnClass': 'menu-button-divider'},
]

const localOptions = reactive({
    'darkMode': {'disabled': true},
    'windowWidthInput': {'disabled': false},
    'showStatsBar': {'disabled': false},
    'showProgressBar': {'disabled': false},
    'showErrorHistory': {'disabled': false},
    'activeLinePosition': {'disabled': false},
    'gapBetweenTexts': {'disabled': false},

    'statsSliceLengthMinutes': {'val': 60},
    'useNLastMinutesForStats': {'val': 5},
})


function reapplyClasses() {
    if (globalState.options.darkMode.val === true) {
        mainBody.classList.remove('light')
        mainBody.classList.add('night')
    } else if (globalState.options.darkMode.val === false) {
        mainBody.classList.remove('night')
        mainBody.classList.add('light')
    }

    root.style.setProperty('--main-width', `${globalState.options.windowWidthInput.val}px`);

    if (globalState.options.showStatsBar.val === true) {
        mainBody.classList.remove('hide-stats-bar')
    } else {
        mainBody.classList.add('hide-stats-bar')
    }

    if (globalState.options.showProgressBar.val === true) {
        mainBody.classList.remove('hide-progress-bar')
    } else {
        mainBody.classList.add('hide-progress-bar')
    }

    if (globalState.options.showErrorHistory.val === true) {
        mainBody.classList.remove('hide-error-history')
    } else {
        mainBody.classList.add('hide-error-history')
    }
}


function blockInputFields() {
    localOptions.darkMode.disabled = true
    localOptions.windowWidthInput.disabled = true
    localOptions.showStatsBar.disabled = true
    localOptions.showProgressBar.disabled = true
    localOptions.showErrorHistory.disabled = true
    localOptions.activeLinePosition.disabled = true
    localOptions.gapBetweenTexts.disabled = true

    localOptions.statsSliceLengthMinutes.disabled = true
    localOptions.useNLastMinutesForStats.disabled = true
}


function unblockInputFields() {
    localOptions.darkMode.disabled = false
    localOptions.windowWidthInput.disabled = false
    localOptions.showStatsBar.disabled = false
    localOptions.showProgressBar.disabled = false
    localOptions.showErrorHistory.disabled = false
    localOptions.activeLinePosition.disabled = false
    localOptions.gapBetweenTexts.disabled = false

    localOptions.statsSliceLengthMinutes.disabled = false
    localOptions.useNLastMinutesForStats.disabled = false
}


function optionInputsValidate() {
    const windowWidthValue = parseInt(globalState.options.windowWidthInput.val)
    if (windowWidthValue < 800) {
        pushNotification('Should be 800 pixels or more, setting to 800...', 'info', 5)
        globalState.options.windowWidthInput.val = 800
    } else if (windowWidthValue > 3840) {
        pushNotification('Should be 3840 pixels or less, setting to 3840...', 'info', 5)
        globalState.options.windowWidthInput.val = 3840
    } else if (isNaN(windowWidthValue)) {
        pushNotification('Should be a positive integer number from 800 to 3840, setting 1000...', 'info', 5)
        globalState.options.windowWidthInput.val = 1000
    } else {
        globalState.options.windowWidthInput.val = windowWidthValue
    }


    const activeLinePositionValue = parseInt(globalState.options.activeLinePosition.val)
    if (activeLinePositionValue < 1 || activeLinePositionValue > 99 || isNaN(activeLinePositionValue)) {
        pushNotification('Should be an integer number of percent, setting to 50', 'info', 5)
        globalState.options.activeLinePosition.val = 50
    } else {
        globalState.options.activeLinePosition.val = activeLinePositionValue
    }


    const gapBetweenTextsValue = parseInt(globalState.options.gapBetweenTexts.val)
    if (gapBetweenTextsValue < 0 || gapBetweenTextsValue > 9999 || isNaN(gapBetweenTextsValue)) {
        pushNotification('Should be a reasonable positive integer number of pixels between texts, setting to 20', 'info', 5)
        globalState.options.gapBetweenTexts.val = 20
    } else {
        globalState.options.gapBetweenTexts.val = gapBetweenTextsValue
    }


    const statsSliceLengthMinutesValue = parseInt(globalState.options.statsSliceLengthMinutes.val)
    if (statsSliceLengthMinutesValue < 1 || statsSliceLengthMinutesValue > 1_000_000 || isNaN(statsSliceLengthMinutesValue)) {
        pushNotification('Should be a reasonable positive integer number of minutes, setting to 60', 'info', 5)
        globalState.options.statsSliceLengthMinutes.val = 60
    } else {
        globalState.options.statsSliceLengthMinutes.val = statsSliceLengthMinutesValue
    }


    const useNLastMinutesForStatsValue = parseInt(globalState.options.useNLastMinutesForStats.val)
    if (useNLastMinutesForStatsValue < 1 || useNLastMinutesForStatsValue > 1_000_000 || isNaN(useNLastMinutesForStatsValue)) {
        pushNotification('Should be a reasonable positive integer number of minutes, setting to 60', 'info', 5)
        globalState.options.useNLastMinutesForStats.val = 60
    } else {
        globalState.options.useNLastMinutesForStats.val = useNLastMinutesForStatsValue
    }
}


function setOptionsFetch() {
    optionInputsValidate()
    reapplyClasses()
    const requestData = {
        'method': 'PUT',
        'headers': { 'Accept': 'application/json', 'Content-Type': 'application/json' },
        'body': JSON.stringify({
            'dark_mode': globalState.options.darkMode.val,
            'window_width': globalState.options.windowWidthInput.val,
            'show_stats_bar': globalState.options.showStatsBar.val,
            'show_progress_bar': globalState.options.showProgressBar.val,
            'show_error_history': globalState.options.showErrorHistory.val,
            'active_line_position': globalState.options.activeLinePosition.val,
            'gap_between_texts': globalState.options.gapBetweenTexts.val,

            'stats_slice_length_minutes': globalState.options.statsSliceLengthMinutes.val,
            'use_n_last_minutes_for_stats': globalState.options.useNLastMinutesForStats.val,
        })
    }
    blockInputFields()
    fetch(`/api/user/`, requestData)
        .then(response => {
            // console.log('set', response)
            if (response.status === 204) {
                unblockInputFields()
            } else {
                pushNotification('Some error has occured...', 'error', 5)
            }
        })
}


function getOptionsFetch() {
    const requestData = {
        'method': 'GET',
        'headers': { 'Accept': 'application/json', 'Content-Type': 'application/json' }
    }
    blockInputFields()
    fetch('/api/user/', requestData)
        .then( response => {
            if (response.status === 200) {
                response.json().then( result => {
                    // console.log('get', result)
                    globalState.user.authenticated = result.authenticated
                    globalState.user.email = result.email

                    globalState.options.darkMode.val = result.dark_mode
                    globalState.options.windowWidthInput.val = result.window_width
                    globalState.options.showStatsBar.val = result.show_stats_bar
                    globalState.options.showProgressBar.val = result.show_progress_bar
                    globalState.options.showErrorHistory.val = result.show_error_history
                    globalState.options.activeLinePosition.val = result.active_line_position
                    globalState.options.gapBetweenTexts.val = result.gap_between_texts

                    globalState.options.statsSliceLengthMinutes.val = result.stats_slice_length_minutes
                    globalState.options.useNLastMinutesForStats.val = result.use_n_last_minutes_for_stats
                    unblockInputFields()
                    reapplyClasses()
                })
            } else {
                pushNotification('Some error has occured...', 'error', 5)
            }
        })
}


function login() {
    window.location.href = '/github_login'
}


function logout() {
    window.location.href = '/logout'
}


function pushNotification(txt, category, seconds) { // possible categories: 'error', 'warning', 'good' and 'info'
    modalsRef.value.addNotification(txt, category, seconds)
}


let mainBody, root

onMounted(() => {
    getOptionsFetch()
    root = document.querySelector(':root')
    mainBody = document.querySelector('body')
})

</script>





<style>
:root {
    --optionsGTC1: 240px;
    --optionsGTC2: 53px;
    --optionsGTC3: 28px;
    --optionsGapH: 7px;
    --optionsGapV: 7px;
}
</style>

<style scoped>
.menu {
    display: flex;
    gap: 5px;
}

.menu-button-divider {
    display: flex;
    flex-grow: 1;
}

.menu-button {
    display: flex;
    border-radius: 3px;
    font-size: 27px;
    padding: 3px;
    padding-left: 15px;
    padding-right: 15px;
    position: relative;
    bottom: 0px;
    transition: 0.1s;
    user-select: none;
}

body.light .menu-button { background-color: var(--grey2) }
body.night .menu-button { background-color: var(--grey7) }

.menu-button>a {
    text-decoration: none;
    font-weight: bold;
}

body.light .menu-button>.a-btn { color: var(--grey7) }
body.night .menu-button>.a-btn { color: var(--grey3) }

.menu-button:hover {
    cursor: pointer;
    bottom: 3px;
}
.menu-button.primary-url { bottom: 3px; }

body.light .menu-button:hover { background-color: var(--grey3); }
body.light .menu-button:hover>.a-btn { color: var(--grey8); }
body.light .menu-button.primary-url { background-color: var(--grey7); }
body.light .menu-button.primary-url>.a-btn { color: var(--grey2); }

body.night .menu-button:hover { background-color: var(--grey6); }
body.night .menu-button:hover>.a-btn { color: var(--grey2); }
body.night .menu-button.primary-url { background-color: var(--grey3); }
body.night .menu-button.primary-url>.a-btn { color: var(--grey9); }





.options-drop-down {
    position: relative;
    display: inline-block;
}

.options-drop-down:hover {
    cursor: default;
    bottom: 0px;
}

.options-drop-down:hover .options-content-hide {
    display: block;
}

.options-drop-down > .options-content-hide {
    display: none;
    position: absolute;
    padding: 10px 12px;
    z-index: 1;
    border-radius: 3px;
    right: 1px;
}

body.light .options-content-hide {
    color: var(--grey8);
    background-color: var(--grey2);
    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
    border: 1px solid #b1b1b1;
}
body.night .options-content-hide {
    color: var(--grey2);
    background-color: var(--grey8);
    box-shadow: 0 8px 16px rgb(255 255 255 / 10%);
    border: 1px solid var(--grey6);
}



.options-dd-content-grid {
    display: grid;
    grid-template-columns: var(--optionsGTC1) var(--optionsGTC2) var(--optionsGTC3);
    grid-gap: var(--optionsGapH) var(--optionsGapV);
    font-size: 21px;
}



.options-content-auth-cont {
    width: calc(var(--optionsGTC1) + var(--optionsGapV) + var(--optionsGTC2) + var(--optionsGapV) + var(--optionsGTC3))
}

.auth-header {
    text-align: center;
    font-weight: bold;
    font-size: 23px;
    margin-bottom: 7px;
}
.auth-email {
    font-size: 23px;
    margin-bottom: 7px;
    white-space: nowrap;
    overflow: hidden;
}
.auth-login-btn {
}
.auth-logout-btn {
}
.auth-btn {
    display: flex;
    border-radius: 3px;
    font-size: 23px;
    padding: 3px;
    padding-left: 15px;
    padding-right: 15px;
    position: relative;
    bottom: 0px;
    /* transition: 0.1s; */
}
body.light .auth-btn { background-color: var(--grey3) }
body.night .auth-btn { background-color: var(--grey7) }

.auth-btn>div {
    text-decoration: none;
    font-weight: bold;
    width: 100%;
    text-align: center;
}

body.light .auth-btn>div { color: var(--grey7) }
body.night .auth-btn>div { color: var(--grey3) }

.auth-btn:hover {
    cursor: pointer;
}

body.light .auth-btn:hover { background-color: var(--grey4); }
body.night .auth-btn:hover { background-color: var(--grey6); }

body.light .auth-btn:hover>div { color: var(--grey8); }
body.night .auth-btn:hover>div { color: var(--grey2); }




.options-content-vis-settings-cont {
    margin-top: 30px;
}
.site-options-header {
    grid-column: span 3;
    text-align: center;
    font-weight: bold;
    font-size: 23px;
}
.options-drop-down .dark-mode-text {
    white-space: nowrap;
    grid-column: span 2
}
.options-drop-down .dark-mode-checkbox {
    transform: scale(1.2);
}

.options-drop-down .width-text {
    /* font-size: 23px; */
}
.options-drop-down .width-input {
    font-size: 17px;
}
.options-drop-down .width-save {
    font-size: 17px;
    padding: 0px 0px;
}

.options-drop-down .show-stats-bar-text {
    grid-column: span 2
}
.options-drop-down .show-stats-bar-checkbox {
    transform: scale(1.2);
}

.options-drop-down .show-progress-bar-text {
    grid-column: span 2
}
.options-drop-down .show-progress-bar-checkbox {
    transform: scale(1.2);
}

.options-drop-down .show-error-history-text {
    grid-column: span 2
}
.options-drop-down .show-error-history-checkbox {
    transform: scale(1.2);
}

.options-drop-down .line-height-input {
    font-size: 17px;
}
.options-drop-down .line-height-save {
    font-size: 17px;
    padding: 0px 0px;
}

.options-drop-down .texts-gap-input {
    font-size: 17px;
}
.options-drop-down .texts-gap-save {
    font-size: 17px;
    padding: 0px 0px;
}






.options-content-stats-settings-cont {
    margin-top: 30px;
}
.stats-options-header {
    grid-column: span 3;
    text-align: center;
    font-weight: bold;
    font-size: 23px;
}
.stats-slice-len-text {
    /* grid-column: span 2 */
}
.stats-slice-len-input {
    font-size: 17px;
}

.stats-slice-len-save {
    font-size: 17px;
    padding: 0px 0px;
}
.stats-use-n-slices-text {
    /* grid-column: span 2 */
}
.stats-use-n-slices-input {
    font-size: 17px;
}
.stats-use-n-slices-save {
    font-size: 17px;
    padding: 0px 0px;
}

</style>