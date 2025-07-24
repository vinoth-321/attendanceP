from django import forms
from django.contrib.auth.models import User
from .models import Student, Course

class StaffRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")

class StudentRegisterForm(forms.Form):
    name = forms.CharField(max_length=100)
    roll_number = forms.CharField(max_length=20)
    course = forms.ModelChoiceField(queryset=Course.objects.all())

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name']

class AssignCourseForm(forms.Form):
    staff = forms.ModelChoiceField(queryset=User.objects.filter(is_superuser=False))
    course = forms.ModelChoiceField(queryset=Course.objects.all())
