from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings

from .models import Staff, Student, Course, AttendanceRecord
from .forms import StaffRegisterForm, StudentRegisterForm, CourseForm, AssignCourseForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('staff_dashboard')
    return render(request, 'login.html')

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@user_passes_test(lambda u: u.is_superuser)
def register_staff(request):
    if request.method == 'POST':
        form = StaffRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Staff.objects.create(user=user)
            return redirect('admin_dashboard')
    else:
        form = StaffRegisterForm()
    return render(request, 'register_staff.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def register_student(request):
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            Student.objects.create(
                name=form.cleaned_data['name'],
                roll_number=form.cleaned_data['roll_number'],
                course=form.cleaned_data['course']
            )
            return redirect('admin_dashboard')
    else:
        form = StudentRegisterForm()
    return render(request, 'register_student.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = CourseForm()
    return render(request, 'add_course.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def assign_course(request):
    if request.method == 'POST':
        form = AssignCourseForm(request.POST)
        if form.is_valid():
            staff_user = form.cleaned_data['staff']
            course = form.cleaned_data['course']
            staff = Staff.objects.get(user=staff_user)
            course.staff = staff
            course.save()
            return redirect('admin_dashboard')
    else:
        form = AssignCourseForm()
    return render(request, 'assign_course.html', {'form': form})

@login_required
def staff_dashboard(request):
    staff = Staff.objects.get(user=request.user)
    courses = Course.objects.filter(staff=staff)
    return render(request, 'staff_dashboard.html', {'courses': courses})

@login_required
def mark_attendance(request, course_id):
    staff = Staff.objects.get(user=request.user)
    course = get_object_or_404(Course, id=course_id, staff=staff)
    students = course.student_set.all()

    if request.method == 'POST':
        present_ids = request.POST.getlist('present')
        for student in students:
            is_present = str(student.id) in present_ids
            AttendanceRecord.objects.create(student=student, course=course, is_present=is_present)

        # Send email to admin
        present = [s.name for s in students if str(s.id) in present_ids]
        absent = [s.name for s in students if str(s.id) not in present_ids]

        send_mail(
            'Attendance Report',
            f'Course: {course.name}\nPresent: {present}\nAbsent: {absent}',
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )

        return redirect('staff_dashboard')

    return render(request, 'mark_attendance.html', {'students': students, 'course': course})
