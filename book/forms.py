from django import forms
from .models import Hotel,HotelImage
class AddhotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name','city','address','overview','highlight','room','rating','price']


class HotelImageForm(forms.ModelForm):
    class Meta:
        model = HotelImage
        fields = ('image',)

from django.forms import modelformset_factory
HotelImageFormSet = modelformset_factory(HotelImage, form=HotelImageForm, extra=5)