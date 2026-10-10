#QB 1

from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3


connection = sqlite3.connect("college.db")
cursor = connection.cursor()

query = "SELECT name, marks FROM students WHERE marks > ? ORDER BY marks DESC"
cursor.execute(query, (80,))

for row in cursor.fetchall():
  print(f"{row[0]} - {row[1]}")

connection.close()

#QB2
import sqlite3

connection = sqlite3.connect("college.db")
cursor = connection.cursor()

query = (
    "INSERT INTO students (name, course, city, marks) VALUES (?, ?, ?, ?)"
)
cursor.execute(query, ("Vikram", "BCA", "Udaipur", 67))

connection.commit()

print(f"Student added successfully. Assigned ID: {cursor.lastrowid}")
connection.close()


## Q4 B: FastAPI Endpoint
from fastapi import FastAPI

app = FastAPI()


@app.get("/hello/{name}")
def say_hello(name: str):
  return {"message": f"Hello {name}"}

 # QC2
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import sqlite3

app = FastAPI()

DB_NAME = "shop.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

class BookBase(BaseModel):
    title: str
    author: str
    price: float

class Book(BookBase):
    id: int

    class Config:
        from_attributes = True

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book: BookBase):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO books (title, author, price) VALUES (?, ?, ?)",
        (book.title, book.author, book.price)
    )
    conn.commit()
    book_id = cursor.lastrowid
    conn.close()
    return Book(id=book_id, **book.model_dump())

@app.get("/books", response_model=list[Book])
def get_books():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author, price FROM books")
    rows = cursor.fetchall()
    conn.close()
    return [Book(id=row["id"], title=row["title"], author=row["author"], price=row["price"]) for row in rows]

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author, price FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    return Book(id=row["id"], title=row["title"], author=row["author"], price=row["price"])

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: BookBase):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM books WHERE id = ?", (book_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    cursor.execute(
        "UPDATE books SET title = ?, author = ?, price = ? WHERE id = ?",
        (book.title, book.author, book.price, book_id)
    )
    conn.commit()
    conn.close()
    
    return Book(id=book_id, **book.model_dump())

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM books WHERE id = ?", (book_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    
    return None

#QC3

from fastapi import FastAPI, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_NAME = "college.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            city TEXT NOT NULL,
            marks REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/students")
def get_students(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse("list.html", {
        "request": request, 
        "students": students, 
        "total": len(students)
    })


@app.post("/students")
def create_student(
    name: str = Form(...),
    course: str = Form(...),
    city: str = Form(...),
    marks: float = Form(...)
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, course, city, marks) VALUES (?, ?, ?, ?)",
        (name, course, city, marks)
    )
    conn.commit()
    conn.close()
    
    return RedirectResponse(url="/students", status_code=status.HTTP_303_SEE_OTHER)

{{% extends "base.html" %}

{% block title %}Student List{% endblock %}

{%- for student in students %}
            <tr>
                <td>{{ student.name }}</td>
                <td>{{ student.city }}</td>
                <td>{{ student.marks }}</td>
            </tr>
            {% endfor %}}
#Why do we redirect with status 303?
'''It enforces the Post/Redirect/Get  pattern. Status 303  ensures the browser makes a subsequent GET request to /students rather than resubmitting the form data, preventing duplicate entries if the user refreshes the page.

Which extra package must be installed for Form(...) to work?
We need to  install python-multipart 
'''