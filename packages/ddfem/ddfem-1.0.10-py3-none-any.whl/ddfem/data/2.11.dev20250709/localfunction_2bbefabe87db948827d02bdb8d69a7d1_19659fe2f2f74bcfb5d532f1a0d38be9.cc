#ifndef GUARD_2bbefabe87db948827d02bdb8d69a7d1
#define GUARD_2bbefabe87db948827d02bdb8d69a7d1

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

namespace UFLLocalFunctions_2bbefabe87db948827d02bdb8d69a7d1
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
    const auto tmp1 = std::abs( tmp0[ 1 ] );
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.75 + tmp6;
    const auto tmp8 = std::abs( tmp7 );
    const auto tmp9 = -0.44083893921935485 + tmp1;
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = -0.6067627457812106 + tmp0[ 0 ];
    const auto tmp12 = tmp11 * tmp11;
    const auto tmp13 = tmp12 + tmp10;
    const auto tmp14 = 1e-10 + tmp13;
    const auto tmp15 = std::sqrt( tmp14 );
    const auto tmp16 = 0.8090169943749475 * tmp1;
    const auto tmp17 = 0.5877852522924731 * tmp0[ 0 ];
    const auto tmp18 = -0.25 + (tmp17 > tmp16 ? tmp15 : tmp8);
    result[ 0 ] = tmp18;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = std::abs( tmp0[ 1 ] );
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.75 + tmp6;
    const auto tmp8 = 2 * tmp6;
    const auto tmp9 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp10 = tmp9 / tmp8;
    const auto tmp11 = tmp10 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp12 = -0.44083893921935485 + tmp1;
    const auto tmp13 = tmp12 * tmp12;
    const auto tmp14 = -0.6067627457812106 + tmp0[ 0 ];
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = tmp15 + tmp13;
    const auto tmp17 = 1e-10 + tmp16;
    const auto tmp18 = std::sqrt( tmp17 );
    const auto tmp19 = 2 * tmp18;
    const auto tmp20 = tmp14 + tmp14;
    const auto tmp21 = tmp20 / tmp19;
    const auto tmp22 = 0.8090169943749475 * tmp1;
    const auto tmp23 = 0.5877852522924731 * tmp0[ 0 ];
    const auto tmp24 = tmp1 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp25 = tmp24 + tmp24;
    const auto tmp26 = tmp25 / tmp8;
    const auto tmp27 = tmp26 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp28 = tmp12 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp29 = tmp28 + tmp28;
    const auto tmp30 = tmp29 / tmp19;
    (result[ 0 ])[ 0 ] = (tmp23 > tmp22 ? tmp21 : tmp11);
    (result[ 0 ])[ 1 ] = (tmp23 > tmp22 ? tmp30 : tmp27);
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::abs;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = std::abs( tmp0[ 1 ] );
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.75 + tmp6;
    const auto tmp8 = 2 * tmp6;
    const auto tmp9 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp10 = tmp9 / tmp8;
    const auto tmp11 = 2 * tmp10;
    const auto tmp12 = tmp11 * tmp10;
    const auto tmp13 = -1 * tmp12;
    const auto tmp14 = 2 + tmp13;
    const auto tmp15 = tmp14 / tmp8;
    const auto tmp16 = tmp15 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp17 = -0.44083893921935485 + tmp1;
    const auto tmp18 = tmp17 * tmp17;
    const auto tmp19 = -0.6067627457812106 + tmp0[ 0 ];
    const auto tmp20 = tmp19 * tmp19;
    const auto tmp21 = tmp20 + tmp18;
    const auto tmp22 = 1e-10 + tmp21;
    const auto tmp23 = std::sqrt( tmp22 );
    const auto tmp24 = 2 * tmp23;
    const auto tmp25 = tmp19 + tmp19;
    const auto tmp26 = tmp25 / tmp24;
    const auto tmp27 = 2 * tmp26;
    const auto tmp28 = tmp27 * tmp26;
    const auto tmp29 = -1 * tmp28;
    const auto tmp30 = 2 + tmp29;
    const auto tmp31 = tmp30 / tmp24;
    const auto tmp32 = 0.8090169943749475 * tmp1;
    const auto tmp33 = 0.5877852522924731 * tmp0[ 0 ];
    const auto tmp34 = tmp1 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp35 = tmp34 + tmp34;
    const auto tmp36 = tmp35 / tmp8;
    const auto tmp37 = 2 * tmp36;
    const auto tmp38 = tmp37 * tmp10;
    const auto tmp39 = -1 * tmp38;
    const auto tmp40 = tmp39 / tmp8;
    const auto tmp41 = tmp40 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp42 = tmp17 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp43 = tmp42 + tmp42;
    const auto tmp44 = tmp43 / tmp24;
    const auto tmp45 = 2 * tmp44;
    const auto tmp46 = tmp45 * tmp26;
    const auto tmp47 = -1 * tmp46;
    const auto tmp48 = tmp47 / tmp24;
    const auto tmp49 = tmp11 * tmp36;
    const auto tmp50 = -1 * tmp49;
    const auto tmp51 = tmp50 / tmp8;
    const auto tmp52 = tmp51 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp53 = tmp27 * tmp44;
    const auto tmp54 = -1 * tmp53;
    const auto tmp55 = tmp54 / tmp24;
    const auto tmp56 = tmp37 * tmp36;
    const auto tmp57 = -1 * tmp56;
    const auto tmp58 = (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1)) * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp59 = tmp58 + tmp58;
    const auto tmp60 = tmp59 + tmp57;
    const auto tmp61 = tmp60 / tmp8;
    const auto tmp62 = tmp61 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp63 = tmp45 * tmp44;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = tmp59 + tmp64;
    const auto tmp66 = tmp65 / tmp24;
    ((result[ 0 ])[ 0 ])[ 0 ] = (tmp33 > tmp32 ? tmp31 : tmp16);
    ((result[ 0 ])[ 0 ])[ 1 ] = (tmp33 > tmp32 ? tmp48 : tmp41);
    ((result[ 0 ])[ 1 ])[ 0 ] = (tmp33 > tmp32 ? tmp55 : tmp52);
    ((result[ 0 ])[ 1 ])[ 1 ] = (tmp33 > tmp32 ? tmp66 : tmp62);
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

} // namespace UFLLocalFunctions_2bbefabe87db948827d02bdb8d69a7d1

PYBIND11_MODULE( localfunction_2bbefabe87db948827d02bdb8d69a7d1_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_2bbefabe87db948827d02bdb8d69a7d1::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_2bbefabe87db948827d02bdb8d69a7d1::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_2bbefabe87db948827d02bdb8d69a7d1_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
