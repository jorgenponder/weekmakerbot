"""upload.py script test."""
#
# (C) Pywikibot team, 2019-2021
#
# Distributed under the terms of the MIT license.
#
import unittest

from contextlib import suppress

from scripts.upload import CHUNK_SIZE_REGEX, get_chunk_size

from tests.aspects import TestCase


class TestUploadScript(TestCase):

    """Test cases for upload."""

    net = False

    def match(self, value: str = '') -> int:
        """Create a match object and call get_chunk_site.

        @param value: a chunk size value
        @return: chunk size in bytes
        """
        option = '-chunked'
        if value:
            option += ':' + value
        match = CHUNK_SIZE_REGEX.match(option)
        return get_chunk_size(match)

    def test_regex(self):
        """Test CHUNK_SIZE_REGEX and get_chunk_size function."""
        self.assertEqual(self.match(), 1024 ** 2)
        self.assertEqual(self.match('12345'), 12345)
        self.assertEqual(self.match('4567k'), 4567 * 1000)
        self.assertEqual(self.match('7890m'), 7890 * 10 ** 6)
        self.assertEqual(self.match('987ki'), 987 * 1024)
        self.assertEqual(self.match('654mi'), 654 * 1024 ** 2)
        self.assertEqual(self.match('3mike'), 0)


if __name__ == '__main__':  # pragma: no cover
    with suppress(SystemExit):
        unittest.main()
