from django.contrib import admin

from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "country", "created_at")
    search_fields = ("full_name", "email")
    list_filter = ("country", "created_at")
    ordering = ("full_name",)
    readonly_fields = ("created_at",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "publication_year", "category", "available_copies")
    search_fields = ("title", "isbn", "author__full_name")
    list_filter = ("category", "publication_year", "author")
    ordering = ("title",)
    readonly_fields = ("created_at",)
    list_editable = ("available_copies",)
