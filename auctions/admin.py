from django.contrib import admin

# Register your models here.
from .models import User, Listing, Bid, Comments, Category

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comments)
admin.site.register(Category)

