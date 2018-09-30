# Django specific modules
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Python specific modules
import uuid
from datetime import timedelta
from datetime import datetime



class Problem(models.Model):
    '''
        code: code of the problems, ex - CCOOK
        name: name of the problem, ex - 'Small Factorials'
        author: author of thr problem
        contest_code: code of the contest from which the problem is taken
        contest_name: name of the above contest
        contest_successful_submissions: number of successful submissions made for that
            specific problem during the contest
        contest_accuracy: accuracy of the submissions made
        tags: tags associated with the problem, ex - 'dp, easy, strings'

        All the above data is fetched via the CodeChef API provided
    '''
    code = models.CharField(max_length = 16, unique = True)
    name = models.CharField(max_length = 64)
    author = models.CharField(max_length = 64)
    contest_code = models.CharField(max_length = 16)
    contest_name = models.CharField(max_length = 64)
    contest_successful_submissions = models.IntegerField()
    contest_accuracy = models.FloatField()
    tags = models.CharField(max_length = 256)

    class Meta:
        ordering = ['-contest_successful_submissions']

    def __str__(self):
        return f'{self.name} ({self.code})'

class CodeChefCookOff(models.Model):
    '''
        code: code of the CodeChef Cook-Off, ex - COOK97A
        name: name of the Cook-Off
        problems: a many-to-many field linked with the Problem model
            defined above
    '''
    code = models.CharField(max_length = 16, unique = True)
    name = models.CharField(max_length = 64)
    problems = models.ManyToManyField(Problem)

    def __str__(self):
        return f'{self.name} ({self.code}) {self.pk}'

class Contest(models.Model):
    '''
        creator: user who created the contest.
        problems: the problems selected(randomly) for the contest.
        participants: user participating in the contest.
        unqiue_id: a 32 character unique id assigned to the contest.
        start_time: time at which the contest starts, its equal to the creation time for practice contest.
                    but is supplied from the 'creater' in case of 'battle royale'.
        end_time: time at which the contest ends. Its equal to 'start_time + 10800'. 
    '''
    creator = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'contest')
    problems = models.ManyToManyField(Problem)
    participants = models.ManyToManyField(User, related_name = 'participated')
    unique_id = models.UUIDField(default = uuid.uuid4, editable = False, unique = True, blank = False)  
    start_time = models.DateTimeField(default = timezone.now, blank = False)
    end_time = models.DateTimeField()
    type = models.BooleanField(default = True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f'{self.creator.username} ({self.type})'

    def has_contest_started(self):
        return self.start_time <= timezone.now()

    def has_contest_ended(self):
        return self.end_time <= timezone.now()
    
    def time_left(self):
        return int((self.end_time - timezone.now()).total_seconds())
    
    def time_left_to_start(self):
        return int((self.start_time - timezone.now()).total_seconds())

# model/table to store the invitations of a battle
# the attribute names explains their usage. Right ?
class Invitation(models.Model):
    inviter = models.ForeignKey(User, on_delete = models.CASCADE)
    invitee = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'invited')
    contest = models.ForeignKey(Contest, on_delete = models.CASCADE)

# model/table to store the latest submission made by a user
# a detailed explanation is not provided as the attribute names does that job extremely well
class Submission(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete = models.CASCADE, related_name = 'submissions')
    problem = models.ForeignKey(Problem, on_delete = models.CASCADE)
    result = models.CharField(max_length = 4)
    time = models.DateTimeField(default = timezone.now)
    time.editable = True
    penalty = models.IntegerField(default = 0)

    def __str__(self):
        return f'{self.user.username} - {self.problem.code}'

# model/table to store a custom problemset created by a user
class CustomSet(models.Model):
    unique_id = models.UUIDField(default = uuid.uuid4, editable = False, unique = True, blank = False)  
    title = models.CharField(max_length = 32)
    description = models.CharField(max_length = 256)
    author = models.ForeignKey(User, on_delete = models.CASCADE)
    duration = models.BigIntegerField(default = 10800)
    problems = models.ManyToManyField(Problem)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.title}'