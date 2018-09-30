# Django specific modules
from django import forms
from django.forms import ValidationError
from django.forms import models
from django.forms.fields import MultipleChoiceField
from django.contrib.auth.models import User
from django.utils import timezone

# Project specific modules/models
from .models import CustomSet
from .models import Problem

# form used to create a battle (/contest/battle/create)
class BattleForm(forms.Form):
    username_help_text = 'Enter a valid username.<br/>The user must have logged in at least once to be a valid user.'
    
    start_time = forms.DateTimeField(label='Start time', help_text = '<b>Required.</b> \
    <br/> Enter a valid date and time (in UTC) in the following format: YYYY-MM-DD HH:MM:SS. \
    <br/> If no time is provided, a default time of 00:00:00 UTC would be taken.<br/>Current UTC time: <span id="utc-time"></span>')
    
    participant_one = forms.CharField(label = 'Praticpant 1', help_text = f'<b>Required.</b><br/>{username_help_text}')
    participant_two = forms.CharField(label = 'Praticpant 2', required=False, help_text = f'{username_help_text}')
    participant_three = forms.CharField(label = 'Praticpant 3', required=False, help_text = f'{username_help_text}')
    participant_four = forms.CharField(label = 'Praticpant 4', required=False, help_text = f'{username_help_text}')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BattleForm, self).__init__(*args, **kwargs)


    # checking if the data submitted is valid or not by taking into account various
    # aspects like:
    # 1. One cannot invite himself/herself
    # 2. One cannot invite the same person twice
    # 3. One can only invite a registered user
    # so on, and so forth!
    def clean_start_time(self):
        start_time = self.cleaned_data['start_time']
        if start_time <= timezone.now():
            raise ValidationError('Enter a valid date/time')
        return start_time

    def clean_participant_one(self):
        participant_one = self.cleaned_data['participant_one'].strip()
        if not User.objects.filter(username=participant_one).exists():
            raise ValidationError(f'{participant_one} is not a valid username.')
        elif participant_one == self.request.user.username:
            raise ValidationError('You cannot invite yourself in a Battle Royale!') 
        return participant_one

    def clean_participant_two(self):
        participant_two = self.cleaned_data['participant_two'].strip()
        if participant_two == '':
            return None
        if not User.objects.filter(username=participant_two).exists():
            raise ValidationError(f'{participant_two} is not a valid username.')
        elif participant_two == self.request.user.username:
            raise ValidationError('You cannot invite yourself in a Battle Royale!') 
        elif list(self.cleaned_data.values()).count(participant_two) > 1:
            raise ValidationError('You cannot invite the same user twice!')
        return participant_two

    def clean_participant_three(self):
        participant_three = self.cleaned_data['participant_three'].strip()
        if participant_three == '':
            return None
        if not User.objects.filter(username=participant_three).exists():
            raise ValidationError(
                f'{participant_three} is not a valid username.')
        elif participant_three == self.request.user.username:
            raise ValidationError('You cannot invite yourself in a Battle Royale!') 
        elif list(self.cleaned_data.values()).count(participant_three) > 1:
            raise ValidationError('You cannot invite the same user twice!')
        return participant_three

    def clean_participant_four(self):
        participant_four = self.cleaned_data['participant_four']
        if participant_four  == '':
            return None
        if not User.objects.filter(username=participant_four).exists():
            raise ValidationError(
                f'{participant_four} is not a valid username.')
        elif participant_four == self.request.user.username:
            raise ValidationError('You cannot invite yourself in a Battle Royale!') 
        elif list(self.cleaned_data.values()).count(participant_four) > 1:
            raise ValidationError('You cannot invite the same user twice!')
        return participant_four


# customizing the ModelChoiceField made available in Django
# to have a better control at the data being displayed in the template(s)
class AdvancedModelChoiceIterator(models.ModelChoiceIterator):
    def choice(self, obj):
        return (self.field.prepare_value(obj), self.field.label_from_instance(obj), obj)

class AdvancedModelChoiceField(models.ModelMultipleChoiceField):
    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return AdvancedModelChoiceIterator(self)
    choices = property(_get_choices, MultipleChoiceField._set_choices)


# form to create a custom problemset
class CustomSetForm(forms.ModelForm):
    title = forms.CharField(max_length = 32, help_text = '<b>Required.</b><br/>Enter a suitable title for the problemset. Example: "Implementation (Easy)".<br/>Maximum length: 32 characters.')
    description = forms.CharField(max_length = 256, help_text = '<b>Required.</b><br/>Enter a suitable description for the problemset. Example: "This problemset contains easy implementation problems from the past Cook-Offs and are suitable for beginners".<br/>Maximum length: 256 characters.')
    duration = forms.CharField(widget = forms.TextInput(attrs = {'min': 20,'max': 300,'type': 'number'}), help_text = '<b>Required.</b><br/>Enter the an appropriate time duration (in minutes) within which the problemset should be solve. Example: 60 (1 hour).<br/> Duration should be between 20 to 300 minutes.')
    
    # using the above customized ModelChoiceField here
    problems = AdvancedModelChoiceField(
        widget = forms.CheckboxSelectMultiple,
        queryset = Problem.objects.all(),
        required = True,
        help_text = '<b>Required.</b><br/>Select the problems for your problemset.'
    )

    class Meta:
        model = CustomSet
        fields = ('title', 'description', 'duration', 'description',)
    
    # checking if the duration entered is valid or not
    def clean_duration(self):
        try:
            duration = int(self.cleaned_data['duration'])
        except:
            raise ValidationError('Please enter an integer between 20 and 300.')
        if duration < 20 or duration > 300:
            raise ValidationError(f'Ensure that the duration is between 20 and 300 minutes (it is {duration} minute(s)).')
        return duration
    
