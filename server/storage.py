from typing import List, Optional
from .schemas import Book, BookCreate, BookUpdate

_books: List[Book] = [
    Book(id=1, title="The Great Gatsby", author="F. Scott Fitzgerald"),
    Book(id=2, title="To Kill a Mockingbird", author="Harper Lee"),
    Book(id=3, title="1984", author="George Orwell"),
]

def list_books() -> List[Book]:
    return _books

def add_book(payload: BookCreate) -> Book:
    next_id = max((b.id for b in _books), default=0) + 1
    book = Book(id=next_id, title=payload.title, author=payload.author)
    _books.append(book)
    return book

def update_book(book_id: int, payload: BookUpdate) -> Optional[Book]:
    for i, b in enumerate(_books):
        if b.id == book_id:
            _books[i] = Book(id=book_id, title=payload.title, author=payload.author)
            return _books[i]
    return None

def delete_book(book_id: int) -> bool:
    for i, b in enumerate(_books):
        if b.id == book_id:
            _books.pop(i)
            return True
    return False

def delete_highest_id() -> Optional[Book]:
    if not _books:
        return None
    highest = max(_books, key=lambda b: b.id)
    delete_book(highest.id)
    return highest

def search_by_title(q: str) -> List[Book]:
    q = (q or "").strip().lower()
    if not q:
        return []
    return [b for b in _books if q in b.title.lower()]
