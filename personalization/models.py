from django.db import models
from django.contrib.auth.models import User
from app1.models import Activity


class PersonalInfo(models.Model):#one per user
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	about_user = models.CharField(max_length=65536, null = True)
	personal_image = models.ImageField(null = True, blank = True)

class Critic(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	is_critic = models.BooleanField()


class Follows(models.Model):
	user = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
	following_user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)

	class Meta:
		unique_together = ('user', 'following_user')

class FavoriteBooks(Activity): #many to one relationship with User
	favorite_id = models.CharField(max_length = 100)
	favorite_title = models.CharField(max_length = 100)
	favorite_cover = models.CharField(max_length = 100)

	#need to return title when refrencing object to properly display on PostForm
	def __str__(self):
		return self.favorite_title
