#include <GL/glew.h>
#include <string>
#include <memory>
#include <vector>
#include <iostream>

#ifndef UTILS_ASDF_H
#define UTILS_ASDF_H

const int D_WIDTH = 1500;
const int D_HEIGHT = 700;


GLuint load_shader(std::string vs_filename, std::string fs_filename);
std::string get_file_str(std::string filename);

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

#endif
