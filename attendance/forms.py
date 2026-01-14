"""
Forms for Attendance Management System
Contains forms for Student, Subject, and Attendance
"""
from django import forms
from django.contrib.auth.models import User
from .models import Student, Subject, Attendance


class StudentForm(forms.ModelForm):
    """
    Form for creating and updating Student records
    Includes username and password fields for User creation
    """
    username = forms.CharField(
        max_length=150,
        required=False,
        help_text="Username for student login (optional)"
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        help_text="Password for student login (optional)"
    )

    class Meta:
        model = Student
        fields = ['roll_number', 'name', 'department', 'year']
        widgets = {
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 21CSE001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})

        if self.instance.pk and self.instance.user:
            self.fields['username'].initial = self.instance.user.username

    def clean_username(self):
        """
        Validate that username is unique (except for current user when editing)
        """
        username = self.cleaned_data.get('username')

        if username:
            existing_user = User.objects.filter(username=username).first()

            if self.instance.pk and self.instance.user and existing_user == self.instance.user:
                return username

            if existing_user:
                raise forms.ValidationError(f'Username "{username}" is already taken. Please choose another username.')

        return username

    def clean(self):
        """
        Validate that if username is provided, password must also be provided (for new users)
        """
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and not self.instance.pk and not password:
            raise forms.ValidationError('Password is required when creating a student with login access.')

        return cleaned_data

    def save(self, commit=True):
        """
        Override save to create User if username and password are provided
        """
        student = super().save(commit=False)

        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username:
            if student.user:
                student.user.username = username
                if password:
                    student.user.set_password(password)
                student.user.save()
            else:
                if password:
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        first_name=student.name.split()[0] if student.name else ''
                    )
                    student.user = user

        if commit:
            student.save()
        return student


class SubjectForm(forms.ModelForm):
    """
    Form for creating and updating Subject records
    """
    class Meta:
        model = Subject
        fields = ['subject_name', 'subject_code', 'department', 'year']
        widgets = {
            'subject_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Data Structures'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CS201'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.Select(attrs={'class': 'form-select'}),
        }


class AttendanceFilterForm(forms.Form):
    """
    Form for filtering attendance records
    Used in View Attendance page
    """
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="All Students"
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="All Subjects"
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="From Date"
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="To Date"
    )


class MarkAttendanceForm(forms.Form):
    """
    Form for marking attendance
    Dynamically generates checkboxes for each student
    """
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Subject"
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Select Date"
    )

    def __init__(self, *args, **kwargs):
        """
        Dynamically add student attendance fields based on selected subject
        """
        subject_id = kwargs.pop('subject_id', None)
        super().__init__(*args, **kwargs)

        if subject_id:
            try:
                subject = Subject.objects.get(id=subject_id)
                students = Student.objects.filter(
                    department=subject.department,
                    year=subject.year
                ).order_by('roll_number')

                for student in students:
                    field_name = f'student_{student.id}'
                    self.fields[field_name] = forms.BooleanField(
                        required=False,
                        label=f"{student.roll_number} - {student.name}",
                        initial=True,  
                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                    )
            except Subject.DoesNotExist:
                pass


class BulkAttendanceForm(forms.Form):
    """
    Simple form for bulk attendance marking
    """
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Subject"
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Attendance Date"
    )
