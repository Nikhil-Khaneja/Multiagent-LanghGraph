// ========================================
// BOOK MANAGEMENT SYSTEM - FRONTEND
// Student Learning Project
// ========================================

// Sample data - Initially includes 3 books
// This is an in-memory database. Data will reset when page reloads.
// For persistent data, you would use a real database!
let books = [
    { id: 1, title: "The Great Gatsby", author: "F. Scott Fitzgerald" },
    { id: 2, title: "To Kill a Mockingbird", author: "Harper Lee" },
    { id: 3, title: "1984", author: "George Orwell" }
];

let nextId = 4;

// ========================================
// INITIALIZATION - Called when page loads
// ========================================

function init() {
    setupNavigation();    // Setup tab navigation
    setupForms();         // Setup form submissions
    renderBooks();        // Display all books
    populateSelects();    // Fill dropdown menus
}

// ========================================
// NAVIGATION - Handle tab switching
// ========================================

function setupNavigation() {
    // Find all navigation buttons
    const navButtons = document.querySelectorAll('.nav-btn');
    
    // Add click listener to each button
    navButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            // Get which section to show from the button's data attribute
            const sectionId = e.target.dataset.section;
            
            // Hide all sections and remove active class from buttons
            navButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
            
            // Show the selected section and mark button as active
            e.target.classList.add('active');
            document.getElementById(sectionId).classList.add('active');

            // Refresh dropdown menus when opening update/delete sections
            if (sectionId === 'update' || sectionId === 'delete') {
                populateSelects();
            }
        });
    });
}

// ========================================
// FORMS - Handle all form submissions
// ========================================

function setupForms() {
    
    // --- ADD BOOK FORM ---
    document.getElementById('addBookForm').addEventListener('submit', (e) => {
        e.preventDefault(); // Prevent page reload
        
        // Get form values
        const title = document.getElementById('addTitle').value.trim();
        const author = document.getElementById('addAuthor').value.trim();

        // Validate input
        if (title && author) {
            // Create new book object
            books.push({
                id: nextId++,
                title: title,
                author: author
            });

            // Clear form
            document.getElementById('addBookForm').reset();
            
            // Show success message
            showSuccessMessage('Book added successfully!');
            
            // Go back to home
            goToHome();
        }
    });

    // --- UPDATE BOOK FORM ---
    document.getElementById('updateBookForm').addEventListener('submit', (e) => {
        e.preventDefault();
        
        const id = parseInt(document.getElementById('updateId').value);
        const title = document.getElementById('updateTitle').value.trim();
        const author = document.getElementById('updateAuthor').value.trim();

        // Find the book and update it
        const book = books.find(b => b.id === id);
        if (book && title && author) {
            book.title = title;
            book.author = author;
            
            // Clear form
            document.getElementById('updateBookForm').reset();
            document.getElementById('updateId').value = '';
            document.getElementById('updateTitle').value = '';
            document.getElementById('updateAuthor').value = '';
            
            showSuccessMessage('Book updated successfully!');
            goToHome();
        }
    });

    // --- DELETE BOOK FORM ---
    document.getElementById('deleteBookForm').addEventListener('submit', (e) => {
        e.preventDefault();
        
        const id = parseInt(document.getElementById('deleteId').value);

        // Find and delete the book
        const index = books.findIndex(b => b.id === id);
        if (index !== -1) {
            const bookTitle = books[index].title;
            books.splice(index, 1); // Remove from array
            
            // Clear form
            document.getElementById('deleteBookForm').reset();
            document.getElementById('deleteId').value = '';
            
            showSuccessMessage(`Book "${bookTitle}" deleted successfully!`);
            goToHome();
        }
    });

    // --- SEARCH FUNCTIONALITY ---
    // This updates as you type (not on form submit)
    document.getElementById('searchInput').addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase().trim();
        const searchResults = document.getElementById('searchResults');

        // If search box is empty, show placeholder text
        if (searchTerm === '') {
            searchResults.innerHTML = '<div class="no-books">Enter a title to search for books.</div>';
            return;
        }

        // Filter books by title (case-insensitive)
        const filteredBooks = books.filter(book => 
            book.title.toLowerCase().includes(searchTerm)
        );

        // Display results
        if (filteredBooks.length === 0) {
            searchResults.innerHTML = '<div class="no-books">No books found matching your search.</div>';
        } else {
            renderBooksToElement(filteredBooks, searchResults);
        }
    });
}

// ========================================
// RENDERING - Display books on page
// ========================================

// Render all books to home view
function renderBooks() {
    const booksList = document.getElementById('booksList');
    if (books.length === 0) {
        booksList.innerHTML = '<div class="no-books">No books available. Add a new book to get started!</div>';
    } else {
        renderBooksToElement(books, booksList);
    }
}

// Generic function to render books to any HTML element
// This prevents repeating the same code in multiple places
function renderBooksToElement(booksToRender, element) {
    element.innerHTML = booksToRender.map(book => `
        <div class="book-card">
            <div class="book-info">
                <h3>${escapeHtml(book.title)}</h3>
                <p><strong>Author:</strong> ${escapeHtml(book.author)}</p>
                <p><span class="book-id">ID: ${book.id}</span></p>
            </div>
        </div>
    `).join('');
}

// ========================================
// DROPDOWNS - Populate select menus
// ========================================

function populateSelects() {
    const updateSelect = document.getElementById('updateId');
    const deleteSelect = document.getElementById('deleteId');

    // Create option tags for each book
    const options = books.map(book => 
        `<option value="${book.id}">ID: ${book.id} - ${escapeHtml(book.title)}</option>`
    ).join('');

    // Add options to both dropdowns
    updateSelect.innerHTML = '<option value="">-- Select a book --</option>' + options;
    deleteSelect.innerHTML = '<option value="">-- Select a book --</option>' + options;

    // When user selects a book in update form, auto-fill the fields
    updateSelect.addEventListener('change', (e) => {
        const id = parseInt(e.target.value);
        const book = books.find(b => b.id === id);
        if (book) {
            // Pre-fill the form with selected book's data
            document.getElementById('updateTitle').value = book.title;
            document.getElementById('updateAuthor').value = book.author;
        } else {
            // Clear fields if no book selected
            document.getElementById('updateTitle').value = '';
            document.getElementById('updateAuthor').value = '';
        }
    });
}

// ========================================
// UI HELPERS - Show messages and navigate
// ========================================

// Show temporary success message
function showSuccessMessage(message) {
    const messageElement = document.getElementById('successMessage');
    messageElement.textContent = '✓ ' + message;
    messageElement.classList.add('show');
    
    // Hide after 3 seconds
    setTimeout(() => {
        messageElement.classList.remove('show');
    }, 3000);
}

// Navigate back to home view
function goToHome() {
    renderBooks();
    
    // Remove active class from all navigation
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
    
    // Activate home button and section
    document.querySelector('[data-section="home"]').classList.add('active');
    document.getElementById('home').classList.add('active');
}

// ========================================
// SECURITY - Prevent XSS attacks
// ========================================

// Escape HTML special characters to prevent malicious code injection
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ========================================
// START THE APP
// ========================================

// Wait for page to fully load before running JavaScript
document.addEventListener('DOMContentLoaded', init);
