from django.contrib import admin

from .models import Week, Profile, Lab, Course, Group, BaseSession, RegularSession, SpecialSession, MakeUpSession, CheckInRecord

admin.site.register(Week)
admin.site.register(Profile)
admin.site.register(Lab)
admin.site.register(Course)
admin.site.register(Group)
admin.site.register(BaseSession)
admin.site.register(RegularSession)
admin.site.register(SpecialSession)
admin.site.register(MakeUpSession)
admin.site.register(CheckInRecord)
