from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Organization, UserProfile 
from .models import Contact, Message, Response

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
        'first_name', 
        'last_name', 
        'organization', 
        'preferred_method',
    )
    list_display_links = (
        'first_name', 
        'last_name', 
        'organization', 
        'preferred_method',
    )
    list_filter = ('organization', 'preferred_method')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('body', 'organization')
    list_display_links = ('body', 'organization')
    list_filter = ('organization', )

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('body', 'contact', 'organization')
    list_display_links = ('body', 'contact', 'organization')
    list_filter = ('body', 'contact', 'organization')

