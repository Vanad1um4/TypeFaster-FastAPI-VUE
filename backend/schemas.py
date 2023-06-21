from pydantic import BaseModel


class Options(BaseModel):
    dark_mode: bool
    window_width: int
    show_stats_bar: bool
    show_progress_bar: bool
    show_error_history: bool
    active_line_position: int
    gap_between_texts: int

    stats_slice_length_minutes: int
    use_n_last_minutes_for_stats: int


class Book(BaseModel):
    title: str
    text: str


class BookText(BaseModel):
    text: str


class BookTitle(BaseModel):
    title: str


class ChapterWithTextCreate(BaseModel):
    book_id: int
    chapter_name: str
    text: str


class TextChapter(BaseModel):
    chapter: str


class StatsReturn(BaseModel):
    class StatsReturnArgs(BaseModel):
        errors: int
        time: int

    args: StatsReturnArgs
    stats_list: list[list[str, int, int]]
