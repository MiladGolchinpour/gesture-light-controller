_SEGMENTS = [
    0x3f, 0x06, 0x5b, 0x4f,
    0x66, 0x6d, 0x7d, 0x07,
    0x7f, 0x6f
]

_TEXT = {
    "A": 0x77,
    "B": 0x7c,
    "C": 0x39,
    "D": 0x5e,
    "E": 0x79,
    "F": 0x71,
    "H": 0x76,
    "I": 0x06,
    "L": 0x38,
    "N": 0x54,
    "O": 0x3f,
    "P": 0x73,
    "R": 0x50,
    "T": 0x78,
    "U": 0x3e,
    "W": 0x3e,
    "Y": 0x6e,
    " ": 0x00
}

class TM1637:
    def __init__(self, clk, dio, brightness=7):
        self.clk = clk
        self.dio = dio
        self.brightness = brightness

        self.clk.init(self.clk.OUT)
        self.dio.init(self.dio.OUT)

    def _start(self):
        self.dio.value(1)
        self.clk.value(1)
        self.dio.value(0)

    def _stop(self):
        self.clk.value(0)
        self.dio.value(0)
        self.clk.value(1)
        self.dio.value(1)

    def _write_byte(self, data):
        for _ in range(8):
            self.clk.value(0)
            self.dio.value(data & 1)
            data >>= 1
            self.clk.value(1)

        self.clk.value(0)
        self.clk.value(1)


    def _write(self, data):
        self._start()
        self._write_byte(0x40)
        self._stop()

        self._start()
        self._write_byte(0xc0)

        for byte in data:
            self._write_byte(byte)

        self._stop()

        self._start()
        self._write_byte(0x88 | self.brightness)
        self._stop()

    def number(self, num):
        digits = [
            num // 1000 % 10,
            num // 100 % 10,
            num // 10 % 10,
            num % 10
        ]

        self._write([_SEGMENTS[d] for d in digits])

    def text(self, chars):
        data = [_TEXT.get(c.upper(), 0x00) for c in chars[:4]]
        data += [0] * (4 - len(data))
        self._write(data)