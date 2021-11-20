import os
import pwd
import secrets
import shutil
import string
import subprocess


def get_username(username: str) -> pwd.struct_passwd:
    """Retrieve the user from passwd."""
    try:
        return pwd.getpwnam(username)
    except KeyError:
        return None


def create_user(username: str) -> pwd.struct_passwd:
    """Create a user, using 'useradd', then check the results."""
    subprocess.run(['useradd', username])
    user = get_username(username)

    # if /etc/skel is a git repo, catch and delete the .git files
    if user:
        git_folder = os.path.join(user.pw_dir, '.git')
        if os.path.exists(git_folder):
            shutil.rmtree(git_folder)

    return user


def generate_password(length: int = 8) -> str:
    """Securely generate a random password."""
    password_characters = []
    for _ in range(length):
        password_characters.append(secrets.choice(string.ascii_letters + string.digits))
    return ''.join(password_characters)


def set_user_password(username: str, password: str):
    """Set a user's password."""
    process = subprocess.Popen(['chpasswd'], stdin=subprocess.PIPE)
    process.communicate(('{0}:{1}\n'.format(username, password)).encode('utf-8'))
