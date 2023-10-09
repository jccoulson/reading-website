from django.db import models
from personalization.models import FavoriteBooks
from app1.models import Activity

class Post(Activity):
    title = models.CharField(max_length=200)
    content = models.TextField()
    book_object = models.ForeignKey(FavoriteBooks, on_delete=models.CASCADE) #one to one relationship

    class Meta:
        ordering = ["-last_modified"]

    def __str__(self):
        return self.title
