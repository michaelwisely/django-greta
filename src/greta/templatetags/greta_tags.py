from django import template
from django.template.defaultfilters import stringfilter

import dulwich
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


@register.filter
@stringfilter
def pretty_ref(value):
    if value.startswith('refs/heads/'):
        value = value[11:]
    if value.startswith('refs/tags/'):
        value = format(value[10:])
    return value


@register.filter
@stringfilter
def is_branch(value):
    return value.startswith('refs/heads/')


@register.filter
@stringfilter
def is_tag(value):
    return value.startswith('refs/tags/')


@register.filter
def is_tree(value):
    return isinstance(value, dulwich.repo.Tree)


@register.filter
def is_blob(value):
    return isinstance(value, dulwich.repo.Blob)
