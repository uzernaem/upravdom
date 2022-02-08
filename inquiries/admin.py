from ast import In
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from .models import Profile, ToDo, Poll, Announcement, Notification, Comment, VoteOption, Vote, Property, Ownership, Info, File

class MyUserAdmin(UserAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Статус', {'fields': ('is_active',)}),
    )



# Register your models here.
admin.site.register(Profile)
# admin.site.register(ToDo)
# admin.site.register(Poll)
# admin.site.register(Announcement)
# admin.site.register(Notification)
# admin.site.register(Comment)
# admin.site.register(VoteOption)
# admin.site.register(Vote)
admin.site.register(Property)
admin.site.register(Ownership)
admin.site.register(Info)
admin.site.register(File)

admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)