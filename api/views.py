# forum/views.py
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAuthenticatedOrReadOnly
from .models import Forum, Message,CustomUser,Notification
from .serializers import ForumSerializer, MessageSerializer,CustomUserSerializer,MessageReadSerializer,CustomUserAdminInfoSerializer
from .permissions import IsForumAdminOrReadOnly, IsMessageAuthorOrAdmin
from rest_framework import status
from rest_framework import serializers
from django.shortcuts import get_object_or_404

User = get_user_model()
class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomUserAdminInfoSerializer(user)
        data = {
            "user": serializer.data,
            "notification": user.mynotification.count()
        }
        return Response(data, status=status.HTTP_200_OK)

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
    def perform_create(self, serializer):
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id})

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        print(user)
        if user and user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def post(self, request, *args, **kwargs):
        request.auth.delete()
        return Response({'success': 'User logged out successfully'})

#used
class ForumListCreateView(generics.ListCreateAPIView):
    serializer_class = ForumSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        filtermood = self.request.query_params.get('filtermood', None)

        if filtermood == 'Subscribed':
            forum = Forum.objects.filter(subscribed_members=user).order_by('created_date')
            return forum
        elif filtermood == "My forums":
            forum = Forum.objects.filter(admin=user).order_by('created_date')
        else:
            return Forum.objects.all()
    def post(self, request, *args, **kwargs):
            user = self.request.user
            title = request.data.get('title')
            description = request.data.get('description')
            tags = request.data.get('tags', [])  

            # Create a new forum
            forum = Forum.objects.create(admin=user, title=title, description=description)
            # Add tags to the forum
            forum.tags.set(tags)

            # Serialize the created forum
            serializer = ForumSerializer(forum)

            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ForumDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    permission_classes = [IsForumAdminOrReadOnly]

#used
class ForumWithMessagesView(APIView):
    def get(self, request, forum_id):
        try:
            # Fetch forum details
            forum = Forum.objects.get(id=forum_id)
            forum.views_count += 1
            forum.save()
            forum_serializer = ForumSerializer(forum)

            # Fetch associated messages
            messages = Message.objects.filter(forum=forum,parent=None)
            message_serializer = MessageSerializer(messages, many=True)
        
            # Combine data
            data = {
                'forum': forum_serializer.data,
                'messages': message_serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except Forum.DoesNotExist:
            return Response({'detail': 'Forum not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        content = request.data.get('content')
        forum_id = request.data.get('forum')  # Assuming you send the forum ID
        is_anonymous = request.data.get('is_anonymous', False)
        parent_id = request.data.get('parent', None)

        # Retrieve forum instance
        try:
            forum = Forum.objects.get(id=forum_id)
        except Forum.DoesNotExist:
            return Response({'error': 'Invalid forum ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        parent = None

        # Check if parent_id is provided
        if parent_id:
            try:
                parent = Message.objects.get(id=parent_id, forum=forum)
            except Message.DoesNotExist:
                return Response({'error': 'Invalid parent ID'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the message
        message = Message.objects.create(
            content=content,
            author=request.user,
            forum=forum,
            is_anonymous=is_anonymous,
            parent=parent
        )
         # Serialize the message instance
        serializer = MessageReadSerializer(message)
        # Return the serialized data in the response
        return Response(serializer.data, status=status.HTTP_201_CREATED)

       
class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsMessageAuthorOrAdmin]

class FreeAccessView(APIView):
    permission_classes = []
    def get(self, request, *args, **kwargs):
        return Response({"message": "This is a free-access view. You can access it without authentication."}, status=status.HTTP_200_OK)


class SubscribeToForum(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, forum_id):
        user = request.user

        # Get the forum object or return 404 if not found
        forum = get_object_or_404(Forum, id=forum_id)
        # Check if the user is already subscribed to the forum
        if user in forum.subscribed_members.all():
            # If subscribed, remove the subscription
            forum.subscribed_members.remove(user)
            forum.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # If not subscribed, add the subscription
            forum.subscribed_members.add(user)
            forum.save()
            return Response(status=status.HTTP_201_CREATED)


class AddLike(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk, format=None):
        message = get_object_or_404(Message, pk=pk)

        message.likes += 1
        message.save()
        if message.parent != None:
            message = get_object_or_404(Message, pk=message.parent.id)

        serializer = MessageSerializer(message)
        return Response(serializer.data)