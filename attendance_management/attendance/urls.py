"""
URL Configuration for Attendance App
Maps URLs to views
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/update/', views.student_update, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),

    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/update/', views.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),

    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('attendance/view/', views.view_attendance, name='view_attendance'),
    path('attendance/percentage/', views.attendance_percentage, name='attendance_percentage'),
]
