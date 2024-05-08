import string
import random
from random_username.generate import generate_username

LETTERS = string.ascii_letters
NUMBERS = string.digits


async def password_generator(length: int = 10):
    printable = f'{LETTERS}{NUMBERS}'

    printable = list(printable)
    random.shuffle(printable)

    random_password = random.choices(printable, k=length)
    random_password = ''.join(random_password)

    return random_password


async def generate_unique_username():
    return generate_username()[0]
