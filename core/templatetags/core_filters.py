from django import template

from django.utils import timezone 

register = template.Library()

@register.filter(name = 'load_list_items')
def load_list_items(data):
    return ', '.join((data[2 : len(data) - 2].split('"'))[0::2])

@register.filter(name = 'has_contest_started')
def has_contest_started(obj):
    return obj.has_contest_started()

@register.filter(name = 'has_contest_ended')
def has_contest_ended(obj):
    return obj.has_contest_ended()

@register.filter(name = 'is_going_on')
def is_going_on(obj):
    if obj.start_time <= timezone.now() and obj.end_time >= timezone.now():
        return True
    return False

@register.filter(name = 'time_left')
def time_left(obj):
    if not obj:
        return -1
    if not obj.has_contest_ended():
        return obj.time_left()
    return None

@register.filter(name = 'time_left_to_start')
def time_left_to_start(obj):
    if not obj:
        return -1
    return obj.time_left_to_start()