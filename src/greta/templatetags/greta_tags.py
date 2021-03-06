from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.html import escape

from pygments import highlight
from pygments.lexers import guess_lexer_for_filename, TextLexer, DiffLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

import dulwich
import datetime
import os
import re

import logging
logger = logging.getLogger(__name__)

register = template.Library()
DIFF_PATHS_RE = re.compile(r'^diff --git a/(.*) b/(.*)$')


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
    value = escape(value)
    title, _, body = value.partition('\n')
    message = u"<h4>{0}</h4> {1}".format(title, body)
    return mark_safe(message)


@register.filter
@stringfilter
def pretty_ref(value):
    if value.startswith('refs/heads/'):
        value = value[11:]
    if value.startswith('refs/tags/'):
        value = format(value[10:])
    if value.startswith('refs/remotes/'):
        value = value[13:]
    return value

@register.filter
@stringfilter
def is_branch(value):
    return value.startswith('refs/heads/') or value == "HEAD"


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


@register.filter
@stringfilter
def basename(value):
    return os.path.basename(value)


@register.filter
@stringfilter
def dirname(value):
    return os.path.dirname(value)


@register.filter
@stringfilter
def split_path(value):
    return value.split(os.path.sep)


@register.filter
@stringfilter
def subpaths(value):
    parts = value.split(os.path.sep)
    return [os.path.sep.join(parts[0:i+1]) for i in xrange(len(parts))]


@register.filter
@stringfilter
def pretty_diffname(value):
    match = DIFF_PATHS_RE.match(value)
    if match.group(1) == match.group(2):
        return match.group(1)
    return "{0} to {1}".format(match.group(1), match.group(2))


@register.filter
def pygmentize_diff(value):
    return mark_safe(highlight(value, DiffLexer(), HtmlFormatter()))


@register.filter
def pygmentize_blob(value, path):
    try:
        lexer = guess_lexer_for_filename(path, value)
    except ClassNotFound:
        lexer = TextLexer()
    return mark_safe(highlight(value, lexer, HtmlFormatter()))
