from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from django.db import transaction
import requests


from .forms import TeamForm, TeamPlayerForm
from .models import Team, LeagueWeek, Registration, Payment, TeamPlayer, Match
# Create your views here.


def home(request):
    active_week = LeagueWeek.objects.filter(status='OPEN').order_by('week_number').first()
    matches = Match.objects.filter(played=True).count()
    completed_weeks = LeagueWeek.objects.filter(status='CLOSED')
    
    if active_week:
        registered_count = active_week.registered_count()
        remaining_slots = 20 - int(registered_count)
        registration_progress = min(100, int(round((registered_count / active_week.max_teams) * 100))) if active_week.max_teams else 0
    else:
        registered_count = 0
        remaining_slots = 0
        registration_progress = 0

    entry_fee = Decimal(str(getattr(settings, 'REGISTRATION_FEE', '3000.00')))
    entry_fee_display = f"N{entry_fee:,.0f}"

    context = {
        'active_week': active_week,
        'registered_count': registered_count,
        'remaining_slots': remaining_slots,
        'registration_progress': registration_progress,
        'entry_fee': entry_fee,
        'entry_fee_display': entry_fee_display,
        'matches': matches,
        'completed_weeks':completed_weeks
    }

    return render(request, "home.html", context)

@login_required(login_url='login')
def register_team(request):
    existing_team = Team.objects.filter(user=request.user).first()
    if existing_team:
        return redirect('app:team', foo=existing_team.team_name)

    teamform = TeamForm()
    captainform = TeamPlayerForm(prefix='captain', role_label='captain')
    playerform = TeamPlayerForm(prefix='player', role_label='player')

    if request.method == "POST":
        teamform = TeamForm(request.POST, request.FILES)
        captainform = TeamPlayerForm(request.POST, prefix='captain', role_label='captain')
        playerform = TeamPlayerForm(request.POST, prefix='player', role_label='player')

        if teamform.is_valid() and captainform.is_valid() and playerform.is_valid():
            with transaction.atomic():
                team = teamform.save(commit=False)
                team.user = request.user
                team.save()

                captain = captainform.save(commit=False)
                captain.team = team
                captain.is_captain = True
                captain.save()

                player = playerform.save(commit=False)
                player.team = team
                player.is_captain = False
                player.save()

            messages.success(request, "Team registered successfully.")
            return redirect('app:team', foo=team.team_name)

    context = {
        "teamform": teamform,
        "captainform": captainform,
        "playerform": playerform,
        "form_action": "app:register",
        "page_title": "Register Your Team",
        "page_subtitle": "Create your team profile and add both players.",
        "form_title": "Team Registration",
        "submit_label": "Complete Registration",
    }
    return render(request, "register_team.html", context)


@login_required(login_url='login')
def edit_team(request):
    team = Team.objects.filter(user=request.user).first()
    if not team:
        messages.info(request, "Register a team before editing it.")
        return redirect('app:register')
    captain = team.players.filter(is_captain=True).first()
    player = team.players.filter(is_captain=False).first()

    teamform = TeamForm(instance=team)
    captainform = TeamPlayerForm(instance=captain, prefix='captain', role_label='captain')
    playerform = TeamPlayerForm(instance=player, prefix='player', role_label='player')

    if request.method == "POST":
        teamform = TeamForm(request.POST, request.FILES, instance=team)
        captainform = TeamPlayerForm(request.POST, instance=captain, prefix='captain', role_label='captain')
        playerform = TeamPlayerForm(request.POST, instance=player, prefix='player', role_label='player')

        if teamform.is_valid() and captainform.is_valid() and playerform.is_valid():
            with transaction.atomic():
                team = teamform.save()

                captain = captainform.save(commit=False)
                captain.team = team
                captain.is_captain = True
                captain.save()

                player = playerform.save(commit=False)
                player.team = team
                player.is_captain = False
                player.save()

            messages.success(request, "Team updated successfully.")
            return redirect('app:team', foo=team.team_name)

    context = {
        "team": team,
        "teamform": teamform,
        "captainform": captainform,
        "playerform": playerform,
        "form_action": "app:edit_team",
        "page_title": "Edit Your Team",
        "page_subtitle": "Update your team profile, captain, and player details.",
        "form_title": "Team Details",
        "submit_label": "Save Changes",
    }
    return render(request, "edit_team.html", context)

# @login_required(login_url='login')
def team_details(request, foo):
    foo = foo.replace('-', ' ')
    team = get_object_or_404(Team, team_name=foo)
    
    context = {
        'team':team
    }
    
    return render(request, "team_profile.html", context)
    

@login_required(login_url='login')
def league_register(request):
    week = LeagueWeek.objects.filter(status="OPEN").first()
    team = Team.objects.filter(user=request.user).first()
    
    if not team:
        messages.error(request, 'You Must Own A Team!!')
        return redirect('app:register')
    
    if not week:
        messages.error(request, 'No Active League Week!!')
        return redirect('app:home')
    
    try:
        team_reg = Registration.objects.get(team=team, status='CONFIRMED', week=week)
        messages.error(request, 'You Have Already Registered For This Week!!')
        return redirect('app:home')
    
    except Registration.DoesNotExist:
        try:
            registration = Registration.objects.create(
                week=week,
                team=team
            )
            
            registration.save()
            return redirect('app:initialize_payment', pk=registration.id)
        except Exception as e:
            messages.error(request, f'Error: {e}')
        
    
    return ''
        
@login_required(login_url='login')
def initialize_payment(request, pk):
    registration = get_object_or_404(Registration, id=pk)
    secret_key = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', None)
    if not secret_key:
        messages.error(request, "Payment gateway is not configured.")
        return redirect('fund_account')
    headers = {
        'Authorization': f'Bearer {secret_key}',
        'Content-Type': 'application/json',
    }
    data = {
        'tx_ref': f'{request.user.id}_{int(timezone.now().timestamp())}',
        'amount': f'{float(3000)}',
        'currency': 'NGN',
        'redirect_url': request.build_absolute_uri(f'/payment-callback/?reg={registration.id}'),
        'customer': {
            'email': request.user.email,
            'name': request.user.username,
        },
        'customizations': {
            'title': f'CANTABALL REGISTRATION - {request.user.username}',
            'description': 'KOHI DOJO CANTABALL LEAGUE',
        },
    }
    try:
        response = requests.post('https://api.flutterwave.com/v3/payments', headers=headers, json=data, timeout=10)
        response_data = response.json()
        if response.ok and response_data.get('status') == 'success':
            payment_link = response_data['data']['link']
            return redirect(payment_link)
        else:
            messages.error(request, "Failed to initialize payment. Please try again.")
            return redirect('app:league_register')
    except requests.RequestException:
        messages.error(request, "An error occurred while connecting to the payment gateway. Please try again.")
        return redirect('app:league_register')
    

def payment_callback(request):
    reg = request.GET.get('reg')
    status = request.GET.get('status')
    tx_ref = request.GET.get('tx_ref')
    transaction_id = request.GET.get('transaction_id')
    registration = get_object_or_404(Registration,id=int(reg))
    team = get_object_or_404(Team, user=request.user)
    week = LeagueWeek.objects.get(id=registration.week.id)

    if status in ['successful', 'completed'] and tx_ref and transaction_id:
        secret_key = getattr(settings, 'FLUTTERWAVE_SECRET_KEY', None)
        if not secret_key:
            messages.error(request, "Payment gateway is not configured.")
            return redirect('home')
        headers = {
            'Authorization': f'Bearer {secret_key}',
        }
        try:
            response = requests.get(f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify', headers=headers, timeout=10)
            response_data = response.json()
            if response.ok and response_data.get('status') == 'success':
                amount = float(response_data['data']['amount'])
                
                registration.status = "CONFIRMED"
                registration.save()
                
                week.max_teams -= 1
                if week.max_teams <= 0:
                    week.status = 'FULL'
                    
                week.save()
                
                Payment.objects.create(
                    team=team,
                    registration=registration,
                    amount=Decimal(amount),
                    reference=tx_ref,
                    gateway="Flutterwave",
                    status="SUCCESS"
                )
                
                messages.success(request, "Your account has been funded successfully!")
                return redirect('app:home')
            else:
                messages.error(request, "Payment verification failed. Please contact support.")
                return redirect('app:home')
        except requests.RequestException:
            messages.error(request, "An error occurred while verifying the payment. Please contact support.")
            return redirect('app:home')
    else:
        messages.error(request, "Payment was not successful. Please try again.")
        return redirect('app:home')
    
    
def fixtures(request):
    search_query = request.GET.get('q', '').strip()
    selected_week = request.GET.get('week', '').strip()
    selected_team = request.GET.get('team', '').strip()

    fixtures_qs = (
        Match.objects
        .select_related('week', 'week__season', 'team1', 'team2')
        .filter(played=False)
        .order_by('played_at', 'week__week_number', 'id')
    )

    if search_query:
        fixtures_qs = fixtures_qs.filter(
            Q(team1__team_name__icontains=search_query) |
            Q(team2__team_name__icontains=search_query)
        )

    if selected_week.isdigit():
        fixtures_qs = fixtures_qs.filter(week__week_number=int(selected_week))

    if selected_team.isdigit():
        fixtures_qs = fixtures_qs.filter(
            Q(team1_id=int(selected_team)) |
            Q(team2_id=int(selected_team))
        )

    context = {
        'fixtures': fixtures_qs,
        'weeks': LeagueWeek.objects.order_by('-week_number'),
        'teams': Team.objects.order_by('team_name'),
        'search_query': search_query,
        'selected_week': selected_week,
        'selected_team': selected_team,
        'fixtures_count': fixtures_qs.count(),
    }
    return render(request, 'fixtures.html', context)

def results(request):
    search_query = request.GET.get('q', '').strip()
    selected_week = request.GET.get('week', '').strip()
    selected_team = request.GET.get('team', '').strip()

    results_qs = (
        Match.objects
        .select_related('week', 'week__season', 'team1', 'team2', 'winner')
        .filter(played=True)
        .order_by('-played_at', '-week__week_number', '-id')
    )

    if search_query:
        results_qs = results_qs.filter(
            Q(team1__team_name__icontains=search_query) |
            Q(team2__team_name__icontains=search_query) |
            Q(winner__team_name__icontains=search_query)
        )

    if selected_week.isdigit():
        results_qs = results_qs.filter(week__week_number=int(selected_week))

    if selected_team.isdigit():
        results_qs = results_qs.filter(
            Q(team1_id=int(selected_team)) |
            Q(team2_id=int(selected_team))
        )

    context = {
        'results': results_qs,
        'weeks': LeagueWeek.objects.order_by('-week_number'),
        'teams': Team.objects.order_by('team_name'),
        'search_query': search_query,
        'selected_week': selected_week,
        'selected_team': selected_team,
        'results_count': results_qs.count(),
    }
    
    return render(request, 'results.html', context)

def rules(request):
    return render(request, 'rules.html')

def mark_match_as_played(request):
    pk = request.GET.get('pk')
    if not pk:
        return JsonResponse({'error': 'Missing match id.'}, status=400)

    match = get_object_or_404(Match, id=pk)
    
    match.played = True
    match.save()
    return JsonResponse({'message': 'Match marked as played.'}, status=200)
