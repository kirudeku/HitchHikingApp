# posts/urls.py
from django.urls import path, include
from .views import index, postings, posting, BookingListView, BookingDetailView, search, post_create, post_detail, booking_detail, booking_cancel
# from .views import post_create, post_detail, booking_detail, booking_cancel

urlpatterns = [
    path('', index, name='index'),
    path('postings/', postings, name='postings'),
    path('postings/<int:posting_id>', posting, name='posting'),
    path('bookings/', BookingListView.as_view(), name='bookings'),
    path('bookings/<int:pk>', BookingDetailView.as_view(), name='booking-detail'),
    path('search/', search, name='search'),
    path('create/', post_create, name='post_create'),
    path('<int:pk>/', post_detail, name='post_detail'),
    path('booking/<int:pk>/', booking_detail, name='booking_detail'),
    path('booking/<int:pk>/cancel/', booking_cancel, name='booking_cancel'),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
