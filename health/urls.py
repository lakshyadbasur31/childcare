from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('parent/', views.parent_dashboard, name='parent_dashboard'),
    path('parent/children/', views.children_dashboard, name='children_dashboard'),
    path('parent/maternal/', views.maternal_dashboard, name='maternal_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='health/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Child & Health
    path('child/add/', views.add_child, name='add_child'),
    path('child/<int:child_id>/', views.child_detail, name='child_detail'),
    path('child/<int:child_id>/growth/add/', views.add_growth_record, name='add_growth_record'),
    path('child/<int:child_id>/toggle-units/', views.toggle_units, name='toggle_units'),
    path('child/<int:child_id>/passport/', views.download_passport, name='download_passport'),
    
    # Admin Actions
    path('vax/<int:vax_id>/complete/', views.mark_vaccine_complete, name='mark_vaccine_complete'),
    path('child/<int:child_id>/remind/', views.trigger_urgent_reminder, name='trigger_urgent_reminder'),
    
    # Maternal Health
    path('maternal/profile/', views.manage_mother_profile, name='manage_mother_profile'),
    path('maternal/profile/delete/', views.delete_mother_profile, name='delete_mother_profile'),
    path('maternal/metric/add/', views.record_recovery_metric, name='record_recovery_metric'),
    path('maternal/lactation-guide/', views.lactation_guide, name='lactation_guide'),
    path('maternal/log-mood/', views.log_mood_exercise, name='log_mood_exercise'),
    
    # Child Actions
    path('child/<int:child_id>/delete/', views.delete_child, name='delete_child'),
    path('child/<int:child_id>/activity/<int:activity_id>/complete/', views.complete_activity, name='complete_activity'),
    path('get-new-story/<int:child_id>/', views.shuffle_story, name='shuffle_story'),
    
    # GPS Detection
    path('api/detect-locality/', views.detect_locality, name='detect_locality'),
    
    # Blueprint Appended Endpoints
    path('api/triage/evaluate/', views.evaluate_triage_view, name='evaluate_triage_view'),
    path('api/nutrition/log/', views.log_nutrition, name='log_nutrition'),
    path('api/nutrition/query/', views.ai_nutrition_query, name='ai_nutrition_query'),
    
    # Translation & Narration
    path('api/translate/', views.translate_story_text, name='translate_story_text'),
    path('api/translate-batch/', views.translate_batch, name='translate_batch'),
    path('api/narrate/', views.narrate_story_audio, name='narrate_story_audio'),
    path('api/set-language/', views.set_language, name='set_language'),
    
    # WhatsApp Integration
    path('whatsapp-demo/', views.whatsapp_demo_trigger_view, name='whatsapp_demo_trigger_view'),
]
