from django import forms
from django.contrib.auth.models import User
from .models import Student, Course, Staff

class StaffRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match!")

class StudentRegisterForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'mobile_number', 'course']
        widgets = {
            'mobile_number': forms.TextInput(attrs={
                'placeholder': 'Enter 10-digit mobile number',
                'pattern': '[0-9]{10}',
                'title': 'Enter valid 10 digit mobile number'
            })
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name']

class AssignCourseForm(forms.Form):
    staff = forms.ModelChoiceField(queryset=Staff.objects.all())
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(), widget=forms.CheckboxSelectMultiple)
