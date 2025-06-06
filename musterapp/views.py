from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe  # for safe HTML in location links
from .models import Attendance, CustomUser
from .forms import PasswordResetForm
from django.contrib.auth.hashers import check_password

class CustomLoginView(LoginView):
    template_name = 'login.html'
    
    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        login(self.request, user)

        if user.role == 'Employee':
            return redirect('employee_dashboard')
        elif user.role == 'Manager':
            return redirect('manager_dashboard')
        elif user.role == 'HR':
            return redirect('hr_dashboard')
        return redirect('home')

@login_required
def clock_in(request):
    if request.user.role != 'Employee':
        raise PermissionDenied

    today = timezone.localdate()
    attendance, created = Attendance.objects.get_or_create(
        employee=request.user, 
        date=today
    )

    if attendance.clock_in:
        messages.info(request, "You have already clocked in today.")
    else:
        attendance.clock_in = timezone.localtime()
        
        lat = request.POST.get('latitude')
        lon = request.POST.get('longitude')
        
        if lat and lon:
            attendance.clock_in_location = f"{lat},{lon}"
        else:
            attendance.clock_in_location = "0,0"
        
        attendance.save()
        messages.success(request, "Clock-in successful with coordinates")

    return redirect('employee_dashboard')

@login_required
def clock_out(request):
    if request.user.role != 'Employee':
        raise PermissionDenied

    today = timezone.localdate()
    attendance = Attendance.objects.filter(
        employee=request.user, 
        date=today
    ).first()

    if not attendance:
        messages.error(request, "You need to clock in first.")
    elif attendance.clock_out:
        messages.error(request, "You have already clocked out today.")
    else:
        attendance.clock_out = timezone.localtime()
        
        lat = request.POST.get('latitude')
        lon = request.POST.get('longitude')
        
        if lat and lon:
            attendance.clock_out_location = f"{lat},{lon}"
        else:
            attendance.clock_out_location = "0,0"
        
        attendance.save()
        messages.success(request, "Clock-out successful with coordinates")

    return redirect('employee_dashboard')

@login_required
def employee_dashboard(request):
    if request.user.role != 'Employee':
        raise PermissionDenied

    today = timezone.localdate()
    today_attendance = Attendance.objects.filter(
        employee=request.user, 
        date=today
    ).first()
    
    past_records = Attendance.objects.filter(
        employee=request.user
    ).order_by('-date')

    return render(request, 'employee_dashboard.html', {
        'attendance': today_attendance,
        'attendance_records': past_records,
    })

@login_required
def manager_dashboard(request):
    if request.user.role != 'Manager':
        raise PermissionDenied

    employees = get_user_model().objects.filter(role='Employee')
    selected_employee_id = request.GET.get('employee_id')
    selected_month = request.GET.get('month')
    
    attendances = Attendance.objects.all().order_by('-date', '-clock_in')

    if selected_employee_id:
        attendances = attendances.filter(employee__employee_id=selected_employee_id)
    if selected_month:
        attendances = attendances.filter(date__month=selected_month)

    # Keep only the latest attendance per employee (based on date and clock_in time)
    latest_attendance_per_employee = {}
    for att in attendances:
        emp_id = att.employee.employee_id
        # If employee not already in dict, add this attendance as latest
        if emp_id not in latest_attendance_per_employee:
            latest_attendance_per_employee[emp_id] = att

    attendances = latest_attendance_per_employee.values()

    # Convert clock in/out locations to clickable map icons as before
    for attendance in attendances:
        # Clock in location
        if attendance.clock_in_location and attendance.clock_in_location != "0,0":
            parts = attendance.clock_in_location.split(',')
            if len(parts) >= 2:
                lat = parts[0].strip()
                lon = parts[1].strip()
                attendance.clock_in_location = mark_safe(
                    f'<a href="https://www.google.com/maps?q={lat},{lon}" target="_blank" title="View Location">'
                    f'<i class="fas fa-map-marker-alt" style="color:red;"></i></a>'
                )
            else:
                attendance.clock_in_location = ""
        else:
            attendance.clock_in_location = ""

        # Clock out location
        if attendance.clock_out_location and attendance.clock_out_location != "0,0":
            parts = attendance.clock_out_location.split(',')
            if len(parts) >= 2:
                lat = parts[0].strip()
                lon = parts[1].strip()
                attendance.clock_out_location = mark_safe(
                    f'<a href="https://www.google.com/maps?q={lat},{lon}" target="_blank" title="View Location">'
                    f'<i class="fas fa-map-marker-alt" style="color:green;"></i></a>'
                )
            else:
                attendance.clock_out_location = ""
        else:
            attendance.clock_out_location = ""

    return render(request, 'manager_dashboard.html', {
        'attendances': attendances,
        'employees': employees,
        'selected_employee_id': selected_employee_id,
        'selected_month': selected_month,
    })

def reset_password(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            employee_id = form.cleaned_data["employee_id"]
            old_password = form.cleaned_data["old_password"]
            new_password = form.cleaned_data["new_password"]

            try:
                user = CustomUser.objects.get(employee_id=employee_id)
                if check_password(old_password, user.password):
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, "Password reset successful.")
                    return redirect("login")
                else:
                    messages.error(request, "Incorrect old password.")
            except CustomUser.DoesNotExist:
                messages.error(request, "Invalid Employee ID.")
    else:
        form = PasswordResetForm()

    return render(request, "reset_password.html", {"form": form})


from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def update_profile_photo(request):
    if request.method == 'POST' and request.FILES.get('profile_photo'):
        request.user.profile_photo = request.FILES['profile_photo']
        request.user.save()
    return redirect('employee_dashboard')  # or wherever your dashboard is

@login_required
def update_profile_photo(request):
    if request.method == 'POST' and request.FILES.get('profile_photo'):
        request.user.profile_photo = request.FILES['profile_photo']
        request.user.save()
    return redirect('manager_dashboard')

