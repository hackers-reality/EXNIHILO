import unittest

from exnihilo import generate_sentence, random_byte_stream, random_word


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.source = random_byte_stream(4096)

    def test_word_length(self):
        for _ in range(1000):
            word = random_word(self.source)
            self.assertGreaterEqual(len(word), 1)
            self.assertLessEqual(len(word), 35)
            self.assertTrue(word.islower())
            self.assertTrue(word.isalpha())

    def test_sentence_has_no_empty_tokens(self):
        for _ in range(1000):
            sentence = generate_sentence(self.source)
            self.assertTrue(sentence)
            self.assertNotIn("  ", sentence)


if __name__ == "__main__":
    unittest.main()
