#include <cmath>
#include <iostream>
#include "plugin_registry.hpp"

class MathPlugin : public IPlugin {
public:
	std::string getName() const override {
		return "MathPlugin";
	}

	std::string getVersion() const override {
		return "1.0.0";
	}

	std::string getDescription() const override {
		return "Provides basic mathematical operations and calculations";
	}

	bool initialize() override {
		std::cout << "  [MathPlugin] Initializing math operations..." << std::endl;
		return true;
	}

	void execute() override {
		std::cout << "  [MathPlugin] Performing mathematical calculations:" << std::endl;

		// Demonstrate some math operations
		double a = 15.5, b = 3.2;
		std::cout << "    " << a << " + " << b << " = " << (a + b) << std::endl;
		std::cout << "    " << a << " * " << b << " = " << (a * b) << std::endl;
		std::cout << "    sqrt(" << a << ") = " << std::sqrt(a) << std::endl;
		std::cout << "    sin(π/2) = " << std::sin(M_PI / 2) << std::endl;

		// Calculate factorial of 5
		int n = 5;
		int factorial = 1;
		for (int i = 1; i <= n; ++i) {
			factorial *= i;
		}
		std::cout << "    " << n << "! = " << factorial << std::endl;
	}

	void shutdown() override {
		std::cout << "  [MathPlugin] Cleaning up math operations..." << std::endl;
	}
};

REGISTER_PLUGIN(MathPlugin);
