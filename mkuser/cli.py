import argparse
import glob
import os
import socket
import subprocess
import sys

import yaml

from mkuser import __version__
from mkuser.mail import send_welcome_mail
from mkuser.ssh import add_ssh_key, validate_sshkey
from mkuser.user import create_user, generate_password, get_username, set_user_password


def run_commandset(folder: str, username: str):
    """Run a set of executables in a folder."""
    if os.path.exists(folder) and os.path.isdir(folder):
        folder_path = os.path.join(os.path.abspath(folder), '*')
        for filename in glob.glob(folder_path):
            if os.path.isfile(filename) and os.access(filename, os.X_OK):
                subprocess.call([filename, username])


def error(message: str):
    """Write an error to STDERR and exit."""
    sys.stderr.write(message)
    sys.exit(1)


def create_argparser() -> argparse.ArgumentParser:
    """Build a ArgumentParser instance for use with the CLI."""
    parser = argparse.ArgumentParser('mkuser')
    parser.add_argument('username', help='Username of the new user')
    parser.add_argument('email', help="The user's email address")
    parser.add_argument('sshkey', help="The user's SSH public key")
    parser.add_argument('-c', '--config', help='Location of the configuration file to use', default='/etc/mkuser/mkuser.yaml')
    parser.add_argument('-v', '--version', action='version', version='mkuser {0}'.format(__version__))
    return parser


def load_config(config_file: str):
    if os.path.exists(config_file):
        with open(config_file, 'r') as fobj:
            try:
                return yaml.safe_load(fobj)
            except yaml.error.YAMLError:
                return None


def main():
    args = create_argparser().parse_args()

    if not sys.platform.startswith('linux'):
        error('mkuser only works on Linux systems')

    if os.getuid() != 0:
        error('mkuser requires root access')

    config = load_config(os.path.expandvars(args.config))
    if config is None:
        error('Configuration file {0} does not exist\n'.format(args.config))

    # Check tha the user doesn't exist
    if get_username(args.username):
        error('User {0} already exists\n'.format(args.username))

    res = validate_sshkey(args.sshkey)
    if res is not True:
        error('SSH key invalid: {0}\n'.format(res))

    # Run pre-creation commands
    run_commandset(config.get('pre_folder', '/etc/mkuser/pre.d'), args.username)

    # Create the user
    password = generate_password()
    user = create_user(args.username)
    if user is None:
        error("Failure occurred when trying to create user {0}, user isn't available in the passwd db".format(args.username))
    set_user_password(user.pw_name, password)

    # Add the SSH key
    if not add_ssh_key(user.pw_name, args.sshkey):
        error("Unable to add SSH key to user's authorized_keys")

    # Send the welcome mail
    template_filename = config.get('mail_template', '/etc/mkuser/mail.tmpl')

    # Use the config file as the basis of the template data
    template_values = config.copy()
    template_values.update({
        'username': user.pw_name,
        'password': password,
        'hostname': socket.getfqdn(),
    })
    for address in (args.email, user.pw_name):
        send_welcome_mail(address, template_filename, template_values)

    # Run post-creation commands
    run_commandset(config.get('post_folder', '/etc/mkuser/pre.d'), args.username)
