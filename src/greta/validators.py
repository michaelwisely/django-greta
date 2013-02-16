from django.core.exceptions import ValidationError

import re

REPO_NAME_REGEX = re.compile(r'^[\w-]+\.git$')


def repo_name_validator(value):
    if REPO_NAME_REGEX.match(value) is None:
        msg = 'Bad repository name. Make sure it ends with ".git"'
        raise ValidationError(msg)
