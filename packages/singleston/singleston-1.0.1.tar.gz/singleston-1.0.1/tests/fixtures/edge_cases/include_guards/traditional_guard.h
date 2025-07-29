#ifndef TRADITIONAL_GUARD_H
#define TRADITIONAL_GUARD_H

#include <vector>

class TraditionalGuardExample {
private:
    std::vector<int> data;
public:
    void addData(int value) { data.push_back(value); }
    size_t size() const { return data.size(); }
};

#endif // TRADITIONAL_GUARD_H
