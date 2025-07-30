from nkunyim_iam.auth.common.urls import quote
from nkunyim_iam.auth.common.urls import unquote


def escape(s):
    return quote(s, safe=b"~")


def unescape(s):
    return unquote(s)
