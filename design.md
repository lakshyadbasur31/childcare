# Bharat-Health Guardian Detailed Design Document

## 1. Database Schema Updates
We will modify the following models:
- **`User` (Custom User Model)**:
  - `phone_number = models.CharField(max_length=20, blank=True, null=True)`
  - `preferred_language = models.CharField(max_length=10, default='en', choices=[('en', 'English'), ('kn', 'Kannada'), ('hi', 'Hindi'), ('te', 'Telugu'), ('ta', 'Tamil')])`
- **`MotherProfile`**:
  - `postpartum_metadata = models.JSONField(default=dict, blank=True)`
  - `priority_mode_metadata = models.JSONField(default=dict, blank=True)`
- **`ChildProfile`**:
  - Add validator to DOB to restrict age to maximum 13 years.

## 2. Service Design
### A. Translation Service
- **Location**: `health/translation/services/translation_service.py`
- **Methods**:
  - `translate_text(text: str, target_lang: str) -> str`
    - Check django local memory cache. If hit, return.
    - If miss, invoke `deep_translator.GoogleTranslator(source='auto', target=target_lang).translate(text)`.
    - Cache results for 24 hours.

### B. Notification & Messaging Service
- **Location**: `health/notifications/services/messaging_service.py`
- **Methods**:
  - `send_alert(user_id: int, message: str, alert_type: str)`
    - Formulate request payload.
    - Queue sending using a thread pool.
    - Implement automatic retry with exponential backoff.
- **Provider Interface**:
  - `BaseSMSProvider`: abstract base class.
  - `ConsoleSMSProvider`: default concrete class that logs notifications.

### C. Postpartum Exercise Progression
- **Location**: `health/recovery/exercise_progression.py`
- **Methods**:
  - `get_recovery_recommendations(mother: MotherProfile) -> dict`
    - Calculate `days_since_delivery`.
    - If `< 90 days` (3 months): return ONLY hydration, sleep, emotional wellness, recovery tips, and safe rest suggestions.
    - If `>= 90 days`: gradually introduce walking, stretching, and low-impact recovery exercises.
    - If C-section delivery: attach additional safety warnings, longer rest periods, and fatigue considerations.

### D. Age-Specific Activity Rules
- **Location**: `health/activities/age_rules.py`
- **Methods**:
  - `get_developmental_activities(child: ChildProfile) -> list`
    - Filter activities according to medical safety rules.
    - Under 6 months: strictly recommend sensory, eye tracking, bonding, sound response. Block advanced motor, running, intensive outdoor activities.
  - `apply_priority_mode(child: ChildProfile, context: dict) -> dict`
    - If child age < 6 months, adjust dashboard layout: increase weight of vaccinations, sleep, feeding, and hydration; reduce developmental/gamified activities.

## 3. UI Design System
- **Layout Styling**: Incorporate premium glassmorphism.
- **Color Codes**:
  - Health/Normal: Soft gradient green (`#10b981` to `#059669`)
  - Warning/Action Required: Orange/Amber (`#f59e0b` to `#d97706`)
  - Urgent Red Flag: Vivid Crimson (`#ef4444` to `#dc2626`)
- **Animations**: Soft fade-ins and pulse alerts using CSS.
- **Calendar**: An interactive mood calendar displaying postpartum recovery day and logged metrics with color dots for mood.
