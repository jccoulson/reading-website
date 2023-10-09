from django import forms
from posts.models import Post
from personalization.models import FavoriteBooks
import requests
#from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'size': '80'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': '10', 'cols': '80'}))

    #gets current user being passed into PostForm and finds all current books of that user
    #everytime PostForm is referenced it needs to be passed request.user
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        favorite_queryset = FavoriteBooks.objects.filter(user = self.user)
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['book_object'] = forms.ModelChoiceField(queryset=favorite_queryset)


    class Meta():
        model = Post
        fields = [ 'title', 'content', 'book_object']
