#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <glm/gtc/matrix_transform.hpp>

#include <vector>
#include <string>
#include <iostream>
#include <fstream>
#include <memory>
#include <string>
#include <stdexcept>
#include <numeric>

#include <stdio.h>
#include <math.h>

const std::string LEFT = "LEFT";
const std::string CENT = "CENT";
const std::string RIGH = "RIGH";


std::vector<struct aes_wector> wectors_aess;

const int stage_width = 1300;
const int stage_height = 600;

struct color {
	float r;
	float g;
	float b;
} typedef color;

struct aes_wector {
	std::pair<float, float> start;
	std::pair<float, float> end;
	struct color color;  // why omit struct for 'color color' throws error?? if struct color has already been typedefed
};

void print_array(std::vector<float> v)
{
	for (std::vector<float>::const_iterator i = v.begin(); i != v.end(); i++)
		std::cout << *i << " ";
	std::cout << "\n";
}

template <typename T>
struct aes_wector calc_wector_data_struct(T wector, float x, float y, color color, float display_multiply_factor);

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

void draw_poly(GLuint shader, GLuint VAO, GLuint VBO, std::vector<float> vs, GLuint primitive, int indices, GLuint mvp_l, glm::mat4 mvp);

const int D_WIDTH = 1500;
const int D_HEIGHT = 700;

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
// may be broken... don't use
	float hypo = sqrt(x_mag * x_mag + y_mag * y_mag);
	if (hypo != 0) {
	    return T(hypo, acos(x_mag / hypo));
	} else {
	    return T(hypo, 0);
	}
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
		v11.direction = v0.direction;
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
	if (forces.size() == 0) {
		return Force(0, 0);
	}

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

class PointMassOnLine : public PointMass {
public:
	float horzd;
	float rotational_inertia;
	Velocity* rot_velocity_ptr;
	PointMassOnLine(PointMass axle, float horzdp, float massp) : PointMass(axle.x + horzdp, axle.y, massp) {
		horzd = horzdp;
		rotational_inertia = mass * pow(horzd, 2);
	}
};

class Line {
public:
	float wheels_horz_d;
	float length;
	PointMass* axle;
	std::vector<PointMassOnLine*> points;
	PointMassOnLine* leftmost;
	PointMassOnLine* rightmost;

	float angle_r;
	float angular_accel_r;
	float angular_speed_r;

	float rotational_inertia;

	float mass;

	std::string axle_loc;

	Line(PointMass* axlep,
	     std::vector<PointMassOnLine*> pointsp,
	     float wheels_horz_dp,
	     float lengthp) {
		length = lengthp;
		axle = axlep;
		wheels_horz_d = wheels_horz_dp;

		// todo assert all same points.ys
		// todo assert all diff points.xs

        points = pointsp;

        PointMassOnLine* smallest = points[0];
        for (auto point : points) {
            if (point->x < smallest->x) {
                smallest = point;
            }
        }
		leftmost = smallest;
		PointMassOnLine* largest = points[0];
        for (auto point : points) {
            if (point->x > smallest->x) {
                largest = point;
            }
        }
		rightmost = largest;

		angle_r = 0;
		angular_accel_r = 0;
		angular_speed_r = 0;

		rotational_inertia = std::accumulate(points.begin(), points.end(), 0.0, [&](float x, PointMassOnLine* y) {return x + y->rotational_inertia;});
		mass = std::accumulate(points.begin(), points.end(), 0.0,  [&](float x, PointMassOnLine* y) {return x + y->mass;});
		axle_loc = LEFT;
	}

	void apply_force(Force force, int distance_from_axle_on_line, color color) {
		if (distance_from_axle_on_line == 0) {
			Velocity dv(force.magnitude / mass, force.direction);
			axle->v = get_net_vector<Velocity>(axle->v, dv);
		} else {
			float torque = force.magnitude * distance_from_axle_on_line * sin(force.direction - angle_r);
			angular_accel_r = torque / rotational_inertia;
			angular_speed_r += angular_accel_r;
		}
	}

	void tick() {
		angle_r += angular_speed_r;
		if (deg(angle_r) > 360) {
			angle_r = rad(deg(angle_r) - 360);  // simplify this to something to do with pi instead of changing it to rad deg back and forth
		}
		axle->tick();
		for (auto point : points) {
			if (point->horzd > 0) {
				if (angular_speed_r > 0)
					point->v = Velocity(point->horzd * angular_speed_r, angle_r + rad(90));
				else if (angular_speed_r < 0)
					point->v = Velocity(abs(point->horzd) * abs(angular_speed_r), angle_r + rad(270));
				else
					point->v = Velocity(0, 0);
			} else if (point->horzd < 0) {
				if (angular_speed_r > 0)
					point->v = Velocity(abs(point->horzd) * angular_speed_r, angle_r + rad(270));
				else if (angular_speed_r < 0)
					point->v = Velocity(abs(point->horzd) * abs(angular_speed_r), angle_r + rad(90));
				else
					point->v = Velocity(0, 0);
			}
			point->rot_velocity_ptr = &point->v;

		    wectors_aess.push_back(calc_wector_data_struct(point->v, point->x, point->y, WHITE, 20));
            wectors_aess.push_back(calc_wector_data_struct(axle->v, axle->x, axle->y, RED, 20));
            std::cout << "point velocity::magnitude: " << point->v.magnitude << " ,direction: " << deg(point->v.direction) << "\n";
			Velocity v = get_net_vector<Velocity>(point->v, axle->v);
             wectors_aess.push_back(calc_wector_data_struct(v, point->x, point->y, GREEN, 20));
			if (axle->v.magnitude != 0) {
				// draw vector
			}
			point->v = v;
			point->tick();
		}
	}

	void draw(GLuint shader, GLuint VAO, GLuint VBO, GLuint mvp_l, glm::mat4 mvp) {
		std::vector<float> leftmostvs = {leftmost->x, leftmost->y, 1.0, 1.0, 1.0, 1.0};
		std::vector<float> rightmostvs = {rightmost->x, rightmost->y, 1.0, 0.0, 1.0, 1.0};
		std::vector<float> axlevs = {axle->x, axle->y, 1.0, 1.0, 0.0, 1.0};

		//print_array(axlevs);
		//print_array(leftmostvs);


		draw_poly(shader, VAO, VBO, leftmostvs, GL_POINTS, 1, mvp_l, mvp);
		draw_poly(shader, VAO, VBO, rightmostvs, GL_POINTS, 1, mvp_l, mvp);
		draw_poly(shader, VAO, VBO, axlevs, GL_POINTS, 1, mvp_l, mvp);

        draw_poly(shader, VAO, VBO, {
            leftmost->x, leftmost->y, 1.0, 1.0, 1.0, 1.0,
            axle->x, axle->y, 1.0, 1.0, 1.0, 1.0}, GL_LINES, 2, mvp_l, mvp);

        draw_poly(shader, VAO, VBO, {
            rightmost->x, rightmost->y, 1.0, 1.0, 1.0, 1.0,
            axle->x, axle->y, 1.0, 1.0, 1.0, 1.0}, GL_LINES, 2, mvp_l, mvp);
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

	GLuint pvao, pvbo;
	glGenVertexArrays(1, &pvao);
	glBindVertexArray(pvao);
	glGenBuffers(1, &pvbo);
	glBindBuffer(GL_ARRAY_BUFFER, pvbo);
	glBufferData(GL_ARRAY_BUFFER, sizeof(p.get_vs()), &p.get_vs()[0], GL_STATIC_DRAW);
	glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(float), (void*) 0);
	glEnableVertexAttribArray(0);
	GLuint polygon_s = load_shader("polygon_vs", "polygon_fs");
	GLuint polygon_color_l = glGetUniformLocation(polygon_s, "color_l");
	GLuint polygon_mvp_l = glGetUniformLocation(polygon_s, "mvp_l");


	GLuint wectors_vao, wectors_vbo;
	glGenVertexArrays(1, &wectors_vao);
	glBindVertexArray(wectors_vao);
	glGenBuffers(1, &wectors_vbo);
	glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*) 0);
	glEnableVertexAttribArray(0);
	glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*) (2 * sizeof(float)));
	glEnableVertexAttribArray(1);
	GLuint wectors_s = load_shader("wectors_vs", "wectors_fs");
	GLuint wectors_mvp_l = glGetUniformLocation(wectors_s, "mvp_l");


	float wheel_radius = 12;

	float init_axle_x = 100;
	float init_axle_y = 500;
	PointMass axle(init_axle_x, init_axle_y, 10);
	float length = 300;
	float wheels_horz_d = 50;
	PointMassOnLine leftmost(axle, length - wheels_horz_d, 20); // wtf why does this have to be a variable???? or else you get different values inside the class constructor for line when passed as a ptr..
	PointMassOnLine rightmost(axle, -wheels_horz_d, 20);
    std::vector<PointMassOnLine*> points = {&leftmost, &rightmost};
	Line l(&axle, points, wheels_horz_d, length);

	GLuint poly_VAO, poly_VBO;
	glGenVertexArrays(1, &poly_VAO);
	glGenVertexArrays(1, &poly_VBO);
	GLuint poly_shader = load_shader("poly_vs", "poly_fs");
	GLuint poly_mvp_l = glGetUniformLocation(poly_shader, "mvp");
	glPointSize(5);


    l.apply_force(Force(100.0, rad(270)), l.rightmost->horzd, WHITE);
    l.tick();
    int i = 0;

	while (!glfwWindowShouldClose(window)) {
	    i++;
		glClearColor(BLACK.r, BLACK.g, BLACK.b, 1.0);
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

		glfwPollEvents();

		wectors_aess = {};

        l.apply_force(Force(1, rad(0)), 0, BLUE);
		l.tick();
		l.draw(poly_shader, poly_VAO, poly_VBO, poly_mvp_l, mvp_m);

		p.reset();
		p.add_force(Force(0.01, 0));
		p.add_force(Force(0.01, rad(90)));
		p.tick();

		wectors_aess.push_back(calc_wector_data_struct(p.v, p.x, p.y, WHITE, 20));
		wectors_aess.push_back(calc_wector_data_struct(Force(0.01, 0), p.x, p.y, RED, 1000));
		wectors_aess.push_back(calc_wector_data_struct(Force(0.01, rad(90)), p.x, p.y, RED, 1000));

		std::vector<float> wectors_dat;
		for (auto struc : wectors_aess) {
			wectors_dat.push_back(struc.start.first);
			wectors_dat.push_back(struc.start.second);

			wectors_dat.push_back(struc.color.r);
			wectors_dat.push_back(struc.color.g);
			wectors_dat.push_back(struc.color.b);

			wectors_dat.push_back(struc.end.first);
			wectors_dat.push_back(struc.end.second);

			wectors_dat.push_back(struc.color.r);
			wectors_dat.push_back(struc.color.g);
			wectors_dat.push_back(struc.color.b);
		}

		glUseProgram(wectors_s);
		glBindVertexArray(wectors_vao);
		glBindBuffer(GL_ARRAY_BUFFER, wectors_vbo);
		glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*) 0);
		glEnableVertexAttribArray(0);
		glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*) (2 * sizeof(float)));
		glEnableVertexAttribArray(1);
		glBufferData(GL_ARRAY_BUFFER, sizeof(float) * wectors_dat.size(), &wectors_dat[0], GL_STATIC_DRAW);
		glDrawArrays(GL_LINES, 0, wectors_aess.size() * 2);
		glUniformMatrix4fv(wectors_mvp_l, 1, GL_FALSE, &mvp_m[0][0]);

		glUseProgram(polygon_s);
		glBindVertexArray(pvao);
		glBindBuffer(GL_ARRAY_BUFFER, pvbo);
		glBufferData(GL_ARRAY_BUFFER, sizeof(p.get_vs()), &p.get_vs()[0], GL_STATIC_DRAW);
		glDrawArrays(GL_POINTS, 0, 1);
		glUniform3f(polygon_color_l, GREEN.r, GREEN.g, GREEN.b);
		glUniformMatrix4fv(polygon_mvp_l, 1, GL_FALSE, &mvp_m[0][0]);

		glfwSwapBuffers(window);
	}
	return 0;
}

template <typename T>
struct aes_wector calc_wector_data_struct(T wector, float x, float y, color color, float display_multiply_factor) {
	float draw_mag = wector.magnitude * display_multiply_factor;

	struct aes_wector aes;

	aes.start.first = x;
	aes.start.second = y;
	aes.end.first = x + cos(wector.direction) * draw_mag;
	aes.end.second = y + sin(wector.direction) * draw_mag;

	aes.color = color;

	return aes;

// todo add text shit into aes struct
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

void draw_poly(GLuint shader, GLuint VAO, GLuint VBO, std::vector<float> vs, GLuint primitive, int indices, GLuint mvp_l, glm::mat4 mvp)
{
	glUseProgram(shader);
	glBindVertexArray(VAO);
	glBindBuffer(GL_ARRAY_BUFFER, VBO);
	glBufferData(GL_ARRAY_BUFFER, vs.size() * sizeof(float), &vs[0], GL_STATIC_DRAW);
	glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*) 0);
	glEnableVertexAttribArray(0);
	glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*) (2 * sizeof(float)));
	glEnableVertexAttribArray(1);
	glDrawArrays(primitive, 0, indices);
	glUniformMatrix4fv(mvp_l, 1, GL_FALSE, &mvp[0][0]);
}
