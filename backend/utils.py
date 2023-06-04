from const import INIT_LOAD_N_PREV_TYPED_TEXTS, INIT_LOAD_N_NEXT_TEXTS_TO_TYPE, NUM_OF_TEXTS_TO_LOAD
from fastapi import Request, Response
from sqlalchemy.orm import Session
import crud
import json


### COOKIE FNS ################################################################

def get_user_id(request: Request, db: Session):
    session_cookies = request.session.get('user')
    # print('session_cookies: ', session_cookies)

    if session_cookies:
        user_email = session_cookies.get('email').lower()
        # print('user_email: ', user_email)

        if user_email:
            user_id = crud.get_user_id_by_email(user_email, db)
            # print('user_id: ', user_id)

            if user_id:
                return user_id

    return None


### PREP TEXTS FOR BOOK CREATION ###############################################

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
    while "—" in text:
        text = text.replace("—", '-')

    texts_list = []
    while text:
        line_break_pos = text.find('\n')
        if line_break_pos != -1:
            texts_list.append(text[:line_break_pos].strip())
            text = text[line_break_pos+1:]
        if line_break_pos == -1:
            texts_list.append(text)
            text = ''

    return texts_list


### PREP TEXT STATS FOR BOOK CREATION ##########################################

def prep_texts_calc_stats(texts: list[str]) -> list[dict]:
    texts_with_stats = []

    for text in texts:
        text_dict = {}
        text_dict['text'] = text
        text_dict['chars_n'] = len(text)
        text_dict['words_n'] = len(text.split())
        texts_with_stats.append(text_dict)

    return texts_with_stats


### STATS PREP FOR LIBRARY #####################################################

def text_stats_prep_for_library(book_id: int, user_id: int, db: Session):
    users_options = crud.get_user_profile(user_id, db)
    all_texts = crud.get_texts_by_book_id(book_id, user_id, False, db)

    chars_sum = sum([text['chars_n'] for text in all_texts])
    chars_done_sum = sum([text['chars_n'] for text in all_texts if text['done'] == True])

    # IF NONE OF THE TEXTS HAVE BEEN FINISHED
    if all_texts[0]['done'] == False:
        return {
            'chart_stats': {'labels': [], 'cpm': [], 'wpm': [], 'acc': []},
            'first_untyped_text_id': all_texts[0]['id'],
            'time_passed': {'h': 0, 'm': 0},
            'time_remaines_approx': {'h': None, 'm': None},
            'chars_sum': chars_sum,
            'chars_done_sum': chars_done_sum,
        }

    tmp_dict_of_texts = {1: {'time': 0, 'chars': 0, 'words': 0, 'errors': 0}}
    i = 1
    sum_ms = 0
    first_untyped_text_id = -1
    first_untyped_text_found = False

    num_of_not_typed_chars = 0

    for text in all_texts:
        if text['done'] == True:
            if tmp_dict_of_texts[i]['time'] > users_options['stats_slice_length_minutes'] * 60 * 1000:  # Converting to ms
                i += 1
                tmp_dict_of_texts[i] = {'time': 0, 'chars': 0, 'words': 0, 'errors': 0}

            sum_ms += text['time']
            tmp_dict_of_texts[i]['time'] += text['time']
            tmp_dict_of_texts[i]['chars'] += text['chars_n']
            tmp_dict_of_texts[i]['words'] += text['words_n']
            tmp_dict_of_texts[i]['errors'] += text['errors']

        else:
            num_of_not_typed_chars += text['chars_n']

            if first_untyped_text_found == False:
                first_untyped_text_id = text['id']
                first_untyped_text_found = True

    result_dict_of_stats = {'chart_stats': {'labels': [], 'cpm': [], 'wpm': [], 'acc': []}}

    # MAKING RESULT DICT OF STATS LISTS SLICED ON CHUNKS
    for n, stats_chunk in tmp_dict_of_texts.items():
        # print(n, stats_chunk)
        result_dict_of_stats['chart_stats']['labels'].append(n)
        if stats_chunk['time'] > 0:
            result_dict_of_stats['chart_stats']['cpm'].append(round(stats_chunk['chars'] / stats_chunk['time'] * 60 * 1000))
            result_dict_of_stats['chart_stats']['wpm'].append(round(stats_chunk['words'] / stats_chunk['time'] * 60 * 1000))
            result_dict_of_stats['chart_stats']['acc'].append(round((1.0 - (stats_chunk['errors'] / stats_chunk['chars'])) * 100))

    result_dict_of_stats['time_passed'] = {}
    result_dict_of_stats['time_passed']['h'] = int(sum_ms // (1000 * 60 * 60))
    sum_ms %= (1000 * 60 * 60)
    result_dict_of_stats['time_passed']['m'] = int(sum_ms // (1000 * 60))

    if first_untyped_text_found == True:
        result_dict_of_stats['first_untyped_text_id'] = first_untyped_text_id
    else:
        result_dict_of_stats['first_untyped_text_id'] = None

    list_of_times_of_done_texts = [text['time'] for text in all_texts if text['done'] == True]

    tmp_accum_minutes = 0
    num_of_last_texts_to_calc_stats = 0

    while (tmp_accum_minutes < users_options['use_n_last_minutes_for_stats'] * 60 * 1000
           and num_of_last_texts_to_calc_stats < len(list_of_times_of_done_texts)):

        tmp_accum_minutes += list_of_times_of_done_texts[-num_of_last_texts_to_calc_stats-1]
        num_of_last_texts_to_calc_stats += 1

    last_cpms = result_dict_of_stats['chart_stats']['cpm'][-num_of_last_texts_to_calc_stats:]
    average_cpm = sum(last_cpms) / len(last_cpms)
    estimated_n_chunks_remains = round(num_of_not_typed_chars / (average_cpm * users_options['stats_slice_length_minutes']))

    last_label = result_dict_of_stats['chart_stats']['labels'][-1]
    list_of_nones = [None for _ in range(estimated_n_chunks_remains)]
    result_dict_of_stats['chart_stats']['labels'] += ([last_label + i for i in range(1, estimated_n_chunks_remains+1)])
    result_dict_of_stats['chart_stats']['cpm'] += (list_of_nones)
    result_dict_of_stats['chart_stats']['wpm'] += (list_of_nones)
    result_dict_of_stats['chart_stats']['acc'] += (list_of_nones)

    approx_remaining_time_ms = (num_of_not_typed_chars / average_cpm) * 60 * 1000
    result_dict_of_stats['time_remaines_approx'] = {}
    result_dict_of_stats['time_remaines_approx']['h'] = int(approx_remaining_time_ms // (1000 * 60 * 60))
    approx_remaining_time_ms %= (1000 * 60 * 60)
    result_dict_of_stats['time_remaines_approx']['m'] = int(approx_remaining_time_ms // (1000 * 60))

    result_dict_of_stats['chars_sum'] = chars_sum
    result_dict_of_stats['chars_done_sum'] = chars_done_sum

    return result_dict_of_stats


### INIT TEXT STATS PREP FOR TYPING ############################################

def init_text_stats_prep_for_typing(book_id: str, user_id: int, db: Session):
    users_options = crud.get_user_profile(user_id, db)

    db_book = crud.get_book_by_id(book_id, user_id, db)
    book_title = db_book.title

    all_texts = crud.get_texts_by_book_id(book_id, user_id, True, db)

    chars_sum = sum([text['chars_n'] for text in all_texts])
    chars_done_sum = sum([text['chars_n'] for text in all_texts if text['done'] == True])

    last_text_id = None
    if all_texts:
        last_text_id = all_texts[-1]['id']

    result_dict = {
        'texts': {},
        'last_text_id': last_text_id,
        'book_title': book_title,
        'chars_sum': chars_sum,
        'chars_done_sum': chars_done_sum
    }

    # IF NONE OF THE TEXTS HAVE BEEN FINISHED
    if all_texts and all_texts[0]['done'] == False:
        texts_list = all_texts[:INIT_LOAD_N_NEXT_TEXTS_TO_TYPE]
        result_dict['texts'] = {text['id']: text for text in texts_list}

        for text_id in result_dict['texts'].keys():
            del result_dict['texts'][text_id]['id']

        return result_dict

    first_untyped_idx = None

    for text in all_texts:
        if text['done'] == False:
            first_untyped_idx = all_texts.index(text)
            break

    # IF ALL THE TEXTS HAVE BEEN FINISHED
    if first_untyped_idx is None:
        return result_dict

    # PREPPING FINISHED TEXTS...
    finished_texts_list = all_texts[:first_untyped_idx]
    finished_texts_dict = {text['id']: text for text in finished_texts_list}
    all_finished_text_ids = finished_texts_dict.keys()

    for text_id in all_finished_text_ids:
        del finished_texts_dict[text_id]['id']

    result_dict['texts'] = finished_texts_dict.copy()

    texts_cnt = 0
    sum_time = 0
    keep_last_n_ms_of_stats = users_options['use_n_last_minutes_for_stats'] * 60 * 1000

    for text_id in reversed(all_finished_text_ids):
        # Dropping excess text stats
        if texts_cnt <= INIT_LOAD_N_PREV_TYPED_TEXTS:
            texts_cnt += 1
        if texts_cnt > INIT_LOAD_N_PREV_TYPED_TEXTS:
            del result_dict['texts'][text_id]['text']

        # Dropping excess texts
        if sum_time > keep_last_n_ms_of_stats and texts_cnt > INIT_LOAD_N_PREV_TYPED_TEXTS:
            del result_dict['texts'][text_id]
        if sum_time <= keep_last_n_ms_of_stats:
            sum_time += result_dict['texts'][text_id]['time']

    # ...PREPPING UNFINISHED TEXTS...
    unfinished_texts_list = all_texts[first_untyped_idx:first_untyped_idx+NUM_OF_TEXTS_TO_LOAD]
    unfinished_texts_dict = {text['id']: text for text in unfinished_texts_list}

    for text_id in unfinished_texts_dict.keys():
        del unfinished_texts_dict[text_id]['id']

    # ...AND GLUEING THEM TOGETHER
    result_dict['texts'].update(unfinished_texts_dict)

    return result_dict


### FOLLOWING TEXT STATS PREP FOR TYPING #######################################

def prep_next_batch_of_texts_for_typing(text_id: int, user_id: int, db: Session):
    texts = crud.get_next_batch_of_texts(text_id, NUM_OF_TEXTS_TO_LOAD, user_id, db)
    texts_dict = {}

    for text in texts:
        txt_id = text['id']
        texts_dict[txt_id] = {}
        texts_dict[txt_id]['done'] = text['done']
        texts_dict[txt_id]['chars_n'] = text['chars_n']
        texts_dict[txt_id]['words_n'] = text['words_n']
        texts_dict[txt_id]['errors'] = text['errors']
        texts_dict[txt_id]['time'] = text['time']
        texts_dict[txt_id]['text'] = text['text']

    return texts_dict
