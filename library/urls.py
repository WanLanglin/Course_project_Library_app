from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.index, name="index"),

    # User profile URLS
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    
    # Authentication URLs
    path("accounts/", include("allauth.urls")),
    
    # Public book URLs
    path("catalog/", views.book_list, name="book_list"),
    path("catalog/<int:pk>/", views.book_detail, name="book_detail"),
    path("catalog/<int:pk>/reserve/", views.book_reserve, name="book_reserve"),
    path("catalog/<int:book_id>/add_review/", views.review_book, name='add_review'),
    path("catalog/<int:review_id>/delete_review", views.delete_review, name='delete_review'),
    path('add/', views.add_book, name='add_book'),
    path('edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('delete/<int:book_id>/', views.delete_book, name='delete_book'),

    # Collection URLs
    path("collection/add/", views.collection_add, name="collection_add"),
    path("collection/<int:pk>/edit/", views.collection_edit, name="collection_edit"),
    path("collection/<int:pk>/delete/", views.collection_delete, name="collection_delete"),
    path("collections/", views.collection_list, name="collection_list"),
    path("collection/<int:pk>/", views.collection_detail, name="collection_detail"),
    path("collection/<int:collection_pk>/add_book/<int:book_pk>/", views.add_book_to_collection, name="add_book_to_collection"),
    path("collection/<int:collection_pk>/remove_book/<int:book_pk>/", views.remove_book_from_collection, name="remove_book_from_collection"),
    path("catalog/collections/<int:collection_pk>/", views.book_list_with_collection, name="book_list_with_collection"),
    path('collection/<int:pk>/request-access/', views.request_access_to_collection, name='request_access_to_collection'),
    path('access-requests/', views.access_requests_view, name='access_requests'),
    path('access-requests/approve/<int:pk>/', views.approve_request, name='approve_request'),
    path('access-requests/deny/<int:pk>/', views.deny_request, name='deny_request'),
    path('users', views.user_list, name='user_list'),
    path('users/manage_user/<int:pk>/', views.manage_user, name='manage_user'),

    # Book Lending URLs
    path('my-books/', views.my_books, name='my_books'),
    path('return-book/<int:lending_id>/', views.return_book, name='return_book'),
    path('book/<int:pk>/request-borrow/', views.request_to_borrow_book, name='request_to_borrow_book'),
    path('access-requests/approve-borrow/<int:pk>/', views.approve_borrowing_request, name='approve_borrowing_request'),
    path('access-requests/deny-borrow/<int:pk>/', views.deny_borrowing_request, name='deny_borrowing_request'),
    path('my-books/cancel-request/<int:pk>/', views.cancel_borrowing_request, name='cancel_borrowing_request'),
    
    # Notification URLs
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/delete-read/', views.delete_all_read_notifications, name='delete_all_read_notifications'),


    # About page
    path('about/', views.about, name='about'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
