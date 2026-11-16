// 03_functions_and_closures.ml - Functions, Lambda, and Closures

println("--- Functions & Recursion ---");

func factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

println("factorial(5) =", factorial(5));
println("factorial(7) =", factorial(7));

println("\n--- First-Class Functions & Higher Order ---");

func applyTwice(f, x) {
    return f(f(x));
}

var double = func(val) {
    return val * 2;
};

println("applyTwice(double, 5) =", applyTwice(double, 5));

println("\n--- Lexical Closures ---");

func createAccumulator(initial) {
    var sum = initial;
    return func(amount) {
        sum += amount;
        return sum;
    };
}

var wallet = createAccumulator(100);
println("Deposited 50, balance:", wallet(50));
println("Deposited 25, balance:", wallet(25));

var savings = createAccumulator(500);
println("Savings balance:", savings(100));
println("Wallet balance remains:", wallet(10));
