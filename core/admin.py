from django.contrib import admin

from .models import Contest
from .models import Problem
from .models import Invitation
from .models import CodeChefCookOff
from .models import Submission
from .models import CustomSet

admin.register(Contest)(admin.ModelAdmin)
admin.register(Problem)(admin.ModelAdmin)
admin.register(Invitation)(admin.ModelAdmin)
admin.register(CodeChefCookOff)(admin.ModelAdmin)
admin.register(Submission)(admin.ModelAdmin)
admin.register(CustomSet)(admin.ModelAdmin)