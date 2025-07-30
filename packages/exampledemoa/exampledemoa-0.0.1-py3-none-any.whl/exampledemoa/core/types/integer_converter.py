# Check byte, short, int with https://www.binaryconvert.com/result_signed_char.html?decimal=045050
from .binary_utils import BinaryUtils

class IntegerConverter:
    def __init__(self):
        self.utils = BinaryUtils()

    def _convert_signed(self, a: int, bits: int, min_val: int, max_val: int) -> tuple[str, str]:
        if not min_val <= a <= max_val:
            raise ValueError(f"Only [{min_val}; {max_val}] allowed")

        if a >= 0:
            res = self.utils.dec2binary(a).zfill(bits)
        else:
            binary_abs = self.utils.dec2binary(abs(a)).zfill(bits)
            flipped = ''.join('1' if bit == '0' else '0' for bit in binary_abs)
            res = self.utils.add_binary(flipped, "1".zfill(bits), bits)

        return res, self._format(res)

    def _convert_unsigned(self, a: int, bits: int, max_val: int) -> tuple[str, str]:
        if not 0 <= a <= max_val:
            raise ValueError(f"Only [0; {max_val}] allowed")

        res = self.utils.dec2binary(a).zfill(bits)
        return res, self._format(res)

    def _format(self, bin_str: str) -> str:
        return ' '.join(bin_str[i:i+8] for i in range(0, len(bin_str), 8))

    def to_byte(self, a: int) -> str:
        return self._convert_signed(a, 8, -128, 127)[0]

    def to_ubyte(self, a: int) -> str:
        return self._convert_unsigned(a, 8, 255)[0]

    def to_short(self, a: int) -> tuple[str, str]:
        return self._convert_signed(a, 16, -32768, 32767)

    def to_ushort(self, a: int) -> tuple[str, str]:
        return self._convert_unsigned(a, 16, 65535)

    def to_int(self, a: int) -> tuple[str, str]:
        return self._convert_signed(a, 32, -2**31, 2**31 - 1)

    def to_uint(self, a: int) -> tuple[str, str]:
        return self._convert_unsigned(a, 32, 2**32 - 1)
