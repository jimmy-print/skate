#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <glm/gtc/matrix_transform.hpp>

#include <vector>
#include <string>
#include <iostream>
#include <fstream>

#include <stdio.h>
#include <math.h>




#include <memory>
#include <string>
#include <stdexcept>

template<typename ... Args>
std::string string_format( const std::string& format, Args ... args )
{
	int size_s = std::snprintf( nullptr, 0, format.c_str(), args ... ) + 1; // Extra space for '\0'
	if( size_s <= 0 ){ throw std::runtime_error( "Error during formatting." ); }
	auto size = static_cast<size_t>( size_s );
	auto buf = std::make_unique<char[]>( size );
	std::snprintf( buf.get(), size, format.c_str(), args ... );
	return std::string( buf.get(), buf.get() + size - 1 ); // We don't want the '\0' inside
}

const int D_WIDTH = 1280;
const int D_HEIGHT = 720;
struct color {
	float r;
	float g;
	float b;
} typedef color;

color BLACK = {0.1, 0.1, 0.1};
color WHITE = {1, 1, 1};
color RED = {1, 0, 0};
color GREEN = {0, 1, 0};
color BLUE = {0, 0, 1};

std::string get_file_str(std::string file);

GLuint load_shader(std::string vs_filename, std::string fs_filename);

float rad(float degangle) {
	return degangle * (M_PI / 180);
}

float deg(float radangle) {
	return radangle * 180 / M_PI;
}

class Wector {
public:
	float magnitude;
	float direction;
};

class Velocity : public Wector {
public:
	Velocity(float speed, float directionp) {
		magnitude = speed;
		direction = directionp;
	}

	std::string repr() {
		return string_format("velocity %f px/s %f deg", magnitude, deg(direction));
	}
};

class Force : public Wector {
public:
	Force(float newtons, float directionp) {
		magnitude = newtons;
		direction = directionp;
	}

	std::string repr() {
		return string_format("force %f N %f deg", magnitude, deg(direction));
	}
};

template <typename T>
std::pair<float, float> get_xy_components(T wector) {
	std::pair<float, float> comp{
		cos(wector.direction) * wector.magnitude,
		sin(wector.direction) * wector.magnitude};
	return comp;
}

template <typename T>
T recombine(float x_mag, float y_mag) {
	float hypo = sqrt(x_mag * x_mag + y_mag * y_mag);
	return T(hypo, acos(x_mag / hypo));
}


float norm(float radangle) {
	float degangle = deg(radangle);
	if (degangle < 0) {
		while (degangle < 0) {
			degangle += 360;
		}
	} else if (degangle > 360) {
		while (degangle > 360) {
			degangle -= 360;
		}
	}
	return rad(degangle);
}

bool isclose(float n, float m, float abs_tol) {
	assert(abs_tol >= 0);
	if (abs(m - n) < abs_tol) {
		return true;
	}
	return false;
}

template <typename T>
T get_net_vector(T v0, T v1) {
	T v00(0, 0);
	T v11(0, 0);
	if (norm(v0.direction) <= norm(v1.direction)) {
		v00.magnitude = v0.magnitude;
		v00.direction = v0.direction;
		v11.magnitude = v1.magnitude;
		v11.direction = v1.direction;
	} else if (norm(v0.direction) > norm(v1.direction)) {
		v00.magnitude = v1.magnitude;
		v00.direction = v1.direction;
		v11.magnitude = v0.magnitude;
		v11.direction = v1.direction;
	}

	// simplify stupid logic
	if (isclose(v00.magnitude, 0, 0.001) || v00.magnitude > 0) {

	} else if (isclose(v11.magnitude, 0, 0.001) or v11.magnitude > 0) {

	} else if (v00.magnitude < 0 || v11.magnitude < 0) {
		throw "negative magnitudes not accepted, fix shit";
	}

	float a = v00.magnitude;
	float b = v11.magnitude;
	float gamma = rad(360) - (norm(v11.direction) + (rad(180) - norm(v00.direction)));

	float __ = pow(a, 2) + pow(b, 2) - 2 * a * b * cos(gamma);
	if (isclose(__, 0, 0.00000001)) {
		__ = 0;
	}
	float c = sqrt(__);

	if (v00.magnitude == 0) {
		return v11;
	} else if (v11.magnitude == 0) {
		return v00;
	}

	if (c == 0) {
		T net_force = T(c, 0);
		return net_force;
	}
	float thing_to_acos = (c * c + a * a - b * b) / (2 * a * c);
	if (thing_to_acos > 1) {
		thing_to_acos = 1;
	} else if (thing_to_acos < -1) {
		thing_to_acos = -1;
	}
	float new_direction = acos(thing_to_acos);
	if (gamma < 0) {
		new_direction = rad(360) - new_direction;
	}
	T net_force = T(c, norm(norm(v00.direction) + norm(new_direction)));
	return net_force;
}

Force get_net_force(std::vector<Force> forces) {
	Force tmp_f = forces[0];
	std::vector<Force> other_fs = std::vector<Force>(forces.begin() + 1, forces.end());
	for (auto f : other_fs) {
		tmp_f = get_net_vector(tmp_f, f);
	}
	return tmp_f;
}

class PointMass {
public:
	float x;
	float y;
	float mass;
	Velocity v = Velocity(0, 0);
	std::vector<Force> current_frm_forces;
	PointMass(float xp, float yp, float massp) {
		x = xp;
		y = yp;
		mass = massp;
	}

	void reset() {
		current_frm_forces = {};
	}

	void add_force(Force f) {
		current_frm_forces.push_back(f);
	}

	void tick() {
		Force net = get_net_force(current_frm_forces);
		float daccel = net.magnitude / mass;
		Velocity dv(daccel, net.direction);
		v = get_net_vector(v, dv);
		
		float dx = cos(v.direction) * v.magnitude;
		float dy = sin(v.direction) * v.magnitude;

		x += dx;
		y += dy;
	}

	std::vector<float> get_vs() {
		return std::vector<float> {x, y};
	}
};

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

	PointMass p(10, 10, 1);

	GLuint vao, vbo;
	glGenVertexArrays(1, &vao);
	glBindVertexArray(vao);
	glGenBuffers(1, &vbo);
	glBindBuffer(GL_ARRAY_BUFFER, vbo);
	glBufferData(GL_ARRAY_BUFFER, sizeof(p.get_vs()), &p.get_vs()[0], GL_STATIC_DRAW);
	glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(float), (void*) 0);
	glEnableVertexAttribArray(0);
	GLuint polygon_s = load_shader("polygon_vs", "polygon_fs");
	GLuint polygon_color_l = glGetUniformLocation(polygon_s, "color_l");
	GLuint polygon_mvp_l = glGetUniformLocation(polygon_s, "mvp_l");

	while (!glfwWindowShouldClose(window)) {
		glClearColor(BLACK.r, BLACK.g, BLACK.b, 1.0);
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

		glfwPollEvents();

		p.reset();
		p.add_force(Force(0.01, 0));
		p.tick();
		glBufferData(GL_ARRAY_BUFFER, sizeof(p.get_vs()), &p.get_vs()[0], GL_STATIC_DRAW);

		glUseProgram(polygon_s);
		glBindVertexArray(vao);
		glBindBuffer(GL_ARRAY_BUFFER, vbo);
		glPointSize(5);
		glDrawArrays(GL_POINTS, 0, 1);
		glUniform3f(polygon_color_l, WHITE.r, WHITE.g, WHITE.b);
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
