"""
Admin configuration for Attendance Management System
Registers models with Django admin panel
"""
from django.contrib import admin
from .models import Student, Subject, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Student model
    """
    list_display = ['roll_number', 'name', 'department', 'year', 'has_login', 'created_at']
    list_filter = ['department', 'year', 'created_at']
    search_fields = ['roll_number', 'name']
    ordering = ['roll_number']

    fieldsets = (
        ('Student Information', {
            'fields': ('roll_number', 'name', 'department', 'year')
        }),
        ('Login Access', {
            'fields': ('user',),
            'description': 'Link to User account for login access'
        }),
    )

    def has_login(self, obj):
        """Display whether student has login access"""
        return obj.user is not None
    has_login.boolean = True
    has_login.short_description = 'Login Enabled'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """
    Admin configuration for Subject model
    """
    list_display = ['subject_code', 'subject_name', 'department', 'year', 'created_at']
    list_filter = ['department', 'year', 'created_at']
    search_fields = ['subject_code', 'subject_name']
    ordering = ['subject_code']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """
    Admin configuration for Attendance model
    """
    list_display = ['date', 'student', 'subject', 'status', 'created_at']
    list_filter = ['status', 'date', 'subject', 'created_at']
    search_fields = ['student__roll_number', 'student__name', 'subject__subject_code']
    date_hierarchy = 'date'
    ordering = ['-date', 'student__roll_number']

    # Prevent duplicate entries
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing object
            return ['student', 'subject', 'date']
        return []

    # Custom save to validate
    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except Exception as e:
            from django.contrib import messages
            messages.error(request, str(e))
