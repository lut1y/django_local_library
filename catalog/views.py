import datetime

from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from catalog.forms import RenewBookForm
from catalog.models import Book, BookInstance, Author, Genre

@login_required
def index(request):
    """
    Функция отображения для домашней страницы
    """
    # Генерация "количеств" некоторых главных объектов
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Доступные книги (статус = 'а')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()  # Метод 'all()' применен по умолчанию.

    # del request.session["num_visits"]
    # Число посещений в отображении, как счетчик в сессии
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    # Отрисовка HTML - шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        "index.html",
        context={"num_books": num_books, "num_instances": num_instances,
                 "num_instances_available": num_instances_available, "num_authors": num_authors,
                 "num_visits": num_visits, "num_genre": Genre.objects.count()},
    )


from django.views import generic


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    # context_object_name = 'my_book_list' # ваше собственное имя переменной контекста в шаблоне
    # queryset = Book.objects.filter(title__contains='war')[:5] # Получение 5 книг, содержащих слово 'war' в заголовке
    # template_name = 'books/my_arbitrary_template_name_list.html' # Определение имени вашего шаблона и его расположения

    # def get_queryset(self):
    #     return Book.objects.filter(title__contains='war')[:5] # Получить 5 книг, содержащих 'war' в заголовке

    # def get_context_data(self, **kwargs):
    #     # В первую очередь получаем базовую реализацию контекста
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Добавляем новую переменную к контексту и иниуиализируем ее некоторым значением
    #     context['some_data'] = 'This is just some data'
    #     return context

    paginate_by = 10
    login_url = '/accounts/login/'


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    Класс, основанный на отображении списка книг взятых текущим пользователем
    """
    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 3

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact="o").order_by('due_back')


class LoanedAllBooksListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_all_user.html"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact="o").order_by("due_back")


@permission_required("catalog.can_mark_returned")
def renew_book_librarian(request, pk):
    """
    Функция отображения для обновления данных BookIntance библиотекарем
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)
    # Если запрос типа POST, тогда запускаем процесс из Form
    if request.method == "POST":

        # Создаем экземпляр формы и заполняем данными из запроса
        form = RenewBookForm(request.POST)

        # Проверка валидности данных формы
        if form.is_valid():
            # Обработка данных из form.cleaned_data
            # (здесь мы просто присваиваем их полю due_back)
            book_inst.due_back = form.cleaned_data["renewal_date"]
            book_inst.save()

            # Переход по адресу "all-borrowed"
            return HttpResponseRedirect(reverse("all-borrowed"))

    # Если это GET (или какой-либо еще), создать форму по умолчанию.
    else:
        suggest_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={"renewal_date": suggest_renewal_date, })
    return render(request, "catalog/book_renew_librarian.html", {"form": form, "bookinst": book_inst})


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = "__all__"
    initial = {"date_of_death": "05/01/2018", }
    permission_required = "catalog.can_mark_returned"


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    permission_required = "catalog.can_mark_returned"


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy("authors")
    permission_required = "catalog.can_mark_returned"


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = "__all__"
    permission_required = "catalog.can_mark_returned"
