from django import forms
from .models import MoviesRead

class MoviesForm(forms.ModelForm):
    class Meta:
        model = MoviesRead
        fields = ('title', 'file_name')
