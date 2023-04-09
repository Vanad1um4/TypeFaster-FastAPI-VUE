from models import User, Book, Chapter, Text
from sqlalchemy.orm import Session
from schemas import OptionsSet
from sqlalchemy import select
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
            db_new_user = create_user(db, user_email)

            return db_new_user.id

        return db_user.id

    except Exception as exc:
        print(exc)
        db.rollback()
        return None


def get_user_profile(db: Session, user_id: int | None):
    try:
        db_user_profile = db.query(User).filter(User.id == user_id).first()

        return dictify_object(db_user_profile)

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def create_user(db: Session, user_email: str | None):
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


def set_user_options(db: Session, options: OptionsSet, user_id: int):
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        # if db_user is None:
        #     db_user = create_user(db, user_email)
        # else:
        db_user.dark_mode = options.dark_mode
        db_user.window_width = options.window_width
        db_user.show_stats_bar = options.show_stats_bar
        db_user.show_progress_bar = options.show_progress_bar
        db_user.show_error_history = options.show_error_history
        db.add(db_user)
        db.commit()

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


### BOOKS CRUDS ###############################################################

def create_book(name: str, user_id: int, db: Session):
    try:
        db_book = Book(name=name, user_id=user_id)
        db.add(db_book)
        db.commit()
        return db_book

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def get_all_books(user_id: int, db: Session):
    try:
        return db.query(Book).filter(Book.user_id == user_id).order_by(Book.id).all()

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def get_book_by_id(id: int, user_id: int, db: Session):
    try:
        return db.query(Book).filter(Book.user_id == user_id).filter(Book.id == id).first()

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def get_book_by_name(name: str, user_id: int, db: Session):
    try:
        return db.query(Book).filter(Book.user_id == user_id).filter(Book.name == name).first()

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def rename_book(id: int, name: str, user_id: int, db: Session):
    try:
        db_book = db.query(Book).filter(Book.user_id == user_id).filter(Book.id == id).first()
        db_book.name = name
        db.add(db_book)
        db.commit()
        return db_book

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


### CHAPTERS CRUDS ############################################################

def create_chapter(book_id: int, chapter: str, user_id: int, db: Session):
    try:
        db_book = db.query(Book).filter(Book.user_id == user_id).filter(Book.id == book_id).first()
        db_chapter = db.query(Chapter).join(Book).filter(Book.id == book_id).filter(Chapter.name == chapter).first()

        if db_chapter is None:
            db_chapter = models.Chapter(name=chapter, book_id=db_book.id)
            db.add(db_chapter)
            db.commit()
            db.refresh(db_chapter)
            chapter_id = db_chapter.id
        else:
            chapter_id = db_chapter.id

        return chapter_id

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def create_texts(chapter_id: int, list_of_text_dicts: list[dict], db: Session):
    try:
        for text_dict in list_of_text_dicts:
            db_text = models.Text(
                chapter_id=chapter_id,
                text=text_dict['text'],
                done=False,
                chars_n=text_dict['chars_n'],
                words_n=text_dict['words_n'],
                errors=text_dict['errors'],
                time=text_dict['time'],
                stats_list=json.dumps([])
            )
            db.add(db_text)
        db.commit()

        return True

    except Exception as exc:
        print(exc)
        db.rollback()
        return False


def get_chapters_by_book_id(book_id: int, db: Session):
    return dictify_list_of_objects(db.query(models.Chapter).filter(models.Chapter.book_id == book_id).all())


def get_chapters_by_chapter_id(chapter_id: int, db: Session):
    return dictify_list_of_objects(db.query(models.Chapter).filter(models.Chapter.id == chapter_id).all())


def delete_chapter_by_id(chapter_id: int, user_id: int, db: Session):
    try:
        subquery = db.query(Chapter).join(Book).filter(Book.user_id == user_id, Chapter.id == chapter_id).subquery()
        # print(subquery)
        db.query(Chapter).filter(Chapter.id.in_(select([subquery.c.id]))).delete(synchronize_session=False)

        db.commit()
        return True
    except Exception as exc:
        print(exc)
        db.rollback()
        return False


### TEXTS CRUDS ###############################################################

def get_texts_and_chapters_by_book_id(book_id: int, user_id: int, db: Session):
    texts_db = db.query(
        Chapter.id.label('ch_id'),
        Chapter.name.label('ch_name'),
        Text.id.label('txt_id'),
        Text.text.label('txt_text'),
        Text.done.label('txt_done'),
        Text.chars_n.label('txt_chars_n'),
        Text.words_n.label('txt_words_n'),
        Text.errors.label('txt_errors'),
        Text.time.label('txt_time'),
    ).join(Chapter).join(Book).filter(Book.user_id == user_id).filter(Book.id == book_id).all()
    # print(texts_db)
    list_of_text_dicts = [dict(item) for item in texts_db]
    return list_of_text_dicts


def get_texts_by_chapter_id(chapter_id: int, user_id: int, db: Session):
    texts_db = db.query(
        Chapter.id.label('ch_id'),
        Chapter.name.label('ch_name'),
        Text.id.label('txt_id'),
        Text.text.label('txt_text'),
        Text.done.label('txt_done'),
        Text.chars_n.label('txt_chars_n'),
        Text.words_n.label('txt_words_n'),
        Text.errors.label('txt_errors'),
        Text.time.label('txt_time'),
    ).join(Chapter).join(Book).filter(Book.user_id == user_id).filter(Text.chapter_id == chapter_id).order_by(Text.id).all()
    # print(texts_db)
    list_of_text_dicts = [dict(item) for item in texts_db]
    # print(list_of_text_dicts)
    return list_of_text_dicts


def get_next_batch_of_texts(chapter_id: int, text_id: int, amt: int, user_id: int, db: Session):
    texts_db = db.query(
        Text.id.label('txt_id'),
        Text.text.label('txt_text'),
        Text.done.label('txt_done'),
        Text.chars_n.label('txt_chars_n'),
        Text.words_n.label('txt_words_n'),
        Text.errors.label('txt_errors'),
        Text.time.label('txt_time'),
    ).join(Chapter).join(Book).filter(Book.user_id == user_id).filter(Chapter.id == chapter_id).filter(Text.id > text_id).order_by(Text.id).limit(amt).all()
    # print(texts_db)
    # print()
    list_of_text_dicts = [dict(item) for item in texts_db]
    # print(list_of_text_dicts)
    return list_of_text_dicts


### STATS CRUDS ###############################################################

def save_stats(text_id: int, errors: int, time: int, stats_list: list, user_id: int, db: Session):
    try:
        # db_text = db.query(Text).get(text_id)
        # db_text = db.query(Text).join(Chapter).join(Book).filter(Book.user_id == user_id).get(text_id)
        db_text = db.query(Text).join(Chapter).join(Book).filter(Book.user_id == user_id).filter(Text.id == text_id).first()
        # print(dictify_object(db_text))
        if db_text is not None:
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
