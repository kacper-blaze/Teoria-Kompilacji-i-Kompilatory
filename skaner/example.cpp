// Example file to test the syntax highlighter
#include <iostream>
#include <string>

/* This is a block comment
   that spans multiple lines */

function calculateSum(int a, int b) {
    var result = a + b;
    return result;
}

int main() {
    // Variable declarations
    int x = 42;
    float pi = 3.14159;
    bool isActive = true;
    bool isDone = false;
    string message = "Hello, World!";

    // Conditional statements
    if (x > 0) {
        cout << "Positive number" << endl;
    } else if (x < 0) {
        cout << "Negative number" << endl;
    } else {
        cout << "Zero" << endl;
    }

    // Loop examples
    for (int i = 0; i < 10; i++) {
        cout << i << " ";
    }

    int count = 0;
    while (count < 5) {
        count++;
        if (count == 3) {
            continue;
        }
        cout << "Count: " << count << endl;
    }

    // Function call
    int sum = calculateSum(x, 10);

    // Operators and expressions
    bool result = (x >= 10) && (isActive == true) || (sum != 0);

    void* ptr = nullptr;

    return 0;
}

// Another function with different parameters
function processArray(int arr[], int size) {
    for (int i = 0; i < size; i++) {
        var value = arr[i];
        if (value % 2 == 0) {
            cout << "Even: " << value << endl;
        }
    }
}