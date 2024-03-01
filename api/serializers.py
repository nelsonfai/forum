# api/serializers.py
from rest_framework import serializers
from .models import Forum, Message, Notification,CustomUser
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)
from rest_framework.exceptions import ValidationError



class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'profile_picture', 'is_private','password','imageurl']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    def create(self, validated_data):
        user = CustomUser.objects.create_user(

            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['username'],
        )
        return user

class CustomUserAdminInfoSerializer(serializers.ModelSerializer):
    imageurl = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['id','profile_picture', 'username','is_private','email','imageurl']

    def get_imageurl (self,obj):
        if obj.profile_picture:
            print('image url -------',obj.profile_picture.url)
            return obj.profile_picture.url
class MessageSerializer(serializers.ModelSerializer):
    author = CustomUserAdminInfoSerializer()
    forum = serializers.StringRelatedField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'content', 'author', 'forum', 'is_anonymous', 'parent', 'created_date',"replies","likes"]
    def get_replies(self, obj):
        serializer = self.__class__(obj.replies.all(), many=True)
        return serializer.data



class MessageWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'author', 'forum', 'is_anonymous', 'parent', 'created_date']

class MessageReadSerializer(serializers.ModelSerializer):
    forum = serializers.StringRelatedField()
    author = CustomUserAdminInfoSerializer()

    class Meta:
        model = Message
        fields = ['id', 'content', 'author', 'forum', 'is_anonymous', 'parent', 'created_date']

class NotificationSerializer(serializers.ModelSerializer):
    message = MessageSerializer()

    class Meta:
        model = Notification
        fields = ['id', 'message', 'recipient', 'is_read', 'created_date']

class ForumSerializer(TaggitSerializer, serializers.ModelSerializer):
    admin_info = CustomUserAdminInfoSerializer(source='admin', read_only=True)
    message_count = serializers.SerializerMethodField()
    views_count = serializers.IntegerField()
    tags = TagListSerializerField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Forum
        fields = ['id', 'title', 'tags', 'description', 'admin', 'admin_info', 'message_count', 'views_count', 'created_date', 'is_subscribed']

    def get_message_count(self, obj):
        return obj.message_count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_user_subscribed(request.user)
        return False