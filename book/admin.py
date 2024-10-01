from django.contrib import admin

# Register your models here.
from .models import User,Hotel,Booking,Review,HotelImage

admin.site.register(User)
admin.site.register(Booking)
admin.site.register(Review)

class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 5 # Number of extra forms to display

class HotelAdmin(admin.ModelAdmin):
    inlines = [HotelImageInline]

admin.site.register(Hotel, HotelAdmin)