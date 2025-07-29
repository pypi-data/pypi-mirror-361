#include <iostream>
#include "plugin_registry.hpp"

class StringPlugin : public IPlugin {
public:
	std::string getName() const override {
		return "StringPlugin";
	}

	std::string getVersion() const override {
		return "2.1.0";
	}

	std::string getDescription() const override {
		return "Provides string manipulation and text processing utilities";
	}

	bool initialize() override {
		std::cout << "  [StringPlugin] Initializing string operations..." << std::endl;
		return true;
	}

	void execute() override {
		std::cout << "  [StringPlugin] Performing string operations:" << std::endl;

		// Demonstrate string operations
		std::string text = "Hello, Plugin System!";
		std::cout << "    Original: \"" << text << "\"" << std::endl;

		// Convert to uppercase
		std::string upper = text;
		std::transform(upper.begin(), upper.end(), upper.begin(), ::toupper);
		std::cout << "    Uppercase: \"" << upper << "\"" << std::endl;

		// Reverse string
		std::string reversed = text;
		std::reverse(reversed.begin(), reversed.end());
		std::cout << "    Reversed: \"" << reversed << "\"" << std::endl;

		// Count words
		int wordCount = countWords(text);
		std::cout << "    Word count: " << wordCount << std::endl;

		// Find substring
		std::string search = "Plugin";
		size_t pos = text.find(search);
		if (pos != std::string::npos) {
			std::cout << "    Found \"" << search << "\" at position " << pos << std::endl;
		}

		// Split into words
		std::vector<std::string> words = splitString(text, ' ');
		std::cout << "    Words: ";
		for (size_t i = 0; i < words.size(); ++i) {
			if (i > 0) std::cout << ", ";
			std::cout << "\"" << words[i] << "\"";
		}
		std::cout << std::endl;
	}

	void shutdown() override {
		std::cout << "  [StringPlugin] Cleaning up string operations..." << std::endl;
	}

private:
	int countWords(const std::string& str) {
		if (str.empty()) return 0;

		int count = 0;
		bool inWord = false;

		for (char c : str) {
			if (c != ' ' && c != '\t' && c != '\n') {
				if (!inWord) {
					count++;
					inWord = true;
				}
			} else {
				inWord = false;
			}
		}

		return count;
	}

	std::vector<std::string> splitString(const std::string& str, char delimiter) {
		std::vector<std::string> tokens;
		std::string token;

		for (char c : str) {
			if (c == delimiter) {
				if (!token.empty()) {
					tokens.push_back(token);
					token.clear();
				}
			} else {
				token += c;
			}
		}

		if (!token.empty()) {
			tokens.push_back(token);
		}

		return tokens;
	}
};

REGISTER_PLUGIN(StringPlugin);
