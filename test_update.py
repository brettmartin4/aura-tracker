import unittest
from update import matches_keyword, entries

class KeywordTests(unittest.TestCase):
    def test_match(self):
        cases = [
            'NARCISSIST', 'narcissists', 'narcissistic', 'narcissism',
            'narcissistically', 'narcisist', 'narsissist', 'narcississt',
            'narccissistic', 'narcissits', "narcissist's", 'NARCISSISSM',
        ]
        for word in cases:
            with self.subTest(word=word):
                self.assertTrue(matches_keyword('Person is ' + word + '!'))

    def test_nonmatch(self):
        for word in ['narcotic', 'narcotics', 'nice person', 'hot dog', 'cat', 'narcissisticperson']:
            with self.subTest(word=word):
                self.assertFalse(matches_keyword(word))

    def test_rss(self):
        xml = b'''<rss><channel><item><guid>abc</guid><title>narcisist</title><description>two narcissists</description><pubDate>Wed, 28 Oct 2026 11:00:00 -0400</pubDate></item></channel></rss>'''
        self.assertEqual(list(entries(xml)), [('2026-10-28', 'abc', True)])

if __name__ == '__main__':
    unittest.main()
