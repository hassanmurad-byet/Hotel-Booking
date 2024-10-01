from xml.dom import ValidationErr
from django.db import models
from django.contrib.auth.models import AbstractUser
import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg

def random_price():
    return random.randint(800,2000)

class User(AbstractUser):
    phone = models.IntegerField(default=None, blank=True, null=True)
    avatar = models.CharField(default=None ,max_length=64, blank=True, null=True)
    pass


ROOM_CHOICES = [
    ('Single','Single'),
    ('Dulux','Dulux'),
]

class Hotel(models.Model):
    name = models.CharField(default=None, max_length=64)
    city = models.CharField(default=None, max_length=64)
    address = models.CharField(default=None, max_length=64)
    overview = models.CharField(default=None, max_length=64)
    highlight = models.CharField(default=None, max_length=64)
    room = models.CharField(default=None, max_length=64)
    room_type = models.CharField(choices=ROOM_CHOICES,default="Single", max_length=64)

    rating = models.CharField(default=0, max_length=64)

    price = models.FloatField(default=random_price)
    image = models.ImageField(upload_to="hotel_img", verbose_name="hotelimg")

    def __str__(self):
        return f"{self.city}"
    
    @property
    def total_price_with_vat(self):
        vat_rate = 0.10  # 10% VAT
        return self.price * (1 + vat_rate)
    
class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='hotel_images/')

    def __str__(self):
        return f'Image for {self.hotel.name}'

class Booking(models.Model):
    hotel = models.ForeignKey(Hotel, related_name="booking", on_delete=models.CASCADE)
    tracking_id = models.CharField(default='000', max_length=64)

    first_name = models.CharField(default=None, max_length=64)
    last_name = models.CharField(default=None, max_length=64)
    email = models.CharField(default=None, max_length=64)
    phone = models.CharField(default=None, max_length=64)

    room = models.IntegerField(default=1)
    room_typ = models.CharField(choices=ROOM_CHOICES, default='Single',max_length=50)

    adult = models.IntegerField(default=1)
    child = models.IntegerField(default=0)

    checkin_date = models.CharField(default=None , max_length=64)
    checkout_date = models.CharField(default=None, max_length=64)
    booking_date = models.DateTimeField(auto_now_add=True)
    price = models.CharField(max_length=64, default=None, null=False)
    room_number = models.IntegerField(default=0)

    user = models.ForeignKey(User, related_name="booking", on_delete=models.SET_NULL, default=None, null=True, blank=True)

    def __str__(self):
        return self.tracking_id
    
    def clean(self):
        # Ensure no other booking exists for the same room in the same date range
        bookings = Booking.objects.filter(hotel=self.hotel, room_number=self.room_number)
        for booking in bookings:
            if not (self.checkout_date <= booking.checkin_date or self.checkin_date >= booking.checkout_date):
                raise ValidationErr(f"Room {self.room_number} is already booked for the selected dates.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Review(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='hotel_name', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_reviews', on_delete=models.CASCADE)
    cusrating = models.IntegerField(default=0)  # Assuming rating is an integer between 1 and 5
    comment = models.CharField(max_length=100, verbose_name="User Comment")
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} for {self.hotel.name}'
    
# @receiver(post_save, sender=Review)
# def update_hotel_rating(sender, instance, **kwargs):
#     hotel = instance.hotel
#     average_rating = Review.objects.filter(hotel=hotel).aggregate(Avg('rating'))['rating__avg']
#     hotel.hrating = average_rating
#     hotel.save()

# @receiver(post_save, sender=receiver)
# def update_hotel_rating(sender, instance, **kwargs):
#     if instance.rating:
#         reviewer = instance.rating
#         reviewer.hrating += 1
#         reviewer.save()