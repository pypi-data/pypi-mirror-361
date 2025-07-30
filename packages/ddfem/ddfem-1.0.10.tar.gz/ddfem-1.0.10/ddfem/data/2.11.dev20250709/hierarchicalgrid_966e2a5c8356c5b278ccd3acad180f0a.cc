#ifndef Guard_hierarchicalgrid_966e2a5c8356c5b278ccd3acad180f0a
#define Guard_hierarchicalgrid_966e2a5c8356c5b278ccd3acad180f0a

#include <config.h>

#define USING_DUNE_PYTHON 1

#include <dune/grid/io/file/dgfparser/dgfyasp.hh>
#include <dune/grid/yaspgrid.hh>
#include <dune/python/grid/hierarchical.hh>

#include <dune/python/common/typeregistry.hh>
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/stl.h>

PYBIND11_MODULE( hierarchicalgrid_966e2a5c8356c5b278ccd3acad180f0a, module )
{
  using pybind11::operator""_a;
  pybind11::module cls0 = module;
  {
    using DuneType = Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >;
    auto cls = Dune::Python::insertClass< DuneType, std::shared_ptr<DuneType> >( cls0, "HierarchicalGrid",pybind11::dynamic_attr(), Dune::Python::GenerateTypeName("Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >"), Dune::Python::IncludeFiles{"dune/grid/io/file/dgfparser/dgfyasp.hh","dune/grid/yaspgrid.hh","dune/python/grid/hierarchical.hh"}).first;
    Dune::Python::registerHierarchicalGrid( cls0, cls );
    cls.def( pybind11::init( [] ( const Dune::EquidistantOffsetCoordinates< double, 2 >& coordinates, std::array<bool, 2> periodic, int overlap ) {std::bitset<2> periodic_;
        for (int i=0;i<2;++i) periodic_.set(i,periodic[i]);
        return new DuneType(coordinates,periodic_,overlap);
      } ), "coordinates"_a, "periodic"_a, "overlap"_a );
  }
}
#endif