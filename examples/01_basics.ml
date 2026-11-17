// 01_basics.ml - Variables, Constants, and Arithmetic

println("--- Basics & Arithmetic ---");

var a = 15;
var b = 4;
const PI = 3.14159;

println("a =", a);
println("b =", b);
println("PI =", PI);

println("a + b =", a + b);
println("a - b =", a - b);
println("a * b =", a * b);
println("a / b =", a / b);
println("a % b =", a % b);
println("2 ^ 8 =", 2 ^ 8);

// Compound assignment
a += 5;
println("a after += 5:", a);

// Strings
var greeting = "Hello";
var target = "World";
var message = greeting + ", " + target + "! Number: " + 100;
println("String concat:", message);

// Math Utilities
println("\n--- Math Utilities ---");
println("abs(-42) =", abs(-42));
println("sign(-25) =", sign(-25), "sign(25) =", sign(25), "sign(0) =", sign(0));
println("min(8, 3, 12, 1) =", min(8, 3, 12, 1));
println("max([4, 19, 7, 2]) =", max([4, 19, 7, 2]));
println("clamp(105, 0, 100) =", clamp(105, 0, 100));
println("rem(17, 5) =", rem(17, 5));
println("gcd(54, 24) =", gcd(54, 24));
println("lcm(12, 18) =", lcm(12, 18));
