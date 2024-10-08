from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Account, UserProfile

class AccountAdmin(UserAdmin):
    list_display = ('email','phone_number','first_name','last_name', 'username','last_login','date_joined','is_active')
    list_display_link = ('email','first_name','last_name')
    readonly_fields = ('last_login','date_joined')
    ordering = ('-date_joined',)
    
    filter_horizontal = ()
    list_filter = ()
    filedsets = ()

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src="{}" width="60" style="border-radius:50%;">'.format(object.profile_picture.url))
    
    thumbnail.short_description = 'Imagen de Pefil'
    list_display = ('thumbnail','user','city','state','country')
    
# Register your models here.
admin.site.register(Account,AccountAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
