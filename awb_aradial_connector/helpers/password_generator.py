from odoo import exceptions
import random
import string

class GeneratePassword(object):
    def generate_password(self):
        letters = string.ascii_letters+string.digits
        password = ''.join(random.sample(letters,8))

        return password