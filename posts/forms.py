from django import forms
from .models import Posting, Booking, Review, Message


class PostForm(forms.ModelForm):
    title = forms.CharField(label="Title", max_length=200)

    class Meta:
        model = Posting
        fields = ['title', 'description', 'start_location',
                  'end_location', 'start_time', 'available_seats', 'price']


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['num_seats']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']
