from rest_framework import serializers
from .models import Posting, Booking, Review, Message, PostingLike
from django.contrib.auth.models import User


class PostingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    review_count = serializers.SerializerMethodField()
    reviews = serializers.StringRelatedField(many=True, read_only=True)
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Posting
        fields = ['id', 'username', 'user', 'user_id', 'title', 'description', 'start_location', 'end_location',
                  'start_time', 'available_seats', 'price', 'likes', 'review_count', 'reviews', 'created_at', 'updated_at']

    def get_review_count(self, obj):
        return Review.objects.filter(posting=obj).count()

    def get_likes(self, post):
        return PostingLike.objects.filter(post=post).count()


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    posting = serializers.ReadOnlyField(source='posting.id')

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_id', 'reviewee', 'reviewee_id', 'reviewer', 'reviewer_id', 'posting',
                  'rating', 'comment', 'created_at', 'reviews']


class PostingLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostingLike
        fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
