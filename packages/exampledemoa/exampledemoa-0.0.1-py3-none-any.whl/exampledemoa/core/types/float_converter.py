# Test with https://evanw.github.io/float-toy/
# Check fp32 with https://www.h-schmidt.net/FloatConverter/IEEE754.html
import math

class FloatConverter:
    def to_fp16(self, num: float) -> str:
        return self._convert(num, exp_bits=5, mantissa_bits=10, bias=15)

    def to_fp32(self, num: float) -> str:
        return self._convert(num, exp_bits=8, mantissa_bits=23, bias=127)

    def to_fp64(self, num: float) -> str:
        return self._convert(num, exp_bits=11, mantissa_bits=52, bias=1023)

    def _convert(self, num: float, exp_bits: int, mantissa_bits: int, bias: int) -> str:
        sign_bit = '0' if math.copysign(1.0, num) > 0 else '1'
        num = abs(num)

        # Special cases
        if math.isnan(num):
            return f"{sign_bit} {'1'*exp_bits} {'1' + '0'*(mantissa_bits-1)}"  # Quiet NaN
        if math.isinf(num):
            return f"{sign_bit} {'1'*exp_bits} {'0'*mantissa_bits}"
        if num == 0.0:
            return f"{sign_bit} {'0'*exp_bits} {'0'*mantissa_bits}"

        # Integer and fractional parts
        int_part = int(num)
        frac_part = num - int_part
        int_bin = bin(int_part)[2:] if int_part else '0'

        # Convert fractional part to binary
        frac_bin = ''
        while frac_part and len(frac_bin) < mantissa_bits + 10:
            frac_part *= 2
            bit = int(frac_part)
            frac_bin += str(bit)
            frac_part -= bit

        # Normalize and extract exponent/mantissa
        if int_part != 0:
            exponent = len(int_bin) - 1
            mantissa = int_bin[1:] + frac_bin
        else:
            first_one = frac_bin.find('1')
            if first_one == -1:
                return f"{sign_bit} {'0'*exp_bits} {'0'*mantissa_bits}"
            exponent = -(first_one + 1)
            mantissa = frac_bin[first_one + 1:]

        biased_exp = exponent + bias

        # Subnormal
        if biased_exp <= 0:
            return f"{sign_bit} {'0'*exp_bits} {'0'*mantissa_bits}"

        # Overflow
        if biased_exp >= 2**exp_bits - 1:
            return f"{sign_bit} {'1'*exp_bits} {'0'*mantissa_bits}"

        # Format final values
        exp_bin = bin(biased_exp)[2:].zfill(exp_bits)
        mantissa = mantissa[:mantissa_bits].ljust(mantissa_bits, '0')

        return f"{sign_bit} {exp_bin} {mantissa}"
