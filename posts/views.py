from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics, permissions, mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Posting, Booking, Review, Message, PostingLike
from .forms import PostForm, BookingForm
from .serializers import PostingSerializer, ReviewSerializer, PostingLikeSerializer, UserSerializer
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.db.models import Q


def index(response):
    num_postings = Posting.objects.all().count()
    num_bookings = Booking.objects.all().count()

    num_pending_bookings = Booking.objects.filter(
        status__exact='PENDING').count()

    num_visits = response.session.get('num_visits', 1)
    response.session['num_visits'] = num_visits + 1

    context = {
        'num_postings': num_postings,
        'num_bookings': num_bookings,
        'num_pending_bookings': num_pending_bookings,
        'num_visits': num_visits,
    }

    return render(response, 'main/index.html', context=context)


def perform_about(response):
    return render(response, 'main/about.html')


def perform_services(response):
    return render(response, 'main/services.html')


def perform_contacts(response):
    return render(response, 'main/contacts.html')


def postings(request):

    postings = Posting.objects.all()
    context = {
        'postings': postings
    }
    print(postings)
    return render(request, 'main/postings.html', context=context)


def posting(request, posting_id):
    single_posting = get_object_or_404(Posting, pk=posting_id)
    return render(request, 'main/posting.html', {'posting': single_posting})


class BookingListView(generic.ListView):
    model = Booking
    paginate_by = 2
    template_name = 'main/booking_list.html'


class BookingDetailView(generic.DetailView):
    model = Booking
    template_name = 'main/booking_detail.html'


def search(request):
    """
    paprasta paieška. query ima informaciją iš paieškos laukelio,
    search_results prafiltruoja pagal įvestą tekstą rezervacijų pavadinimus ir aprašymus.
    Icontains nuo contains skiriasi tuo, kad icontains ignoruoja ar raidės 
    didžiosios/mažosios.
    """
    query = request.GET.get('query')
    search_results = Booking.objects.filter(
        Q(title__icontains=query) | Q(summary__icontains=query))
    return render(request, 'main/search.html', {'bookings': search_results, 'query': query})


@login_required
def posting_create(response):
    if response.method == 'POST':
        form = PostForm(response.POST)

        if form.is_valid():
            posting = form.save(commit=False)
            posting.author = response.user
            posting.save()
            posting.author.posting.add()
            messages.success(response, 'Sėkmingai sukurtas skelbimas!')
            return redirect('posting_detail', pk=posting.pk)
    else:
        form = PostForm()
    context = {
        'form': form,
    }
    return render(response, 'posts/post_form.html', context)


@login_required
def posting_detail(response, pk):
    posting = get_object_or_404(Posting, pk=pk)
    if response.method == 'POST':
        form = BookingForm(response.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.posting = posting
            booking.booker = response.user
            booking.save()
            messages.success(response, 'Rezervacija sėkminga!')
            return redirect('posting_detail', pk=posting.pk)
    else:
        form = BookingForm()
    context = {
        'posting': posting,
        'form': form,
    }
    return render(response, 'posts/posting_detail.html', context)


# @login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    context = {
        'booking': booking,
    }
    return render(request, 'posts/booking_detail.html', context)


# @login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Your booking has been canceled!')
        return redirect('posting_detail', pk=booking.post.pk)
    context = {
        'booking': booking,
    }
    return render(request, 'posts/booking_cancel.html', context)


class PostListView(generic.ListView):
    model = Posting
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']
    paginate_by = 10


class UserPostListView(LoginRequiredMixin, generic.ListView):
    model = Posting
    template_name = 'posts/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Posting.objects.filter(user=user).order_by('-created_at')


class PostCreateView(LoginRequiredMixin, generic.CreateView):
    model = Posting
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('posts:post-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Posting
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('posts:post-list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Posting
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('posts:post-list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user

# ----------------------------------------TRIED SOME DRF----------------------------------------


class PostingList(generics.ListCreateAPIView):
    queryset = Posting.objects.all()
    serializer_class = PostingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostingDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Posting.objects.all()
    serializer_class = PostingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def delete(self, request, *args, **kwargs):
        posting = Posting.objects.filter(
            pk=kwargs['pk'], user=self.request.user)
        if posting.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError('Negalima trinti svetimų pranešimų!')

    def put(self, request, *args, **kwargs):
        posting = Posting.objects.filter(
            pk=kwargs['pk'], user=self.request.user)
        if posting.exists():
            return self.update(request, *args, **kwargs)
        else:
            raise ValidationError('Negalima koreguoti svetimų pranešimų!')


class PostingLikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = PostingLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        posting = Posting.objects.get(pk=self.kwargs['pk'])
        return PostingLike.objects.filter(posting=posting, user=user)

    def perform_create(self, serializer):
        posting = Posting.objects.get(pk=self.kwargs['pk'])
        serializer.save(user=self.request.user, posting=posting)

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError(
                'Jūs nepalikote patiktuko po šiuo pranešimu!')


class ReviewList(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        posting = Posting.objects.get(pk=self.kwargs['pk'])
        serializer.save(user=self.request.user, posting=posting)

    def get_queryset(self):
        posting = Posting.objects.get(pk=self.kwargs['pk'])
        return Review.objects.filter(posting=posting)


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def delete(self, request, *args, **kwargs):
        review = Review.objects.filter(pk=kwargs['pk'], user=self.request.user)
        if review.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError('Negalima trinti svetimų įvertinimų!')

    def put(self, request, *args, **kwargs):
        review = Review.objects.filter(pk=kwargs['pk'], user=self.request.user)
        if review.exists():
            return self.update(request, *args, **kwargs)
        else:
            raise ValidationError('Negalima koreguoti svetimų įvertinimų!')


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny, )

    def delete(self, request, *args, **kwargs):
        user = User.objects.filter(pk=self.request.user.pk)
        if user.exists():
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('User doesn\'t exist.')
