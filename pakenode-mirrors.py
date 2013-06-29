#!/usr/bin/env python3

import os
import sys

import clap
import pake


try:
    mode = sys.argv[1]
except IndexError:
    mode = ''
finally:
    if mode not in ['add', 'main', 'rm', 'print']:
        print('pakenode: fatal: unrecognized mode: {0}'.format(mode))
        exit()

formater = clap.formater.Formater(sys.argv[2:])
formater.format()

options = clap.parser.Parser(list(formater))
options.add(short='v', long='version')
options.add(short='h', long='help')
options.add(short='V', long='verbose')
options.add(short='R', long='root', type=str, hint='alternative root, warning: *only* for testing purposes')

if mode in ['add', 'main']: required = True
else: required = False

options.add(short='u', long='url', type=str, required=required, hint='URL from which the node can be downloaded eg. http://pake.example.com/')
options.add(short='p', long='push-url', type=str, required=required, hint='URL which will be used to connect to FTP server eg. example.com')
options.add(short='c', long='cwd', type=str, required=required, hint='directory to which pake should go before uploading files eg. /domains/example.com/public_html/pake')

try:
    options.check()
except clap.errors.UnrecognizedOptionError as e:
    print('pake: fatal: unrecognized option: {0}'.format(e))
    exit()
except clap.errors.RequiredOptionNotFoundError as e:
    print('pakenode: fatal: required option not found: {0}'.format(e))
    exit()

options.parse()
if '--help' in options:
    options.help()
    exit()
if '--version' in options:
    if '--verbose' in options: print('pake: version: {0}'.format(pake.__version__))
    else: print(pake.__version__)
    exit()


if '--root' in options: root = options.get('--root')
else: root = os.path.join(os.path.abspath(os.path.expanduser('~')), '.pakenode')

if '--verbose' in options: verbose = True
else: verbose = False


def add(url, push_url, cwd):
    pake.node.Mirrors(root).add(url)
    if verbose: print('pake: added URL to mirrors: {0}'.format(url))
    pake.node.Pushers(root).add(url, push_url, cwd)
    if verbose: print('pake: added new pusher: {0}'.format(url))


def remove(url):
    pake.node.Mirrors(root).remove(url)
    if verbose: print('pake: removed URL from mirrors: {0}'.format(url))
    pake.node.Pushers(root).remove(url)
    if verbose: print('pake: removed pusher: {0}'.format(url))


def echo():
    if verbose: mirrors = pake.node.Pushers(root)
    else: mirrors = pake.node.Mirrors(root)
    for i in mirrors.content:
        if verbose:
            print('{0} => {1}{2}'.format(i['url'], i['push-url'], i['cwd']))
        else:
            print(i)


if mode == 'add':
    add(options.get('--url'), options.get('--push-url'), options.get('--cwd'))
elif mode == 'rm':
    [remove(url) for url in options.arguments]
elif mode == 'print':
    echo()
elif mode == 'main':
    pusher = pake.node.NodePusher()
    pusher['url'] = options.get('--url')
    pusher['push-url'] = options.get('--push-url')
    pusher['cwd'] = options.get('--cwd')
