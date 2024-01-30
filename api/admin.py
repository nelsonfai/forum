from django.contrib import admin
from .models import CustomUser, Forum, Message, Notification

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff')
    search_fields = ('email', 'username')

class ForumAdmin(admin.ModelAdmin):
    list_display = ('title', 'admin', 'created_date')
    search_fields = ('title', 'admin__email')

class MessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'forum', 'is_anonymous', 'created_date')
    search_fields = ('content', 'author__email', 'forum__title')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'recipient', 'is_read', 'created_date')
    search_fields = ('message__content', 'recipient__email')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Notification, NotificationAdmin)

