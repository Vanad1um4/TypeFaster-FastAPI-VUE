from fastapi import FastAPI, Path, Query, HTTPException, Depends, status, Request, Response
from schemas import OptionsSet, ChapterWithTextCreate, BookName, StatsReturn, TextChapter
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from secrets import SESSION_SECRET_KEY, SESSION_EXPIRATION_TIME_HOURS
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.middleware.sessions import SessionMiddleware
from secrets import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from secrets import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
from models import Base, engine, SessionLocal
from fastapi.staticfiles import StaticFiles
from secrets import APP_IP, APP_PORT
from starlette.config import Config
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Any
import uvicorn
import logic
import httpx
import crud
import json
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    max_age=SESSION_EXPIRATION_TIME_HOURS * 60 * 60,
    session_cookie="session",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


### GOOGLE AUTH ROUTES ########################################################
# TODO: To be returned upon domain purcahse...

# config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
# oauth_config = Config(environ=config_data)
# oauth = OAuth(oauth_config)
# oauth.register(
#     name='google',
#     server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
#     client_kwargs={
#         'scope': 'openid email profile',
#         'prompt': 'select_account',  # force to select account
#     }
# )


# @app.route('/login')
# async def login(request: Request):
#     redirect_uri = request.url_for('auth')
#     return await oauth.google.authorize_redirect(request, redirect_uri)


# @app.route('/auth')
# async def auth(request: Request):
#     try:
#         access_token = await oauth.google.authorize_access_token(request)
#         # print(f'{access_token = }')
#     except OAuthError:
#         return RedirectResponse(url='/')
#     user_data = access_token['userinfo']
#     request.session['user'] = user_data
#     return RedirectResponse(url='/')


### GITHUB AUTH ROUTES ########################################################

@app.get('/github_login')
async def login():
    return RedirectResponse(f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}')


@app.get('/github_return')
async def return_from_github(code: str, request: Request):
    params = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code
    }
    headers = {'Accept': 'application/json'}

    async with httpx.AsyncClient() as client:
        response = await client.post(url='https://github.com/login/oauth/access_token', params=params, headers=headers)

    response_json = response.json()
    access_token = response_json['access_token']

    async with httpx.AsyncClient() as client:
        headers.update({'Authorization': f'Bearer {access_token}'})
        response = await client.get('https://api.github.com/user', headers=headers)

    response_json = response.json()
    request.session['user'] = {'email': response_json['email']}

    return RedirectResponse(url='/')


@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


### USER ROUTES ###############################################################

@app.get('/api/user/', tags=['User'])
async def get_user(request: Request, db: Session = Depends(get_db)):
    user_id = logic.get_user_id(request, db)
    user_data = {
        'authenticated': False,
        'dark_mode': True,
        'window_width': 1000,
        'show_stats_bar': False,
        'show_progressbar': False,
        'show_error_message': False
    }

    if user_id:
        user_data['authenticated'] = True
        user_data.update(crud.get_user_profile(db, user_id))

    return user_data


@app.put('/api/user/', status_code=status.HTTP_204_NO_CONTENT, tags=['User'])
async def set_options(options: OptionsSet, request: Request, db: Session = Depends(get_db)):
    user_id = logic.get_user_id(request, db)
    crud.set_user_options(db, options, user_id)


### BOOKS ROUTES ##############################################################

@app.post('/api/books/', status_code=status.HTTP_204_NO_CONTENT, tags=['Books'])
async def create_a_book(book: BookName, request: Request, db: Session = Depends(get_db)):
    user_id = logic.get_user_id(request, db)
    db_book = crud.get_book_by_name(book.name, user_id, db)
    if db_book:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Book with this name already exists")
    crud.create_book(book.name, user_id, db)


@app.get('/api/books/', status_code=status.HTTP_200_OK, tags=['Books'])
async def show_all_books(request: Request, db: Session = Depends(get_db)):
    user_id = logic.get_user_id(request, db)
    db_books = crud.get_all_books(user_id, db)
    # print(db_books)
    if db_books is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There's no books")
    return db_books


@app.put('/api/books/{book_id}/', status_code=status.HTTP_204_NO_CONTENT, tags=['Books'])
async def rename_a_book(book_id: int, book: BookName, request: Request, db: Session = Depends(get_db)):
    user_id = logic.get_user_id(request, db)
    db_book = crud.get_book_by_id(book_id, user_id, db)
    if db_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There's no book with this id")
    crud.rename_book(book_id, book.name, user_id, db)


@app.delete('/api/books/{book_id}/', tags=['Books'])
async def delete_a_book_by_id(book_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = logic.get_user_id(request, db)
    db_book = crud.get_book_by_id(book_id, user_id, db)
    if db_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There's no book with this id")
    res = crud.delete_book_by_id(book_id, user_id, db)
    if res is True:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    if res is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something's went wrong...")


### CHAPTER ROUTES ############################################################

@app.post('/api/chapters/', tags=['Chapters'])
async def create_a_chapter(input_values: ChapterWithTextCreate, request: Request, db: Session = Depends(get_db)):
    user_id = logic.get_user_id(request, db)
    texts_list = logic.texts_slice(input_values.text)
    texts_dicts = logic.prep_texts_with_stats(texts_list)
    chapter_id = crud.create_chapter(input_values.book_id, input_values.chapter_name, user_id, db)
    res = crud.create_texts(chapter_id, texts_dicts, db)
    if res is True:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    if res is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something's went wrong...")


@app.get('/api/chapters/{book_id}/', status_code=status.HTTP_200_OK, tags=['Chapters'])
async def get_chapters_by_book_id(book_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = logic.get_user_id(request, db)
    chapters = logic.prep_chapters_for_library_display(book_id, user_id, db)
    return JSONResponse(content={'chapters': chapters})


@app.delete("/api/chapters/{chapter_id}/", status_code=status.HTTP_204_NO_CONTENT, tags=['Chapters'])
async def delete_chapter_by_id(chapter_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = logic.get_user_id(request, db)
    res = crud.delete_chapter_by_id(chapter_id, user_id, db)
    if res is True:
        return {'detail': 'Successfully deleted'}
    if res is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something's went wrong...")


### TEXTS ROUTES ##############################################################

# @app.get('/api/texts/', tags=['Texts'])  # Debug route.
# async def get_all_texts(db: Session = Depends(get_db)):
#     db_texts = crud.get_all_texts(db)
#     if db_texts is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There are no texts")
#     return db_texts


@app.get('/api/texts/{chapter_id}/{text_id}/', status_code=status.HTTP_200_OK, tags=['Texts'])
async def send_next_batch_of_texts(chapter_id: int, text_id: int, request: Request,  db: Session = Depends(get_db)):
    user_id = logic.get_user_id(request, db)
    texts_dict = logic.prep_next_batch_of_texts_for_typing(chapter_id, text_id, user_id, db)
    return JSONResponse(content={'texts': texts_dict})


@app.get('/api/texts/{chapter_id}/', status_code=status.HTTP_200_OK, tags=['Texts'])
async def return_texts_selected_by_chapter_id(chapter_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = logic.get_user_id(request, db)
    chapter_dict, texts_dict = logic.prep_texts_and_a_chapter_for_typing(chapter_id, user_id, db)
    return JSONResponse(content={'chapter': chapter_dict, 'texts': texts_dict})


### RETURN STATS ##############################################################

@app.post('/api/stats/{text_id}/', status_code=status.HTTP_200_OK, tags=['Stats'])
async def return_stats(text_id: int, stats: StatsReturn, request: Request, db: Session = Depends(get_db)):
    user_id = logic.get_user_id(request, db)
    res = crud.save_stats(text_id, stats.dict()['args']['errors'], stats.dict()['args']['time'], stats.dict()['stats'], user_id, db)
    if res is True:
        return JSONResponse(status_code=status.HTTP_200_OK, content={'detail': 'Stats were saved successfully'})
    if res is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something's went wrong...")


### SITE ROUTES ###############################################################

app.mount('/', StaticFiles(directory='static', html=True))


@app.get('/', response_class=FileResponse, tags=['Site'])
async def show_homepage():
    return FileResponse('static/index.html')


if __name__ == "__main__":
    uvicorn.run(app, host=f"{APP_IP}", port=APP_PORT)
