// 04_lists.ml - Lists and Built-in Operations

var numbers = [10, 20, 30];
println("Initial list:", numbers);
println("Length:", len(numbers));

// Indexing and mutation
println("First element:", numbers[0]);
println("Last element:", numbers[-1]);

numbers[1] = 999;
println("After mutating index 1:", numbers);

// Push and pop
push(numbers, 40);
push(numbers, 50);
println("After push operations:", numbers);

var popped = pop(numbers);
println("Popped value:", popped);
println("After pop:", numbers);

// Range generation and loop
println("\nIteration over range(0, 5):");
var r = range(0, 5);
for i to len(r) - 1 {
    println("Index", i, "Value:", r[i]);
}

// Slicing, Splitting, and Joining
println("\n--- Slicing, Splitting, and Joining ---");
var sub = slice(numbers, 1, 3);
println("slice(numbers, 1, 3):", sub);
println("Original remains unchanged:", numbers);

var sentence = "programming languages are fun";
var words = split(sentence, " ");
println("split(sentence, ' '):", words);

var hyphenated = join(words, "-");
println("join(words, '-'):", hyphenated);
