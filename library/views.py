from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Book, Profile, Collection, BookLending, AccessRequest, Review, Notification
from .forms import BookForm, ProfileForm, CollectionForm, ReviewForm
from django.contrib.auth.models import User, Group
from django.http import HttpResponseBadRequest
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)


RECENT_BOOKS_AMOUNT = 30

# TODO: Add email notifications for overdue books
# TODO: Add revision history for book edits
# TODO: Add recycle bin feature for deleted books

def index(request):
    """
    Main page view - displays all books in a grid layout
    """
    # Automatically add the user to the "Patron" group if logged in and not already a member
    if request.user.is_authenticated and not request.user.groups.filter(name='Patron').exists():
        request.user.groups.add(Group.objects.get_or_create(name='Patron')[0])
    
    # Get all books
    books = Book.objects.all()
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    # Handle status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        books = books.filter(status=status_filter)
    
    # Get total book count
    total_books_count = books.count()
    
    # Get the most recently added books for the carousel
    recent_books = Book.objects.order_by('-created_at')[:RECENT_BOOKS_AMOUNT]
    
    # Pagination - 54 books per page (fills a 6x9 grid)
    paginator = Paginator(books, 54)  # Show 54 books per page (6 columns x 9 rows)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    
    # Get status choices for the filter dropdown
    status_choices = Book.AVAILABILITY_CHOICES
    
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user = request.user, is_read=False).count()

    return render(request, 'library/index.html', {
        'books': books,
        'recent_books': recent_books,
        'status_choices': status_choices,
        'search_query': search_query,
        'total_books_count': total_books_count,
        'is_paginated': books.has_other_pages(),
        'page_obj': books,
        'unread_count': unread_count,
    })

def about(request):
    """
    About page view - displays information about the A22 Team
    """
    return render(request, 'library/about.html')

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    logger.warning(profile.name)
    return render(request, 'library/user/profile/index.html', {'profile': profile})

@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            # Handle the profile picture if it's in the request
            if 'profile_pic' in request.FILES:
                # Get the uploaded file
                uploaded_file = request.FILES['profile_pic']
                # Get the file extension
                ext = uploaded_file.name.split('.')[-1]
                # Create a unique filename based on user ID
                uploaded_file.name = f"{request.user.id}_{request.user.username}.{ext}"
                profile.profile_pic = uploaded_file
            profile.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'library/user/profile/edit.html', {'form': form, 'profile': profile})

# Public book views
def book_list(request):
    # Get all books
    books = Book.objects.all()
    
    # Get the most recently added books
    recent_books = Book.objects.order_by('-created_at')[:RECENT_BOOKS_AMOUNT]
    
    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    # Handle status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        books = books.filter(status=status_filter)
    
    # Get total book count before pagination
    total_books_count = books.count()
    
    # Pagination - 54 books per page (fills a 6x9 grid)
    paginator = Paginator(books, 54)  # Show 54 books per page (6 columns x 9 rows)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    
    # Get status choices for the filter dropdown
    status_choices = Book.AVAILABILITY_CHOICES
    
    context = {
        'books': books,
        'recent_books': recent_books,
        'status_choices': status_choices,
        'is_paginated': books.has_other_pages(),
        'page_obj': books,
        'total_books_count': total_books_count,
    }
    
    return render(request, 'library/book_list.html', context)

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.all()
    user_has_review = False
    if request.user.is_authenticated:
        user_has_review = reviews.filter(reviewer=request.user).exists()

    collection_count = book.collections.count()

    return render(request, 'library/book_detail.html', {'book': book, 'reviews':reviews, 'user_has_review':user_has_review, 'collection_count': collection_count})

@login_required
def book_reserve(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.status == 'available':
        book.status = 'reserved'
        book.save()
        messages.success(request, f'Book "{book.title}" has been reserved.')
    else:
        messages.error(request, f'Book "{book.title}" is not available for reservation.')
    return redirect('book_list')

@login_required
def add_book(request):
    """
    Add new book to library
    Only staff members should be able to add books - fix this later
    """
    if not request.user.groups.filter(name = 'Librarian').exists():
        return redirect('book_list')
    
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" has been added successfully!')
            return redirect('index')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form, 'action': 'Add'})

@login_required
def edit_book(request, book_id):
    """
    Edit existing book details
    Should add revision history later
    """
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" has been updated successfully!')
            return redirect('index')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form, 'action': 'Edit'})

@login_required
def delete_book(request, book_id):
    """
    Delete a book from the library
    Should add recycle bin feature later
    """
    book = get_object_or_404(Book, id=book_id)
    title = book.title
    book.delete()
    messages.success(request, f'Book "{title}" has been deleted successfully!')
    return redirect('index')

@login_required
def review_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    user = request.user
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)

        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = user
            review.book = book
            review.save()
            messages.success(request, f'Review submitted for "{book.title}!')
            return redirect('book_detail', book_id)
    else:
        form = ReviewForm()
    return render(request, 'library/book_add_review.html', {'form': form, 'action': 'Review'})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    messages.success(request, f'Review deleted successfuly!')
    
    return redirect('book_list')

# COLLECTION VIEWS
# _________________________________________________________________
@login_required
def collection_add(request):
    if request.method == "POST":
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.creator = request.user
            if request.user.groups.filter(name='Librarian').exists():
                pass 
            else:
                collection.is_private = 'public' 
            collection.save()
            # set allowed users if any were selected
            if request.user.groups.filter(name='Librarian').exists():
                collection.allowed_users.set(form.cleaned_data['allowed_users'])
            return redirect('collection_list')
    else:
        form = CollectionForm()
        if not request.user.groups.filter(name='Librarian').exists():
            form.fields['is_private'].choices = [('public', 'Public')]
            form.fields['is_private'].initial = 'public'
            form.fields['is_private'].widget.attrs['readonly'] = True
            form.fields['allowed_users'].widget.attrs['disabled'] = True
            form.fields['allowed_users'].required = False
    return render(request, 'library/collections/collection_form.html', {'form': form, 'action': 'Add'})

@login_required
def collection_edit(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.user == collection.creator or request.user.groups.filter(name='Librarian').exists():
        if request.method == "POST":
            form = CollectionForm(request.POST, instance=collection)
            if form.is_valid():
                form.save()
                return redirect('collection_list')
        else:
            form = CollectionForm(instance=collection)
            if not request.user.groups.filter(name='Librarian').exists():
                form.fields['is_private'].choices = [('public', 'Public')]
                form.fields['is_private'].initial = 'public'
                form.fields['is_private'].disabled = True
                form.fields['allowed_users'].widget.attrs['disabled'] = True
                form.fields['allowed_users'].required = False
        return render(request, 'library/collections/collection_form.html', {'form': form, 'action': 'Edit'})
    else:
        messages.error(request, "You do not have permission to edit this collection.")
        return redirect('collection_list')

@login_required
def collection_delete(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.user == collection.creator or request.user.groups.filter(name='Librarian').exists():
        if request.method == "POST":
            title = collection.title
            collection.delete()
            messages.success(request, f'Collection "{title}" has been deleted.')
            return redirect('collection_list')
    else:
        messages.error(request, "You do not have permission to delete this collection.")
        return redirect('collection_list')



def collection_list(request):
    """
    display all collections with search functionality
    search by title and description
    respect privacy settings based on user authentication
    """
    # handle search
    search_query = request.GET.get('search', '')
    
    # handle permissions
    if request.user.is_authenticated:
        collections = Collection.objects.all()
    else:
        collections = Collection.objects.filter(is_private='public')
    
    # apply search filter if query exists
    if search_query:
        collections = collections.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    return render(request, 'library/collections/collection_list.html', {
        'collections': collections,
        'search_query': search_query
    })


def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    books = collection.books.all()
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    status_filter = request.GET.get('status', '')
    if status_filter:
        books = books.filter(status=status_filter)

    # Pagination - 54 books per page (6x9 grid)
    paginator = Paginator(books, 54)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    if collection.is_private == 'private':
        # Allow access only for the creator, librarians, or allowed users
        user_has_access = (
            request.user == collection.creator or
            request.user.groups.filter(name='Librarian').exists() or
            request.user in collection.allowed_users.all()
        )
        if not user_has_access:
            messages.error(request, "You do not have permission to view this private collection.")
            return redirect('collection_list')
    
    return render(request, 'library/collections/collection_detail.html', {
        'collection': collection,
        'books': books,
        'search_query': search_query,
        'status_filter': status_filter,
        'is_paginated': books.has_other_pages(),
        'page_obj': books,
    })

@login_required
def add_book_to_collection(request, collection_pk, book_pk):
    if book_pk == 0:
    # Redirect to book list with collection_pk as a parameter
        return redirect('book_list_with_collection', collection_pk)

    collection = get_object_or_404(Collection, pk=collection_pk)
    book = get_object_or_404(Book, pk=book_pk)
    
    # Check if book is already in a private collection
    if book.collections.filter(is_private='private').exists():
        messages.error(request, "Book is already in a private collection.")
        return redirect('collection_detail', pk=collection_pk)
    
    # Remove book from all other collections 
    if collection.is_private == 'private':
        for other_collection in book.collections.all():
            if other_collection != collection:
                other_collection.books.remove(book)
    
    collection.books.add(book)
    messages.success(request, f'Book added to collection "{collection.title}"')
    return redirect('collection_detail', pk=collection_pk)



@login_required
def book_list_with_collection(request, collection_pk):
    books = Book.objects.all()
    collection = get_object_or_404(Collection, pk=collection_pk)
    context = {
        'books': books,
        'collection_pk': collection_pk,
        'collection': collection,
    }
    return render(request, 'library/collections/book_list_with_collection.html', context)


@login_required
def remove_book_from_collection(request, collection_pk, book_pk):
    collection = get_object_or_404(Collection, pk=collection_pk)
    book = get_object_or_404(Book, pk=book_pk)
    collection.books.remove(book)
    messages.success(request, f'Book removed from collection "{collection.title}"')
    return redirect('collection_detail', pk=collection_pk)

# BOOK REQUEST

@login_required
def my_books(request):
    # show what books the user has checked out
    # and their borrowing history
    
    # get their current checkouts
    active_lendings = BookLending.objects.filter(
        borrower=request.user,
        status__in=['active', 'overdue']
    ).select_related('book')
    
    pending_requests = BookLending.objects.filter(
        borrower = request.user,
        status__in = ['pending']
    ).select_related('book')
    # see if any books are overdue
    for lending in active_lendings:
        lending.is_overdue()
    
    # get books they've returned before
    lending_history = BookLending.objects.filter(
        borrower=request.user,
        status__in=['returned']
    ).select_related('book')
    
    return render(request, 'library/my_books.html', {
        'active_lendings': active_lendings,
        'lending_history': lending_history,
        'pending_requests': pending_requests,
    })


@login_required
def return_book(request, lending_id):
    # handle returning a borrowed book
    # lending_id tells us which checkout to process
    lending = get_object_or_404(BookLending, id=lending_id, borrower=request.user)
    
    if request.method == 'POST':
        # mark it as returned and update the book status
        lending.return_book()
        messages.success(request, f'Successfully returned "{lending.book.title}"')
        return redirect('my_books')
    
    return HttpResponseBadRequest('Invalid request method')

@login_required
def request_to_borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if book.status != 'available':
        messages.error(request, f'The book "{book.title}" is not available for borrowing.')
        return redirect('book_detail', pk=pk)

    # Check if there's already a pending request for this book by the user
    existing_request = BookLending.objects.filter(book=book, borrower=request.user, status='pending').exists()
    if existing_request:
        messages.info(request, f'You have already requested to borrow "{book.title}".')
        return redirect('book_detail', pk=pk)

    # Create a new borrowing request
    BookLending.objects.create(book=book, borrower=request.user)
    book.status = 'reserved'
    book.save()
    messages.success(request, f'Your request to borrow "{book.title}" has been submitted.')
    return redirect('book_detail', pk=pk)


@login_required
def approve_borrowing_request(request, pk):
    if request.user.groups.filter(name='Librarian').exists():
        borrowing_request = get_object_or_404(BookLending, pk=pk)
        
        # Approve the borrowing request
        borrowing_request.approve_lending()
        
        # Create a notification for the user
        Notification.objects.create(
            user=borrowing_request.borrower,
            message=f'Your request to borrow "{borrowing_request.book.title}" has been approved.'
        )
        logger.info(f"Notification created for {borrowing_request.borrower.username}: Approved '{borrowing_request.book.title}'")
        messages.success(request, f'Borrowing approved for "{borrowing_request.book.title}".')
    else:
        messages.error(request, "You do not have permission to approve borrowing requests.")
    
    return redirect('access_requests')

@login_required
def deny_borrowing_request(request, pk):
    if request.user.groups.filter(name='Librarian').exists():
        borrowing_request = get_object_or_404(BookLending, pk=pk)
        
        # Deny the borrowing request
        borrowing_request.deny_lending()
        
        # Create a notification for the user
        Notification.objects.create(
            user=borrowing_request.borrower,
            message=f'Your request to borrow "{borrowing_request.book.title}" has been denied.'
        )
        
        messages.success(request, f'Borrowing denied for "{borrowing_request.book.title}".')
    else:
        messages.error(request, "You do not have permission to deny borrowing requests.")
    
    return redirect('access_requests')

@login_required
def cancel_borrowing_request(request, pk):
    borrowing_request = get_object_or_404(BookLending, pk=pk, borrower=request.user)

    if borrowing_request.status == 'pending':
        borrowing_request.deny_lending()
        messages.success(request, f'Your request to borrow "{borrowing_request.book.title}" has been canceled.')
    else:
        messages.error(request, "You can only cancel pending requests.")

    return redirect('my_books')

@login_required
def request_access_to_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)

    # Check if the user already has access or is the creator
    if request.user == collection.creator or request.user in collection.allowed_users.all():
        messages.error(request, "You already have access to this collection.")
        return redirect('collection_list')

    # Check if the user has already requested access
    existing_request = AccessRequest.objects.filter(user=request.user, collection=collection, status='pending').exists()
    if existing_request:
        messages.info(request, "You have already requested access to this collection.")
        return redirect('collection_list')

    # Create a new access request
    AccessRequest.objects.create(user=request.user, collection=collection)
    messages.success(request, "Your access request has been submitted.")
    return redirect('collection_list')

@login_required
def access_requests_view(request):
    is_librarian = request.user.groups.filter(name='Librarian').exists()
    if is_librarian:
        # Get all pending collection access requests and book borrowing requests
        collection_requests = AccessRequest.objects.filter(status='pending')
        borrowing_requests = BookLending.objects.filter(status='pending')
        
        return render(request, 'library/access_requests.html', {
            'collection_requests': collection_requests,
            'borrowing_requests': borrowing_requests,
            'is_librarian': is_librarian,
        })
    else:
        messages.error(request, "You do not have permission to view access requests.")
        return redirect('collection_list')

# Approve/deny for private collection access requests
@login_required
def approve_request(request, pk):
    if request.user.groups.filter(name='Librarian').exists():
        access_request = get_object_or_404(AccessRequest, pk=pk)
        access_request.status = 'approved'
        access_request.collection.allowed_users.add(access_request.user)
        access_request.save()
        Notification.objects.create(
            user=access_request.user,
            message=f'Your request to access the "{access_request.collection}" collection has been approved.'
        )
        messages.success(request, f"Access approved for {access_request.user.username}.")
    else:
        messages.error(request, "You do not have permission to approve requests.")
    return redirect('access_requests')

@login_required
def deny_request(request, pk):
    if request.user.groups.filter(name='Librarian').exists():
        access_request = get_object_or_404(AccessRequest, pk=pk)
        access_request.status = 'denied'
        access_request.save()
        Notification.objects.create(
            user=access_request.user,
            message=f'Your request to access the "{access_request.collection}" collection has been denied.'
        )
        messages.success(request, f"Access denied for {access_request.user.username}.")
    else:
        messages.error(request, "You do not have permission to deny requests.")
    return redirect('access_requests')

# USER MANAGEMENT
def user_list(request):
    profiles = Profile.objects.all()

    search_query = request.GET.get('search', '')
    if search_query:
        search_filter = Q(name__icontains=search_query) | Q(user__username__icontains=search_query)
        
        if search_query.isdigit():
            search_filter |= Q(user__id=search_query)
            
        profiles = profiles.filter(search_filter)

    return render(request, 'library/user_list.html', {'profiles': profiles})

def manage_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile, created = Profile.objects.get_or_create(user=user)
    
    librarian_group, _ = Group.objects.get_or_create(name="Librarian")
    if request.method == 'POST':
        if user.groups.filter(name="Librarian").exists():
            user.groups.remove(librarian_group)
            messages.success(request, f"{user.username} has been demoted to Patron.")
        else:
            user.groups.add(librarian_group)
            messages.success(request, f"{user.username} has been promoted to Librarian.")

    return render(request, 'library/manage_user.html', {'profile': profile, 'managed_user': user})


# NOTIFICATIONS

@login_required
def notifications_view(request):
    # update notifications
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    notifications = request.user.notifications.all().order_by('-created_at')
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    return render(request, 'library/notifications/notifications.html', {'notifications': notifications})

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return redirect('notifications')

@login_required
def delete_all_read_notifications(request):
    read_notifications = Notification.objects.filter(user=request.user, is_read=True)
    read_notifications.delete()
    return redirect('notifications')