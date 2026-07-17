from django.db import models
from django.urls import reverse


class Author(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name_plural = "authors"

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse("library:author_detail", kwargs={"pk": self.pk})


class Book(models.Model):
    CATEGORY_CHOICES = [
        ("fiction", "Fiction"),
        ("non_fiction", "Non-Fiction"),
        ("science", "Science"),
        ("technology", "Technology"),
        ("history", "History"),
        ("biography", "Biography"),
        ("philosophy", "Philosophy"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=300)
    isbn = models.CharField(max_length=13, unique=True)
    publication_year = models.PositiveIntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    available_copies = models.PositiveIntegerField(default=1)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="books",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "books"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("library:book_detail", kwargs={"pk": self.pk})
