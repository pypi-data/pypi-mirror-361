#!/usr/bin/env python
#
# Copyright (c) 2003 Richard Jones (richard@mechanicalcat.net)
#
from __future__ import print_function

import errno
import getopt
import os
import shutil
import socket
import sys

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from roundup import configuration
from roundup.scripts import roundup_server

# Path where demo instance files will be stored
TRACKER_HOME = os.path.abspath('demo')


def install_demo(home, backend, template, use_port=None, use_host=None):
    """Install a demo tracker

    Parameters:
        home:
            tracker home directory path
        backend:
            database backend name
        template:
            tracker template

    """

    from roundup import init, instance, password

    # set up the config for this tracker
    template_dir = os.path.join('share', 'roundup', 'templates', template)

    # Load optional override ini file. Missing ini file is ignored.
    template_cfg = configuration.UserConfig(template_dir + "/config_ini.ini")
    config = configuration.CoreConfig(settings={
        i.name: i.get() for i in template_cfg.items()
    })
    config['TRACKER_HOME'] = home
    config['MAIL_DOMAIN'] = 'localhost'
    config['DATABASE'] = 'db'
    config['WEB_DEBUG'] = True
    if backend in ('mysql', 'postgresql'):
        config['RDBMS_HOST'] = 'localhost'
        config['RDBMS_USER'] = 'rounduptest'
        config['RDBMS_PASSWORD'] = 'rounduptest'
        config['RDBMS_NAME'] = 'rounduptest'

    config['RDBMS_BACKEND'] = backend

    # see if we need to clean up existing directory
    if os.path.exists(home):
        if os.path.exists(home + '/config.ini'):
            # clear everything out to avoid conflicts with former
            # extensions and detectors
            print("Nuking directory left from the previous demo instance.")
            shutil.rmtree(home)
        else:
            print("Error: Refusing to nuke non-tracker directory:")
            print("    %s" % home)
            sys.exit(1)

    init.install(home, template_dir)
    # Remove config_ini.ini file from tracker_home (not template dir).
    # Ignore file not found - not all templates have
    #   config_ini.ini files.
    try:
        os.remove(home + "/config_ini.ini")
    except OSError as e:  # FileNotFound exception under py3
        if e.errno == 2:
            pass
        else:
            raise

    # don't have email flying around
    nosyreaction = os.path.join(home, 'detectors', 'nosyreaction.py')
    if os.path.exists(nosyreaction):
        os.remove(nosyreaction)
    nosyreaction += 'c'
    if os.path.exists(nosyreaction):
        os.remove(nosyreaction)

    # figure basic params for server
    hostname = use_host or 'localhost'
    # pick a fairly odd, random port
    port = use_port or 8917
    while 1:
        print('Trying to set up web server on port %d ...' % port,)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.connect((hostname, port))
        except socket.error as e:
            if not hasattr(e, 'args') or e.args[0] != errno.ECONNREFUSED:
                raise
            print('should be ok.')
            break
        else:
            s.close()
            print('already in use.')
            port += 100
    config['TRACKER_WEB'] = 'http://%s:%s/demo/' % (hostname, port)

    # write the config
    config['INSTANT_REGISTRATION'] = 1
    config.save(os.path.join(home, config.INI_FILE))

    # open the tracker and initialise
    tracker = instance.open(home)
    tracker.init(password.Password('admin', config=config))

    # add the "demo" user
    db = tracker.open('admin')
    # FIXME: Move tracker-specific demo initialization into the tracker
    # templates.
    if os.path.basename(template) == 'minimal':
        db.user.create(username='demo',
                       password=password.Password('demo', config=db.config),
                       roles='User')
    else:
        db.user.create(username='demo',
                       password=password.Password('demo', config=db.config),
                       realname='Demo User', roles='User')
    db.commit()
    db.close()


def run_demo(home, bind_addr=None, bind_port=None):
    """Run the demo tracker instance from its ``home`` directory

       For running under docker, we need to split ports into
       the port roundup-server binds to (usually 8080) and the
       external mapping requested by docker to be used in external url's.
    """

    print("\nDemo Tracker Home:", home)

    cfg = configuration.CoreConfig(home)
    url = cfg["TRACKER_WEB"]
    try:
        hostname, port = urlparse.urlparse(url)[1].split(':')
    except ValueError:
        print("\nThe TRACKER_WEB url:\n\n  %(url)s\n\nin\n\n"
              "  %(home)s/config.ini"
              "\n\nis missing a port number.\n"
              "\nAre you using demo mode to start a production tracker? "
              "Try running\ndemo mode with a different directory. "
              "Use roundup-server to serve\nproduction trackers. "
              "Exiting.\n" % {'home': home, 'url': url})
        exit(1)

    bind_addr = bind_addr or hostname
    port = int(bind_port or port)
    success_message = '''Server running - connect to:\n
    %(url)s\n
1. Log in as "demo"/"demo" or "admin"/"admin".
2. Hit Control-C to stop the server.
3. Re-start the server by running "%(script)s" again.
4. Reset the tracker by running "%(script)s nuke".

By default the demo tracker is set up to be accessed from "localhost".
If you want to run it on a server,
edit "%(datadir)s/config.ini"
and set the "web" option in section "[tracker]" to your host name,
then restart demo. If you want to change backend types, you must use "nuke".

''' % dict(url=url, script=sys.argv[0], datadir=TRACKER_HOME)

    # disable command line processing in roundup_server
    sys.argv = sys.argv[:1] + ['-p', str(port), '-n', bind_addr, 'demo=' + home]
    roundup_server.run(success_message=success_message)


def usage(msg=''):
    if msg:
        print(msg)
    print("""\
Usage: %(script)s [options] [nuke]

 Run a demo server. Config and database files are created in
 %(datadir)s subdirectory of %(script)s dir.

 'nuke' will re-initialize the demo instance, deleting the old data.

 See docs/installation "For The Really Impatient" for more details.

Options:
 -h                -- print this help message
 -t template       -- specify the tracker template to use
 -b backend        -- specify the database backend to use
""" % dict(script=sys.argv[0], datadir=TRACKER_HOME+os.sep))


def main():
    """Run a demo server for users to play with for instant gratification.

    Sets up the web service on localhost. Disables nosy lists.
    """

    try:
        opts, args = getopt.getopt(sys.argv[1:], 't:b:h')
    except getopt.GetoptError as e:
        usage(str(e))
        return 1
    for opt, _arg in opts:
        if opt == '-h':
            usage()
            return 0

    home = os.path.abspath(TRACKER_HOME)
    nuke = args and args[0] == 'nuke'
    if not os.path.exists(home) or nuke:
        backend = 'anydbm'
        template = 'classic'
        for opt, arg in opts:
            if opt == '-t':
                template = arg
            elif opt == '-b':
                backend = arg
        if (len(args) > 1 or
            (len(args) == 1 and args[0] != 'nuke')):
            usage()
            return 1

        print("Initializing demo instance in:\n    %s" % home)
        install_demo(home, backend, template)
    elif opts:
        print("Error: Arguments are not allowed when running an existing demo.")
        print("       Use the 'nuke' command to start over.")
        sys.exit(1)

    run_demo(home)


if __name__ == '__main__':
    sys.exit(main())

# vim: set filetype=python sts=4 sw=4 et si :
