args = `pkg-config --cflags --libs freetype2` -I. -lglfw3 -lGLEW -lGLU -lGL -lX11 -ldl -lpthread -lm
all: skate
skate: main.cpp text.cpp
	g++ -o skate main.cpp text.cpp $(args) -std=c++17 -g
