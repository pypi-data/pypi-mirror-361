
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/numpy.h>
#include <dune/python/pybind11/stl.h>

#include <dune/common/typelist.hh>
#include <dune/grid/yaspgrid/coordinates.hh>

#include <dune/python/common/typeregistry.hh>
#include <dune/python/common/fvector.hh>

using namespace Dune;
using namespace Dune::Python;
namespace py = pybind11;

template<typename T>
auto registerCoords(py::module module, std::string name)
{
  auto includes = IncludeFiles{"dune/grid/yaspgrid/coordinates.hh"};
  std::string nspace("Dune::");
  auto typeName = GenerateTypeName(nspace+name, MetaType<double>(), "2");
  auto cls = insertClass<T>(module, name, typeName, includes);
  if (cls.second)
  {
    // cls.first.def("name", [name](const T & self)
    cls.first.def_static("name", [name]() { return name; });
    cls.first.def_property_readonly_static("typeName", [typeName](py::object) { return typeName.name(); });
    cls.first.def_property_readonly_static("dimgrid", [](py::object) { return 2; });
    cls.first.def_property_readonly_static("numpy_ctype", [](py::object) { return py::dtype::of<double>(); });
    cls.first.def_property_readonly_static("ctype", [](py::object) { return "double"; });
  }
  return cls.first;
}

PYBIND11_MODULE(yaspcoordinates_dim2_ctdouble, module)
{
  // make sure FieldVector is known to pybind11
  addToTypeRegistry<double>(GenerateTypeName("double"));
  registerFieldVector<double,2>(module);

  // EquidistantCoordinates(const Dune::FieldVector<ct,dim>& upperRight, const std::array<int,dim>& s)
  //py::class_<EquidistantCoordinates<double,2>>(module, "EquidistantCoordinates")
  registerCoords<EquidistantCoordinates<double,2>>(module, "EquidistantCoordinates")
    .def(py::init<Dune::FieldVector<double,2>, std::array<int,2>>());

  // EquidistantOffsetCoordinates(const Dune::FieldVector<ct,dim>& lowerLeft, const Dune::FieldVector<ct,dim>& upperRight, const std::array<int,dim>& s)
  registerCoords<EquidistantOffsetCoordinates<double,2>>(module, "EquidistantOffsetCoordinates")
    .def(py::init<Dune::FieldVector<double,2>, Dune::FieldVector<double,2>, std::array<int,2>>());
    //.def(py::init( [] (std::array<double,2>, std::array<double,2>, std::array<int,2>) { return static_cast<EquidistantOffsetCoordinates<double,2>*>(0); } ));

  // TensorProductCoordinates(const std::array<std::vector<ct>,dim>& c, const std::array<int,dim>& offset)
  registerCoords<TensorProductCoordinates<double,2>>(module, "TensorProductCoordinates")
    .def(py::init<std::array<std::vector<double>,2>, std::array<int,2>>());
}

