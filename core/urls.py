# Django specific modules
from django.urls import path

# Project specific modules/views
from .views import main_landing
from .views import practice_cookoff_landing
from .views import create_practice_cookoff
from .views import practice_random_landing
from .views import create_practice_random
from .views import practice_custom_landing
from .views import create_practice_custom
from .views import solve_practice_custom
from .views import solve_practice_custom_create_contest
from .views import get_contest
from .views import end_contest
from .views import dashboard
from .views import dashboard_practice
from .views import dashboard_battles
from .views import dashboard_problemsets
from .views import edit_practice_custom
from .views import battle
from .views import accept_contest_invitation
from .views import reject_contest_invitation
from .views import practice_landing
from .views import battle_introduction
from .views import check_submission
from .views import ranklist


urlpatterns = [
    path('', main_landing),
    path('dashboard', dashboard),
    path('dashboard/practice', dashboard_practice),
    path('dashboard/battles', dashboard_battles),
    path('dashboard/problemsets', dashboard_problemsets),
    path('dashboard/problemsets/<uuid:set_id>/edit', edit_practice_custom),
    path('contest/practice', practice_landing),
    path('contest/practice/cookoff', practice_cookoff_landing),
    path('contest/practice/cookoff/create/<str:cookoff_code>', create_practice_cookoff),
    path('contest/practice/random', practice_random_landing),
    path('contest/practice/random/create', create_practice_random),
    path('contest/practice/custom', practice_custom_landing),
    path('contest/practice/custom/create', create_practice_custom),
    path('contest/practice/custom/solve', solve_practice_custom),
    path('contest/practice/custom/solve/<uuid:customset_id>', solve_practice_custom_create_contest),
    path('contest/practice/<uuid:contest_id>', get_contest, name = 'get_practice_contest'),
    path('contest/practice/<uuid:contest_id>/end', end_contest),
    path('contest/battle', battle_introduction),
    path('contest/battle/create', battle),
    path('contest/battle/<uuid:contest_id>', get_contest, name = 'get_battle_contest'),
    path('contest/battle/<uuid:contest_id>/end', end_contest),
    path('contest/battle/<uuid:contest_id>/invitation/accept', accept_contest_invitation),
    path('contest/battle/<uuid:contest_id>/invitation/reject', reject_contest_invitation),
    path('contest/practice/<uuid:contest_id>/<str:problem_code>/check', check_submission),
    path('contest/battle/<uuid:contest_id>/ranklist', ranklist),
]