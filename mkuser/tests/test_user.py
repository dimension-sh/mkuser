import string
from mkuser.user import generate_password


def test_generate_password():
    for x in range(1, 20):
        # Check the length is as expected
        passwd = generate_password(length=x)
        assert len(passwd) == x

        # Check the passwords use the correct character sets
        for letter in passwd:
            assert letter in string.ascii_letters + string.digits
