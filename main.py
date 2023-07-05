import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware, db

from schema import Book as SchemaBook
from schema import Author as SchemaAuthor

from models import Book as ModelBook
from models import Author as ModelAuthor

import os
from dotenv import load_dotenv

load_dotenv('.env')

app = FastAPI()

# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])


@app.get("/")
async def root():
    return {"message": "hello world"}


@app.post('/book/', response_model=SchemaBook, summary="Add a book")
async def book(book: SchemaBook):
    db_book = ModelBook(title=book.title, rating=book.rating, author_id=book.author_id)
    db.session.add(db_book)
    db.session.commit()
    return db_book


@app.get('/book/', summary="Show all books", )
async def book():
    book = db.session.query(ModelBook).all()
    return book


@app.post('/author/', response_model=SchemaAuthor, summary="Add an author")
async def author(author: SchemaAuthor):
    db_author = ModelAuthor(name=author.name, age=author.age)
    db.session.add(db_author)
    db.session.commit()
    return db_author


@app.post('/author/delete/{author_id}', summary="Delete an author")
async def remove_author(author_id):
    db_author = db.session.query(ModelAuthor).filter_by(id=author_id).one()
    db.session.delete(db_author)
    db.session.commit()
    return 200


@app.get('/author/', summary="Show all authors", )
async def author():
    author = db.session.query(ModelAuthor).all()
    return author


@app.patch("/author/update/{author_id}", response_model=SchemaAuthor)
def update_author(author_id: int, author_to_change: SchemaAuthor):
    db_author = db.session.get(ModelAuthor, author_id)
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    author_data = author_to_change.dict(exclude_unset=True)
    for key, value in author_data.items():
        setattr(db_author, key, value)
    db.session.add(db_author)
    db.session.commit()
    db.session.refresh(db_author)
    return db_author


# To run locally
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
