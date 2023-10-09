from django.db import models
from django.contrib.auth.models import User
from app1.models import Activity

class BookReview(Activity):#child of activity class
    book_id = models.CharField(max_length=100)
    text_review = models.CharField(max_length=65536)
    star_review = models.IntegerField()
    book_title = models.CharField(max_length=100)
    book_cover = models.CharField(max_length=100)
