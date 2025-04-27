from django.core.management.base import BaseCommand
from library.models import Book


class Command(BaseCommand):
    help = 'Clears ALL books from the database. USE WITH CAUTION!'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirmation flag required to actually delete books'
        )
        parser.add_argument(
            '--production',
            action='store_true',
            help='Use this flag when running in production environment'
        )

    def handle(self, *args, **kwargs):
        confirm = kwargs.get('confirm', False)
        is_production = kwargs.get('production', False)
        
        if not confirm:
            self.stdout.write(self.style.ERROR(
                'This command will delete ALL books from the database. '
                'To confirm, run with the --confirm flag.'
            ))
            return
        
        if not is_production:
            self.stdout.write(self.style.ERROR(
                'This command should only be run in production environments. '
                'To confirm, run with the --production flag.'
            ))
            return
        
        # Delete all books
        all_books = Book.objects.all()
        count = all_books.count()
        all_books.delete()
        
        self.stdout.write(self.style.SUCCESS(
            f'PRODUCTION MODE: Successfully deleted all {count} books from the database'
        ))