<template>

    <div
        v-if="route.params.chapter_id"
        class="information"
    >
        <div class="chapter-name">Chapter: {{ chapter.name }}</div>
        <div class="placeholder"></div>
        <div class="stats">CPM:&nbsp;{{ chapter.cpm }} <span>&nbsp;&nbsp;</span> WPM:&nbsp;{{ chapter.wpm }} <span>&nbsp;&nbsp;</span> Accuracy:&nbsp;{{ chapter.acc }}%</div>
    </div>

    <!-- :style="{ backgroundImage: `linear-gradient(to right, #585858 ${0}%, #ffffff00 0%)` }" -->
    <div
        v-if="route.params.chapter_id"
        class="progress-bar"
    >
        completed: {{ Math.round(chapter.done * 100) }}%
    </div>

    <div
        v-if="route.params.chapter_id"
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
        v-if="route.params.chapter_id"
        class="main-scroll"
    >
        <div v-for="text in texts" v-bind:class="['text' + text.id, text.id == typeState.currTextId ? 'active' : 'inactive']">
            <span v-for="ch in text.chars" v-bind:class="ch.res"> {{ ch.ch }} </span>
            <span v-bind:class="['next-text', text.end === true ? 'current' : '']">⏎</span>
        </div>
    </div>

    <Modals ref="modalsRef"/>
</template>





<script setup>
import { useRoute } from 'vue-router'
import { ref, reactive, computed, onMounted, onUnmounted, onUpdated } from 'vue';
import Modals from './modals.vue'
import router from '../router.js'

const route = useRoute()
const modalsRef = ref()
let timeoutID

const keysIgnore = [
    'ArrowRight',
    'ArrowDown',
    'ArrowLeft',
    'CapsLock',
    'ArrowUp',
    'Control',
    'Escape',
    'Shift',
    'Tab',
    'Alt',
]

let chapter = reactive({
    'id': 0,
    'name': '',
    'done': 0,
    'charsTotal': 0,
    'chars': 0,
    'words': 0,
    'errors': 0,
    'time': 0,
    'cpm': 0,
    'wpm': 0,
    'acc': 0,
    'lastTextId': 999999,
})

let typeState = reactive({
    'currTextId': 0,
    'currCharId': 0,
    'globalEnd': false,
    'pauseStatusMssg': false,
    'theEndStatusMssg': false,
})

let texts = reactive({
    0: {
        id: 0,
        text: '',
        done: false,
        end: false,
        words_n: 0,
        chars_n: 0,
        chars: {
            0: {
                id: 0,
                ch: '',
                time: 0,
                err: 0,
                res: 'neutral',
            }
        },
    }
})

function pushNotification(txt, category) { // possible categories: 'error', 'warning', 'good' and 'info'
    modalsRef.value.addNotification(txt, category)
}

function scrollActiveTextToCenter() {
    const currTextDiv = document.querySelector(`.text${typeState.currTextId}`);
    const mainScrollDiv = currTextDiv.parentElement;
    const currTextRect = currTextDiv.getBoundingClientRect();
    const mainScrollRect = mainScrollDiv.getBoundingClientRect();
    const scrollValue = currTextRect.top - mainScrollRect.top - (mainScrollRect.height - currTextRect.height) / 2;
    mainScrollDiv.scrollBy({ top: scrollValue, behavior: 'smooth' });
}


function keyPressEval(event) {
    if (!keysIgnore.includes(event.key)) {
        if (typeState.globalEnd === false) {
            if (event.key === 'Backspace') { propagateBackward() }
            else {
                if (event.key === ' ') { event.preventDefault() }
                // console.log(event.key)
                // console.log(typeState.globalEnd, event.key)
                // console.log(typeof(typeState.globalEnd), typeof(event.key))
                propagateForward(event.key)
            }
        }
        else if (typeState.globalEnd === true && event.key === 'Backspace') { router.push({ name: 'library' }) }




        // if (event.key === 'Backspace') { propagateBackward() }
        // else {
        //     if (event.key === ' ') { event.preventDefault() }
        //     // console.log(event.key)
        //     console.log(typeState.globalEnd, event.key)
        //     console.log(typeof(typeState.globalEnd), typeof(event.key))
        //     if (typeState.globalEnd === false) {propagateForward(event.key)}
        //     else if (typeState.globalEnd === true && event.key === 'Backspace') {
        //         router.push({ name: 'library' })
        //     }

        // }
    }
}

function propagateBackward() {
    if (typeState.currCharId > 0 && texts[typeState.currTextId]['end'] === false) {
        texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'neutral'
        typeState.currCharId--
        texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'current'
    }
}

function showWaitStatusMessage() {
    typeState.pauseStatusMssg = true

}
function hideWaitStatusMessage() {
    typeState.pauseStatusMssg = false
}

function propagateForward(key) {
    hideWaitStatusMessage()
    clearTimeout(timeoutID)
    timeoutID = setTimeout(showWaitStatusMessage, 5000)
    if (texts[typeState.currTextId]['end'] === false) {

        if (texts[typeState.currTextId]['chars'][typeState.currCharId]['ch'] === key) {
            // console.log('yep')
            if (texts[typeState.currTextId]['chars'][typeState.currCharId]['err'] === 0) {
                texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'right'
            } else {
                texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'corrected'
            }
        } else {
            // console.log('nope')
            texts[typeState.currTextId]['chars'][typeState.currCharId]['err']++
            texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'wrong'
        }

        texts[typeState.currTextId]['chars'][typeState.currCharId]['time'] = Date.now()

        if (typeState.currCharId === texts[typeState.currTextId]['text'].length-1) {
            texts[typeState.currTextId]['end'] = true
        } else {
            typeState.currCharId++
            texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'current'
        }
        // scrollActiveTextToCenter()

    // console.log(typeState.currTextId, chapter.lastTextId)
    } else if (texts[typeState.currTextId]['end'] === true) {
        // console.log(typeState.currTextId, chapter.lastTextId)

        if (key === 'Enter') {
            postStatsPrepAndSend(typeState.currTextId)
            deleteOldAndFetchNewTexts()
            recalcStats()
            texts[typeState.currTextId]['end'] = false

            // console.log(typeState.currTextId, chapter.lastTextId)
            // console.log(typeof(typeState.currTextId), typeof(chapter.lastTextId))
            // const lastTextId = Object.keys(texts)[Object.keys(texts).length - 1]
            if (typeState.currTextId == chapter.lastTextId) {
                // console.log(typeState.currTextId, chapter.lastTextId)
                // console.log('lool')
                typeState.globalEnd = true
                typeState.theEndStatusMssg = true
                clearTimeout(timeoutID)
            } else if (typeState.currTextId < chapter.lastTextId) {
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

function deleteOldAndFetchNewTexts() {
    for (const id in texts) {
        if (document.querySelector(`.text${id}`).getBoundingClientRect().top < 0) {
            delete texts[id]
        } else {
            break
        }
    }
    // const scrollDiv = document.querySelector('.main-scroll')
    const scrollRectHeight = document.querySelector('.main-scroll').getBoundingClientRect().height
    // console.log(scrollRectHeight)
    const activeTextbottom = document.querySelector('.main-scroll .active').getBoundingClientRect().bottom
    // const lastTextRect = document.querySelector('.main-scroll').lastChild.querySelector('*').getBoundingClientRect()
    const lastTextBottom = document.querySelector('.main-scroll :last-child *').getBoundingClientRect().bottom
    // console.log(lastTextBottom, activeTextbottom)
    // console.log(lastTextBottom - activeTextbottom)
    if (lastTextBottom - activeTextbottom < scrollRectHeight) {
        const lastTextId = Object.keys(texts)[Object.keys(texts).length - 1]
        // console.log(lastTextId)
        if (lastTextId < chapter.lastTextId) {
            // console.log(lastTextId, chapter.lastTextId)
            getNextBatchOfTextsFetch(chapter.id, lastTextId)
        }
    }
}

function recalcStats() {
    chapter.chars += texts[typeState.currTextId]['chars_n']
    chapter.words += texts[typeState.currTextId]['words_n']
    chapter.errors += texts[typeState.currTextId]['errors']
    chapter.time += texts[typeState.currTextId]['time']
    chapter.done = chapter.chars / chapter.charsTotal
    chapter.cpm = Math.round(chapter.chars / chapter.time * 60 * 1000)
    chapter.wpm = Math.round(chapter.words / chapter.time * 60 * 1000)
    chapter.acc = Math.round((1.0 - (chapter.errors / chapter.chars)) * 100)
    paintProgressBar()
}

function paintProgressBar() {
    const progressBar = document.querySelector('.progress-bar')
    // console.log(document.querySelector('body').classList.contains('night'))
    if (document.querySelector('body').classList.contains('night')) {
        progressBar.style.backgroundImage = `linear-gradient(to right, #ffffff36 ${chapter.done*100}%, #ffffff00 0%)`;
    } else if (document.querySelector('body').classList.contains('light')) {
        progressBar.style.backgroundImage = `linear-gradient(to right, #00000045 ${chapter.done*100}%, #ffffff00 0%)`;
    }

}

function prepNextBatch(result) {
    for (const [id, text] of Object.entries(result.texts)) {
        // console.log(text)
        texts[id] = {}
        texts[id]['id'] = id
        texts[id]['text'] = text.text
        texts[id]['done'] = text.done
        texts[id]['end'] = false
        texts[id]['words_n'] = text.words
        texts[id]['chars_n'] = text.chars
        texts[id]['chars'] = {}

        for (let i = 0; i < text.text.length; i++) {
            texts[id]['chars'][i] = {}
            texts[id]['chars'][i]['id'] = i
            texts[id]['chars'][i]['ch'] = text.text[i]
            texts[id]['chars'][i]['err'] = 0
            texts[id]['chars'][i]['res'] = 'neutral'
        }
    }
}

function mainPrep(result) {
    chapter.id = result.chapter['chapterId']
    chapter.name = result.chapter['chapterName']
    chapter.done = result.chapter['done']
    // console.log()
    chapter.charsTotal = result.chapter['charsTotal']
    chapter.chars = result.chapter['chars']
    chapter.words = result.chapter['words']
    chapter.errors = result.chapter['errors']
    chapter.time = result.chapter['time']
    chapter.lastTextId = result.chapter['lastTextId']
    // console.log(chapter)

    if (chapter.chars > 0) {
        chapter.cpm = Math.round(chapter.chars / chapter.time * 60 * 1000)
        chapter.wpm = Math.round(chapter.words / chapter.time * 60 * 1000)
        chapter.acc = Math.round((1.0 - (chapter.errors / chapter.chars)) * 100)
    }

    delete texts[0]

    prepNextBatch(result)

    // console.log(texts)

    for (const [key, value] of Object.entries(texts)) {
        // console.log(key, value)
        if (value.done === false) {
            typeState.currTextId = parseInt(key)
            // texts[key].currCharId = 0
            break
        }
    }
    // console.log(typeState)
    texts[typeState.currTextId]['chars'][typeState.currCharId]['res'] = 'current'

    // recalcStats()
    paintProgressBar()
}

function getNextBatchOfTextsFetch(chapter_id, text_id) {
    const requestData = {
        method: 'GET',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }
    }
    fetch(`/api/texts/${chapter_id}/${text_id}/`, requestData)
        .then( response => {
            if (response.status === 200) {
                response.json().then( result => {
                    // console.log(result)
                    prepNextBatch(result)
                })
            } else {
                pushNotification('Some error has occured...', 'error')
            }
        })
}

function initGetTextsFetch(chapter_id) {
    const requestData = {
        method: 'GET',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }
    }
    fetch(`/api/texts/${chapter_id}/`, requestData)
        .then( response => {
            if (response.status === 200) {
                response.json().then( result => {
                    // console.log(result)
                    mainPrep(result)
                })
            } else {
                pushNotification('Some error has occured...', 'error')
            }
        })
}

function postStatsPrepAndSend(text_id) {
    // console.log(texts[text_id])
    let statsArray = []
    let time_sum = 0
    let prev_time = texts[text_id]['chars'][0]['time']
    let errors = 0
    let fisrtSkipped = false
    for (const value of Object.values(texts[text_id]['chars'])) {
        // console.log(value)
        if (value.time - prev_time < 5000) {
            time_sum += value.time - prev_time
            // console.log(value.time - prev_time)
            if (fisrtSkipped) {statsArray.push([value.ch, value.time-prev_time, value.err])}
            else {statsArray.push([value.ch, value.time, value.err]); fisrtSkipped=true}
        } else {
            if (fisrtSkipped) {statsArray.push([value.ch, 0, value.err])}
            else {statsArray.push([value.ch, value.time, value.err]); fisrtSkipped=true}
        }
        prev_time = value.time
        errors += value.err
    }

    texts[text_id]['time'] = time_sum
    texts[text_id]['errors'] = errors

    const argsObj = {
        errors: errors,
        time: time_sum,
    }
    // console.log(argsObj)
    const requestData = {
        method: 'POST',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
            args: argsObj,
            stats: statsArray
        })
    }
    fetch(`/api/stats/${text_id}/`, requestData)
        .then( response => {
            if (response.status === 200) {
                response.json().then( result => {
                    // console.log(result)
                    // pushNotification('Success!', 'error')
                })
            } else {
                pushNotification('Some error has occured...', 'error')
            }
        })
}

onUpdated(() => {
    // console.log('v-for has finished rendering');
    scrollActiveTextToCenter()
    // testtesttesttest()
});


onMounted(() => {
    // console.log(route.params.chapter_id)
    if (!route.params.chapter_id) {
        pushNotification('First select a chapter to type in the library section...', 'warning')
    } else {
        initGetTextsFetch(route.params.chapter_id)
    }
    document.addEventListener('keydown', keyPressEval);
    // document.addEventListener('keyup', keyUpHandle);
})

// function testtesttesttest() {
//     const activeDiv = document.querySelector(`.main-scroll .active`)
//     const activeTop = activeDiv.getBoundingClientRect().top
//     // console.log(activeTop)
//     for (const [id, text] of Object.entries(texts)) {
//         // console.log(document.querySelector(`.main-scroll .active`).getBoundingClientRect())
//         // console.log(document.querySelector(`.text${id}`).getBoundingClientRect())
//         const div = document.querySelector(`.text${id}`)
//         const divTop = div.getBoundingClientRect().top
//         console.log(div, divTop)
//     }
// }


onUnmounted(() => {
    document.removeEventListener('keydown', keyPressEval);
    // document.removeEventListener('keyup', keyUpHandle);
})

</script>





<style>
.content {
}


</style>


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

.chapter-name {
}
/* body.light .chapter-name { color: var(--grey7) } */
/* body.night .chapter-name { color: var(--grey3) } */
.placeholder {
    flex-grow: 1;
}

.stats {
    text-align: end;
}

.progress-bar {
    /* flex-grow: 1; */
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
    flex-grow: 1;

    font-family: monospace;
    font-weight: bold;
    user-select: none;
    font-size: 200%;
    padding: 7px 15px;
    cursor: text;

    overflow: auto;
    display: flex;
    gap: 14px;
    flex-direction: column;
    /* height: 98%; */
}
.main-scroll::-webkit-scrollbar {
    display: none;
}
.next-text {
    padding: 0px 8px;
}




.active {
}
/* body.light .active .wrong { background-color: red }
body.light .active .wrong { color: white }
body.light .active .right { color: #9bb59b }
body.light .active .corrected { color: #cbb5b5 }
body.light .active .current { background-color: var(--black) }
body.light .active .current { color: var(--white) }
body.light .active .neutral { background-color: var(--grey1) }
body.light .active .neutral { color: var(--grey7) }

body.night .active .wrong { background-color: #a12d2d }
body.night .active .wrong { color: white }
body.night .active .right { color: #506a50 }
body.night .active .corrected { color: #6e5656 }
body.night .active .current { background-color: var(--white) }
body.night .active .current { color: var(--black) }
body.night .active .neutral { background-color: var(--grey8) }
body.night .active .neutral { color: var(--grey4) } */

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



</style>