from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/cycle/', views.edit_cycle_profile_view, name='edit_cycle_profile'),
    
    # Period Tracking URLs
    path('periods/', views.period_list_view, name='period_list'),
    path('periods/add/', views.add_period_view, name='add_period'),
    path('periods/<int:period_id>/edit/', views.edit_period_view, name='edit_period'),
    path('periods/<int:period_id>/delete/', views.delete_period_view, name='delete_period'),
    
    # Daily Log URLs
    path('log/', views.daily_log_view, name='daily_log'),
    path('log/history/', views.daily_log_history_view, name='daily_log_history'),
    
    # Calendar URLs
    path('calendar/', views.calendar_view, name='calendar'),
    
    # Contraceptive URLs
    path('contraceptives/', views.contraceptive_list_view, name='contraceptive_list'),
    path('contraceptives/add/', views.add_contraceptive_use_view, name='add_contraceptive'),
    
    # Health Provider URLs
    path('providers/', views.health_provider_list_view, name='health_provider_list'),
    path('providers/add/', views.add_health_provider_view, name='add_health_provider'),
    
    # Appointment URLs
    path('appointments/', views.appointment_list_view, name='appointment_list'),
    path('appointments/add/', views.add_appointment_view, name='add_appointment'),
    
    # Settings URLs
    path('settings/', views.settings_view, name='settings'),
    
    # Analytics and Insights URLs
    path('insights/', views.insights_view, name='insights'),
    path('analytics/', views.analytics_view, name='analytics'),
    
    # Notifications URLs
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read_view, name='mark_notification_read'),
]