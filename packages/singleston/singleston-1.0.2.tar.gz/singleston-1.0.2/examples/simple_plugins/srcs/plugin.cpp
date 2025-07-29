#include <algorithm>
#include <iostream>
#include "plugin_registry.hpp"

// Singleton implementation
PluginRegistry& PluginRegistry::getInstance() {
	static PluginRegistry instance;
	return instance;
}

void PluginRegistry::registerPlugin(std::unique_ptr<IPlugin> plugin) {
	if (plugin) {
		std::cout << "Registering plugin: " << plugin->getName() << std::endl;
		plugins_.push_back(std::move(plugin));
	}
}

void PluginRegistry::executeAll() {
	std::cout << "\n=== Executing all plugins ===" << std::endl;
	for (auto& plugin : plugins_) {
		if (plugin->initialize()) {
			std::cout << "Executing: " << plugin->getName() << std::endl;
			plugin->execute();
		} else {
			std::cout << "Failed to initialize: " << plugin->getName() << std::endl;
		}
	}
}

void PluginRegistry::shutdownAll() {
	std::cout << "\n=== Shutting down all plugins ===" << std::endl;
	for (auto& plugin : plugins_) {
		std::cout << "Shutting down: " << plugin->getName() << std::endl;
		plugin->shutdown();
	}
}

void PluginRegistry::listPlugins() const {
	std::cout << "\n=== Registered Plugins ===" << std::endl;
	for (const auto& plugin : plugins_) {
		std::cout << "Name: " << plugin->getName() << std::endl;
		std::cout << "Version: " << plugin->getVersion() << std::endl;
		std::cout << "Description: " << plugin->getDescription() << std::endl;
		std::cout << "---" << std::endl;
	}
}

IPlugin* PluginRegistry::getPlugin(const std::string& name) const {
	auto it = std::find_if(plugins_.begin(), plugins_.end(),
		[&name](const std::unique_ptr<IPlugin>& plugin) {
			return plugin->getName() == name;
		});

	return (it != plugins_.end()) ? it->get() : nullptr;
}

const std::vector<std::unique_ptr<IPlugin>>& PluginRegistry::getPlugins() const {
	return plugins_;
}
