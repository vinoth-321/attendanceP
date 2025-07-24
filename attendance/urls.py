from django.urls import path
from . import views
from django.shortcuts import redirect

def redirect_root(request):
    return redirect('login')

urlpatterns = [
    path('',redirect_root),
    path('login/', views.login_view, name='login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/register_staff/', views.register_staff, name='register_staff'),
    path('admin/register_student/', views.register_student, name='register_student'),
    path('admin/add_course/', views.add_course, name='add_course'),
    path('admin/assign_course/', views.assign_course, name='assign_course'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/mark/<int:course_id>/', views.mark_attendance, name='mark_attendance'),
]
