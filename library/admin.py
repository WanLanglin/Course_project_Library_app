from django.contrib import admin
from .models import Book, Profile, Collection

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'status', 'publication_year', 'pub_date', 'cover', 'summary')
    list_filter = ('status', 'publication_year')
    search_fields = ('title', 'author', 'isbn')
    ordering = ('title', 'author')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'publication_year', 'pub_date', 'cover', 'summary')
        }),
        ('Additional Details', {
            'fields': ('description', 'publisher')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    ) 
admin.site.register(Profile)
admin.site.register(Collection)