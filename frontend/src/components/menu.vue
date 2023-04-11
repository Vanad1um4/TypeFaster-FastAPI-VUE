<template>

<div class="menu inner-box">

    <div v-for="menu in menuButtons" v-bind:class="[menu.btnClass, { 'primary-url': $route.name === menu.url }]">
        <a class="a-btn" v-on:click="$router.push({ name: menu.url })"> {{ menu.text }} </a>
    </div>

    <div class="menu-button options-drop-down">
        <a class="a-btn"> {{ globalState.user.authenticated ? 'Profile' : 'Login' }} </a>
        <div class="options-content-hide">
            <div class="options-content-grid">
                <!-- <div class="profile-header"> Profile </div> -->
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
                    v-if="globalState.user.authenticated === false"
                    class="auth-btn auth-login-btn"
                    v-on:click="login"

                >
                    <div class="auth-btn-txt">🔓 Login via github</div>
                </div>
                <div
                    v-if="globalState.user.authenticated === true"
                    class="auth-btn auth-logout-btn"
                    v-on:click="logout"
                >
                    <div class="auth-btn-txt">🔓 Logout</div>
                </div>

                <div
                    v-if="globalState.user.authenticated === true"
                    class="options-header"
                > Settings </div>
                <div
                    v-if="globalState.user.authenticated === true"
                    class="text dark-mode-text"
                >{{ options.darkMode.text }}</div>
                <input
                    v-if="globalState.user.authenticated === true"
                    type="checkbox"
                    class="checkbox dark-mode-checkbox"
                    v-model="options.darkMode.val"
                    v-bind:disabled="options.darkMode.disabled"
                    v-on:change="sendOptionsToServer"
                >

                <div
                    v-if="globalState.user.authenticated === true"
                    class="text width-text"
                >Max width</div>
                <input
                    v-if="globalState.user.authenticated === true"
                    type="text"
                    class="input-field width-input"
                    title="800 - 3840"
                    v-model="options.windowWidthInput.val"
                    v-bind:disabled="options.windowWidthInput.disabled"
                    v-on:keydown.enter="sendOptionsToServer"
                >
                <button
                    v-if="globalState.user.authenticated === true"
                    type="submit"
                    class="width-save"
                    v-on:click="sendOptionsToServer"
                >💾</button>

                <div
                    v-if="globalState.user.authenticated === true"
                    class="text show-stats-bar-text"
                >{{ options.showStatsBar.text }}</div>
                <input
                    v-if="globalState.user.authenticated === true"
                    type="checkbox"
                    class="checkbox show-stats-bar-checkbox"
                    v-model="options.showStatsBar.val"
                    v-bind:disabled="options.showStatsBar.disabled"
                    v-on:change="sendOptionsToServer"
                >

                <div
                    v-if="globalState.user.authenticated === true"
                    class="text show-progress-bar-text"
                >{{ options.showProgressBar.text }}</div>
                <input
                    v-if="globalState.user.authenticated === true"
                    type="checkbox"
                    class="checkbox show-progress-bar-checkbox"
                    v-model="options.showProgressBar.val"
                    v-bind:disabled="options.showProgressBar.disabled"
                    v-on:change="sendOptionsToServer"
                >

                <div
                    v-if="globalState.user.authenticated === true"
                    class="text show-error-history-text"
                >
                    {{ options.showErrorHistory.text }}
                </div>
                <input
                    v-if="globalState.user.authenticated === true"
                    type="checkbox"
                    class="checkbox show-error-history-checkbox"
                    v-model="options.showErrorHistory.val"
                    v-bind:disabled="options.showErrorHistory.disabled"
                    v-on:change="sendOptionsToServer"
                >
            </div>
        </div>
    </div>
</div>

<Modals ref="modalsRef"/>

</template>





<script setup>

import { ref, reactive, onMounted } from 'vue';
import Modals from './modals.vue'
import { globalState } from '../state.js'

const modalsRef = ref()

const menuButtons = [
    { text: 'Library', type: 'btn', url: 'library', btnClass: 'menu-button books'},
    { text: 'Type', type: 'btn', url: 'type', btnClass: 'menu-button type'},
    { text: 'Statistics', type: 'btn', url: 'stats' , btnClass: 'menu-button stats'},
    { text: '', type: 'divider', btnClass: 'menu-button-divider'},
    // { text: '👤️️', type: 'options' , btnClass: 'menu-button options-drop-down'},
    // { text: '🛠️️', type: 'options' , btnClass: 'menu-button options-drop-down'},
]

// const user = reactive ({
//     authenticated: false,
//     email: '',
// })

const options = reactive({
    darkMode: { text: 'Dark theme', val: false, disabled: true },
    windowWidthInput: { text: 'Main width', val: 1000, disabled: false },
    windowWidthBtn: { disabled: false }, // TODO
    showStatsBar: { text: 'Show stats bar', val: true, disabled: false },
    showProgressBar: { text: 'Show progress bar', val: true, disabled: false },
    showErrorHistory: { text: 'Show error history', val: true, disabled: false },
})

function applyVars() {
    if (options.darkMode.val === true) {
        mainBody.classList.remove('light')
        mainBody.classList.add('night')
    } else if (options.darkMode.val === false) {
        mainBody.classList.remove('night')
        mainBody.classList.add('light')
    }

    root.style.setProperty('--main-width', `${options.windowWidthInput.val}px`);

    if (options.showStatsBar.val === true) {
        mainBody.classList.remove('hide-stats-bar')
    } else {
        mainBody.classList.add('hide-stats-bar')
    }

    if (options.showProgressBar.val === true) {
        mainBody.classList.remove('hide-progress-bar')
    } else {
        mainBody.classList.add('hide-progress-bar')
    }

    if (options.showErrorHistory.val === true) {
        mainBody.classList.remove('hide-error-history')
    } else {
        mainBody.classList.add('hide-error-history')
    }
}

function windowWidthValidate() {
    const value = parseInt(options.windowWidthInput.val)
    if (value < 800) {
        options.windowWidthInput.val = 800
    } else if (value > 3840) {
        options.windowWidthInput.val = 3840
    } else if (isNaN(value)) {
        options.windowWidthInput.val = 1000
    } else {
        options.windowWidthInput.val = value
    }
}

function sendOptionsToServer() {
    windowWidthValidate()
    applyVars()
    const requestData = {
        method: 'PUT',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
            'dark_mode': options.darkMode.val,
            'window_width': options.windowWidthInput.val,
            'show_stats_bar': options.showStatsBar.val,
            'show_progress_bar': options.showProgressBar.val,
            'show_error_history': options.showErrorHistory.val,
        })
    }
    options.darkMode.disabled = true
    options.windowWidthInput.disabled = true
    options.showStatsBar.disabled = true
    options.showProgressBar.disabled = true
    options.showErrorHistory.disabled = true
    fetch(`/api/user/`, requestData)
        .then(response => {
            if (response.status === 204) {
                options.darkMode.disabled = false
                options.windowWidthInput.disabled = false
                options.showStatsBar.disabled = false
                options.showProgressBar.disabled = false
                options.showErrorHistory.disabled = false
            } else {
                pushNotification('Some error has occured...', 'error', 5)
            }
        })
}

function getOptionsFromServer() {
    const requestData = {
        method: 'GET',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }
    }
    options.darkMode.disabled = true
    options.windowWidthInput.disabled = true
    options.showStatsBar.disabled = true
    options.showProgressBar.disabled = true
    options.showErrorHistory.disabled = true
    fetch('/api/user/', requestData)
        .then( response => {
            if (response.status === 200) {
                response.json().then( result => {
                    console.log(result)
                    globalState.user.authenticated = result.authenticated
                    globalState.user.email = result.email
                    options.darkMode.val = result.dark_mode
                    options.windowWidthInput.val = result.window_width
                    options.showStatsBar.val = result.show_stats_bar
                    options.showProgressBar.val = result.show_progress_bar
                    options.showErrorHistory.val = result.show_error_history

                    if (globalState.user.authenticated === true) {
                        options.darkMode.disabled = false
                        options.windowWidthInput.disabled = false
                        options.showStatsBar.disabled = false
                        options.showProgressBar.disabled = false
                        options.showErrorHistory.disabled = false
                    }

                    applyVars()
                })
            } else {
                pushNotification('Some error has occured...', 'error', 5)
            }
        })
}

let mainBody, root
onMounted(() => {
    getOptionsFromServer()
    root = document.querySelector(':root')
    mainBody = document.querySelector('body')
})

function login() {
    window.location.href = '/github_login'
}
function logout() {
    window.location.href = '/logout'
}

function pushNotification(txt, category, seconds) { // possible categories: 'error', 'warning', 'good' and 'info'
    modalsRef.value.addNotification(txt, category, seconds)
}

</script>

<!-- <script>
export default {
  setup() {
    return {
      user
    }
  },
}
</script> -->




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

body.light .menu-button:hover { background-color: var(--grey3); }
body.night .menu-button:hover { background-color: var(--grey6); }

body.light .menu-button:hover>.a-btn { color: var(--grey8); }
body.night .menu-button:hover>.a-btn { color: var(--grey2); }

body.light .menu-button.primary-url { background-color: var(--grey7); }
body.night .menu-button.primary-url { background-color: var(--grey3); }

body.light .menu-button.primary-url>.a-btn { color: var(--grey2); }
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
    background-color: var(--grey2);
    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
    border: 1px solid #b1b1b1;
}
body.night .options-content-hide {
    background-color: var(--grey8);
    /* box-shadow: 0px 8px 16px 0px rgba(255,255,255,0.2); */
    box-shadow: 0 8px 16px rgb(255 255 255 / 10%);

    border: 1px solid var(--grey6);
}

.options-drop-down .options-content-grid {
    display: grid;
    grid-template-columns: 163px 53px 28px;
    grid-gap: 10px 6px;
    font-size: 21px;
}


.profile-header, .options-header {
    grid-column: span 3;
    text-align: center;
    font-weight: bold;
    font-size: 23px;
}
.auth-header {
    grid-column: span 3;
}
.auth-email {
    grid-column: span 3;
    white-space: nowrap;
    overflow: hidden;
}
.auth-login-btn {
    grid-column: span 3;
}
.auth-logout-btn {
    grid-column: span 3;
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





.options-header {
    margin-top: 20px;
}
.options-drop-down .dark-mode-text {
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

.options-drop-down .text {
    white-space: nowrap;
    /* font-weight: bold; */
}

</style>