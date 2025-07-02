from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date, timedelta


class UserProfile(models.Model):
    """Extended user profile for additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=15, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    notifications_enabled = models.BooleanField(default=True)
    privacy_level = models.CharField(
        max_length=20,
        choices=[
            ('private', 'Private'),
            ('family', 'Family Only'),
            ('public', 'Public')
        ],
        default='private'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class CycleProfile(models.Model):
    """User's menstrual cycle characteristics"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    average_cycle_length = models.IntegerField(
        default=28,
        validators=[MinValueValidator(21), MaxValueValidator(45)]
    )
    average_period_length = models.IntegerField(
        default=5,
        validators=[MinValueValidator(2), MaxValueValidator(10)]
    )
    first_period_date = models.DateField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_irregular = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Cycle Profile"


class Period(models.Model):
    """Individual period records"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    flow_intensity = models.CharField(
        max_length=10,
        choices=[
            ('light', 'Light'),
            ('medium', 'Medium'),
            ('heavy', 'Heavy'),
            ('very_heavy', 'Very Heavy')
        ],
        default='medium'
    )
    cycle_day = models.IntegerField(default=1)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        unique_together = ['user', 'start_date']

    def __str__(self):
        return f"{self.user.username} - Period starting {self.start_date}"

    @property
    def duration(self):
        if self.end_date:
            return (self.end_date - self.start_date).days + 1
        return None


class DailyLog(models.Model):
    """Daily tracking of symptoms, mood, and other factors"""
    FLOW_CHOICES = [
        ('none', 'None'),
        ('spotting', 'Spotting'),
        ('light', 'Light'),
        ('medium', 'Medium'),
        ('heavy', 'Heavy'),
        ('very_heavy', 'Very Heavy')
    ]

    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('anxious', 'Anxious'),
        ('irritable', 'Irritable'),
        ('calm', 'Calm'),
        ('energetic', 'Energetic'),
        ('tired', 'Tired'),
        ('neutral', 'Neutral')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    flow = models.CharField(max_length=15, choices=FLOW_CHOICES, default='none')
    mood = models.CharField(max_length=15, choices=MOOD_CHOICES, blank=True)
    energy_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Rate from 1 (very low) to 10 (very high)"
    )
    pain_level = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Rate from 0 (no pain) to 10 (severe pain)"
    )
    sleep_hours = models.DecimalField(
        max_digits=4, decimal_places=2,
        null=True, blank=True
    )
    exercise_minutes = models.IntegerField(null=True, blank=True)
    water_intake_glasses = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class Symptom(models.Model):
    """Predefined symptoms that users can track"""
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(
        max_length=20,
        choices=[
            ('physical', 'Physical'),
            ('emotional', 'Emotional'),
            ('digestive', 'Digestive'),
            ('skin', 'Skin'),
            ('other', 'Other')
        ]
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class DailySymptom(models.Model):
    """User's daily symptom tracking"""
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, related_name='symptoms')
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    severity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rate from 1 (mild) to 5 (severe)"
    )

    class Meta:
        unique_together = ['daily_log', 'symptom']

    def __str__(self):
        return f"{self.symptom.name} - Severity {self.severity}"


class ContraceptiveType(models.Model):
    """Types of contraceptives available"""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20,
        choices=[
            ('emergency', 'Emergency Contraception'),
            ('hormonal', 'Hormonal'),
            ('barrier', 'Barrier'),
            ('iud', 'IUD'),
            ('implant', 'Implant'),
            ('injection', 'Injection'),
            ('patch', 'Patch'),
            ('ring', 'Ring'),
            ('pill', 'Birth Control Pill'),
            ('other', 'Other')
        ]
    )
    affects_cycle = models.BooleanField(
        default=False,
        help_text="Does this contraceptive typically affect menstrual cycles?"
    )
    typical_cycle_delay_days = models.IntegerField(
        null=True, blank=True,
        help_text="Typical delay in days for next period (for emergency contraception)"
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ContraceptiveUse(models.Model):
    """User's contraceptive usage records"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contraceptive_type = models.ForeignKey(ContraceptiveType, on_delete=models.CASCADE)
    date_taken = models.DateTimeField()
    dosage = models.CharField(max_length=100, blank=True)
    reason = models.CharField(
        max_length=20,
        choices=[
            ('emergency', 'Emergency Contraception'),
            ('regular', 'Regular Contraception'),
            ('missed_pill', 'Missed Regular Pill'),
            ('other', 'Other')
        ]
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_taken']

    def __str__(self):
        return f"{self.user.username} - {self.contraceptive_type.name} on {self.date_taken.date()}"


class Prediction(models.Model):
    """Predicted cycle events"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prediction_type = models.CharField(
        max_length=20,
        choices=[
            ('next_period', 'Next Period'),
            ('ovulation', 'Ovulation'),
            ('fertile_window', 'Fertile Window'),
            ('pms_start', 'PMS Start')
        ]
    )
    predicted_date = models.DateField()
    confidence_level = models.CharField(
        max_length=10,
        choices=[
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low')
        ],
        default='medium'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['predicted_date']

    def __str__(self):
        return f"{self.user.username} - {self.prediction_type} on {self.predicted_date}"


class Notification(models.Model):
    """User notifications and reminders"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('period_reminder', 'Period Reminder'),
            ('ovulation_reminder', 'Ovulation Reminder'),
            ('pill_reminder', 'Pill Reminder'),
            ('log_reminder', 'Daily Log Reminder'),
            ('appointment_reminder', 'Appointment Reminder'),
            ('general', 'General')
        ]
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    scheduled_date = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class HealthProvider(models.Model):
    """Healthcare provider information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    specialty = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Appointment(models.Model):
    """Medical appointments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    health_provider = models.ForeignKey(
        HealthProvider, on_delete=models.CASCADE,
        null=True, blank=True
    )
    appointment_date = models.DateTimeField()
    appointment_type = models.CharField(
        max_length=50,
        choices=[
            ('routine_checkup', 'Routine Checkup'),
            ('gynecology', 'Gynecology'),
            ('contraception', 'Contraception Consultation'),
            ('fertility', 'Fertility Consultation'),
            ('other', 'Other')
        ]
    )
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['appointment_date']

    def __str__(self):
        return f"{self.user.username} - {self.appointment_type} on {self.appointment_date.date()}"


class CycleInsight(models.Model):
    """Generated insights about user's cycle patterns"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    insight_type = models.CharField(
        max_length=30,
        choices=[
            ('cycle_length_trend', 'Cycle Length Trend'),
            ('symptom_pattern', 'Symptom Pattern'),
            ('mood_pattern', 'Mood Pattern'),
            ('irregularity_alert', 'Irregularity Alert'),
            ('contraceptive_effect', 'Contraceptive Effect'),
            ('general', 'General Insight')
        ]
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    data_period_start = models.DateField()
    data_period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_dismissed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Settings(models.Model):
    """User app settings and preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Notification preferences
    period_reminder_days = models.IntegerField(default=1)
    ovulation_reminder_enabled = models.BooleanField(default=True)
    daily_log_reminder_time = models.TimeField(null=True, blank=True)
    pill_reminder_times = models.JSONField(default=list, blank=True)
    
    # Privacy settings
    share_data_for_research = models.BooleanField(default=False)
    allow_data_export = models.BooleanField(default=True)
    
    # Display preferences
    date_format = models.CharField(
        max_length=10,
        choices=[
            ('dd/mm/yyyy', 'DD/MM/YYYY'),
            ('mm/dd/yyyy', 'MM/DD/YYYY'),
            ('yyyy-mm-dd', 'YYYY-MM-DD')
        ],
        default='dd/mm/yyyy'
    )
    temperature_unit = models.CharField(
        max_length=1,
        choices=[('C', 'Celsius'), ('F', 'Fahrenheit')],
        default='C'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Settings"