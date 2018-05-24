"""locallibrary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path

from catalog import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^books/$', views.BookListView.as_view(), name="books"),
    url(r'^book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name="book-detail"),
    url(r'^authors/$', views.AuthorListView.as_view(), name="authors"),
    url(r'^author/(?P<pk>\d+)$', views.AuthorDetailView.as_view(), name="author-detail"),
]

urlpatterns += [
    path("mybooks/", views.LoanedBooksByUserListView.as_view(), name="my-borrowed"),
    path("allbooks/", views.LoanedAllBooksListView.as_view(), name="all-borrowed"),
]

urlpatterns += [
    url(r"^book/(?P<pk>[-\w]+)/renew/$", views.renew_book_librarian, name="renew-book-librarian"),
]

urlpatterns += [
    path("author/create/", views.AuthorCreate.as_view(), name="author_create"),
    path("author/<int:pk>/update", views.AuthorUpdate.as_view(), name="author_update"),
    path("author/<int:pk>/delete", views.AuthorDelete.as_view(), name="author_delete"),
    path("book/create/", views.BookCreate.as_view(), name="book_create"),
]

