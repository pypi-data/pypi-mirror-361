# Expected output for simple project amalgamation
#include <iostream>

void utility_function();

void utility_function() {
    std::cout << "Utility function called" << std::endl;
}

int main() {
    std::cout << "Simple project main" << std::endl;
    utility_function();
    return 0;
}
