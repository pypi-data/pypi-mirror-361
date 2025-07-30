#ifndef GUARD_161bbe6dde741c6e3f90c2919b8d17a4
#define GUARD_161bbe6dde741c6e3f90c2919b8d17a4

#define USING_DUNE_PYTHON 1
#include <config.h>
#include <dune/grid/io/file/dgfparser/dgfyasp.hh>
#include <dune/grid/yaspgrid.hh>
#include <dune/python/grid/hierarchical.hh>
#include <dune/fem/function/localfunction/bindable.hh>
#include <dune/fem/common/intersectionside.hh>
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/extensions.h>
#include <dune/fempy/py/grid/gridpart.hh>
#include <dune/common/exceptions.hh>
#include <dune/fempy/py/ufllocalfunction.hh>

namespace UFLLocalFunctions_161bbe6dde741c6e3f90c2919b8d17a4
{

  // UFLLocalFunction
// ----------------

template< class GridPart >
struct UFLLocalFunction
  : public Dune::Fem::BindableGridFunctionWithSpace<GridPart,Dune::Dim<1>>
{
  typedef GridPart GridPartType;
  typedef typename GridPartType::GridViewType GridView;
  typedef typename GridView::ctype ctype;
  typedef Dune::Fem::BindableGridFunctionWithSpace<GridPart,Dune::Dim<1>> BaseType;
  typedef Dune::Fem::GridFunctionSpace<GridPartType,Dune::Dim<1>> FunctionSpaceType;
  typedef typename GridPartType::template Codim< 0 >::EntityType EntityType;
  typedef typename GridPartType::IntersectionType IntersectionType;
  typedef typename EntityType::Geometry Geometry;
  typedef typename Geometry::GlobalCoordinate GlobalCoordinateType;
  typedef Dune::Fem::IntersectionSide Side;
  typedef std::tuple<> ConstantTupleType;
  typedef std::tuple<> CoefficientTupleType;
  static constexpr bool gridPartValid = true;
  template< std::size_t i >
  using CoefficientType = std::tuple_element_t< i, CoefficientTupleType >;
  template< std::size_t i >
  using ConstantType = typename std::tuple_element_t< i, ConstantTupleType >::element_type;
  using BaseType::entity;
  using BaseType::geometry;

  UFLLocalFunction ( const GridPartType &gridPart, const std::string &name, int order, const Dune::Fem::ParameterReader &parameter = Dune::Fem::Parameter::container() )
    : BaseType(gridPart,name,order)
  {}

  void bind ( const IntersectionType &intersection, Side side )
  {
    BaseType::bind(intersection, side);
  }

  void bind ( const EntityType &entity )
  {
    BaseType::bind(entity);
  }

  void unbind ()
  {
    BaseType::unbind();
  }

  template< class Point >
  void evaluate ( const Point &x, typename FunctionSpaceType::RangeType &result ) const
  {
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = -0.1 + tmp0[ 0 ];
    const auto tmp4 = tmp3 * tmp3;
    const auto tmp5 = tmp4 + tmp2;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -0.5 + tmp7;
    result[ 0 ] = tmp8;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = -0.1 + tmp0[ 0 ];
    const auto tmp4 = tmp3 * tmp3;
    const auto tmp5 = tmp4 + tmp2;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = 2 * tmp7;
    const auto tmp9 = tmp3 + tmp3;
    const auto tmp10 = tmp9 / tmp8;
    const auto tmp11 = tmp1 + tmp1;
    const auto tmp12 = tmp11 / tmp8;
    (result[ 0 ])[ 0 ] = tmp10;
    (result[ 0 ])[ 1 ] = tmp12;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = -0.1 + tmp0[ 0 ];
    const auto tmp4 = tmp3 * tmp3;
    const auto tmp5 = tmp4 + tmp2;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = 2 * tmp7;
    const auto tmp9 = tmp3 + tmp3;
    const auto tmp10 = tmp9 / tmp8;
    const auto tmp11 = 2 * tmp10;
    const auto tmp12 = tmp11 * tmp10;
    const auto tmp13 = -1 * tmp12;
    const auto tmp14 = 2 + tmp13;
    const auto tmp15 = tmp14 / tmp8;
    const auto tmp16 = tmp1 + tmp1;
    const auto tmp17 = tmp16 / tmp8;
    const auto tmp18 = 2 * tmp17;
    const auto tmp19 = tmp18 * tmp10;
    const auto tmp20 = -1 * tmp19;
    const auto tmp21 = tmp20 / tmp8;
    const auto tmp22 = tmp11 * tmp17;
    const auto tmp23 = -1 * tmp22;
    const auto tmp24 = tmp23 / tmp8;
    const auto tmp25 = tmp18 * tmp17;
    const auto tmp26 = -1 * tmp25;
    const auto tmp27 = 2 + tmp26;
    const auto tmp28 = tmp27 / tmp8;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp15;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp21;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp24;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp28;
  }

  template< std::size_t i >
  const ConstantType< i > &constant () const
  {
    return *std::get< i >( constants_ );
  }

  template< std::size_t i >
  ConstantType< i > &constant ()
  {
    return *std::get< i >( constants_ );
  }
  ConstantTupleType constants_;
  std::tuple<  > coefficients_;
};

} // namespace UFLLocalFunctions_161bbe6dde741c6e3f90c2919b8d17a4

PYBIND11_MODULE( localfunction_161bbe6dde741c6e3f90c2919b8d17a4_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_161bbe6dde741c6e3f90c2919b8d17a4::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_161bbe6dde741c6e3f90c2919b8d17a4::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_161bbe6dde741c6e3f90c2919b8d17a4_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
