// 02_control_flow.ml - Conditionals and Loops

println("--- Conditionals ---");

var score = 85;

if (score >= 90) {
    println("Grade: A");
} else if (score >= 80) {
    println("Grade: B");
} else {
    println("Grade: C or below");
}

println("\n--- While Loop ---");
var count = 3;
while (count > 0) {
    println("Countdown:", count);
    count -= 1;
}
println("Liftoff!");

println("\n--- For Loop with Break & Continue ---");
var total = 0;
for i = 1 to 10 {
    if (i % 2 == 0) {
        continue; // Skip even numbers
    }
    if (i > 7) {
        break; // Stop when i > 7
    }
    println("Adding odd number:", i);
    total += i;
}
println("Sum of odd numbers <= 7:", total);

println("\n--- For Loop with 'to' and 'by' (Increments & Decrements) ---");
println("Default +1 step (for i to 3):");
for i to 3 {
    println("i =", i);
}

println("\nPositive step by 2 (for i = 0 to 6 by 2):");
for i = 0 to 6 by 2 {
    println("even step:", i);
}

println("\nNegative step by -1 (for i = 5 to 1 by -1):");
for i = 5 to 1 by -1 {
    println("countdown:", i);
}
