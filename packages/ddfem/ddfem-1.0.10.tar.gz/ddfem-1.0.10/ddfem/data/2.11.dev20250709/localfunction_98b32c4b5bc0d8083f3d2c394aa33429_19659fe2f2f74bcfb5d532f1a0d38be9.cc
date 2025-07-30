#ifndef GUARD_98b32c4b5bc0d8083f3d2c394aa33429
#define GUARD_98b32c4b5bc0d8083f3d2c394aa33429

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

namespace UFLLocalFunctions_98b32c4b5bc0d8083f3d2c394aa33429
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
    using std::tanh;
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
    const auto tmp19 = 3 * tmp18;
    const auto tmp20 = tmp19 / 0.1;
    const auto tmp21 = std::tanh( tmp20 );
    const auto tmp22 = -1 * tmp21;
    const auto tmp23 = 1 + tmp22;
    const auto tmp24 = 0.5 * tmp23;
    result[ 0 ] = tmp24;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::cosh;
    using std::pow;
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
    const auto tmp19 = 3 * tmp18;
    const auto tmp20 = tmp19 / 0.1;
    const auto tmp21 = 2.0 * tmp20;
    const auto tmp22 = std::cosh( tmp21 );
    const auto tmp23 = 1.0 + tmp22;
    const auto tmp24 = std::cosh( tmp20 );
    const auto tmp25 = 2.0 * tmp24;
    const auto tmp26 = tmp25 / tmp23;
    const auto tmp27 = std::pow( tmp26, 2 );
    const auto tmp28 = 2 * tmp6;
    const auto tmp29 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp30 = tmp29 / tmp28;
    const auto tmp31 = tmp30 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp32 = 2 * tmp15;
    const auto tmp33 = tmp11 + tmp11;
    const auto tmp34 = tmp33 / tmp32;
    const auto tmp35 = 3 * (tmp17 > tmp16 ? tmp34 : tmp31);
    const auto tmp36 = tmp35 / 0.1;
    const auto tmp37 = tmp36 * tmp27;
    const auto tmp38 = -1 * tmp37;
    const auto tmp39 = 0.5 * tmp38;
    const auto tmp40 = tmp1 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp41 = tmp40 + tmp40;
    const auto tmp42 = tmp41 / tmp28;
    const auto tmp43 = tmp42 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp44 = tmp9 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp45 = tmp44 + tmp44;
    const auto tmp46 = tmp45 / tmp32;
    const auto tmp47 = 3 * (tmp17 > tmp16 ? tmp46 : tmp43);
    const auto tmp48 = tmp47 / 0.1;
    const auto tmp49 = tmp48 * tmp27;
    const auto tmp50 = -1 * tmp49;
    const auto tmp51 = 0.5 * tmp50;
    (result[ 0 ])[ 0 ] = tmp39;
    (result[ 0 ])[ 1 ] = tmp51;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::abs;
    using std::cosh;
    using std::pow;
    using std::sinh;
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
    const auto tmp19 = 3 * tmp18;
    const auto tmp20 = tmp19 / 0.1;
    const auto tmp21 = 2.0 * tmp20;
    const auto tmp22 = std::cosh( tmp21 );
    const auto tmp23 = 1.0 + tmp22;
    const auto tmp24 = std::cosh( tmp20 );
    const auto tmp25 = 2.0 * tmp24;
    const auto tmp26 = tmp25 / tmp23;
    const auto tmp27 = std::pow( tmp26, 2 );
    const auto tmp28 = 2 * tmp6;
    const auto tmp29 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp30 = tmp29 / tmp28;
    const auto tmp31 = 2 * tmp30;
    const auto tmp32 = tmp31 * tmp30;
    const auto tmp33 = -1 * tmp32;
    const auto tmp34 = 2 + tmp33;
    const auto tmp35 = tmp34 / tmp28;
    const auto tmp36 = tmp35 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp37 = 2 * tmp15;
    const auto tmp38 = tmp11 + tmp11;
    const auto tmp39 = tmp38 / tmp37;
    const auto tmp40 = 2 * tmp39;
    const auto tmp41 = tmp40 * tmp39;
    const auto tmp42 = -1 * tmp41;
    const auto tmp43 = 2 + tmp42;
    const auto tmp44 = tmp43 / tmp37;
    const auto tmp45 = 3 * (tmp17 > tmp16 ? tmp44 : tmp36);
    const auto tmp46 = tmp45 / 0.1;
    const auto tmp47 = tmp46 * tmp27;
    const auto tmp48 = tmp30 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp49 = 3 * (tmp17 > tmp16 ? tmp39 : tmp48);
    const auto tmp50 = tmp49 / 0.1;
    const auto tmp51 = std::sinh( tmp20 );
    const auto tmp52 = tmp50 * tmp51;
    const auto tmp53 = 2.0 * tmp52;
    const auto tmp54 = std::sinh( tmp21 );
    const auto tmp55 = 2.0 * tmp50;
    const auto tmp56 = tmp55 * tmp54;
    const auto tmp57 = tmp56 * tmp26;
    const auto tmp58 = -1 * tmp57;
    const auto tmp59 = tmp58 + tmp53;
    const auto tmp60 = tmp59 / tmp23;
    const auto tmp61 = 2 * tmp60;
    const auto tmp62 = tmp61 * tmp26;
    const auto tmp63 = tmp62 * tmp50;
    const auto tmp64 = tmp63 + tmp47;
    const auto tmp65 = -1 * tmp64;
    const auto tmp66 = 0.5 * tmp65;
    const auto tmp67 = tmp1 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp68 = tmp67 + tmp67;
    const auto tmp69 = tmp68 / tmp28;
    const auto tmp70 = 2 * tmp69;
    const auto tmp71 = tmp70 * tmp30;
    const auto tmp72 = -1 * tmp71;
    const auto tmp73 = tmp72 / tmp28;
    const auto tmp74 = tmp73 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp75 = tmp9 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp76 = tmp75 + tmp75;
    const auto tmp77 = tmp76 / tmp37;
    const auto tmp78 = 2 * tmp77;
    const auto tmp79 = tmp78 * tmp39;
    const auto tmp80 = -1 * tmp79;
    const auto tmp81 = tmp80 / tmp37;
    const auto tmp82 = 3 * (tmp17 > tmp16 ? tmp81 : tmp74);
    const auto tmp83 = tmp82 / 0.1;
    const auto tmp84 = tmp83 * tmp27;
    const auto tmp85 = tmp69 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp86 = 3 * (tmp17 > tmp16 ? tmp77 : tmp85);
    const auto tmp87 = tmp86 / 0.1;
    const auto tmp88 = tmp87 * tmp51;
    const auto tmp89 = 2.0 * tmp88;
    const auto tmp90 = 2.0 * tmp87;
    const auto tmp91 = tmp90 * tmp54;
    const auto tmp92 = tmp91 * tmp26;
    const auto tmp93 = -1 * tmp92;
    const auto tmp94 = tmp93 + tmp89;
    const auto tmp95 = tmp94 / tmp23;
    const auto tmp96 = 2 * tmp95;
    const auto tmp97 = tmp96 * tmp26;
    const auto tmp98 = tmp97 * tmp50;
    const auto tmp99 = tmp98 + tmp84;
    const auto tmp100 = -1 * tmp99;
    const auto tmp101 = 0.5 * tmp100;
    const auto tmp102 = tmp31 * tmp69;
    const auto tmp103 = -1 * tmp102;
    const auto tmp104 = tmp103 / tmp28;
    const auto tmp105 = tmp104 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp106 = tmp40 * tmp77;
    const auto tmp107 = -1 * tmp106;
    const auto tmp108 = tmp107 / tmp37;
    const auto tmp109 = 3 * (tmp17 > tmp16 ? tmp108 : tmp105);
    const auto tmp110 = tmp109 / 0.1;
    const auto tmp111 = tmp110 * tmp27;
    const auto tmp112 = tmp62 * tmp87;
    const auto tmp113 = tmp112 + tmp111;
    const auto tmp114 = -1 * tmp113;
    const auto tmp115 = 0.5 * tmp114;
    const auto tmp116 = tmp70 * tmp69;
    const auto tmp117 = -1 * tmp116;
    const auto tmp118 = (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1)) * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp119 = tmp118 + tmp118;
    const auto tmp120 = tmp119 + tmp117;
    const auto tmp121 = tmp120 / tmp28;
    const auto tmp122 = tmp121 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp123 = tmp78 * tmp77;
    const auto tmp124 = -1 * tmp123;
    const auto tmp125 = tmp119 + tmp124;
    const auto tmp126 = tmp125 / tmp37;
    const auto tmp127 = 3 * (tmp17 > tmp16 ? tmp126 : tmp122);
    const auto tmp128 = tmp127 / 0.1;
    const auto tmp129 = tmp128 * tmp27;
    const auto tmp130 = tmp97 * tmp87;
    const auto tmp131 = tmp130 + tmp129;
    const auto tmp132 = -1 * tmp131;
    const auto tmp133 = 0.5 * tmp132;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp66;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp101;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp115;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp133;
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

} // namespace UFLLocalFunctions_98b32c4b5bc0d8083f3d2c394aa33429

PYBIND11_MODULE( localfunction_98b32c4b5bc0d8083f3d2c394aa33429_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_98b32c4b5bc0d8083f3d2c394aa33429::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_98b32c4b5bc0d8083f3d2c394aa33429::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_98b32c4b5bc0d8083f3d2c394aa33429_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
