from pydantic import BaseModel


class OptionsSet(BaseModel):
    dark_mode: bool
    window_width: int
    show_stats_bar: bool
    show_progress_bar: bool
    show_error_history: bool


class BookName(BaseModel):
    name: str


class ChapterWithTextCreate(BaseModel):
    book_id: int
    chapter_name: str
    text: str


class TextChapter(BaseModel):
    chapter: str


class StatsReturn(BaseModel):
    class StatsReturnArgs(BaseModel):
        # cpm: int
        # wpm: int
        # acc: float
        # chars: int
        # words: int
        errors: int
        time: int

    # class StatsReturnSingleChar(BaseModel):
    #     time: int
    #     error: int
    #     txt: str

    args: StatsReturnArgs
    # stats: dict[str, StatsReturnSingleChar]
    stats: list[list[str, int, int]]

    # class Config:
    #     orm_mode = True
