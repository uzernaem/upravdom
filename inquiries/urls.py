from django.urls import path, include
from django.urls.conf import re_path
from django.views.generic import base
from rest_framework import routers
# from .views import ToDoViewSet, PollViewSet, \
#     PropertyViewSet, \
#     CommentViewSet, \
#     VoteOptionViewSet, VoteViewSet, ProfileViewSet, NotificationViewSet, \
#     AnnouncementViewSet
from .views import announcement_detail, announcement_list, comment_list, get_user, notification_detail, notification_list, poll_list, user_list

router = routers.DefaultRouter()
# router.register(r'announcements', AnnouncementViewSet, basename='Announcements')
# router.register(r'todos', ToDoViewSet, basename='ToDos')
# router.register(r'polls', PollViewSet)
# router.register(r'notifications', NotificationViewSet, basename='Notifications')
# router.register(r'properties', PropertyViewSet)
# router.register(r'comments', CommentViewSet)
# router.register(r'vote_options', VoteOptionViewSet)
# router.register(r'votes', VoteViewSet)
# router.register(r'profiles', ProfileViewSet)

from .views import todo_list, todo_detail

urlpatterns = [
    path('', include(router.urls)),    
    re_path(r'^user$', get_user),
    re_path(r'^users$', user_list),
    re_path(r'^todos$', todo_list),
    re_path(r'^todos/(?P<pk>[0-9]+)$', todo_detail),
    re_path(r'^announcements$', announcement_list),
    re_path(r'^announcements/(?P<pk>[0-9]+)$', announcement_detail),
    re_path(r'^notifications$', notification_list),
    re_path(r'^notifications/(?P<pk>[0-9]+)$', notification_detail),
    re_path(r'^comments/(?P<inquiry_id>[0-9]+)$', comment_list),
    re_path(r'^polls$', poll_list),
]