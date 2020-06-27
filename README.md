# mkuser

`mkuser` is a simple tool to allow for the easy creation of users on a tilde style server.

## Configuration

`mkuser` uses the OS defined configuration for the `useradd` command. On a Redhat derrived system this will be in `/etc/login.defs`. No configuration for the user is held by any `mkuser` file.

The email template must be located at `/etc/mkuser/welcome_email.tmpl` and it uses Python's string Template format. Further details on the synax can be found within the [Python documentation](https://docs.python.org/3/library/string.html#template-strings).

## Usage

```
usage: mkuser [-h] username email sshkey

positional arguments:
  username    Username of the new user
  email       Email address to send the welcome mail to
  sshkey      SSH public key

optional arguments:
  -h, --help  show this help message and exit
  ```