from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.forms import modelform_factory
from django.utils.timezone import now
from datetime import date
from django.utils.safestring import mark_safe
import json
from django.http import HttpResponse  
import csv
from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.utils import timezone
from openpyxl import Workbook
from io import BytesIO

from .models import Staff, Student, Course, AttendanceRecord
from .forms import StaffRegisterForm, StudentRegisterForm, CourseForm, AssignCourseForm

def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    error = False
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('admin_dashboard' if user.is_superuser else 'staff_dashboard')
        else:
            error = True
    return render(request, 'login.html', {'error': error})

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html', {
        'courses': Course.objects.all(),
        'students': Student.objects.all(),
        'staff_members': Staff.objects.all(),
        'attendance_records': AttendanceRecord.objects.all(),
    })

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
            form.save()
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
            staff = form.cleaned_data['staff']
            for course in form.cleaned_data['courses']:
                course.staff_members.add(staff)
            return redirect('admin_dashboard')
    else:
        form = AssignCourseForm()
    return render(request, 'assign_course.html', {'form': form})

@login_required
def staff_dashboard(request):
    staff = Staff.objects.get(user=request.user)
    courses = Course.objects.filter(staff_members=staff)
    return render(request, 'staff_dashboard.html', {'courses': courses})

@login_required
def mark_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = Student.objects.filter(course=course)
    staff = get_object_or_404(Staff, user=request.user)

    if request.method == 'POST':
        present_ids = request.POST.getlist('present')
        date = timezone.now().date()
        time_marked = timezone.now().time()

        total_present = 0
        total_absent = 0

        wb = Workbook()
        ws = wb.active
        ws.title = f"Attendance {date}"
        ws.append(["Student Name", "Mobile Number", "Status"])

        for student in students:
            status = 'Present' if str(student.id) in present_ids else 'Absent'
            AttendanceRecord.objects.create(
                student=student,
                course=course,
                date=date,
                status=status,
                marked_by=request.user,
                time_marked=timezone.now()
            )

            ws.append([student.name, student.mobile_number, status])
            if status == 'Present':
                total_present += 1
            else:
                total_absent += 1

        ws.append([])
        ws.append(["Course", course.name])
        ws.append(["Marked By", staff.user.get_full_name()])
        ws.append(["Email", staff.user.email])
        ws.append(["Date", str(date)])
        ws.append(["Time", str(time_marked)[:8]])
        ws.append(["Total Present", total_present])
        ws.append(["Total Absent", total_absent])

        # Save to in-memory file
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)

        # Email
        email = EmailMessage(
            subject=f"Attendance Report: {course.name} ({date})",
            body=(
                f"Attendance has been marked for {course.name}.\n\n"
                f"Marked by: {staff.user} ({staff.user.email})\n"
                f"Date: {date}\n"
                f"Time: {str(time_marked)[:8]}\n"
                f"Total Present: {total_present}\n"
                f"Total Absent: {total_absent}\n"
            ),
            from_email='your-email@example.com',
            to=[settings.ADMIN_EMAIL],  # Replace with admin email
        )
        email.attach(f"{course.name}_Attendance_{date}.xlsx", excel_file.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        email.send()

        return redirect('staff_dashboard')

    return render(request, 'mark_attendance.html', {
        'course': course,
        'students': students
    })

@login_required
@login_required
def attendance_view(request):
    if not request.user.is_superuser:
        return redirect('staff_dashboard')

    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    courses = Course.objects.all()
    students = Student.objects.all()

    course_data = []
    for course in courses:
        records = AttendanceRecord.objects.filter(course=course, date=selected_date)
        course_data.append({
            'course': course,
            'total_marked': records.count(),
            'present': records.filter(status='present').count(),
            'absent': records.filter(status='absent').count(),
        })

    selected_course = None
    course_student_data = []

    course_id = request.GET.get('course_id')
    if course_id:
        selected_course = get_object_or_404(Course, id=course_id)
        course_students = students.filter(course=selected_course)
        for student in course_students:
            total = AttendanceRecord.objects.filter(student=student, course=selected_course).count()
            present = AttendanceRecord.objects.filter(student=student, course=selected_course, status='present').count()
            today_status = AttendanceRecord.objects.filter(student=student, course=selected_course, date=selected_date).first()

            # Using status field directly instead of is_present
            if today_status:
                if today_status.status == 'present':
                    today_display = 'Present'
                else:
                    today_display = 'Absent'
            else:
                today_display = 'Not Marked'

            course_student_data.append({
                'student': student,
                'total_classes': total,
                'present_count': present,
                'today': today_display
            })

    return render(request, 'attendance_view.html', {
        'today': date.today(),
        'selected_date': selected_date,
        'course_data': course_data,
        'selected_course': selected_course,
        'course_student_data': course_student_data,
    })

@login_required
def export_attendance_csv(request):
    if not request.user.is_superuser:
        return redirect('staff_dashboard')

    course_id = request.GET.get('course_id')
    selected_date = request.GET.get('date')
    course = get_object_or_404(Course, id=course_id)

    try:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except:
        selected_date = date.today()

    students = Student.objects.filter(course=course)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{course.name}_attendance_{selected_date}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Mobile Number', 'Date', 'Status'])

    for student in students:
        record = AttendanceRecord.objects.filter(student=student, course=course, date=selected_date).first()
        status = 'Present' if record and record.is_present else 'Absent' if record else 'Not Marked'
        writer.writerow([student.name, student.mobile_number, selected_date, status])

    return response


# MODIFY / DELETE
@login_required
def modify_staff_list(request):
    if request.user.is_superuser:
        staff_members = Staff.objects.all()
        print(staff_members)
        return render(request, 'modify_staff_list.html', {'staff_members': staff_members})
    return redirect('staff_dashboard')


@login_required
def modify_staff_detail(request, staff_id):
    if not request.user.is_superuser:
        return redirect('staff_dashboard')

    staff = get_object_or_404(Staff, id=staff_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        staff.user.username = username
        staff.user.email = email
        staff.user.save()

        staff.mobile = mobile
        staff.save()

        messages.success(request, 'Staff details updated successfully!')
        return redirect('modify_staff_list')

    return render(request, 'modify_staff_detail.html', {'staff': staff})



@login_required
def delete_staff(request, staff_id):
    if request.user.is_superuser:
        staff = get_object_or_404(Staff, id=staff_id)
        staff.delete()
        messages.success(request, 'Staff deleted successfully!')
        return redirect('modify_staff_list')
    return redirect('staff_dashboard')

# Course Views
def modify_course_list(request):
    courses = Course.objects.all()
    return render(request, 'modify_course_list.html', {'courses': courses})

def modify_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('modify_course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'edit_course.html', {'form': form})

# Student Views
def modify_student_list(request):
    students = Student.objects.all()
    return render(request, 'modify_student_list.html', {'students': students})

def modify_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('modify_student_list')
    else:
        form = StudentRegisterForm(instance=student)
    return render(request, 'edit_student.html', {'form': form})




@user_passes_test(lambda u: u.is_superuser)
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_superuser)
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return redirect('admin_dashboard')



def create_superuser(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('Spoko', 'admin@example.com', 'Gogul@2022')
        return HttpResponse("Superuser created successfully!")
    else:
        return HttpResponse("Superuser already exists.")

