<template>

    <div
        v-if="route.params.book_id"
        class="information"
    >
        <div class="chapter-name">{{ typeState.bookTitle }}</div>
        <div class="filler"></div>
        <div class="stats">
            CPM:&nbsp;{{ calculatedStats.cpm ? calculatedStats.cpm : '---' }} <span>&nbsp;&nbsp;</span>
            WPM:&nbsp;{{ calculatedStats.wpm ? calculatedStats.wpm : '--' }} <span>&nbsp;&nbsp;</span>
            Accuracy:&nbsp;{{ calculatedStats.acc ? calculatedStats.acc : '--' }}%</div>
    </div>

    <div
        v-if="route.params.book_id"
        class="progress-bar"
    >
        completed: {{ calculatedStats.fractionOfBookDone }}%
    </div>

    <div
        v-if="route.params.book_id"
        class="status-bar"
    >
        <div v-show="typeState.pauseStatusMssg" class="status-pause">
            Countdown paused. Pauses more than 5 seconds do not count. Continue typing when ready to resume.
        </div>
        <div v-show="typeState.theEndStatusMssg" class="status-end">
            Completed. Hit [Backspace] to return to library.
        </div>
    </div>

    <div
        v-if="route.params.book_id"
        class="main-scroll"
    >
        <div v-for="(text, textId) in texts" v-bind:class="['text', 'text' + textId, textId == typeState.currTextId ? 'active' : 'inactive']">

            <span v-for="char in text.chars" v-bind:class="char.res"> {{ char.ch }} </span>

            <span
                v-bind:class="[
                    'next-text',
                    (textId == typeState.currTextId && typeState.currCharId == Object.keys(texts[typeState.currTextId]['chars']).length) ? 'current' : ''
                ]"
            >⏎</span>

            <div class="loading-cont">
                <img v-show="text.statsUploadShow.wait" v-bind:src="waitImg" class="wait-img" title="Sending statistics back to server..." >
                <img v-show="text.statsUploadShow.good" v-bind:src="goodImg" class="good-img" title="Stats have been successfully uploaded to the server." >
                <img v-show="text.statsUploadShow.bad" v-bind:src="badImg" class="bad-img" title="Some error has occured..." >
            </div>

        </div>
    </div>

    <Modals ref="modalsRef"/>

</template>







<script setup>

import { ref, reactive, onMounted, onUnmounted, onUpdated } from 'vue';
import { globalState } from '../state.js'
import { useRoute } from 'vue-router'
import Modals from './modals.vue'
import router from '../router.js'

import waitImg from '@/pics/wait.png'
import goodImg from '@/pics/good.png'
import badImg from '@/pics/bad.png'

const route = useRoute()
const modalsRef = ref()
let timeoutID

const keysIgnore = [
    'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
    'CapsLock', 'Control', 'Escape', 'Shift', 'Tab', 'Alt',
    'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
]

let textsStats = reactive({})
let texts = reactive({})

let calculatedStats = reactive({
    cpm: 0,
    wpm: 0,
    acc: 0,
    charsSum: 0,
    charsDoneSum: 0,
    fractionOfBookDone: 0,
})

let typeState = reactive({
    currTextId: 0,
    currCharId: 0,
    globalEnd: false,
    pauseStatusMssg: false,
    theEndStatusMssg: false,
    lastTextId: -1,
    bookTitle: '',
    currSpanLastCalculatedTop: 0,
    textsAmtAfterLastShift: 0,
})


function keyPressEval(event) {
    if (keysIgnore.includes(event.key)) { return }

    if (typeState.globalEnd === false) {
        if (event.key === 'Backspace') { propagateBackward() }
        else {
            if (event.key === ' ') { event.preventDefault() }
            propagateForward(event.key)
        }
    }
    else if (typeState.globalEnd === true && event.key === 'Backspace') { router.push({ name: 'library' }) }
}


function propagateBackward() {
    if (typeState.currCharId > 0 && typeState.currCharId < Object.keys(texts[typeState.currTextId]['chars']).length) {
        texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'neutral'
        typeState.currCharId--
        texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'current'
    }
}


function propagateForward(key) {
    hideWaitStatusMessage()
    clearTimeout(timeoutID)
    timeoutID = setTimeout(showWaitStatusMessage, 5000)

    if (typeState.currCharId < Object.keys(texts[typeState.currTextId]['chars']).length) {

        if (texts[typeState.currTextId]['chars'][typeState.currCharId]['ch'] === key) {
            if (texts[typeState.currTextId]['chars'][typeState.currCharId]['err'] === 0) {
                texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'right'
            } else {
                texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'corrected'
            }
        } else {
            texts[typeState.currTextId]['chars'][typeState.currCharId]['err']++
            texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'wrong'
        }

        texts[typeState.currTextId]['chars'][typeState.currCharId]['time'] = Date.now()
        typeState.currCharId++

        if (typeState.currCharId < Object.keys(texts[typeState.currTextId]['chars']).length) {
            texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'current'
        }

    } else {

        if (key === 'Enter') {
            prepStatsForSending(typeState.currTextId)
            recalcStats(typeState.currTextId)
            evaluateWhetherToFetchMoreTexts()
            paintProgressBar()

            if (typeState.currTextId == typeState.lastTextId) {
                typeState.globalEnd = true
                typeState.theEndStatusMssg = true
                clearTimeout(timeoutID)
            } else {
                const textIds = Object.keys(texts)
                let currTextID = typeState.currTextId.toString()
                const nextId = textIds.indexOf(currTextID) + 1
                typeState.currTextId = textIds[nextId]
                typeState.currCharId = 0
                texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'current'
            }
        }
    }
}


function evaluateWhetherToFetchMoreTexts() {
    for (const textId in texts) {
        if (document.querySelector(`.text${textId}`).getBoundingClientRect().bottom < 0) {
            delete texts[textId]
        } else { break }
    }

    const scrollRectBottom = document.querySelector('.main-scroll').getBoundingClientRect().bottom
    const scrollRectHeight = document.querySelector('.main-scroll').getBoundingClientRect().height
    const lastTextTop = document.querySelector('.main-scroll > div:last-child').getBoundingClientRect().top

    if (lastTextTop < scrollRectBottom + scrollRectHeight) {
        const currBatchLastTextId = Object.keys(texts)[Object.keys(texts).length - 1]

        if (currBatchLastTextId < typeState.lastTextId) {
            getNextBatchOfTextsFetch(currBatchLastTextId)
        }
    }
}


function scrollActiveLineIntoView() {
    const currSpanRectTop = document.querySelector(`.text${typeState.currTextId} .current`)?.getBoundingClientRect().top
    if (!currSpanRectTop) { return }

    const textDivs = document.querySelectorAll('.text')
    if (currSpanRectTop === typeState.currSpanLastCalculatedTop && textDivs.length === typeState.textsAmtAfterLastShift) { return }

    typeState.currSpanLastCalculatedTop = currSpanRectTop
    typeState.textsAmtAfterLastShift = textDivs.length

    const textGap = globalState.options.gapBetweenTexts.val
    const currTextRectTop = document.querySelector(`.text${typeState.currTextId}`).getBoundingClientRect().top
    const lineShift = currSpanRectTop - currTextRectTop

    const mainScrollRect = document.querySelector('.main-scroll').getBoundingClientRect()
    const mainScrollRectHeight = mainScrollRect.bottom - mainScrollRect.top
    const activeLinePositionOnTheScreen = globalState.options.activeLinePosition.val
    const activeTextTargetPositionTop = Math.round(mainScrollRectHeight / 100 * activeLinePositionOnTheScreen)

    let heightAccum = 0
    for (let i = 0; i < textDivs.length; i++) {
        if (textDivs[i].classList.contains('active')) { break }
        const textDivHeight = textDivs[i].getBoundingClientRect().bottom - textDivs[i].getBoundingClientRect().top + textGap
        heightAccum += textDivHeight
    }

    const startingPositionTop = activeTextTargetPositionTop - heightAccum
    let nextPositionTop = startingPositionTop - lineShift

    for (let i = 0; i < textDivs.length; i++) {
        textDivs[i].style.top = `${nextPositionTop}px`
        nextPositionTop += textDivs[i].getBoundingClientRect().height + textGap
    }
}


//// STATS FNs /////////////////////////////////////////////////////////////////

function recalcStats(textId = null) {
    if (textId) { textsStats[textId]['done'] = true }

    const timeThreshold = globalState.options.useNLastMinutesForStats.val * 60 * 1000
    let charsSum = 0
    let wordsSum = 0
    let errorsSum = 0
    let timeSum = 0

    for (let textId of Object.keys(textsStats).reverse()) {
        if (timeSum < timeThreshold) {
            if (textsStats[textId]['done']) {
                charsSum += textsStats[textId]['charsN']
                wordsSum += textsStats[textId]['wordsN']
                errorsSum += textsStats[textId]['errors']
                timeSum += textsStats[textId]['time']
            }
        } else {
            delete textsStats[textId]
        }
    }

    if (textId) { calculatedStats.charsDoneSum += textsStats[textId]['charsN'] }
    if (calculatedStats.charsDoneSum > 0) { calculatedStats.cpm = Math.round((charsSum / timeSum) * 60 * 1000) } else { calculatedStats.cpm = 0 }
    if (calculatedStats.charsDoneSum > 0) { calculatedStats.wpm = Math.round((wordsSum / timeSum) * 60 * 1000) } else { calculatedStats.wpm = 0 }
    if (calculatedStats.charsDoneSum > 0) { calculatedStats.acc = Math.round((1.0 - (errorsSum / charsSum)) * 100) } else { calculatedStats.acc = 0 }

    calculatedStats.fractionOfBookDone = Math.round((calculatedStats.charsDoneSum / calculatedStats.charsSum) * 10000) / 100
}


function prepStatsForSending(textId) {
    let statsArray = []
    let time_sum = 0
    let prev_time = texts[textId]['chars'][0]['time']
    let errors = 0
    let fisrtSkipped = false

    for (const charObj of Object.values(texts[textId]['chars'])) {
        if (charObj.time - prev_time < 5000) {
            time_sum += charObj.time - prev_time
            if (fisrtSkipped) {statsArray.push([charObj.ch, charObj.time-prev_time, charObj.err])}
            else {statsArray.push([charObj.ch, charObj.time, charObj.err]); fisrtSkipped=true}
        } else {
            if (fisrtSkipped) {statsArray.push([charObj.ch, 0, charObj.err])}
            else {statsArray.push([charObj.ch, charObj.time, charObj.err]); fisrtSkipped=true}
        }
        prev_time = charObj.time
        errors += charObj.err
    }

    textsStats[textId]['errors'] = errors
    textsStats[textId]['time'] = time_sum

    statsSendFetch(textId, errors, time_sum, statsArray)
}


function paintProgressBar() { const progressBar = document.querySelector('.progress-bar')
    if (document.querySelector('body').classList.contains('night')) {
        progressBar.style.backgroundImage = `linear-gradient(to right, #ffffff36 ${calculatedStats.fractionOfBookDone}%, #ffffff00 0%)`;
    } else if (document.querySelector('body').classList.contains('light')) {
        progressBar.style.backgroundImage = `linear-gradient(to right, #00000045 ${calculatedStats.fractionOfBookDone}%, #ffffff00 0%)`;
    }
}


//// INIT FNs ///////////////////////////////////////////////////////////////////

function initPrep(response) {
    typeState.lastTextId = response.last_text_id
    typeState.bookTitle = response.book_title

    prepTexts(response)
    // console.log('textsStats:', textsStats)
    // console.log('texts:', texts)

    prepTypeState()
    // console.log('typeState:', typeState)

    prepStats(response)
    // console.log('calculatedStats:', calculatedStats)

    recalcStats()
    paintProgressBar()
}


function prepTexts(result) {
    for (const [textId, textObj] of Object.entries(result['texts'])) {
        textsStats[textId] = {}
        textsStats[textId]['done'] = textObj['done']
        textsStats[textId]['charsN'] = textObj['chars_n']
        textsStats[textId]['wordsN'] = textObj['words_n']
        textsStats[textId]['errors'] = textObj['errors']
        textsStats[textId]['time'] = textObj['time']

        if (textObj?.text) {
            texts[textId] = {}
            texts[textId]['statsUploadShow'] = {cont: false, wait: false, good: false, bad: false}
            texts[textId]['chars'] = {}
            for (let i = 0; i < textObj['text'].length; i++) {
                texts[textId]['chars'][i] = {}
                texts[textId]['chars'][i]['ch'] = textObj['text'][i]
                texts[textId]['chars'][i]['err'] = 0
                texts[textId]['chars'][i]['res'] = 'neutral'
            }
        }
    }
}


function prepTypeState() {
    for (const [statsTextId, statsTextObj] of Object.entries(textsStats)) {
        if (statsTextObj.done === false) {
            typeState.currTextId = parseInt(statsTextId)
            break
        }
    }
    texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'current'
}


function prepStats(response) {
    calculatedStats.charsSum = response['chars_sum']
    calculatedStats.charsDoneSum = response['chars_done_sum']
}


//// FETCHES ///////////////////////////////////////////////////////////////////

function initGetTextsFetch(book_id) {
    const requestData = {
        method: 'GET',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' }
    }
    fetch(`/api/texts/${book_id}/initiate/`, requestData)
        .then( response => {
            if (response.status === 200) {
                response.json().then( result => {
                    // console.log('/api/texts/${book_id}/initiate/', result)
                    initPrep(result)
                })
            } else {
                pushNotification('Some error has occured...', 'error')
            }
        })
}


function getNextBatchOfTextsFetch(textId) {
    const requestData = {
        method: 'GET',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' }
    }
    fetch(`/api/texts/${textId}/advance/`, requestData)
        .then( response => {
            if (response.status === 200) {
                response.json().then( result => {
                    // console.log('/api/texts/${textId}/advance/', result)
                    prepTexts(result)
                })
            } else {
                pushNotification('Some error has occured...', 'error')
            }
        })
}


function statsSendFetch(textId, errors, time_sum, statsArray) {
    texts[textId]['statsUploadShow']['wait'] = true
    const argsObj = {
        errors: errors,
        time: time_sum,
    }
    const requestData = {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
            args: argsObj,
            stats_list: statsArray
        })
    }

    fetch(`/api/stats/${textId}/`, requestData)
        .then( response => {
            if (response.status === 200) {
                response.json().then( result => {
                    // console.log('/api/stats/${textId}/', result)
                    texts[textId]['statsUploadShow']['wait'] = false
                    texts[textId]['statsUploadShow']['good'] = true
                })
            } else {
                texts[textId]['statsUploadShow']['wait'] = false
                texts[textId]['statsUploadShow']['bad'] = true
                pushNotification('Some error has occured...', 'error')
            }
        })
}


////////////////////////////////////////////////////////////////////////////////

function pushNotification(txt, category) { // possible categories: 'error', 'warning', 'good' and 'info'
    modalsRef.value.addNotification(txt, category)
}


function showWaitStatusMessage() {
    typeState.pauseStatusMssg = true
}


function hideWaitStatusMessage() {
    typeState.pauseStatusMssg = false
}


onUpdated(() => {
    scrollActiveLineIntoView()
});


onMounted(() => {
    if (!route.params.book_id) {
        pushNotification('First select a book to type in the library section...', 'warning')
    } else {
        initGetTextsFetch(route.params.book_id)
    }

    document.addEventListener('keydown', keyPressEval);
})


onUnmounted(() => {
    document.removeEventListener('keydown', keyPressEval);
})

</script>







<style scoped>

.information {
    display: flex;
    gap: 10px;
    font-family: Helvetica,sans-serif;
    font-size: 27px;
    font-weight: 700;
    margin-bottom: 5px;
}
body.light .information { color: var(--grey7) }
body.night .information { color: var(--grey3) }

body.hide-stats-bar .information { display: none }

.information > div {
    padding: 0px var(--padding)
}
.filler {
    flex-grow: 1;
}

.stats {
    text-align: end;
}
.progress-bar {
    text-align: center;
    font-size: 27px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 5px;
}
body.light .progress-bar { color: var(--grey7) }
body.night .progress-bar { color: var(--grey3) }

body.hide-progress-bar .progress-bar { display: none }

.status-bar {
    font-family: Helvetica,sans-serif;
    font-size: 27px;
    font-weight: 700;
    text-align: center;
}
.status-bar .status-pause, .status-end {
    padding: 0px 10px;
    margin-bottom: 5px;
}
body.light .status-pause { color: var(--grey7) }
body.light .status-pause { background-color: #f5e367 }
body.night .status-pause { color: #f5e367 }
body.night .status-pause { background-color: transparent }

body.light .status-end { color: var(--grey7) }
body.light .status-end { background-color: #5ed55e }
body.night .status-end { color: #5ed55e }
body.night .status-end { background-color: transparent }

.main-scroll {
    font-family: monospace;
    font-weight: bold;
    user-select: none;
    font-size: 200%;
    cursor: text;
    white-space: pre-wrap;
    position: relative;
    overflow: hidden;
    height: -webkit-fill-available;
}
.main-scroll::-webkit-scrollbar {
    display: none;
}

.text {
    position: absolute;
    padding: 0px 15px;
    width: -webkit-fill-available;
}

.next-text {
    padding: 0px 8px;
}

body.light .wrong { background-color: red }
body.light.hide-error-history .inactive .wrong { background-color: var(--grey1) }
body.light .wrong { color: white }
body.light.hide-error-history .inactive .wrong { color: var(--grey7) }
body.light .inactive .right { color: #005800 }
body.light .right { color: #237a23 }
body.light.hide-error-history .right { color: var(--grey7) }
body.light .corrected { color: #af3636 }
body.light .inactive .corrected { color: #8f0000 }
body.light.hide-error-history .corrected { color: var(--grey7) }
body.light .current { background-color: var(--black) }
body.light .current { color: var(--white) }
body.light .neutral { background-color: var(--grey1) }
body.light .neutral { color: var(--grey7) }

body.night .wrong { background-color: #a12d2d }
body.night.hide-error-history .inactive .wrong { background-color: var(--grey8) }
body.night .wrong { color: white }
body.night.hide-error-history .inactive .wrong { color: var(--grey4) }
body.night .right { color: #639b63 }
body.night.hide-error-history .right { color: var(--grey4) }
body.night .corrected { color: #cb7e7e }
body.night.hide-error-history .corrected { color: var(--grey4) }
body.night .current { background-color: var(--white) }
body.night .current { color: var(--black) }
body.night .neutral { background-color: var(--grey8) }
body.night .neutral { color: var(--grey4) }

.inactive {
    filter: opacity(50%);
}





.loading-cont {
    position: absolute;
    bottom: 0;
    right: 0;
    margin: 0px 10px
}

.wait-img, .good-img, .bad-img {
    width: 25px;
    height: 25px;
}

body.light .wait-img, .good-img, .bad-img { filter: opacity(50%); }
body.night .wait-img, .good-img, .bad-img { filter: opacity(70%); }

</style>