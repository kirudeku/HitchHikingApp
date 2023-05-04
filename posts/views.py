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
    return render(request, 'posts/postings.html', context=context)


def posting(request, posting_id):
    single_posting = get_object_or_404(Posting, pk=posting_id)
    return render(request, 'posts/posting.html', {'posting': single_posting})


def search(request):
    """
    paprasta paieška. query ima informaciją iš paieškos laukelio,
    search_results prafiltruoja pagal įvestą tekstą rezervacijų pavadinimus ir aprašymus.
    Icontains nuo contains skiriasi tuo, kad icontains ignoruoja ar raidės 
    didžiosios/mažosios.
    """
    query = request.GET.get('query')
    search_results = Posting.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query) | Q(start_location__icontains=query)| Q(end_location__icontains=query)| Q(start_time__icontains=query)| Q(available_seats__icontains=query)| Q(price__icontains=query))
    return render(request, 'main/search.html', {'posting': search_results, 'query': query})


@login_required
def booking_detail(response, pk):
    booking = get_object_or_404(Booking, pk=pk)
    context = {
        'booking': booking,
    }
    return render(response, 'posts/booking_detail.html', context)


@login_required
def booking_cancel(response, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if response.method == 'POST':
        booking.delete()
        messages.success(response, 'Rezervacija atšaukta sėkmingai!')
        return redirect('post-detail', pk=booking.post.pk)
    context = {
        'booking': booking,
    }
    return render(response, 'posts/booking_cancel.html', context)

# -----------------------------------Posting view classes----------------------------
class PostCreateView(LoginRequiredMixin, generic.CreateView):
    model = Posting
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        self.object.save()
        self.success_url = reverse_lazy(
            'post-detail', kwargs={'pk': self.object.pk})
        return response


class PostDetailView(generic.DetailView):
    model = Posting
    template_name = 'posts/post_detail.html'
    context_object_name = 'posting'

    def post(self, request, *args, **kwargs):
        posting = self.get_object()
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.posting = posting
            booking.booker = request.user
            booking.save()
            messages.success(request, 'Rezervacija sėkminga!')
            return redirect('post-detail', pk=posting.pk)
        else:
            context = self.get_context_data(object=self.object, form=form)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BookingForm()
        return context


class PostListView(generic.ListView):
    model = Posting
    template_name = 'posts/postings.html'
    context_object_name = 'postings'
    ordering = ['-created_at']
    paginate_by = 10


class UserPostListView(LoginRequiredMixin, generic.ListView):
    model = Posting
    template_name = 'posts/user_posts.html'
    context_object_name = 'postings'
    success_url = reverse_lazy('user-posts')
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Posting.objects.filter(user=user).order_by('-created_at')


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Posting
    form_class = PostForm
    template_name = 'posts/post_form.html'
    label = 'update'

    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Posting
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('postings')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user
    
# ---------------------------Booking view classes------------------------------------
    
class BookingCreateView(LoginRequiredMixin, generic.CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 'PENDING'
        form.instance.posting_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('posting-detail', kwargs={'pk': self.kwargs['pk']})    

class BookingListView(generic.ListView):
    model = Booking
    paginate_by = 2
    template_name = 'posts/booking_list.html'


class BookingDetailView(generic.DetailView):
    model = Booking
    template_name = 'posts/booking_detail.html'

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
