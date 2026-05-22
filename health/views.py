from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import ChildProfile, VaccinationSchedule, NutritionRecommendation, GrowthRecord, Notification, MotherProfile, RecoveryMetric
from .forms import ChildProfileForm, GrowthRecordForm, MotherProfileForm, RecoveryMetricForm
from .logic.scheduler import generate_schedule
from .logic.recommender import get_nutrition_recommendation
from .logic.maternal_logic import get_postpartum_context, check_maternal_red_flags
from .logic.pdf_gen import generate_health_passport
from .logic.game_integration import get_validated_games
import os

# Permission Helpers
def is_parent(user):
    return user.is_authenticated and user.is_parent

def is_admin(user):
    return user.is_authenticated and user.is_vaccination_admin

# --- DASHBOARDS ---

def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    from django.contrib.auth import login as auth_login
    from .models import User, Locality
    from .services.onboarding_service import OnboardingService
    from datetime import datetime, date

    localities = Locality.objects.all()
    errors = {}
    
    if request.method == 'POST':
        # Validation
        username = request.POST.get('username')
        password = request.POST.get('password')
        delivery_date = request.POST.get('delivery_date')
        child_name = request.POST.get('child_name')
        child_date_of_birth = request.POST.get('child_date_of_birth')
        child_weight = request.POST.get('child_weight')
        child_height = request.POST.get('child_height')
        
        if not username:
            errors['username'] = "Username is required."
        elif User.objects.filter(username=username).exists():
            errors['username'] = "Username is already taken."
            
        if not password or len(password) < 6:
            errors['password'] = "Password must be at least 6 characters."
            
        if not delivery_date:
            errors['delivery_date'] = "Delivery date is required for mother's profile."
            
        # Age validation for child if child details are provided
        if child_name:
            if not child_date_of_birth:
                errors['child_date_of_birth'] = "Child date of birth is required if child details are provided."
            else:
                try:
                    dob = datetime.strptime(child_date_of_birth, '%Y-%m-%d').date()
                    today = date.today()
                    if dob > today:
                        errors['child_date_of_birth'] = "Child date of birth cannot be in the future."
                    else:
                        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                        if age > 13:
                            errors['child_date_of_birth'] = "Child age cannot exceed 13 years."
                except ValueError:
                    errors['child_date_of_birth'] = "Invalid date format."
                    
            if not child_weight:
                errors['child_weight'] = "Child weight is required if child details are provided."
            if not child_height:
                errors['child_height'] = "Child height is required if child details are provided."
                
        if not errors:
            try:
                # Delegate to the service layer for transaction-safe processing
                user = OnboardingService.process_onboarding(request.POST)
                
                # Automatically log in the user and redirect to parent_dashboard
                auth_login(request, user)
                return redirect('parent_dashboard')
            except ValueError as ve:
                errors['non_field'] = str(ve)
            except Exception as e:
                errors['non_field'] = f"An error occurred during registration: {str(e)}"
                
    return render(request, 'health/signup.html', {
        'localities': localities,
        'errors': errors,
        'data': request.POST
    })

@login_required
def index(request):
    if request.user.is_vaccination_admin:
        return redirect('admin_dashboard')
    return redirect('parent_dashboard')

@login_required
@user_passes_test(is_parent)
def parent_dashboard(request):
    children = ChildProfile.objects.filter(parent=request.user).order_by('-created_at')
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    urgent_count = notifications.filter(is_urgent=True, is_read=False).count()
    
    try:
        mother = request.user.mother_profile
    except Exception:
        mother = None
    maternal_context = None
    if mother:
        maternal_context = get_postpartum_context(mother)
        
    return render(request, 'health/parent_dashboard.html', {
        'children': children,
        'notifications': notifications,
        'urgent_count': urgent_count,
        'mother': mother,
        'maternal_context': maternal_context,
    })

@login_required
@user_passes_test(is_parent)
def children_dashboard(request):
    children = ChildProfile.objects.filter(parent=request.user).order_by('-created_at')
    return render(request, 'health/children_dashboard.html', {
        'children': children,
    })

@login_required
@user_passes_test(is_parent)
def maternal_dashboard(request):
    try:
        mother = request.user.mother_profile
    except Exception:
        mother = None
    if not mother:
        return redirect('manage_mother_profile')
        
    maternal_context = get_postpartum_context(mother)
    
    try:
        from .recovery.exercise_progression import get_exercise_guidance
        exercise_guidance = get_exercise_guidance(mother)
    except Exception:
        exercise_guidance = None
        
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    metric_form = RecoveryMetricForm()
    children = ChildProfile.objects.filter(parent=request.user).order_by('-created_at')
    
    # Fetch mood logs for calendar
    from .models import MotherExerciseMoodLog
    from django.utils import timezone
    import datetime
    import calendar
    
    thirty_days_ago = timezone.now().date() - datetime.timedelta(days=30)
    mood_logs = MotherExerciseMoodLog.objects.filter(mother=mother, date__gte=thirty_days_ago).order_by('date')
    
    # Generate current month's calendar matrix for a full responsive grid calendar
    today = datetime.date.today()
    current_year = today.year
    current_month = today.month
    month_name = calendar.month_name[current_month]
    month_cal = calendar.monthcalendar(current_year, current_month)
    
    month_logs = MotherExerciseMoodLog.objects.filter(
        mother=mother,
        date__year=current_year,
        date__month=current_month
    )
    logs_by_day = {log.date.day: log for log in month_logs}
    
    calendar_weeks = []
    for week in month_cal:
        week_days = []
        for day in week:
            if day == 0:
                week_days.append({'day': '', 'log': None, 'is_today': False})
            else:
                log = logs_by_day.get(day)
                is_today = (day == today.day)
                week_days.append({
                    'day': day,
                    'log': log,
                    'is_today': is_today
                })
        calendar_weeks.append(week_days)
        
    # Calculate shopping list based on children's recommendations and mother's pantry
    shopping_list = set()
    pantry_items = [item.strip().lower() for item in mother.pantry_items.split(',')] if mother.pantry_items else []
    
    for child in children:
        try:
            rec = child.recommendations.latest('created_at')
            for food in rec.recommended_foods.all():
                # Simple exclusion if the name contains the pantry item or vice versa
                exclude = False
                for pantry_item in pantry_items:
                    if pantry_item in food.name.lower() or food.name.lower() in pantry_item:
                        exclude = True
                        break
                if not exclude:
                    shopping_list.add(food)
        except Exception:
            pass
            
    return render(request, 'health/maternal_dashboard.html', {
        'mother': mother,
        'maternal_context': maternal_context,
        'exercise_guidance': exercise_guidance,
        'notifications': notifications,
        'metric_form': metric_form,
        'children': children,
        'mood_logs': mood_logs,
        'shopping_list': list(shopping_list),
        'calendar_weeks': calendar_weeks,
        'calendar_month_name': month_name,
        'calendar_year': current_year,
    })

@login_required
@user_passes_test(is_parent)
def delete_mother_profile(request):
    try:
        mother = request.user.mother_profile
    except Exception:
        mother = None
    if mother:
        mother.delete()
    return redirect('parent_dashboard')

def get_oracle_insights(locality):
    """
    Village Oracle Feature: Predictive analytics for health administrators.
    """
    import datetime
    current_month = datetime.datetime.now().month
    insights = []
    
    # Harvest Season Logic (Simulated for Rural India)
    if current_month in [10, 11, 4]: # Harvest months (Kharif/Rabi)
        insights.append({
            "type": "Predictive Alert",
            "message": "Peak Harvest Season: 40% of families in this locality will be busy with fields next week. Recommended: Move vaccination camp to this Sunday.",
            "urgency": "High"
        })
    
    # Weather/Climate Logic
    if current_month in [6, 7, 8]: # Monsoon
        insights.append({
            "type": "Health Insight",
            "message": "Monsoon Active: Increased risk of waterborne illness. Ensure 'Clean Water' notifications are sent to all parents.",
            "urgency": "Medium"
        })
    
    # Vaccine Density Logic
    pending_vax = VaccinationSchedule.objects.filter(child__locality=locality, status='pending').count()
    if pending_vax > 20:
        insights.append({
            "type": "Strategic Tool",
            "message": f"Concentration Alert: {pending_vax} pending vaccines detected. A cluster camp is more efficient than individual appointments.",
            "urgency": "Medium"
        })
        
    return insights

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    search_query = request.GET.get('q', '')
    if search_query:
        children = ChildProfile.objects.filter(name__icontains=search_query) | ChildProfile.objects.filter(id__icontains=search_query)
    else:
        children = ChildProfile.objects.all()
    
    # Locality Logic: Show all if admin is at a District/HQ level, else filter by specific village
    locality = request.user.locality
    if locality and "HQ" not in locality.name and "District" not in locality.name:
        children = children.filter(locality=locality)
        oracle_insights = get_oracle_insights(locality)
    else:
        oracle_insights = get_oracle_insights(locality) if locality else []
        
    return render(request, 'health/admin_dashboard.html', {
        'children': children,
        'search_query': search_query,
        'oracle_insights': oracle_insights
    })

# --- CHILD MANAGEMENT ---

@login_required
@user_passes_test(is_parent)
def add_child(request):
    if request.method == 'POST':
        form = ChildProfileForm(request.POST)
        if form.is_valid():
            mother_name = form.cleaned_data.get('mother_name')
            mother_delivery_date = form.cleaned_data.get('mother_delivery_date')
            
            child = form.save(commit=False)
            
            # Backend Normalization: Store in KG and CM
            if child.weight_unit == 'g':
                child.current_weight = float(child.current_weight) / 1000
            if child.height_unit == 'm':
                child.current_height = float(child.current_height) * 100
                
            from django.db import transaction
            import uuid
            from .models import User, MotherProfile
            from health.logic.vaccination_initializer import VaccinationInitializer
            from django.contrib import messages
            
            try:
                with transaction.atomic():
                    # Create a new unique user for this mother
                    username = f"mother_{uuid.uuid4().hex[:8]}"
                    new_user = User.objects.create_user(
                        username=username,
                        password="tempPassword123",
                        first_name=mother_name[:30] if mother_name else "",
                        is_parent=True,
                        preferred_language=request.user.preferred_language
                    )
                    
                    # Create MotherProfile for the new user
                    MotherProfile.objects.create(
                        user=new_user,
                        delivery_date=mother_delivery_date,
                        delivery_type='normal',
                        onboarding_completed=True
                    )
                    
                    # Link child to the NEW mother instead of request.user
                    child.parent = new_user
                    child.save()
                    VaccinationInitializer.initialize_for_child(child)
                    
                messages.success(request, f"Child and Mother ({mother_name}) successfully registered! Generated login: {username}")
                return redirect('add_child') # Redirect to add_child to allow continuous registration
            except Exception as e:
                messages.error(request, f"Failed to initialize child: {e}")
                return redirect('add_child')
    else:
        form = ChildProfileForm()
    return render(request, 'health/add_child.html', {'form': form})

@login_required
def child_detail(request, child_id):
    child = get_object_or_404(ChildProfile, id=child_id)
    
    # Security: Parents can only see their own children
    if not request.user.is_vaccination_admin and child.parent != request.user:
        return redirect('index')

    vaccinations = VaccinationSchedule.objects.filter(child=child).order_by('due_date')
    
    # Prepare display values based on preferences
    display_weight = child.current_weight * 1000 if child.weight_unit == 'g' else child.current_weight
    display_height = child.current_height / 100 if child.height_unit == 'm' else child.current_height
    # Nutrition Engine
    from .logic.recommender import get_nutrition_recommendation
    from django.utils import timezone
    try:
        recommendation = NutritionRecommendation.objects.filter(child=child).latest('created_at')
        
        # Check if the existing recommendation is missing the 'alt_food' key
        has_alt = True
        if recommendation.seven_day_plan:
            try:
                for day_name, meals in recommendation.seven_day_plan.items():
                    if isinstance(meals, list) and len(meals) > 0:
                        if 'alt_food' not in meals[0]:
                            has_alt = False
                            break
            except Exception:
                has_alt = False
        else:
            has_alt = False
            
        if not recommendation.seven_day_plan or recommendation.created_at.date() < timezone.now().date() or not has_alt:
            recommendation = get_nutrition_recommendation(child)
    except NutritionRecommendation.DoesNotExist:
        recommendation = get_nutrition_recommendation(child)

    # Brain Development & Offline Activities
    from .models import BedtimeStory
    if BedtimeStory.objects.count() < 7:
        try:
            from .logic.populate_activities import seed_brain_data
            seed_brain_data()
        except Exception:
            pass

    from .logic.activity_logic import get_brain_development_context
    from django.utils import timezone
    story_date = request.session.get(f'story_date_{child.id}')
    today_str = timezone.now().date().strftime('%Y%m%d')
    story_id = None
    if story_date == today_str:
        story_id = request.session.get(f'story_id_{child.id}')
        
    brain_context = get_brain_development_context(child, story_id=story_id)
    
    growth_records = child.growth_records.all().order_by('recorded_at')
    
    # Pre-Seeded Visual Metrics
    if not growth_records.exists():
        import datetime
        from django.utils import timezone
        today = timezone.now().date()
        base_weight = child.current_weight if child.current_weight else 3.5
        base_height = child.current_height if child.current_height else 50.0
        
        class MockRecord:
            def __init__(self, date, weight, height):
                self.recorded_at = date
                self.weight = weight
                self.height = height
                
        mock_records = []
        for i in range(5, -1, -1):
            mock_date = today - datetime.timedelta(days=i*30)
            mock_records.append(MockRecord(
                mock_date, 
                base_weight - (i * 0.4), 
                base_height - (i * 1.5)
            ))
        growth_records = mock_records
    
    # Prepare JSON-ready data for Charts
    growth_data = {
        'labels': [r.recorded_at.strftime('%b %d') for r in growth_records],
        'weights': [r.weight for r in growth_records],
        'heights': [r.height for r in growth_records]
    }
    
    # Calculate age for UI adaptive logic
    import datetime
    age_months = (datetime.date.today() - child.date_of_birth).days // 30
    
    current_day = datetime.date.today().strftime("%A")
    today_plan = recommendation.seven_day_plan.get(current_day, []) if recommendation.seven_day_plan else []
        
    return render(request, 'health/child_detail.html', {
        'child': child,
        'age_months': age_months,
        'brain_context': brain_context,
        'vaccinations': vaccinations,
        'recommendation': recommendation,
        'diet_plan': recommendation.seven_day_plan,
        'today_plan': today_plan,
        'current_day': current_day,
        'growth_records': growth_records,
        'growth_json': growth_data,
        'display_weight': display_weight,
        'display_height': display_height
    })

@login_required
def complete_activity(request, child_id, activity_id):
    """
    Marks an offline activity as completed for the Memory Page.
    """
    from .models import OfflineActivity, ActivityCompletion
    child = get_object_or_404(ChildProfile, id=child_id, parent=request.user)
    activity = get_object_or_404(OfflineActivity, id=activity_id)
    ActivityCompletion.objects.get_or_create(child=child, activity=activity)
    return redirect('child_detail', child_id=child.id)

@login_required
@user_passes_test(is_parent)
def shuffle_story(request, child_id):
    """
    Asynchronous Bedtime Story Refresh Engine
    Fetches a random story excluding the currently active one.
    """
    import random
    from .models import BedtimeStory
    child = get_object_or_404(ChildProfile, id=child_id, parent=request.user)
    
    current_story_title = request.GET.get('current_story_title')
    
    # Allow shuffling through ALL bedtime stories to prevent being locked into only 2 regional stories.
    stories = BedtimeStory.objects.all()
    if current_story_title:
        stories = stories.exclude(title=current_story_title)
        
    if not stories.exists():
        # Complete fallback if no other stories exist
        stories = BedtimeStory.objects.all()
        
    if not stories.exists():
        return JsonResponse({'error': 'No stories found'}, status=404)
        
    story_template = random.choice(list(stories))
    
    # Save selection to user session for the day
    from django.utils import timezone
    request.session[f'story_date_{child.id}'] = timezone.now().date().strftime('%Y%m%d')
    request.session[f'story_id_{child.id}'] = story_template.id
    
    # Calculate age tier to return the exact bg_class
    import datetime
    today = datetime.date.today()
    age_years = today.year - child.date_of_birth.year - ((today.month, today.day) < (child.date_of_birth.month, child.date_of_birth.day))
    if age_years < 2:
        tier = 'infant'
    elif age_years < 7:
        tier = 'early'
    else:
        tier = 'preteen'
        
    from .logic.activity_logic import get_story_background
    bg_class = get_story_background(tier, story_template.title)
    
    # Personalize text and lesson in real-time
    story_text = story_template.template_text
    story_lesson = story_template.moral_lesson
    locality_name = child.locality.name if child.locality else "our peaceful village"
    
    story_text = story_text.replace("[Name]", child.name).replace("[name]", child.name)
    story_text = story_text.replace("[Locality]", locality_name).replace("[locality]", locality_name)
    story_lesson = story_lesson.replace("[Name]", child.name).replace("[name]", child.name)
    story_lesson = story_lesson.replace("[Locality]", locality_name).replace("[locality]", locality_name)
    
    return JsonResponse({
        'title': story_template.title,
        'text': story_text,
        'lesson': story_lesson,
        'bg_class': bg_class
    })


# --- ADMIN ACTIONS ---

@login_required
@user_passes_test(is_admin)
def mark_vaccine_complete(request, vax_id):
    vax = get_object_or_404(VaccinationSchedule, id=vax_id)
    vax.status = 'completed'
    vax.administered_date = timezone.now().date()
    vax.save()
    
    # Create notification for parent
    Notification.objects.create(
        user=vax.child.parent,
        title="Vaccine Administered",
        message=f"The vaccine {vax.vaccine.name} has been successfully administered to {vax.child.name}."
    )
    
    return redirect('child_detail', child_id=vax.child.id)

@login_required
@user_passes_test(is_admin)
def trigger_urgent_reminder(request, child_id):
    child = get_object_or_404(ChildProfile, id=child_id)
    overdue_vaxs = VaccinationSchedule.objects.filter(child=child, status='overdue')
    
    if overdue_vaxs.exists():
        vax = overdue_vaxs.first()
        hero_term = "Heroine" if child.gender == 'F' else "Hero"
        consequence = vax.vaccine.consequence_text if vax.vaccine.consequence_text else f"Leaving your {hero_term} vulnerable to severe medical risks."
        message = f"Delaying the {vax.vaccine.name} booster leaves your {hero_term} vulnerable. {consequence} Build their immunity armor today."
    else:
        message = f"One or more vaccinations for {child.name} are overdue. Please visit the health center immediately."
        
    Notification.objects.create(
        user=child.parent,
        title="URGENT: Vaccination Overdue",
        message=message,
        is_urgent=True
    )
    return redirect('child_detail', child_id=child.id)

# --- UTILS ---

def download_passport(request, child_id):
    child = get_object_or_404(ChildProfile, id=child_id)
    if not request.user.is_vaccination_admin and child.parent != request.user:
        return redirect('index')
        
    vaccinations = VaccinationSchedule.objects.filter(child=child).order_by('due_date')
    
    # Fetch recommendation
    try:
        recommendation = NutritionRecommendation.objects.filter(child=child).latest('created_at')
    except NutritionRecommendation.DoesNotExist:
        recommendation = get_nutrition_recommendation(child)
        
    # Maternal Context for PDF
    try:
        mother = request.user.mother_profile
    except Exception:
        mother = None
    maternal_context = get_postpartum_context(mother) if mother else None
    
    pdf_path = generate_health_passport(child, vaccinations, recommendation, maternal_context)
    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=f"health_passport_{child.name}.pdf")

@login_required
def add_growth_record(request, child_id):
    child = get_object_or_404(ChildProfile, id=child_id)
    if child.parent != request.user: return redirect('index')
    
    if request.method == 'POST':
        weight = float(request.POST.get('weight'))
        height = float(request.POST.get('height'))
        
        # Normalize based on child's preference before saving to database
        norm_weight = weight / 1000 if child.weight_unit == 'g' else weight
        norm_height = height * 100 if child.height_unit == 'm' else height
        
        GrowthRecord.objects.create(child=child, weight=norm_weight, height=norm_height)
        child.current_weight = norm_weight
        child.current_height = norm_height
        child.save()
    return redirect('child_detail', child_id=child.id)

@login_required
def toggle_units(request, child_id):
    child = get_object_or_404(ChildProfile, id=child_id)
    if child.parent != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            weight_unit = data.get('weight_unit')
            height_unit = data.get('height_unit')
        except json.JSONDecodeError:
            # Fallback for standard form post
            weight_unit = request.POST.get('weight_unit')
            height_unit = request.POST.get('height_unit')
            
        if weight_unit in ['kg', 'g']:
            child.weight_unit = weight_unit
        if height_unit in ['cm', 'm']:
            child.height_unit = height_unit
        child.save()
        
        # Return new display values
        display_weight = child.current_weight * 1000 if child.weight_unit == 'g' else child.current_weight
        display_height = child.current_height / 100 if child.height_unit == 'm' else child.current_height
        
        return JsonResponse({
            'weight_unit': child.weight_unit,
            'height_unit': child.height_unit,
            'display_weight': round(display_weight, 1),
            'display_height': round(display_height, 1)
        })
    return JsonResponse({'error': 'Invalid method'}, status=400)

@login_required
@user_passes_test(is_parent)
def manage_mother_profile(request):
    try:
        mother = request.user.mother_profile
    except Exception:
        mother = None
    if request.method == 'POST':
        form = MotherProfileForm(request.POST, instance=mother)
        locality_id = request.POST.get('locality')
        if form.is_valid():
            mother = form.save(commit=False)
            mother.user = request.user
            mother.save()
            
            # Update user locality if provided
            if locality_id:
                request.user.locality_id = locality_id
                request.user.save()
                
            return redirect('parent_dashboard')
    else:
        form = MotherProfileForm(instance=mother)
    
    # Pass localities for the GPS feature
    from .models import Locality
    localities = Locality.objects.all()
    
    return render(request, 'health/manage_mother_profile.html', {
        'form': form,
        'localities': localities
    })

@login_required
@user_passes_test(is_parent)
def record_recovery_metric(request):
    mother = get_object_or_404(MotherProfile, user=request.user)
    if request.method == 'POST':
        # Handle manual form submission for better UI integration
        weight = request.POST.get('weight')
        systolic = request.POST.get('systolic_bp')
        diastolic = request.POST.get('diastolic_bp')
        symptoms = request.POST.getlist('symptoms')
        
        metric = RecoveryMetric.objects.create(
            mother=mother,
            weight=float(weight) if weight else None,
            systolic_bp=int(systolic) if systolic else None,
            diastolic_bp=int(diastolic) if diastolic else None,
            symptoms=symptoms
        )
        
        # Sync metrics to MotherProfile
        if metric.weight:
            mother.current_weight = metric.weight
        if metric.systolic_bp:
            mother.last_systolic_bp = metric.systolic_bp
        mother.save()
        
        # Check for red flags and add message
        has_red_flags = check_maternal_red_flags(metric)
        from django.contrib import messages
        if has_red_flags:
            messages.error(request, "⚠️ Vital Check: Warning detected! Please review your alerts and consult a doctor if symptoms persist.")
        else:
            messages.success(request, "✅ Health Integrity Verified: Your vitals are within stable recovery ranges.")
            
        return redirect('parent_dashboard')
    return redirect('parent_dashboard')

@login_required
@user_passes_test(is_parent)
def delete_child(request, child_id):
    child = get_object_or_404(ChildProfile, id=child_id, parent=request.user)
    child.delete()
    return redirect('parent_dashboard')

@login_required
def lactation_guide(request):
    return render(request, 'health/lactation_guide.html')

def detect_locality(request):
    try:
        lat = float(request.GET.get('lat', 0))
        lon = float(request.GET.get('lon', 0))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid coordinates provided'}, status=400)
    
    localities = Locality.objects.exclude(latitude__isnull=True)
    if not localities.exists():
        return JsonResponse({'error': 'No geocoded localities found in database'}, status=404)
        
    # Find nearest using simple Euclidean distance
    nearest = min(localities, key=lambda l: (l.latitude - lat)**2 + (l.longitude - lon)**2)
    
    return JsonResponse({
        'id': nearest.id,
        'name': nearest.name,
        'region': nearest.get_region_tag_display()
    })

@login_required
@user_passes_test(is_parent)
def evaluate_triage_view(request):
    """
    Blueprint: Triage evaluation endpoint.
    """
    try:
        mother = request.user.mother_profile
        latest_metric = RecoveryMetric.objects.filter(mother=mother).latest('recorded_at')
        
        from .logic.maternal_logic import evaluate_maternal_triage
        flags = evaluate_maternal_triage(latest_metric)
        
        return JsonResponse({'status': 'success', 'triage_flags': flags})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def log_nutrition(request):
    """
    Blueprint: NutritionLog endpoint.
    """
    from .models import NutritionLog
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            meal_type = data.get('meal_type', 'Unknown')
            food_items = data.get('food_items', '')
            iron_score = data.get('iron_score', 0)
            
            NutritionLog.objects.create(
                user=request.user,
                meal_type=meal_type,
                food_items=food_items,
                iron_score=iron_score
            )
            return JsonResponse({'status': 'success', 'message': 'Nutrition logged successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
@user_passes_test(is_parent)
def log_mood_exercise(request):
    if request.method == 'POST':
        from .models import MotherExerciseMoodLog
        import datetime
        try:
            mother = request.user.mother_profile
            mood = request.POST.get('mood')
            exercise_done = request.POST.get('exercise_done') == 'on'
            affirmation_done = request.POST.get('affirmation_done') == 'on'
            notes = request.POST.get('notes', '')
            
            # Create or update today's log
            log, created = MotherExerciseMoodLog.objects.update_or_create(
                mother=mother,
                date=datetime.date.today(),
                defaults={
                    'mood': mood,
                    'exercise_done': exercise_done,
                    'affirmation_done': affirmation_done,
                    'notes': notes
                }
            )
        except Exception as e:
            pass
    return redirect('maternal_dashboard')

@login_required
def ai_nutrition_query(request):
    """
    Asynchronous AI Nutrition Companion Query Engine.
    Provides regional, allergy-safe responses.
    """
    import json
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip().lower()
            
            # Intelligent rule-based regional and clinical response simulator
            if not query:
                return JsonResponse({'status': 'success', 'answer': 'Please ask a question about meal substitutions, allergy advice, or high-iron staples!'})
                
            if "ragi" in query or "substitute" in query or "substitution" in query:
                response_text = "Ragi is exceptionally high in calcium and iron. If you need a substitute, Bajra (Pearl Millet), Jowar (Sorghum), or Red Rice powder are excellent low-cost regional alternatives."
            elif "allergy" in query or "allergen" in query or "safe" in query:
                response_text = "For allergy safety, we dynamically substitute dairy with Almond Milk, wheat with Millets, paneer with Tofu, and ghee with Sesame Oil in all meal plans."
            elif "iron" in query or "folate" in query or "anaemia" in query or "blood" in query or "weakness" in query:
                response_text = "To fight anaemia, prioritize Spinach, Jaggery (Gur), Ragi, and beetroot. In coastal areas, clean green leaves are highly recommended."
            elif "lactation" in query or "milk supply" in query or "breastfeed" in query:
                response_text = "To naturally boost lactation, include fresh garlic, Moringa leaves, cumin seeds (jeera), and fenugreek (methi) water in your postpartum recovery diet."
            elif "weight" in query or "gain" in query or "calorie" in query:
                response_text = "Ensure you are consuming energy-dense local grains (like broken wheat dalia or red rice) with a teaspoon of cow ghee (or sesame oil if dairy-free)."
            else:
                response_text = "AI Companion: Focus on fresh, local, warm foods. Make sure to hydrate during breastfeeds and incorporate leafy greens to meet your daily micronutrient needs."
                
            return JsonResponse({'status': 'success', 'answer': response_text})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

def set_language(request):
    """
    Sets the user's preferred language in profile and session.
    """
    if request.method == 'POST':
        lang = request.POST.get('language')
        if lang in ['en', 'kn', 'hi', 'te', 'ta']:
            if request.user.is_authenticated:
                request.user.preferred_language = lang
                request.user.save()
            request.session['preferred_language'] = lang
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)

def translate_story_text(request):
    """
    Translates text to the specified language using deep-translator with caching.
    """
    import json
    from health.translation.services.translation_service import TranslationService

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        lang = data.get('lang', 'en')
        
        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)
            
        translated_text = TranslationService.translate(text, lang)
        return JsonResponse({'translated_text': translated_text})
    except Exception as e:
        print(f"Translation Error: {e}")
        # Fallback to original text if translation fails
        return JsonResponse({'translated_text': text})

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def translate_batch(request):
    """
    Translates an array of text strings dynamically for the UI.
    """
    import json
    from health.translation.services.translation_service import TranslationService
    from deep_translator import GoogleTranslator
    from django.core.cache import cache

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
        
    try:
        data = json.loads(request.body)
        texts = data.get('texts', [])
        lang = data.get('lang', 'en')
        
        if not texts or lang == 'en':
            return JsonResponse({'translations': {}})
            
        target_lang = lang.split('-')[0].lower()
        
        translations = {}
        to_translate = []
        
        for t in texts:
            cache_key = TranslationService.get_cache_key(t, target_lang)
            cached = cache.get(cache_key)
            if cached:
                translations[t] = cached
            else:
                to_translate.append(t)
                
        if to_translate:
            # Manually batch strings to make only 1 HTTP request per chunk to avoid rate limits
            chunk_size = 100
            for i in range(0, len(to_translate), chunk_size):
                chunk = to_translate[i:i+chunk_size]
                try:
                    clean_chunk = [str(c).replace('\n', ' ') for c in chunk]
                    combined = " \n\n ".join(clean_chunk)
                    
                    translator = GoogleTranslator(source='auto', target=target_lang)
                    res_combined = translator.translate(combined)
                    
                    if res_combined:
                        results = [s.strip() for s in res_combined.split('\n\n')]
                    else:
                        results = []
                        
                    if len(results) != len(chunk):
                        # Slow fallback if Google swallowed a newline
                        results = translator.translate_batch(chunk)
                        
                    for orig, res in zip(chunk, results):
                        if res:
                            translations[orig] = res
                            cache.set(TranslationService.get_cache_key(orig, target_lang), res, 86400)
                        else:
                            translations[orig] = orig
                except Exception as e:
                    print(f"Batch chunk error: {e}")
                    for orig in chunk:
                        translations[orig] = orig
                        
        return JsonResponse({'translations': translations})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def narrate_story_audio(request):
    """
    Generates audio for translated text using gTTS.
    """
    import json
    import os
    import tempfile
    from gtts import gTTS
    from health.translation.services.translation_service import TranslationService

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        lang = data.get('lang', 'en-IN')
        
        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)
            
        target_lang = lang.split('-')[0]
        
        # 1. Translate using cached TranslationService
        if target_lang != 'en':
            translated_text = TranslationService.translate(text, target_lang)
        else:
            translated_text = text
            target_lang = 'en'
            
        # 2. Generate Audio
        tts = gTTS(text=translated_text, lang=target_lang)
        
        # 3. Save to temp file
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f'narration_{target_lang}.mp3')
        tts.save(temp_file)
        
        # 4. Return as FileResponse
        response = FileResponse(open(temp_file, 'rb'), content_type='audio/mpeg')
        return response
    except Exception as e:
        print(f"Narration Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

