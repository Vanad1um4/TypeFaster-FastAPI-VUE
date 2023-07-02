import uvicorn
import httpx

from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

import crud
import utils

from secrets import APP_IP, APP_PORT
from secrets import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
from secrets import SESSION_SECRET_KEY, SESSION_EXPIRATION_TIME_HOURS

from schemas import Options, Book, BookTitle, BookText, StatsReturn
from models import Base, engine, SessionLocal
from const import default_user_data


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
    user_id = utils.get_user_id(request, db)
    user_data = default_user_data  # so there's no errors frontend-side if there's no user authed

    if user_id:
        user_data['authenticated'] = True
        user_data.update(crud.get_user_profile(user_id, db))

    return user_data


@app.put('/api/user/', status_code=status.HTTP_204_NO_CONTENT, tags=['User'])
async def set_options(options: Options, request: Request, db: Session = Depends(get_db)):
    user_id = utils.get_user_id(request, db)
    crud.set_user_options(options, user_id, db)


### BOOKS ROUTES ##############################################################

@app.post('/api/books/{book_id}/', tags=['Books'])
async def create_a_book(book_id: int, book_text: BookText, request: Request, db: Session = Depends(get_db)):
    user_id = utils.get_user_id(request, db)
    list_of_texts = utils.texts_slice(book_text.text)
    list_of_text_dicts = utils.prep_texts_calc_stats(list_of_texts)
    res = crud.create_texts(book_id, user_id, list_of_text_dicts, db)

    if res:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The texts haven't been created for some reason")


@app.post('/api/books/', tags=['Books'])
async def create_a_book(book: Book, request: Request, db: Session = Depends(get_db)):
    user_id = utils.get_user_id(request, db)
    db_book = crud.get_book_by_title(book.title, user_id, db)

    if db_book:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Book with this name already exists")
    created_book = crud.create_book(book.title, user_id, db)

    if not created_book:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The book hasn't been created for some reason")

    created_book_id = created_book.id
    list_of_texts = utils.texts_slice(book.text)
    list_of_text_dicts = utils.prep_texts_calc_stats(list_of_texts)
    res = crud.create_texts(created_book_id, user_id, list_of_text_dicts, db)

    if res:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The texts haven't been created for some reason")


@app.get('/api/books/', status_code=status.HTTP_200_OK, tags=['Books'])
async def get_all_books(request: Request, db: Session = Depends(get_db)):
    user_id = utils.get_user_id(request, db)
    db_books = crud.get_all_books(user_id, db)

    if db_books is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There's no books")

    return db_books


@app.get('/api/books/{book_id}/', status_code=status.HTTP_200_OK, tags=['Books'])
async def get_stats_of_a_book(book_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = utils.get_user_id(request, db)
    db_book = crud.get_book_by_id(book_id, user_id, db)

    if db_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There's no book with such an id")
    else:
        stats = utils.text_stats_prep_for_library(book_id, user_id, db)

    return stats


@app.put('/api/books/{book_id}/', tags=['Books'])
async def rename_a_book(book_id: int, book: BookTitle, request: Request, db: Session = Depends(get_db)):
    user_id = utils.get_user_id(request, db)
    db_book = crud.get_book_by_id(book_id, user_id, db)

    if db_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There's no book with this id")

    res = crud.rename_book(book_id, book.title, user_id, db)

    if res:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The text hasn't been renamed for some reason")


@app.delete('/api/books/{book_id}/', tags=['Books'])
async def delete_a_book_by_id(book_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = utils.get_user_id(request, db)
    db_book = crud.get_book_by_id(book_id, user_id, db)

    if db_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There's no book with this id")

    res = crud.delete_book_by_id(book_id, user_id, db)

    if res:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something's went wrong...")


### TEXTS ROUTES ##############################################################

@app.get('/api/texts/{text_id}/initiate/', status_code=status.HTTP_200_OK, tags=['Texts'])
async def init_get_texts_for_typing(text_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = utils.get_user_id(request, db)
    prepped_dict = utils.init_text_stats_prep_for_typing(text_id, user_id, db)

    return JSONResponse(content=prepped_dict)


@app.get('/api/texts/{text_id}/advance/', status_code=status.HTTP_200_OK, tags=['Texts'])
async def get_texts_to_continue_typing(text_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = utils.get_user_id(request, db)
    texts_dict = utils.prep_next_batch_of_texts_for_typing(text_id, user_id, db)

    return JSONResponse(content={'texts': texts_dict})


### RETURN STATS ##############################################################

@app.post('/api/stats/{text_id}/', tags=['Stats'])
async def return_stats(text_id: int, stats: StatsReturn, request: Request, db: Session = Depends(get_db)):
    user_id = utils.get_user_id(request, db)
    res = crud.save_stats(text_id, stats.dict()['args']['errors'], stats.dict()['args']['time'], stats.dict()['stats_list'], user_id, db)

    if res:
        return JSONResponse(status_code=status.HTTP_200_OK, content={'detail': 'Stats were saved successfully'})

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something's went wrong...")


### SITE ROUTES ###############################################################

app.mount('/', StaticFiles(directory='static', html=True))


@app.get('/', response_class=FileResponse, tags=['Site'])
async def show_homepage():
    return FileResponse('static/index.html')


if __name__ == "__main__":
    uvicorn.run(app, host=f"{APP_IP}", port=APP_PORT)
