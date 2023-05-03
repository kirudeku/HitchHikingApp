from django.contrib import admin
from .models import Posting, Booking, Review, Message, PostingLike


admin.site.register(Posting)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Message)
admin.site.register(PostingLike)
