// 05_fibonacci.ml - Benchmark Fibonacci calculation

func fib(n) {
    if (n <= 1) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

var n = 20;
println("Calculating fib(" + n + ")...");

var start = clock();
var result = fib(n);
var elapsed = clock() - start;

println("fib(" + n + ") =", result);
println("Calculation took:", elapsed, "seconds");
