#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import webbrowser
import bottle

from regex_tester import index_get, index_post, server_static

DEBUG = False

if __name__ == "__main__":
    if DEBUG:
        bottle.debug(True)
        bottle.run(host='localhost', port=9999, reloader=True)
    else:
        webbrowser.open('http://127.0.0.1:9999/')
        bottle.run(host='localhost', port=9999)