from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("add_to_watchlist/<str:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("delete_from_watchlist/<str:listing_id>", views.delete_from_watchlist, name="delete_from_watchlist"),
    path("watchlist", views.show_watchlist, name="show_watchlist"),
    path("category/<str:category_id>", views.show_category, name = "show_category"),
    path("listing/<str:listing_id>", views.show_listing, name = "show_listing"),
    path("place_bid", views.place_bid, name = "place_bid"),
    path("close_bid/<str:listing_id>", views.close_bid, name = "close_bid"),
    path("add_comment", views.add_comment, name = "add_comment"),
    path("category", views.category_main, name = "category_main"),
    
]
