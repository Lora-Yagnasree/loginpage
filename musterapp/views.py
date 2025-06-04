from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import get_user_model
from datetime import datetime
from .models import Attendance, CustomUser
from .forms import PasswordResetForm
from django.contrib.auth.hashers import check_password

class CustomLoginView(LoginView):
    template_name = 'login.html'
    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        login(self.request, user)

        if user.role == 'Employee':
            return redirect('employee_dashboard')
        elif user.role == 'Manager':
            return redirect('manager_dashboard')
        elif user.role == 'HR':
            return redirect('hr_dashboard')
        else:
            return redirect('home')

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect
from .models import Attendance

@login_required
def clock_in(request):
    if request.user.role != 'Employee':
        raise PermissionDenied

    today = timezone.localdate()
    attendance, created = Attendance.objects.get_or_create(employee=request.user, date=today)

    if attendance.clock_in:
        messages.info(request, "You have already clocked in today.")
    else:
        attendance.clock_in = timezone.localtime()
        attendance.clock_in_location = request.POST.get("location")  # 🧠 Get location from form
        attendance.save()
        messages.success(request, "Clock-in successful!")

    return redirect('employee_dashboard')

@login_required
def clock_out(request):
    if request.user.role != 'Employee':
        raise PermissionDenied

    today = timezone.localdate()
    attendance = Attendance.objects.filter(employee=request.user, date=today).first()

    if not attendance:
        messages.error(request, "You need to clock in first.")
    elif attendance.clock_out:
        messages.error(request, "You have already clocked out today.")
    else:
        attendance.clock_out = timezone.localtime()
        attendance.clock_out_location = request.POST.get("location")  # 🧠 Get location from form
        attendance.save()
        messages.success(request, "Clock-out successful!")

    return redirect('employee_dashboard')

@login_required
def employee_dashboard(request):
    if request.user.role != 'Employee':
        raise PermissionDenied

    today = timezone.localdate()
    today_attendance = Attendance.objects.filter(employee=request.user, date=today).first()
    past_records = Attendance.objects.filter(employee=request.user).order_by('-date')

    return render(request, 'employee_dashboard.html', {
        'attendance': today_attendance,
        'attendance_records': past_records,
    })


@login_required
def manager_dashboard(request):
    if request.user.role != 'Manager':
        raise PermissionDenied

    employees = get_user_model().objects.filter(role='Employee')
    selected_employee_id = request.GET.get('employee_id', None)
    selected_month = request.GET.get('month', None)

    if selected_employee_id and selected_month:
        attendances = Attendance.objects.filter(
            employee__employee_id=selected_employee_id,
            date__month=selected_month
        )
    elif selected_employee_id:
        attendances = Attendance.objects.filter(employee__employee_id=selected_employee_id)
    elif selected_month:
        attendances = Attendance.objects.filter(date__month=selected_month)
    else:
        attendances = Attendance.objects.all()

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
