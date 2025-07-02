from django import forms
from django.contrib.auth.models import User
from .models import (
    UserProfile, CycleProfile, Period, DailyLog, ContraceptiveUse,
    HealthProvider, Appointment, Settings
)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'date_of_birth', 'phone_number', 'emergency_contact',
            'emergency_phone', 'timezone', 'notifications_enabled',
            'privacy_level'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+1234567890'}),
            'emergency_contact': forms.TextInput(attrs={'placeholder': 'Emergency contact name'}),
            'emergency_phone': forms.TextInput(attrs={'placeholder': '+1234567890'}),
            'timezone': forms.Select(),
        }


class CycleProfileForm(forms.ModelForm):
    class Meta:
        model = CycleProfile
        fields = [
            'average_cycle_length', 'average_period_length',
            'first_period_date', 'is_irregular', 'notes'
        ]
        widgets = {
            'first_period_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any additional notes about your cycle...'}),
        }
        help_texts = {
            'average_cycle_length': 'Number of days from the start of one period to the start of the next (21-45 days)',
            'average_period_length': 'Number of days your period typically lasts (2-10 days)',
            'first_period_date': 'Date of your first recorded period (helps with tracking)',
        }


class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = ['start_date', 'end_date', 'flow_intensity', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any notes about this period...'}),
        }
        help_texts = {
            'end_date': 'Leave blank if period is ongoing',
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date.")

        return cleaned_data


class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        fields = [
            'flow', 'mood', 'energy_level', 'pain_level',
            'sleep_hours', 'exercise_minutes', 'water_intake_glasses', 'notes'
        ]
        widgets = {
            'energy_level': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'pain_level': forms.NumberInput(attrs={'min': 0, 'max': 10}),
            'sleep_hours': forms.NumberInput(attrs={'step': '0.5', 'min': 0, 'max': 24}),
            'exercise_minutes': forms.NumberInput(attrs={'min': 0}),
            'water_intake_glasses': forms.NumberInput(attrs={'min': 0}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'How are you feeling today?'}),
        }


class ContraceptiveUseForm(forms.ModelForm):
    class Meta:
        model = ContraceptiveUse
        fields = ['contraceptive_type', 'date_taken', 'dosage', 'reason', 'notes']
        widgets = {
            'date_taken': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'dosage': forms.TextInput(attrs={'placeholder': 'e.g., 1 tablet, 1.5mg'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes...'}),
        }


class HealthProviderForm(forms.ModelForm):
    class Meta:
        model = HealthProvider
        fields = ['name', 'specialty', 'phone', 'email', 'address', 'is_primary', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Dr. Jane Smith'}),
            'specialty': forms.TextInput(attrs={'placeholder': 'Gynecologist'}),
            'phone': forms.TextInput(attrs={'placeholder': '+1234567890'}),
            'email': forms.EmailInput(attrs={'placeholder': 'doctor@example.com'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Full address...'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes...'}),
        }


class AppointmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['health_provider'].queryset = HealthProvider.objects.filter(user=user)

    class Meta:
        model = Appointment
        fields = ['health_provider', 'appointment_date', 'appointment_type', 'notes']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Purpose of visit, questions to ask...'}),
        }


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = [
            'period_reminder_days', 'ovulation_reminder_enabled',
            'daily_log_reminder_time', 'share_data_for_research',
            'allow_data_export', 'date_format', 'temperature_unit'
        ]
        widgets = {
            'period_reminder_days': forms.NumberInput(attrs={'min': 0, 'max': 7}),
            'daily_log_reminder_time': forms.TimeInput(attrs={'type': 'time'}),
        }