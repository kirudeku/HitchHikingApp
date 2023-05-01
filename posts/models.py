from django.db import models
from django.contrib.auth.models import User


class Posting(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Pastabos, jei yra")
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    available_seats = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=8, decimal_places=2, help_text="Kaina eurais")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cover = models.ImageField('Viršelis', upload_to='covers', null=True)

    class Meta:
        verbose_name = 'Skelbimas'
        verbose_name_plural = 'Skelbimai'


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    posting = models.ForeignKey(Posting, on_delete=models.CASCADE)
    num_seats = models.PositiveIntegerField()
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rezervacija'
        verbose_name_plural = 'Rezervacijos'


class Review(models.Model):
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews_written')
    reviewee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews_received')
    posting = models.ForeignKey(Posting, on_delete=models.CASCADE, null=True)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Įvertinimas'
        verbose_name_plural = 'Įvertinimai'


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_messages')
    posting = models.ForeignKey(Posting, on_delete=models.CASCADE, null=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Žinutė'
        verbose_name_plural = 'Žinutės'
