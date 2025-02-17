#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

# Note that while the regex tester test Python 2.7 regex idioms,
# the code base itself has been made to be run on host with Python 2.6

import re
#import sys
import os
#import webbrowser
import json

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
print('file: %s' % __file__)
print('ROOT_DIR: %s' %ROOT_DIR)

#sys.path.insert(0, os.path.join(ROOT_DIR, 'libs'))

from pprint import pformat
from operator import or_

import bottle
from bottle import get, post, request, route, view, static_file

bottle.TEMPLATE_PATH.insert(0, os.path.join(ROOT_DIR, 'views'))

CODES = {
    'search': """re.search(%(is_unicode)s%(is_raw)s'''%(regex)s''', %(is_unicode)s'''%(text)s'''%(flags_param)s)""",
    'split': """re.split(%(is_unicode)s%(is_raw)s'''%(regex)s''', %(is_unicode)s'''%(text)s'''%(flags_param)s)""",
    'findall': """re.findall(%(is_unicode)s%(is_raw)s'''%(regex)s''', %(is_unicode)s'''%(text)s'''%(flags_param)s)""",
    'match': """re.match(%(is_unicode)s%(is_raw)s'''%(regex)s''', %(is_unicode)s'''%(text)s'''%(flags_param)s)""",
    'sub': """re.sub(%(is_unicode)s%(is_raw)s'''%(regex)s''', %(is_unicode)s%(is_raw)s'''%(replace)s''', %(is_unicode)s'''%(text)s'''%(flags_param)s)""",
    'subn': """re.subn(%(is_unicode)s%(is_raw)s'''%(regex)s''', %(is_unicode)s%(is_raw)s'''%(replace)s''', %(is_unicode)s'''%(text)s'''%(flags_param)s)""",
}

FLAGS = dict((flag, getattr(re, flag)) for flag in (
    'IGNORECASE',
    'LOCALE',
    'MULTILINE',
    'DOTALL',
    'UNICODE',
    'VERBOSE'
))

DEFAULT = {
        'regex': '',
        'text': '',
        'replace': '',
        'is_unicode': '',
        'error': '',
        'code': '',
        'result': None,
        'function': 'search',
        'is_unicode': 'u',
        'is_raw': 'r',
        'markers': '[]',
    }

# todo: color matching in the text
# todo: allow arguments functions surch as maxsplit for split

@get('/')
@view('index')
def index_get():
    ctx = dict(DEFAULT)
    ctx.update(dict((flag, False) for flag in FLAGS))
    return ctx


@post('/')
@view('index')
def index_post():

    forms = request.forms
    ctx = dict(DEFAULT)
    regex = forms.get('regex', '').decode('utf-8')
    text = forms.get('text', '').decode('utf-8')
    replace = forms.get('replace', '')
    is_unicode =  'u' * bool(forms.get('is_unicode', False))
    is_raw =  'r' * bool(forms.get('is_raw', False))
    function = forms.get('function', 'search')

    set_flags = dict((flag, bool(forms.get(flag))) for flag in FLAGS)
    ctx.update(set_flags)
    set_flags = set_flags.items()
    flags = reduce(or_, (FLAGS[flag] for flag, on in set_flags if on), 0)

    if function not in CODES:
        error = u'This function is not supported'

    if regex.strip() and text.strip():

        if "'''" in regex:
            error = u"""
                        Regex containing ''' (triple single quotes) are
                        not supported
                    """
            ctx.update(locals())
            return ctx

        if not is_raw:
            regex = regex.decode('unicode_escape')
        elif regex.endswith('\\'):
            error = u"""
                        Raw string litterals ending with '\\' are not supported
                        in Python
                    """
            ctx.update(locals())
            return ctx

        if not is_unicode:
            regex = regex.encode('utf-8')
            text = text.encode('utf-8')
            replace = replace.encode('utf-8')

        try:
            pattern = re.compile(regex, flags=flags)
            if 'sub' in function:
                result = getattr(re, function)(pattern, replace, text)

            else:
                result = getattr(re, function)(pattern, text)

        except Exception as e:
            result = None
            error = u'There is an error in your regular expression'

        if result:
            if hasattr(result, 'group'):
                group = pformat(result.group())
                groupdict = pformat(result.groupdict())
                markers = result.span()
            else:
                markers = (m.span() for m in re.finditer(regex, text, flags=flags))
                markers = (x for boundaries in markers for x in boundaries)

            markers = json.dumps(tuple(markers))

        flags_param = ''
        if flags != 0:
            flags_param = ", flags=" + '|'.join('re.' + flag for flag, on in set_flags if on)
        code = CODES[function] % locals()

    ctx.update(locals())
    return ctx


@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root=os.path.join(ROOT_DIR, 'static'))