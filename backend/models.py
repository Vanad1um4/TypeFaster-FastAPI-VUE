from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from secrets import DB_HOST, DB_NAME, DB_USER, DB_PASS

# SQLite
# DATABASE_URL = 'sqlite:///./db.sqlite'
# engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

# PostgreSQL
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    is_admin = Column(Boolean, default=False)
    dark_mode = Column(Boolean, default=True)
    window_width = Column(Integer, default=1000)
    show_stats_bar = Column(Boolean, default=True)
    show_progress_bar = Column(Boolean, default=True)
    show_error_history = Column(Boolean, default=True)


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    name = Column(String)
    chars_n = Column(Integer)
    words_n = Column(Integer)
    errors = Column(Integer)
    time = Column(Integer)

    owner = relationship('User', foreign_keys=[user_id], viewonly=True)
    chapters_of_book = relationship('Chapter', cascade='all,delete', backref='book')


class Chapter(Base):
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    book_id = Column(Integer, ForeignKey('books.id', ondelete='CASCADE'))
    chars_n = Column(Integer)
    words_n = Column(Integer)
    errors = Column(Integer)
    time = Column(Integer)

    book_of_chapter = relationship('Book', foreign_keys=[book_id], viewonly=True)
    texts_of_chapter = relationship('Text', cascade='all,delete', backref='chapter')


class Text(Base):
    __tablename__ = 'texts'

    id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id', ondelete='CASCADE'))
    text = Column(String)
    done = Column(Boolean)
    chars_n = Column(Integer)
    words_n = Column(Integer)
    errors = Column(Integer)
    time = Column(Integer)
    stats_list = Column(String)

    chapter_of_text = relationship('Chapter', foreign_keys=[chapter_id], viewonly=True)
