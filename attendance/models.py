from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Course(models.Model):
    name = models.CharField(max_length=100)
    staff_members = models.ManyToManyField(Staff, blank=True, related_name='courses')

    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=10, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.course.name})"

class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])  # ✅
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # ✅
    time_marked = models.DateTimeField(default=timezone.now)  # ✅

    def __str__(self):
        return f"{self.student.name} - {self.course.name} - {self.date} - {self.status}"
