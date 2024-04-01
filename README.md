# mkuser

[![Liberapay logo](https://img.shields.io/liberapay/receives/dimension.sh.svg?logo=liberapay)](https://liberapay.com/dimension.sh/)

`mkuser` is a simple tool to allow for the easy creation of users on a tilde style server.

## Configuration

`mkuser` uses the OS defined configuration for the `useradd` command. On a Redhat derived system this will be in `/etc/login.defs`. No configuration for the user is held by any `mkuser` file.

The email template must be located at `/etc/mkuser/mail.tmpl` and it uses Python's string Template format. Further details on the syntax can be found within the [Python documentation](https://docs.python.org/3/library/string.html#template-strings).

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

## Pre/Post Run Commands

Executable files located in `/etc/mkuser/pre.d` or `/etc/mkuser/post.d` will be executed after the user has been created, they will be called with the username of the newly created (or to be created) user.