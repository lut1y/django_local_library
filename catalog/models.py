from datetime import date
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse  # используется для генерации url "переворачиванием" url паттерна
import uuid  # Требуется для уникального экземпляра книги


# Create your models here.

class Genre(models.Model):
    """
    Модель представляет жанр книги (т.е. Научная фантастика, фантастика)
    """
    name = models.CharField(max_length=200, help_text="Введите жанр книги "
                                                      "(т.е. Научная фантастика, Французская поэзия)")

    def __str__(self):
        """
        Строка представляет объект модели (в админке)
        """
        return self.name


class Language(models.Model):
    """
    Модель представляет язык (Английский, Французский, Японский и т.д.)
    """
    name = models.CharField(max_length=200,
                            help_text="Введите язык, на котором написана книга")

    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Модель представляет книгу (а не ее копию)
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey("Author", on_delete=models.SET_NULL, null=True)
    # Используется Внешний ключ, потому что книга имеет только одного автора,
    # но автор может иметь несколько книг
    summary = models.TextField(max_length=1000, help_text="Введите краткое содержание книги")
    isbn = models.CharField("ISBN", max_length=13,
                            help_text="13 символов <a href=\"www.isbn-international.org/content/"
                                      "what-isbn\">ISBN номера</a>")
    genre = models.ManyToManyField(Genre, help_text="Выберите жанр для этой книги")
    # Многие-ко-многим используется, потому что жанр может содержать много книг и книги
    # могут содержать несколько жанров
    language = models.ForeignKey("Language", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """
        Строка представляет объект модели
        """
        return self.title

    def get_absolute_url(self):
        """
        Возвращает url для доступа к конкретному экремпляру книги
        """
        return reverse("book-detail", args=[str(self.id)])

    def display_genre(self):
        """
        Создается строка для Жанра. Она требуется для отображения жанра в Админке.
        """
        return ", ".join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = "Genre"


class BookInstance(models.Model):
    """
    Модель представляет определенную копию книги (которая может найдена в библиотеке)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Уникальный ID для конкретной книги во всей библиотеке")
    book = models.ForeignKey("Book", on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),  # на ремонте
        ('o', 'On loan'),  # в займы
        ('a', 'Available'),  # доступна
        ('r', 'Reserved'),  # зарежервирована
        # d - техническое обслуживание
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='d',
                              help_text="Статус книги")
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),) # Разрешение

    def __str__(self):
        return "{0} ({1})".format(self.id, self.book.title)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False


class Author(models.Model):
    """
    Модель представляет автора
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField("Died", null=True, blank=True)

    def get_absolute_url(self):
        return reverse("author-detail", args=[str(self.id)])

    def __str__(self):
        return "{0}, {1}".format(self.last_name, self.first_name)

    class Meta:
        ordering = ["last_name"]
