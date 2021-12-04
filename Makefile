args = -lglfw3 -lGLEW -lGLU -lGL -lX11 -ldl -lpthread -lm
skate: main.cpp
	g++ -o skate main.cpp $(args)
