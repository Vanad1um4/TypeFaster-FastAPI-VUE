<template>
    <div v-show="globalState.user.authenticated" class="main-container">
        
        <!-- BOOKS LIST -->
        <div class="book-list">
            <div
                v-for="book in books"
                v-bind:id="book.id"
                class="book-cont hoverable"
                v-on:click="bookClicked"
            >
                <div class="book-name">{{ book.title }}</div>
            </div>
            <div
                class="book-cont book-cont-add hoverable"
                v-on:click="addBookClicked"
            >
                <div class="book-plus"> + Add new book... </div>
            </div>
        </div>

        <div class="book-content">
            
            
            <!-- SELECTED BOOK DISPLAY -->
            <div v-show="divState.selectedBook.visible" class="selected-book">

                <div class="selected-book-header">
                    <div
                        v-show="!divState.selectedBook.renameVisible"
                        class="header"
                    >
                        {{ divState.selectedBook.bookName }}
                    </div>
                    <input
                        v-show="divState.selectedBook.renameVisible"
                        ref="renameBookInput"
                        v-bind:value="divState.selectedBook.bookName"
                        class="name"
                        v-on:keydown.enter="renameBook(renameBookInput)"
                    >
                    <button
                        v-show="divState.selectedBook.renameVisible"
                        class="btn"
                        v-on:click="renameBook(renameBookInput)"
                    >
                        Save
                    </button>
                    <button
                        class="btn"
                        v-on:click="divState.selectedBook.renameVisible = !divState.selectedBook.renameVisible"
                    >
                        {{ divState.selectedBook.renameVisible ? 'Cancel' : 'Rename' }}
                    </button>
                    <button
                        class="btn"
                        v-on:click="askUserBeforeBookDelete"
                    >
                        Delete
                    </button>
                </div>

                <div class="selected-book-info-cont">
                    <div
                        v-show="divState.selectedBook.nextTextToType !== -1"
                        class="selected-book-info-chars-n"
                    >
                        There're {{ divState.selectedBook.charsSum }} characters in this book.
                    </div>
                    <div
                        v-show="divState.selectedBook.nextTextToType === -1"
                        class="selected-book-info-finished-message"
                    >
                        Congratulations! You have finished this book!
                    </div>
                    <div
                        v-show="divState.selectedBook.nextTextToType === -1"
                        class="selected-book-info-finished-chars-n"
                    >
                        You have typed {{ divState.selectedBook.charsDoneSum }} chars.
                    </div>
                    <div
                        v-show="divState.selectedBook.nextTextToType !== -1 && divState.selectedBook.charsDoneSum !== 0"
                        class="selected-book-info-typed-chars"
                    >
                        You have already typed {{ divState.selectedBook.charsDoneSum }} chars. ({{ Math.round((divState.selectedBook.charsDoneSum / divState.selectedBook.charsSum) * 10000) / 100 }}%) <br>
                    </div>
                    <div
                        v-show="divState.selectedBook.charsDoneSum !== 0"
                        class="selected-book-info-typed-time"
                    >
                        It took you {{ divState.selectedBook.timePassed.h }} hours and {{ divState.selectedBook.timePassed.m }} minutes.
                    </div>
                    <div
                        v-show="divState.selectedBook.charsDoneSum === 0"
                        class="selected-book-info-not-started"
                    >
                        You have not yet started this book.
                    </div>
                    <div
                        v-show="divState.selectedBook.nextTextToType !== -1 && divState.selectedBook.charsDoneSum !== 0"
                        class="selected-book-info-to-type-chars-n"
                    >
                        Remains to be typed: {{ divState.selectedBook.charsSum - divState.selectedBook.charsDoneSum }} ({{ (10000.0 - Math.round((divState.selectedBook.charsDoneSum / divState.selectedBook.charsSum) * 10000)) / 100 }}%)
                    </div>
                    <div
                        v-show="divState.selectedBook.timeRemainesApprox.h !== null && (divState.selectedBook.timeRemainesApprox.h !== 0 || divState.selectedBook.timeRemainesApprox.m !== 0)"
                        class="selected-book-info-to-type-time"
                    >
                        It will take approximately {{ divState.selectedBook.timeRemainesApprox.h }} hours and {{ divState.selectedBook.timeRemainesApprox.m }} minutes for you to finish the book.
                    </div>
                    <!-- <button>Add more texts</button> -->
                </div>

                <div
                    v-show="divState?.selectedBook?.chart?.data?.labels?.length !== 0"
                    class="selected-book-stats"
                >
                    <Line :data="chartData" :options="chartOptions" />
                </div>

                <div class="selected-book-buttons">
                    <div
                        v-bind:class="['selected-book-btn', 'selected-book-start-btn', divState.selectedBook.nextTextToType === -1 ? 'deactivated' : '']"
                        v-on:click="typeBookBtnClicked"
                    >
                        {{ divState.selectedBook.nextTextToType === -1 ? 'Book finished' : divState.selectedBook.charsDoneSum === 0 ? 'Click here to begin typing' : 'Click here to continue typing' }}
                    </div>
                    <div
                        v-bind:class="['selected-book-btn', 'selected-book-add-text-btn']"
                        v-on:click="addMoreTextsToExistingBook"
                    >
                        Add more texts
                    </div>
                </div>

            </div>

            

            <!-- HEADER OF A NEW BOOK SECTION -->
            <div v-show="divState.newTitle.visibleCont" class="new-book">
                
                <div class="new-book-header">
                    Add new book to your library
                </div>

                <div class="new-book-title-field-div">
                    <input
                        v-model=divState.newTitle.value
                        class="new-book-title-input"
                        type="text"
                        placeholder="Enter title of the book here"
                    >
                </div>
                
            </div>
            
            

            <!-- ADD TEXTS FIELDS -->
            <div v-show="divState.newTexts.visibleCont" class="new-texts-fields">

                <div
                    v-for="tab in divState.newTexts.tabs"
                    v-bind:class="tab.active ? 'active' : 'inactive'"
                    class="new-texts-add-text-tab"
                    v-on:click="switchAddBookTab(tab)"
                >
                    {{ tab.text }}
                </div>
                
                <div
                    v-show="divState.newTexts.tabs.paste.active"
                    class="new-texts-add-text-selected-tab-paste"
                >
                    <textarea
                        v-model="divState.newTexts.textToAdd"
                        class="new-texts-text-input"
                        placeholder="Paste text here"
                        rows="10"
                    ></textarea>
                </div>

                <div
                    v-show="divState.newTexts.tabs.upload.active"
                    class="new-texts-add-text-selected-tab-upload"
                >
                    <!-- TODO: implement sometime later... -->
                    Coming soon... 
                </div>
                
            </div>



            <!-- ADD TEXTS BUTTONS -->
            <div v-show="divState.addTextButtons.visibleCont" class="new-texts-btns">
                <div 
                    v-bind:class="['new-texts-add-btn', divState.addTextButtons.ready == false ? 'deactivated' : '']"
                    v-on:click="clickedAddTexts()"
                >
                    Add
                </div>

                <div 
                    v-bind:class="['new-texts-cancel-btn', divState.addTextButtons.ready == false ? 'deactivated' : '']"
                    v-on:click="clickedCancelCreateBook()"
                >
                    Cancel
                </div>

            </div>



            <!-- LOADING INDICATOR -->
            <div v-show="divState.loadingGif.visible" class="loading">
                <img v-bind:src="loadingImageUrl" class="loading-gif">
            </div>

        </div>
    </div>

    <Modals ref="modalsRef" v-on:answer="gotAnswerFromUser" />

</template>





<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import loadingImageUrl from '@/pics/loading.gif'
import Modals from './modals.vue'
import router from '../router.js'
import { globalState } from '../state.js'
import { chartOptions as importedChartOptions, chartColors as importedChartColors } from '../const.js'

import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
import { Line } from 'vue-chartjs'

const modalsRef = ref()
const renameBookInput = ref()
const books = reactive([])

const divState = reactive({
    selectedBook: {
        id: 0,
        visible: false,
        bookName: '',
        renameVisible: false,
        nextTextToType: 0,
        chart: {
            data: {labels: [], cpm: [], wpm: [], acc: []},
            colors: {
                cpm: globalState.options.darkMode.val === false ? importedChartColors.light.cpm : importedChartColors.night.cpm, 
                wpm: globalState.options.darkMode.val === false ? importedChartColors.light.wpm : importedChartColors.night.wpm, 
                acc: globalState.options.darkMode.val === false ? importedChartColors.light.acc : importedChartColors.night.acc, 
            },
        },
        timePassed: {h: 0, m: 0},
        timeRemainesApprox: {h: null, m: null},
        charsSum: 0,
        charsDoneSum: 0,
    },
    loadingGif: {visible: false},
    newTitle: {visibleCont: false, value: ''},
    newTexts: {
        visibleCont: false,
        visibleOne: true,
        visibleMany: false,
        tabs: {
            paste: {text: 'Upload text', active: true},
            upload: {text: 'Upload a file', active: false},
        },
        textToAdd: ''
    },
    addTextButtons: {
        visibleCont: false,
        ready: true,
    },
})

const actionState = reactive({
    actionType: 'someAction',
    params: '',
})

const chartData = computed(() => ({
    labels: divState.selectedBook.chart.data.labels,
    datasets: [
        {
            label: 'CPM',
            borderColor: divState.selectedBook.chart.colors.cpm,
            backgroundColor: divState.selectedBook.chart.colors.cpm,
            data: divState.selectedBook.chart.data.cpm,
            yAxisID: 'y',
        },
        {
            label: 'WPM',
            borderColor: divState.selectedBook.chart.colors.wpm,
            backgroundColor: divState.selectedBook.chart.colors.wpm,
            data: divState.selectedBook.chart.data.wpm,
            yAxisID: 'y1',
        },
        {
            label: 'ACC',
            borderColor: divState.selectedBook.chart.colors.acc,
            backgroundColor: divState.selectedBook.chart.colors.acc,
            data: divState.selectedBook.chart.data.acc,
            yAxisID: 'y2',
        },
    ]
}))

const chartOptions = importedChartOptions

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
)


function bookClicked(event) {
    divState.selectedBook.renameVisible = false
    divState.newTitle.visibleCont = false
    divState.newTexts.visibleCont = false
    divState.addTextButtons.visibleCont = false

    const bookId = event.target.id
    const bookName = event.target.childNodes[0].textContent
    divState.selectedBook.id = bookId
    divState.selectedBook.bookName = bookName
    getTheBooksStatsFetch(bookId)
}


function addBookClicked() {
    divState.newTitle.visibleCont = true
    divState.newTexts.visibleCont = true
    divState.addTextButtons.visibleCont = true
    divState.selectedBook.visible = false
    divState.selectedBook.id = 0
}


function switchAddBookTab(tab) {
    if (!tab.active) {
        if (divState.newTexts.tabs.paste.active === true) {
            divState.newTexts.tabs.paste.active = false
            divState.newTexts.tabs.upload.active = true
        } else {
            divState.newTexts.tabs.paste.active = true
            divState.newTexts.tabs.upload.active = false
        }
    }
}


function typeBookBtnClicked() {
    if (divState.selectedBook.nextTextToType === -1) {
        pushNotification(`
            You've already completed this book. It is not designed to be retyped.
            If you really want to type it again, you can add it again with new title.`, 'warning', 10)

    } else {
        router.push({ name: 'type', params: { book_id: divState.selectedBook.id } })
    }
}


function validateBookTitle(title) {
    let trimmedTitle = title.trim()
    if (trimmedTitle.length > 0 && trimmedTitle.length < 256) {
        return trimmedTitle
    } else {
        pushNotification('Book title must be from 1 to 255 characters long', 'error')
        return false
    }
}


function validateBookText(text) {
    // TODO: maybe think of some a little bit more interesting checks sometime?
    let trimmedText = text.trim()
    if (trimmedText.length > 0) {
        return trimmedText
    } else {
        pushNotification("There should be some text, don't you think? :)", 'error')
        return false
    }
}


function addMoreTextsToExistingBook() {
    divState.newTexts.visibleCont = !divState.newTexts.visibleCont
    divState.addTextButtons.visibleCont = !divState.addTextButtons.visibleCont
}

function clickedAddTexts() {
    if (!divState.addTextButtons.ready) {
        pushNotification('Please give server a chance to respond :)', 'info')
        return
    }
    if (divState.selectedBook.id) {
        const text = validateBookText(divState.newTexts.textToAdd)
        if (!text) {
            pushNotification('Aborting...', 'info')
            return
        }
        addMoreTextToABookFetch(text)
    } else {
        const title = validateBookTitle(divState.newTitle.value)
        const text = validateBookText(divState.newTexts.textToAdd)
        if (!title || !text) {
            pushNotification('Aborting...', 'info')
            return
        }
        createBookFetch(title, text)
    }
}


function clickedCancelCreateBook() {
    if (!divState.addTextButtons.ready) {
        pushNotification('Please give server a chance to respond :)', 'info')
        return
    }
    divState.newTitle.visibleCont = false
    divState.newTexts.visibleCont = false
    divState.addTextButtons.visibleCont = false
}


function renameBook(newBookName) {
    const newName = validateBookTitle(newBookName.value)
    if (newName === false) {
        pushNotification('The name of the book must be from 1 to 255 characters long...', 'warning')
    } else {
        renameBookFetch(newName)
        divState.selectedBook.renameVisible = false
    }
}


function askUserBeforeBookDelete() {
    actionState['actionType'] = 'bookDelById'
    actionState['params'] = divState.selectedBook.id

    const question = 'Are you sure you want to delete this book? This operation is irreversible.'
    const yesAnswer = 'Yes, delete'
    const noAnswer = 'No, go back'
    modalsRef.value.showModalQuestion(question, yesAnswer, noAnswer)
}


function gotAnswerFromUser(answ) {
    if (answ === 'yes') {
        if (actionState.actionType === 'bookDelById') {
            deleteBookFetch(actionState.params)
        } else if (actionState.actionType === 'chapterDelById') {
            deleteChapterFetch(actionState.params)
        }
    // } else if (answ === 'no') {
    }
    actionState['actionType'] = ''
    actionState['params'] = ''
}


function pushNotification(txt, category, seconds) { // possible categories: 'error', 'warning', 'good' and 'info'
    modalsRef.value.addNotification(txt, category, seconds)
}


function parseResponseWithStats(res) {
    divState.selectedBook.nextTextToType = res?.first_untyped_text_id ?? -1
    divState.selectedBook.chart.data = res?.chart_stats ?? {labels: [], cpm: [], wpm: [], acc: []}
    divState.selectedBook.timePassed = res?.time_passed ?? {h: 0, m: 0}
    divState.selectedBook.timeRemainesApprox = res?.time_remaines_approx ?? {h: null, m: null}
    divState.selectedBook.charsSum = res?.chars_sum ?? 0
    divState.selectedBook.charsDoneSum = res?.chars_done_sum ?? 0
}


////////////////////////////////////////////////////////////// BOOK FETCHES ///

function addMoreTextToABookFetch(bookText) {
    const bookId = divState.selectedBook.id
    const requestData = {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
            text: bookText
        })
    }
    fetch(`/api/books/${bookId}/`, requestData)
        .then( response => {
            if (response.status === 204) {
                getBooksFetch()
                pushNotification('Book extended successfully', 'good')
            } else {
                pushNotification('Something went wrong', 'error')
            }
            divState.addTextButtons.ready = true
        })
}


function createBookFetch(bookTitle, bookText) {
    divState.addTextButtons.ready = false
    const requestData = {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: bookTitle,
            text: bookText
        })
    }
    fetch('/api/books/', requestData)
        .then( response => {
            if (response.status === 204) {
                getBooksFetch()
                pushNotification('Book created successfully', 'good')
            } else if (response.status === 409) {
                pushNotification('Book with this name already exists, try another one', 'warning')
            } else {
                pushNotification('Something went wrong', 'error')
            }
            divState.addTextButtons.ready = true
        })
}


function getTheBooksStatsFetch(bookId) {
    divState.loadingGif.visible = true
    const requestData = {
        method: 'GET',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' }
    }
    fetch(`/api/books/${bookId}/`, requestData)
        .then( response => {
            if (response.status === 200) {
                response.json().then( result => {
                    // console.log(result)
                    parseResponseWithStats(result)
                    divState.loadingGif.visible = false
                    divState.selectedBook.visible = true
                })
            } else {
                divState.loadingGif.visible = false
            }
        })
}


function getBooksFetch() {
    divState.newTitle.visibleCont = false
    divState.newTexts.visibleCont = false
    divState.selectedBook.visible = false
    divState.addTextButtons.visibleCont = false
    books.length = 0
    const requestData = {
        method: 'GET',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' }
    }
    fetch('/api/books/', requestData)
        .then( response => {
            if (response.status === 200) {
                response.json().then( result => {
                    // console.log(result)
                    for (const book of result) {
                        books.push(book)
                    }
                })
            }
        })
}


function renameBookFetch(newBookName) {
    const requestData = {
        method: 'PUT',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: newBookName
        })
    }
    fetch(`/api/books/${divState.selectedBook.id}/`, requestData)
        .then( response => {
            if (response.status === 204) {
                divState.selectedBook.bookName = newBookName
                getBooksFetch()
                pushNotification('Book renamed successfully', 'good')
            } else {
                pushNotification('Something went wrong', 'error')
            }
        })
}


function deleteBookFetch(bookId) {
    const requestData = {
        method: 'DELETE',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    }
    fetch(`/api/books/${bookId}/`, requestData)
        .then( response => {
            if (response.status === 204) {
                getBooksFetch()
                pushNotification('Book deleted successfully', 'good')
            } else {
                pushNotification('Something went wrong', 'error')
            }
        })
}


onMounted(() => {
    getBooksFetch()
})

watch(() => globalState.options.darkMode.val, (darkMode) => {
    if (darkMode === false) {
        divState.selectedBook.chart.colors.cpm = importedChartColors.light.cpm
        divState.selectedBook.chart.colors.wpm = importedChartColors.light.wpm
        divState.selectedBook.chart.colors.acc = importedChartColors.light.acc
    } else if (darkMode === true) {
        divState.selectedBook.chart.colors.cpm = importedChartColors.night.cpm
        divState.selectedBook.chart.colors.wpm = importedChartColors.night.wpm
        divState.selectedBook.chart.colors.acc = importedChartColors.night.acc
    }
})
</script>




<style scoped>

h2 {
    margin: 7px;
    text-align: center;
}

.main-container {
    display: flex;
    height: 100%;
}
.main-container > .book-list {
    width: 34%;

    display: flex;
    flex-direction: column;
    gap: var(--gap-5px);
}

.main-container > .book-list > .book-cont {
    border-radius: var(--main-border-radius-3px);
    padding: 5px 5px;
    height: 40px;
    position: relative;
    bottom: 0px;
    transition: 0.1s;

    display: flex;
    align-items: center;
}
body.light .main-container > .book-list > .book-cont { background-color: var(--grey2) }
body.night .main-container > .book-list > .book-cont { background-color: var(--grey7) }

body.light .main-container > .book-list > .book-cont { color: var(--grey7); }
body.night .main-container > .book-list > .book-cont { color: var(--grey2); }

.main-container > .book-list > .book-cont > .book-name, .book-plus {
    font-weight: 700;
    font-size: 20px;
    pointer-events: none;

    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.main-container > .book-list > .book-cont > .book-plus {
    text-align: center;
    width: 100%;
    font-size: 20px;
}

.main-container > .book-list > .hoverable:hover {
    cursor: pointer;
    left: 5px;
}
body.light .main-container > .book-list > .hoverable:hover {
    color: var(--grey8);
    background-color: var(--grey3);
}
body.night .main-container > .book-list > .hoverable:hover {
    color: var(--white);
    background-color: var(--grey6);
}

.main-container > .book-content {
    width: 66%;

    margin-left: 10px;

    display: flex;
    flex-direction: column;
    gap: var(--gap-5px);
}





.selected-book {
    display: flex;
    flex-direction: column;
    gap: var(--gap-5px);
}


.selected-book-header {
    border-radius: var(--main-border-radius-3px);
    padding: 5px 5px;
}
body.light .selected-book-header { background-color: var(--grey2) }
body.night .selected-book-header { background-color: var(--grey7) }

.selected-book-header {
    display: flex;
    gap: var(--gap-5px);
    align-items: center;
}
.selected-book-header > * {
    font-weight: 700;
    font-size: 20px;
}
.selected-book-header > .header {
    flex-grow: 1;
    overflow: hidden;
}
.selected-book-header > .name {
    flex-grow: 1;
}
.selected-book-header > .btn {
    white-space: nowrap;
    font-weight: normal;
    font-size: 16px;
}





.selected-book-info-cont {
    display: flex;
    flex-direction: column;
    gap: 9px;

    border-radius: var(--main-border-radius-3px);
    padding: 5px 5px;
    font-size: 18px;
}

body.light .selected-book-info-cont { background-color: var(--grey2) }
body.night .selected-book-info-cont { background-color: var(--grey7) }







.selected-book-stats {
    border-radius: var(--main-border-radius-3px);
    padding: 5px 5px;
    /* background-color: red; */
    height: 250px;
}
body.light .selected-book-stats { background-color: var(--grey2) }
body.night .selected-book-stats { background-color: var(--grey7) }




.selected-book-buttons {
    display: flex;
    gap: var(--gap-5px);
}

.selected-book-btn {
    border-radius: var(--main-border-radius-3px);
    padding: 8px 5px;
    font-weight: 700;
    font-size: 20px;
    text-align: center;
    cursor: pointer;
}
.selected-book-btn.deactivated {
    cursor: not-allowed;
}
body.light .selected-book-btn { background-color: var(--grey2) }
body.night .selected-book-btn { background-color: var(--grey7) }

body.light .selected-book-btn.deactivated { color: var(--grey3) }
body.night .selected-book-btn.deactivated { color: var(--grey6) }

.selected-book-start-btn {
    flex-grow: 3;
}

.selected-book-add-text-btn {
    flex-grow: 1;
}





/* ADD TEXT HEADER */

.new-book {
    display: grid;
    grid-template-columns: 100%;
    gap: var(--gap-5px);

    font-weight: 700;
    font-size: 20px;
}
.new-book > * {
    border-radius: var(--main-border-radius-3px);
    padding: 5px 5px;
}
body.light .new-book > * { background-color: var(--grey2) }
body.night .new-book > * { background-color: var(--grey7) }

.new-book-header,
.new-book-title-field-div {
    grid-column: span 2;
}
.new-book-title-input {
    width: -webkit-fill-available;
    font-size: 20px;
    font-weight: 700;
}





/* ADD TEXT FIELDS */

.new-texts-fields {
    display: grid;
    grid-template-columns: 50% 50%;
    gap: var(--gap-5px);

    font-weight: 700;
    font-size: 20px;
}
.new-texts-fields > * {
    border-radius: var(--main-border-radius-3px);
    padding: 5px 5px;
}
body.light .new-texts-fields > * { background-color: var(--grey2) }
body.night .new-texts-fields > * { background-color: var(--grey7) }

.new-texts-add-text-selected-tab-paste,
.new-texts-add-text-selected-tab-upload {
    grid-column: span 2;
}

body.light .new-texts-add-text-tab.inactive { color: var(--grey4) }
body.night .new-texts-add-text-tab.inactive { color: var(--grey5) }

.new-texts-add-text-tab {
    text-align: center;
    cursor: pointer;
    user-select: none;
}

.new-texts-text-input {
    width: -webkit-fill-available;
    word-wrap: normal;
}









/* ADD TEXT BUTTONS */

.new-texts-btns {
    display: grid;
    grid-template-columns: 50% 50%;
    gap: var(--gap-5px);

    font-weight: 700;
    font-size: 20px;
}
.new-texts-btns > * {
    border-radius: var(--main-border-radius-3px);
    padding: 5px 5px;
}
.new-texts-add-btn,
.new-texts-cancel-btn {
    text-align: center;
    cursor: pointer;
    user-select: none;
}
.new-texts-add-btn.deactivated,
.new-texts-cancel-btn.deactivated {
    cursor: not-allowed;
}
body.light .new-texts-add-btn { background-color: #68c968 }
body.night .new-texts-add-btn { background-color: #076c07 }

body.light .new-texts-add-btn.deactivated { color: var(--grey3) }
body.light .new-texts-add-btn.deactivated { background-color: var(--grey2) }
body.night .new-texts-add-btn.deactivated { color: var(--grey6) }
body.night .new-texts-add-btn.deactivated { background-color: var(--grey7) }

body.light .new-texts-cancel-btn { background-color: #e77b7b }
body.night .new-texts-cancel-btn { background-color: #891616 }

body.light .new-texts-cancel-btn.deactivated { color: var(--grey3) }
body.light .new-texts-cancel-btn.deactivated { background-color: var(--grey2) }
body.night .new-texts-cancel-btn.deactivated { color: var(--grey6) }
body.night .new-texts-cancel-btn.deactivated { background-color: var(--grey7) }










.main-container > .book-content > .loading {
    border-radius: var(--main-border-radius-3px);
    padding: 5px 5px;
    text-align: center;
}
.main-container > .book-content > .loading > .loading-gif {
    width: 25px;
    height: 25px;
}
body.light .book-content .loading { background-color: var(--grey2) }
body.night .book-content .loading { background-color: var(--grey7) }




/* TODO: delete chapter stuff */
/* .chapter-add-cont {
    display: flex;
    flex-wrap: wrap;
    gap: var(--gap-5px);
    user-select: none;
}

.chapter-add-btn {
    flex-basis: 45%;
    flex-grow: 1;
    border-radius: var(--main-border-radius-3px);
    padding: 5px 5px;
    cursor: pointer;
}

body.light .chapter-add-btn { background-color: var(--grey2) }
body.night .chapter-add-btn { background-color: var(--grey7) }

.chapter-add-hide {
    flex-grow: 1;
    border-radius: var(--main-border-radius-3px);
    padding: 5px 5px;
}

body.light .chapter-add-hide { background-color: var(--grey2) }
body.night .chapter-add-hide { background-color: var(--grey7) }

.chapter-add-one-header {
    font-weight: 700;
    font-size: 20px;
    grid-column: span 2;
    text-align: center;
}

.chapter-add-one-cont, .chapter-add-many {
    display: grid;
    gap: var(--gap-5px) 10px;
    grid-template-columns: max-content auto;
}

.chapter-add-one-chapter-tag, .chapter-add-one-text-tag {}
.chapter-add-one-save-btn {
    grid-column: span 2;
    font-weight: 700;
    font-size: 20px;
} */

</style>