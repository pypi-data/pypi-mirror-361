#ifndef PLUGIN_HPP
# define PLUGIN_HPP
# include <string>

class IPlugin {
public:
	virtual ~IPlugin() = default;

	// Plugin identification
	virtual std::string getName() const = 0;
	virtual std::string getVersion() const = 0;
	virtual std::string getDescription() const = 0;

	// Plugin lifecycle
	virtual bool initialize() = 0;
	virtual void execute() = 0;
	virtual void shutdown() = 0;
};

#endif
