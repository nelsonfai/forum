

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from taggit.managers import TaggableManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_private = models.BooleanField(default=False) 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    


class Forum(models.Model):
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    subscribed_members = models.ManyToManyField(CustomUser, related_name='subscribed_forums', blank=True)  # Set blank=True to make it optional
    tags = TaggableManager(blank=True)  # Set blank=True to make it optional
    created_date = models.DateTimeField(auto_now_add=True)
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    def is_user_subscribed(self, user):
        return self.subscribed_members.filter(id=user.id).exists()
    def message_count(self):
        return Message.objects.filter(forum = self).count()

class Message(models.Model):
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='messages')
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    is_anonymous = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f"Message by {self.author} in {self.forum.title}"

    def get_replies(self):
        return self.replies.all()

    def add_reply(self, content, author, is_anonymous=False):
        reply = Message.objects.create(
            content=content,
            author=author,
            forum=self.forum,
            is_anonymous=is_anonymous,
            parent=self,
        )
        return reply

    def has_replies(self):
        return self.replies.exists()

    def delete_with_replies(self):
        if self.has_replies():
            self.replies.all().delete()
        self.delete()


class Notification(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name="mynotification")
    is_read = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.message} to {self.recipient}"
