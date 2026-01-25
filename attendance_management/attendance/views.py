"""
Views for Attendance Management System
All views are function-based for simplicity
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.db import IntegrityError
from datetime import date, datetime
from .models import Student, Subject, Attendance
from .forms import StudentForm, SubjectForm, AttendanceFilterForm, BulkAttendanceForm



def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_staff or user.is_superuser


def is_student(user):
    """Check if user is a student"""
    try:
        return hasattr(user, 'student') and user.student is not None
    except:
        return False


def welcome_view(request):
    """
    Welcome/Landing page for the application
    Redirects to dashboard if user is already authenticated
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'attendance/welcome.html')


def login_view(request):
    """
    Login page for both admin and students
    POST: Authenticate user and redirect to dashboard
    GET: Display login form
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'attendance/login.html')


@login_required
def logout_view(request):
    """
    Logout user and redirect to login page
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')



@login_required
def dashboard(request):
    """
    Dashboard showing statistics
    Admin: See all statistics
    Student: See their own attendance statistics
    """
    context = {}

    if is_admin(request.user):
        context['total_students'] = Student.objects.count()
        context['total_subjects'] = Subject.objects.count()
        context['total_attendance_records'] = Attendance.objects.count()
        context['present_today'] = Attendance.objects.filter(date=date.today(), status='P').count()
        context['absent_today'] = Attendance.objects.filter(date=date.today(), status='A').count()
        context['is_admin'] = True
        context['recent_attendance'] = Attendance.objects.select_related('student', 'subject').order_by('-date', '-created_at')[:10]

    elif is_student(request.user):
        student = request.user.student
        context['student'] = student
        context['is_student'] = True
        total_classes = Attendance.objects.filter(student=student).count()
        present_classes = Attendance.objects.filter(student=student, status='P').count()

        if total_classes > 0:
            context['attendance_percentage'] = round((present_classes / total_classes) * 100, 2)
        else:
            context['attendance_percentage'] = 0

        context['total_classes'] = total_classes
        context['present_classes'] = present_classes
        context['absent_classes'] = total_classes - present_classes
        subjects = Subject.objects.filter(department=student.department, year=student.year)
        subject_attendance = []

        for subject in subjects:
            total = Attendance.objects.filter(student=student, subject=subject).count()
            present = Attendance.objects.filter(student=student, subject=subject, status='P').count()

            if total > 0:
                percentage = round((present / total) * 100, 2)
            else:
                percentage = 0

            subject_attendance.append({
                'subject': subject,
                'total': total,
                'present': present,
                'absent': total - present,
                'percentage': percentage
            })

        context['subject_attendance'] = subject_attendance

        context['recent_attendance'] = Attendance.objects.filter(student=student).select_related('subject').order_by('-date')[:10]

    return render(request, 'attendance/dashboard.html', context)



@login_required
@user_passes_test(is_admin)
def student_list(request):
    """
    Display list of all students with search functionality
    """
    students = Student.objects.all().order_by('roll_number')
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(roll_number__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    department = request.GET.get('department', '')
    if department:
        students = students.filter(department=department)

    year = request.GET.get('year', '')
    if year:
        students = students.filter(year=year)

    context = {
        'students': students,
        'search_query': search_query,
        'departments': Student.DEPARTMENT_CHOICES,
        'years': Student.YEAR_CHOICES,
    }

    return render(request, 'attendance/student_list.html', context)


@login_required
@user_passes_test(is_admin)
def student_create(request):
    """
    Create new student
    """
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'Student {student.name} created successfully!')
            return redirect('student_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm()

    context = {'form': form, 'title': 'Add New Student', 'button_text': 'Create Student'}
    return render(request, 'attendance/student_form.html', context)


@login_required
@user_passes_test(is_admin)
def student_update(request, pk):
    """
    Update existing student
    """
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student {student.name} updated successfully!')
            return redirect('student_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm(instance=student)

    context = {'form': form, 'title': 'Edit Student', 'button_text': 'Update Student', 'student': student}
    return render(request, 'attendance/student_form.html', context)


@login_required
@user_passes_test(is_admin)
def student_delete(request, pk):
    """
    Delete student
    """
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student_name = student.name
        student.delete()
        messages.success(request, f'Student {student_name} deleted successfully!')
        return redirect('student_list')

    context = {'student': student}
    return render(request, 'attendance/student_confirm_delete.html', context)



@login_required
@user_passes_test(is_admin)
def subject_list(request):
    """
    Display list of all subjects with search functionality
    """
    subjects = Subject.objects.all().order_by('subject_code')

    search_query = request.GET.get('search', '')
    if search_query:
        subjects = subjects.filter(
            Q(subject_code__icontains=search_query) |
            Q(subject_name__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    department = request.GET.get('department', '')
    if department:
        subjects = subjects.filter(department=department)

    year = request.GET.get('year', '')
    if year:
        subjects = subjects.filter(year=year)

    context = {
        'subjects': subjects,
        'search_query': search_query,
        'departments': Student.DEPARTMENT_CHOICES,
        'years': Student.YEAR_CHOICES,
    }

    return render(request, 'attendance/subject_list.html', context)


@login_required
@user_passes_test(is_admin)
def subject_create(request):
    """
    Create new subject
    """
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject {subject.subject_name} created successfully!')
            return redirect('subject_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm()

    context = {'form': form, 'title': 'Add New Subject', 'button_text': 'Create Subject'}
    return render(request, 'attendance/subject_form.html', context)


@login_required
@user_passes_test(is_admin)
def subject_update(request, pk):
    """
    Update existing subject
    """
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, f'Subject {subject.subject_name} updated successfully!')
            return redirect('subject_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm(instance=subject)

    context = {'form': form, 'title': 'Edit Subject', 'button_text': 'Update Subject', 'subject': subject}
    return render(request, 'attendance/subject_form.html', context)


@login_required
@user_passes_test(is_admin)
def subject_delete(request, pk):
    """
    Delete subject
    """
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        subject_name = subject.subject_name
        subject.delete()
        messages.success(request, f'Subject {subject_name} deleted successfully!')
        return redirect('subject_list')

    context = {'subject': subject}
    return render(request, 'attendance/subject_confirm_delete.html', context)



@login_required
@user_passes_test(is_admin)
def mark_attendance(request):
    """
    Mark attendance for students
    Step 1: Select subject and date
    Step 2: Mark attendance for each student
    """
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        attendance_date = request.POST.get('date')

        if not subject_id or not attendance_date:
            messages.error(request, 'Please select both subject and date.')
            return redirect('mark_attendance')

        subject = get_object_or_404(Subject, pk=subject_id)
        attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()

        students = Student.objects.filter(
            department=subject.department,
            year=subject.year
        ).order_by('roll_number')

        if not students.exists():
            messages.warning(request, 'No students found for this subject.')
            return redirect('mark_attendance')

        if 'submit_attendance' in request.POST:
            success_count = 0
            error_count = 0

            for student in students:
                is_present = request.POST.get(f'student_{student.id}') == 'on'
                status = 'P' if is_present else 'A'

                try:
                    attendance, created = Attendance.objects.update_or_create(
                        student=student,
                        subject=subject,
                        date=attendance_date,
                        defaults={'status': status}
                    )
                    success_count += 1
                except IntegrityError:
                    error_count += 1

            if success_count > 0:
                messages.success(request, f'Attendance marked successfully for {success_count} students!')
            if error_count > 0:
                messages.error(request, f'Failed to mark attendance for {error_count} students.')

            return redirect('view_attendance')

        existing_attendance = {}
        for att in Attendance.objects.filter(subject=subject, date=attendance_date):
            existing_attendance[att.student.id] = att.status

        students_list = list(students)
        for student in students_list:
            student.attendance_status = existing_attendance.get(student.id, None)

        context = {
            'subject': subject,
            'date': attendance_date,
            'students': students_list,
            'existing_attendance': existing_attendance,
        }

        return render(request, 'attendance/mark_attendance_form.html', context)

    form = BulkAttendanceForm()
    context = {'form': form}
    return render(request, 'attendance/mark_attendance.html', context)



@login_required
def view_attendance(request):
    """
    View attendance records with filtering
    Admin: Can see all records
    Student: Can see only their records
    """
    attendance_records = Attendance.objects.select_related('student', 'subject').order_by('-date', 'student__roll_number')

    if is_student(request.user):
        attendance_records = attendance_records.filter(student=request.user.student)

    student_id = request.GET.get('student')
    subject_id = request.GET.get('subject')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if student_id:
        attendance_records = attendance_records.filter(student_id=student_id)

    if subject_id:
        attendance_records = attendance_records.filter(subject_id=subject_id)

    if date_from:
        attendance_records = attendance_records.filter(date__gte=date_from)

    if date_to:
        attendance_records = attendance_records.filter(date__lte=date_to)
    if is_admin(request.user):
        form = AttendanceFilterForm(request.GET)
    else:
        form = None

    total_count = attendance_records.count()
    present_count = attendance_records.filter(status='P').count()
    absent_count = attendance_records.filter(status='A').count()

    context = {
        'attendance_records': attendance_records,
        'form': form,
        'is_admin': is_admin(request.user),
        'total_count': total_count,
        'present_count': present_count,
        'absent_count': absent_count,
    }

    return render(request, 'attendance/view_attendance.html', context)



@login_required
def attendance_percentage(request):
    """
    View attendance percentage
    Admin: See all students' percentages
    Student: See only their percentage
    """
    if is_admin(request.user):
        students = Student.objects.all().order_by('roll_number')

        student_data = []
        for student in students:
            total_classes = Attendance.objects.filter(student=student).count()
            present_classes = Attendance.objects.filter(student=student, status='P').count()

            if total_classes > 0:
                percentage = round((present_classes / total_classes) * 100, 2)
            else:
                percentage = 0

            student_data.append({
                'student': student,
                'total_classes': total_classes,
                'present_classes': present_classes,
                'absent_classes': total_classes - present_classes,
                'percentage': percentage,
            })

        department = request.GET.get('department', '')
        if department:
            student_data = [data for data in student_data if data['student'].department == department]

        year = request.GET.get('year', '')
        if year:
            student_data = [data for data in student_data if data['student'].year == int(year)]

        context = {
            'student_data': student_data,
            'is_admin': True,
            'departments': Student.DEPARTMENT_CHOICES,
            'years': Student.YEAR_CHOICES,
        }

    else:
        return redirect('dashboard')

    return render(request, 'attendance/attendance_percentage.html', context)
