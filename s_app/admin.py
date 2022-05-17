from django.contrib import admin
from .models import *


class EmployeekAdmin(admin.ModelAdmin):
    list_display = ('emp_id', 'name', 'age', 'gender', 'mobile', 'designation', 'shift')


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('emp_id', 'name', 'designation', 'shift', 'enter', 'exit')
    # list_display = ('name', 'enter', 'exit')


admin.site.register(Employee, EmployeekAdmin)
admin.site.register(EmployeeImage)
admin.site.register(UnidentifiedFaces)
admin.site.register(Attendance, AttendanceAdmin)
