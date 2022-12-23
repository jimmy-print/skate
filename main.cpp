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
#include <map>

#include <stdio.h>
#include <math.h>
#include <utils.h>
#include <text.h>

// todo fix naming with horz, horzd, horz_d

const std::string LEFT = "LEFT";
const std::string CENT = "CENT";
const std::string RIGH = "RIGH";

const std::string LEFTWHEEL = "LEFTWHEEL";
const std::string RIGHTWHEEL = "RIGHTWHEEL";


std::vector<struct aes_wector> wectors_aess;

const int stage_width = 1300;
const int stage_height = 600;

const float g_accel = 0.4;
float wheel_radius = 12;

struct color {
	float r;
	float g;
	float b;
} typedef color;

#define EXP_COLOR(color)			\
	color.r, color.g, color.b, 1.0

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

void draw_poly(GLuint shader, GLuint VAO, GLuint VBO, std::vector<float> vs, GLuint primitive, int indices, GLuint mvp_l, glm::mat4 mvp);


color BLACK = {0, 0, 0};
color WHITE = {1, 1, 1};
color RED = {1, 0, 0};
color GREEN = {0, 1, };
color BLUE = {0, 0, 1};

color rgb_py_to_gl(float r, float g, float b) {
	return (color) {r / 255, g / 255, b / 255};
}
color DARKGREY = rgb_py_to_gl(25, 25, 25);
color KINDA_DARK_GREY = rgb_py_to_gl(40, 40, 40);
color CYAN = rgb_py_to_gl(0, 255, 255);

std::string get_file_str(std::string file);

GLuint load_shader(std::string vs_filename, std::string fs_filename);

float rad(float degangle) {
	return degangle * (M_PI / 180);
}

float deg(float radangle) {
	return radangle * 180 / M_PI;
}

bool close(float n, float m, float min_diff=3) {
	return abs(n - m) <= min_diff;
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
//
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

	void maintain_axle(std::string new_axle_loc) {
		if (new_axle_loc == axle_loc) {
			return;
		}

		axle_loc = new_axle_loc;

		if (axle_loc == CENT) {
			axle->x = leftmost->x + cos(angle_r) * length / 2;
			axle->y = leftmost->y + sin(angle_r) * length / 2;

			// todo rm these repetitions
			leftmost->horzd = -1 * length / 2;
			leftmost->rotational_inertia = leftmost->mass * pow(leftmost->horzd, 2);
			leftmost->x = axle->x + leftmost->horzd;
			leftmost->y = axle->y;
			leftmost->mass = leftmost->mass;

			rightmost->horzd = length / 2;
			rightmost->rotational_inertia = rightmost->mass * pow(rightmost->horzd, 2);
			leftmost->x = axle->x + rightmost->horzd;
			leftmost->y = axle->y;
			leftmost->mass = rightmost->mass;
		} else if (axle_loc == LEFT) {
			axle->x = leftmost->x + cos(angle_r) * wheels_horz_d;
			axle->y = leftmost->y + sin(angle_r) * wheels_horz_d;

			leftmost->horzd = -1 * wheels_horz_d;
			leftmost->rotational_inertia = leftmost->mass * pow(leftmost->horzd, 2);
			leftmost->x = axle->x + leftmost->horzd;
			leftmost->y = axle->y;
			leftmost->mass = leftmost->mass;

			rightmost->horzd = length - wheels_horz_d;
			rightmost->rotational_inertia = rightmost->mass * pow(rightmost->horzd, 2);
			leftmost->x = axle->x + rightmost->horzd;
			leftmost->y = axle->y;
			leftmost->mass = rightmost->mass;

		} else if (axle_loc == RIGH) {
			axle->x = leftmost->x + cos(angle_r) * (length - wheels_horz_d);
			axle->y = leftmost->y + sin(angle_r) * (length - wheels_horz_d);

			leftmost->horzd = -(length - wheels_horz_d);
			leftmost->rotational_inertia = leftmost->mass * pow(leftmost->horzd, 2);
			leftmost->x = axle->x + leftmost->horzd;
			leftmost->y = axle->y;
			leftmost->mass = leftmost->mass;

			rightmost->horzd = wheels_horz_d;
			rightmost->rotational_inertia = rightmost->mass * pow(rightmost->horzd, 2);
			leftmost->x = axle->x + rightmost->horzd;
			leftmost->y = axle->y;
			leftmost->mass = rightmost->mass;
		}

		leftmost->x = axle->x + cos(angle_r) * leftmost->horzd;
		leftmost->y = axle->y + sin(angle_r) * leftmost->horzd;

		rightmost->x = axle->x + cos(angle_r) * rightmost->horzd;
		rightmost->y = axle->y + sin(angle_r) * rightmost->horzd;

		points = {leftmost, rightmost};
                rotational_inertia = std::accumulate(points.begin(), points.end(), 0.0, [&](float x, PointMassOnLine* y) {return x + y->rotational_inertia;});
	}

	void sticky() {
		angular_speed_r *= 0.7;
   	}

   	void raise_uniformwise(float dy) {
		for (auto point : points) {
			point->y += dy;
		}
		axle->y += dy;
   	}

   	void push_left_uniformwise(float dx) {
		// the += and left seems to be wrong (after translating from python)
		// but just keep it for now, because changing these things during translation is probably
		// more complexity for no immediate gain
		for (auto point : points) {
			point->x += dx;
		}
		axle->x += dx;
   	}
};

bool skateboard_is_in_contact_with_ground(
        float left_wheel_center_y, float right_wheel_center_y,
        float radius_of_both_wheels, float ground_y) {
	if (left_wheel_center_y - radius_of_both_wheels <= ground_y) {
		return true;
	} else if (right_wheel_center_y - radius_of_both_wheels <= ground_y) {
		return true;
	}
	return false;
}


std::map<char, bool> perrier;
std::vector<char> perrier_implemented_keys = {'d', 'a', 'c', 'z'};  // there's no mechanism to guarantee that these are the keys
// that are actually implemented in the below key_callback function or in the main game loop.
// This is only for the reset function.

void reset_perrier() {
	// goes at the beginning of the game loop, before glfwPollEvents();.
	for (auto key : perrier_implemented_keys) {
		perrier[key] = false;
	}
}

void key_callback(GLFWwindow *window, int key, int scancode, int action, int mods) {
	if (action == GLFW_PRESS) {
		switch(key) {

		case GLFW_KEY_D:
			perrier['d'] = true;
			break;
		case GLFW_KEY_A:
			perrier['a'] = true;
			break;
		case GLFW_KEY_C:
			perrier['c'] = true;
			break;
		case GLFW_KEY_Z:
			perrier['z'] = true;
			break;
		}
	}
}


int main() {
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

	glfwSetKeyCallback(window, key_callback);

	std::map<char, glyph> glyphs = init_glyphs("inconsolata.ttf");
	configure_blending();
	GLuint text_VAO, text_VBO;
	get_vao_vbo(&text_VAO, &text_VBO);
	glm::mat4 text_mvp = get_mvp();
	GLuint text_shader;
	GLuint text_mvp_l, text_color_l;
	get_shader("text_vs", "text_fs", &text_shader, &text_mvp_l, &text_color_l);
//    void dtext()


	glm::mat4 projection_m = glm::ortho(0.0f, (float) D_WIDTH, 0.0f, (float) D_HEIGHT);
	glm::vec3 position_v = glm::vec3(0, 0, 1);
	glm::mat4 view_m = glm::lookAt(position_v, glm::vec3(0, 0, 0), glm::vec3(0, 1, 0));
	glm::mat4 model_m = glm::mat4(1.0f);
	glm::mat4 mvp_m = projection_m * view_m * model_m;

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



	float ground_y = 50 + (D_HEIGHT - stage_height);

	float init_axle_x = 50;
	float init_axle_y = ground_y + wheel_radius * 5;
	PointMass axle(init_axle_x, init_axle_y, 10);
	float length = 250;
	float wheels_horz_d = 50;
	PointMassOnLine leftmost(axle, length - wheels_horz_d, 20); // wtf why does this have to be a variable???? or else you get different values inside the class constructor for line when passed as a ptr..
	PointMassOnLine rightmost(axle, -wheels_horz_d, 20);
	std::vector<PointMassOnLine*> points = {&leftmost, &rightmost};
	Line l(&axle, points, wheels_horz_d, length);

	float total_horz = abs(l.leftmost->horzd) + l.rightmost->horzd;

	GLuint poly_VAO, poly_VBO;
	glGenVertexArrays(1, &poly_VAO);
	glGenVertexArrays(1, &poly_VBO);
	GLuint poly_shader = load_shader("poly_vs", "poly_fs");
	GLuint poly_mvp_l = glGetUniformLocation(poly_shader, "mvp");
	glPointSize(5);

	int i = 0;

	bool pausing_this_frm;

	double mouse_x, mouse_y;

#define DTEXT(text, x, y, scale, r, g, b)				\
	do {								\
		draw_text(text, x, y, scale, r, g, b, glyphs, text_VAO, text_VBO, text_mvp, text_shader, text_mvp_l, text_color_l); \
	} while (0)

	float recording_area_height = D_HEIGHT - stage_height;
	int num_of_actions = 6;
	float each_bar_height = recording_area_height / num_of_actions;

	float left_wheel_center_y = 0;
	float right_wheel_center_y = 0;

	while (!glfwWindowShouldClose(window)) {
		i++;
		glClearColor(BLACK.r, BLACK.g, BLACK.b, 1.0);
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

		reset_perrier();

		glfwPollEvents();

		wectors_aess = {};


		pausing_this_frm = false;

		glfwGetCursorPos(window, &mouse_x, &mouse_y);

		draw_poly(poly_shader, poly_VAO, poly_VBO, {
				0, 0 + (D_HEIGHT - stage_height), EXP_COLOR(KINDA_DARK_GREY),
				0, 0, EXP_COLOR(KINDA_DARK_GREY),
				D_WIDTH, 0, EXP_COLOR(KINDA_DARK_GREY),
				D_WIDTH, 0 + (D_HEIGHT - stage_height), EXP_COLOR(KINDA_DARK_GREY)
			}, GL_QUADS, 4, poly_mvp_l, mvp_m);

		/*
		  int state = glfwGetKey(window, GLFW_KEY_D);
		  if (state == GLFW_PRESS) {
		  std::cout << "D pressed type2\n";
		  }
		*/
		if (skateboard_is_in_contact_with_ground(left_wheel_center_y, right_wheel_center_y, wheel_radius, ground_y)) {
			if (perrier['d']) {
				l.apply_force(Force(100, rad(0)), 0, WHITE);
			}
			if (perrier['a']) {
				l.apply_force(Force(-100, rad(0)), 0, WHITE);
			}
		}

		bool shift_held = (glfwGetKey(window, GLFW_KEY_LEFT_SHIFT) == GLFW_PRESS) || (glfwGetKey(window, GLFW_KEY_RIGHT_SHIFT) == GLFW_PRESS);

		if (perrier['c'] && !shift_held) {
			l.apply_force(Force(150, l.angle_r + rad(270)), l.rightmost->horzd, WHITE);
		}

		if (perrier['z'] && !shift_held) {
			l.apply_force(Force(150, l.angle_r + rad(270)), l.leftmost->horzd, WHITE);
		}

		if (perrier['c'] && shift_held) {
			l.maintain_axle(RIGH);
			l.apply_force(Force(4000, rad(270)), l.rightmost->horzd, WHITE);
		}
		if (perrier['z'] && shift_held) {
			l.maintain_axle(LEFT);
			l.apply_force(Force(4000, rad(270)), l.leftmost->horzd, WHITE);
		}

		// when text is rendered with opengl, the coordinates provided are the x y values of the
		// lower left corner of the text. but in pygame the coordinates provided are the
		// upper left corner. I've not modified the draw_text function to account for this,
		// so here I manually add a magic number offset.
		int offset = 12;
		DTEXT("Push down left side (z)", 10, D_HEIGHT - (stage_height + offset), 1.0, 1.0, 1.0, 1.0);
		DTEXT("Push down right side (c)", 10, D_HEIGHT - (stage_height + offset) - 1 * each_bar_height, 1.0, 1.0, 1.0, 1.0);
		DTEXT("Pop left side (shift+z)", 10, D_HEIGHT - (stage_height + offset) - 2 * each_bar_height, 1.0, 1.0, 1.0, 1.0);
		DTEXT("Pop right side (shift+c)", 10, D_HEIGHT - (stage_height + offset) - 3 * each_bar_height, 1.0, 1.0, 1.0, 1.0);
		DTEXT("Move left (a)", 10, D_HEIGHT - (stage_height + offset) - 4 * each_bar_height, 1.0, 1.0, 1.0, 1.0);
		DTEXT("Move left (d)", 10, D_HEIGHT - (stage_height + offset) - 5 * each_bar_height, 1.0, 1.0, 1.0, 1.0);



		// TODO make color struct support transparency and then change this macro
		// TODO render consistent how color is handled



		l.apply_force(Force(g_accel * l.mass, rad(270)), 0, WHITE);
		float center_x = l.leftmost->x + cos(l.angle_r - rad(15)) * wheels_horz_d;
		float center_y = (l.leftmost->y + sin(l.angle_r - rad(15)) * wheels_horz_d);
		left_wheel_center_y = center_y;
		right_wheel_center_y = (center_y + sin(l.angle_r) * (total_horz - wheels_horz_d * 2));
		float left_wheel_center_x = center_x;
		float right_wheel_center_x = (center_x + cos(l.angle_r) * (total_horz - wheels_horz_d * 2));

		float left_wheel_base_y = left_wheel_center_y - wheel_radius;
		// no LEFTWHEEL or RIGHTWHEEL
		float right_wheel_base_y = right_wheel_center_y - wheel_radius;
		if (skateboard_is_in_contact_with_ground(left_wheel_center_y, right_wheel_center_y, wheel_radius, ground_y)) {
			l.apply_force(Force(g_accel * l.mass, rad(90)), 0, WHITE);


			float x_component = get_xy_components(l.axle->v).first;
			if (x_component > 0) {
				l.axle->v = Velocity(x_component, 0);
			} else if (x_component < 0) {
				l.axle->v = Velocity(abs(x_component), rad(180));
			} else if (x_component == 0) {
				l.axle->v = Velocity(0, 0);
			}

			if (!close(deg(l.angle_r), 0, 1.3)) {
				l.apply_force(Force(g_accel * l.leftmost->mass, rad(270)), l.leftmost->horzd, WHITE);
				l.apply_force(Force(g_accel * l.rightmost->mass, rad(270)), l.rightmost->horzd, WHITE);
			} else {
				l.sticky();
			}

			if (std::min(left_wheel_base_y, right_wheel_base_y) == left_wheel_base_y) {
				l.maintain_axle(LEFT);
			} else if (std::min(left_wheel_base_y, right_wheel_base_y) == right_wheel_base_y) {
				l.maintain_axle(RIGH);
			}

			float d = ground_y - std::min(left_wheel_base_y, right_wheel_base_y);
			l.raise_uniformwise(d - 1);
		}

		if (l.leftmost->y < ground_y && l.axle_loc == LEFT && abs(l.angular_speed_r) > 0) {
			Velocity paradox = l.rightmost->v;
			Velocity wittgensteinpopper = l.leftmost->v;
			Velocity watchtower = l.axle->v;

			l.maintain_axle(CENT);
			l.angular_speed_r = 0;
			l.apply_force(Force(wittgensteinpopper.magnitude * l.mass, wittgensteinpopper.direction + rad(180)), 0, WHITE);
			l.apply_force(Force(watchtower.magnitude * l.mass, watchtower.direction), 0, CYAN);
			l.apply_force(Force(l.mass * paradox.magnitude / 4, paradox.direction), l.rightmost->horzd, WHITE);
			l.apply_force(Force(wittgensteinpopper.magnitude * 0.2 * l.mass, rad(90)), 0, WHITE);
		}
		if (l.rightmost->y < ground_y && l.axle_loc == RIGH && abs(l.angular_speed_r) > 0) {
			Velocity paradox = l.leftmost->v;
			Velocity wittgensteinpopper = l.rightmost->v;
			Velocity watchtower = l.axle->v;

			l.maintain_axle(CENT);
			l.angular_speed_r = 0;
			l.apply_force(Force(wittgensteinpopper.magnitude * l.mass, wittgensteinpopper.direction + rad(180)), 0, WHITE);
			l.apply_force(Force(watchtower.magnitude * l.mass, watchtower.direction), 0, CYAN);
			l.apply_force(Force(l.mass * paradox.magnitude / 4, paradox.direction), l.leftmost->horzd, WHITE);
			l.apply_force(Force(wittgensteinpopper.magnitude * 0.2 * l.mass, rad(90)), 0, WHITE);
		}
		if (l.leftmost->y < ground_y && l.axle_loc == CENT && get_xy_components(l.axle->v).second < 0) {
			float x_component = get_xy_components(l.axle->v).first;

			if (x_component > 0) {
				l.axle->v = Velocity(x_component, 0);
			} else if (x_component < 0) {
				l.axle->v = Velocity(abs(x_component), rad(180));
			} else if (x_component == 0) {
				l.axle->v = Velocity(0, 0);
			}
			l.apply_force(Force(l.mass * l.leftmost->v.magnitude, rad(90)), l.leftmost->horzd, WHITE);
			l.raise_uniformwise(ground_y - l.leftmost->y);
			l.raise_uniformwise(5);
		}
		if (l.rightmost->y < ground_y && l.axle_loc == CENT && get_xy_components(l.axle->v).second < 0) {
			float x_component = get_xy_components(l.axle->v).first;

			if (x_component > 0) {
				l.axle->v = Velocity(x_component, 0);
			} else if (x_component < 0) {
				l.axle->v = Velocity(abs(x_component), rad(180));
			} else if (x_component == 0) {
				l.axle->v = Velocity(0, 0);
			}
			l.apply_force(Force(l.mass * l.rightmost->v.magnitude, rad(90)), l.rightmost->horzd, WHITE);
			l.raise_uniformwise(ground_y - l.rightmost->y);
			l.raise_uniformwise(5);
		}

		if (l.leftmost->x < 0) {
			float y_component = get_xy_components(l.axle->v).second;

			if (y_component > 0) {
				l.axle->v = Velocity(y_component, rad(90));
			} else if (y_component < 0) {
				l.axle->v = Velocity(abs(y_component), rad(270));
			} else if (y_component == 0) {
				l.axle->v = Velocity(0, 0);
			}
			l.apply_force(Force(l.mass * l.leftmost->v.magnitude, rad(0)), l.leftmost->horzd, CYAN);
			l.push_left_uniformwise(5);
		}
		if (l.rightmost->x < 0) {
			float y_component = get_xy_components(l.axle->v).second;

			if (y_component > 0) {
				l.axle->v = Velocity(y_component, rad(90));
			} else if (y_component < 0) {
				l.axle->v = Velocity(abs(y_component), rad(270));
			} else if (y_component == 0) {
				l.axle->v = Velocity(0, 0);
			}
			l.apply_force(Force(l.mass * l.rightmost->v.magnitude, rad(0)), l.rightmost->horzd, CYAN);
			l.push_left_uniformwise(5);
		}
		if (l.leftmost->x > stage_width) {
			float y_component = get_xy_components(l.axle->v).second;

			if (y_component > 0) {
				l.axle->v = Velocity(y_component, rad(90));
			} else if (y_component < 0) {
				l.axle->v = Velocity(abs(y_component), rad(270));
			} else if (y_component == 0) {
				l.axle->v = Velocity(0, 0);
			}
			l.apply_force(Force(l.mass * l.leftmost->v.magnitude, rad(180)), l.leftmost->horzd, CYAN);
			l.push_left_uniformwise(-5);
		}
		if (l.rightmost->x > stage_width) {
			float y_component = get_xy_components(l.axle->v).second;

			if (y_component > 0) {
				l.axle->v = Velocity(y_component, rad(90));
			} else if (y_component < 0) {
				l.axle->v = Velocity(abs(y_component), rad(270));
			} else if (y_component == 0) {
				l.axle->v = Velocity(0, 0);
			}
			l.apply_force(Force(l.mass * l.rightmost->v.magnitude, rad(180)), l.rightmost->horzd, CYAN);
			l.push_left_uniformwise(-5);
		}

		l.tick();
		l.draw(poly_shader, poly_VAO, poly_VBO, poly_mvp_l, mvp_m);



		// Draw wheels here, as series of points
		// TODO refactor into draw_circle function
		glPointSize(5);
		draw_poly(poly_shader, poly_VAO, poly_VBO, {
				left_wheel_center_x, left_wheel_center_y, EXP_COLOR(RED)},
			GL_POINTS, 1, poly_mvp_l, mvp_m);
		draw_poly(poly_shader, poly_VAO, poly_VBO, {
				right_wheel_center_x, right_wheel_center_y, EXP_COLOR(GREEN)},
			GL_POINTS, 1, poly_mvp_l, mvp_m);

		glPointSize(1);
		std::vector<float> left_wheel_points;
		std::vector<float> right_wheel_points;
		float resolution_d = 0.5;
		float theta_r = 0;
		for (float deg = 0; deg < 360; deg += resolution_d){
			theta_r = rad(deg);

			float left_px = left_wheel_center_x + cos(theta_r) * wheel_radius;
			float left_py = left_wheel_center_y + sin(theta_r) * wheel_radius;

			float right_px = right_wheel_center_x + cos(theta_r) * wheel_radius;
			float right_py = right_wheel_center_y + sin(theta_r) * wheel_radius;

			left_wheel_points.push_back(left_px);
			left_wheel_points.push_back(left_py);
			left_wheel_points.push_back(WHITE.r);
			left_wheel_points.push_back(WHITE.g);
			left_wheel_points.push_back(WHITE.b);
			left_wheel_points.push_back(1.0);

			right_wheel_points.push_back(right_px);
			right_wheel_points.push_back(right_py);
			right_wheel_points.push_back(WHITE.r);
			right_wheel_points.push_back(WHITE.g);
			right_wheel_points.push_back(WHITE.b);
			right_wheel_points.push_back(1.0);
		}

		draw_poly(poly_shader, poly_VAO, poly_VBO, left_wheel_points, GL_POINTS, left_wheel_points.size()/6, poly_mvp_l, mvp_m);
		draw_poly(poly_shader, poly_VAO, poly_VBO, right_wheel_points, GL_POINTS, right_wheel_points.size()/6, poly_mvp_l, mvp_m);
		glPointSize(5);


		std::vector<float> ground_vs = {
			0, ground_y, 1.0, 1.0, 1.0, 1.0,
			D_WIDTH, ground_y, 1.0, 1.0, 1.0, 1.0};
		draw_poly(poly_shader, poly_VAO, poly_VBO, ground_vs, GL_LINES, 2, poly_mvp_l, mvp_m);


		draw_poly(poly_shader, poly_VAO, poly_VBO, {stage_width, 0, EXP_COLOR(DARKGREY),
							    stage_width, D_HEIGHT, EXP_COLOR(DARKGREY),
							    stage_width + (D_WIDTH - stage_width), D_HEIGHT, EXP_COLOR(DARKGREY),
							    stage_width + (D_WIDTH - stage_width), 0, EXP_COLOR(DARKGREY)}, GL_QUADS, 4, poly_mvp_l, mvp_m);


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
