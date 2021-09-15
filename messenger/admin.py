from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (Autoreply, Contact, Message, MessageLog, 
    Note, Organization, Response, Tag, UserProfile)

admin.site.register(Organization)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'link_to_user',
        'organization',
    )
    list_display_links = (
        'id',
        'organization',
    )
    list_select_related = ('user', 'organization')
    list_filter = ('organization',)

    def link_to_user(self, obj):
        link = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', link, obj.user.username)
    link_to_user.short_description = 'Edit user'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ( 
        'id',
        'first_name', 
        'last_name', 
        'organization', 
        'phone',
        'email',
        'preferred_method',
    )
    list_display_links = (
        'id',
        'first_name', 
        'last_name', 
        'organization', 
        'phone',
        'email',
        'preferred_method',
    )
    list_filter = ('organization', 'preferred_method', 'tags')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'body', 'organization', 'method', 'date_created'
    )
    list_display_links = (
        'body', 'organization', 'method', 'date_created'
    )
    list_filter = ('organization', 'method')

@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('message', 'contact', 'date', 'sender')
    list_display_links = ('message', 'contact', 'date', 'sender')
    list_filter = ('message__organization', 'contact', 'message' )

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('body', 'contact', 'organization')
    list_display_links = ('body', 'contact', 'organization')
    list_filter = ('body', 'contact', 'organization')

@admin.register(Autoreply)
class AutoreplyAdmin(admin.ModelAdmin):
    list_display = ('organization', 'text', 'reply')
    list_display_links = ('organization', 'text', 'reply')
    list_filter = ('organization',)

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('body', 'date', 'author')
    list_display_links = ('body', 'date', 'author')
    list_filter = ('contact', 'message', 'response', 'author')



