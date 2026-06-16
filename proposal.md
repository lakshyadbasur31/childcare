# Bharat-Health Guardian Enhancements Proposal

## 1. Architecture Strategy
To maintain the integrity of the existing Django healthcare platform, we follow a strictly modular, service-oriented extension strategy:
- **Thin Views, Fat Services**: All business logic (e.g., translation, messaging, age-specific validation, maternal exercise progression) is decoupled from `views.py` and placed in dedicated service modules.
- **Modular Directory Layout**:
  - `health/translation/services/translation_service.py` for regional translations.
  - `health/notifications/services/messaging_service.py` for SMS/WhatsApp alert dispatch.
  - `health/recovery/exercise_progression.py` for postnatal recovery progression.
  - `health/activities/age_rules.py` for infant age tier filtering and priority mode rules.
- **Backward Compatibility**: Existing database schemas, child profiles, and vaccination schedules are preserved. All new fields (`phone_number`, `preferred_language`, etc.) will have safe default values.

## 2. Migration Strategy
All migrations are non-destructive and backward compatible:
1. **Explain Migrations**: Before running any migration, we will detail the tables affected and validation rules.
2. **Add Fields Safely**:
   - `User.phone_number` will be a nullable or blank-enabled `CharField` to avoid breaking existing users.
   - `User.preferred_language` will be a `CharField` defaulting to `'en'` (English).
   - `MotherProfile.priority_mode_metadata` and `postpartum_metadata` will be `JSONField`s with empty dict defaults to store dynamic metrics without schema bloating.
3. **Pre-populated Values**: Run-time checks or data seeds will populate any missing parameters for old records.

## 3. Modular Structure
New directories will be created under `health/`:
- `health/services/`: Generic platform services.
- `health/translation/`: Dynamic/static translation mechanisms.
- `health/notifications/`: SMS-ready and future WhatsApp-ready alert dispatch.
- `health/recovery/`: Postpartum exercise and wellness logic.
- `health/activities/`: Child age rules and infant activity filtering.

## 4. Service Design
Each feature is encapsulated in a service class/module:
- `TranslationService`: Translates strings dynamically using `deep-translator` (free Google Translator API) with caching to prevent API abuse.
- `MessagingService`: Implements a provider-based abstraction for notifications, supporting async dispatch (thread-based background queues) and retry safety.
- `ExerciseProgression`: Implements rule-based postpartum recovery guides.
- `AgeRules`: Validates developmental activities and manages infant priority mode.

## 5. API Design
- `POST /api/translate/`: Dynamic string translation.
- `POST /api/onboard/`: Redesigned Mother-first child onboarding transaction.
- `GET/POST /maternal/log-mood/`: Hydration, sleep, mood, and recovery logs.

## 6. UI Enhancement Strategy
- Maternal Dashboard: Update `maternal_dashboard.html` to introduce glassmorphism CSS styling, CSS animations, interactive cards for sleep/hydration, and a mood indicator calendar.
- Navbar/Profile Settings: Dropdown selection for Language (English, Kannada, Hindi, Telugu, Tamil).

## 7. Testing Strategy
- **Unit Tests**: Test case suites for the new translation service, age rules engine, and maternal exercise constraints.
- **Integration Tests**: Transaction validation for Mother-First child onboarding flow.
- **Regression Tests**: Ensure the vaccination scheduler, PDF generator, and nutrition recommender remain completely functional.

## 8. Rollback Strategy
- Database backups will be simulated or generated.
- Migration rollbacks (`python manage.py migrate health <previous_migration_name>`) will be defined for each database change step.

## 9. Scalability Planning
- Queue-ready architecture: Notifications can be easily ported to Celery or Django-Q task workers without changing core business code.
- Translation caching reduces external API latencies to 0ms for cached strings.
