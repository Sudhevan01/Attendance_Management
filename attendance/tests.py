"""
Tests for Attendance Management System
Add your test cases here
"""
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Student, Subject, Attendance
from datetime import date


class StudentModelTest(TestCase):
    """Test cases for Student model"""

    def setUp(self):
        """Set up test data"""
        self.student = Student.objects.create(
            roll_number='21CSE001',
            name='Test Student',
            department='CSE',
            year=1
        )

    def test_student_creation(self):
        """Test student is created successfully"""
        self.assertEqual(self.student.roll_number, '21CSE001')
        self.assertEqual(self.student.name, 'Test Student')
        self.assertEqual(self.student.department, 'CSE')
        self.assertEqual(self.student.year, 1)

    def test_student_str(self):
        """Test string representation of student"""
        self.assertEqual(str(self.student), '21CSE001 - Test Student')


class SubjectModelTest(TestCase):
    """Test cases for Subject model"""

    def setUp(self):
        """Set up test data"""
        self.subject = Subject.objects.create(
            subject_code='CS101',
            subject_name='Data Structures',
            department='CSE',
            year=1
        )

    def test_subject_creation(self):
        """Test subject is created successfully"""
        self.assertEqual(self.subject.subject_code, 'CS101')
        self.assertEqual(self.subject.subject_name, 'Data Structures')

    def test_subject_str(self):
        """Test string representation of subject"""
        self.assertEqual(str(self.subject), 'CS101 - Data Structures')


class AttendanceModelTest(TestCase):
    """Test cases for Attendance model"""

    def setUp(self):
        """Set up test data"""
        self.student = Student.objects.create(
            roll_number='21CSE001',
            name='Test Student',
            department='CSE',
            year=1
        )
        self.subject = Subject.objects.create(
            subject_code='CS101',
            subject_name='Data Structures',
            department='CSE',
            year=1
        )

    def test_attendance_creation(self):
        """Test attendance is created successfully"""
        attendance = Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            date=date.today(),
            status='P'
        )
        self.assertEqual(attendance.status, 'P')
        self.assertEqual(attendance.student, self.student)
        self.assertEqual(attendance.subject, self.subject)

    def test_duplicate_attendance_prevention(self):
        """Test that duplicate attendance is prevented"""
        Attendance.objects.create(
            student=self.student,
            subject=self.subject,
            date=date.today(),
            status='P'
        )

        # Try creating duplicate - should raise IntegrityError
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(
                student=self.student,
                subject=self.subject,
                date=date.today(),
                status='A'
            )
