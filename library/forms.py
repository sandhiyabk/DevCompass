import datetime

from django import forms

from .models import Author, Book


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ["full_name", "email", "country"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Full Name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email Address"}),
            "country": forms.TextInput(attrs={"placeholder": "Country"}),
        }

    def clean_full_name(self):
        name = self.cleaned_data.get("full_name", "").strip()
        if not name:
            raise forms.ValidationError("Author name is required.")
        return name


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "isbn", "publication_year", "category", "available_copies", "author"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Book Title"}),
            "isbn": forms.TextInput(attrs={"placeholder": "ISBN (13 digits)"}),
            "publication_year": forms.NumberInput(attrs={"placeholder": "Publication Year"}),
            "available_copies": forms.NumberInput(attrs={"min": "0"}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("Book title is required.")
        return title

    def clean_publication_year(self):
        year = self.cleaned_data.get("publication_year")
        if year and year > datetime.date.today().year:
            raise forms.ValidationError("Publication year cannot be in the future.")
        return year

    def clean_available_copies(self):
        copies = self.cleaned_data.get("available_copies")
        if copies is not None and copies < 0:
            raise forms.ValidationError("Available copies cannot be negative.")
        return copies
