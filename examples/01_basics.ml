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
