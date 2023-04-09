<template>
    <div
        class="main-modal-bg"
        v-show="modalsState.modalQuestion.visible"
        v-on:click="modalQuestionPressedNo"
    >
        <div class="modal-window">
            <div class="modal-window-message"> {{ modalsState.modalQuestion.question }} </div>
            <div class="modal-window-yes" v-on:click.stop="modalQuestionPressedYes">{{ modalsState.modalQuestion.answerYes }}</div>
            <div class="modal-window-no" v-on:click.stop="modalQuestionPressedNo">{{ modalsState.modalQuestion.answerNo }}</div>
        </div>
    </div>

    <div
        class="main-popup"
    >
        <div
            class="single-popup"
            v-for="notiff in modalsState.notification.list"
            v-bind:class="notiff.class"
        >
            {{ notiff.message }}
        </div>
    </div>
</template>



<script setup>
import { toRef, ref, reactive } from 'vue';

// import { onMounted } from 'vue';
// onMounted(() => {
//     console.log("AAAAAAAAAAAAAAAAAAAAAAA")
//     addNotification('BIG VERY BIG ad veeeery long text of a push notification why on Earth anyone would write something like that? CRAAAAAZY', 'error', 50000)
//     addNotification('BIG VERY BIG ad veeeery long text of a push notification why on Earth anyone would write something like that? CRAAAAAZY', 'warning', 50000)
//     addNotification('BIG VERY BIG ad veeeery long text of a push notification why on Earth anyone would write something like that? CRAAAAAZY', 'good', 50000)
//     addNotification('BIG VERY BIG ad veeeery long text of a push notification why on Earth anyone would write something like that? CRAAAAAZY', 'info', 50000)
// })

// const props = defineProps({
//     modalQuestionIsActive: {
//         type: Boolean,
//         default: true
//     },
//     text: {
//         type: String,
//         default: 'No text...'
//     }
// })

const modalsState = reactive({
    modalQuestion: {
        visible: false,
        question: '',
        answerYes: '',
        answerNo: '',
    },
    notification: {
        index: 0,
        list: {} // 0: {'message': 'lalala', 'class': 'warning'}
    }
})

const emit = defineEmits(['modalQuestionPressedYes', 'modalQuestionPressedNo'])

function modalQuestionPressedYes() {
    modalsState.modalQuestion.visible = false
    emit('answer', 'yes')
}
function modalQuestionPressedNo() {
    modalsState.modalQuestion.visible = false
    emit('answer', 'no')
}

function showModalQuestion(question, answerYes, answerNo) {
    modalsState.modalQuestion.visible = true
    modalsState.modalQuestion.question = question
    modalsState.modalQuestion.answerYes = answerYes
    modalsState.modalQuestion.answerNo = answerNo
}

function addNotification(notiffText, notiffClass='info', timerSec=5) {
    modalsState.notification.index++
    const nextIdx = modalsState.notification.index
    modalsState.notification.list[nextIdx] = {}
    modalsState.notification.list[nextIdx]['message'] = notiffText
    if (['error', 'warning', 'good'].includes(notiffClass)) {
        modalsState.notification.list[nextIdx]['class'] = notiffClass
    } else {
        modalsState.notification.list[nextIdx]['class'] = 'info'
    }
    // console.log(modalsState.notification.list)
    setTimeout(function () {removeOldNotifications(nextIdx)}, timerSec*1000)

    function removeOldNotifications(idx) {
        delete modalsState.notification.list[idx]
        // console.log(modalsState.notification.list)
    }
}


defineExpose({ showModalQuestion, addNotification })

</script>



<style scoped>
.main-modal-bg {
    user-select: none;
    /* display: none; */
    position: fixed;
    z-index: 1;
    /* padding-top: 0px; */
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    /* overflow: auto; */
    /* background-color: rgb(0,0,0); */
    background-color: rgb(0 0 0 / 60%);
}
.modal-window {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    align-items: center;
    font-size: 150%;
    font-weight: bold;
    /* background-color: white; */
    color: black;
    margin: auto;
    padding: 0;
    /* width: min-content; */
    width: 500px;
    /* height: 100%; */
    animation-name: animateappear;
    /* animation-duration: 0.2s; */
    /* white-space: nowrap; */
    margin-top: 38%;
    text-align: center;
}
/* @keyframes animateappear {
    from {opacity:0}
    to {opacity:1}
} */
.modal-window > div {
    border-radius: 5px;
    padding: 9px;
    box-shadow: 5px 6px 5px rgba(0, 0, 0, 0.35);
}
.modal-window-message {
    flex: 0 1 100%;
    /* background-color: white; */
}
.modal-window-yes {
    /* background-color: rgb(115, 214, 115); */
}
.modal-window-no {
    /* background-color: #ff7575; */
}
.modal-window-yes, .modal-window-no {
    flex-grow: 1;
    cursor: pointer;
}
body.light .modal-window-message { color: black }
body.light .modal-window-message { background-color: #e7e7e7 }
body.night .modal-window-message { color: white }
body.night .modal-window-message { background-color: #424242 }

body.light .modal-window-yes { color: black }
body.light .modal-window-yes { background-color: #2ee94e }
body.night .modal-window-yes { color: white }
body.night .modal-window-yes { background-color: #3a7227 }

body.light .modal-window-no { color: black }
body.light .modal-window-no { background-color: #e73232 }
body.night .modal-window-no { color: white }
body.night .modal-window-no { background-color: #952626 }




.main-popup {
    display: flex;
    flex-wrap: wrap;
    flex-direction: column;
    align-items: end;
    gap: 25px;

    position: fixed;
    z-index: 1;
    right: 0;
    bottom: 0;
    padding: 25px;
    width: 400px;

    user-select: none;
    z-index: 0;
}

.single-popup {
    /* align-self: flex-end; */

    border: solid rgb(169 169 169) 1px;
    border-radius: 5px;
    padding: 9px;
    box-shadow: 5px 6px 5px rgba(0, 0, 0, 0.35);
    font-weight: bold;
    font-size: larger;
    text-align: justify;
    width: fit-content;
}
/* .error{
    background-color: red;
    color: white;
}
.warning{
    background-color: orange;
}
.good{
    background-color: green;
    color: white;
}
.info{
    background-color: white;
} */

body.light .info { color: black }
body.light .info { background-color: #ededed }
body.night .info { color: black }
body.night .info { background-color: #d5d5d5 }

body.light .good { color: black }
body.light .good { background-color: #69eb6d }
body.night .good { color: black }
body.night .good { background-color: #6ae76a }

body.light .warning { color: black }
body.light .warning { background-color: #ffc65d }
body.night .warning { color: black }
body.night .warning { background-color: #f1b548 }

body.light .error { color: black }
body.light .error { background-color: #ff4949 }
body.night .error { color: black }
body.night .error { background-color: #ff5757 }

</style>