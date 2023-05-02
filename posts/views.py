from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Posting, Booking, Review, Message
from .forms import PostForm, BookingForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Q


def index(request):
    num_postings = Posting.objects.all().count()
    num_bookings = Booking.objects.all().count()

    num_pending_bookings = Booking.objects.filter(
        status__exact='PENDING').count()

    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_postings': num_postings,
        'num_bookings': num_bookings,
        'num_pending_bookings': num_pending_bookings,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)


def perform_about(request):
    return render(request, 'about.html')


def perform_services(request):
    return render(request, 'services.html')


def perform_contacts(request):
    return render(request, 'contacts.html')


def postings(request):

    postings = Posting.objects.all()
    context = {
        'postings': postings
    }
    print(postings)
    return render(request, 'postings.html', context=context)


def posting(request, posting_id):
    single_posting = get_object_or_404(Posting, pk=posting_id)
    return render(request, 'posting.html', {'posting': single_posting})


class BookingListView(generic.ListView):
    model = Booking
    paginate_by = 2
    template_name = 'booking_list.html'


class BookingDetailView(generic.DetailView):
    model = Booking
    template_name = 'booking_detail.html'


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
    return render(request, 'search.html', {'bookings': search_results, 'query': query})


# @login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Sėkmingai sukurtas skelbimas!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    context = {
        'form': form,
    }
    return render(request, 'posts/post_form.html', context)


# @login_required
def post_detail(request, pk):
    post = get_object_or_404(Posting, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.post = post
            booking.booker = request.user
            booking.save()
            messages.success(request, 'Rezervacija sėkminga!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = BookingForm()
    context = {
        'post': post,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


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
        return redirect('post_detail', pk=booking.post.pk)
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
