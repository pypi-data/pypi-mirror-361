class BinaryUtils:
    @staticmethod
    def dec2binary(a: int) -> str:
        if a == 0:
            return "0"
        res = ""
        while a > 0:
            res = str(a % 2) + res
            a //= 2
        return res

    @staticmethod
    def add_binary(a: str, b: str, precision: int) -> str:
        a = a[::-1]
        b = b[::-1]
        carry = 0
        res = ""

        for i in range(max(len(a), len(b))):
            digitA = int(a[i]) if i < len(a) else 0
            digitB = int(b[i]) if i < len(b) else 0
            total = digitA + digitB + carry
            res = str(total % 2) + res
            carry = total // 2

        if carry:
            res = "1" + res

        return res[-precision:]