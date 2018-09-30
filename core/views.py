# Django specific modules
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseServerError
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages

# Python specific modules
import random
import string
import requests
import json
import pytz
from operator import itemgetter
from datetime import datetime
from datetime import timedelta


# Project specific modules/models/forms/variables
from chefsarena.settings import CLIENT_ID
from chefsarena.settings import CLIENT_SECRET
from chefsarena.settings import REDIRECTION_URL
from oauth.views import fetch_data
from .models import Contest
from .models import Problem
from .models import Invitation
from .models import CodeChefCookOff
from .models import Submission
from .models import CustomSet
from .forms import CustomSetForm
from .forms import BattleForm


# view to handle the case when the user visits the home/landing page ('/')
def main_landing(request):
    if request.user.is_authenticated:
        template = 'core/authorised_landing_page.html'
        context = {
            'invitations_exist': invitations_present(request.user)
        }
        return render(request, template, context)
    state = ''.join(random.choices(string.ascii_letters + string.digits, k = 16))

    template = 'core/unauthorised_landing_page.html'
    context = {
        'client_id': CLIENT_ID, 'redirection_url': REDIRECTION_URL,'state': state
    }
    return render(request, template, context)

# view to generate a random practice contest/battle
def generate_contest(request, contest_type, start_time):
    contest = Contest(
        creator = request.user,
        type = contest_type
    )
    if start_time is not None:
        contest.start_time = start_time
    else:
        contest.start_time = timezone.now()
    contest.end_time = contest.start_time + timedelta(hours = 3)
    contest.save()
    first = CodeChefCookOff.objects.first().id
    last = CodeChefCookOff.objects.last().id
    random_ids = random.sample(range(first, last), 5)
    random_cookoffs = CodeChefCookOff.objects.filter(id__in = random_ids)
    for index, cookoff in enumerate(random_cookoffs):
        contest.problems.add(cookoff.problems.all()[index])
    contest.participants.add(request.user)
    contest.save()
    return contest

# view to check if a user is in a contest or not
def user_already_in_contest(request, contest_type):
    now = timezone.now()
    if Contest.objects.filter(
        creator         = request.user, 
        end_time__gt    = now,
        type            = contest_type
    ).exists():
        return True
    return False

# view to check if a user has any invitations for a bttle or not
def invitations_present(user):
    return Invitation.objects.filter(invitee = user).exists()

# view to handle the case when the user visits the practice landing page ('/contest/practice')
@login_required
def practice_landing(request):
    now = timezone.now()
    contest = None
    try:
        contest = Contest.objects.get(
            creator         = request.user, 
            start_time__lt = now, 
            end_time__gt   = now,
            type = True
        )
    except Contest.DoesNotExist:
        contest = None

    template = 'core/practice_landing.html'
    context = {
        'contest': contest,
        'invitations_exist': invitations_present(request.user)
    }
    return render(request, template, context)

# view to handle the case when the user visits the practice (random category) 
# landing page ('/contest/practice/random')
@login_required
def practice_random_landing(request):
    if user_already_in_contest(request, True):
        return redirect('/contest/practice')
    template = 'core/practice_random_landing.html'
    context = {
        'invitations_exist': invitations_present(request.user)
    }
    return render(request, template, context)
    
# view to handle the case when the user visits the practice (cook-off category) 
# landing page ('/contest/practice/cookoff')
@login_required
def practice_cookoff_landing(request):
    if user_already_in_contest(request, True):
        return redirect('/contest/practice')
    template = 'core/practice_cookoff_landing.html'
    context = {
        'cookoffs': CodeChefCookOff.objects.all().order_by('-code'),
        'invitations_exist': invitations_present(request.user)
    }
    return render(request, template, context)
    
# view to handle when the user visits the practice (custom set category) 
# landing page ('/contest/practice/custom')
@login_required
def practice_custom_landing(request):
    if user_already_in_contest(request, True):
        return redirect('/contest/practice')
    template = 'core/practice_custom_landing.html'
    context = {
        'invitations_exist': invitations_present(request.user)
    }
    return render(request, template, context)
    

# view to handle when the user visits the battle landing page ('/contest/battle')
@login_required
def battle_introduction(request):
    now = timezone.now()
    contest = None
    try:
        contest = Contest.objects.get(
            creator         = request.user,  
            end_time__gte   = now,
            type = False
        )
    except Contest.DoesNotExist:
        contest = None
    invitations_exist = Invitation.objects.filter(invitee = request.user).exists()
    template = 'core/battle_introduction.html'
    context = {
        'contest': contest,
        'invitations_exist': invitations_exist        
    }
    return render(request, template, context)

# view to creata a random practice contest
def create_practice_random(request):
    if request.user.is_authenticated:
        if user_already_in_contest(request, True):
            return redirect('/contest/practice')
        contest_id = generate_contest(request, True, None).unique_id
        return redirect(f'/contest/practice/{contest_id}')
    return redirect('/')

# view to create a cookoff practice contest
def create_practice_cookoff(request, cookoff_code):
    if request.user.is_authenticated:
        if user_already_in_contest(request, True):
            return redirect('/contest/practice')
        if cookoff_code[-1] == 'A':
            cookoff_code = cookoff_code[:-1] + 'B'
        problems = Problem.objects.filter(contest_code = cookoff_code)
        if not problems:
            return redirect('/contest/practice')
        contest = Contest(
            creator = request.user,
            type = True,
            start_time = timezone.now(),
            end_time = timezone.now() + timedelta(hours = 3)
        )
        contest.save()
        contest.problems.set(problems)
        contest.participants.add(request.user)
        contest.save()
        return redirect(f'/contest/practice/{contest.unique_id}')
    return redirect('/')

# view to create a custom problemset
@login_required
def create_practice_custom(request):
    if request.method == 'POST':
        form = CustomSetForm(request.POST)
        if form.is_valid():
            custom_set = CustomSet(
                title = form.cleaned_data['title'],
                description = form.cleaned_data['description'],
                author = request.user,
                duration = form.cleaned_data['duration'],
            )
            custom_set.save()
            custom_set.problems.set(form.cleaned_data['problems'])
            custom_set.save()
            messages.success(request, 'Your problemset was created successfully! You can view it in your dashboard.')
            return redirect('/contest/practice/custom/create')
        else:
            return render(request, 'core/create_practice_custom.html', {'form': form})
    form = CustomSetForm()
    return render(request, 'core/create_practice_custom.html', {'form': form})

# view to edit a custom problemset
@login_required
def edit_practice_custom(request, set_id):
    problemset = None
    try:
        problemset = CustomSet.objects.prefetch_related('problems').get(
            unique_id = set_id,
            author = request.user
        )
    except CustomSet.DoesNotExist:
        return redirect('/dashboard')
    if request.method == 'POST':
        form = CustomSetForm(request.POST, instance = problemset)
        if form.is_valid():
            problemset.title = form.cleaned_data['title']
            problemset.description = form.cleaned_data['description']
            problemset.duration = form.cleaned_data['duration']       
            problemset.problems.set(form.cleaned_data['problems'])
            problemset.save()
            messages.success(request, 'Your problemset was updated successfully!')
            return redirect(f'/dashboard/problemsets/{problemset.unique_id}/edit')
    form = CustomSetForm(instance = problemset)    
    return render(request, 'core/edit_practice_custom.html', {'form': form})

# view to create a contest from a custom problemset - landing page
@login_required
def solve_practice_custom(request):
    if user_already_in_contest(request, True):
        return redirect('/contest/practice')
    template = 'core/solve_practice_custom.html'
    context = {
        'invitations_present': invitations_present(request.user),
        'custom_sets': CustomSet.objects.select_related('author').prefetch_related('problems').all()  
    }
    return render(request, template, context)

# view to create a contest from a custom problemset - logic
@login_required
def solve_practice_custom_create_contest(request, customset_id):
    if user_already_in_contest(request, True):
        return redirect('/contest/practice')
    try:
        custom_set = CustomSet.objects.prefetch_related('problems').get(unique_id = customset_id)
    except CustomSet.DoesNotExist:
        return redirect('/contest/practice')
    contest = Contest(
        creator = request.user,
        type = True,
        start_time = timezone.now(),
        end_time = timezone.now() + timedelta(minutes = custom_set.duration)
    )
    contest.save()
    for problem in custom_set.problems.all():
        contest.problems.add(problem)
    contest.participants.add(request.user)
    contest.save()
    return redirect(f'/contest/practice/{contest.unique_id}')
    

# view to create a an Invitation
def create_invitaion(request, username, contest):
    invitation = Invitation()
    invitation.inviter = request.user
    invitation.invitee = User.objects.get(username = username)
    invitation.contest = contest
    invitation.save()

# view to handle GET/POST on '/practice/battle/create'
def battle(request):
    if request.user.is_authenticated:
        if user_already_in_contest(request, False):
            return redirect('/contest/battle')
        invitations_exist = Invitation.objects.filter(invitee = request.user).exists()        
        if request.method == 'POST':
            form = BattleForm(request.POST, request = request)
            if form.is_valid():
                contest = generate_contest(request, False, form.cleaned_data['start_time'])                
                create_invitaion(request, form.cleaned_data['participant_one'], contest)
                if form.cleaned_data['participant_two'] is not None:
                    create_invitaion(request, form.cleaned_data['participant_two'], contest)
                if form.cleaned_data['participant_three'] is not None:
                    create_invitaion(request, form.cleaned_data['participant_three'], contest)
                if form.cleaned_data['participant_four'] is not None:
                    create_invitaion(request, form.cleaned_data['participant_four'], contest)
                return redirect(f'/contest/battle/{contest.unique_id}') 
            else:
                return render(request, 'core/battle_init.html', {'form': form, 'invitations_exist': invitations_exist})         
        else:
            if user_already_in_contest(request, False):
                return redirect('/contest/battle')
        form = BattleForm()
        return render(request, 'core/battle_init.html', {'form': form, 'invitations_exist': invitations_exist})
    return redirect('/')

# view to fetch a contest based on contest_id
# along with submission status and score of the user
def get_contest(request, contest_id):
    if request.user.is_authenticated:
        contest = Contest.objects.prefetch_related('creator', 'problems', 'participants').get(unique_id=contest_id)
        if request.user not in contest.participants.all():
            return redirect('/')        
        score = 0
        penalty = 0
        submissions = Submission.objects.select_related('problem').filter(user = request.user, contest = contest)            
        accepted_solutions = []
        wrong_solutions = []
        for temp in submissions.filter(result = 'AC'):
            accepted_solutions.append(temp.problem)
            penalty += temp.penalty
        for temp in submissions.filter(result = 'WA'):
            wrong_solutions.append(temp.problem)
        for problem in contest.problems.all():
            problem.accepted = 0
            if problem in accepted_solutions:
                problem.accepted = 1
                score += 1
            elif problem in wrong_solutions:
                problem.accepted = 2
        if contest.type:
            invitations_exist = Invitation.objects.filter(invitee = request.user).exists()
            context = {
                'contest': contest, 
                'score': score, 
                'penalty': penalty, 
                'invitations_exist': invitations_exist
            }        
            return render(request, 'core/practice.html', context)
        else:
            invitations = Invitation.objects.prefetch_related('invitee').filter(contest = contest)
            if invitations.filter(invitee = request.user).exists():
                invitations_exist = True
            else:
                invitations_exist = False
                context = {
                    'contest': contest, 
                    'score': score, 
                    'penalty': penalty, 
                    'invitations': invitations, 
                    'invitations_exist': invitations_exist
                }
            return render(request, 'core/battle.html', context)
    return redirect('/')

# view to handle the case when the user decides to end a practice contest
def end_contest(request, contest_id):
    if request.user.is_authenticated:
        try:
            contest = Contest.objects.get(creator = request.user, unique_id = contest_id, end_time__gte = timezone.now(), type = True)
        except Contest.DoesNotExist:
            return redirect('/')
        contest.end_time = timezone.now()
        contest.save()
        return redirect('/contest/practice')

# view to handle the case when a user visits his/her dahsboard
def dashboard(request):
    if request.user.is_authenticated:
        practice_contests = Contest.objects.select_related('creator').filter(
            creator = request.user, type = True)[:5]
        battles = Contest.objects.select_related('creator').filter(
            participants = request.user, type = False
        )[:5]
        problemsets = CustomSet.objects.prefetch_related('problems').filter(
            author = request.user
        )[:5]
        invitations = Invitation.objects.select_related('inviter', 'contest').filter(invitee = request.user)
        if invitations:
            invitations_exist = True
        else:
            invitations_exist = False
        context = {
            'practice_contests': practice_contests, 
            'invitations': invitations, 
            'battles': battles, 
            'invitations_exist': invitations_exist, 
            'problemsets': problemsets
        }
        return render(request, 'core/dashboard.html', context)
    return redirect('/')

@login_required
def dashboard_practice(request):
    practice_contests = Contest.objects.select_related('creator').filter(
        creator = request.user, type = True)
    return render(request, 'core/dashboard_practice.html', {'practice_contests': practice_contests, 'invitations_exist': invitations_present(request.user) })

@login_required
def dashboard_battles(request):
    battles = Contest.objects.select_related('creator').filter(
        participants = request.user, type = False)
    return render(request, 'core/dashboard_battles.html', {'battles': battles, 'invitations_exist': invitations_present(request.user) })

@login_required
def dashboard_problemsets(request):
    problemsets = CustomSet.objects.prefetch_related('problems').filter(
            author = request.user
    )
    return render(request, 'core/dashboard_problemsets.html', {'problemsets': problemsets, 'invitations_exist': invitations_present(request.user) })

# views to handle the cases when a user accepts/rejects an invitation
def accept_contest_invitation(request, contest_id):
    if request.user.is_authenticated:
        try:
            contest = Contest.objects.get(unique_id = contest_id)
        except Contest.DoesNotExist:
            return redirect('/') 
        
        try:
            invitation = Invitation.objects.get(invitee = request.user, contest = contest)
        except Invitation.DoesNotExist:
            return redirect('/')
        
        contest.participants.add(request.user)
        contest.save()
        invitation.delete()
        return redirect(f'/contest/battle/{contest.unique_id}')
    return redirect('/')

def reject_contest_invitation(request, contest_id):
    if request.user.is_authenticated:
        try:
            contest = Contest.objects.get(unique_id = contest_id)
        except Contest.DoesNotExist:
            return redirect('/') 
        
        try:
            invitation = Invitation.objects.get(invitee = request.user, contest = contest)
        except Invitation.DoesNotExist:
            return redirect('/')

        invitation.delete()
        return redirect('/dashboard')
    return redirect('/')

# view to convert IST to UTC
# (since CodeChef API returns datetime in IST)
def get_datetime_in_utc(submission_time):
    obj = datetime.strptime(submission_time, '%Y-%m-%d %H:%M:%S')
    obj = pytz.timezone('Asia/Kolkata').localize(obj)
    return obj.astimezone(pytz.utc)

# view to handle the case when the user requests to check the 
# status of his/her solution
def check_submission(request, contest_id, problem_code):
    if request.user.is_authenticated:
        try:
            contest = Contest.objects.get(unique_id = contest_id, start_time__lte = timezone.now(), end_time__gte = timezone.now())
        except Contest.DoesNotExist:
            return redirect('/')
        
        try:
            problem = Problem.objects.get(code = problem_code)
        except Problem.DoesNotExist:
            return redirect('/')
        
        url = f'https://api.codechef.com/submissions/?username={request.user.username}&problemCode={problem_code}&fields=date%2C%20result'
        response = fetch_data(request, url)
        
        if response['result']['data']['code'] == 9001:
            submissions = response['result']['data']['content']
            score = Submission.objects.filter(user = request.user, contest = contest, result = 'AC').count()
            penalty = Submission.objects.filter(user = request.user, contest = contest, result = 'AC').aggregate(sum = Sum('penalty'))
            if (penalty['sum'] == None):
                penalty = 0
            else:
                penalty = penalty['sum']
            try:
                submission_model = Submission.objects.get(user = request.user, contest = contest, problem = problem)
                if submission_model.result == 'AC':
                    return JsonResponse({"status":"AC", "penalty":penalty, "score":score})
                else:
                    submissions_temp = []
                    for submission in submissions:
                        submission_datetime_utc = get_datetime_in_utc(submission['date'])
                        if submission_datetime_utc > submission_model.time and submission_datetime_utc <= contest.end_time:
                            submissions_temp.append([submission['result'], submission_datetime_utc])
                    if submissions_temp:
                        i_penalty = submission_model.penalty
                        status = 'WA'
                        time = submissions_temp[-1][1]
                        submissions_temp.sort(key = lambda x : x[1])
                        for submission in submissions_temp:
                            if submission[0] == 'AC':
                                status = 'AC'
                                score += 1
                                time = submission[1]
                                break
                            elif submission[0] != 'CTE':
                                i_penalty += 1
                        submission_model.result = status 
                        submission_model.time = time
                        submission_model.penalty = i_penalty
                        submission_model.save()
                        if status == 'AC':
                            penalty += i_penalty
                        return JsonResponse({"status":status, "penalty":penalty, "score":score})
                    else:
                        return JsonResponse({"status":"NA"})  
            except Submission.DoesNotExist:
                submissions_temp = []
                for submission in submissions:
                    submission_datetime_utc = get_datetime_in_utc(submission['date'])
                    if submission_datetime_utc >= contest.start_time and submission_datetime_utc <= contest.end_time:
                        submissions_temp.append([submission['result'], submission_datetime_utc])
                if submissions_temp:
                    i_penalty = 0
                    status = 'WA'
                    submissions_temp.sort(key = lambda x : x[1])
                    time = submissions_temp[-1][1]
                    for submission in submissions_temp:
                        if submission[0] == 'AC':
                            status = 'AC'
                            time = submission[1]
                            score += 1
                            break
                        elif submission[0] != 'CTE':
                            i_penalty += 1
                    submission_model = Submission(user = request.user, contest = contest, problem = problem, result = status, time = time, penalty = i_penalty)
                    submission_model.save()
                    if status == 'AC':
                        penalty += i_penalty
                    return JsonResponse({"status":status, "penalty":penalty, "score":score})
                else:
                    return JsonResponse({"status":"NA"})  
        else:
            return JsonResponse({"status":"NA"})
    return redirect('/')


# view to handle the case when the user requests for the ranklist of a battle
def ranklist(request, contest_id):
    contest = Contest.objects.prefetch_related('problems', 'participants').get(unique_id = contest_id)
    if request.user not in contest.participants.all():
        return redirect('/')
    invitations_exist = Invitation.objects.filter(invitee = request.user).exists()        
    participant_details = []
    for participant in contest.participants.all():
        details = {}
        submitted = []
        total_score = 0
        total_time = 0
        total_penalty = 0
        details['username'] = participant.username
        details['problems'] = {}
        submissions = Submission.objects.select_related('problem').filter(user = participant, contest = contest, result = 'AC')
        for submission in submissions:
            submitted.append(submission.problem)
        for problem in contest.problems.all():
            details['problems'][str(problem)] = {}
            details['problems'][str(problem)]['status'] = '-'
            details['problems'][str(problem)]['penalty'] = ''
            if problem in submitted:
                details['problems'][str(problem)]['status'] = 1
                temp = submissions.get(problem = problem)
                total_score += 1
                total_time += ((temp.time - contest.start_time).total_seconds() + (1200 * temp.penalty))
                details['problems'][str(problem)]['penalty'] = temp.penalty 
                total_penalty += temp.penalty
        details['score'] = total_score
        details['total_penalty'] = total_penalty
        details['total_time'] = str(timedelta(seconds = int(total_time)))
        participant_details.append(details)
    participant_details.sort(key = itemgetter('total_time'))
    participant_details.sort(key = itemgetter('score'), reverse = True)
    return render(request, 'core/ranklist.html', {'contest': contest, 'participant_details': participant_details, 'invitations_exist': invitations_exist})

# view to handle 404 error
def handler404(request, exception):
    return render(request, 'core/404.html', locals())

# view to handle 500 error - when API consumption limit is reached!
def handler500(request):
    return render(request, 'core/500.html', locals())