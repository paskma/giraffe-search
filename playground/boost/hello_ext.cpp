#include <boost/python.hpp>
#include <iostream>
#include <vector>
#include <climits>
using namespace boost::python;

char const* greet()
{
	return "hello, world";
}

struct World
{
	void set(std::string msg) { this->msg = msg; }
	std::string greet() { return msg; }
	std::string msg;
	int x(list lst) 
	{
		for(int i = 0; i < len(lst); i++)
		{
			object o = lst[i];
			std::cout << "cout " << i << std::endl;
			int val = extract<int>(o);
			std::cout << val << std::endl;
		}
		return len(lst); 
	};
};

list multiread(list lists)
{
	list result;
	int count = 0, foo = 0;
	
	for (int i = 0; i < len(lists); i++)
	{
		list a = extract<list>(lists[i]);
		for (int j = 0; j < len(a); j++)
		{
			foo += extract<int>(a[j]);
			count++;
		}
	}
	
	std::cout << "count " << count << " foo " << foo << std::endl;
	
	return result;
}

list multion(list lists)
{
//	result = []
	list result;
//	active = list(lists)
	std::vector<list> active;
	for(int i = 0; i < len(lists); i++)
		active.push_back(extract<list>(lists[i]));
//	indices = [0] * len(active)
	std::vector<int> indices(active.size(), 0);
/*	for(int i = 0; i < active.size(); i++)
		indices.push_back(0);*/

//	while True:	
	for(;;)
	{
//		new_active = []
		std::vector<list> new_active;
//		new_indices = []
		std::vector<int> new_indices;
//		
//		for i, lst in enumerate(active):
		for(int i = 0; i < active.size(); i++)
		{
//			if indices[i] < len(lst):
			if(indices.at(i) < len(active.at(i)))
			{
//				new_active.append(lst)
				new_active.push_back(active.at(i));
//				new_indices.append(indices[i])
				new_indices.push_back(indices.at(i));
			}
		}

//		
//		active = new_active
		active = new_active;
//		indices = new_indices
		indices = new_indices;

//		if not active:
		if(!active.size())
//			return result
			return result;
		
//		mindoc = 2**64
		int mindoc = INT_MAX;
//		increment = []
		std::vector<int> increment;
//		for i, lst in enumerate(active):
		for(int i = 0; i < active.size(); i++)
		{
//			doc = lst[indices[i]]
			int doc = extract<int>(active.at(i)[indices.at(i)]);
//			if doc < mindoc:
			if(doc < mindoc)
			{
//				increment = [i]
				increment.empty();
				increment.push_back(i);
//				mindoc = doc
				mindoc = doc;
			}
//			elif doc == mindoc:
			else if (doc == mindoc)
//				increment.append(i)
				increment.push_back(i);
		}

//		if len(result) == 0 or result[len(result)-1] != mindoc:
		if(len(result) == 0 || extract<int>(result[len(result)-1]) != mindoc)
//			result.append(mindoc)
			result.append(mindoc);
			
//		for i in increment:
		for(std::vector<int>::iterator i = increment.begin(); i != increment.end(); i++)
//			indices[i] += 1
			indices[*i] += 1;
	}
}

BOOST_PYTHON_MODULE(hello_ext)
{

	def("greet", greet);
	def("multion", multion);
	def("multiread", multiread);
	
	class_<World>("World")
        .def("greet", &World::greet)
        .def("set", &World::set)
        .def("x", &World::x)
    ;
};

