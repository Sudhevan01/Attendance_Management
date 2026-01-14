"""
Models for Attendance Management System
Contains Student, Subject, and Attendance models
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Student(models.Model):
    """
    Student Model - Stores student information
    Fields:
        - user: Links to Django's built-in User model (for login)
        - roll_number: Unique identifier for each student
        - name: Full name of the student
        - department: Department name (e.g., CSE, ECE, MECH)
        - year: Academic year (1, 2, 3, 4)
    """
    DEPARTMENT_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('ECE', 'Electronics and Communication Engineering'),
        ('MECH', 'Mechanical Engineering'),
        ('CIVIL', 'Civil Engineering'),
        ('BA', 'BUSSINESS ADMINISTRATION'),
        ('IT', 'Information Technology'),
    ]

    YEAR_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
    ]

    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

   
    roll_number = models.CharField(max_length=20, unique=True, help_text="Student's Roll Number")
    name = models.CharField(max_length=100, help_text="Student's Full Name")
    department = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES, help_text="Department")
    year = models.IntegerField(choices=YEAR_CHOICES, help_text="Academic Year")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['roll_number']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

    def __str__(self):
        """String representation of Student"""
        return f"{self.roll_number} - {self.name}"

    def get_attendance_percentage(self, subject=None):
        """
        Calculate attendance percentage for this student
        Args:
            subject: Optional subject filter
        Returns:
            Percentage as float
        """
        if subject:
            total = Attendance.objects.filter(student=self, subject=subject).count()
            present = Attendance.objects.filter(student=self, subject=subject, status='P').count()
        else:
            total = Attendance.objects.filter(student=self).count()
            present = Attendance.objects.filter(student=self, status='P').count()

        if total == 0:
            return 0
        return round((present / total) * 100, 2)


class Subject(models.Model):
    """
    Subject Model - Stores subject/course information
    Fields:
        - subject_name: Name of the subject
        - subject_code: Unique code for the subject
        - department: Department offering the subject
        - year: Year in which subject is taught
    """
    subject_name = models.CharField(max_length=100, help_text="Subject Name")
    subject_code = models.CharField(max_length=20, unique=True, help_text="Subject Code")
    department = models.CharField(max_length=10, choices=Student.DEPARTMENT_CHOICES, help_text="Department")
    year = models.IntegerField(choices=Student.YEAR_CHOICES, help_text="Academic Year")


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['subject_code']
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'

    def __str__(self):
        """String representation of Subject"""
        return f"{self.subject_code} - {self.subject_name}"


class Attendance(models.Model):
    """
    Attendance Model - Stores attendance records
    Fields:
        - student: Foreign key to Student
        - subject: Foreign key to Subject
        - date: Date of attendance
        - status: Present (P) or Absent (A)
    Constraints:
        - Unique together: student, subject, date (prevents duplicate entries)
    """
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('A', 'Absent'),
    ]

  
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendances')

   
    date = models.DateField(help_text="Date of Attendance")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P', help_text="Present or Absent")


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'subject', 'date']
        ordering = ['-date', 'student__roll_number']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        """String representation of Attendance"""
        return f"{self.student.roll_number} - {self.subject.subject_code} - {self.date} - {self.status}"

    def clean(self):
        """
        Custom validation to ensure student and subject are from same department and year
        """
        if self.student and self.subject:
            if self.student.department != self.subject.department:
                raise ValidationError("Student and Subject must be from the same department")
            if self.student.year != self.subject.year:
                raise ValidationError("Student and Subject must be from the same year")
