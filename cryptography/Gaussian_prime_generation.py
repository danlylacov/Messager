import random
import math


class GaussGenerator:

    def __init__(self):
        self.p = self.generate_prime(1024)
        self.q = self.generate_prime(1024)


    def is_prime(self, num, k=5):
        """Проверяет, является ли число вероятно простым."""
        if num < 2:
            return False
        if num < 4:
            return True
        if num % 2 == 0:
            return False

        # Представляем num - 1 как (2^r) * d
        r, d = 0, num - 1
        while d % 2 == 0:
            r += 1
            d //= 2

        # Проводим k тестов Миллера-Рабина
        for _ in range(k):
            a = random.randint(2, num - 2)
            x = pow(a, d, num)
            if x == 1 or x == num - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, num)
                if x == num - 1:
                    break
            else:
                return False
        return True


    def generate_prime(self, bits):
        """Генерирует простое число длиной bits бит."""
        while True:
            num = random.getrandbits(bits)
            # Устанавливаем самый значащий и мимимальный бит для удостоверения, что число имеет длину bits бит
            num |= (1 << (bits - 1)) | 1
            if self.is_prime(num):
                return num


