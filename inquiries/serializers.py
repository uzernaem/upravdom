from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import PrimaryKeyRelatedField
from .models import Announcement, Attachment, ToDo, Poll, Notification, Property, Comment, ToDoCategory, VoteOption, Vote, Profile, Info


class UserSerializer(serializers.ModelSerializer):
    is_manager = PrimaryKeyRelatedField(source='profile.is_manager', read_only=True)
    phone_number = PrimaryKeyRelatedField(source='profile.phone_number', read_only=True)

    class Meta:
        model = User
        fields = 'id', 'username', 'first_name', 'last_name', 'phone_number', 'is_manager'


class CommentSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
            representation = super(CommentSerializer, self).to_representation(instance)
            representation['comment_creator'] = UserSerializer(instance.comment_creator).data
            return representation

    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        comment = Comment(
           inquiry=validated_data['inquiry'],
           comment_text=validated_data['comment_text'],
           comment_creator=validated_data['comment_creator']
        )
        comment.save()
        return comment


class ToDoSerializer(serializers.ModelSerializer):
    todo_category_name = serializers.CharField(read_only=True, source='get_todo_category_display')
    todo_status_name = serializers.CharField(read_only=True, source='get_todo_status_display')
    todo_priority_name = serializers.CharField(read_only=True, source='get_todo_priority_display')
    comments = CommentSerializer(read_only=True, source='comment_set', many=True)

    def to_representation(self, instance):
            representation = super(ToDoSerializer, self).to_representation(instance)
            representation['inquiry_creator'] = UserSerializer(instance.inquiry_creator).data            
            representation['todo_assigned_to'] = UserSerializer(instance.todo_assigned_to).data
            return representation

    class Meta:
        model = ToDo
        fields = '__all__'

    def create(self, validated_data):
        todo = ToDo(
            inquiry_creator=validated_data['inquiry_creator'],
            inquiry_title=validated_data['inquiry_title'],
            inquiry_text=validated_data['inquiry_text'],
            todo_category=validated_data['todo_category']
        )
        todo.save()
        return todo

class ToDoListSerializer(serializers.ModelSerializer):
    todo_category_name = serializers.CharField(read_only=True, source='get_todo_category_display')
    todo_status_name = serializers.CharField(read_only=True, source='get_todo_status_display')
    todo_priority_name = serializers.CharField(read_only=True, source='get_todo_priority_display')

    def to_representation(self, instance):
            representation = super(ToDoListSerializer, self).to_representation(instance)
            representation['inquiry_creator'] = UserSerializer(instance.inquiry_creator).data
            return representation

    class Meta:
        model = ToDo
        fields = '__all__'


# class ToDoUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ToDo
#         fields = 'inquiry_updated_at', 'todo_assigned_to', 'todo_status'

#     def update(self, instance, validated_data):
#         instance.inquiry_updated_at = validated_data.get('inquiry_updated_at', instance.inquiry_updated_at)
#         instance.todo_assigned_to = validated_data.get('todo_assigned_to', instance.todo_assigned_to)
#         instance.todo_status = validated_data.get('todo_status', instance.todo_status)
#         print('used')
#         instance.save()
#         return instance


class ToDoCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ToDoCategory
        fields = '__all__'


class AnnouncementSerializer(serializers.ModelSerializer):
    announcement_category_name = serializers.CharField(read_only=True, source='get_announcement_category_display')
    comments = CommentSerializer(read_only=True, source='comment_set', many=True)
    
    class Meta:
        model = Announcement
        fields = '__all__'
    

    def to_representation(self, instance):
            representation = super(AnnouncementSerializer, self).to_representation(instance)
            representation['inquiry_creator'] = UserSerializer(instance.inquiry_creator).data
            return representation

    def create(self, validated_data):
        announcement = Announcement(
            inquiry_title=validated_data['inquiry_title'],            
            inquiry_creator=validated_data['inquiry_creator'],
            inquiry_text=validated_data['inquiry_text'],
            announcement_is_visible=validated_data['announcement_is_visible'],
            announcement_auto_invisible_date=validated_data['announcement_auto_invisible_date'],
            announcement_category=validated_data['announcement_category']
        )
        announcement.save()
        return announcement


class AnnouncementListSerializer(serializers.ModelSerializer):
    announcement_category_name = serializers.CharField(read_only=True, source='get_announcement_category_display')
    
    class Meta:
        model = Announcement
        fields = '__all__'
    

    def to_representation(self, instance):
            representation = super(AnnouncementListSerializer, self).to_representation(instance)
            representation['inquiry_creator'] = UserSerializer(instance.inquiry_creator).data
            return representation


    # def update(self, instance, validated_data):
    #     instance.inquiry_updated_at = validated_data.get('inquiry_updated_at', instance.inquiry_updated_at)
    #     instance.announcement_is_visible = validated_data.get('announcement_is_visible', instance.announcement_is_visible)
    #     instance.announcement_auto_invisible_date = validated_data.get('announcement_auto_invisible_date', instance.announcement_auto_invisible_date)
    #     instance.save()
    #     return instance

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'


class VoteOptionSerializer(serializers.ModelSerializer):    
    votes = VoteSerializer(read_only=True, source='vote_set', many=True)

    class Meta:
        model = VoteOption
        fields = '__all__'

    def create(self, validated_data):
        voteoption = VoteOption(
           vote_option_text=validated_data['vote_option_text'],
           poll=validated_data['poll']
        )
        voteoption.save()
        return voteoption


class PollSerializer(serializers.ModelSerializer):
    vote_options = VoteOptionSerializer(read_only=True, source='voteoption_set', many=True)

    class Meta:
        model = Poll
        fields = '__all__'

    def to_representation(self, instance):
            representation = super(PollSerializer, self).to_representation(instance)
            representation['inquiry_creator'] = UserSerializer(instance.inquiry_creator).data
            return representation

    def create(self, validated_data):
        # user = self.context['request'].user
        poll = Poll(
            inquiry_title=validated_data['inquiry_title'],            
            inquiry_creator=validated_data['inquiry_creator'],
            inquiry_text=validated_data['inquiry_text'],
            # poll_open=validated_data['poll_open'],
            poll_preliminary_results=validated_data['poll_preliminary_results'],
            poll_deadline=validated_data['poll_deadline']
        )
        poll.save()
        return poll

    def update(self, instance, validated_data):
        instance.inquiry_updated_at = validated_data.get('inquiry_updated_at', instance.inquiry_updated_at)
        # instance.inquiry_is_done = validated_data.get('inquiry_is_done', instance.inquiry_is_done)
        instance.save()
        return instance


class NotificationSerializer(serializers.ModelSerializer):
    notification_category_name = serializers.CharField(read_only=True, source='get_notification_category_display')
    class Meta:
        model = Notification
        fields = '__all__'

    def create(self, validated_data):
        notification = Notification(
            inquiry_title=validated_data['inquiry_title'],
            inquiry_text=validated_data['inquiry_text'],
            notification_recipient=validated_data['notification_recipient'],
            notification_category=validated_data['notification_category']
        )
        notification.save()
        return notification

    # def update(self, instance, validated_data):
    #     instance.inquiry_updated_at = validated_data.get('inquiry_updated_at', instance.inquiry_updated_at)
    #     # instance.inquiry_is_done = validated_data.get('inquiry_is_done', instance.inquiry_is_done)
    #     instance.notification_is_read = validated_data.get('notification_is_read', instance.notification_is_read)
    #     instance.save()
    #     return instance


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'


class InfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Info
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = "__all__"