#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <glm/gtc/matrix_transform.hpp>

#include <vector>
#include <string>
#include <iostream>
#include <fstream>

#include <stdio.h>

const int D_WIDTH = 1280;
const int D_HEIGHT = 720;

struct color {
	float r;
	float g;
	float b;
} typedef color;

color BLACK = {0, 0, 0};
color WHITE = {255, 255, 255};
color RED = {255, 0, 0};
color GREEN = {0, 255, 0};
color BLUE = {0, 0, 255};

std::string get_file_str(std::string file);

GLuint load_shader(std::string vs_filename, std::string fs_filename);

int main()
{
	glfwInit();
#ifdef __APPLE__
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
	glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
#endif
	GLFWwindow *window = glfwCreateWindow(D_WIDTH, D_HEIGHT, "skate", 0, 0);
	glfwMakeContextCurrent(window);
#ifdef __APPLE__
	glewExperimental = GL_TRUE;
#endif
	glewInit();

	glm::mat4 projection_m = glm::ortho(0.0f, (float) D_WIDTH, 0.0f, (float) D_HEIGHT);
	glm::vec3 position_v = glm::vec3(0, 0, 1);
	glm::mat4 view_m = glm::lookAt(position_v, glm::vec3(0, 0, 0), glm::vec3(0, 1, 0));
	glm::mat4 model_m = glm::mat4(1.0f);
	glm::mat4 mvp_m = projection_m * view_m * model_m;

	std::vector<float> vs = {
		25.0, 50.0,
		90.0, 50.0
	};
	GLuint vao, vbo;
	glGenVertexArrays(1, &vao);
	glBindVertexArray(vao);
	glGenBuffers(1, &vbo);
	glBindBuffer(GL_ARRAY_BUFFER, vbo);
	glBufferData(GL_ARRAY_BUFFER, sizeof(vs), &vs[0], GL_STATIC_DRAW);
	glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(float), (void*) 0);
	glEnableVertexAttribArray(0);
	GLuint polygon_s = load_shader("polygon_vs", "polygon_fs");
	GLuint polygon_color_l = glGetUniformLocation(polygon_s, "color_l");
	GLuint polygon_mvp_l = glGetUniformLocation(polygon_s, "mvp_l");

	while (!glfwWindowShouldClose(window)) {
		glClearColor(0.0, 0.0, 0.0, 1.0);
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

		glfwPollEvents();

		glUseProgram(polygon_s);
	        glBindVertexArray(vao);
		glBindBuffer(GL_ARRAY_BUFFER, vbo);
		glDrawArrays(GL_LINES, 0, 4);
		glUniform3f(polygon_color_l, RED.r, RED.g, RED.b);
		glUniformMatrix4fv(polygon_mvp_l, 1, GL_FALSE, &mvp_m[0][0]);

		glfwSwapBuffers(window);
	}
	return 0;
}

GLuint load_shader(std::string vs_filename, std::string fs_filename)
{
	const char *vs_cstr;
	const char *fs_cstr;
	std::string vs_str = get_file_str(vs_filename);
	std::string fs_str = get_file_str(fs_filename);
	vs_cstr = vs_str.c_str();
	fs_cstr = fs_str.c_str();

	GLuint program;

	program = glCreateProgram();

	GLuint vs, fs;
	vs = glCreateShader(GL_VERTEX_SHADER);
	glShaderSource(vs, 1, &vs_cstr, NULL);
	glCompileShader(vs);

	fs = glCreateShader(GL_FRAGMENT_SHADER);
	glShaderSource(fs, 1, &fs_cstr, NULL);
	glCompileShader(fs);

	// Check for errors
	GLint vs_success, fs_success;
	vs_success = 0;
	fs_success = 0;
	glGetShaderiv(vs, GL_COMPILE_STATUS, &vs_success);
	glGetShaderiv(fs, GL_COMPILE_STATUS, &fs_success);

	if (vs_success == GL_FALSE) {
		GLint vs_max_len;
		glGetShaderiv(vs, GL_INFO_LOG_LENGTH, &vs_max_len);
		std::vector<GLchar> vs_error_log(vs_max_len);
		glGetShaderInfoLog(vs, vs_max_len, &vs_max_len, &vs_error_log[0]);

		std::cout << "ERROR: Vertex shader compilation\n";
		for (auto c : vs_error_log) {
			std::cout << c;
		}
		std::cout << "\n";
	}
	if (fs_success == GL_FALSE) {
		GLint fs_max_len;
		glGetShaderiv(fs, GL_INFO_LOG_LENGTH, &fs_max_len);
		std::vector<GLchar> fs_error_log(fs_max_len);
		glGetShaderInfoLog(fs, fs_max_len, &fs_max_len, &fs_error_log[0]);

		std::cout << "ERROR: Fragment shader compilation\n";
		for (auto c : fs_error_log) {
			std::cout << c;
		}
	}

	glAttachShader(program, vs);
	glAttachShader(program, fs);
	glLinkProgram(program);
	glValidateProgram(program);

	glDeleteShader(vs);
	glDeleteShader(fs);

	return program;
}

std::string get_file_str(std::string file)
{
	std::ifstream f(file);
	if (f.fail()) {
		std::cout << file << " opening failed\n";
	}
	std::string s((std::istreambuf_iterator<char>(f)),
		      (std::istreambuf_iterator<char>()));
	return s;
}
