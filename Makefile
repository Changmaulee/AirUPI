# Project Brahmand: Zero-Dependency Makefile
CXX ?= g++
CXXFLAGS = -std=c++17 -O3 -Wall -Wextra -Icpp_core

TARGET = brahmand
SRCS = cpp_core/main.cpp

all: $(TARGET)

$(TARGET): $(SRCS) cpp_core/*.hpp
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRCS)

benchmark: $(TARGET)
	./$(TARGET) --benchmark

clean:
	rm -f $(TARGET) $(TARGET).exe

wasm:
	em++ $(CXXFLAGS) -s WASM=1 -s ALLOW_MEMORY_GROWTH=1 -o brahmand.html $(SRCS)

.PHONY: all benchmark clean wasm
