from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import date, datetime, timedelta
from calendar import monthrange
import json

from .models import (
    UserProfile, CycleProfile, Period, DailyLog, Symptom, DailySymptom,
    ContraceptiveType, ContraceptiveUse, Prediction, Notification,
    HealthProvider, Appointment, CycleInsight, Settings
)
from .forms import (
    UserProfileForm, CycleProfileForm, PeriodForm, DailyLogForm,
    ContraceptiveUseForm, HealthProviderForm, AppointmentForm, SettingsForm
)



# Authentication Views
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create associated profiles
            UserProfile.objects.create(user=user)
            CycleProfile.objects.create(user=user)
            Settings.objects.create(user=user)
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# Dashboard and Main Views
@login_required
def dashboard_view(request):
    user = request.user
    today = date.today()
    
    # Get recent period
    recent_period = Period.objects.filter(user=user).first()
    
    # Get today's log
    today_log, created = DailyLog.objects.get_or_create(
        user=user, 
        date=today,
        defaults={'flow': 'none'}
    )
    
    # Get predictions
    predictions = Prediction.objects.filter(
        user=user,
        is_active=True,
        predicted_date__gte=today
    ).order_by('predicted_date')
    
    # Get recent insights
    insights = CycleInsight.objects.filter(
        user=user,
        is_dismissed=False
    )[:3]
    
    # Get unread notifications
    notifications = Notification.objects.filter(
        user=user,
        is_read=False,
        scheduled_date__lte=timezone.now()
    )[:5]
    
    context = {
        'recent_period': recent_period,
        'today_log': today_log,
        'predictions': predictions,
        'insights': insights,
        'notifications': notifications,
        'today': today,
    }
    return render(request, 'dashboard.html', context)


# Profile Views
@login_required
def profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    cycle_profile = get_object_or_404(CycleProfile, user=request.user)
    
    context = {
        'user_profile': user_profile,
        'cycle_profile': cycle_profile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def edit_cycle_profile_view(request):
    cycle_profile = get_object_or_404(CycleProfile, user=request.user)
    
    if request.method == 'POST':
        form = CycleProfileForm(request.POST, instance=cycle_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cycle profile updated successfully!')
            # Regenerate predictions after profile update
            generate_predictions(request.user)
            return redirect('profile')
    else:
        form = CycleProfileForm(instance=cycle_profile)
    
    return render(request, 'accounts/edit_cycle_profile.html', {'form': form})


# Period Tracking Views
@login_required
def period_list_view(request):
    periods = Period.objects.filter(user=request.user)
    paginator = Paginator(periods, 10)
    page_number = request.GET.get('page')
    periods = paginator.get_page(page_number)
    
    return render(request, 'period_list.html', {'periods': periods})


@login_required
def add_period_view(request):
    if request.method == 'POST':
        form = PeriodForm(request.POST)
        if form.is_valid():
            period = form.save(commit=False)
            period.user = request.user
            period.save()
            
            # Update cycle profile if this is the first period
            cycle_profile = request.user.cycleprofile
            if not cycle_profile.first_period_date:
                cycle_profile.first_period_date = period.start_date
                cycle_profile.save()
            
            # Generate new predictions
            generate_predictions(request.user)
            
            messages.success(request, 'Period added successfully!')
            return redirect('period_list')
    else:
        form = PeriodForm()
    
    return render(request, 'add_period.html', {'form': form})


@login_required
def edit_period_view(request, period_id):
    period = get_object_or_404(Period, id=period_id, user=request.user)
    
    if request.method == 'POST':
        form = PeriodForm(request.POST, instance=period)
        if form.is_valid():
            form.save()
            generate_predictions(request.user)
            messages.success(request, 'Period updated successfully!')
            return redirect('period_list')
    else:
        form = PeriodForm(instance=period)
    
    return render(request, 'edit_period.html', {'form': form, 'period': period})


@login_required
def delete_period_view(request, period_id):
    period = get_object_or_404(Period, id=period_id, user=request.user)
    
    if request.method == 'POST':
        period.delete()
        generate_predictions(request.user)
        messages.success(request, 'Period deleted successfully!')
        return redirect('period_list')
    
    return render(request, 'delete_period.html', {'period': period})


# Daily Log Views
@login_required
def daily_log_view(request):
    today = date.today()
    log_date = request.GET.get('date')
    
    if log_date:
        try:
            log_date = datetime.strptime(log_date, '%Y-%m-%d').date()
        except ValueError:
            log_date = today
    else:
        log_date = today
    
    daily_log, created = DailyLog.objects.get_or_create(
        user=request.user,
        date=log_date,
        defaults={'flow': 'none'}
    )
    
    if request.method == 'POST':
        form = DailyLogForm(request.POST, instance=daily_log)
        if form.is_valid():
            form.save()
            
            # Handle symptoms
            symptom_ids = request.POST.getlist('symptoms')
            severities = request.POST.getlist('severities')
            
            # Clear existing symptoms
            DailySymptom.objects.filter(daily_log=daily_log).delete()
            
            # Add new symptoms
            for i, symptom_id in enumerate(symptom_ids):
                if symptom_id and i < len(severities) and severities[i]:
                    DailySymptom.objects.create(
                        daily_log=daily_log,
                        symptom_id=symptom_id,
                        severity=int(severities[i])
                    )
            
            messages.success(request, f'Daily log for {log_date} saved successfully!')
            return redirect('daily_log')
    else:
        form = DailyLogForm(instance=daily_log)
    
    # Get all symptoms for the form
    symptoms = Symptom.objects.all().order_by('category', 'name')
    existing_symptoms = DailySymptom.objects.filter(daily_log=daily_log)
    
    context = {
        'form': form,
        'daily_log': daily_log,
        'log_date': log_date,
        'symptoms': symptoms,
        'existing_symptoms': existing_symptoms,
        'today': today,
    }
    return render(request, 'daily_log.html', context)


@login_required
def daily_log_history_view(request):
    logs = DailyLog.objects.filter(user=request.user).order_by('-date')
    paginator = Paginator(logs, 30)
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)
    
    return render(request, 'daily_log_history.html', {'logs': logs})


# Calendar Views
@login_required
def calendar_view(request):
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # Get the first and last day of the month
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    
    # Get periods for this month
    periods = Period.objects.filter(
        user=request.user,
        start_date__lte=last_day,
        end_date__gte=first_day
    )
    
    # Get daily logs for this month
    daily_logs = DailyLog.objects.filter(
        user=request.user,
        date__range=[first_day, last_day]
    )
    
    # Get predictions for this month
    predictions = Prediction.objects.filter(
        user=request.user,
        is_active=True,
        predicted_date__range=[first_day, last_day]
    )
    
    # Create calendar data
    calendar_data = []
    current_date = first_day
    while current_date <= last_day:
        day_data = {
            'date': current_date,
            'periods': [p for p in periods if p.start_date <= current_date <= (p.end_date or p.start_date)],
            'daily_log': next((log for log in daily_logs if log.date == current_date), None),
            'predictions': [p for p in predictions if p.predicted_date == current_date],
        }
        calendar_data.append(day_data)
        current_date += timedelta(days=1)
    
    # Navigation dates
    prev_month = first_day - timedelta(days=1)
    next_month = last_day + timedelta(days=1)
    
    context = {
        'calendar_data': calendar_data,
        'current_month': first_day,
        'prev_month': prev_month,
        'next_month': next_month,
        'year': year,
        'month': month,
    }
    return render(request, 'calendar.html', context)


# Contraceptive Views
@login_required
def contraceptive_list_view(request):
    contraceptive_uses = ContraceptiveUse.objects.filter(user=request.user)
    contraceptive_types = ContraceptiveType.objects.all()
    
    context = {
        'contraceptive_uses': contraceptive_uses,
        'contraceptive_types': contraceptive_types,
    }
    return render(request, 'contraceptive_list.html', context)


@login_required
def add_contraceptive_use_view(request):
    if request.method == 'POST':
        form = ContraceptiveUseForm(request.POST)
        if form.is_valid():
            contraceptive_use = form.save(commit=False)
            contraceptive_use.user = request.user
            contraceptive_use.save()
            
            # If it's emergency contraception, update predictions
            if contraceptive_use.reason == 'emergency':
                update_predictions_for_emergency_contraception(request.user, contraceptive_use)
            
            messages.success(request, 'Contraceptive use recorded successfully!')
            return redirect('contraceptive_list')
    else:
        form = ContraceptiveUseForm()
    
    return render(request, 'add_contraceptive.html', {'form': form})


# Health Provider Views
@login_required
def health_provider_list_view(request):
    providers = HealthProvider.objects.filter(user=request.user)
    return render(request, 'health_provider_list.html', {'providers': providers})


@login_required
def add_health_provider_view(request):
    if request.method == 'POST':
        form = HealthProviderForm(request.POST)
        if form.is_valid():
            provider = form.save(commit=False)
            provider.user = request.user
            provider.save()
            messages.success(request, 'Health provider added successfully!')
            return redirect('health_provider_list')
    else:
        form = HealthProviderForm()
    
    return render(request, 'add_health_provider.html', {'form': form})


# Appointment Views
@login_required
def appointment_list_view(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'appointment_list.html', {'appointments': appointments})


@login_required
def add_appointment_view(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, 'Appointment scheduled successfully!')
            return redirect('appointment_list')
    else:
        form = AppointmentForm(user=request.user)
    
    return render(request, 'add_appointment.html', {'form': form})


# Settings Views
@login_required
def settings_view(request):
    settings = get_object_or_404(Settings, user=request.user)
    
    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('settings')
    else:
        form = SettingsForm(instance=settings)
    
    return render(request, 'settings.html', {'form': form})


# Insights and Analytics Views
@login_required
def insights_view(request):
    insights = CycleInsight.objects.filter(user=request.user, is_dismissed=False)
    return render(request, 'insights.html', {'insights': insights})


@login_required
def analytics_view(request):
    user = request.user
    
    # Get cycle statistics
    periods = Period.objects.filter(user=user).order_by('-start_date')
    recent_periods = periods[:6]  # Last 6 periods
    
    cycle_lengths = []
    for i in range(len(recent_periods) - 1):
        current_period = recent_periods[i]
        next_period = recent_periods[i + 1]
        cycle_length = (current_period.start_date - next_period.start_date).days
        cycle_lengths.append(cycle_length)
    
    avg_cycle_length = sum(cycle_lengths) / len(cycle_lengths) if cycle_lengths else 0
    
    # Get mood patterns
    mood_logs = DailyLog.objects.filter(
        user=user,
        mood__isnull=False,
        date__gte=date.today() - timedelta(days=90)
    )
    
    context = {
        'periods': recent_periods,
        'cycle_lengths': cycle_lengths,
        'avg_cycle_length': round(avg_cycle_length, 1),
        'mood_logs': mood_logs,
    }
    return render(request, 'analytics.html', context)


# Notifications Views
@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    return render(request, 'notifications.html', {'notifications': notifications})


@login_required
def mark_notification_read_view(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')


# Utility Functions
def generate_predictions(user):
    """Generate cycle predictions based on user's cycle history"""
    cycle_profile = user.cycleprofile
    recent_periods = Period.objects.filter(user=user).order_by('-start_date')[:3]
    
    if not recent_periods:
        return
    
    last_period = recent_periods[0]
    avg_cycle_length = cycle_profile.average_cycle_length
    
    # Clear old predictions
    Prediction.objects.filter(user=user).update(is_active=False)
    
    # Predict next period
    next_period_date = last_period.start_date + timedelta(days=avg_cycle_length)
    Prediction.objects.create(
        user=user,
        prediction_type='next_period',
        predicted_date=next_period_date,
        confidence_level='medium' if len(recent_periods) >= 3 else 'low'
    )
    
    # Predict ovulation (typically 14 days before next period)
    ovulation_date = next_period_date - timedelta(days=14)
    Prediction.objects.create(
        user=user,
        prediction_type='ovulation',
        predicted_date=ovulation_date,
        confidence_level='medium'
    )
    
    # Predict fertile window (5 days before and 1 day after ovulation)
    fertile_start = ovulation_date - timedelta(days=5)
    Prediction.objects.create(
        user=user,
        prediction_type='fertile_window',
        predicted_date=fertile_start,
        confidence_level='medium'
    )


def update_predictions_for_emergency_contraception(user, contraceptive_use):
    """Update predictions when emergency contraception is taken"""
    contraceptive_type = contraceptive_use.contraceptive_type
    
    if contraceptive_type.typical_cycle_delay_days:
        # Get current next period prediction
        next_period_prediction = Prediction.objects.filter(
            user=user,
            prediction_type='next_period',
            is_active=True
        ).first()
        
        if next_period_prediction:
            # Delay the prediction
            new_date = next_period_prediction.predicted_date + timedelta(
                days=contraceptive_type.typical_cycle_delay_days
            )
            next_period_prediction.predicted_date = new_date
            next_period_prediction.confidence_level = 'low'
            next_period_prediction.save()
            
            # Create insight about potential delay
            CycleInsight.objects.create(
                user=user,
                insight_type='contraceptive_effect',
                title='Potential Period Delay',
                description=f'Due to taking {contraceptive_type.name}, your next period may be delayed by up to {contraceptive_type.typical_cycle_delay_days} days.',
                data_period_start=date.today(),
                data_period_end=date.today()
            )