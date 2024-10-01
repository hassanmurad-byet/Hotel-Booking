from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render,redirect,get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import math
import time
from django.utils.timezone import now
from datetime import timedelta
from django.views.generic import CreateView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum
from book.forms import AddhotelForm
from .forms import *
from .models import Hotel, HotelImage
from .forms import HotelImageForm, HotelImageFormSet
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from paytm import Checksum
from .models import *

# Create your views here.


def index(request):
    popular = Hotel.objects.filter(rating='5 star')
    return render(request, "book/index.html", {
        "popular": popular[8:14]
    })


def cities(request):
    cities = Hotel.objects.values('city').distinct()
    new = {city["city"]: None for city in cities}
    return JsonResponse(new, safe=False)


def search_hotels(request):
    try:
        q = request.GET["q"]
        q = q[0].upper() + q[1:]
        try:
            sort = request.GET["sort"]
        except:
            sort = "def"
        if sort == "r_asc":
            all_hotels = Hotel.objects.filter(city=q).order_by('-rating')
        elif sort == "r_desc":
            all_hotels = Hotel.objects.filter(city=q).order_by('rating')
        elif sort == "p_asc":
            all_hotels = Hotel.objects.filter(city=q).order_by('-price')
        elif sort == "p_desc":
            all_hotels = Hotel.objects.filter(city=q).order_by('price')
        else:
            all_hotels = Hotel.objects.filter(city=q)
            sort = "def"
    except:
        q = None
        all_hotels = None

    if len(request.GET) < 1:
        return render(request, "book/search.html", {
            "message": "Search Hotels"
        })

    if not all_hotels:
        return render(request, "book/search.html", {
            "message": "City not found"
        })

    p = Paginator(all_hotels, 6)
    try:
        page_num = request.GET["page"]
    except:
        page_num = 1
    page_obj = p.get_page(page_num)
   
    return render(request, "book/search.html", {
        "page_obj": page_obj,
        "city": q,
        "sort": sort,
        "total": len(all_hotels),
    })


def popular_hotels(request):
    hotels = Hotel.objects.filter(Q(rating='4') | Q(rating='5'))
    return render(request, "book/popular.html", {'hotels': hotels})
  
# kuakata 
def hotels_in_kuakata(request):
    kuakata_hotels = Hotel.objects.filter(city='Kuakata')

    return render(request, 'book/kaukata.html', {'hotel': kuakata_hotels})

# cox's bazar .... 
def hotels_in_coxs(request):
    coxs_hotels = Hotel.objects.filter(city="Cox's Bazar")
    return render(request, 'book/coxs.html', {'hotel':coxs_hotels})

# saint matrin 
def hotels_in_saint(request):
    saint_hotels = Hotel.objects.filter(city='Saint Martin')
    return render(request, 'book/saint.html', {'hotel':saint_hotels})

# sajek 
def hotels_in_sajek(request):
    sajek_hotels = Hotel.objects.filter(city='Sajek')
    return render(request, 'book/sajek.html', {'hotel':sajek_hotels})


def hotel_view(request, id):
    hotel = get_object_or_404(Hotel,id=id)
    images = hotel.images.all() 
    hotel = Hotel.objects.get(id=id)
   

    return render(request, "book/hotel.html", {
        "hotel": hotel,"img":images
    })


def create_price(id, room, adult, child, days):
    original_price = Hotel.objects.get(id=id).price
    price = original_price * room
    price += math.floor(original_price * (adult - 1) * 0.5)
    price += math.floor(original_price * child / 4)
    price += math.floor(original_price * (days - 1) / 3)
    return price


# @login_required(login_url="login")
def book_hotel(request):
    if request.method != "POST":
        return render(request, "book/book.html", {
            "message": "Page does not exist"
        })

    room = int(request.POST["room"])
    adult = int(request.POST["adult"])
    child = int(request.POST["child"])

    days = int(request.POST["days"])
    id = int(request.POST["id"])

    checkin = request.POST["checkin"]
    checkout = request.POST["checkout"]

    price = create_price(id, room, adult, child, days)

    hotel = Hotel.objects.get(id=id)
    return render(request, "book/book.html", {
        "price": price,
        "hotel": hotel,
        "room": room,
        "adult": adult,
        "child": child,
        "checkin": checkin,
        "checkout": checkout,
        "days": days,
    })


def successful(request):
    if request.method != "POST":
        return render(request, "book/apology.html", {
            "message": "Error occurred"
        })

    id = int(request.POST["id"])
    hotel = Hotel.objects.get(id=id)
    checkin = request.POST["checkin"]
    checkout = request.POST["checkout"]

    first_name = request.POST["first_name"]
    last_name = request.POST["last_name"]
    phone = request.POST["phone"]
    email = request.POST["email"]

    room = int(request.POST["room"])
    adult = int(request.POST["adult"])
    child = int(request.POST["child"])
    days = int(request.POST["days"])

    price = str(create_price(id, room, adult, child, days))

    tracking_id = first_name[0] + last_name[0] + str(int(time.time()))
    print(tracking_id)

    b = Booking(
        hotel=hotel,
        checkin_date=checkin,
        checkout_date=checkout,
        room=room,
        adult=adult,
        child=child,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        tracking_id=tracking_id,
        price=price
    )

    try:
        b.save()
    except Exception as e:
        print(f"Error Occurred: {e}")
        return render(request, "book/apology.html", {
            "message": "Internal Server Error"
        })

    return render(request, "book/successful.html", {
        "message": "Booking successful",
        "tracking_id": tracking_id
    })


@csrf_exempt
def callback(request):
    if request.method == "POST":
        tracking_id = request.POST["ORDERID"]
        print(request.POST)
        return render(request, "book/successful.html", {
            "tracking_id": tracking_id
        })
    # paytm callback
    print(request.GET)
    return render(request, "book/apology.html", {
        "message": "Order failed due to some reason"
    })


def track_booking(request):
    if request.method == "POST":
        tracking_id = request.POST["tracking-id"]
        phone = request.POST["phone"]
        try:
            booking = Booking.objects.get(tracking_id=tracking_id, phone=phone)
            return render(request, "book/track.html", {
                "booking": booking
            })

        except:
            return render(request, "book/track.html", {
                "message": "Invalid tracking ID"
            })

    return render(request, "book/track.html")


@login_required(login_url="login")
def profile(request):
    return render(request, "book/profile.html")


def login_view(request):
    if request.user.is_authenticated:
        return render(request, "book/apology.html", {
            "message": "Already logged in"
        })
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
            return render(request, "book/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "book/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return render(request, "book/apology.html", {
            "message": "Already logged in"
        })
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        phone = int(request.POST["phone"])

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "book/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.phone = phone
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "book/register.html", {
                "message": "Email address already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "book/register.html")



# dashbord ...


def Dashboard(request):
    total_hotel = Hotel.objects.count()
    total_customer = User.objects.count()
    total_booking = Booking.objects.count()
    booking = Booking.objects.all()

   
      # Calculate the total revenue from all bookings
    total_revenue = Booking.objects.aggregate(total_revenue=Sum('price'))['total_revenue']



    context = {
        'total_hotel':total_hotel,
        'total_customer':total_customer,
        'total_booking':total_booking,
        'total_revenue':total_revenue,
        'booking':booking,


    }
    return render(request, "book/dashboard.html", context)


def hotellist(request):
    totalhotel = Hotel.objects.all()
    return render(request, "book/hotellist.html", {'totalhotel':totalhotel})


def customerlist(request):
    totalhotel = Hotel.objects.all()
    return render(request, "book/hotellist.html", {'totalhotel':totalhotel})



# Add HotelImage

# class AddHotel(LoginRequiredMixin, CreateView):
#     model = Hotel
  
#     template_name = 'book/add_hotel.html'
#     fields = ('name','city','address','overview','highlight','room','price','image')
    
#     def form_valid(self, form):
#         prod_obj = form.save(commit=False)
#         prod_obj.user =self.request.user
#         prod_obj.save()
#         return HttpResponseRedirect(reverse('hotel_list'))






class AddHotel(LoginRequiredMixin, CreateView):
    model = Hotel
    template_name = 'book/add_hotel.html'
    fields = ('name', 'city', 'address', 'overview', 'highlight', 'room','rating', 'price', 'image')

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        image_formset = HotelImageFormSet(queryset=HotelImage.objects.none())
        return self.render_to_response(self.get_context_data(form=form, image_formset=image_formset))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        image_formset = HotelImageFormSet(self.request.POST, self.request.FILES, queryset=HotelImage.objects.none())

        if form.is_valid() and image_formset.is_valid():
            return self.form_valid(form, image_formset)
        else:
            return self.form_invalid(form, image_formset)

    def form_valid(self, form, image_formset):
        prod_obj = form.save(commit=False)
        prod_obj.user = self.request.user
        prod_obj.save()

        for image_form in image_formset:
            image_obj = image_form.save(commit=False)
            image_obj.hotel = prod_obj
            image_obj.save()

        return HttpResponseRedirect(reverse('hotel_list'))

    def form_invalid(self, form, image_formset):
        return self.render_to_response(self.get_context_data(form=form, image_formset=image_formset))
    



# add hotel more image 
# class AddHotelimg(LoginRequiredMixin, CreateView):
#     model = HotelImage
#     template_name = 'book/add_moreimg.html'
#     fields = ('hotel','image')
    
#     def form_valid(self, form):
#         prod_obj = form.save(commit=False)
#         prod_obj.user =self.request.user
#         prod_obj.save()
#         return HttpResponseRedirect(reverse('add_hotel'))



# Update hotel 
@login_required
def UpdateHotel(request, pk):
    product = get_object_or_404(Hotel, pk=pk)
    
    if request.method == 'POST':
        form = AddhotelForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('hotel_list')  # Redirect to the product detail page
    else:
        form = AddhotelForm(instance=product)
    
    return render(request, 'book/add_hotel.html', {'form': form})


@login_required
def deleteHotel(request, del_id):
    hotel = get_object_or_404(Hotel, pk=del_id)
    if request.method == 'POST':
        hotel.delete()
        messages.success(request, 'Hotel deleted successfully.')
        # return redirect('productlist') 
    return render(request, 'book/hotel_del.html', {'hotel': hotel})



# Customer List 
@login_required
def Customer_list(request):
  customer = User.objects.all()
  return render(request, 'book/customer_list.html', {'customers': customer})

@login_required
def Booking_list(request):
  booking = Booking.objects.all()
  return render(request, 'book/booking_list.html', {'booking': booking})



def Report(request):
    bookings = Booking.objects.all()
    # Calculate the total revenue from all bookings
    total_revenue = Booking.objects.aggregate(total_revenue=Sum('price'))['total_revenue']

    # Calculate the current time
    current_time = now()
    # Calculate the start of the last month and the last 24 hours
    last_month_start = current_time - timedelta(days=30)
    last_24_hours_start = current_time - timedelta(hours=24)

    # Get the list of bookings from the last month
    bookings_last_month = Booking.objects.filter(booking_date__gte=last_month_start)

    # Get the list of bookings from the last 24 hours
    bookings_last_24_hours = Booking.objects.filter(booking_date__gte=last_24_hours_start)
    



    # Calculate the total revenue for the last month
    total_revenue_last_month = Booking.objects.filter(booking_date__gte=last_month_start).aggregate(total_revenue=Sum('price'))['total_revenue'] or 0

    # Calculate the total revenue for the last 24 hours
    total_revenue_last_24_hours = Booking.objects.filter(booking_date__gte=last_24_hours_start).aggregate(total_revenue=Sum('price'))['total_revenue'] or 0

 
    context = {
        'booking': bookings,
        'total_price': total_revenue,
        'last_month_book':bookings_last_month,
        'last_month':total_revenue_last_month,
        'bookings_last24h':bookings_last_24_hours,
        'last_day':total_revenue_last_24_hours,
    } 
    return render(request, 'book/report.html', context)