import unittest
import warnings

from pact import Pact, PactException


class TestPact(unittest.TestCase):
    def test_missing_attributes(self):
        class MyPact(Pact):
            foo: str
            bar: str

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)

            with self.assertRaises(PactException) as context:
                class BrokenPact(MyPact):
                    foo = 'foo'  # bar missing

        self.assertIn('bar', str(context.exception))
        self.assertIn('BrokenPact', str(context.exception))

    def test_type_mismatch_attributes(self):
        class MyPact(Pact):
            foo: str
            bar: int

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)

            with self.assertRaises(PactException) as context:
                class BrokenPact(MyPact):
                    foo = 'foo'
                    bar = 'should be int'  # Wrong type

        self.assertIn('bar', str(context.exception))
        self.assertIn('BrokenPact', str(context.exception))

    def test_valid_attributes(self):
        class MyPact(Pact):
            foo: str
            bar: str

        try:
            class GoodPact(MyPact):
                foo = 'foo'
                bar = 'bar'
        except PactException:
            self.fail('PactException raised unexpectedly')
