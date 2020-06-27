#!/usr/bin/env python3

import sys
import os
import base64
import binascii
import struct
import argparse
import pwd
import subprocess
import secrets
import string
import pathlib
import socket


def validate_sshkey(keystring):
    """ Validates that SSH pubkey string is valid """
    # do we have 3 fields?
    fields = len(keystring.split(' '))
    if fields < 2 or fields > 3:
        return 'Incorrect number of fields (%d)' % fields

    if fields == 2:
        keytype, pubkey = keystring.split(' ')
    if fields == 3:
        keytype, pubkey, _ = keystring.split(' ')

    # Check it is a valid type
    if not keytype in ['ssh-rsa', 'ssh-ed25519']:
        return 'Invalid keytype'

    # Decode the key data from Base64
    try:
        data = base64.decodebytes(pubkey.encode())
    except binascii.Error:
        return 'Error decoding the pubkey'

    # Get the length from the data
    try:
        str_len = struct.unpack('>I', data[:4])[0]
    except struct.error:
        return 'Error aquiring key length'

    # Keytype is encoded and must match
    if not data[4:4+str_len].decode('ascii') == keytype:
        return 'Embedded keytype does not match declared keytype (%s vs %s)' % (data[4:4+str_len].decode('ascii'), keytype)

    return True


def get_username(username):
    """ Retreives the user from passwd """
    try:
        return pwd.getpwnam(username)
    except KeyError:
        return None


def create_user(username):
    """ Create a user, using 'useradd', then check the results """
    subprocess.run(['useradd', username])
    return get_username(username)


def generate_password(length=8):
    """ Generates a random password """
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(length))


def set_user_password(username, password):
    """ Sets a user's password """
    proc = subprocess.Popen(['chpasswd'], stdin=subprocess.PIPE)
    proc.communicate(("%s:%s\n" % (username, password)).encode("utf-8"))


def add_ssh_key(username, sshkey):
    """ Adds the provided SSH key to the user's authorized_keys file """
    user = get_username(username)
    ssh_folder = os.path.join(user.pw_dir, '.ssh')
    key_file = os.path.join(ssh_folder, 'authorized_keys')
    try:
        os.mkdir(ssh_folder)
    except FileExistsError:
        pass
    os.chmod(ssh_folder, 0o700)
    os.chown(ssh_folder, user.pw_uid, user.pw_gid)
    with open(key_file, 'a') as fobj:
        fobj.write(sshkey + '\n')
    os.chown(key_file, user.pw_uid, user.pw_gid)
    os.chmod(key_file, 0o600)


def send_welcome_mail(address, mail_data):
    """ Emails out a welcome email to the user """
    import smtplib
    from email.message import EmailMessage
    from string import Template

    msg = EmailMessage()

    with open('/etc/mkuser/welcome_mail.tmpl') as fobj:
        content = Template(fobj.read())
    msg.set_content(content.safe_substitute(**mail_data))

    msg['From'] = 'root'
    msg['To'] = address
    msg['Subject'] = 'Welcome to dimension.sh'

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help='Username of the new user')
    parser.add_argument('email', help='Email address to send the welcome mail to')
    parser.add_argument('sshkey', help='SSH public key')

    args = parser.parse_args()

    # Check tha the user doesn't exist
    if get_username(args.username):
        sys.stderr.write('User %s already exists\n' % args.username)
        sys.exit(1)

    if args.sshkey.strip() == '':
        sys.stderr.write('SSH key is blank')
        sys.exit(1)

    res = validate_sshkey(args.sshkey)
    if res != True:
        sys.stderr.write('SSH key invalid: %s' % res)
        sys.exit(1)

    # Create the user
    password = generate_password()
    user = create_user(args.username)
    set_user_password(user.pw_name, password)

    # Add the SSH key
    add_ssh_key(user.pw_name, args.sshkey)

    # Send the welcome mail
    for address in (args.email, user.pw_name):
        send_welcome_mail(address, {
            'username': user.pw_name,
            'password': password,
            'hostname': socket.getfqdn(),
        })

if __name__ == '__main__':
    main()