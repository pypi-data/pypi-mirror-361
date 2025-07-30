#ifndef GUARD_3c10414582133a0fa8e341c4544a97c7
#define GUARD_3c10414582133a0fa8e341c4544a97c7

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

namespace UFLLocalFunctions_3c10414582133a0fa8e341c4544a97c7
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
    using std::abs;
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = std::abs( tmp1 );
    const auto tmp3 = -0.3 + tmp2;
    const auto tmp4 = -0.1 + tmp0[ 0 ];
    const auto tmp5 = std::abs( tmp4 );
    const auto tmp6 = -0.8 + tmp5;
    const auto tmp7 = std::max( tmp6, tmp3 );
    const auto tmp8 = std::max( tmp3, 0.0 );
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = std::max( tmp6, 0.0 );
    const auto tmp11 = tmp10 * tmp10;
    const auto tmp12 = tmp11 + tmp9;
    const auto tmp13 = 1e-10 + tmp12;
    const auto tmp14 = std::sqrt( tmp13 );
    const auto tmp15 = -1 * (tmp7 > 0.0 ? tmp14 : tmp7);
    result[ 0 ] = tmp15;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.1 + tmp0[ 0 ];
    const auto tmp2 = -0.3 + tmp0[ 1 ];
    const auto tmp3 = std::abs( tmp2 );
    const auto tmp4 = -0.3 + tmp3;
    const auto tmp5 = std::abs( tmp1 );
    const auto tmp6 = -0.8 + tmp5;
    const auto tmp7 = (tmp6 > tmp4 ? 1 : 0.0) * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp8 = std::max( tmp4, 0.0 );
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = std::max( tmp6, 0.0 );
    const auto tmp11 = tmp10 * tmp10;
    const auto tmp12 = tmp11 + tmp9;
    const auto tmp13 = 1e-10 + tmp12;
    const auto tmp14 = std::sqrt( tmp13 );
    const auto tmp15 = 2 * tmp14;
    const auto tmp16 = (tmp6 > 0.0 ? 1 : 0.0) * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp17 = tmp16 * tmp10;
    const auto tmp18 = tmp17 + tmp17;
    const auto tmp19 = tmp18 / tmp15;
    const auto tmp20 = std::max( tmp6, tmp4 );
    const auto tmp21 = -1 * (tmp20 > 0.0 ? tmp19 : tmp7);
    const auto tmp22 = -1 * (tmp6 > tmp4 ? 1 : 0.0);
    const auto tmp23 = 1.0 + tmp22;
    const auto tmp24 = tmp23 * (tmp2 == 0.0 ? 0.0 : (tmp2 < 0.0 ? -1 : 1));
    const auto tmp25 = (tmp4 > 0.0 ? 1 : 0.0) * (tmp2 == 0.0 ? 0.0 : (tmp2 < 0.0 ? -1 : 1));
    const auto tmp26 = tmp25 * tmp8;
    const auto tmp27 = tmp26 + tmp26;
    const auto tmp28 = tmp27 / tmp15;
    const auto tmp29 = -1 * (tmp20 > 0.0 ? tmp28 : tmp24);
    (result[ 0 ])[ 0 ] = tmp21;
    (result[ 0 ])[ 1 ] = tmp29;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::abs;
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = std::abs( tmp1 );
    const auto tmp3 = -0.3 + tmp2;
    const auto tmp4 = std::max( tmp3, 0.0 );
    const auto tmp5 = tmp4 * tmp4;
    const auto tmp6 = -0.1 + tmp0[ 0 ];
    const auto tmp7 = std::abs( tmp6 );
    const auto tmp8 = -0.8 + tmp7;
    const auto tmp9 = std::max( tmp8, 0.0 );
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = tmp10 + tmp5;
    const auto tmp12 = 1e-10 + tmp11;
    const auto tmp13 = std::sqrt( tmp12 );
    const auto tmp14 = 2 * tmp13;
    const auto tmp15 = (tmp8 > 0.0 ? 1 : 0.0) * (tmp6 == 0.0 ? 0.0 : (tmp6 < 0.0 ? -1 : 1));
    const auto tmp16 = tmp15 * tmp9;
    const auto tmp17 = tmp16 + tmp16;
    const auto tmp18 = tmp17 / tmp14;
    const auto tmp19 = 2 * tmp18;
    const auto tmp20 = tmp19 * tmp18;
    const auto tmp21 = -1 * tmp20;
    const auto tmp22 = tmp15 * tmp15;
    const auto tmp23 = tmp22 + tmp22;
    const auto tmp24 = tmp23 + tmp21;
    const auto tmp25 = tmp24 / tmp14;
    const auto tmp26 = std::max( tmp8, tmp3 );
    const auto tmp27 = -1 * (tmp26 > 0.0 ? tmp25 : 0.0);
    const auto tmp28 = (tmp3 > 0.0 ? 1 : 0.0) * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp29 = tmp28 * tmp4;
    const auto tmp30 = tmp29 + tmp29;
    const auto tmp31 = tmp30 / tmp14;
    const auto tmp32 = 2 * tmp31;
    const auto tmp33 = tmp32 * tmp18;
    const auto tmp34 = -1 * tmp33;
    const auto tmp35 = tmp34 / tmp14;
    const auto tmp36 = -1 * (tmp26 > 0.0 ? tmp35 : 0.0);
    const auto tmp37 = tmp19 * tmp31;
    const auto tmp38 = -1 * tmp37;
    const auto tmp39 = tmp38 / tmp14;
    const auto tmp40 = -1 * (tmp26 > 0.0 ? tmp39 : 0.0);
    const auto tmp41 = tmp32 * tmp31;
    const auto tmp42 = -1 * tmp41;
    const auto tmp43 = tmp28 * tmp28;
    const auto tmp44 = tmp43 + tmp43;
    const auto tmp45 = tmp44 + tmp42;
    const auto tmp46 = tmp45 / tmp14;
    const auto tmp47 = -1 * (tmp26 > 0.0 ? tmp46 : 0.0);
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp27;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp36;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp40;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp47;
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

} // namespace UFLLocalFunctions_3c10414582133a0fa8e341c4544a97c7

PYBIND11_MODULE( localfunction_3c10414582133a0fa8e341c4544a97c7_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_3c10414582133a0fa8e341c4544a97c7::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_3c10414582133a0fa8e341c4544a97c7::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_3c10414582133a0fa8e341c4544a97c7_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
