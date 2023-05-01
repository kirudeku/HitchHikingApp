from django.contrib import admin
from .models import Posting, Booking, Review, Message


admin.site.register(Posting)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Message)
