import base64
import binascii
import os
import struct

from mkuser.user import get_username

# Permissions used for creating SSH related user files
SSH_FOLDER_PERMS = 0o700
SSH_FILE_PERMS = 0o600

VALID_SSH_KEYTYPES = (
    'sk-ecdsa-sha2-nistp256@openssh.com',
    'ecdsa-sha2-nistp256',
    'ecdsa-sha2-nistp384',
    'ecdsa-sha2-nistp521',
    'sk-ssh-ed25519@openssh.com',
    'ssh-ed25519',
    'ssh-rsa',
)


def validate_sshkey(keystring: str):
    """
    Validate that SSH pubkey string is valid.
    
    This function does some basic validation that the provided SSH public key
    string is correct and valid:

    * The key type is valid for OpenSSH
    * It can be correctly decoded
    * The public key length is valid and correct
    * The key type in the decoded key represents the type defined in the key string 
    """
    # do we have 3 fields?
    fields = keystring.split(' ')
    if len(fields) < 2:
        return 'Incorrect number of fields provided ({0})'.format(fields)
    else:
        keytype = fields[0]
        pubkey = fields[1]

    # Check it is a valid type
    if keytype not in VALID_SSH_KEYTYPES:
        return 'Key has an invalid key type'

    # Decode the key data from Base64
    try:
        decoded_key = base64.decodebytes(pubkey.encode())
    except binascii.Error:
        return 'Error decoding the SSH public key'

    # Get the length from the data
    try:
        str_len = struct.unpack('>I', decoded_key[:4])[0]
    except struct.error:
        return 'Error acquiring the public key length'

    # Keytype is encoded and must match
    if decoded_key[4:4 + str_len].decode('ascii') != keytype:
        return 'Embedded keytype does not match declared key type ({0} vs {1})'.format(
            decoded_key[4: 4 + str_len].decode('ascii'),
            keytype,
        )
    return True


def add_ssh_key(username: str, sshkey: str) -> bool:
    """Add the provided SSH key string to the user's authorized_keys file."""
    user = get_username(username)
    if not user:
        return False
    ssh_folder = os.path.join(user.pw_dir, '.ssh')
    key_file = os.path.join(ssh_folder, 'authorized_keys')
    try:
        os.mkdir(ssh_folder)
    except FileExistsError:
        pass  # noqa: WPS420
    os.chmod(ssh_folder, SSH_FOLDER_PERMS)
    os.chown(ssh_folder, user.pw_uid, user.pw_gid)
    with open(key_file, 'a') as fobj:
        fobj.write('{0}\n'.format(sshkey))
    os.chown(key_file, user.pw_uid, user.pw_gid)
    os.chmod(key_file, SSH_FILE_PERMS)
    return True
