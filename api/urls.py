from django.urls import path
from .views import ForumListCreateView, ForumDetailView,MessageListCreateView,MessageDetailView,UserCreateView,UserLoginView,UserLogoutView,FreeAccessView,ForumWithMessagesView,SubscribeToForum,UserInfoView,AddLike
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('free-access/', FreeAccessView.as_view(), name='free-access'),
    path('user-info/', UserInfoView.as_view(), name='user-info'),
    path('signup/', UserCreateView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('forums/', ForumListCreateView.as_view(), name='forum-list-create'),#used
    path('forums/<int:pk>/', ForumDetailView.as_view(), name='forum-detail'),
    path('forums/<int:forum_id>/messages/', ForumWithMessagesView.as_view(), name='forum-messages'),#used
    path('subscribe/<int:forum_id>/', SubscribeToForum.as_view(), name='subscribe_to_forum'),

    path('messages/', MessageListCreateView.as_view(), name='message-list-create'), #used create only
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
    path('messages/<int:pk>/like/', AddLike.as_view(), name='message-detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



