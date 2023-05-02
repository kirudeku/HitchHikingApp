# posts/urls.py
from django.urls import path, include
from . import views
# from .views import post_create, post_detail, booking_detail, booking_cancel

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.perform_about, name='perform_about'),
    path('services/', views.perform_services, name='perform_services'),
    path('contacts/', views.perform_contacts, name='perform_contacts'),
    path('postings/', views.postings, name='postings'),
    path('postings/<int:posting_id>', views.posting, name='posting'),
    path('bookings/', views.BookingListView.as_view(), name='bookings'),
    path('bookings/<int:pk>', views.BookingDetailView.as_view(),
         name='booking-detail'),
    path('search/', views.search, name='search'),
    path('create/', views.post_create, name='post_create'),
    path('<int:pk>/', views.post_detail, name='post_detail'),
    path('booking/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('booking/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
