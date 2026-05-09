from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import ChildProfile, VaccinationSchedule, NutritionRecommendation, GrowthRecord, Notification
from .forms import ChildProfileForm, GrowthRecordForm
from .logic.scheduler import generate_schedule
from .logic.recommender import get_nutrition_recommendation
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
    
    return render(request, 'health/parent_dashboard.html', {
        'children': children,
        'notifications': notifications,
        'urgent_count': urgent_count
    })

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
    
    # In a real app, filter by admin's locality
    locality = request.user.locality
    if locality:
        children = children.filter(locality=locality)
        oracle_insights = get_oracle_insights(locality)
    else:
        oracle_insights = []
        
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
    
    try:
        recommendation = NutritionRecommendation.objects.filter(child=child).latest('created_at')
        if not recommendation.seven_day_plan:
            recommendation = get_nutrition_recommendation(child)
    except NutritionRecommendation.DoesNotExist:
        recommendation = get_nutrition_recommendation(child)
    
    online_games = get_validated_games(child)
    growth_records = child.growth_records.all().order_by('recorded_at')
    
    return render(request, 'health/child_detail.html', {
        'child': child,
        'vaccinations': vaccinations,
        'recommendation': recommendation,
        'online_games': online_games,
        'diet_plan': recommendation.seven_day_plan,
        'growth_records': growth_records
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
    Notification.objects.create(
        user=child.parent,
        title="URGENT: Vaccination Overdue",
        message=f"One or more vaccinations for {child.name} are overdue. Please visit the health center immediately.",
        is_urgent=True
    )
    return redirect('child_detail', child_id=child.id)

# --- UTILS ---

def download_passport(request, child_id):
    child = get_object_or_404(ChildProfile, id=child_id)
    if not request.user.is_vaccination_admin and child.parent != request.user:
        return redirect('index')
        
    vaccinations = VaccinationSchedule.objects.filter(child=child).order_by('due_date')
    recommendation = NutritionRecommendation.objects.filter(child=child).latest('created_at')
    pdf_path = generate_health_passport(child, vaccinations, recommendation)
    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=f"health_passport_{child.name}.pdf")

@login_required
def add_growth_record(request, child_id):
    child = get_object_or_404(ChildProfile, id=child_id)
    if child.parent != request.user: return redirect('index')
    
    if request.method == 'POST':
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        GrowthRecord.objects.create(child=child, weight=weight, height=height)
        child.current_weight = weight
        child.current_height = height
        child.save()
    return redirect('child_detail', child_id=child.id)
