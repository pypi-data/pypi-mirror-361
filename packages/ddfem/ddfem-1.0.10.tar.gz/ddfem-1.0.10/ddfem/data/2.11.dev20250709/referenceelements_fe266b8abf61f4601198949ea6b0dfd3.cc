#ifndef Guard_referenceelements_fe266b8abf61f4601198949ea6b0dfd3
#define Guard_referenceelements_fe266b8abf61f4601198949ea6b0dfd3

#include <config.h>

#define USING_DUNE_PYTHON 1

#include <dune/python/geometry/referenceelements.hh>

#include <dune/python/common/typeregistry.hh>
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/stl.h>

PYBIND11_MODULE( referenceelements_fe266b8abf61f4601198949ea6b0dfd3, module )
{
  using pybind11::operator""_a;
  pybind11::module cls0 = module;
  {
    using DuneType = Dune::Geo::ReferenceElement<Dune::Geo::ReferenceElementImplementation<double,3> >;
    auto cls = Dune::Python::insertClass< DuneType >( cls0, "ReferenceElements", Dune::Python::GenerateTypeName("Dune::Geo::ReferenceElement<Dune::Geo::ReferenceElementImplementation<double,3> >"), Dune::Python::IncludeFiles{"dune/python/geometry/referenceelements.hh"}).first;
    Dune::Python::registerReferenceElements( cls0, cls );
  }
}
#endif