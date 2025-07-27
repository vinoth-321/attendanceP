from django.urls import path
from . import views
from django.shortcuts import redirect

def redirect_root(request):
    return redirect('login')

urlpatterns = [
    path('', redirect_root),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # ✅ Added logout

    # Admin Views
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/register_staff/', views.register_staff, name='register_staff'),
    path('admin/register_student/', views.register_student, name='register_student'),
    path('admin/add_course/', views.add_course, name='add_course'),
    path('admin/assign_course/', views.assign_course, name='assign_course'),
    path('admin/attendance/', views.attendance_view, name='attendance_view'),
     path('admin/modify_staff/', views.modify_staff_list, name='modify_staff_list'),
    path('admin/modify_staff/<int:staff_id>/', views.modify_staff_detail, name='modify_staff_detail'),
    path('admin/delete_staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),

   
path('admin/modify_course/', views.modify_course_list, name='modify_course_list'),
path('admin/modify_course/<int:course_id>/', views.modify_course, name='modify_course'),


path('admin/modify_student/', views.modify_student_list, name='modify_student_list'),
path('admin/modify_student/<int:student_id>/', views.modify_student, name='modify_student'),

    
    path('admin/delete_student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('admin/delete_course/<int:course_id>/', views.delete_course, name='delete_course'),

    # Staff Views
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/mark/<int:course_id>/', views.mark_attendance, name='mark_attendance'),

    path('export-attendance/', views.export_attendance_csv, name='export_attendance_csv'),

]
