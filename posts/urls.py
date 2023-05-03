# posts/urls.py
from django.urls import path, include
from . import views
from django.views.generic.base import TemplateView


urlpatterns = [
    path('posts/' or '/', views.index, name='index'),
    # path('', views.index, name='index'),
    path('about/', views.perform_about, name='perform_about'),
    path('services/', views.perform_services, name='perform_services'),
    path('contacts/', views.perform_contacts, name='perform_contacts'),
    path('postings/', views.postings, name='postings'),
    path('postings/<int:posting_id>', views.posting, name='posting'),
    path('bookings/', views.BookingListView.as_view(), name='bookings'),
    path('bookings/<int:pk>', views.BookingDetailView.as_view(),
         name='booking-detail'),
    path('search/', views.search, name='search'),
    path('create/', views.posting_create, name='posting_create'),
    path('<int:pk>/', views.posting_detail, name='posting_detail'),
    path('booking/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('booking/<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
    # ----------below are DRF links, will not work ----------
    path('postingstry', views.PostingList.as_view()),
    path('postingstry/<int:pk>', views.PostingDetail.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('postingstry/<int:pk>/reviews', views.ReviewList.as_view()),
    path('reviews/<int:pk>', views.ReviewDetail.as_view()),
    path('postingstry/<int:pk>/like', views.PostingLikeCreate.as_view()),
    path('signup', views.UserCreate.as_view()),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', TemplateView.as_view(template_name='main/home.html'), name='home'),
]
