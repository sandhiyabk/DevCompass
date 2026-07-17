import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from library.models import Author, Book
from library.forms import AuthorForm, BookForm

class AuthorModelTest(TestCase):
    def setUp(self):
        self.author_data = {
            "full_name": "Jane Austen",
            "email": "jane@example.com",
            "country": "United Kingdom"
        }
        self.author = Author.objects.create(**self.author_data)

    def test_author_str(self):
        self.assertEqual(str(self.author), "Jane Austen")

    def test_author_get_absolute_url(self):
        self.assertEqual(
            self.author.get_absolute_url(),
            reverse("library:author_detail", kwargs={"pk": self.author.pk})
        )

    def test_author_unique_email(self):
        # Creating another author with the same email should fail
        with self.assertRaises(IntegrityError):
            Author.objects.create(
                full_name="Another Jane",
                email="jane@example.com",
                country="USA"
            )


class BookModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            full_name="Leo Tolstoy",
            email="tolstoy@example.com"
        )
        self.book = Book.objects.create(
            title="War and Peace",
            isbn="1234567890123",
            publication_year=1869,
            category="fiction",
            available_copies=5,
            author=self.author
        )

    def test_book_str(self):
        self.assertEqual(str(self.book), "War and Peace")

    def test_book_get_absolute_url(self):
        self.assertEqual(
            self.book.get_absolute_url(),
            reverse("library:book_detail", kwargs={"pk": self.book.pk})
        )

    def test_book_unique_isbn(self):
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                title="Anna Karenina",
                isbn="1234567890123",  # Duplicate ISBN
                publication_year=1877,
                author=self.author
            )


class AuthorFormTest(TestCase):
    def test_author_form_valid(self):
        form_data = {
            "full_name": "Charles Dickens",
            "email": "charles@example.com",
            "country": "United Kingdom"
        }
        form = AuthorForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_author_form_invalid_blank_name(self):
        form_data = {
            "full_name": "  ",
            "email": "charles@example.com"
        }
        form = AuthorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("full_name", form.errors)

    def test_author_form_invalid_email(self):
        form_data = {
            "full_name": "Charles Dickens",
            "email": "not-an-email"
        }
        form = AuthorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class BookFormTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(
            full_name="Mark Twain",
            email="twain@example.com"
        )

    def test_book_form_valid(self):
        form_data = {
            "title": "Adventures of Huckleberry Finn",
            "isbn": "9780143105442",
            "publication_year": 1884,
            "category": "fiction",
            "available_copies": 3,
            "author": self.author.id
        }
        form = BookForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_book_form_invalid_future_year(self):
        future_year = datetime.date.today().year + 1
        form_data = {
            "title": "Future Book",
            "isbn": "9780143105442",
            "publication_year": future_year,
            "category": "fiction",
            "available_copies": 1,
            "author": self.author.id
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("publication_year", form.errors)

    def test_book_form_invalid_negative_copies(self):
        form_data = {
            "title": "Negative Copies",
            "isbn": "9780143105442",
            "publication_year": 2020,
            "category": "fiction",
            "available_copies": -5,
            "author": self.author.id
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("available_copies", form.errors)


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author1 = Author.objects.create(
            full_name="Virginia Woolf",
            email="woolf@example.com",
            country="United Kingdom"
        )
        self.author2 = Author.objects.create(
            full_name="Gabriel Garcia Marquez",
            email="gabriel@example.com",
            country="Colombia"
        )
        self.book1 = Book.objects.create(
            title="Mrs Dalloway",
            isbn="9780156628709",
            publication_year=1925,
            category="fiction",
            available_copies=2,
            author=self.author1
        )
        self.book2 = Book.objects.create(
            title="One Hundred Years of Solitude",
            isbn="9780060883287",
            publication_year=1967,
            category="fiction",
            available_copies=4,
            author=self.author2
        )

    def test_home_view(self):
        response = self.client.get(reverse("library:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/home.html")
        self.assertEqual(response.context["total_books"], 2)
        self.assertEqual(response.context["total_authors"], 2)
        self.assertEqual(len(response.context["recent_books"]), 2)

    def test_author_list_view(self):
        # Test without query
        response = self.client.get(reverse("library:author_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/author_list.html")
        self.assertEqual(len(response.context["authors"]), 2)

        # Test search match
        response = self.client.get(reverse("library:author_list") + "?q=Woolf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["authors"]), 1)
        self.assertEqual(response.context["authors"][0], self.author1)

        # Test search no match
        response = self.client.get(reverse("library:author_list") + "?q=Unknown")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["authors"]), 0)

    def test_author_detail_view(self):
        response = self.client.get(
            reverse("library:author_detail", kwargs={"pk": self.author1.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/author_detail.html")
        self.assertEqual(response.context["author"], self.author1)

        # Missing author -> 404
        response = self.client.get(
            reverse("library:author_detail", kwargs={"pk": 999})
        )
        self.assertEqual(response.status_code, 404)

    def test_author_create_view(self):
        create_url = reverse("library:author_create")
        
        # GET normal
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/author_form.html")

        # GET HTMX
        response = self.client.get(create_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/partials/author_form.html")

        # POST normal valid
        post_data = {
            "full_name": "Fyodor Dostoevsky",
            "email": "fyodor@example.com",
            "country": "Russia"
        }
        response = self.client.post(create_url, data=post_data)
        new_author = Author.objects.get(email="fyodor@example.com")
        self.assertRedirects(response, new_author.get_absolute_url())

        # POST HTMX valid
        post_data_htmx = {
            "full_name": "Albert Camus",
            "email": "albert@example.com",
            "country": "France"
        }
        response = self.client.post(create_url, data=post_data_htmx, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/partials/author_row.html")
        self.assertTrue(Author.objects.filter(email="albert@example.com").exists())

        # POST normal invalid
        response = self.client.post(create_url, data={"full_name": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/author_form.html")

        # POST HTMX invalid
        response = self.client.post(create_url, data={"full_name": ""}, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/partials/author_form.html")

    def test_author_edit_view(self):
        edit_url = reverse("library:author_edit", kwargs={"pk": self.author1.pk})
        
        # GET normal
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/author_form.html")

        # GET HTMX
        response = self.client.get(edit_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/partials/author_form.html")

        # POST normal valid
        post_data = {
            "full_name": "Virginia Woolf Edited",
            "email": "woolf@example.com",
            "country": "UK"
        }
        response = self.client.post(edit_url, data=post_data)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.full_name, "Virginia Woolf Edited")
        self.assertRedirects(response, self.author1.get_absolute_url())

        # POST HTMX valid
        post_data_htmx = {
            "full_name": "Virginia Woolf HTMX",
            "email": "woolf@example.com",
            "country": "UK"
        }
        response = self.client.post(edit_url, data=post_data_htmx, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/partials/author_row.html")
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.full_name, "Virginia Woolf HTMX")

    def test_author_delete_view(self):
        delete_url = reverse("library:author_delete", kwargs={"pk": self.author2.pk})
        
        # GET normal
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/author_confirm_delete.html")

        # POST HTMX
        response = self.client.post(delete_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "")
        self.assertFalse(Author.objects.filter(pk=self.author2.pk).exists())

        # POST normal
        author_to_delete = Author.objects.create(
            full_name="Temp Author",
            email="temp@example.com"
        )
        delete_url_normal = reverse("library:author_delete", kwargs={"pk": author_to_delete.pk})
        response = self.client.post(delete_url_normal)
        self.assertRedirects(response, reverse("library:author_list"))
        self.assertFalse(Author.objects.filter(pk=author_to_delete.pk).exists())

    def test_book_list_view(self):
        # Search
        response = self.client.get(reverse("library:book_list") + "?q=Mrs")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["books"]), 1)
        self.assertEqual(response.context["books"][0], self.book1)

        # Sorting by title
        response = self.client.get(reverse("library:book_list") + "?sort=title")
        self.assertEqual(response.status_code, 200)
        # Alphabetical: Mrs Dalloway, One Hundred Years of Solitude
        self.assertEqual(response.context["books"][0], self.book1)
        self.assertEqual(response.context["books"][1], self.book2)

        # Sorting by year
        response = self.client.get(reverse("library:book_list") + "?sort=year")
        self.assertEqual(response.status_code, 200)
        # Year order: 1925, 1967
        self.assertEqual(response.context["books"][0], self.book1)
        self.assertEqual(response.context["books"][1], self.book2)

    def test_book_detail_view(self):
        response = self.client.get(
            reverse("library:book_detail", kwargs={"pk": self.book1.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/book_detail.html")
        self.assertEqual(response.context["book"], self.book1)

        # Missing book
        response = self.client.get(
            reverse("library:book_detail", kwargs={"pk": 999})
        )
        self.assertEqual(response.status_code, 404)

    def test_book_create_view(self):
        create_url = reverse("library:book_create")
        
        # GET normal
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/book_form.html")

        # GET HTMX
        response = self.client.get(create_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/partials/book_form.html")

        # POST normal
        post_data = {
            "title": "To the Lighthouse",
            "isbn": "9780156907392",
            "publication_year": 1927,
            "category": "fiction",
            "available_copies": 3,
            "author": self.author1.id
        }
        response = self.client.post(create_url, data=post_data)
        new_book = Book.objects.get(isbn="9780156907392")
        self.assertRedirects(response, new_book.get_absolute_url())

        # POST HTMX
        post_data_htmx = {
            "title": "The Waves",
            "isbn": "9780156949606",
            "publication_year": 1931,
            "category": "fiction",
            "available_copies": 1,
            "author": self.author1.id
        }
        response = self.client.post(create_url, data=post_data_htmx, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/partials/book_row.html")
        self.assertTrue(Book.objects.filter(isbn="9780156949606").exists())

    def test_book_edit_view(self):
        edit_url = reverse("library:book_edit", kwargs={"pk": self.book1.pk})
        
        # GET normal
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/book_form.html")

        # GET HTMX
        response = self.client.get(edit_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/partials/book_form.html")

        # POST normal
        post_data = {
            "title": "Mrs Dalloway Edited",
            "isbn": "9780156628709",
            "publication_year": 1925,
            "category": "fiction",
            "available_copies": 5,
            "author": self.author1.id
        }
        response = self.client.post(edit_url, data=post_data)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "Mrs Dalloway Edited")
        self.assertEqual(self.book1.available_copies, 5)
        self.assertRedirects(response, self.book1.get_absolute_url())

        # POST HTMX
        post_data_htmx = {
            "title": "Mrs Dalloway HTMX",
            "isbn": "9780156628709",
            "publication_year": 1925,
            "category": "fiction",
            "available_copies": 6,
            "author": self.author1.id
        }
        response = self.client.post(edit_url, data=post_data_htmx, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/partials/book_row.html")
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, "Mrs Dalloway HTMX")
        self.assertEqual(self.book1.available_copies, 6)

    def test_book_delete_view(self):
        delete_url = reverse("library:book_delete", kwargs={"pk": self.book2.pk})
        
        # GET normal
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "library/book_confirm_delete.html")

        # POST HTMX
        response = self.client.post(delete_url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "")
        self.assertFalse(Book.objects.filter(pk=self.book2.pk).exists())

        # POST normal
        book_to_delete = Book.objects.create(
            title="Temp Book",
            isbn="9999999999999",
            publication_year=2000,
            author=self.author1
        )
        delete_url_normal = reverse("library:book_delete", kwargs={"pk": book_to_delete.pk})
        response = self.client.post(delete_url_normal)
        self.assertRedirects(response, reverse("library:book_list"))
        self.assertFalse(Book.objects.filter(pk=book_to_delete.pk).exists())
