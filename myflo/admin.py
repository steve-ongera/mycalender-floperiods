from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    UserProfile, CycleProfile, Period, DailyLog, Symptom, DailySymptom,
    ContraceptiveType, ContraceptiveUse, Prediction, Notification,
    HealthProvider, Appointment, CycleInsight, Settings
)


# Inline admin classes
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        ('date_of_birth', 'timezone'),
        ('phone_number', 'emergency_contact', 'emergency_phone'),
        ('notifications_enabled', 'privacy_level'),
    )


class CycleProfileInline(admin.StackedInline):
    model = CycleProfile
    can_delete = False
    verbose_name_plural = 'Cycle Profile'
    fields = (
        ('average_cycle_length', 'average_period_length'),
        ('first_period_date', 'is_irregular'),
        'notes',
    )


class SettingsInline(admin.StackedInline):
    model = Settings
    can_delete = False
    verbose_name_plural = 'Settings'
    fields = (
        ('period_reminder_days', 'ovulation_reminder_enabled'),
        ('daily_log_reminder_time', 'date_format', 'temperature_unit'),
        ('share_data_for_research', 'allow_data_export'),
    )


class DailySymptomInline(admin.TabularInline):
    model = DailySymptom
    extra = 0
    fields = ('symptom', 'severity')
    autocomplete_fields = ['symptom']


# Extended User Admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, CycleProfileInline, SettingsInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 
                   'is_staff', 'get_profile_info', 'date_joined')
    list_filter = BaseUserAdmin.list_filter + ('userprofile__privacy_level',)
    
    def get_profile_info(self, obj):
        try:
            profile = obj.userprofile
            return f"Age: {profile.date_of_birth or 'N/A'} | Privacy: {profile.privacy_level}"
        except UserProfile.DoesNotExist:
            return "No profile"
    get_profile_info.short_description = "Profile Info"


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'privacy_level', 'notifications_enabled', 'created_at')
    list_filter = ('privacy_level', 'notifications_enabled', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'date_of_birth', 'timezone')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'emergency_contact', 'emergency_phone')
        }),
        ('Privacy & Notifications', {
            'fields': ('privacy_level', 'notifications_enabled')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CycleProfile)
class CycleProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'average_cycle_length', 'average_period_length', 
                   'is_irregular', 'last_updated')
    list_filter = ('is_irregular', 'average_cycle_length', 'last_updated')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('last_updated',)
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Cycle Information', {
            'fields': (('average_cycle_length', 'average_period_length'),
                      ('first_period_date', 'is_irregular'))
        }),
        ('Additional Information', {
            'fields': ('notes', 'last_updated')
        })
    )


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'flow_intensity', 
                   'get_duration', 'cycle_day')
    list_filter = ('flow_intensity', 'start_date', 'created_at')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at', 'get_duration')
    
    fieldsets = (
        ('Period Information', {
            'fields': ('user', ('start_date', 'end_date'), 
                      ('flow_intensity', 'cycle_day'))
        }),
        ('Additional Information', {
            'fields': ('notes', 'get_duration')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_duration(self, obj):
        return f"{obj.duration} days" if obj.duration else "Ongoing"
    get_duration.short_description = "Duration"


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'flow', 'mood', 'energy_level', 
                   'pain_level', 'get_symptoms_count')
    list_filter = ('flow', 'mood', 'date', 'energy_level', 'pain_level')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at', 'get_symptoms_count')
    inlines = [DailySymptomInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'date', 'flow', 'mood')
        }),
        ('Health Metrics', {
            'fields': (('energy_level', 'pain_level'), 
                      ('sleep_hours', 'exercise_minutes'), 
                      'water_intake_glasses')
        }),
        ('Additional Information', {
            'fields': ('notes', 'get_symptoms_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_symptoms_count(self, obj):
        count = obj.symptoms.count()
        if count > 0:
            url = reverse('admin:myflo_dailysymptom_changelist') + f'?daily_log__id={obj.id}'
            return format_html('<a href="{}">{} symptoms</a>', url, count)
        return "No symptoms"
    get_symptoms_count.short_description = "Symptoms"


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_usage_count')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    ordering = ('category', 'name')
    
    def get_usage_count(self, obj):
        count = obj.dailysymptom_set.count()
        return f"{count} uses"
    get_usage_count.short_description = "Usage Count"


@admin.register(DailySymptom)
class DailySymptomAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'get_date', 'symptom', 'severity')
    list_filter = ('symptom', 'severity', 'daily_log__date')
    search_fields = ('daily_log__user__username', 'symptom__name')
    autocomplete_fields = ['symptom']
    
    def get_user(self, obj):
        return obj.daily_log.user.username
    get_user.short_description = "User"
    
    def get_date(self, obj):
        return obj.daily_log.date
    get_date.short_description = "Date"


@admin.register(ContraceptiveType)
class ContraceptiveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'affects_cycle', 'typical_cycle_delay_days')
    list_filter = ('category', 'affects_cycle')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')


@admin.register(ContraceptiveUse)
class ContraceptiveUseAdmin(admin.ModelAdmin):
    list_display = ('user', 'contraceptive_type', 'date_taken', 'reason', 'dosage')
    list_filter = ('contraceptive_type', 'reason', 'date_taken')
    search_fields = ('user__username', 'contraceptive_type__name')
    date_hierarchy = 'date_taken'
    readonly_fields = ('created_at',)
    autocomplete_fields = ['contraceptive_type']
    
    fieldsets = (
        ('Usage Information', {
            'fields': ('user', 'contraceptive_type', 'date_taken', 'reason')
        }),
        ('Details', {
            'fields': ('dosage', 'notes')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'prediction_type', 'predicted_date', 
                   'confidence_level', 'is_active', 'created_at')
    list_filter = ('prediction_type', 'confidence_level', 'is_active', 'predicted_date')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'predicted_date'
    readonly_fields = ('created_at',)
    
    actions = ['mark_as_inactive', 'mark_as_active']
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
    mark_as_inactive.short_description = "Mark selected predictions as inactive"
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
    mark_as_active.short_description = "Mark selected predictions as active"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'scheduled_date', 
                   'is_sent', 'is_read')
    list_filter = ('notification_type', 'is_sent', 'is_read', 'scheduled_date')
    search_fields = ('user__username', 'title', 'message')
    date_hierarchy = 'scheduled_date'
    readonly_fields = ('created_at',)
    
    actions = ['mark_as_sent', 'mark_as_read']
    
    def mark_as_sent(self, request, queryset):
        queryset.update(is_sent=True)
    mark_as_sent.short_description = "Mark selected notifications as sent"
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected notifications as read"


@admin.register(HealthProvider)
class HealthProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'specialty', 'phone', 'is_primary')
    list_filter = ('specialty', 'is_primary')
    search_fields = ('name', 'user__username', 'specialty', 'phone', 'email')
    
    fieldsets = (
        ('Provider Information', {
            'fields': ('user', 'name', 'specialty', 'is_primary')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        })
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_provider_name', 'appointment_date', 
                   'appointment_type', 'is_completed')
    list_filter = ('appointment_type', 'is_completed', 'appointment_date')
    search_fields = ('user__username', 'health_provider__name', 'notes')
    date_hierarchy = 'appointment_date'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Appointment Information', {
            'fields': ('user', 'health_provider', 'appointment_date', 'appointment_type')
        }),
        ('Status & Notes', {
            'fields': ('is_completed', 'notes')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_completed']
    
    def get_provider_name(self, obj):
        return obj.health_provider.name if obj.health_provider else "No provider"
    get_provider_name.short_description = "Provider"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(is_completed=True)
    mark_as_completed.short_description = "Mark selected appointments as completed"


@admin.register(CycleInsight)
class CycleInsightAdmin(admin.ModelAdmin):
    list_display = ('user', 'insight_type', 'title', 'data_period_start', 
                   'data_period_end', 'is_dismissed', 'created_at')
    list_filter = ('insight_type', 'is_dismissed', 'created_at')
    search_fields = ('user__username', 'title', 'description')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Insight Information', {
            'fields': ('user', 'insight_type', 'title')
        }),
        ('Content', {
            'fields': ('description',)
        }),
        ('Data Period', {
            'fields': (('data_period_start', 'data_period_end'),)
        }),
        ('Status', {
            'fields': ('is_dismissed', 'created_at')
        })
    )
    
    actions = ['mark_as_dismissed']
    
    def mark_as_dismissed(self, request, queryset):
        queryset.update(is_dismissed=True)
    mark_as_dismissed.short_description = "Mark selected insights as dismissed"


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'period_reminder_days', 'ovulation_reminder_enabled', 
                   'date_format', 'share_data_for_research')
    list_filter = ('ovulation_reminder_enabled', 'date_format', 'temperature_unit',
                  'share_data_for_research', 'allow_data_export')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notification Settings', {
            'fields': ('period_reminder_days', 'ovulation_reminder_enabled',
                      'daily_log_reminder_time', 'pill_reminder_times')
        }),
        ('Privacy Settings', {
            'fields': ('share_data_for_research', 'allow_data_export')
        }),
        ('Display Preferences', {
            'fields': ('date_format', 'temperature_unit')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


# Custom admin site configuration
admin.site.site_header = "Menstrual Cycle Tracking Admin"
admin.site.site_title = "Cycle Tracker Admin"
admin.site.index_title = "Welcome to Cycle Tracker Administration"