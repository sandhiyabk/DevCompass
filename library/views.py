from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AuthorForm, BookForm
from .models import Author, Book


def _is_htmx(request):
    return request.headers.get("HX-Request") == "true"



def home(request):
    total_books = Book.objects.count()
    total_authors = Author.objects.count()
    recent_books = Book.objects.select_related("author").order_by("-created_at")[:5]
    return render(request, "library/home.html", {
        "total_books": total_books,
        "total_authors": total_authors,
        "recent_books": recent_books,
    })


# ── Author Views ──────────────────────────────────────────

def author_list(request):
    query = request.GET.get("q", "").strip()
    authors = Author.objects.all()
    if query:
        authors = authors.filter(full_name__icontains=query)
    return render(request, "library/author_list.html", {
        "authors": authors,
        "query": query,
    })


def author_detail(request, pk):
    author = get_object_or_404(Author.objects.prefetch_related("books"), pk=pk)
    return render(request, "library/author_detail.html", {"author": author})


def author_create(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            if _is_htmx(request):
                return render(request, "library/partials/author_row.html", {"author": author})
            return redirect("library:author_detail", pk=author.pk)
    else:
        form = AuthorForm()

    if _is_htmx(request):
        return render(request, "library/partials/author_form.html", {"form": form})
    return render(request, "library/author_form.html", {"form": form, "editing": False})


def author_edit(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == "POST":
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            author = form.save()
            if _is_htmx(request):
                return render(request, "library/partials/author_row.html", {"author": author})
            return redirect("library:author_detail", pk=author.pk)
    else:
        form = AuthorForm(instance=author)

    if _is_htmx(request):
        return render(request, "library/partials/author_form.html", {"form": form, "author": author})
    return render(request, "library/author_form.html", {
        "form": form,
        "author": author,
        "editing": True,
    })


def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == "POST":
        author.delete()
        if _is_htmx(request):
            return HttpResponse("")
        return redirect("library:author_list")
    return render(request, "library/author_confirm_delete.html", {"author": author})


# ── Book Views ────────────────────────────────────────────

BOOK_SORT_FIELDS = {
    "title": "title",
    "year": "publication_year",
    "author": "author__full_name",
}


def book_list(request):
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "")
    books = Book.objects.select_related("author").all()

    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__full_name__icontains=query)
        )

    sort_field = BOOK_SORT_FIELDS.get(sort)
    if sort_field:
        books = books.order_by(sort_field)

    return render(request, "library/book_list.html", {
        "books": books,
        "query": query,
        "current_sort": sort,
    })


def book_detail(request, pk):
    book = get_object_or_404(Book.objects.select_related("author"), pk=pk)
    return render(request, "library/book_detail.html", {"book": book})


def book_create(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            if _is_htmx(request):
                return render(request, "library/partials/book_row.html", {"book": book})
            return redirect("library:book_detail", pk=book.pk)
    else:
        form = BookForm()

    if _is_htmx(request):
        return render(request, "library/partials/book_form.html", {"form": form})
    return render(request, "library/book_form.html", {"form": form, "editing": False})


def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            if _is_htmx(request):
                return render(request, "library/partials/book_row.html", {"book": book})
            return redirect("library:book_detail", pk=book.pk)
    else:
        form = BookForm(instance=book)

    if _is_htmx(request):
        return render(request, "library/partials/book_form.html", {"form": form, "book": book})
    return render(request, "library/book_form.html", {
        "form": form,
        "book": book,
        "editing": True,
    })


def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.delete()
        if _is_htmx(request):
            return HttpResponse("")
        return redirect("library:book_list")
    return render(request, "library/book_confirm_delete.html", {"book": book})
