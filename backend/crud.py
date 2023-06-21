from models import User, Book, Text
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from schemas import Options
import models
import json


def dictify_object(db_obj):
    return {k: v for k, v in db_obj.__dict__.items() if k != '_sa_instance_state'}


def dictify_list_of_objects(list_of_db_objs):
    return [dictify_object(db_obj) for db_obj in list_of_db_objs]


### USER CRUDs ################################################################

def get_user_id_by_email(user_email: str, db: Session):
    try:
        db_user = db.query(User).filter(User.email == user_email).first()

        if db_user is None:
            db_new_user = create_user(user_email, db)

            return db_new_user.id

        return db_user.id

    except Exception as exc:
        print(exc)
        db.rollback()
        return None


def get_user_profile(user_id: int, db: Session):
    try:
        db_user_profile = db.query(User).filter(User.id == user_id).first()

        return dictify_object(db_user_profile)

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def create_user(user_email: str, db: Session):
    try:
        db_user_profile = User(email=user_email)
        db.add(db_user_profile)
        db.commit()
        db.refresh(db_user_profile)
        return db_user_profile

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def set_user_options(options: Options, user_id: int, db: Session):
    try:
        db_user = db.query(User).filter(User.id == user_id).first()

        db_user.dark_mode = options.dark_mode
        db_user.window_width = options.window_width
        db_user.show_stats_bar = options.show_stats_bar
        db_user.show_progress_bar = options.show_progress_bar
        db_user.show_error_history = options.show_error_history
        db_user.active_line_position = options.active_line_position
        db_user.gap_between_texts = options.gap_between_texts

        db_user.stats_slice_length_minutes = options.stats_slice_length_minutes
        db_user.use_n_last_minutes_for_stats = options.use_n_last_minutes_for_stats

        db.add(db_user)
        db.commit()

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


### BOOKS CRUDS ###############################################################

def create_book(book_title: str, user_id: int, db: Session):
    try:
        db_book = Book(title=book_title, user_id=user_id)
        db.add(db_book)
        db.commit()
        return db_book

    except Exception as exc:
        print(exc)
        db.rollback()
        return None


def get_all_books(user_id: int, db: Session):
    try:
        return db.query(Book).filter(Book.user_id == user_id).order_by(Book.id).all()

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def get_book_by_id(book_id: int, user_id: int, db: Session):
    try:
        return db.query(Book).filter(Book.user_id == user_id).filter(Book.id == book_id).first()

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def get_book_by_title(name: str, user_id: int, db: Session):
    try:
        return db.query(Book).filter(Book.user_id == user_id).filter(Book.title == name).first()

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def rename_book(book_id: int, book_title: str, user_id: int, db: Session):
    try:
        db_book = db.query(Book).filter(Book.user_id == user_id).filter(Book.id == book_id).first()
        db_book.title = book_title
        db.add(db_book)
        db.commit()
        return True

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def delete_book_by_id(book_id: int, user_id: int, db: Session):
    try:
        db.query(Book).filter(Book.user_id == user_id).filter(Book.id == book_id).delete()
        db.commit()
        return True

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


### TEXTS CRUDS ###############################################################


def create_texts(book_id: int, user_id: int, list_of_text_dicts: list[dict], db: Session):
    try:
        book_id_validated = db.query(Book).filter(Book.user_id == user_id).filter(Book.id == book_id).first().id

        if not book_id_validated:
            return False

        for text_dict in list_of_text_dicts:
            db_text = models.Text(
                book_id=book_id_validated,
                text=text_dict['text'],
                done=False,
                chars_n=text_dict['chars_n'],
                words_n=text_dict['words_n'],
                errors=0,
                time=0,
                stats_list=json.dumps([])
            )
            db.add(db_text)
        db.commit()
        return True

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def get_texts_by_book_id(book_id: int, user_id: int, include_text: bool, db: Session):
    columns = [
        Text.id.label('id'),
        Text.done.label('done'),
        Text.chars_n.label('chars_n'),
        Text.words_n.label('words_n'),
        Text.errors.label('errors'),
        Text.time.label('time'),
    ]
    if include_text:
        columns.append(Text.text.label('text'))

    query = select(columns).join(Book).filter(Book.user_id == user_id).filter(Text.book_id == book_id).order_by(Text.id)
    texts_db = db.execute(query).fetchall()
    list_of_text_dicts = [dict(item) for item in texts_db]
    return list_of_text_dicts


def get_next_batch_of_texts(text_id: int, amt: int, user_id: int, db: Session):
    columns = [
        Text.id.label('id'),
        Text.text.label('text'),
        Text.done.label('done'),
        Text.chars_n.label('chars_n'),
        Text.words_n.label('words_n'),
        Text.errors.label('errors'),
        Text.time.label('time'),
    ]
    query = select(columns).join(Book).filter(Book.user_id == user_id).filter(Text.id > text_id).order_by(Text.id).limit(amt)
    texts_db = db.execute(query).fetchall()
    list_of_text_dicts = [dict(item) for item in texts_db]
    # print(list_of_text_dicts)
    return list_of_text_dicts


### STATS CRUDS ###############################################################

def save_stats(text_id: int, errors: int, time: int, stats_list: list, user_id: int, db: Session):
    try:
        db_text = db.query(Text).join(Book).filter(Book.user_id == user_id).filter(Text.id == text_id).first()

        if db_text is None:
            return False
        else:
            db_text.done = True
            db_text.errors = errors
            db_text.time = time
            db_text.stats_list = json.dumps(stats_list)
            db.add(db_text)
            db.commit()
            return True

    except Exception as exc:
        print(exc)
        db.rollback()
        return False
