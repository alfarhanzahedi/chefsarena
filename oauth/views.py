# Django specific modules
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse

# Python specific libraries/modules
import requests
import json

# Project specific modules/variables
from chefsarena.settings import CLIENT_ID
from chefsarena.settings import CLIENT_SECRET
from chefsarena.settings import REDIRECTION_URL
from .models import UserCodechefAuth


def fetch_data(request, url):
    '''
        fetch_data(request, url) is a generic function to fetch data from the CodeChef API.
        All calls to the API is done via this function.
        It takes into account the expiration of access_token and requests for a new one 
        using the refresh_token as and when required.
    '''
    extra_data = json.loads(request.user.usercodechefauth.extra_data)
    access_token = extra_data['access_token']
    headers_for_data = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }    
    response_for_data = {}
    response_for_data = requests.get(url, headers = headers_for_data)

    if response_for_data.json()['status'] == 'error':
        # fetch new access_token
        refresh_token = extra_data['refresh_token']
        headers_for_access_token = {
            'content-Type': 'application/json',
        }
        data_for_access_token = '{"grant_type":"refresh_token" ,"refresh_token":"'+ refresh_token +'", "client_id":"'+ CLIENT_ID +'","client_secret":"'+ CLIENT_SECRET +'"}'
        response_for_access_token = requests.post('https://api.codechef.com/oauth/token', headers = headers_for_access_token, data = data_for_access_token)
        
        # save the new access_token and refresh_token received
        request.user.usercodechefauth.extra_data = str(json.dumps(response_for_access_token.json()['result']['data']))
        request.user.usercodechefauth.save()

        # try to fetch the data required again with the new access_token
        extra_data = json.loads(request.user.usercodechefauth.extra_data)
        access_token = extra_data['access_token']
        headers_for_data = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }    
        response_for_data = requests.get(url, headers = headers_for_data)
        if response_for_data.json()['status'] == 'error':
            return HttpResponse('Error! Please try again later!')
    
    # return the fetched data in JSON format
    return response_for_data.json()

def success(request):
    '''
        http://domain.com/outh/success is the callback URL for using the CodeChef API.
        The URL is assocaited with this view.
        It uses the authorisation_token received to get the access_token and refresh_token,
        and save it in the database (along with the the user's CodeChef username).
    '''
    authorisation_code = request.GET['code']
    headers = {
        'content-Type': 'application/json',
    }
    data = '{"grant_type": "authorization_code","code":"' + authorisation_code + '","client_id":"'+ CLIENT_ID +'","client_secret":"' + CLIENT_SECRET + '","redirect_uri":"' + REDIRECTION_URL + '/oauth/success"}'
    response = requests.post('https://api.codechef.com/oauth/token', headers = headers, data = data)
    print(response.json())
    response_data = response.json()['result']['data']
    access_token = response_data['access_token']

    # fetch the user's CodeChef username 
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get('https://api.codechef.com/users/me', headers = headers)
    data = response.json()['result']['data']['content']
    username = data['username']
    
    # store the username alongwith the access_token and refresh_token in the database
    try:
        user = User.objects.get(username = username)
        user.usercodechefauth.extra_data = str(json.dumps(response_data))
        user.usercodechefauth.save()
    except User.DoesNotExist:
        user = User()
        user.username = username
        user.save()
        cuser = UserCodechefAuth()
        cuser.user = user
        cuser.extra_data = str(json.dumps(response_data))
        cuser.save()

    # authenticate and login the user and redirect to homepage ('/')    
    login(request, user)
    return redirect('/')