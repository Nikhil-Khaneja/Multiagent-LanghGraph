print("✅ RUNNING server/api.py VERSION = 2026-02-10 A")

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .schemas import Book, BookCreate, BookUpdate
from .storage import list_books, add_book, update_book, delete_book, delete_highest_id, search_by_title

app = FastAPI(title="HW2 Book API")

# CORS (safe for local homework)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend
app.mount("/web", StaticFiles(directory="webapp"), name="webapp")

@app.get("/", include_in_schema=False)
def home():
    return FileResponse("webapp/index.html")

# ---- API ----

@app.get("/api/books", response_model=list[Book])
def api_list_books():
    return list_books()

@app.post("/api/books", response_model=Book)
def api_add_book(payload: BookCreate):
    return add_book(payload)

@app.put("/api/books/{book_id}", response_model=Book)
def api_update_book(book_id: int, payload: BookUpdate):
    updated = update_book(book_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated

@app.delete("/api/books/{book_id}")
def api_delete_book(book_id: int):
    ok = delete_book(book_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"deleted": book_id}

@app.delete("/api/books/delete/highest")
def api_delete_highest():
    deleted = delete_highest_id()
    if not deleted:
        raise HTTPException(status_code=404, detail="No books to delete")
    return {"deleted": deleted}

@app.get("/api/books/search", response_model=list[Book])
def api_search(title: str = Query(..., min_length=1)):
    return search_by_title(title)
