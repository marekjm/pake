#!/usr/bin/env python3


"""Interface to PAKE node.

SYNTAX:
    pakenode [global_opts...] [mode [mode_opts...] [submode [submode_opts...]...]]


GLOBAL OPTIONS:
    These options can be placed before or after mode declaration.

{0}

----

This program is part of the PAKE toolset and is published under GNU GPL v3+ license.
Text of the license can be found at: https://gnu.org/licenses/gpl.html

Copyright Marek Marecki (c) 2013"""


import getpass
import os
import sys
import urllib
import warnings

import clap
import pake


uifile = pake.shared.getuipath('node')
if not uifile: exit('pake: ui: fatal: no ui file found')

formater = clap.formater.Formater(sys.argv[1:])
formater.format()

builder = clap.builder.Builder(path=uifile, argv=list(formater))
builder.build()

ui = pake.shared.checkinput(builder.get())


if '--version' in ui:
    print(pake.__version__)
    exit()

if '--help' in ui:
    print(__doc__.format('\n'.join(clap.helper.Helper(ui).help()[1:])))
    exit()


root = pake.shared.getnodepath()
fail = False

# this will exit the program if there is no node on which to operate
# unless the program is called in `init` mode because it means that user will be initializing the node
if not root and str(ui) != 'init': exit('pake: fatal: no root found')


# If everything went fine, which means:
#   * root was found,
#   * UI files were found,
#   * UI has been built.
#
# Execute according to user input.

reqs = []  # list of requests to run

if str(ui) == 'init':
    """This mode is used for initialization of local node.
    Note, that when you'll reinitialize all config JSON will
    be overwritten.
    """
    if root:
        if '--debug' in ui:
            print('pake: debug: node already exists in {0}'.format(root))
        if '--regen' in ui:
            """In the regeneration mode we want to preserve config files but generate entirely new directory
            structure. This is useful when updating.
            """
            reqs.append({'act': 'node.manager.reinit', 'path': root})
            if '--debug' in ui: print('pake: debug: stored config files in memory')
        elif '--force' in ui:
            """This means that a user wants to reinitialize the node.
            We will remove everything from the old one so the environment is clean and
            new node can be initialized.
            """
            reqs.append({'act': 'node.manager.remove', 'path': root})
            if '--debug' in ui: print('pake: debug: old node will be removed from {0}'.format(root))
        else:
            """Node cannot be initialized because it's already present.
            """
            message = 'pake: fatal: node cannot be initialized'
            if '--verbose' in ui: message += ' in {0}'.format(root)
            print(message)
            fail = True
    if not fail:
        """If everything went fine so far it means that we can try to create a node.
        """
        root = pake.shared.getnodepath(check=False)
        if not reqs: reqs.append({'act': 'node.manager.init', 'path': root})
        pake.transactions.runner.Runner(root=root, requests=reqs).finalize().run()
        if '--force' in ui or '--regen' in ui: message = 'pake: node reinitialized'
        else: message = 'pake: node initialized'
        if '--verbose' in ui: message += ' in {0}'.format(root)
        if '--quiet' not in ui: print(message)
elif str(ui) == 'meta':
    """Logic for meta.json manipulation.
    """
    if '--set' in ui:
        key, value = ui.get('--set')
        request = {'act': 'node.config.meta.set', 'key': key, 'value': value}
        pake.transactions.runner.Runner(root=root).execute(request)
    if '--remove' in ui:
        request = {'act': 'node.config.meta.remove', 'key': ui.get('--remove')}
        pake.transactions.runner.Runner(root=root).execute(request)
    if '--get' in ui:
        request = {'act': 'node.config.meta.get', 'key': ui.get('--get')}
        print(pake.transactions.runner.Runner(root=root).execute(request).getstack()[-1])
    if '--list-keys' in ui:
        request = {'act': 'node.config.meta.getkeys'}
        keys = pake.transactions.runner.Runner(root=root).execute(request).getstack()[-1]
        meta = pake.config.node.Meta(os.path.join(root, '.pakenode'))
        if '--verbose' in ui:
            for key in sorted(keys):
                value = pake.transactions.runner.Runner(root=root).execute({'act': 'node.config.meta.get', 'key': key}).getstack()[-1]
                print('{0}: {1}'.format(key, value))
        else:
            s = ', '.join(sorted(keys))
            if s: print(s)
    if '--reset' in ui:
        pake.transactions.runner.Runner(root=root).execute({'act': 'node.config.meta.reset'})
    if '--pretty' in ui:
        """This should be independent from
        other options to always enable the possibility
        to format JSON in pretty way

        No transaction for it is available for this.
        """
        pake.config.node.Meta(root).write(pretty=True)
elif str(ui) == 'mirrors':
    """This mode is used for management of pushers list.
    """
    pushers = pake.config.node.Pushers(root)

    if '--add' in ui:
        """Code used to add mirrors and pushers which are very much alike each other.
        *Mirrors* are visible to the outside network and are just a list of URLs while
        *pushers* contain additional data:
            - host which is used for connection,
            - directory to which PAKE should go.
        """
        url = ui.get('--url')
        host = ui.get('--host')
        cwd = ui.get('--cwd')
        if url not in pushers:
            """If URL is not in mirrors everything's fine and we can just add it to the list
            of pushers and mirrors.
            """
            pushers.add(url=url, host=host, cwd=cwd).write()
            message = 'pake: node: added mirror'
            if '--verbose' in ui: message += ' {0}'.format(url)
            if '--quiet' not in ui: print(message)
        else:
            """Otherwise fail and tell user that mirror with this URL already exists.
            """
            message = 'pake: node: fail: mirror already exists'
            if '--verbose' in ui: message += ': {0}'.format(url)
            if '--quiet' not in ui: print(message)
    if '--remove' in ui:
        """Code used to remove mirrors and pushers.
        Mirrors and pushers are identified via URLs because they are unique - hostnames and directories may be
        the same across different mirrors.
        """
        url = ui.get('--remove')
        mirrors.remove(url).write()
        pushers.remove(url).write()
        message = 'pake: node: mirror removed'
        if '--verbose' in ui: message += ': {0}'.format(url)
        if '--quiet' not in ui: print(message)
    if '--list' in ui:
        if '--verbose' in ui:
            for m in pushers:
                print(' * {0}'.format(m['url']))
                print('   + host: {0}'.format(m['host']))
                print('   + cwd:  {0}'.format(m['cwd']))
        else:
            for m in mirrors: print(m)
    if '--gen-list' in ui:
        """Used to generate mirrors.json list which is sent to server and
        is served to the network.
        """
        pake.node.pusher.genmirrorlist(root)
        if '--quiet' not in ui: print('pake: generated mirrors.json list...')
    if '--pretty' in ui:
        """Format pushers.json in a pretty (more human readable form).
        """
        pushers.write(pretty=True)
        if '--verbose' in ui: print('pake: formatted pushers.json')
elif str(ui) == 'push':
    """This mode is used to push node's contents to mirror servers on the Net.
    """
    def getcredentials(url, pushers):
        """Returns two-tuple (username, password) for given URL.
        Prompting user to enter them.
        """
        username = input('Username for {0}: '.format(url))
        prompt = 'Password for {0}@{1}: '.format(username, pushers.get(url)['host'])
        password = getpass.getpass(prompt)
        return (username, password)

    pushers = pake.config.node.Pushers(root)
    mirrors = pushers.geturls()
    installed = '--installed' in ui  # whether push also installed.json file
    credentials = []
    if '--only' in ui: urls = [ui.get('--only')]
    if '--only-main' in ui: urls = [pake.config.node.Meta(root).get('url')]
    else: urls = [m for m in mirrors]

    for url in urls:
        # check input for invalid mirror URLs
        if url in mirrors:
            # if a URL is valid ask for credentials
            try:
                credentials.append(getcredentials(url, pushers))
            except KeyboardInterrupt:
                # append empty credentials - do not push to this mirror
                credentials.append(())
                print()
            except EOFError:
                # cancel push operation
                print()
                exit()
        else:
            # if it's not valid print error message
            print('pake: fail: no such mirror: {0}'.format(url))
            # and append empty credentials to keep indexes synced
            credentials.append(())

    # this is a line break between credentials input and
    # reports about push status
    print()

    for i, url in enumerate(urls):
        # enumeration is required to get index for credentials
        # they are stored in a list synced with list of URLs
        if credentials[i]:
            print('* pushing to mirror {0}...'.format(url))
            username, password = credentials[i]
            try:
                pake.node.pusher.push(root, url, username, password, reupload=('--reupload' in ui))
                message = '* pushing to mirror {0}: OK'.format(url)
            except KeyboardInterrupt:
                message = '* pushing to mirror {0}: cancelled by user'.format(url)
            except Exception as e:
                if '--debug' in ui:
                    # if running with --debug option reraise the exception to
                    # provide stack trace and debug info
                    message = '* pushing to mirror {0}: failed: showing debug trace'.format(url)
                    print()
                    raise
                else:
                    # otherwise, silence the exception and just show error message
                    message = '* pushing to mirror {0}: failed: {1} (cause: {2})'.format(url, e, str(type(e))[8:-2])
            finally:
                print(message)
elif str(ui) == 'aliens':
    """This mode is used for aliens.
    """
    aliens = pake.config.node.Aliens(root)
    if '--add' in ui:
        """This is used to add an alien to the network.
        """
        url = ui.get('--add')
        if url[-1] == '/': url = url[:-1]
        try:
            added = pake.aliens.manager.add(root, url)
            message = 'pake: alien added: {0}'.format(added['meta']['url'])
            if '--verbose' in ui:
                """Print some additional data about the alien if --verbose option is found.
                """
                message = ' (with {0} mirror(s))'.format(len(added['mirrors']))
        except KeyboardInterrupt as e:
            """Operation cancelled by user. Just print the message.
            Empty print if for adding a line break after the ^C (it looks nicer this way).
            """
            print()
            message = 'pake: operation cancelled'
        except urllib.error.URLError as e:
            """This is most likely 404 error.
            """
            message = 'pake: fail: alien was not found: {0}'.format(e)
        except Exception as e:
            """By default silence all exception and just print out the error message to not scare the user too much.
            However, if --debug option is found reraise the exception to show stack trace.
            """
            message = 'pake: adding alien failed: {0} ({1})'.format(e, type(e))
            if '--debug' in ui: raise
        finally:
            if '--quiet' not in ui: print(message)
    if '--remove' in ui:
        try:
            aliens.remove(ui.get('--remove'))
            message = 'pake: alien removed'
        except KeyError as e:
            message = 'pake: fail: alien not found: {0}'.format(e)
        finally:
            if '--quiet' not in ui: print(message)
    if '--update' in ui:
        print('not impelemented')
    if '--list' in ui:
        for url in aliens:
            print(' * {0}'.format(url))
            if '--verbose' in ui:
                amirrors = aliens.get(url)['mirrors']
                for am in amirrors: print('   + {0}'.format(am))
elif str(ui) == 'nests':
    """Interface code for nest management.
    """
    nests = pake.config.node.Nests(root)
    if '--register' in ui:
        """Code used to register nests.
        Nest which is being registered must have a valid meta (containing name and version).
        """
        try:
            path = os.path.join(ui.get('--register'), '.pakenest')
            if path[0] == '~': path = os.path.abspath(os.path.expanduser(path))
            pake.node.packages.register(root, path)
            meta = pake.config.nest.Meta(path)
            if not os.path.isdir(path): raise pake.errors.PAKEError('nest not found in: {0}'.format(path))

            report = 'pake: registered nest'
            if '--verbose' in ui: report += ' for package: {0} (version: {1})'.format(meta.get('name'), meta.get('version'))
        except (pake.errors.PAKEError) as e:
            report = 'pake: fatal: {0}'.format(e)
        finally:
            print(report)
    if '--unregister' in ui:
        """Used to remove nest from the list of registered nests.
        """
        try:
            nests.remove(name=ui.get('--unregister')).write()
        except KeyError as e:
            print('pake: nest for package {0} was not registered'.format(e))
        finally:
            pass
    if '--list' in ui:
        """List all nests registered in this node.
        """
        for package in nests:
            meta = pake.config.nest.Meta(nests.get(package))
            report = '{0} {1} {2}'.format(meta['name'], meta['version'], nests.get(package))
            if '--verbose' in ui:
                report += ' (licensed under: {0})'.format(p['license'])
                if 'description' in p: report += ': {0}'.format(p['description'])
            print(report)
    if '--gen-pkg-list' in ui:
        """This is used to build list of packages that is served on your node.

        It reads data from all registered nests and forges a packages.json data file.
        """
        pake.node.packages.genpkglist(root)
        if '--quiet' not in ui: print('pake: generated packages.json list')
elif str(ui) == '':
    """Local options of top mode.
    """
    if '--gen-cache' in ui:
        print('IMPLEMENT ME!')
        print('pake: generated cache')
else:
    if '--debug' in ui: print('pake: fail: mode `{0}` is not implemented yet'.format(str(ui)))
