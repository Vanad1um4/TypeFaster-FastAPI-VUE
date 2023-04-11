<template>
    <div v-show="globalState.user.authenticated" class="container">
        <div class="book-list">
            <div
                v-for="book in books"
                v-bind:id="book.id"
                class="book-cont hoverable"
                v-on:click="bookClicked"
            >
                <div class="book-name">{{ book.name }}</div>
            </div>
            <div
                class="book-cont book-cont-add hoverable"
                v-on:click="addBookClicked"
            >
                <div class="book-plus"> + create book... </div>
            </div>
        </div>

        <div class="text-list">
            <div v-show="divState.newBook.visible" class="new-book">
                <div class="cont">
                    <div class="header">
                        Enter title of the book:
                    </div>
                    <input
                        ref="createBookInput"
                        class="name new-book-input"
                        type="text"
                        v-on:keydown.enter="createBook(createBookInput)"
                    >
                    <button
                        class="btn add new-book-btn-add"
                        v-on:click="createBook(createBookInput)"
                    >
                        Add
                    </button>
                    <button
                        class="btn cancel new-book-btn-cancel"
                        v-on:click="divState.newBook.visible = false"
                    >
                        Cancel
                    </button>
                </div>
            </div>

            <div v-show="divState.selectedBook.visible" class="book">
                <div class="cont">
                    <div class="header">{{ divState.selectedBook.bookName }}</div>
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
                        💾
                    </button>
                    <button
                        class="btn"
                        v-on:click="divState.selectedBook.renameVisible = !divState.selectedBook.renameVisible"
                    >
                        🏷️
                    </button>
                    <button
                        class="btn"
                        v-on:click="askUserBeforeBookDelete"
                    >
                        🚮
                    </button>
                </div>
            </div>

            <div v-show="divState.loadingGif.visible" class="loading">
                <img v-bind:src="loadingImageUrl" class="loading-gif">
            </div>

            <div v-show="divState.chaptersList.visible" class="texts texts-cont">
                <div
                    v-for="chapter in chapters"
                    class="chapter-cont"
                    v-on:click="chapterClicked(chapter)"
                >
                    <div
                        class="chapter-head-cont"
                    >
                        <!-- v-on:click.stop="chapter.chapter.show = !chapter.chapter.show" -->
                        <!-- v-on:mouseenter="chapter.delBtnShow = true"
                        v-on:mouseleave="chapter.delBtnShow = false" -->
                        <div
                            class="cell chapter-done-pic">
                            {{ chapter.done == 1 ? '✅' : chapter.done == 0 ? '❌' : `🟡` }}
                        </div>
                        <div
                            class="cell chapter-done-num">
                            {{ chapter.done == 1 ? '100%' : chapter.done == 0 ? '0%' : `${Math.round(chapter.done * 100)}%` }}
                        </div>
                        <div class="cell chapter-name">{{ chapter.ch_name }}</div>
                        <div class="cell chapter-cpm">{{ chapter.cpm == 0 ? '- CPM' : chapter.cpm + ' CPM' }}</div>
                        <div class="cell chapter-wpm">{{ chapter.wpm == 0 ? '- WPM' : chapter.wpm + ' WPM' }}</div>
                        <div class="cell chapter-acc">{{ chapter.acc == 0 ? '- % acc.' : chapter.acc + '% acc.' }}</div>
                        <button
                            class="chapter-del"
                            v-on:click.stop="askUserBeforeChapterDelete(chapter)"
                        >
                            🚮
                        </button>
                    </div>

                </div>
            </div>

            <div v-show="divState.chaptersList.visible" class="chapter-add-cont">
                <div class="chapter-add-btn" v-on:click.stop="clickedAddTextOne">+ add one chapter</div>
                <div class="chapter-add-btn" v-on:click.stop="clickedAddTextMany">+ add two or more chapters</div>
                <div
                    v-show="divState.addText.visibleMain"
                    class="chapter-add-hide"
                >

                    <div
                        v-show="divState.addText.visibleOne"
                        class="chapter-add-one-cont"
                    >
                        <div class="chapter-add-one-header">Add one chapter</div>
                        <div class="chapter-add-one-chapter-tag">Chapter name:</div>
                        <input
                            ref="createTextChapter"
                            class="chapter-add-one-chapter-input"
                            type="text"
                            placeholder="Paste chapter name here"
                        >
                        <div class="chapter-add-one-text-tag">Text:</div>
                        <textarea
                            ref="createTextStr"
                            class="chapter-add-one-text-input"
                            placeholder="Paste text here"
                            rows="10"
                        ></textarea>
                        <button
                            class="chapter-add-one-save-btn"
                            v-on:click.stop="clickedSaveTextOne"
                        >
                            Save
                        </button>
                    </div>
                    <div
                        v-show="divState.addText.visibleMany"
                        class="chapter-add-many"
                    >
                        <div class="chapter-add-many-header">Add text to be automatically split into specified number of chapters<br>Yet to be implemented...</div>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <!-- <button v-on:click="testFunc">CLICK</button> -->

    <Modals ref="modalsRef" v-on:answer="gotAnswerFromUser" />

    <!-- <button v-on:click="pushNotification('Some big and very clever message to our best user')">CLICK</button> -->

</template>





<script setup>

import { ref, reactive, onMounted } from 'vue';
import loadingImageUrl from '@/pics/loading.gif'
import Modals from './modals.vue'
import router from '../router.js'
import { globalState } from '../state.js'

const modalsRef = ref()
const books = reactive([])
const chapters = reactive([])
const renameBookInput = ref()
const createBookInput = ref()
const createTextChapter = ref()
const createTextStr = ref()

const divState = reactive({
    newBook: {visible: false},
    selectedBook: {visible: false, id: 0, bookName: '', renameVisible: false},
    chaptersList: {visible: false},
    loadingGif: {visible: false},
    addText: {visibleMain: false, visibleOne: true, visibleMany: false},
})

const actionState = reactive({
    actionType: 'someAction',
    params: '',
})

// const someTestVal = ref(true)
// function testFunc() {
//     someTestVal.value = !someTestVal.value
// }

function bookClicked(event) {
    divState.newBook.visible = false
    divState.selectedBook.renameVisible = false
    divState.addText.visibleMain = false
    divState.chaptersList.visible = false

    const bookId = event.target.id
    const bookName = event.target.childNodes[0].textContent
    // console.log(bookId, bookName)
    divState.selectedBook.id = bookId
    divState.selectedBook.bookName = bookName
    getChaptersFetch(bookId)
}


function addBookClicked() {
    divState.newBook.visible = true
    divState.selectedBook.visible = false
    divState.chaptersList.visible = false
}

function chapterClicked(chapter) {
    if (chapter.done == 1) {
        pushNotification(`
            You've already completed this chapter. It is not designed to be retyped.
            If you really want to type it again, you can delete it and add once more.
        `, 'warning', 10)
    } else {
        // console.log(chapter.ch_id)
        router.push({ name: 'type', params: { chapter_id: chapter.ch_id } })
    }
}


function validateNameString(name) {
    let trimmedName = name.trim()
    if (trimmedName.length < 256 && trimmedName.length > 0) {
        return trimmedName
    } else {
        return false
    }
}


function createBook(newBookName) {
    const newName = validateNameString(newBookName.value)
    if (newName === false) {
        pushNotification('The name of the book must be from 1 to 255 characters long...', 'warning')
    } else {
        createBookFetch(newName)
    }
}


function renameBook(newBookName) {
    const newName = validateNameString(newBookName.value)
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
    // console.log(actionState)
    // console.log(typeof(actionState))

    const question = 'Are you sure you want to delete this book? This operation is irreversible.'
    const yesAnswer = 'Yes, delete'
    const noAnswer = 'No, go back'
    modalsRef.value.showModalQuestion(question, yesAnswer, noAnswer)
}

function askUserBeforeChapterDelete(obj) {
    // console.log(obj)
    actionState['actionType'] = 'chapterDelById'
    actionState['params'] = obj.ch_id
    // console.log(actionState)

    const question = 'Are you sure you want to delete this chapter? This operation is irreversible.'
    const yesAnswer = 'Yes, delete'
    const noAnswer = 'No, go back'
    modalsRef.value.showModalQuestion(question, yesAnswer, noAnswer)
}

function gotAnswerFromUser(answ) {
    // console.log(answ)
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


function clickedAddTextOne() {
    if (divState.addText.visibleMain === true) {
        if (divState.addText.visibleOne === true) {
            divState.addText.visibleMain = false
        } else {
            divState.addText.visibleMany = false
            divState.addText.visibleOne = true
        }
    } else {
        // console.log(divState.addText)
        divState.addText.visibleMain = true
        divState.addText.visibleMany = false
        divState.addText.visibleOne = true
    }
}


function clickedAddTextMany() {
    if (divState.addText.visibleMain === true) {
        if (divState.addText.visibleMany === true) {
            divState.addText.visibleMain = false
        } else {
            divState.addText.visibleOne = false
            divState.addText.visibleMany = true
        }
    } else {
        // console.log(divState.addText)
        divState.addText.visibleMain = true
        divState.addText.visibleOne = false
        divState.addText.visibleMany = true
    }
}

function clickedSaveTextOne() {
    const bookId = divState.selectedBook.id
    const chapterName = createTextChapter.value.value
    const textStr = createTextStr.value.value
    // console.log(bookId, chapterName, textStr)

    const validatedChapterName = validateNameString(chapterName)
    if (validatedChapterName === false) {
        pushNotification('The name of the chapter must be from 1 to 255 characters long...', 'warning')
    } else {
        if (textStr.length < 1) {
            pushNotification('Looks like you forgot to add text...', 'warning')
        } else {
            // console.log(bookId, chapterName, textStr)
            createChapterFetch(bookId, chapterName, textStr)
        }
    }
}

////////////////////////////////////////////////////////////// BOOK FETCHES ///

function createBookFetch(newBookName) {
    const requestData = {
        method: 'POST',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
            'name': newBookName
        })
    }
    fetch('/api/books/', requestData)
        .then( response => {
            if (response.status === 204) {
                getBooksFetch()
                pushNotification('Book created successfully', 'good')
            } else if (response.status === 409) {
                pushNotification('This book already exist', 'warning')
            } else {
                pushNotification('Something went wrong', 'error')
            }
        })
}


function getBooksFetch() {
    divState.newBook.visible = false
    divState.addText.visibleMain = false
    divState.chaptersList.visible = false
    divState.selectedBook.visible = false
    books.length = 0
    const requestData = {
        method: 'GET',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }
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
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
            'name': newBookName
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
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
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

////////////////////////////////////////////////////////////// TEXT FETCHES ///

function createChapterFetch(bookId, chapterName, textStr) {
    const requestData = {
        method: 'POST',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
            'book_id': bookId,
            'chapter_name': chapterName,
            'text': textStr,
        })
    }
    fetch('/api/chapters/', requestData)
        .then( response => {
            console.log(response.status)
            if (response.status === 204) {
                getBooksFetch()
                pushNotification('Text added successfully', 'good')
            } else {
                pushNotification('Something went wrong', 'error')
            }
        })
}


function getChaptersFetch(bookId) {
    divState.loadingGif.visible = true
    const requestData = {
        method: 'GET',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }
    }
    fetch(`/api/chapters/${bookId}/`, requestData)
        .then( response => {
            if (response.status === 200) {
                response.json().then( result => {
                    // console.log(result)
                    chapters.length = 0
                    for (const chapter of result.chapters) {
                        chapters.push(chapter)
                        // console.log(chapter)
                    }
                    // console.log(chapters)
                    divState.loadingGif.visible = false
                    divState.chaptersList.visible = true
                    divState.selectedBook.visible = true
                })
            } else {
                divState.loadingGif.visible = false
            }
        })
}


// function deleteTextsByChapterNameFetch(chapterName) {
function deleteChapterFetch(ch_id) {
    const requestData = {
        method: 'DELETE',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
        // body: JSON.stringify({
        //     'chapter': chapterName,
        // })
    }
    fetch(`/api/chapters/${ch_id}/`, requestData)
        .then( response => {
            if (response.status === 204) {
                getBooksFetch()
                pushNotification('Chapter deleted successfully', 'good')
            } else {
                pushNotification('Something went wrong', 'error')
            }
        })
}


onMounted(() => {
    getBooksFetch()
})

</script>



<style>
:root {
    --gtc1: 26px;
    --gtc2: 52px;
    --gtc3: 1fr;
    --gtc4: 80px;
    --gtc5: 85px;
    --gtc6: 86px;
    --gtc7: 33px;
    /* --gtc7: max-content; */
    /* --gtc7: max-content; */
}
</style>

<style scoped>

/* .hidden {
    display: none;
} */

h2 {
    margin: 7px;
    text-align: center;
}

/* .container-info {
    display: grid;
    grid-template-columns: 35% 65%;
    user-select: none;
    font-size: 18px;
}
.container-info .book-list-info { padding-left: 13px }
.container-info .text-list-info { padding-left: 25px }

body.light .container-info .book-list-info { color: var(--grey7) }
body.light .container-info .text-list-info { color: var(--grey7) }
body.night .container-info .book-list-info { color: var(--grey4) }
body.night .container-info .text-list-info { color: var(--grey4) } */



.container {
    /* display: grid; */
    /* grid-template-columns: 35% 65%; */
    display: flex;
    height: 100%;
}
.container > .book-list {
    width: 34%;

    display: flex;
    flex-direction: column;
    gap: 5px;
}

.container > .book-list > .book-cont {
    border-radius: 3px;
    /* margin-bottom: 5px; */
    padding: 5px 5px;
    height: 40px;
    position: relative;
    bottom: 0px;
    transition: 0.1s;

    display: flex;
    align-items: center;
}
body.light .container > .book-list > .book-cont { background-color: var(--grey2) }
body.night .container > .book-list > .book-cont { background-color: var(--grey7) }

body.light .container > .book-list > .book-cont { color: var(--grey7); }
body.night .container > .book-list > .book-cont { color: var(--grey2); }

/* .container > .book-list > .book-cont-add {
} */

.container > .book-list > .book-cont > .book-name, .book-plus {
    font-weight: 700;
    font-size: 20px;
    pointer-events: none;

    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.container > .book-list > .book-cont > .book-plus {
    text-align: center;
    width: 100%;
    font-size: 20px;
}

/* .container > .book-list > .book-cont-add:hover {
} */
.container > .book-list > .hoverable:hover {
    cursor: pointer;
    left: 5px;
}
body.light .container > .book-list > .hoverable:hover {
    color: var(--grey8);
    background-color: var(--grey3);
}
body.night .container > .book-list > .hoverable:hover {
    color: var(--white);
    background-color: var(--grey6);
}




.container > .text-list {
    width: 66%;

    margin-left: 10px;

    display: flex;
    flex-direction: column;
    gap: 5px;

    /* flex: 1 0 auto; */
    /* height: 1%; */
}
.container > .text-list > .new-book > .cont {
    display: flex;
    gap: 5px;
    justify-content: center;
    align-items: center;
}
.container > .text-list > .new-book > .cont > * {
    font-weight: 700;
    font-size: 20px;
}
.container > .text-list > .new-book > .cont > .header {
    /* flex-grow: 2; */
    /* flex: 1 1 auto */
}
.container > .text-list > .new-book > .cont > .name {
    /* flex-grow: 1; */
    /* flex: 1 1 auto */
    width: 50%
}






.container > .text-list > .book > .cont {
    border-radius: 3px;
    /* margin-bottom: 5px; */
    padding: 5px 5px;
}
body.light .text-list .book .cont { background-color: var(--grey2) }

body.night .text-list .book .cont { background-color: var(--grey7) }

.container > .text-list > .book > .cont {
    display: flex;
    gap: 5px;
    align-items: center;
}
.container > .text-list > .book > .cont > * {
    font-weight: 700;
    font-size: 20px;
}
.container > .text-list > .book > .cont > .header {
    flex-grow: 1;
    overflow: hidden;
}
.container > .text-list > .book > .cont > .name {
    flex-grow: 1;
}
.container > .text-list > .book > .cont > .btn {
    white-space: nowrap;
}





.container > .text-list > .loading {
    border-radius: 3px;
    /* margin-bottom: 5px; */
    padding: 5px 5px;
    text-align: center;
}
.container > .text-list > .loading > .loading-gif {
    width: 25px;
    height: 25px;
}
body.light .text-list .loading { background-color: var(--grey2) }
body.night .text-list .loading { background-color: var(--grey7) }





/* .container > .text-list > .texts {
} */

/* .container > .text-list > .texts > .chapter-cont {
} */

.container > .text-list > .texts {
    user-select: none;
    /* flex-grow: 1; */

    display: flex;
    flex-direction: column;
    gap: 5px;
    overflow: auto;
    /* height: 300px; */
}

.container > .text-list > .texts > .chapter-cont > .chapter-head-cont {
    display: grid;
    grid-template-columns: var(--gtc1) var(--gtc2) var(--gtc3) var(--gtc4) var(--gtc5) var(--gtc6) var(--gtc7);
    gap: 5px;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    border-radius: 3px;
    /* margin-bottom: 5px; */
    padding: 3px 5px;
}
body.light .text-list > .texts > .chapter-cont > .chapter-head-cont { background-color: var(--grey2) }
body.night .text-list > .texts > .chapter-cont > .chapter-head-cont { background-color: var(--grey7) }

.container > .text-list > .texts > .chapter-cont > .chapter-head-cont > .cell {
    margin: 1px 4px;
}
.container > .text-list > .texts > .chapter-cont > .chapter-head-cont > .chapter-done-pic {
    pointer-events: none;
}
.container > .text-list > .texts > .chapter-cont > .chapter-head-cont > .chapter-done-num {
    pointer-events: none;
    text-align: end;
}
.container > .text-list > .texts > .chapter-cont > .chapter-head-cont > .chapter-name {
    flex-grow: 1;
    pointer-events: none;
    font-style: oblique;
}
.container > .text-list > .texts > .chapter-cont > .chapter-head-cont > .chapter-cpm, .chapter-wpm, .chapter-acc {
    text-align: end;
}






.chapter-add-cont {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    user-select: none;
}

.chapter-add-btn {
    flex-basis: 45%;
    /* width: 50%; */
    flex-grow: 1;
    border-radius: 3px;
    /* margin-bottom: 5px; */
    padding: 5px 5px;
    cursor: pointer;
}

body.light .chapter-add-btn { background-color: var(--grey2) }
body.night .chapter-add-btn { background-color: var(--grey7) }

.chapter-add-hide {
    flex-grow: 1;
    border-radius: 3px;
    /* margin-bottom: 5px; */
    padding: 5px 5px;
    /* flex-basis: 90%; */
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
    gap: 5px 10px;
    grid-template-columns: max-content auto;
}

.chapter-add-one-chapter-tag, .chapter-add-one-text-tag {
    /* font-weight: 700; */
    /* font-size: 20px; */
}
.chapter-add-one-save-btn {
    grid-column: span 2;
    font-weight: 700;
    font-size: 20px;
}



/* <div class="chapter-add-one-header">Add one chapter</div>
<div class="chapter-add-one-chapter-tag">Chapter name:</div>
<input class="chapter-add-one-chapter-input" type="text">
<div class="chapter-add-one-text-tag">Text:</div>
<textarea class="chapter-add-one-text-input" name="" id="" cols="30" rows="10"></textarea>
<button class="chapter-add-one-save-btn">Save</button> */




/* .container > .text-list > .add-text > .cont {
    border-radius: 3px;
    margin-bottom: 5px;
    padding: 5px 5px;
}
body.light .text-list > .add-text > .cont { background-color: var(--grey2) }
body.night .text-list > .add-text > .cont { background-color: var(--grey7) } */

/* .container > .text-list > .add-text > .cont {
} */
/* .container > .text-list > .add-text > .cont > .add {
    font-size: 20px;
    font-weight: 700;
    cursor: pointer;
    text-align: center;
} */
/* .container > .text-list > .add-text > .cont > .cont {
} */
/* .container > .text-list > .add-text > .cont > .cont > .add-chapter-input {
    width: 98%;
    margin-bottom: 5px;
}
.container > .text-list > .add-text > .cont > .cont > .add-text-input {
    width: 98%;
} */

</style>