web: gunicorn library.wsgi --log-file -
populate_books: python manage.py create_test_books --production --count ${COUNT:-100}
populate_books_and_clear: python manage.py create_test_books --production --count ${COUNT:-100} --clear
clear_all_books: python manage.py clear_all_books --production --confirm