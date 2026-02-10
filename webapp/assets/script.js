const API = "/api";

let cachedBooks = [];

async function getJSON(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${res.status} ${path}`);
  return res.json();
}

async function sendJSON(path, method, body) {
  const res = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined
  });
  if (!res.ok) throw new Error(`${res.status} ${path}`);
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

function escapeHtml(text) {
  const map = { "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#039;" };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

function showSuccess(msg) {
  const el = document.getElementById("successMessage");
  el.textContent = "✓ " + msg;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 3000);
}

async function refreshBooks() {
  cachedBooks = await getJSON(`${API}/books`);
}

function renderBooks(list, targetId) {
  const el = document.getElementById(targetId);
  if (!list.length) {
    el.innerHTML = '<div class="no-books">No books available.</div>';
    return;
  }
  el.innerHTML = list.map(b => `
    <div class="book-card">
      <div class="book-info">
        <h3>${escapeHtml(b.title)}</h3>
        <p><strong>Author:</strong> ${escapeHtml(b.author)}</p>
        <p><span class="book-id">ID: ${b.id}</span></p>
      </div>
    </div>
  `).join("");
}

function fillDropdowns() {
  const updateSel = document.getElementById("updateId");
  const deleteSel = document.getElementById("deleteId");

  const opts = cachedBooks.map(b =>
    `<option value="${b.id}">ID: ${b.id} - ${escapeHtml(b.title)}</option>`
  ).join("");

  updateSel.innerHTML = '<option value="">-- Select a book --</option>' + opts;
  deleteSel.innerHTML = '<option value="">-- Select a book --</option>' + opts;

  updateSel.onchange = () => {
    const id = parseInt(updateSel.value);
    const book = cachedBooks.find(x => x.id === id);
    document.getElementById("updateTitle").value = book ? book.title : "";
    document.getElementById("updateAuthor").value = book ? book.author : "";
  };
}

async function goHome() {
  await refreshBooks();
  renderBooks(cachedBooks, "booksList");
  fillDropdowns();

  document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
  document.querySelector('[data-section="home"]').classList.add("active");
  document.getElementById("home").classList.add("active");
}

function setupNav() {
  const navButtons = document.querySelectorAll(".nav-btn");
  navButtons.forEach(btn => {
    btn.addEventListener("click", async (e) => {
      const sectionId = e.target.dataset.section;
      navButtons.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));

      e.target.classList.add("active");
      document.getElementById(sectionId).classList.add("active");

      if (sectionId === "update" || sectionId === "delete") {
        await refreshBooks();
        fillDropdowns();
      }
    });
  });
}

function setupForms() {
  // Q1 Add
  document.getElementById("addBookForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("addTitle").value.trim();
    const author = document.getElementById("addAuthor").value.trim();
    if (!title || !author) return;

    await sendJSON(`${API}/books`, "POST", { title, author });
    e.target.reset();
    showSuccess("Book added!");
    await goHome();
  });

  // Generic update
  document.getElementById("updateBookForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = parseInt(document.getElementById("updateId").value);
    const title = document.getElementById("updateTitle").value.trim();
    const author = document.getElementById("updateAuthor").value.trim();
    if (!id || !title || !author) return;

    await sendJSON(`${API}/books/${id}`, "PUT", { title, author });
    showSuccess("Book updated!");
    await goHome();
  });

  // Q2 Required: Update ID=1
  document.getElementById("presetUpdateBtn").addEventListener("click", async () => {
    await sendJSON(`${API}/books/1`, "PUT", { title: "Harry Potter", author: "J.K Rowling" });
    showSuccess('Book #1 set to "Harry Potter"');
    await goHome();
  });

  // Delete selected (optional)
  document.getElementById("deleteBookForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = parseInt(document.getElementById("deleteId").value);
    if (!id) return;

    await sendJSON(`${API}/books/${id}`, "DELETE");
    showSuccess(`Deleted book #${id}`);
    await goHome();
  });

  // Q3 Required: Delete highest
  document.getElementById("deleteMaxBtn").addEventListener("click", async () => {
    await sendJSON(`${API}/books/delete/highest`, "DELETE");
    showSuccess("Deleted highest ID book!");
    await goHome();
  });

  // Q4 Search (backend)
  document.getElementById("searchInput").addEventListener("input", async (e) => {
    const term = e.target.value.trim();
    const target = document.getElementById("searchResults");

    if (!term) {
      target.innerHTML = '<div class="no-books">Enter a title to search for books.</div>';
      return;
    }
    const results = await getJSON(`${API}/books/search?title=${encodeURIComponent(term)}`);
    renderBooks(results, "searchResults");
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  setupNav();
  setupForms();
  await goHome();
});
