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
    
    mother = getattr(request.user, 'mother_profile', None)
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
    mother = getattr(request.user, 'mother_profile', None)
    if not mother:
        return redirect('manage_mother_profile')
        
    maternal_context = get_postpartum_context(mother)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    metric_form = RecoveryMetricForm()
    children = ChildProfile.objects.filter(parent=request.user).order_by('-created_at')
    
    return render(request, 'health/maternal_dashboard.html', {
        'mother': mother,
        'maternal_context': maternal_context,
        'notifications': notifications,
        'metric_form': metric_form,
        'children': children,
    })

@login_required
@user_passes_test(is_parent)
def delete_mother_profile(request):
    mother = getattr(request.user, 'mother_profile', None)
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
            child = form.save(commit=False)
            
            # Backend Normalization: Store in KG and CM
            if child.weight_unit == 'g':
                child.current_weight = float(child.current_weight) / 1000
            if child.height_unit == 'm':
                child.current_height = float(child.current_height) * 100
                
            child.parent = request.user
            child.save()
            generate_schedule(child)
            get_nutrition_recommendation(child)
            return redirect('child_detail', child_id=child.id)
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
        if not recommendation.seven_day_plan or recommendation.created_at.date() < timezone.now().date():
            recommendation = get_nutrition_recommendation(child)
    except NutritionRecommendation.DoesNotExist:
        recommendation = get_nutrition_recommendation(child)

    # Brain Development & Offline Activities
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
        
    return render(request, 'health/child_detail.html', {
        'child': child,
        'age_months': age_months,
        'brain_context': brain_context,
        'vaccinations': vaccinations,
        'recommendation': recommendation,
        'diet_plan': recommendation.seven_day_plan,
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
    region = child.locality.region_tag if child.locality else 'NORTH_INDIA'
    
    stories = BedtimeStory.objects.filter(region_tag=region)
    if current_story_title:
        stories = stories.exclude(title=current_story_title)
        
    if not stories.exists():
        # Fallback to any other story from other regions
        stories = BedtimeStory.objects.all().exclude(title=current_story_title)
        
    if not stories.exists():
        # Complete fallback if only 1 story exists in the entire DB
        stories = BedtimeStory.objects.all()
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
    
    return JsonResponse({
        'title': story_template.title,
        'text': story_template.template_text,
        'lesson': story_template.moral_lesson,
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
    mother = getattr(request.user, 'mother_profile', None)
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
    mother = getattr(request.user, 'mother_profile', None)
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
