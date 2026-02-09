# ========================================
# BOOK MANAGEMENT SYSTEM - BACKEND API
# Student Learning Project using FastAPI
# ========================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import Book, BookCreate, BookUpdate

# ========================================
# CREATE AND CONFIGURE APP
# ========================================

# Create FastAPI application
# FastAPI automatically generates interactive API documentation!
app = FastAPI(
    title="Book Management API",
    description="A simple REST API for managing books - Built for learning!",
    version="1.0.0"
)

# Add CORS (Cross-Origin Resource Sharing) middleware
# This allows the frontend (running on a different port) to make requests to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin (fine for learning projects)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
)

# ========================================
# DATABASE - In-memory storage
# ========================================

# This is a simple in-memory database
# In production, you would use a real database like PostgreSQL or MongoDB
books_db = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee"},
    {"id": 3, "title": "1984", "author": "George Orwell"}
]

# Counter for generating new book IDs
next_id = 4

# ========================================
# ENDPOINTS - API Routes
# ========================================

# Root endpoint - Health check
@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint - Returns welcome message"""
    return {
        "message": "Welcome to Book Management API",
        "version": "1.0.0",
        "docs": "Visit /docs for interactive documentation"
    }


# --- READ ENDPOINTS ---

@app.get("/api/books", response_model=List[Book], tags=["Books"])
async def get_all_books():
    """
    Get all books from the database.
    
    Returns:
        List[Book]: A list of all books
    """
    return books_db


@app.get("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def get_book(book_id: int):
    """
    Get a specific book by its ID.
    
    Args:
        book_id: The ID of the book to retrieve
        
    Returns:
        Book: The book with matching ID
        
    Raises:
        HTTPException: 404 if book not found
    """
    for book in books_db:
        if book["id"] == book_id:
            return book
    
    # Return 404 error if book not found
    raise HTTPException(status_code=404, detail="Book not found")


@app.get("/api/books/search/", response_model=List[Book], tags=["Books"])
async def search_books(title: str = ""):
    """
    Search for books by title (case-insensitive).
    
    Args:
        title: Search term (partial title matches work)
        
    Returns:
        List[Book]: Books matching the search term
    """
    if not title:
        return books_db
    
    # Filter books where the title contains the search term
    return [book for book in books_db if title.lower() in book["title"].lower()]


# --- CREATE ENDPOINT ---

@app.post("/api/books", response_model=Book, tags=["Books"])
async def create_book(book: BookCreate):
    """
    Create a new book.
    
    Args:
        book: BookCreate object with title and author
        
    Returns:
        Book: The newly created book with assigned ID
    """
    global next_id
    
    # Create new book object with auto-generated ID
    new_book = {
        "id": next_id,
        "title": book.title,
        "author": book.author
    }
    
    # Add to database
    books_db.append(new_book)
    
    # Increment ID counter for next book
    next_id += 1
    
    return new_book


# --- UPDATE ENDPOINT ---

@app.put("/api/books/{book_id}", response_model=Book, tags=["Books"])
async def update_book(book_id: int, book: BookUpdate):
    """
    Update an existing book.
    
    Args:
        book_id: ID of the book to update
        book: BookUpdate object with new title and/or author
        
    Returns:
        Book: The updated book
        
    Raises:
        HTTPException: 404 if book not found
    """
    for existing_book in books_db:
        if existing_book["id"] == book_id:
            # Update only provided fields
            if book.title is not None:
                existing_book["title"] = book.title
            if book.author is not None:
                existing_book["author"] = book.author
            
            return existing_book
    
    raise HTTPException(status_code=404, detail="Book not found")


# --- DELETE ENDPOINTS ---

@app.delete("/api/books/{book_id}", tags=["Books"])
async def delete_book(book_id: int):
    """
    Delete a book by ID.
    
    Args:
        book_id: ID of the book to delete
        
    Returns:
        dict: Confirmation message and deleted book data
        
    Raises:
        HTTPException: 404 if book not found
    """
    global books_db
    
    for i, book in enumerate(books_db):
        if book["id"] == book_id:
            # Remove from database
            deleted_book = books_db.pop(i)
            return {
                "message": f"Book '{deleted_book['title']}' deleted successfully",
                "book": deleted_book
            }
    
    raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/api/books/delete/highest", tags=["Books"])
async def delete_highest_id_book():
    """
    Delete the book with the highest ID.
    
    Returns:
        dict: Confirmation message and deleted book data
        
    Raises:
        HTTPException: 404 if no books exist
    """
    global books_db
    
    if not books_db:
        raise HTTPException(status_code=404, detail="No books to delete")
    
    # Find book with highest ID
    highest_id_book = max(books_db, key=lambda x: x["id"])
    
    # Remove from database
    books_db = [book for book in books_db if book["id"] != highest_id_book["id"]]
    
    return {
        "message": f"Book '{highest_id_book['title']}' deleted successfully",
        "book": highest_id_book
    }


# ========================================
# RUN THE SERVER
# ========================================

if __name__ == "__main__":
    import uvicorn
    
    # Start the server
    # Visit http://localhost:8000 to access the API
    # Visit http://localhost:8000/docs for interactive documentation
    uvicorn.run(app, host="0.0.0.0", port=8000)
