from email.policy import default
from unittest.util import _MAX_LENGTH
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length = 60)

    def __str__(self):
        return f'{self.name}'

class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length = 64, null=False)
    description= models.CharField(max_length = 200, null= False)
    starting_bid= models.IntegerField(null = False)
    image_url = models.CharField(max_length = 250)
    category = models.ForeignKey(Category, on_delete =models.CASCADE, related_name = 'listing')
    author = models.ForeignKey(User, on_delete =models.CASCADE, related_name = 'listing')
    active = models.BooleanField(default = True, null = False)


    def __str__(self):
        return f'{self.title}: {self.description} - ${self.starting_bid}'

class Bid(models.Model):
    bid= models.IntegerField(null = False, default = 0)
    listing = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name = 'bid')
    bidder = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'bid')
    date_created = models.DateField(default = timezone.now)

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete =models.CASCADE, related_name = 'watchlist')
    listing = models.ManyToManyField(Listing, blank = True, related_name = 'watchlist')

    def __str__(self):
        return f"{self.user}'s Watchlist"


class Comments(models.Model):
    comment = models.CharField(max_length = 250, default = "")
    author = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'comment', blank = True, null = True)
    listing = models.ForeignKey(Listing, on_delete = models.CASCADE, related_name = 'comment', blank = True, null= True)
    date_created = models.DateField(default = timezone.now)

    def __str__(self):
        return f'{self.author} commented on {self.listing} with: "{self.comment}"'



