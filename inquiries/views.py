from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse

from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, FileUploadParser
from inquiries.serializers import UserSerializer, AnnouncementSerializer, ToDoSerializer, PollSerializer, NotificationSerializer, \
    CommentSerializer, VoteOptionSerializer, VoteSerializer, ProfileSerializer, ToDoCategorySerializer, InfoSerializer, ToDoListSerializer, AnnouncementListSerializer, \
    FileSerializer
from inquiries.models import Announcement, ToDo, Poll, Notification, Info, Property, Comment, VoteOption, Vote, Profile, ToDoCategory, Inquiry, File
from django.contrib.auth.models import User

# Create your views here.
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def user_list(request):
    if request.method == 'GET':
        if request.user.profile.is_manager:
            users = User.objects.all()
            users_serializer = UserSerializer(users, many=True)
            return JsonResponse(users_serializer.data, safe=False)    
        return JsonResponse({'message': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'POST':
        if request.user.profile.is_manager:
            user_data = JSONParser().parse(request)
            users_serializer = UserSerializer(data=user_data)
            if users_serializer.is_valid():
                users_serializer.save()
                return JsonResponse(users_serializer.data, status=status.HTTP_201_CREATED) 
            return JsonResponse(users_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'message': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def get_user(request):
    if request.method == 'GET':
        user = UserSerializer(request.user)
        return JsonResponse(user.data, safe=False)

    elif request.method == 'PUT':
        user_data = JSONParser().parse(request)
        User.objects.filter(pk=request.user.pk).update(
            first_name = user_data['first_name'],
            last_name = user_data['last_name'],
            email = user_data['email'])
        Profile.objects.filter(pk=request.user.pk).update(phone_number = user_data['phone_number'])
        return JsonResponse({'message': 'Профиль пользователя обновлён'}, status=status.HTTP_200_OK)
        



@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def todo_list(request):
    if request.method == 'GET':
        
        if request.user.profile.is_manager == True:
            todos = ToDo.objects.all()
        else:
            todos = ToDo.objects.filter(inquiry_creator=request.user)
        
        title = request.GET.get('inquiry_title', None)
        if title is not None:
            todos = todos.filter(title__icontains=title)

        todos_serializer = ToDoListSerializer(todos, many=True)
        return JsonResponse(todos_serializer.data, safe=False)

    elif request.method == 'POST':
        todo_data = JSONParser().parse(request)
        todo_data['inquiry_creator'] = request.user.id
        todo_serializer = ToDoSerializer(data=todo_data)
        if todo_serializer.is_valid():
            todo_serializer.save()
            return JsonResponse(todo_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(todo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def voteoption_list(request):

    if request.method == 'GET':
        voteoptions = VoteOption.objects.all()
        voteoption_serializer = VoteOptionSerializer(voteoptions, many=True)
        return JsonResponse(voteoption_serializer.data, safe=False)

    if request.method == 'POST':
        voteoption_data = JSONParser().parse(request)
        voteoption_serializer = VoteOptionSerializer(data=voteoption_data, many=True)
        if voteoption_serializer.is_valid():
            voteoption_serializer.save()
            return JsonResponse(voteoption_serializer.data, status=status.HTTP_201_CREATED, safe=False)
        return JsonResponse(voteoption_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'message': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def post_vote(request):

    if request.method == 'POST':
        vote_data = JSONParser().parse(request)
        vote_data['voter'] = request.user.id

        vote_options = VoteOption.objects.get(pk=vote_data['selected_option']).poll.voteoption_set.all()
        for option in vote_options:
            if option.vote_set.values().filter(voter_id=request.user.id):
                return JsonResponse({'message': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

        vote_serializer = VoteSerializer(data=vote_data)
        if vote_serializer.is_valid():
            vote_serializer.save()
            return JsonResponse(vote_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(vote_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'message': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def comment_list(request, inquiry_id):

    if request.method == 'POST':
        comment_data = JSONParser().parse(request)
        comment_data['comment_creator'] = request.user.id
        comment_serializer = CommentSerializer(data=comment_data) 
        if Announcement.objects.filter(inquiry_id=inquiry_id).exists():
            if comment_serializer.is_valid():
                comment_serializer.save()
                return JsonResponse(comment_serializer.data, status=status.HTTP_201_CREATED)
            return JsonResponse(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif ToDo.objects.filter(inquiry_id=inquiry_id).exists():
            if ((ToDo.objects.get(inquiry_id=inquiry_id).inquiry_creator.id==request.user.id) | request.user.profile.is_manager):
                if comment_serializer.is_valid():
                    comment_serializer.save()
                    return JsonResponse(comment_serializer.data, status=status.HTTP_201_CREATED)
                return JsonResponse(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'message': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def announcement_list(request):

    if request.method == 'GET':

        announcements = Announcement.objects.filter(
            Q(announcement_is_visible = True, announcement_auto_invisible_date__gt=datetime.today().date()) | 
            Q(inquiry_creator=request.user))
        title = request.GET.get('inquiry_title', None)
        if title is not None:
            announcements = announcements.filter(title__icontains=title)
        
        announcements_serializer = AnnouncementListSerializer(announcements, many=True)
        return JsonResponse(announcements_serializer.data, safe=False)

    elif request.method == 'POST':
        announcement_data = JSONParser().parse(request)
        announcement_data['inquiry_creator'] = request.user.id
        announcement_data['announcement_auto_invisible_date'] = announcement_data['announcement_auto_invisible_date'][0:10]
        announcements_serializer = AnnouncementSerializer(data=announcement_data)
        if announcements_serializer.is_valid():
            announcements_serializer.save()
            return JsonResponse(announcements_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(announcements_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def poll_list(request):

    if request.method == 'GET':

        polls = Poll.objects.all()
        title = request.GET.get('inquiry_title', None)
        if title is not None:
            polls = polls.filter(title__icontains=title)
        
        polls_serializer = PollSerializer(polls, many=True)
        return JsonResponse(polls_serializer.data, safe=False)

    elif request.method == 'POST':
        polls_data = JSONParser().parse(request)
        polls_data['inquiry_creator'] = request.user.id
        polls_serializer = PollSerializer(data=polls_data)
        if polls_serializer.is_valid():
            poll = polls_serializer.save()
            for option in polls_data['vote_options']:
                option['poll'] = poll.inquiry_id
            vote_options = VoteOptionSerializer(data=polls_data['vote_options'], many=True)
            if vote_options.is_valid():
                vote_options.save()
            return JsonResponse(polls_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(polls_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def notification_list(request):

    if request.method == 'GET':
        notifications = Notification.objects.filter(notification_recipient=request.user)
        title = request.GET.get('inquiry_title', None)
        if title is not None:
            notifications = notifications.filter(title__icontains=title)
        
        notifications_serializer = NotificationSerializer(notifications, many=True)
        return JsonResponse(notifications_serializer.data, safe=False)

    elif request.method == 'POST':
        notification_data = JSONParser().parse(request)
        notification_data['inquiry_creator'] = request.user.id
        notifications_serializer = NotificationSerializer(data=notification_data)
        if notifications_serializer.is_valid():
            notifications_serializer.save()
            return JsonResponse(notifications_serializer.data, status=status.HTTP_201_CREATED) 
        return JsonResponse(notifications_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def info_panel(request):

    if request.method == 'GET':
        infos = Info.objects.all()

        
        infos_serializer = InfoSerializer(infos, many=True)
        return JsonResponse(infos_serializer.data, safe=False)
        

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def announcement_detail(request, pk):
    try: 
        announcement = Announcement.objects.get(pk=pk)
    except Announcement.DoesNotExist: 
        return JsonResponse({'message': 'Объявление не существует'}, status=status.HTTP_404_NOT_FOUND) 

    if request.method == 'GET': 
        announcement_serializer = AnnouncementSerializer(announcement)
        data = JsonResponse(announcement_serializer.data)
        return data 


    elif request.method == 'PUT': 
        if announcement.inquiry_creator == request.user:
            announcement_data = JSONParser().parse(request)
            Announcement.objects.filter(pk=pk).update(
                announcement_is_visible = announcement_data['announcement_is_visible'],
                announcement_auto_invisible_date = announcement_data['announcement_auto_invisible_date'],
                inquiry_updated_at = timezone.now())
            return JsonResponse({'message': 'Статус публикации изменён'}, status=status.HTTP_200_OK)
        return JsonResponse({'message': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)


    elif request.method == 'DELETE':
        if announcement.inquiry_creator == request.user:
            Announcement.objects.filter(pk=pk).delete()
            return JsonResponse({'message': 'Объявление удалено'}, status=status.HTTP_200_OK)
        return JsonResponse({'message': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def poll_detail(request, pk):
    try: 
        poll = Poll.objects.get(pk=pk)
    except Poll.DoesNotExist: 
        return JsonResponse({'message': 'Голосование не существует'}, status=status.HTTP_404_NOT_FOUND) 

    if request.method == 'GET': 
        poll_serializer = PollSerializer(poll)
        data = JsonResponse(poll_serializer.data)
        return data
        

@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def notification_detail(request, pk):
    try: 
        notification = Notification.objects.get(pk=pk)
    except Notification.DoesNotExist: 
        return JsonResponse({'message': 'Уведомление не существует'}, status=status.HTTP_404_NOT_FOUND) 

    if request.method == 'GET': 
        notification_serializer = NotificationSerializer(notification)
        data = JsonResponse(notification_serializer.data)
        return data

    elif request.method == 'PUT': 
        if notification.notification_recipient == request.user:
            Notification.objects.filter(pk=pk).update(
                notification_is_read = True,
                inquiry_updated_at = timezone.now())
            return JsonResponse({'message': 'Уведомление прочтено получателем'}, status=status.HTTP_200_OK)
        return JsonResponse({'message': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

 
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def todo_detail(request, pk):
    try:
        todo = ToDo.objects.get(pk=pk)
    except ToDo.DoesNotExist:
        return JsonResponse({'message': 'Заявка не существует'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if ((todo.inquiry_creator==request.user) | (request.user.profile.is_manager)):
            todo_serializer = ToDoSerializer(todo)
            data = JsonResponse(todo_serializer.data)
            return data
        return JsonResponse({'message': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'PUT':
        if (((todo.todo_status == 'n') | (todo.todo_status == 'w')) &
         ((todo.todo.todo_assigned_to == request.user) | (todo.todo.todo_assigned_to is None)) & (request.user.profile.is_manager)):
            todo_data = JSONParser().parse(request)
            ToDo.objects.filter(pk=pk).update(
                todo_assigned_to = todo_data['todo_assigned_to'],
                todo_status = todo_data['todo_status'],
                inquiry_updated_at = timezone.now())
            return JsonResponse({'message': 'Статус заявки и исполнитель обновлены'}, status=status.HTTP_200_OK)
        elif ((todo.todo_status == 'r') & (todo.inquiry_creator==request.user)):
            todo_data = JSONParser().parse(request)
            ToDo.objects.filter(pk=pk).update(todo_status = todo_data['todo_status'],
                inquiry_updated_at = timezone.now())
            return JsonResponse({'message': 'Статус заявки обновлён'}, status=status.HTTP_200_OK)
        return JsonResponse({'message': 'Доступ запрещён'}, status=status.HTTP_403_FORBIDDEN)

class FileUploadView(APIView):
    parser_class = (FileUploadParser,)
    
    def post(self, request, *args, **kwargs):
      
      file_serializer = FileSerializer(data=request.data)

      if file_serializer.is_valid():
          file_serializer.save()
          return Response(file_serializer.data, status=status.HTTP_201_CREATED)
      else:
          return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def file_download(request, pk):
    try: 
        file = File.objects.get(pk=pk)
    except Notification.DoesNotExist: 
        return JsonResponse({'message': 'Файл не существует'}, status=status.HTTP_404_NOT_FOUND) 

    if request.method == 'GET': 
        file_serializer = FileSerializer(file)
        data = JsonResponse(file_serializer.data)       
        return data

    elif request.method == 'PUT':
        request.data['id'] = pk
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file = File.objects.get(pk=pk)
            file.file.delete()
            file.file = request.data['file']
            file.save()
            return JsonResponse({'message': 'Файл обновлён'}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def file_upload(request):
    if request.method == 'POST':
        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            return JsonResponse(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'POST', 'DELETE'])
# @permission_classes([permissions.IsAuthenticated])
# def todocategory_list(request):
#     if request.method == 'GET':
#         categories = ToDoCategory.objects.all()
#         categories_serializer = ToDoCategorySerializer(categories, many=True)
#         return JsonResponse(categories_serializer.data, safe=False)
#     categories_serializer = ToDoCategorySerializer()
#     return JsonResponse(categories_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'PUT', 'DELETE'])
# @permission_classes([permissions.IsAuthenticated])
# def todocategory_detail(request, pk):
#     try: 
#         category = ToDoCategory.objects.get(pk=pk) 
#     except ToDoCategory.DoesNotExist: 
#         return JsonResponse({'message': 'Категория не существует'}, status=status.HTTP_404_NOT_FOUND) 

#     if request.method == 'GET': 
#         todocategory_serializer = ToDoCategorySerializer(category) 
#         return JsonResponse(todocategory_serializer.data) 

#     elif request.method == 'PUT': 
#         todocategory_data = JSONParser().parse(request)
#         todocategory_serializer = ToDoCategorySerializer(category, data=todocategory_data) 
#         if todocategory_serializer.is_valid(): 
#             todocategory_serializer.save() 
#             return JsonResponse(todocategory_serializer.data) 
#         return JsonResponse(todocategory_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


# class ToDoViewSet(viewsets.ModelViewSet):
#     serializer_class = ToDoSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return ToDo.objects.filter(Q(inquiry_creator=user) | Q(todo_assigned_to=user))


# class AnnouncementViewSet(viewsets.ModelViewSet):
#     serializer_class = AnnouncementSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return Announcement.objects.filter(Q(announcement_auto_invisible_date__gt=date.today(), announcement_is_visible=True) | Q(inquiry_creator=user) | Q(announcement_auto_invisible_date__isnull=True))


# class PollViewSet(viewsets.ModelViewSet):
#     queryset = Poll.objects.all()
#     serializer_class = PollSerializer
#     permission_classes = [permissions.IsAuthenticated]


# class NotificationViewSet(viewsets.ModelViewSet):
#     serializer_class = NotificationSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         return Notification.objects.filter(Q(inquiry_creator=user) | Q(notification_recipient=user))


# class PropertyViewSet(viewsets.ModelViewSet):
#     queryset = Property.objects.all()
#     serializer_class = AnnouncementSerializer
#     permission_classes = [permissions.IsAuthenticated]


# class CommentViewSet(viewsets.ModelViewSet):
#     queryset = Comment.objects.all()
#     serializer_class = CommentSerializer
#     permission_classes = [permissions.IsAuthenticated]


# class VoteOptionViewSet(viewsets.ModelViewSet):
#     queryset = VoteOption.objects.all()
#     serializer_class = VoteOptionSerializer
#     permission_classes = [permissions.IsAuthenticated]


# class VoteViewSet(viewsets.ModelViewSet):
#     queryset = Vote.objects.all()
#     serializer_class = VoteSerializer
#     permission_classes = [permissions.IsAuthenticated]


# class ProfileViewSet(viewsets.ModelViewSet):
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer
#     permission_classes = [permissions.IsAuthenticated]


