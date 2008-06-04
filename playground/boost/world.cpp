#include <boost/python.hpp>
using namespace boost::python;

struct World
{
	std::string msg;

	void set(std::string msg) { this->msg = msg; }
	std::string greet() { return msg; }

	int my_sum(list lst) 
	{
		int result = 0;
		for(int i = 0; i < len(lst); i++)
		{
			int val = extract<int>(lst[i]);
			result += val;
		}
		return result; 
	};
};

BOOST_PYTHON_MODULE(world)
{	
    class_<World>("World")
        .def("greet", &World::greet)
        .def("set", &World::set)
        .def("my_sum", &World::my_sum)
    ;
};
