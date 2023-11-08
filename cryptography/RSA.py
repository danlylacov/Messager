import math
import random
from .Gaussian_prime_generation import GaussGenerator

class RSA(GaussGenerator):

    def euler_function(self, a, b):
        return (a - 1)*(b - 1)

    def find_coprime(self, n):
        """Находит взаимно простое число с n."""

        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        coprime = n
        while gcd(n, coprime) != 1:
            coprime -= random.randint(1, 100)
        return coprime


    def extended_gcd(self, a, b):
        """Расширенный алгоритм Евклида для нахождения НОД и коэффициентов x, y."""
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = self.extended_gcd(b % a, a)
            return (g, x - (b // a) * y, y)

    def find_mod_inverse(self, e, phi):
        """
                    Нахождение мультипликативной инверсии (обратного элемента) для e по модулю phi.
                    Решает уравнение d * e ≡ 1 (mod phi).
                    """
        g, x, y = self.extended_gcd(e, phi)
        if g != 1:
            raise Exception('Обратный элемент не существует')
        else:
            return x % phi

    def create_keys(self):
        p, q = self.p, self.q
        n = p * q
        f = self.euler_function(p, q)
        e = self.find_coprime(f)
        public_key = [e, n]

        d = self.find_mod_inverse(e, f)  # Находим секретный экспонент d
        private_key = [d, n]

        return [public_key, private_key]


    def message_to_num(self, message: str):
        decoded_message = []
        for i in range(len(message)):
            decoded_message.append(ord(message[i]))
        return decoded_message

    def num_to_message(self, nums: list):
        encoded_message = ''
        for i in range(len(nums)):
            encoded_message += chr(nums[i])
        return encoded_message

    def fast_exponentiation(self, base, exponent, mod):
        result = 1
        while exponent > 0:
            if exponent % 2 == 1:
                result = (result * base) % mod
            base = (base * base) % mod
            exponent //= 2
        return result


    def encrypt(self, message: str, public_key):
        message = self.message_to_num(message)
        for i in range(len(message)):
            message[i] = self.fast_exponentiation(message[i], public_key[0], public_key[1])
        return message


    def decrypt(self, message: list, private_key):
        for i in range(len(message)):
            message[i] = self.fast_exponentiation(message[i], private_key[0], private_key[1])

        return self.num_to_message(message)



rsa = RSA()
keys = rsa.create_keys()
mes = rsa.encrypt('f', keys[0])
print(rsa.decrypt(mes, keys[1]))


