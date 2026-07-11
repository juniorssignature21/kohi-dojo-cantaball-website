from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_team, name='register'),
    path('team/edit/', views.edit_team, name='edit_team'),
    path('team/<str:foo>/', views.team_details, name="team"),
    path('league/', views.league_register, name='league_register'),
    path('initialize/<int:pk>/', views.initialize_payment, name='initialize_payment'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('fixtures/', views.fixtures, name='fixtures'),
    path('results/', views.results, name='results'),
    path('rules/', views.rules, name='rules'),
    path('mark-as-played/', views.mark_match_as_played, name="mark_match"),
]
