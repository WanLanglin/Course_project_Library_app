from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from library.models import Book
from datetime import date, datetime, timedelta
import os
import base64
import random
import string
import requests
from django.core.files.temp import NamedTemporaryFile
from io import BytesIO
from PIL import Image

class Command(BaseCommand):
    help = 'Creates test books for development purposes'
    
    def get_book_cover(self, isbn):
        """Try to get a book cover from Open Library Covers API using ISBN"""
        # Try to get a cover image from Open Library (large size)
        url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
        response = requests.get(url)
        
        # Check if we got a real image (the API returns a 1x1 px image for missing covers)
        if response.status_code == 200:
            try:
                img = Image.open(BytesIO(response.content))
                width, height = img.size
                # If the image is very small, it's probably the placeholder
                if width <= 1 or height <= 1:
                    return None
                
                # If we got here, we have a valid image
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(response.content)
                img_temp.flush()
                return img_temp
            except:
                return None
        return None
    
    def download_random_book_cover(self):
        """Download a random book cover from a free book cover API"""
        # For random books, we'll use placeholder images from different sources
        # Picsum offers random images that can work as book covers
        width, height = 800, 1200  # Common book cover dimensions
        image_id = random.randint(1, 1000)  # Random image ID
        url = f"https://picsum.photos/id/{image_id}/{width}/{height}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(response.content)
                img_temp.flush()
                return img_temp
        except:
            pass
            
        # Fallback to a different size if the specific ID wasn't found
        try:
            url = f"https://picsum.photos/{width}/{height}"
            response = requests.get(url)
            if response.status_code == 200:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(response.content)
                img_temp.flush()
                return img_temp
        except:
            return None
            
        return None

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of test books to create (default: 100)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test books before creating new ones'
        )
        parser.add_argument(
            '--production',
            action='store_true',
            help='Use this flag when running in production environment'
        )

    def handle(self, *args, **kwargs):
        count_to_create = kwargs['count']
        clear_existing = kwargs.get('clear', False)
        is_production = kwargs.get('production', False)
        
        if clear_existing:
            if is_production:
                # In production mode with clear flag, delete ALL books
                all_books = Book.objects.all()
                count_deleted = all_books.count()
                all_books.delete()
                self.stdout.write(self.style.WARNING(f'PRODUCTION MODE: Deleted ALL {count_deleted} books from the database'))
            else:
                # In non-production mode, only clear test books (ISBN starts with '99')
                test_books = Book.objects.filter(isbn__startswith='99')
                count_deleted = test_books.count()
                test_books.delete()
                self.stdout.write(self.style.WARNING(f'Deleted {count_deleted} existing test books'))
        
        # Sample book titles, authors, and publishers for variety
        titles = [
            "The Lost City", "Midnight's Echo", "The Silent Guardian", "Echoes of Time", 
            "Whispers in the Dark", "Forgotten Dreams", "The Last Journey", "Beyond the Horizon",
            "A World Apart", "The Hidden Truth", "Shadows of the Past", "Eternal Bonds",
            "The Secret Path", "Beneath the Surface", "The Broken Promise", "Rising Dawn",
            "Fading Memories", "The Unexpected Hero", "Untold Stories", "Beyond Redemption",
            "The Perfect Lie", "Into the Unknown", "The Final Countdown", "Shattered Reality",
            "Twisted Fate", "The Missing Piece", "Abandoned Hope", "Lingering Shadows",
            "The Last Stand", "Vanishing Point", "The Awakening", "A New Beginning",
            "The Lost Treasure", "Forbidden Knowledge", "The Darkest Hour", "Forgotten Legacy",
            "The Empty Room", "Whispering Winds", "The Silent Witness", "Burning Bridges",
            "The Forgotten Child", "Hidden Passages", "The Broken Mirror", "Fading Light",
            "The Lonely Path", "Scattered Pieces", "A Distant Memory", "The Secret Door",
            "Lingering Doubts", "The Final Chapter"
        ]
        
        authors = [
            "Emma Mitchell", "James Anderson", "Sophia Roberts", "Liam Walker", 
            "Olivia Johnson", "Noah Williams", "Isabella Brown", "William Jones",
            "Ava Davis", "Benjamin Miller", "Mia Wilson", "Henry Moore",
            "Charlotte Taylor", "Alexander Thomas", "Abigail White", "Samuel Jackson",
            "Emily Harris", "Daniel Martin", "Elizabeth Thompson", "Matthew Garcia",
            "Sofia Martinez", "David Rodriguez", "Victoria Lewis", "Joseph Lee",
            "Grace Allen", "Andrew Hall", "Lily Wright", "Christopher King",
            "Chloe Scott", "Ethan Green", "Hannah Baker", "Joshua Adams",
            "Zoey Nelson", "Gabriel Carter", "Nora Hill", "Ryan Mitchell",
            "Audrey Phillips", "Luke Campbell", "Scarlett Evans", "John Collins",
            "Aria Stewart", "Thomas Young", "Maya Sanchez", "Jack Morris",
            "Lucy Reed", "Owen Parker", "Stella Brooks", "Theodore Price"
        ]
        
        publishers = [
            "Horizon Publishing", "Summit Books", "Coastal Press", "Evergreen Publications",
            "Galaxy Media", "Pinnacle House", "Lighthouse Books", "Marble Arch Press",
            "Riverbank Publishing", "Sterling House", "Cascade Books", "Magnolia Press",
            "Redwood Publishing", "Blue Harbor Books", "Crown Point Press", "Emerald City Books",
            "Falcon Publications", "Golden Gate Press", "Highland Books", "Ivy League Publishing"
        ]
        
        genres = [
            "Fiction", "Science Fiction", "Fantasy", "Mystery", "Thriller", 
            "Romance", "Historical Fiction", "Non-Fiction", "Biography", "Self-Help",
            "Business", "Technology", "Science", "Philosophy", "Poetry"
        ]
        
        # Create realistic but test-only ISBNs (start with 99 to mark as test data)
        def generate_test_isbn():
            # Create an ISBN starting with 99 (our marker for test data)
            # followed by 11 random digits to make a 13-digit ISBN
            return '99' + ''.join(random.choices(string.digits, k=11))
        
        # Generate detailed book descriptions
        def generate_description(title, genre):
            descriptions = [
                f"A {genre.lower()} masterpiece that explores the depths of human emotion through captivating storytelling.",
                f"An engaging {genre.lower()} that takes readers on a journey through unexpected twists and profound revelations.",
                f"This compelling {genre.lower()} examines the complexities of relationships against a backdrop of societal change.",
                f"A groundbreaking {genre.lower()} that challenges conventional wisdom and offers new perspectives.",
                f"An immersive {genre.lower()} experience that blends vivid imagery with thought-provoking themes.",
                f"A profound {genre.lower()} that delves into the mysteries of existence and the human condition.",
                f"This acclaimed {genre.lower()} offers readers a unique glimpse into worlds both familiar and fantastical.",
                f"A captivating {genre.lower()} that weaves together multiple storylines into a cohesive and rewarding narrative.",
                f"An innovative {genre.lower()} that pushes boundaries and redefines expectations of the genre.",
                f"This celebrated {genre.lower()} combines elegant prose with insightful observations about life and society."
            ]
            return random.choice(descriptions) + f" '{title}' stands as a testament to the power of literature to inspire and transform."
        
        # Storage for generated ISBNs to ensure uniqueness
        generated_isbns = set()
        count = 0
        
        # Some initial real books to include (with real ISBNs for cover retrieval)
        real_books = [
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'isbn': '9780743273565',
                'description': 'A novel about the decadence and excess of the Jazz Age, as experienced by a young man who becomes entangled with wealthy socialites.',
                'publication_year': 1925,
                'pub_date': date(1925, 4, 10),
                'publisher': 'Scribner',
                'status': 'available',
                'summary': 'The story of the mysteriously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan.',
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'isbn': '9780061120084',
                'description': 'A novel about racial injustice and moral growth in the American South during the 1930s, told through the eyes of a young girl.',
                'publication_year': 1960,
                'pub_date': date(1960, 7, 11),
                'publisher': 'HarperCollins',
                'status': 'available',
                'summary': 'The unforgettable novel of a childhood in a sleepy Southern town and the crisis of conscience that rocked it.',
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'isbn': '9780451524935',
                'description': 'A dystopian novel set in a totalitarian state where government surveillance is omnipresent.',
                'publication_year': 1949,
                'pub_date': date(1949, 6, 8),
                'publisher': 'Signet Classic',
                'status': 'available',
                'summary': 'The timeless classic that explores the dangers of totalitarianism and government surveillance.',
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'isbn': '9780141439518',
                'description': 'A romantic novel that follows the character development of Elizabeth Bennet, who learns not to judge by first impressions.',
                'publication_year': 1813,
                'pub_date': date(1813, 1, 28),
                'publisher': 'Penguin Classics',
                'status': 'available',
                'summary': 'A beloved story of manners, upbringing, morality, education, and marriage in Georgian England.',
            },
            {
                'title': 'The Hobbit',
                'author': 'J.R.R. Tolkien',
                'isbn': '9780547928227',
                'description': 'A fantasy novel about the adventures of hobbit Bilbo Baggins, who embarks on a quest to win a share of a dragon\'s treasure.',
                'publication_year': 1937,
                'pub_date': date(1937, 9, 21),
                'publisher': 'Houghton Mifflin Harcourt',
                'status': 'available',
                'summary': 'The classic prelude to The Lord of the Rings trilogy.',
            },
            {
                'title': 'Harry Potter and the Philosopher\'s Stone',
                'author': 'J.K. Rowling',
                'isbn': '9780747532743',
                'description': 'The first novel in the Harry Potter series, which follows the life of a young wizard and his friends at Hogwarts School of Witchcraft and Wizardry.',
                'publication_year': 1997,
                'pub_date': date(1997, 6, 26),
                'publisher': 'Bloomsbury',
                'status': 'available',
                'summary': 'The beginning of the beloved series about a young wizard\'s journey at Hogwarts School of Witchcraft and Wizardry.',
            },
            {
                'title': 'The Lord of the Rings',
                'author': 'J.R.R. Tolkien',
                'isbn': '9780618640157',
                'description': 'An epic fantasy novel that follows the quest to destroy the One Ring, which was created by the Dark Lord Sauron.',
                'publication_year': 1954,
                'pub_date': date(1954, 7, 29),
                'publisher': 'Houghton Mifflin Harcourt',
                'status': 'available',
                'summary': 'The classic high fantasy epic that has captivated readers for generations.',
            },
            {
                'title': 'The Catcher in the Rye',
                'author': 'J.D. Salinger',
                'isbn': '9780316769488',
                'description': 'A novel that follows the experiences of a teenager named Holden Caulfield in New York City after being expelled from prep school.',
                'publication_year': 1951,
                'pub_date': date(1951, 7, 16),
                'publisher': 'Little, Brown and Company',
                'status': 'available',
                'summary': 'A classic coming-of-age novel about teenage alienation and loss of innocence.',
            },
            {
                'title': 'The Hunger Games',
                'author': 'Suzanne Collins',
                'isbn': '9780439023481',
                'description': 'A dystopian novel set in a post-apocalyptic society where children are selected to compete in a televised death match.',
                'publication_year': 2008,
                'pub_date': date(2008, 9, 14),
                'publisher': 'Scholastic Press',
                'status': 'available',
                'summary': 'In a dystopian future, Katniss Everdeen volunteers to take her sister\'s place in a televised fight to the death.',
            },
            {
                'title': 'The Alchemist',
                'author': 'Paulo Coelho',
                'isbn': '9780062315007',
                'description': 'A philosophical novel about an Andalusian shepherd boy named Santiago who travels from his homeland in Spain to the Egyptian desert in search of a treasure.',
                'publication_year': 1988,
                'pub_date': date(1988, 1, 1),
                'publisher': 'HarperOne',
                'status': 'available',
                'summary': 'A magical story about following your dreams and listening to your heart.',
            },
        ]
        
        # First create the real books if they don't exist
        for book_data in real_books:
            if not Book.objects.filter(isbn=book_data['isbn']).exists():
                book = Book.objects.create(**book_data)
                
                # Try to get a real cover image for the book
                cover_file = self.get_book_cover(book_data['isbn'])
                if cover_file:
                    book.cover.save(f"{book_data['isbn']}.jpg", cover_file)
                    self.stdout.write(self.style.SUCCESS(f'Downloaded real cover for: {book.title}'))
                else:
                    # Set default cover if unable to get a real one
                    book.cover = 'books/covers/default.jpg'
                    book.save()
                    self.stdout.write(self.style.WARNING(f'Using default cover for: {book.title}'))
                
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Created real book: {book.title}'))
            else:
                existing_book = Book.objects.get(isbn=book_data['isbn'])
                # If the book exists but has default cover, try to update it
                if existing_book.cover.name == 'books/covers/default.jpg':
                    cover_file = self.get_book_cover(book_data['isbn'])
                    if cover_file:
                        existing_book.cover.save(f"{book_data['isbn']}.jpg", cover_file)
                        self.stdout.write(self.style.SUCCESS(f'Updated cover for existing book: {existing_book.title}'))
                self.stdout.write(self.style.WARNING(f'Book already exists: {book_data["title"]}'))
        
        # Generate random books
        books_to_create = count_to_create - count
        
        for i in range(books_to_create):
            # Generate unique book data
            title = random.choice(titles) + " " + str(i+1)
            author = random.choice(authors)
            genre = random.choice(genres)
            
            # Generate a unique ISBN
            while True:
                isbn = generate_test_isbn()
                if isbn not in generated_isbns and not Book.objects.filter(isbn=isbn).exists():
                    generated_isbns.add(isbn)
                    break
            
            # Generate publication details
            current_year = datetime.now().year
            pub_year = random.randint(1950, current_year)
            pub_month = random.randint(1, 12)
            pub_day = random.randint(1, 28)  # Avoiding potential month day issues
            
            # Create book
            book_data = {
                'title': title,
                'author': author,
                'isbn': isbn,
                'description': generate_description(title, genre),
                'summary': f"A {genre.lower()} book about {title.lower().replace('the ', '')}.",
                'publication_year': pub_year,
                'pub_date': date(pub_year, pub_month, pub_day),
                'publisher': random.choice(publishers),
                'status': random.choice(['available'] * 8 + ['checked_out', 'reserved']),  # Weighted to have more available
            }
            
            # Create the book
            book = Book.objects.create(**book_data)
            
            # First try to get a specific cover for this book (for test ISBNs, unlikely to find one)
            cover_file = self.get_book_cover(isbn)
            
            # If no specific cover found, download a random image to use as cover
            if not cover_file:
                cover_file = self.download_random_book_cover()
            
            if cover_file:
                # Save the image as the book cover
                book.cover.save(f"{isbn}.jpg", cover_file)
                self.stdout.write(self.style.SUCCESS(f'Set random cover for: {book.title}'))
            else:
                # Set default cover as fallback
                book.cover = 'books/covers/default.jpg'
                book.save()
            
            count += 1
            
            # Show progress every 10 books
            if count % 10 == 0 or count == count_to_create:
                self.stdout.write(self.style.SUCCESS(f'Created {count}/{count_to_create} books...'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} test books'))