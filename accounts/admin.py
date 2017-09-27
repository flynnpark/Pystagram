from django.contrib import admin
from .models import Profile, Relation

class FollowInline(admin.TabularInline):
    model = Relation
    fk_name = 'from_user'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'nickname', 'user']
    list_display_links = ['nickname', 'user']
    search_fields = ['nickname']
