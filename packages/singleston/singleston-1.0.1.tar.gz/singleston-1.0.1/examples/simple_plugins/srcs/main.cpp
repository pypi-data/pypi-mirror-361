#include <iostream>
#include "plugin_registry.hpp"

int main() {
	std::cout << "=== Plugin System Demo ===" << std::endl;

	// List all registered plugins
	PluginRegistry& registry = PluginRegistry::getInstance();
	registry.listPlugins();

	// Execute all plugins
	registry.executeAll();

	std::cout << "\n=== Demo: Get specific plugin ===" << std::endl;
	IPlugin* mathPlugin = registry.getPlugin("MathPlugin");
	if (mathPlugin) {
		std::cout << "Found plugin: " << mathPlugin->getName() 
				  << " v" << mathPlugin->getVersion() << std::endl;
	}

	// Shutdown all plugins
	registry.shutdownAll();

	std::cout << "\n=== Plugin System Demo Complete ===" << std::endl;
	return 0;
}
