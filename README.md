# MyFlo Periods 🌸

A comprehensive Django-based menstrual cycle tracking application that empowers users to monitor their reproductive health, predict cycles, and gain valuable insights into their well-being.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Contributing](#contributing)
- [Privacy & Security](#privacy--security)
- [License](#license)
- [Support](#support)

## ✨ Features

### Core Tracking
- **Period Logging**: Track menstrual cycles with flow intensity, duration, and custom notes
- **Daily Symptom Monitoring**: Record physical and emotional symptoms with severity ratings
- **Mood & Energy Tracking**: Monitor daily mood patterns and energy levels
- **Pain Level Assessment**: Track and analyze pain patterns throughout cycles

### Health Management
- **Contraceptive Tracking**: Monitor various types of birth control and their effects
- **Healthcare Provider Management**: Store and organize healthcare professional information
- **Appointment Scheduling**: Track medical appointments and checkups
- **Emergency Contraception Monitoring**: Special tracking for emergency contraceptive use

### Smart Predictions
- **Cycle Predictions**: AI-powered predictions for next periods and ovulation
- **Fertile Window Calculations**: Identify optimal conception windows
- **PMS Onset Predictions**: Anticipate premenstrual syndrome timing
- **Confidence Scoring**: Reliability indicators for all predictions

### Insights & Analytics
- **Pattern Recognition**: Identify trends in cycle length, symptoms, and mood
- **Personalized Insights**: Custom health insights based on individual data
- **Irregularity Alerts**: Notifications for unusual cycle patterns
- **Data Visualization**: Graphical representations of health trends

### User Experience
- **Smart Notifications**: Customizable reminders for periods, ovulation, and daily logging
- **Privacy Controls**: Granular privacy settings (private, family, public)
- **Multi-timezone Support**: Global accessibility with timezone awareness
- **Responsive Design**: Optimized for mobile and desktop usage

## 🛠 Technology Stack

- **Backend**: Django 4.x
- **Database**: PostgreSQL (recommended) / SQLite (development)
- **Authentication**: Django's built-in user system
- **API**: Django REST Framework
- **Task Queue**: Celery (for notifications and predictions)
- **Caching**: Redis
- **Frontend**: HTML/CSS/JavaScript (or your preferred framework)

## 🚀 Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+ (recommended)
- Redis (for caching and task queue)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/myflo-periods.git
   cd myflo-periods
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load initial data**
   ```bash
   python manage.py loaddata fixtures/symptoms.json
   python manage.py loaddata fixtures/contraceptives.json
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/myflo_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Timezone
TIME_ZONE=UTC
```

### Settings Configuration

Key settings in `settings.py`:

```python
# Cycle prediction settings
CYCLE_PREDICTION_CONFIDENCE_THRESHOLD = 0.7
DEFAULT_CYCLE_LENGTH = 28
DEFAULT_PERIOD_LENGTH = 5

# Notification settings
NOTIFICATION_BATCH_SIZE = 100
DAILY_LOG_REMINDER_DEFAULT_TIME = "20:00"

# Privacy settings
DATA_RETENTION_DAYS = 2555  # ~7 years
ALLOW_DATA_EXPORT = True
```

## 📱 Usage

### For End Users

1. **Registration & Profile Setup**
   - Create account and complete profile
   - Set cycle characteristics and preferences
   - Configure notification preferences

2. **Daily Logging**
   - Record daily symptoms, mood, and flow
   - Track pain levels and energy
   - Add personal notes and observations

3. **Cycle Management**
   - Log period start and end dates
   - Monitor cycle patterns and irregularities
   - Track contraceptive usage

4. **Health Insights**
   - View personalized cycle predictions
   - Analyze symptom patterns
   - Export data for healthcare providers

### For Developers

#### Key Models

- `UserProfile`: Extended user information and preferences
- `CycleProfile`: User's menstrual cycle characteristics
- `Period`: Individual period records
- `DailyLog`: Daily symptom and mood tracking
- `Prediction`: AI-generated cycle predictions
- `CycleInsight`: Pattern-based health insights

#### API Endpoints

```
GET    /api/v1/cycles/           # List user's cycles
POST   /api/v1/cycles/           # Create new cycle entry
GET    /api/v1/daily-logs/       # Get daily logs
POST   /api/v1/daily-logs/       # Create daily log entry
GET    /api/v1/predictions/      # Get cycle predictions
GET    /api/v1/insights/         # Get personalized insights
```

## 📊 Database Schema

### Core Entities

- **Users & Profiles**: User authentication and extended profile information
- **Cycle Data**: Period records, daily logs, and symptom tracking
- **Predictions**: AI-generated forecasts and confidence scoring
- **Health Management**: Contraceptive tracking and healthcare provider info
- **Notifications**: Smart reminders and user communications
- **Settings**: User preferences and privacy controls

### Key Relationships

- One-to-One: User → UserProfile, CycleProfile, Settings
- One-to-Many: User → Periods, DailyLogs, Predictions
- Many-to-Many: DailyLog → Symptoms (through DailySymptom)

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure privacy and security compliance

### Testing

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test apps.cycles.tests

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🔒 Privacy & Security

MyFlo takes user privacy seriously:

- **Data Encryption**: All sensitive data encrypted at rest and in transit
- **Privacy Levels**: Granular control over data sharing (private/family/public)
- **Data Retention**: Configurable data retention policies
- **Export Rights**: Users can export their complete data
- **GDPR Compliance**: Full compliance with data protection regulations
- **Secure Authentication**: Multi-factor authentication support

### Security Features

- CSRF protection on all forms
- SQL injection prevention through ORM
- XSS protection with template escaping
- Secure session management
- Rate limiting on API endpoints

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

### Getting Help

- **Documentation**: [Full documentation](https://docs.myflo.app)
- **Issues**: [GitHub Issues](https://github.com/yourusername/myflo-periods/issues)
- **Email**: support@myflo.app
- **Community**: [Discord Server](https://discord.gg/myflo)

### Reporting Issues

When reporting issues, please include:
- Django version and environment details
- Steps to reproduce the issue
- Expected vs actual behavior
- Relevant log outputs (sanitize sensitive data)

---

## 🌟 Acknowledgments

- Thanks to all contributors who help make period tracking more accessible
- Healthcare professionals who provided medical guidance
- The Django community for excellent documentation and support

**Made with ❤️ for reproductive health awareness**