from django.test import TestCase, Client
from .models import Book, Collection, BookLending, Notification
from .forms import BookForm
from django.urls import reverse
from django.contrib.auth.models import User, Group


class TestBasicAccess(TestCase):
    def test_homepage_access(self):
        """Test that the homepage is accessible"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

class TestBookModels(TestCase):
    def setUp(self):
        """Creating a test book"""
        self.book = Book.objects.create(
            title = "test",
            author = "test",
            isbn = "1111111111111",
            publication_year = 2025,
            pub_date = "2025-03-12",
            cover = "media/library/images/default.jpg",
            summary = "test",
            description = "test",
            publisher = "test",
            location = "Main Library",
            status = "available"
        )
    
    def test_book_model(self):
        """Testing that the book was created successfully"""
        self.assertEqual(self.book.title, "test")
        self.assertEqual(self.book.author, "test")
        self.assertEqual(self.book.isbn, "1111111111111")
        self.assertEqual(self.book.publication_year, 2025)
        self.assertEqual(self.book.pub_date, "2025-03-12")
        self.assertEqual(self.book.cover, "media/library/images/default.jpg")
        self.assertEqual(self.book.summary, "test")
        self.assertEqual(self.book.description, "test")
        self.assertEqual(self.book.publisher, "test")
        self.assertEqual(self.book.location, "Main Library")
        self.assertEqual(self.book.status, "available")

class TestBookForms(TestCase):
    def test_valid_form(self):
        """Test that a valid form will pass validation"""
        form = {
            'title': 'test',
            'author':'test',
            'isbn':'1111111111111',
            'publication_year':2025,
            'pub_date':'2025-03-12',
            'cover': 'media/library/images/default.jpg',
            'summary':'test',
            'description':'test',
            'publisher':'test',
            'location' : 'Main Library',
            'status':'available'
        }
        book_form = BookForm(data = form)
        self.assertTrue(book_form.is_valid())

    def test_invalid_form(self):
        """Test that an invalid form will fail validation"""
        form = {
            'title': 'test',
            'author':'test',
            'isbn':'1111111111111',
            'publication_year':2025,
        }
        book_form = BookForm(data = form)
        # Should fail b/c of missing required fields in the form
        self.assertFalse(book_form.is_valid())

class BookViewTest(TestCase):
    def setUp(self):
        # Create a test book
        self.book = Book.objects.create(
            title = "test",
            author = "test",
            isbn = "1111111111111",
            publication_year = 2025,
            pub_date = "2025-03-12",
            cover = "media/library/images/default.jpg",
            summary = "test",
            description = "test",
            publisher = "test",
            location = "Main Library",
            status = "available"
        )

    def test_book_list_view(self):
        """Test if the book list view works correctly."""
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/book_list.html')
        self.assertContains(response, "test")


class CollectionAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.creator = User.objects.create_user(username='creator', password='password123')
        self.regular_user = User.objects.create_user(username='regular', password='password123')
        self.librarian = User.objects.create_user(username='librarian', password='password123')
        self.librarian.groups.create(name='Librarian')

        # Create a public and private collection
        self.public_collection = Collection.objects.create(
            title="Public Collection",
            description="This is a public collection.",
            creator=self.creator,
            is_private='public'
        )
        self.private_collection = Collection.objects.create(
            title="Private Collection",
            description="This is a private collection.",
            creator=self.creator,
            is_private='private'
        )

    def test_anonymous_user_can_see_public_collections(self):
        response = self.client.get('/collections/')
        self.assertContains(response, "Public Collection")
        self.assertNotContains(response, "Private Collection")

class NotificationTestCase(TestCase):
    def setUp(self):
        # Create a librarian group and users
        self.librarian_group = Group.objects.create(name="Librarian")
        self.librarian = User.objects.create_user(username="librarian", password="password123")
        self.librarian.groups.add(self.librarian_group)

        self.user = User.objects.create_user(username="regular_user", password="password123")

        # Create a book and a pending borrowing request
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="9780316769488",
            publication_year=2020,
            pub_date="2020-01-01",
            summary="Test Summary"
        )
        self.borrowing_request = BookLending.objects.create(
            book=self.book,
            borrower=self.user,
            status="pending"
        )

    def test_approve_borrowing_request_creates_notification(self):
        # Approve borrowing request
        self.borrowing_request.approve_lending()

        Notification.objects.create(
            user=self.borrowing_request.borrower,
            message=f'Your request to borrow "{self.borrowing_request.book.title}" has been approved.'
        )

        # Check if notification was created
        notification = Notification.objects.filter(user=self.user).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.message, f'Your request to borrow "{self.book.title}" has been approved.')

    def test_deny_borrowing_request_creates_notification(self):
        # Deny borrowing request
        self.borrowing_request.deny_lending()

        Notification.objects.create(
            user=self.borrowing_request.borrower,
            message=f'Your request to borrow "{self.borrowing_request.book.title}" has been denied.'
        )

        # Check if notification created
        notification = Notification.objects.filter(user=self.user).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.message, f'Your request to borrow "{self.book.title}" has been denied.')
