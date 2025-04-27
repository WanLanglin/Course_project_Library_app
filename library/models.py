from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.utils import timezone
from django.db.models import Avg
import os

class Book(models.Model):
    # Basic book information
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(
        max_length=13,
        unique=True,
        help_text="ISBN-13 format: 13 digits (e.g., 9780316769488)",
        validators=[
            RegexValidator(
                regex='^[0-9]{13}$',
                message='ISBN must be exactly 13 digits',
                code='invalid_isbn'
            )
        ]
    )
    publication_year = models.IntegerField()
    pub_date = models.DateField()
    cover = models.ImageField(upload_to='books/covers', default="books/covers/default.jpg")
    description = models.TextField()
    
    # Additional details
    summary = models.TextField(blank=True)
    publisher = models.CharField(max_length=200)

    # Locations:
    LOCATION_CHOICES = [
        ('', '--Select a Location--'),
        ('Main Library', 'Main Library'),
        ('Work Library', 'Work Library'),
        ('Online Only', 'Online Only'),
    ]

    location = models.CharField(max_length=200, 
        choices=LOCATION_CHOICES,
        default='Main Library'
    )
    
    # Book status
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('checked_out', 'Checked Out'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Under Maintenance'),
    ]
    status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"ISBN: {self.isbn} - {self.title} by {self.author}"
    
    class Meta:
        ordering = ['isbn', 'title', 'author']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        indexes = [
            models.Index(fields=['isbn']),
        ]

class BookLending(models.Model):
    # lending info
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='lendings')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowed_books')
    checkout_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    
    # lending status
    LENDING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('overdue', 'Overdue'),
        ('returned', 'Returned'),
        ('lost', 'Lost'),
        ('denied', 'Denied'),
    ]
    status = models.CharField(
        max_length=20,
        choices=LENDING_STATUS_CHOICES,
        default='pending'
    )

    def approve_lending(self):
        # Approve the lending request
        self.status = 'active'
        self.checkout_date = timezone.now()
        self.due_date = timezone.now() + timezone.timedelta(days=14)  # Set due date (2 weeks)
        self.book.status = 'checked_out'
        self.book.save()
        self.save()
    
    def deny_lending(self):
        # Deny the lending request
        self.status = 'denied'
        self.book.status = 'available'  # Reset book status to available
        self.book.save()
        self.save()
    
    def return_book(self):
        # mark book as returned
        self.return_date = timezone.now()
        self.status = 'returned'
        self.book.status = 'available'
        self.book.save()
        self.save()
    
    def is_overdue(self):
        # check if book is overdue
        if not self.return_date and timezone.now() > self.due_date:
            if self.status != 'overdue':
                self.status = 'overdue'
                self.save()
            return True
        return False
    
    def __str__(self):
        return f"{self.book.title} - borrowed by {self.borrower.username}"
    
    class Meta:
        ordering = ['-checkout_date']
        verbose_name = 'Book Lending'
        verbose_name_plural = 'Book Lendings'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    profile_pic = models.ImageField(default='profiles/profile_pictures/default.jpg', upload_to='profiles/profile_pictures/')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
    @property
    def is_librarian(self):
        return self.user.groups.filter(name="Librarian").exists()

    def promote_to_librarian(self):
        librarian_group = Group.objects.get_or_create(name="Librarian")
        self.user.groups.add(librarian_group)

    def demote_to_patron(self):
        librarian_group = Group.objects.get_or_create(name="Librarian")
        if librarian_group:
            self.user.groups.remove(librarian_group)

class Collection(models.Model):
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    is_private = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='public')
    allowed_users = models.ManyToManyField(User, related_name='allowed_collections', blank=True)
    books = models.ManyToManyField(Book, related_name= 'collections', blank=True)

    def __str__(self):
        return f"{self.title} by {self.creator.username}"


class AccessRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')], default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} requested access to {self.collection.title}"

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)


class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()

    def __str__(self):
            return f'{self.book.name} rated {self.rating} with comment {self.comment} by {self.reviewer.username}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:20]}"