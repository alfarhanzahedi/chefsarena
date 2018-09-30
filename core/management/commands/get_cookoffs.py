from django.core.management.base import BaseCommand
from core.models import CodeChefCookOff, Problem

import requests, json, time

class Command(BaseCommand):
    help = "Updates database with CodeChef COOK-OFF details and Problems."
    def add_arguments(self, parser):
        parser.add_argument('access_token', type=str, help='Indicates a valid access token to use the CodeChef API.')

    def handle(self, *args, **options):
        access_token = options['access_token']
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        url = 'https://api.codechef.com/contests?fields=code&status=past'
        contests = requests.get(url, headers = headers).json()['result']['data']['content']['contestList']
        cookoffs = filter(lambda x: 'COOK' in x['code'], contests)   
        for cookoff in cookoffs:
            cookoff = cookoff['code']
            if not CodeChefCookOff.objects.filter(code = cookoff).exists(): 
                print(f'Extracting data for {cookoff}',end=' ')   
                url = f'https://api.codechef.com/contests/{cookoff}?fields=name%2CproblemsList'
                cookoff_details = requests.get(url, headers = headers).json()['result']['data']['content']
                cookoff_name = cookoff_details['name']
                print(f'- {cookoff_name}')
                cookoff_problems = cookoff_details['problemsList']
                if cookoff_problems != []:
                    codechef_cookoff = CodeChefCookOff(code = cookoff, name = cookoff_name)
                    codechef_cookoff.save()
                    for index, problem in enumerate(cookoff_problems):
                        print(f'-> Extracting data for {problem["problemCode"]}')
                        url = f'https://api.codechef.com/contests/{cookoff}/problems/{problem["problemCode"]}?fields=problemName%2Cauthor%2Ctags'
                        problem_details = requests.get(url, headers = headers).json()['result']['data']['content']
                        try:
                            model_problem = Problem.objects.get(code = problem['problemCode'])
                        except Problem.DoesNotExist:
                            model_problem = Problem(
                                code = problem['problemCode'],
                                name = problem_details['problemName'],
                                author = problem_details['author'],
                                contest_code = cookoff,
                                contest_name = cookoff_name,
                                contest_successful_submissions = problem['successfulSubmissions'],
                                contest_accuracy = problem['accuracy'],
                                tags = str(json.dumps(problem_details['tags']))
                            )
                            model_problem.save()
                        codechef_cookoff.problems.add(model_problem)
                    print('\nGoing to sleep....')
                    time.sleep(90)
                    print('\nWaking up..!!\n')
                else:
                    print('No problems found!!\n')
