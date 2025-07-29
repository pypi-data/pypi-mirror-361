#pragma once
#include <memory>
#include <vector>
#include "plugin.hpp"

class PluginRegistry {
public:
	static PluginRegistry& getInstance();

	// Plugin management
	void registerPlugin(std::unique_ptr<IPlugin> plugin);
	void executeAll();
	void shutdownAll();
	void listPlugins() const;
	
	// Get plugin by name
	IPlugin* getPlugin(const std::string& name) const;
	
	// Get all plugins
	const std::vector<std::unique_ptr<IPlugin>>& getPlugins() const;

private:
	PluginRegistry() = default;
	std::vector<std::unique_ptr<IPlugin>> plugins_;
};

// Helper macro for plugin registration
#define REGISTER_PLUGIN(PluginClass) \
	static bool registered_##PluginClass = []() { \
		PluginRegistry::getInstance().registerPlugin(std::make_unique<PluginClass>()); \
		return true; \
	}();
