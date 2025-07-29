#ifndef NESTED_CONDITIONALS_HPP
#define NESTED_CONDITIONALS_HPP

#ifdef DEBUG
    #define LOG(x) printf(x)
#else
    #define LOG(x)
#endif

#if defined(PLATFORM_LINUX)
    #include <unistd.h>
    #define PLATFORM_NAME "Linux"
#elif defined(PLATFORM_WINDOWS)
    #include <windows.h>
    #define PLATFORM_NAME "Windows"
#else
    #define PLATFORM_NAME "Unknown"
#endif

class NestedConditionalsExample {
public:
    const char* getPlatform() { return PLATFORM_NAME; }
};

#endif // NESTED_CONDITIONALS_HPP
