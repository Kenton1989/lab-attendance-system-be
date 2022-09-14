from django.contrib import admin

from .models import Week, Profile, Lab, Course, Group, BaseSession, RegularSession, SpecialSession, MakeUpSession, CheckInRecord

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Define an inline admin descriptor for Profile model
# which acts a bit like a singleton


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

# Define a new User admin


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Week)
admin.site.register(Lab)
admin.site.register(Course)
admin.site.register(Group)
admin.site.register(BaseSession)
admin.site.register(RegularSession)
admin.site.register(SpecialSession)
admin.site.register(MakeUpSession)
admin.site.register(CheckInRecord)
