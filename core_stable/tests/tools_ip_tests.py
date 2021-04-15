#!/usr/bin/python
"""Test IP module/regex."""
#
# (C) Pywikibot team, 2012-2021
#
# Distributed under the terms of the MIT license.
import unittest

from contextlib import suppress

from pywikibot.tools import is_IP, PYTHON_VERSION

from tests import unittest_print

from tests.aspects import TestCase
from tests.utils import expected_failure_if


class IPAddressModuleTestCase(TestCase):

    """Unit test class base for IP matching."""

    net = False

    ip6 = [
        # test from http://download.dartware.com/thirdparty/test-ipv6-regex.pl
        (False, ''),  # empty string
        (True, '::1'),  # loopback, compressed, non-routable
        (True, '::'),  # unspecified, compressed, non-routable
        (True, '0:0:0:0:0:0:0:1'),  # loopback, full
        (True, '0:0:0:0:0:0:0:0'),  # unspecified, full
        (True, '2001:DB8:0:0:8:800:200C:417A'),  # unicast, full
        (True, 'FF01:0:0:0:0:0:0:101'),  # multicast, full
        # unicast, compressed
        (True, '2001:DB8::8:800:200C:417A'),
        (True, 'FF01::101'),  # multicast, compressed
        # unicast, full
        (False, '2001:DB8:0:0:8:800:200C:417A:221'),
        (False, 'FF01::101::2'),  # multicast, compressed
        (True, 'fe80::217:f2ff:fe07:ed62'),

        (True, '2001:0000:1234:0000:0000:C1C0:ABCD:0876'),
        (True, '3ffe:0b00:0000:0000:0001:0000:0000:000a'),
        (True, 'FF02:0000:0000:0000:0000:0000:0000:0001'),
        (True, '0000:0000:0000:0000:0000:0000:0000:0001'),
        (True, '0000:0000:0000:0000:0000:0000:0000:0000'),
        # leading space
        (False, ' 2001:0000:1234:0000:0000:C1C0:ABCD:0876'),
        # trailing space
        (False, '2001:0000:1234:0000:0000:C1C0:ABCD:0876 '),
        # leading and trailing space
        (False, ' 2001:0000:1234:0000:0000:C1C0:ABCD:0876 '),
        # junk after valid address
        (False, '2001:0000:1234:0000:0000:C1C0:ABCD:0876  0'),
        # internal space
        (False, '2001:0000:1234: 0000:0000:C1C0:ABCD:0876'),

        # seven segments
        (False, '3ffe:0b00:0000:0001:0000:0000:000a'),
        # nine segments
        (False, 'FF02:0000:0000:0000:0000:0000:0000:0000:0001'),
        (False, '3ffe:b00::1::a'),  # double '::'
        # double "::"
        (False, '::1111:2222:3333:4444:5555:6666::'),
        (True, '2::10'),
        (True, 'ff02::1'),
        (True, 'fe80::'),
        (True, '2002::'),
        (True, '2001:db8::'),
        (True, '2001:0db8:1234::'),
        (True, '::ffff:0:0'),
        (True, '::1'),
        (True, '1:2:3:4:5:6:7:8'),
        (True, '1:2:3:4:5:6::8'),
        (True, '1:2:3:4:5::8'),
        (True, '1:2:3:4::8'),
        (True, '1:2:3::8'),
        (True, '1:2::8'),
        (True, '1::8'),
        (True, '1::2:3:4:5:6:7'),
        (True, '1::2:3:4:5:6'),
        (True, '1::2:3:4:5'),
        (True, '1::2:3:4'),
        (True, '1::2:3'),
        (True, '1::8'),
        (True, '::2:3:4:5:6:7:8'),
        (True, '::2:3:4:5:6:7'),
        (True, '::2:3:4:5:6'),
        (True, '::2:3:4:5'),
        (True, '::2:3:4'),
        (True, '::2:3'),
        (True, '::8'),
        (True, '1:2:3:4:5:6::'),
        (True, '1:2:3:4:5::'),
        (True, '1:2:3:4::'),
        (True, '1:2:3::'),
        (True, '1:2::'),
        (True, '1::'),
        (True, '1:2:3:4:5::7:8'),
        (False, '1:2:3::4:5::7:8'),  # Double "::"
        (False, '12345::6:7:8'),
        (True, '1:2:3:4::7:8'),
        (True, '1:2:3::7:8'),
        (True, '1:2::7:8'),
        (True, '1::7:8'),

        # IPv4 addresses as dotted-quads
        (True, '1:2:3:4:5:6:1.2.3.4'),
        (True, '1:2:3:4:5::1.2.3.4'),
        (True, '1:2:3:4::1.2.3.4'),
        (True, '1:2:3::1.2.3.4'),
        (True, '1:2::1.2.3.4'),
        (True, '1::1.2.3.4'),
        (True, '1:2:3:4::5:1.2.3.4'),
        (True, '1:2:3::5:1.2.3.4'),
        (True, '1:2::5:1.2.3.4'),
        (True, '1::5:1.2.3.4'),
        (True, '1::5:11.22.33.44'),
        (False, '1::5:400.2.3.4'),
        (False, '1::5:260.2.3.4'),
        (False, '1::5:256.2.3.4'),
        (False, '1::5:1.256.3.4'),
        (False, '1::5:1.2.256.4'),
        (False, '1::5:1.2.3.256'),
        (False, '1::5:300.2.3.4'),
        (False, '1::5:1.300.3.4'),
        (False, '1::5:1.2.300.4'),
        (False, '1::5:1.2.3.300'),
        (False, '1::5:900.2.3.4'),
        (False, '1::5:1.900.3.4'),
        (False, '1::5:1.2.900.4'),
        (False, '1::5:1.2.3.900'),
        (False, '1::5:300.300.300.300'),
        (False, '1::5:3000.30.30.30'),
        (False, '1::400.2.3.4'),
        (False, '1::260.2.3.4'),
        (False, '1::256.2.3.4'),
        (False, '1::1.256.3.4'),
        (False, '1::1.2.256.4'),
        (False, '1::1.2.3.256'),
        (False, '1::300.2.3.4'),
        (False, '1::1.300.3.4'),
        (False, '1::1.2.300.4'),
        (False, '1::1.2.3.300'),
        (False, '1::900.2.3.4'),
        (False, '1::1.900.3.4'),
        (False, '1::1.2.900.4'),
        (False, '1::1.2.3.900'),
        (False, '1::300.300.300.300'),
        (False, '1::3000.30.30.30'),
        (False, '::400.2.3.4'),
        (False, '::260.2.3.4'),
        (False, '::256.2.3.4'),
        (False, '::1.256.3.4'),
        (False, '::1.2.256.4'),
        (False, '::1.2.3.256'),
        (False, '::300.2.3.4'),
        (False, '::1.300.3.4'),
        (False, '::1.2.300.4'),
        (False, '::1.2.3.300'),
        (False, '::900.2.3.4'),
        (False, '::1.900.3.4'),
        (False, '::1.2.900.4'),
        (False, '::1.2.3.900'),
        (False, '::300.300.300.300'),
        (False, '::3000.30.30.30'),
        (True, 'fe80::217:f2ff:254.7.237.98'),
        (True, '::ffff:192.168.1.26'),
        # garbage instead of "." in IPv4
        (False, '2001:1:1:1:1:1:255Z255X255Y255'),
        (False, '::ffff:192x168.1.26'),  # ditto
        (True, '::ffff:192.168.1.1'),
        # IPv4-compatible IPv6 address, full, deprecated
        (True, '0:0:0:0:0:0:13.1.68.3'),
        # IPv4-mapped IPv6 address, full
        (True, '0:0:0:0:0:FFFF:129.144.52.38'),
        # IPv4-compatible IPv6 address, compressed, deprecated
        (True, '::13.1.68.3'),
        # IPv4-mapped IPv6 address, compressed
        (True, '::FFFF:129.144.52.38'),
        (True, 'fe80:0:0:0:204:61ff:254.157.241.86'),
        (True, 'fe80::204:61ff:254.157.241.86'),
        (True, '::ffff:12.34.56.78'),
        (False, '::ffff:2.3.4'),
        (False, '::ffff:257.1.2.3'),

        (False, '1.2.3.4:1111:2222:3333:4444::5555'),  # Aeron
        (False, '1.2.3.4:1111:2222:3333::5555'),
        (False, '1.2.3.4:1111:2222::5555'),
        (False, '1.2.3.4:1111::5555'),
        (False, '1.2.3.4::5555'),
        (False, '1.2.3.4::'),

        # Testing IPv4 addresses represented as dotted-quads
        (True, '::ffff:192.0.2.128'),
        (False, 'XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:1.2.3.4'),
        (False, '1111:2222:3333:4444:5555:6666:256.256.256.256'),

        # Subnet mask not accepted

        # full, with prefix
        (False, '2001:0DB8:0000:CD30:0000:0000:0000:0000/60'),
        # compressed, with prefix
        (False, '2001:0DB8::CD30:0:0:0:0/60'),
        # compressed, with prefix #2
        (False, '2001:0DB8:0:CD30::/60'),
        # compressed, unspecified address type, non-routable
        (False, '::/128'),
        # compressed, loopback address type, non-routable
        (False, '::1/128'),
        # compressed, multicast address type
        (False, 'FF00::/8'),
        # compressed, link-local unicast, non-routable
        (False, 'FE80::/10'),
        # compressed, site-local unicast, deprecated
        (False, 'FEC0::/10'),
        # standard IPv4, prefix not allowed
        (False, '124.15.6.89/60'),

        (True, 'fe80:0000:0000:0000:0204:61ff:fe9d:f156'),
        (True, 'fe80:0:0:0:204:61ff:fe9d:f156'),
        (True, 'fe80::204:61ff:fe9d:f156'),
        (True, '::1'),
        (True, 'fe80::'),
        (True, 'fe80::1'),
        (False, ':'),
        (True, '::ffff:c000:280'),

        # Aeron supplied these test cases
        (False, '1111:2222:3333:4444::5555:'),
        (False, '1111:2222:3333::5555:'),
        (False, '1111:2222::5555:'),
        (False, '1111::5555:'),
        (False, '::5555:'),
        (False, ':::'),
        (False, '1111:'),
        (False, ':'),

        (False, ':1111:2222:3333:4444::5555'),
        (False, ':1111:2222:3333::5555'),
        (False, ':1111:2222::5555'),
        (False, ':1111::5555'),
        (False, ':::5555'),
        (False, ':::'),

        # Additional test cases
        # from https://rt.cpan.org/Public/Bug/Display.html?id=50693

        (True, '2001:0db8:85a3:0000:0000:8a2e:0370:7334'),
        (True, '2001:db8:85a3:0:0:8a2e:370:7334'),
        (True, '2001:db8:85a3::8a2e:370:7334'),
        (True, '2001:0db8:0000:0000:0000:0000:1428:57ab'),
        (True, '2001:0db8:0000:0000:0000::1428:57ab'),
        (True, '2001:0db8:0:0:0:0:1428:57ab'),
        (True, '2001:0db8:0:0::1428:57ab'),
        (True, '2001:0db8::1428:57ab'),
        (True, '2001:db8::1428:57ab'),
        (True, '0000:0000:0000:0000:0000:0000:0000:0001'),
        (True, '::1'),
        (True, '::ffff:0c22:384e'),
        (True, '2001:0db8:1234:0000:0000:0000:0000:0000'),
        (True, '2001:0db8:1234:ffff:ffff:ffff:ffff:ffff'),
        (True, '2001:db8:a::123'),
        (True, 'fe80::'),

        (False, '123'),
        (False, 'ldkfj'),
        (False, '2001::FFD3::57ab'),
        (False, '2001:db8:85a3::8a2e:37023:7334'),
        (False, '2001:db8:85a3::8a2e:370k:7334'),
        (False, '1:2:3:4:5:6:7:8:9'),
        (False, '1::2::3'),
        (False, '1:::3:4:5'),
        (False, '1:2:3::4:5:6:7:8:9'),

        # New from Aeron
        (True, '1111:2222:3333:4444:5555:6666:7777:8888'),
        (True, '1111:2222:3333:4444:5555:6666:7777::'),
        (True, '1111:2222:3333:4444:5555:6666::'),
        (True, '1111:2222:3333:4444:5555::'),
        (True, '1111:2222:3333:4444::'),
        (True, '1111:2222:3333::'),
        (True, '1111:2222::'),
        (True, '1111::'),
        (True, '1111:2222:3333:4444:5555:6666::8888'),
        (True, '1111:2222:3333:4444:5555::8888'),
        (True, '1111:2222:3333:4444::8888'),
        (True, '1111:2222:3333::8888'),
        (True, '1111:2222::8888'),
        (True, '1111::8888'),
        (True, '::8888'),
        (True, '1111:2222:3333:4444:5555::7777:8888'),
        (True, '1111:2222:3333:4444::7777:8888'),
        (True, '1111:2222:3333::7777:8888'),
        (True, '1111:2222::7777:8888'),
        (True, '1111::7777:8888'),
        (True, '::7777:8888'),
        (True, '1111:2222:3333:4444::6666:7777:8888'),
        (True, '1111:2222:3333::6666:7777:8888'),
        (True, '1111:2222::6666:7777:8888'),
        (True, '1111::6666:7777:8888'),
        (True, '::6666:7777:8888'),
        (True, '1111:2222:3333::5555:6666:7777:8888'),
        (True, '1111:2222::5555:6666:7777:8888'),
        (True, '1111::5555:6666:7777:8888'),
        (True, '::5555:6666:7777:8888'),
        (True, '1111:2222::4444:5555:6666:7777:8888'),
        (True, '1111::4444:5555:6666:7777:8888'),
        (True, '::4444:5555:6666:7777:8888'),
        (True, '1111::3333:4444:5555:6666:7777:8888'),
        (True, '::3333:4444:5555:6666:7777:8888'),
        (True, '::2222:3333:4444:5555:6666:7777:8888'),
        (True, '1111:2222:3333:4444:5555:6666:123.123.123.123'),
        (True, '1111:2222:3333:4444:5555::123.123.123.123'),
        (True, '1111:2222:3333:4444::123.123.123.123'),
        (True, '1111:2222:3333::123.123.123.123'),
        (True, '1111:2222::123.123.123.123'),
        (True, '1111::123.123.123.123'),
        (True, '::123.123.123.123'),
        (True, '1111:2222:3333:4444::6666:123.123.123.123'),
        (True, '1111:2222:3333::6666:123.123.123.123'),
        (True, '1111:2222::6666:123.123.123.123'),
        (True, '1111::6666:123.123.123.123'),
        (True, '::6666:123.123.123.123'),
        (True, '1111:2222:3333::5555:6666:123.123.123.123'),
        (True, '1111:2222::5555:6666:123.123.123.123'),
        (True, '1111::5555:6666:123.123.123.123'),
        (True, '::5555:6666:123.123.123.123'),
        (True, '1111:2222::4444:5555:6666:123.123.123.123'),
        (True, '1111::4444:5555:6666:123.123.123.123'),
        (True, '::4444:5555:6666:123.123.123.123'),
        (True, '1111::3333:4444:5555:6666:123.123.123.123'),
        (True, '::2222:3333:4444:5555:6666:123.123.123.123'),

        # Playing with combinations of "0" and "::"
        # NB: these are all sytactically correct, but are bad form
        #   because "0" adjacent to "::" should be combined into "::"
        (True, '::0:0:0:0:0:0:0'),
        (True, '::0:0:0:0:0:0'),
        (True, '::0:0:0:0:0'),
        (True, '::0:0:0:0'),
        (True, '::0:0:0'),
        (True, '::0:0'),
        (True, '::0'),
        (True, '0:0:0:0:0:0:0::'),
        (True, '0:0:0:0:0:0::'),
        (True, '0:0:0:0:0::'),
        (True, '0:0:0:0::'),
        (True, '0:0:0::'),
        (True, '0:0::'),
        (True, '0::'),

        # New invalid from Aeron
        # Invalid data
        (False, 'XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX'),

        # Too many components
        (False, '1111:2222:3333:4444:5555:6666:7777:8888:9999'),
        (False, '1111:2222:3333:4444:5555:6666:7777:8888::'),
        (False, '::2222:3333:4444:5555:6666:7777:8888:9999'),

        # Too few components
        (False, '1111:2222:3333:4444:5555:6666:7777'),
        (False, '1111:2222:3333:4444:5555:6666'),
        (False, '1111:2222:3333:4444:5555'),
        (False, '1111:2222:3333:4444'),
        (False, '1111:2222:3333'),
        (False, '1111:2222'),
        (False, '1111'),

        # Missing :
        (False, '11112222:3333:4444:5555:6666:7777:8888'),
        (False, '1111:22223333:4444:5555:6666:7777:8888'),
        (False, '1111:2222:33334444:5555:6666:7777:8888'),
        (False, '1111:2222:3333:44445555:6666:7777:8888'),
        (False, '1111:2222:3333:4444:55556666:7777:8888'),
        (False, '1111:2222:3333:4444:5555:66667777:8888'),
        (False, '1111:2222:3333:4444:5555:6666:77778888'),

        # Missing : intended for ::
        (False, '1111:2222:3333:4444:5555:6666:7777:8888:'),
        (False, '1111:2222:3333:4444:5555:6666:7777:'),
        (False, '1111:2222:3333:4444:5555:6666:'),
        (False, '1111:2222:3333:4444:5555:'),
        (False, '1111:2222:3333:4444:'),
        (False, '1111:2222:3333:'),
        (False, '1111:2222:'),
        (False, '1111:'),
        (False, ':'),
        (False, ':8888'),
        (False, ':7777:8888'),
        (False, ':6666:7777:8888'),
        (False, ':5555:6666:7777:8888'),
        (False, ':4444:5555:6666:7777:8888'),
        (False, ':3333:4444:5555:6666:7777:8888'),
        (False, ':2222:3333:4444:5555:6666:7777:8888'),
        (False, ':1111:2222:3333:4444:5555:6666:7777:8888'),

        # :::
        (False, ':::2222:3333:4444:5555:6666:7777:8888'),
        (False, '1111:::3333:4444:5555:6666:7777:8888'),
        (False, '1111:2222:::4444:5555:6666:7777:8888'),
        (False, '1111:2222:3333:::5555:6666:7777:8888'),
        (False, '1111:2222:3333:4444:::6666:7777:8888'),
        (False, '1111:2222:3333:4444:5555:::7777:8888'),
        (False, '1111:2222:3333:4444:5555:6666:::8888'),
        (False, '1111:2222:3333:4444:5555:6666:7777:::'),

        # Double ::
        (False, '::2222::4444:5555:6666:7777:8888'),
        (False, '::2222:3333::5555:6666:7777:8888'),
        (False, '::2222:3333:4444::6666:7777:8888'),
        (False, '::2222:3333:4444:5555::7777:8888'),
        (False, '::2222:3333:4444:5555:7777::8888'),
        (False, '::2222:3333:4444:5555:7777:8888::'),

        (False, '1111::3333::5555:6666:7777:8888'),
        (False, '1111::3333:4444::6666:7777:8888'),
        (False, '1111::3333:4444:5555::7777:8888'),
        (False, '1111::3333:4444:5555:6666::8888'),
        (False, '1111::3333:4444:5555:6666:7777::'),

        (False, '1111:2222::4444::6666:7777:8888'),
        (False, '1111:2222::4444:5555::7777:8888'),
        (False, '1111:2222::4444:5555:6666::8888'),
        (False, '1111:2222::4444:5555:6666:7777::'),

        (False, '1111:2222:3333::5555::7777:8888'),
        (False, '1111:2222:3333::5555:6666::8888'),
        (False, '1111:2222:3333::5555:6666:7777::'),

        (False, '1111:2222:3333:4444::6666::8888'),
        (False, '1111:2222:3333:4444::6666:7777::'),

        (False, '1111:2222:3333:4444:5555::7777::'),

        # Too many components"
        (False, '1111:2222:3333:4444:5555:6666:7777:8888:1.2.3.4'),
        (False, '1111:2222:3333:4444:5555:6666:7777:1.2.3.4'),
        (False, '1111:2222:3333:4444:5555:6666::1.2.3.4'),
        (False, '::2222:3333:4444:5555:6666:7777:1.2.3.4'),
        (False, '1111:2222:3333:4444:5555:6666:1.2.3.4.5'),

        # Too few components
        (False, '1111:2222:3333:4444:5555:1.2.3.4'),
        (False, '1111:2222:3333:4444:1.2.3.4'),
        (False, '1111:2222:3333:1.2.3.4'),
        (False, '1111:2222:1.2.3.4'),
        (False, '1111:1.2.3.4'),

        # Missing :
        (False, '11112222:3333:4444:5555:6666:1.2.3.4'),
        (False, '1111:22223333:4444:5555:6666:1.2.3.4'),
        (False, '1111:2222:33334444:5555:6666:1.2.3.4'),
        (False, '1111:2222:3333:44445555:6666:1.2.3.4'),
        (False, '1111:2222:3333:4444:55556666:1.2.3.4'),
        (False, '1111:2222:3333:4444:5555:66661.2.3.4'),

        # Missing .
        (False, '1111:2222:3333:4444:5555:6666:255255.255.255'),
        (False, '1111:2222:3333:4444:5555:6666:255.255255.255'),
        (False, '1111:2222:3333:4444:5555:6666:255.255.255255'),

        # Missing : intended for ::
        (False, ':1.2.3.4'),
        (False, ':6666:1.2.3.4'),
        (False, ':5555:6666:1.2.3.4'),
        (False, ':4444:5555:6666:1.2.3.4'),
        (False, ':3333:4444:5555:6666:1.2.3.4'),
        (False, ':2222:3333:4444:5555:6666:1.2.3.4'),
        (False, ':1111:2222:3333:4444:5555:6666:1.2.3.4'),

        # :::
        (False, ':::2222:3333:4444:5555:6666:1.2.3.4'),
        (False, '1111:::3333:4444:5555:6666:1.2.3.4'),
        (False, '1111:2222:::4444:5555:6666:1.2.3.4'),
        (False, '1111:2222:3333:::5555:6666:1.2.3.4'),
        (False, '1111:2222:3333:4444:::6666:1.2.3.4'),
        (False, '1111:2222:3333:4444:5555:::1.2.3.4'),

        # Double ::
        (False, '::2222::4444:5555:6666:1.2.3.4'),
        (False, '::2222:3333::5555:6666:1.2.3.4'),
        (False, '::2222:3333:4444::6666:1.2.3.4'),
        (False, '::2222:3333:4444:5555::1.2.3.4'),

        (False, '1111::3333::5555:6666:1.2.3.4'),
        (False, '1111::3333:4444::6666:1.2.3.4'),
        (False, '1111::3333:4444:5555::1.2.3.4'),

        (False, '1111:2222::4444::6666:1.2.3.4'),
        (False, '1111:2222::4444:5555::1.2.3.4'),

        (False, '1111:2222:3333::5555::1.2.3.4'),

        # Missing parts
        (False, '::.'),
        (False, '::..'),
        (False, '::...'),
        (False, '::1...'),
        (False, '::1.2..'),
        (False, '::1.2.3.'),
        (False, '::.2..'),
        (False, '::.2.3.'),
        (False, '::.2.3.4'),
        (False, '::..3.'),
        (False, '::..3.4'),
        (False, '::...4'),

        # Extra : in front
        (False, ':1111:2222:3333:4444:5555:6666:7777::'),
        (False, ':1111:2222:3333:4444:5555:6666::'),
        (False, ':1111:2222:3333:4444:5555::'),
        (False, ':1111:2222:3333:4444::'),
        (False, ':1111:2222:3333::'),
        (False, ':1111:2222::'),
        (False, ':1111::'),
        (False, ':::'),
        (False, ':1111:2222:3333:4444:5555:6666::8888'),
        (False, ':1111:2222:3333:4444:5555::8888'),
        (False, ':1111:2222:3333:4444::8888'),
        (False, ':1111:2222:3333::8888'),
        (False, ':1111:2222::8888'),
        (False, ':1111::8888'),
        (False, ':::8888'),
        (False, ':1111:2222:3333:4444:5555::7777:8888'),
        (False, ':1111:2222:3333:4444::7777:8888'),
        (False, ':1111:2222:3333::7777:8888'),
        (False, ':1111:2222::7777:8888'),
        (False, ':1111::7777:8888'),
        (False, ':::7777:8888'),
        (False, ':1111:2222:3333:4444::6666:7777:8888'),
        (False, ':1111:2222:3333::6666:7777:8888'),
        (False, ':1111:2222::6666:7777:8888'),
        (False, ':1111::6666:7777:8888'),
        (False, ':::6666:7777:8888'),
        (False, ':1111:2222:3333::5555:6666:7777:8888'),
        (False, ':1111:2222::5555:6666:7777:8888'),
        (False, ':1111::5555:6666:7777:8888'),
        (False, ':::5555:6666:7777:8888'),
        (False, ':1111:2222::4444:5555:6666:7777:8888'),
        (False, ':1111::4444:5555:6666:7777:8888'),
        (False, ':::4444:5555:6666:7777:8888'),
        (False, ':1111::3333:4444:5555:6666:7777:8888'),
        (False, ':::3333:4444:5555:6666:7777:8888'),
        (False, ':::2222:3333:4444:5555:6666:7777:8888'),
        (False, ':1111:2222:3333:4444:5555:6666:1.2.3.4'),
        (False, ':1111:2222:3333:4444:5555::1.2.3.4'),
        (False, ':1111:2222:3333:4444::1.2.3.4'),
        (False, ':1111:2222:3333::1.2.3.4'),
        (False, ':1111:2222::1.2.3.4'),
        (False, ':1111::1.2.3.4'),
        (False, ':::1.2.3.4'),
        (False, ':1111:2222:3333:4444::6666:1.2.3.4'),
        (False, ':1111:2222:3333::6666:1.2.3.4'),
        (False, ':1111:2222::6666:1.2.3.4'),
        (False, ':1111::6666:1.2.3.4'),
        (False, ':::6666:1.2.3.4'),
        (False, ':1111:2222:3333::5555:6666:1.2.3.4'),
        (False, ':1111:2222::5555:6666:1.2.3.4'),
        (False, ':1111::5555:6666:1.2.3.4'),
        (False, ':::5555:6666:1.2.3.4'),
        (False, ':1111:2222::4444:5555:6666:1.2.3.4'),
        (False, ':1111::4444:5555:6666:1.2.3.4'),
        (False, ':::4444:5555:6666:1.2.3.4'),
        (False, ':1111::3333:4444:5555:6666:1.2.3.4'),
        (False, ':::2222:3333:4444:5555:6666:1.2.3.4'),

        # Extra : at end
        (False, '1111:2222:3333:4444:5555:6666:7777:::'),
        (False, '1111:2222:3333:4444:5555:6666:::'),
        (False, '1111:2222:3333:4444:5555:::'),
        (False, '1111:2222:3333:4444:::'),
        (False, '1111:2222:3333:::'),
        (False, '1111:2222:::'),
        (False, '1111:::'),
        (False, ':::'),
        (False, '1111:2222:3333:4444:5555:6666::8888:'),
        (False, '1111:2222:3333:4444:5555::8888:'),
        (False, '1111:2222:3333:4444::8888:'),
        (False, '1111:2222:3333::8888:'),
        (False, '1111:2222::8888:'),
        (False, '1111::8888:'),
        (False, '::8888:'),
        (False, '1111:2222:3333:4444:5555::7777:8888:'),
        (False, '1111:2222:3333:4444::7777:8888:'),
        (False, '1111:2222:3333::7777:8888:'),
        (False, '1111:2222::7777:8888:'),
        (False, '1111::7777:8888:'),
        (False, '::7777:8888:'),
        (False, '1111:2222:3333:4444::6666:7777:8888:'),
        (False, '1111:2222:3333::6666:7777:8888:'),
        (False, '1111:2222::6666:7777:8888:'),
        (False, '1111::6666:7777:8888:'),
        (False, '::6666:7777:8888:'),
        (False, '1111:2222:3333::5555:6666:7777:8888:'),
        (False, '1111:2222::5555:6666:7777:8888:'),
        (False, '1111::5555:6666:7777:8888:'),
        (False, '::5555:6666:7777:8888:'),
        (False, '1111:2222::4444:5555:6666:7777:8888:'),
        (False, '1111::4444:5555:6666:7777:8888:'),
        (False, '::4444:5555:6666:7777:8888:'),
        (False, '1111::3333:4444:5555:6666:7777:8888:'),
        (False, '::3333:4444:5555:6666:7777:8888:'),
        (False, '::2222:3333:4444:5555:6666:7777:8888:'),

        # Additional cases:
        # http://crisp.tweakblogs.net/blog/2031/ipv6-validation-%28and-caveats%29.html
        (True, '0:a:b:c:d:e:f::'),
        # syntactically correct, but bad form (::0:... could be combined)
        (True, '::0:a:b:c:d:e:f'),
        (True, 'a:b:c:d:e:f:0::'),
        (False, "':10.0.0.1"),

        # Known bugs with ipaddr v2.1.10 but works with ipaddress
        (False, '02001:0000:1234:0000:0000:C1C0:ABCD:0876'),
        (False, '2001:0000:1234:0000:00001:C1C0:ABCD:0876'),
    ]

    def setUp(self):
        """Set up test."""
        self.total = 0
        super().setUp()

    def tearDown(self):
        """Tear down test."""
        super().tearDown()
        unittest_print('{} subtests done'.format(self.total))

    def ipv6test(self, result, ip_address):
        """Perform one ip_address test."""
        self.total += 1
        with self.subTest(ip_address=ip_address):
            self.assertEqual(result, is_IP(ip_address))

    def test_ipaddress_module(self):
        """Test ipaddress module."""
        for result, ip_address in self.ip6:
            self.ipv6test(result, ip_address)

    @unittest.expectedFailure
    def test_T76286a_failures(self):
        """Test known bugs in the ipaddress module."""
        # The following fail with the ipaddress module. See T76286
        self.ipv6test(False, '1111:2222:3333:4444:5555:6666:00.00.00.00')

    @unittest.expectedFailure
    def test_T76286b_failures(self):
        """Test known bugs in the ipaddress module."""
        self.ipv6test(False, '1111:2222:3333:4444:5555:6666:000.000.000.000')

    @expected_failure_if(PYTHON_VERSION >= (3, 8))
    def test_T240060_failures(self):
        """Test known deviated behaviour in Python 3.8."""
        # Testing IPv4 addresses represented as dotted-quads
        # Leading zero's in IPv4 addresses not allowed: some systems treat the
        # leading "0" in ".086" as the start of an octal number
        # Update: The BNF in RFC-3986 explicitly defines the dec-octet
        # (for IPv4 addresses) not to have a leading zero
        self.ipv6test(False,
                      'fe80:0000:0000:0000:0204:61ff:254.157.241.086')


if __name__ == '__main__':  # pragma: no cover
    with suppress(SystemExit):
        unittest.main()
