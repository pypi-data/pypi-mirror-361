TARGET			:= simple_plugins.out
EXPORT_TARGET	:= simple_plugins_export.cpp
CXX				:= clang++
CXXFLAGS		:= -MMD -Wall -Wextra -Iinclude
SRCS			:= $(wildcard srcs/*.cpp)
OBJS			:= $(SRCS:%.cpp=%.o)
DEPS			:= $(OBJS:%.o=%.d)

all: $(TARGET) $(EXPORT_TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) $^ -o $@

$(EXPORT_TARGET): $(OBJS)
	python3 ../../scripts/singleston.py $(DEPS) -o $@

clean:
	rm -rf $(DEPS) $(EXPORT_TARGET) $(OBJS) $(TARGET)

re: clean all

run: $(NAME)
	./$<

-include $(DEPS)

.PHONY: all clean re run
