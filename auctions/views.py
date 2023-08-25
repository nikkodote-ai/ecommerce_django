from unicodedata import category, name
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
#for troubleshooting
import sys

from .models import User, Listing, Bid, Comments, Category, Watchlist, Comments


def index(request):
    """
    Home page, lists active listing
    """
    active_listings = Listing.objects.filter(active = True).all()
    for listing in active_listings:
        print(f'LISTING = {listing.id} {listing.active}')

    # user_watchlist = Watchlist.objects.get(user = request.user)

    # watchlist_count = f'({len(user_watchlist.listing.all())})'
    # for listing in active_listings:
    #     print(listing.title)
    return render(request, "auctions/index.html", {
        'active_listings': active_listings,
        # 'watchlist_count' : watchlist_count
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    category_list = Category.objects.all()
    if request.method == "POST":
        new_listing = Listing.objects.create(
            title = request.POST['title'],
            description = request.POST['description'],
            starting_bid = request.POST['starting_bid'],
            image_url = request.POST['image_url'],
            category = Category.objects.get(name = request.POST['category']),
            author = request.user
        )
        current_bid = Bid.objects.create(bid = request.POST['starting_bid'], listing = new_listing, bidder = request.user)
        return HttpResponseRedirect(reverse('index'))

    return render(request, "auctions/create_listing.html", {
        "category_list" : category_list
    })

@login_required
def add_to_watchlist(request, listing_id):
    if request.method =='POST':
        #get user's watchlist
        user_watchlist = Watchlist.objects.get_or_create(user = request.user)[0] 
        print(f'USER WATCHLIST {user_watchlist}')
        listing = Listing.objects.get(pk = listing_id)
        print(f'LISTING: {listing}')
        if len(user_watchlist.listing.filter(id = listing_id)) == 0:
           
            user_watchlist.listing.add(listing)
        else:
            error_message = "This item is already added to your watchlist."
            return render(request, 'auctions/error.html', {'error_message': error_message})
        return HttpResponseRedirect(reverse('index'))

@login_required
def delete_from_watchlist(request, listing_id):
    if request.method =='POST':
        listing = Listing.objects.get(pk = listing_id)
        user_watchlist = Watchlist.objects.get_or_create(user = request.user)[0] 
        user_watchlist.listing.remove(listing)
        
        
        #print('delete succesful')
        return HttpResponseRedirect(reverse('show_watchlist'))


@login_required
def show_watchlist(request):
    watchlist = Watchlist.objects.get(user = request.user)
    listings = watchlist.listing.all()
    print(listings)
    return render(request, "auctions/watchlist.html", {'listings' : listings})

def show_category(request, category_id):
    category_listing = Listing.objects.filter(category = category_id).all()
    category = Category.objects.get(pk = category_id).name
    return render(request, "auctions/category_listings.html", {
        "category_listing": category_listing,
        "category" : category
        })

def category_main(request):
    category_list = Category.objects.all()
    return render(request, "auctions/category_main.html", {
        "category_list":category_list
    })

def show_listing(request, listing_id):
    listing = Listing.objects.get(pk = listing_id)
    all_bids = Bid.objects.filter(listing = listing)
    current_bid = all_bids.aggregate(Max('bid'))['bid__max']
    comments = Comments.objects.filter(listing = listing)
    winning_bid = Bid.objects.filter(bid =current_bid).first()
    winner = 'No bidder'
    if winning_bid is not None:
        winner = winning_bid.bidder
    print(f'current bid {current_bid}')
    print(f'the winner is {winner}')
    return render(request, "auctions/listing.html", {
        "listing" : listing,
        "current_bid" : current_bid,
        "number_of_bids" : (len(all_bids)),
        'comments' : comments,
        'author' : listing.author,
        'winner' : winner
    })

@login_required
def close_bid(request, listing_id):
    listing = Listing.objects.get(pk = int(listing_id))
    if request.user == listing.author:
        listing.active = False
        listing.save()
        print(f'{listing.active}')
        print(f'LISTING {listing_id} closed successfully')
        return HttpResponseRedirect(reverse('index'))
        
@login_required
def place_bid(request):
    if request.method == 'POST':
        placed_bid = int(request.POST['bid'])
        listing_id = request.POST['listing_id']
        print(f'LISTING ID IS {listing_id}')
        listing = Listing.objects.get(pk=listing_id)
        print(f'LISTING: {listing}')
        all_bids = Bid.objects.filter(listing = listing, bidder = request.user)
        print(f'{all_bids}')
        current_bid = all_bids.aggregate(Max('bid'))['bid__max']
        if current_bid == None:
            current_bid = 0

        print(f'LISTING: {listing} with starting bid {listing.starting_bid} and CURRENT_BID: {current_bid}')
        if placed_bid > listing.starting_bid and placed_bid > current_bid:
            # print('please code to place bid')
            Bid.objects.create(listing = listing, bid = placed_bid, bidder = request.user)
            print('bid successful')
        else:
            error_message = 'Please place a higher bid than the starting and current bid'
            return render(request, 'auctions/error.html', {"error_message": error_message} )
        return HttpResponseRedirect(reverse(show_listing, kwargs = {'listing_id': listing_id}))

@login_required
def add_comment(request):
    listing_id = request.POST['listing_id']
    listing = Listing.objects.get(pk = listing_id)
    comment = request.POST['comment']
    new_comment = Comments.objects.create(listing = listing, comment = comment, author = request.user)
    return HttpResponseRedirect(reverse(show_listing, kwargs = {'listing_id': listing_id}))