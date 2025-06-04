

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Attendance

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('employee_id', 'email', 'role', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'role')
    search_fields = ('employee_id', 'email', 'first_name', 'last_name')
    ordering = ('employee_id',)
    fieldsets = (
        (None, {'fields': ('employee_id', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(CustomUser, CustomUserAdmin)

def mark_as_completed(modeladmin, request, queryset):
    queryset.update(clock_out=True)

mark_as_completed.short_description = 'Mark selected attendance as completed'

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'clock_in', 'clock_out')
    list_filter = ('employee', 'date')
    search_fields = ('employee__employee_id',)
    actions = [mark_as_completed]  
admin.site.register(Attendance, AttendanceAdmin)
