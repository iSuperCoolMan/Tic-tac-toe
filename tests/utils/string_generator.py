import random
import string


chars = string.ascii_uppercase + string.digits


def random_string(length: int) -> str:
    return ''.join(random.choice(chars) for _ in range(length))