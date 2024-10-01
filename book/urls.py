from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('dashboard/', views.Dashboard, name="dashboard"),
    path('hotel-list/', views.hotellist, name="hotel_list"),
    path('add-hotel/', views.AddHotel.as_view(), name="add_hotel"),
    # path('add-hotelimg/', views.AddHotelimg.as_view(), name="add_hotelimg"),
    path('update-hotel/<pk>/', views.UpdateHotel, name="update_hotel"),
    path('delhotel/<int:del_id>/', views.deleteHotel, name='delHotel'),
    path('customer-list/', views.Customer_list, name="customer_list"),
    path('booking-list/', views.Booking_list, name="booking_list"),
    path('report/', views.Report, name="report"),



  






    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("hotel/<int:id>", views.hotel_view, name="hotel"),
    path("cities", views.cities, name="cities"),
    path("search", views.search_hotels, name="search"),
    path("popular", views.popular_hotels, name="popular"),
    path("profile", views.profile, name="profile"),
    path("book", views.book_hotel, name="book"),
    path("success", views.successful, name="success"),
    path("track", views.track_booking, name="track"),
    path("callback", views.callback, name="callback"),
    path('hotels-in-kuakata/', views.hotels_in_kuakata, name='hotels_in_kuakata'),
    path('hotels-in-coxs-bazar/', views.hotels_in_coxs, name='hotels_in_coxs'),
    path('hotels-in-saint/', views.hotels_in_saint, name='hotels_in_saint'),
    path('hotels-in-sajek/', views.hotels_in_sajek, name='hotels_in_sajek'),




]
