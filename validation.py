import re


class Validator:
    def __init__(self, username: str, email: str, password :str):
        self.username = self._is_valid_username(username)
        self.email = self._is_valid_email(email)
        self.password = self._is_valid_password(password)

    def _is_valid_username(self, username):
        regex = "^[A-Za-z]\\w{4,14}$"
        r = re.compile(regex)
        if re.search(r, username):
            return username
        return ValueError("Invalid username.")

    def _is_valid_email(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.fullmatch(regex, email):
            raise ValueError("It's not an email address.")
        return email

    def _is_valid_password(self, password):
        length = len(password)
        if length < 6:
            raise ValueError("Minimum password length is 6 characters.")
        elif length > 20:
            raise ValueError("Maximum password length is 20 characters.")
        return password
    