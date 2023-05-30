args = `pkg-config --cflags --libs freetype2` -I. -lglfw3 -lGLEW -lGLU -lGL -lX11 -ldl -lpthread -lm
all: skate
skate: main.cpp text.cpp
	g++ -o skate main.cpp text.cpp $(args) -std=c++17 -g

skatemacos: main.cpp text.cpp
	g++ -o skate main.cpp text.cpp `pkg-config --cflags --libs glfw3 glew freetype2` -framework OpenGL -g -std=c++17 -I.
