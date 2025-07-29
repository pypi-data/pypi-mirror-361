""" Unit tests for checksum module.

  License::

    MIT License

    Copyright (c) 2015-2022 by Martin Scharrer <martin.scharrer@web.de>

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software
    and associated documentation files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or
    substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
    BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
import random
import sys

import crccheck
from crccheck.base import CrccheckError
from crccheck.crc import ALLCRCCLASSES, ALLCRCCLASSES_ALIASES, \
    Crc32, Crc, crccls, find, identify, \
    Crc8Base, Crc16Base, Crc32Base
from tests import TestCase

TESTCRCCLASSES = list(ALLCRCCLASSES) + [Crc8Base, Crc16Base, Crc32Base]


class TestCrc(TestCase):

    def test_allcrc(self):
        """Test if expected 'check' result is calulated with standard test vector."""
        for crcclass in TESTCRCCLASSES:
            with self.subTest(crcclass=crcclass):
                crcclass.selftest()

    def test_allcrcfail(self):
        """Test if 'check' result is not reached with different input."""
        for crcclass in TESTCRCCLASSES:
            with self.subTest(crcclass=crcclass), self.assertRaises(CrccheckError):
                crcclass.selftest(bytearray(b"wrongtestinput"), crcclass._check_result)

    def test_generator(self):
        Crc32.calc((n for n in range(0, 255)))

    def test_list1(self):
        Crc32.calc([n for n in range(0, 255)])

    def test_list2(self):
        Crc32.calc([n for n in range(0, 255)], 123)

    def test_bytearray(self):
        Crc32.calc(bytearray.fromhex("12345678909876543210"))

    def test_bytes(self):
        if sys.version_info < (3, 3, 0):  # pragma: no cover
            raise self.skipTest("")
        Crc32.calc(bytes.fromhex("12345678909876543210"))

    def test_string1(self):
        if sys.version_info < (3, 3, 0):  # pragma: no cover
            raise self.skipTest("")
        Crc32.calc(b"Teststring")

    def test_string2(self):
        if sys.version_info < (3, 3, 0):  # pragma: no cover
            raise self.skipTest("")
        Crc32.calc("Teststring".encode(), )

    def test_general_crc(self):
        crc = Crc(32, 0x4C11DB7, 0xFFFFFFFF, True, True, 0x00000000, 0x340BC6D9)
        crc.selftest()

    def test_general_crc_fail(self):
        with self.assertRaises(CrccheckError):
            crc = Crc(32, 0x4C11DB7, 0xFFFFFFFF, True, True, 0x00000000, ~0x340BC6D9)
            crc.selftest()

    def test_general_crccls(self):
        crc = crccls(32, 0x4C11DB7, 0xFFFFFFFF, True, True, 0x00000000, 0x340BC6D9)
        crc.selftest()

    def test_general_crccls_fail(self):
        with self.assertRaises(CrccheckError):
            crc = crccls(32, 0x4C11DB7, 0xFFFFFFFF, True, True, 0x00000000, ~0x340BC6D9)
            crc.selftest()

    def test_backwards_compatible(self):
        """Crc8Base was called Crc8, etc. Must still be equal CRCs"""
        self.assertEqual(crccheck.crc.Crc8(), crccheck.crc.Crc8Base())
        self.assertEqual(crccheck.crc.Crc16(), crccheck.crc.Crc16Base())
        self.assertEqual(crccheck.crc.Crc32(), crccheck.crc.Crc32Base())

    def test_find32(self):
        for cls in find(width=32):
            self.assertEqual(cls._width, 32)

    def test_find_unknown(self):
        self.assertEqual(len(find(width=12345)), 0)

    def test_find_all(self):
        self.assertEqual(find(), list(ALLCRCCLASSES))

    def test_find_some(self):
        self.assertListEqual(find(ALLCRCCLASSES[1:3]), list(ALLCRCCLASSES[1:3]))

    def test_find_width(self):
        self.assertListEqual(find(width=32), list(cls for cls in ALLCRCCLASSES if cls._width == 32))

    def test_find_poly(self):
        self.assertListEqual(find(poly=0x04C11DB7), list(cls for cls in ALLCRCCLASSES if cls._poly == 0x04C11DB7))

    def test_find_initvalue(self):
        self.assertListEqual(find(initvalue=0), list(cls for cls in ALLCRCCLASSES if cls._initvalue == 0))

    def test_find_reflect_input(self):
        self.assertListEqual(find(reflect_input=True), list(cls for cls in ALLCRCCLASSES if cls._reflect_input))

    def test_find_reflect_output(self):
        self.assertListEqual(find(reflect_output=False), list(cls for cls in ALLCRCCLASSES if not cls._reflect_output))

    def test_find_xor_output(self):
        self.assertListEqual(find(xor_output=0), list(cls for cls in ALLCRCCLASSES if cls._xor_output == 0))

    def test_find_check_result(self):
        self.assertListEqual(find(check_result=6), list(cls for cls in ALLCRCCLASSES if cls._check_result == 6))

    def test_find_residue(self):
        self.assertListEqual(find(residue=0), list(cls for cls in ALLCRCCLASSES if cls._residue == 0))

    def test_find_mixed(self):
        self.assertListEqual(
            find(ALLCRCCLASSES[0:20], width=8, residue=0, reflect_input=False, reflect_output=False),
            list(cls for cls in ALLCRCCLASSES[0:20]
                 if cls._width == 8 and cls._residue == 0 and not cls._reflect_input and not cls._reflect_output))

    def test_identify_1(self):
        data = bytes(random.randrange(256) for _ in range(10))
        cls = crccheck.crc.Crc64GoIso
        self.assertEqual(identify(data, cls.calc(data))(), cls())

    def test_identify_2(self):
        data = bytes(random.randrange(256) for _ in range(10))
        classes = [crccheck.crc.Crc64GoIso, crccheck.crc.Crc8, crccheck.crc.Crc32IsoHdlc]
        cls = crccheck.crc.Crc32IsoHdlc
        self.assertEqual(identify(data, cls.calc(data), classes=classes)(), cls())

    def test_identify_width(self):
        data = bytes(random.randrange(256) for _ in range(10))
        allcrc32 = [c for c in ALLCRCCLASSES if c._width == 32]
        cls = random.choice(allcrc32)
        self.assertEqual(identify(data, cls.calc(data), 32)(), cls())
        self.assertEqual(identify(data, cls.calc(data), 32, allcrc32)(), cls())

    def test_identify_width_list(self):
        data = bytes(random.randrange(256) for _ in range(10))
        allcrc32 = [c for c in ALLCRCCLASSES if c._width == 32]
        cls = random.choice(allcrc32)
        result = identify(data, cls.calc(data), 32, one=False)
        self.assertEqual(len(result) >= 1 and result[0](), cls())
        result = identify(data, cls.calc(data), 32, allcrc32, one=False)
        self.assertEqual(len(result) >= 1 and result[0](), cls())

    def test_identify_notexisting(self):
        self.assertIsNone(identify(b'Test', 0))
        self.assertIsNone(identify(b'Test', 0, 234))
        self.assertIsNone(identify(b'Test', 0, classes=[]))
        self.assertIsNone(identify(b'Test', 0, 235, classes=[]))
        self.assertListEqual(identify(b'Test', 0, one=False), [])
        self.assertListEqual(identify(b'Test', 0, 234, one=False), [])
        self.assertListEqual(identify(b'Test', 0, classes=[], one=False), [])
        self.assertListEqual(identify(b'Test', 0, 235, classes=[], one=False), [])

    def test_repr(self):
        """Test if __repr__ does not cause errors"""
        c = Crc(16, 0xDEAD, initvalue=0x00, reflect_input=False, reflect_output=False,
                xor_output=0x00, check_result=None, residue=None)
        # noinspection PyUnusedLocal
        r = repr(c)
        c = Crc(16, 0xDEAD, initvalue=0x00, reflect_input=False, reflect_output=False,
                xor_output=0x00, check_result=None, residue=0x00)
        # noinspection PyUnusedLocal
        r = repr(c)
        c = Crc(16, 0xDEAD, initvalue=0x00, reflect_input=False, reflect_output=False,
                xor_output=0x00, check_result=0x00, residue=None)
        # noinspection PyUnusedLocal
        r = repr(c)
        c = Crc(16, 0xDEAD, initvalue=0x00, reflect_input=False, reflect_output=False,
                xor_output=0x00, check_result=0x00, residue=0x00)
        # noinspection PyUnusedLocal
        r = repr(c)

    def test_selftest_data(self):
        c = Crc(21, 0xDEAD)
        c.selftest(b'Test', 0x40be8)

    def test_crc_calc(self):
        self.assertEqual(Crc(21, 0xDEAD).calc(b'Test'), 265192)

    def test_crc_calchex(self):
        self.assertEqual(Crc(21, 0xDEAD).calchex(b'Test'), '040be8')

    def test_crc_calcbytes_big(self):
        self.assertEqual(Crc(21, 0xDEAD).calcbytes(b'Test', byteorder='big'), b'\x04\x0b\xe8')

    def test_crc_calcbytes_little(self):
        self.assertEqual(Crc(21, 0xDEAD).calcbytes(b'Test', byteorder='little'), b'\xe8\x0b\x04')

    def test_aliases(self):
        self.assertTrue(set(ALLCRCCLASSES).issubset(ALLCRCCLASSES_ALIASES))

    def test_getter(self):
        """Test if all getter return the underlying value correctly."""
        for cls in ALLCRCCLASSES:
            for attr in ("poly", "reflect_input", "reflect_output", "xor_output", "residue"):
                for clsorinst in (cls, cls()):
                    with self.subTest(clsorinst=clsorinst, attr=attr):
                        # x.foo() should return x._foo
                        self.assertEqual(getattr(clsorinst, attr)(), getattr(clsorinst, "_" + attr))
