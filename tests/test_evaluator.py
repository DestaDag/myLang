import io
import unittest
from mylang import execute
from mylang.errors import RuntimeError


class TestEvaluator(unittest.TestCase):

    def run_code(self, code: str) -> tuple[any, str]:
        output = io.StringIO()
        res = execute(code, output_stream=output)
        return res, output.getvalue()

    def test_arithmetic(self):
        res, _ = self.run_code("2 + 3 * 4;")
        self.assertEqual(res, 14)

        res, _ = self.run_code("(2 + 3) * 4;")
        self.assertEqual(res, 20)

        res, _ = self.run_code("2 ^ 3 ^ 2;")
        self.assertEqual(res, 512)

        res, _ = self.run_code("10 % 3;")
        self.assertEqual(res, 1)

    def test_string_concatenation(self):
        res, _ = self.run_code('"Hello, " + "World!";')
        self.assertEqual(res, "Hello, World!")

        res, _ = self.run_code('"Count: " + 42;')
        self.assertEqual(res, "Count: 42")

    def test_short_circuit_logic(self):
        # In 'true or undefined_var', the right side shouldn't be evaluated!
        res, _ = self.run_code("true or not_defined;")
        self.assertEqual(res, True)

        res, _ = self.run_code("false and not_defined;")
        self.assertEqual(res, False)

    def test_scoping_and_shadowing(self):
        code = """
        var x = 10;
        var y = 0;
        {
            var x = 20;
            y = x;
        }
        x + y;
        """
        res, _ = self.run_code(code)
        self.assertEqual(res, 30)

    def test_constant_reassignment(self):
        code = """
        const PI = 3.14;
        PI = 3.14159;
        """
        with self.assertRaises(RuntimeError):
            self.run_code(code)

    def test_function_and_recursion(self):
        code = """
        func fib(n) {
            if (n <= 1) {
                return n;
            }
            return fib(n - 1) + fib(n - 2);
        }
        fib(10);
        """
        res, _ = self.run_code(code)
        self.assertEqual(res, 55)

    def test_closures(self):
        code = """
        func makeCounter(start) {
            var count = start;
            return func() {
                count += 1;
                return count;
            };
        }
        var c1 = makeCounter(10);
        c1();
        c1();
        var c2 = makeCounter(100);
        c2();
        c1();
        """
        res, _ = self.run_code(code)
        self.assertEqual(res, 13)

    def test_loops_with_break_and_continue(self):
        code = """
        var sum = 0;
        for i = 0 to 9 {
            if (i % 2 == 0) {
                continue;
            }
            if (i > 7) {
                break;
            }
            sum += i;
        }
        sum;
        """
        # i = 1, 3, 5, 7 -> sum = 16
        res, _ = self.run_code(code)
        self.assertEqual(res, 16)

    def test_for_loop_to_default_step(self):
        code = """
        var acc = 0;
        for i to 4 {
            acc += i;
        }
        acc;
        """
        # i = 0, 1, 2, 3, 4 -> 10
        res, _ = self.run_code(code)
        self.assertEqual(res, 10)

    def test_for_loop_with_positive_by(self):
        code = """
        var items = [];
        for i = 1 to 10 by 3 {
            push(items, i);
        }
        items;
        """
        # i = 1, 4, 7, 10
        res, _ = self.run_code(code)
        self.assertEqual(res, [1, 4, 7, 10])

    def test_for_loop_with_negative_by(self):
        code = """
        var countdown = [];
        for i = 10 to 4 by -2 {
            push(countdown, i);
        }
        countdown;
        """
        # i = 10, 8, 6, 4
        res, _ = self.run_code(code)
        self.assertEqual(res, [10, 8, 6, 4])

    def test_for_loop_from_existing_variable_countdown(self):
        code = """
        var i = 5;
        var list = [];
        for i to 1 by -1 {
            push(list, i);
        }
        list;
        """
        # i starts from 5, goes down to 1
        res, _ = self.run_code(code)
        self.assertEqual(res, [5, 4, 3, 2, 1])

    def test_for_loop_zero_step_error(self):
        code = """
        for i = 1 to 5 by 0 {
            print(i);
        }
        """
        with self.assertRaises(RuntimeError):
            self.run_code(code)

    def test_lists_and_builtins(self):
        code = """
        var items = [1, 2, 3];
        push(items, 4);
        var p = pop(items);
        items[0] = 99;
        var l = len(items);
        [items[0], p, l];
        """
        res, _ = self.run_code(code)
        self.assertEqual(res, [99, 4, 3])

    def test_print_builtin(self):
        code = """
        print("Hello", 42, [1, 2]);
        """
        _, out = self.run_code(code)
        self.assertEqual(out.strip(), "Hello 42 [1, 2]")

    def test_error_reporting(self):
        code = """
        var a = 10;
        var b = 0;
        var c = a / b;
        """
        with self.assertRaises(RuntimeError) as ctx:
            self.run_code(code)
        self.assertIn("Division by zero", str(ctx.exception))

    def test_slice(self):
        code = """
        var nums = [10, 20, 30, 40, 50];
        var s1 = slice(nums, 1, 4);
        var s2 = slice(nums, 2);
        var s3 = slice(nums, -2);
        var original_len = len(nums);

        var text = "Hello, World!";
        var t1 = slice(text, 0, 5);
        var t2 = slice(text, 7, 12);
        var t3 = slice(text, 7);

        [s1, s2, s3, original_len, t1, t2, t3];
        """
        res, _ = self.run_code(code)
        self.assertEqual(res, [
            [20, 30, 40],
            [30, 40, 50],
            [40, 50],
            5,
            "Hello",
            "World",
            "World!",
        ])

    def test_split(self):
        code = """
        var csv = "apple,banana,orange";
        var parts = split(csv, ",");
        var words = split("one two  three");
        [parts, words];
        """
        res, _ = self.run_code(code)
        self.assertEqual(res, [
            ["apple", "banana", "orange"],
            ["one", "two", "three"],
        ])

    def test_join(self):
        code = """
        var letters = ["a", "b", "c"];
        var j1 = join(letters, "-");
        var j2 = join([1, 2, 3], ", ");
        var j3 = join(["x", "y", "z"]);
        [j1, j2, j3];
        """
        res, _ = self.run_code(code)
        self.assertEqual(res, [
            "a-b-c",
            "1, 2, 3",
            "xyz",
        ])

    def test_math_utilities(self):
        code = """
        var a1 = abs(-15);
        var a2 = abs(42);
        var a3 = abs(0);

        var s1 = sign(-99);
        var s2 = sign(55);
        var s3 = sign(0);

        var m1 = min(5, 2, 9, -3);
        var m2 = min([10, 4, 25, 2]);

        var mx1 = max(5, 2, 9, -3);
        var mx2 = max([10, 4, 25, 2]);

        var c1 = clamp(15, 0, 10);
        var c2 = clamp(-5, 0, 10);
        var c3 = clamp(7, 0, 10);

        var r1 = rem(10, 3);
        var r2 = rem(7.5, 2.5);

        var g1 = gcd(48, 18);
        var g2 = gcd(101, 10);

        var l1 = lcm(12, 15);
        var l2 = lcm(4, 6);

        [a1, a2, a3, s1, s2, s3, m1, m2, mx1, mx2, c1, c2, c3, r1, r2, g1, g2, l1, l2];
        """
        res, _ = self.run_code(code)
        self.assertEqual(res, [
            15, 42, 0,
            -1, 1, 0,
            -3, 2,
            9, 25,
            10, 0, 7,
            1, 0.0,
            6, 1,
            60, 12,
        ])

    def test_math_utilities_errors(self):
        with self.assertRaises(RuntimeError) as ctx:
            self.run_code("rem(10, 0);")
        self.assertIn("division by zero", str(ctx.exception))

        with self.assertRaises(RuntimeError) as ctx:
            self.run_code("clamp(5, 10, 2);")
        self.assertIn("cannot be greater than", str(ctx.exception))

        with self.assertRaises(RuntimeError) as ctx:
            self.run_code("gcd(1.5, 2);")
        self.assertIn("must be integers", str(ctx.exception))

        with self.assertRaises(RuntimeError) as ctx:
            self.run_code("abs('hello');")
        self.assertIn("expects a number", str(ctx.exception))

        with self.assertRaises(RuntimeError) as ctx:
            self.run_code("min([]);")
        self.assertIn("empty list", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
