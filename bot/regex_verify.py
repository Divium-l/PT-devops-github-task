import re

def verify_password(text) -> bool:
    passwordRegex = re.compile(r"(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*()]).{8,}$")
    result = passwordRegex.search(text)

    if (not result):
        return False
    else:
        return True