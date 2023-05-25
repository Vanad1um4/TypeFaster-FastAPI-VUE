from sqlalchemy.orm import Session
from fastapi import Request, Response
import crud
import json


### COOKIE FNS ################################################################

def get_user_id(request: Request, db: Session):
    session_cookies = request.session.get('user')
    # print(session_cookies)

    if session_cookies:
        user_email = session_cookies.get('email').lower()
        # print(user_email)

        if user_email:
            user_id = crud.get_user_id_by_email(user_email, db)
            # print(user_id)

            if user_id:
                return user_id
    else:
        return None


# def get_user_email(request: Request):
#     session_cookies = request.session.get('user')

#     if session_cookies:
#         user_email = session_cookies.get('email')
#         return user_email

#     else:
#         return None


### TEXTS CREATE FNS ##########################################################

def texts_slice(text: str) -> list[str]:
    while '\n\n' in text:
        text = text.replace('\n\n', '\n')
    while '  ' in text:
        text = text.replace('  ', ' ')
    while '…' in text:
        text = text.replace('…', '...')
    while "’" in text:
        text = text.replace("’", "'")
    while "‘" in text:
        text = text.replace("‘", "'")
    while "‘" in text:
        text = text.replace("‘", "'")
    while "“" in text:
        text = text.replace("“", '"')
    while "”" in text:
        text = text.replace("”", '"')
    while "»" in text:
        text = text.replace("»", '"')
    while "«" in text:
        text = text.replace("«", '"')
    while "–" in text:
        text = text.replace("–", '-')

    texts_list = []
    MIN_CHARS_PER_TEXT = 0
    while text:
        line_break_pos = text.find('\n', MIN_CHARS_PER_TEXT)
        if line_break_pos != -1:
            texts_list.append(text[:line_break_pos].strip())
            text = text[line_break_pos+1:]
        if line_break_pos == -1:
            texts_list.append(text)
            text = ''

    return texts_list


def prep_texts_with_stats(texts: list[str]) -> list[dict]:
    texts_with_stats = []

    for text in texts:
        text_dict = {}
        text_dict['text'] = text
        text_dict['done'] = False
        text_dict['chars_n'] = len(text)
        text_dict['words_n'] = len(text.split())
        text_dict['errors'] = 0
        text_dict['time'] = 0
        texts_with_stats.append(text_dict)

    return texts_with_stats


### TEXTS CREATE FNS ##########################################################

def prep_chapters_for_library_display(book_id: int, user_id: int, db: Session):
    texts = crud.get_texts_and_chapters_by_book_id(book_id, user_id, db)
    chapters_dict = {}

    for text in texts:

        if text['ch_id'] not in chapters_dict.keys():
            chapters_dict[text['ch_id']] = {}
            chapters_dict[text['ch_id']]['ch_id'] = text['ch_id']
            chapters_dict[text['ch_id']]['ch_name'] = text['ch_name']
            chapters_dict[text['ch_id']]['charsTotal'] = 0
            chapters_dict[text['ch_id']]['chars'] = 0
            chapters_dict[text['ch_id']]['words'] = 0
            chapters_dict[text['ch_id']]['errors'] = 0
            chapters_dict[text['ch_id']]['time'] = 0
            chapters_dict[text['ch_id']]['done'] = 0
            chapters_dict[text['ch_id']]['cpm'] = 0
            chapters_dict[text['ch_id']]['wpm'] = 0
            chapters_dict[text['ch_id']]['acc'] = 0

        chapters_dict[text['ch_id']]['charsTotal'] += text['txt_chars_n']

        if text['txt_done'] == True:
            chapters_dict[text['ch_id']]['chars'] += text['txt_chars_n']
            chapters_dict[text['ch_id']]['words'] += text['txt_words_n']
            chapters_dict[text['ch_id']]['errors'] += text['txt_errors']
            chapters_dict[text['ch_id']]['time'] += text['txt_time']

    for key in chapters_dict:
        chapters_dict[key]['done'] = chapters_dict[key]['chars'] / chapters_dict[key]['charsTotal']
        if chapters_dict[key]['done'] > 0:
            chapters_dict[key]['cpm'] = round(chapters_dict[key]['chars'] / chapters_dict[key]['time'] * 60 * 1000)
            chapters_dict[key]['wpm'] = round(chapters_dict[key]['words'] / chapters_dict[key]['time'] * 60 * 1000)
            chapters_dict[key]['acc'] = round((1.0 - (chapters_dict[key]['errors'] / chapters_dict[key]['chars'])) * 100)

    sorted_chapters = sorted(chapters_dict.items(), key=lambda x: x[0])
    return [chapter[1] for chapter in sorted_chapters]


def prep_texts_and_a_chapter_for_typing(chapter_id: int, user_id: int, db: Session):
    texts = crud.get_texts_by_chapter_id(chapter_id, user_id, db)

    chapter_dict = {
        'chapterId': texts[0]['ch_id'],
        'chapterName': texts[0]['ch_name'],
        'charsTotal': 0,
        'chars': 0,
        'words': 0,
        'errors': 0,
        'time': 0,
        'done': 0,
    }
    texts_dict = {}
    current_text_id = False

    for text in texts:
        # print(text)

        txt_id = text['txt_id']
        texts_dict[txt_id] = {}
        texts_dict[txt_id]['done'] = text['txt_done']
        texts_dict[txt_id]['chars'] = text['txt_chars_n']
        texts_dict[txt_id]['words'] = text['txt_words_n']
        texts_dict[txt_id]['errors'] = text['txt_errors']
        texts_dict[txt_id]['time'] = text['txt_time']
        texts_dict[txt_id]['text'] = text['txt_text']

        chapter_dict['charsTotal'] += text['txt_chars_n']

        if text['txt_done'] == True:
            chapter_dict['chars'] += text['txt_chars_n']
            chapter_dict['words'] += text['txt_words_n']
            chapter_dict['errors'] += text['txt_errors']
            chapter_dict['time'] += text['txt_time']

        if current_text_id == False and text['txt_done'] == False:
            current_text_id = text['txt_id']

    chapter_dict['done'] = chapter_dict['chars'] / chapter_dict['charsTotal']
    # current_text_id = texts[-1]['txt_id'] if current_text_id == False else current_text_id
    chapter_dict['lastTextId'] = texts[-1]['txt_id']

    # print(current_text_id)
    # print(chapter_dict)
    # print(texts_dict.keys())
    # print(len(texts_dict.keys()))

    AMT = 20
    keys_range = AMT
    texts_keys = list(texts_dict.keys())
    # print(texts_keys)
    start_idx = texts_keys.index(current_text_id) - keys_range
    start_idx = start_idx if start_idx >= 0 else 0
    end_idx = texts_keys.index(current_text_id) + keys_range+1
    text_keys_clipped = texts_keys[start_idx:end_idx]
    texts_dict_clipped = {k: v for k, v in texts_dict.items() if k in text_keys_clipped}

    # for (idx, text) in texts_dict_clipped.items():
    #     # for text in texts_dict.values():
    #     print(idx, text)

    # resulting_dict = {'chapter': chapter_dict, 'texts': texts_dict}
    # print(resulting_dict)
    # return resulting_dict
    # return chapter_dict, texts_dict
    return chapter_dict, texts_dict_clipped


def prep_next_batch_of_texts_for_typing(chapter_id: int, text_id: int, user_id: int, db: Session):
    AMT = 10
    texts = crud.get_next_batch_of_texts(chapter_id, text_id, AMT, user_id, db)
    # print(texts)
    texts_dict = {}

    for text in texts:
        # print(text)
        txt_id = text['txt_id']
        texts_dict[txt_id] = {}
        texts_dict[txt_id]['done'] = text['txt_done']
        texts_dict[txt_id]['chars'] = text['txt_chars_n']
        texts_dict[txt_id]['words'] = text['txt_words_n']
        texts_dict[txt_id]['errors'] = text['txt_errors']
        texts_dict[txt_id]['time'] = text['txt_time']
        texts_dict[txt_id]['text'] = text['txt_text']

    # for (idx, text) in texts_dict.items():
    #     # for text in texts_dict.values():
    #     print(idx, text)

    return texts_dict
