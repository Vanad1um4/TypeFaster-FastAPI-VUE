from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from secrets import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS


DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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
    active_line_position = Column(Integer, default=33)
    gap_between_texts = Column(Integer, default=20)

    stats_slice_length_minutes = Column(Integer, default=60)
    use_n_last_minutes_for_stats = Column(Integer, default=60)


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    title = Column(String)
    chars_n = Column(Integer)
    words_n = Column(Integer)
    errors = Column(Integer)
    time = Column(Integer)

    owner = relationship('User', foreign_keys=[user_id], viewonly=True)
    texts = relationship('Text', cascade='all,delete', backref='book')


class Text(Base):
    __tablename__ = 'texts'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id', ondelete='CASCADE'))
    text = Column(String)
    done = Column(Boolean)
    chars_n = Column(Integer)
    words_n = Column(Integer)
    errors = Column(Integer)
    time = Column(Integer)
    stats_list = Column(String)

    book_of_text = relationship('Book', foreign_keys=[book_id], viewonly=True)


# Base.metadata.drop_all(bind=engine, tables=[Book.__table__, Chapter.__table__, Text.__table__])
# Base.metadata.drop_all(bind=engine, tables=[Book.__table__, Text.__table__])
# Base.metadata.create_all(engine)
