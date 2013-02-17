from django import template
from django.template.defaultfilters import stringfilter

import markdown
import datetime
import re

register = template.Library()


@register.filter
def to_datetime(value):
    timestamp = int(value)
    return datetime.datetime.fromtimestamp(timestamp)


@register.filter
def committer_email(value):
    match = re.match(r'.*<(?P<email>.*)>', value)
    if match is None:
        return value
    return match.group('email')


@register.filter
def committer(value):
    match = re.match(r'(?P<committer>.*)<.*>', value)
    if match is None:
        return value
    return match.group('committer').strip()

@register.filter
@stringfilter
def commit_message(value):
    try:
        title, _, body = value.partition('\n')
        return "<h4>{0}</h4> {1}".format(title, markdown.markdown(body))
    except:
        print "Caught an exception"
        return value
