# posts/urls.py
from django.urls import path, include
from . import views
from django.views.generic.base import TemplateView


urlpatterns = [
    path('posts/', views.index, name='index'),
    path('about/', views.perform_about, name='perform_about'),
    path('services/', views.perform_services, name='perform_services'),
    path('contacts/', views.perform_contacts, name='perform_contacts'),
    path('search/', views.search, name='search'),
    path('postings/', views.PostListView.as_view(), name='postings'),
    path('postings/<int:posting_id>', views.posting, name='posting'),
    path('user-posts/<username>',
         views.UserPostListView.as_view(), name='user_posts'),
    path('createbooking/<int:pk>/', views.BookingCreateView.as_view(), name='booking-create'),
    path('bookings/', views.BookingListView.as_view(), name='bookings'),
    path('bookings/<int:pk>', views.BookingDetailView.as_view(),
         name='booking-detail'),
    path('create/', views.PostCreateView.as_view(), name='post-create'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('<int:pk>/update/', views.PostUpdateView.as_view(), name='post-update'),
    path('<int:pk>/delete/', views.PostDeleteView.as_view(), name='post-delete'),
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
