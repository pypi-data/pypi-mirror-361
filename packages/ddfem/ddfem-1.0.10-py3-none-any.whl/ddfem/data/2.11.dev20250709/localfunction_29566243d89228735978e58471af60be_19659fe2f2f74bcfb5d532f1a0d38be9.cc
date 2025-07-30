#ifndef GUARD_29566243d89228735978e58471af60be
#define GUARD_29566243d89228735978e58471af60be

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

namespace UFLLocalFunctions_29566243d89228735978e58471af60be
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
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = std::abs( tmp0[ 0 ] );
    const auto tmp2 = -0.2 + tmp1;
    const auto tmp3 = tmp2 * tmp2;
    const auto tmp4 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp5 = tmp4 + tmp3;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -0.5 + tmp7;
    const auto tmp9 = -0.1 + tmp8;
    const auto tmp10 = tmp1 * tmp1;
    const auto tmp11 = std::abs( tmp0[ 1 ] );
    const auto tmp12 = -0.565685424949238 + tmp11;
    const auto tmp13 = tmp12 * tmp12;
    const auto tmp14 = tmp13 + tmp10;
    const auto tmp15 = 1e-10 + tmp14;
    const auto tmp16 = std::sqrt( tmp15 );
    const auto tmp17 = -1 * tmp16;
    const auto tmp18 = 0.565685424949238 * tmp1;
    const auto tmp19 = -0.2 * tmp12;
    const auto tmp20 = 0.1 + (tmp19 > tmp18 ? tmp17 : tmp9);
    result[ 0 ] = tmp20;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = std::abs( tmp0[ 0 ] );
    const auto tmp2 = -0.2 + tmp1;
    const auto tmp3 = tmp2 * tmp2;
    const auto tmp4 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp5 = tmp4 + tmp3;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = 2 * tmp7;
    const auto tmp9 = tmp2 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp10 = tmp9 + tmp9;
    const auto tmp11 = tmp10 / tmp8;
    const auto tmp12 = tmp1 * tmp1;
    const auto tmp13 = std::abs( tmp0[ 1 ] );
    const auto tmp14 = -0.565685424949238 + tmp13;
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = tmp15 + tmp12;
    const auto tmp17 = 1e-10 + tmp16;
    const auto tmp18 = std::sqrt( tmp17 );
    const auto tmp19 = 2 * tmp18;
    const auto tmp20 = tmp1 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp21 = tmp20 + tmp20;
    const auto tmp22 = tmp21 / tmp19;
    const auto tmp23 = -1 * tmp22;
    const auto tmp24 = 0.565685424949238 * tmp1;
    const auto tmp25 = -0.2 * tmp14;
    const auto tmp26 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp27 = tmp26 / tmp8;
    const auto tmp28 = tmp14 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp29 = tmp28 + tmp28;
    const auto tmp30 = tmp29 / tmp19;
    const auto tmp31 = -1 * tmp30;
    (result[ 0 ])[ 0 ] = (tmp25 > tmp24 ? tmp23 : tmp11);
    (result[ 0 ])[ 1 ] = (tmp25 > tmp24 ? tmp31 : tmp27);
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::abs;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = std::abs( tmp0[ 0 ] );
    const auto tmp2 = -0.2 + tmp1;
    const auto tmp3 = tmp2 * tmp2;
    const auto tmp4 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp5 = tmp4 + tmp3;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = 2 * tmp7;
    const auto tmp9 = tmp2 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp10 = tmp9 + tmp9;
    const auto tmp11 = tmp10 / tmp8;
    const auto tmp12 = 2 * tmp11;
    const auto tmp13 = tmp12 * tmp11;
    const auto tmp14 = -1 * tmp13;
    const auto tmp15 = (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1)) * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp16 = tmp15 + tmp15;
    const auto tmp17 = tmp16 + tmp14;
    const auto tmp18 = tmp17 / tmp8;
    const auto tmp19 = tmp1 * tmp1;
    const auto tmp20 = std::abs( tmp0[ 1 ] );
    const auto tmp21 = -0.565685424949238 + tmp20;
    const auto tmp22 = tmp21 * tmp21;
    const auto tmp23 = tmp22 + tmp19;
    const auto tmp24 = 1e-10 + tmp23;
    const auto tmp25 = std::sqrt( tmp24 );
    const auto tmp26 = 2 * tmp25;
    const auto tmp27 = tmp1 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp28 = tmp27 + tmp27;
    const auto tmp29 = tmp28 / tmp26;
    const auto tmp30 = 2 * tmp29;
    const auto tmp31 = tmp30 * tmp29;
    const auto tmp32 = -1 * tmp31;
    const auto tmp33 = tmp16 + tmp32;
    const auto tmp34 = tmp33 / tmp26;
    const auto tmp35 = -1 * tmp34;
    const auto tmp36 = 0.565685424949238 * tmp1;
    const auto tmp37 = -0.2 * tmp21;
    const auto tmp38 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp39 = tmp38 / tmp8;
    const auto tmp40 = 2 * tmp39;
    const auto tmp41 = tmp40 * tmp11;
    const auto tmp42 = -1 * tmp41;
    const auto tmp43 = tmp42 / tmp8;
    const auto tmp44 = tmp21 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp45 = tmp44 + tmp44;
    const auto tmp46 = tmp45 / tmp26;
    const auto tmp47 = 2 * tmp46;
    const auto tmp48 = tmp47 * tmp29;
    const auto tmp49 = -1 * tmp48;
    const auto tmp50 = tmp49 / tmp26;
    const auto tmp51 = -1 * tmp50;
    const auto tmp52 = tmp12 * tmp39;
    const auto tmp53 = -1 * tmp52;
    const auto tmp54 = tmp53 / tmp8;
    const auto tmp55 = tmp30 * tmp46;
    const auto tmp56 = -1 * tmp55;
    const auto tmp57 = tmp56 / tmp26;
    const auto tmp58 = -1 * tmp57;
    const auto tmp59 = tmp40 * tmp39;
    const auto tmp60 = -1 * tmp59;
    const auto tmp61 = 2 + tmp60;
    const auto tmp62 = tmp61 / tmp8;
    const auto tmp63 = tmp47 * tmp46;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1)) * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp66 = tmp65 + tmp65;
    const auto tmp67 = tmp66 + tmp64;
    const auto tmp68 = tmp67 / tmp26;
    const auto tmp69 = -1 * tmp68;
    ((result[ 0 ])[ 0 ])[ 0 ] = (tmp37 > tmp36 ? tmp35 : tmp18);
    ((result[ 0 ])[ 0 ])[ 1 ] = (tmp37 > tmp36 ? tmp51 : tmp43);
    ((result[ 0 ])[ 1 ])[ 0 ] = (tmp37 > tmp36 ? tmp58 : tmp54);
    ((result[ 0 ])[ 1 ])[ 1 ] = (tmp37 > tmp36 ? tmp69 : tmp62);
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

} // namespace UFLLocalFunctions_29566243d89228735978e58471af60be

PYBIND11_MODULE( localfunction_29566243d89228735978e58471af60be_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_29566243d89228735978e58471af60be::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_29566243d89228735978e58471af60be::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_29566243d89228735978e58471af60be_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
