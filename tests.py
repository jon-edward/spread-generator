from unittest import TestCase
from spread_generator import spread_generator, SpreadGeneratorError


class TestSpreadGenerator(TestCase):
    def test_spread_generator_outside_assignment(self):
        """
        Test that spread_generator raises an error if used outside of an assignment
        """

        @spread_generator
        def test_func():
            yield 1
            yield 2
            yield 3
            yield 4
            yield 5
            yield 6
            yield 7

        with self.assertRaises(SpreadGeneratorError):
            test_func()

    def test_spread_generator_tuple_list(self):
        """
        Test that spread_generator works on both tuples and list assignments
        """

        @spread_generator
        def test_func():
            yield 1
            yield 2
            yield 3
            yield 4
            yield 5
            yield 6
            yield 7

        (a_tup, b_tup, c_tup), rest_tup = test_func()
        [a_list, b_list, c_list], rest_list = test_func()

        self.assertEqual(a_tup, a_list)
        self.assertEqual(b_tup, b_list)
        self.assertEqual(c_tup, c_list)

        self.assertListEqual(list(rest_tup), list(rest_list))

    def test_spread_generator_all(self):
        """
        Test that spread_generator can be used to unpack all values to
        names in an assignment
        """

        @spread_generator
        def test_func():
            yield 1
            yield 2
            yield 3
            yield 4
            yield 5
            yield 6
            yield 7

        (a, *b, c), empty = test_func()

        self.assertEqual(a, 1)
        self.assertListEqual(b, [2, 3, 4, 5, 6])
        self.assertEqual(c, 7)
        self.assertListEqual(list(empty), [])

    def test_spread_generator_infinite(self):
        """
        Test that spread_generator can be used to unpack infinite generators
        """

        @spread_generator
        def test_func():
            while True:
                yield 1

        (a, b, c), infinite_gen = test_func()

        self.assertEqual(a, 1)
        self.assertEqual(b, 1)
        self.assertEqual(c, 1)
        self.assertEqual(next(infinite_gen), 1)

    def test_spread_generator_no_names(self):
        """
        Test that spread_generator raises an error if the assignment has no names
        """

        @spread_generator
        def test_func():
            yield 1
            yield 2
            yield 3
            yield 4
            yield 5
            yield 6
            yield 7

        (), rest = test_func()

        self.assertListEqual(list(rest), [1, 2, 3, 4, 5, 6, 7])
