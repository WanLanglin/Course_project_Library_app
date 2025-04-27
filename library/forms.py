from django import forms
from django.contrib.auth.models import User
from .models import Book, Profile, Collection, Review

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        # all the fields we need to fill out
        fields = [
            'title',
            'author',
            'isbn',
            'publication_year',
            'pub_date',
            'cover',
            'description',
            'summary',
            'publisher',
            'location',
            'status'
        ]
        # make it look nice
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),  # bigger text box for summary
            'publication_year': forms.NumberInput(attrs={'min': 1000, 'max': 9999}),  # no super old or future books
        } 


class CollectionForm(forms.ModelForm):
    allowed_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Collection
        fields = ['title', 'description', 'is_private', 'allowed_users']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs and kwargs['initial'].get('creator'):
            creator = kwargs['initial']['creator']
            if not creator.groups.filter(name='Librarian').exists():
                self.fields['is_private'].choices = [('public', 'Public')]
                self.fields['is_private'].initial = 'public'
                self.fields['is_private'].disabled = True
                self.fields['allowed_users'].widget.attrs['disabled'] = True
                self.fields['allowed_users'].required = False
        else:
            # Handle the case where 'initial' is not provided or does not contain 'creator'
            pass

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'name']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

        rating_value = forms.ChoiceField(
            choices=[(i, i) for i in range(1, 6)],
            widget=forms.Select(attrs={'class': 'form-control'})
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user' in kwargs:
            self.fields['reviewer'].initial = kwargs['user']

