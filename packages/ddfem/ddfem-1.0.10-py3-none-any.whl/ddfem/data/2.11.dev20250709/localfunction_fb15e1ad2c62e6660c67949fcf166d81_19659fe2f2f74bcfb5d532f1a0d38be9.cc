#ifndef GUARD_fb15e1ad2c62e6660c67949fcf166d81
#define GUARD_fb15e1ad2c62e6660c67949fcf166d81

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

namespace UFLLocalFunctions_fb15e1ad2c62e6660c67949fcf166d81
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
    const auto tmp1 = std::abs( tmp0[ 0 ] );
    const auto tmp2 = 0.2 + tmp1;
    const auto tmp3 = tmp2 * tmp2;
    const auto tmp4 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp5 = tmp4 + tmp3;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -0.5 + tmp7;
    const auto tmp9 = 0.1 + tmp8;
    const auto tmp10 = tmp1 * tmp1;
    const auto tmp11 = std::abs( tmp0[ 1 ] );
    const auto tmp12 = -0.3464101615137755 + tmp11;
    const auto tmp13 = tmp12 * tmp12;
    const auto tmp14 = tmp13 + tmp10;
    const auto tmp15 = 1e-10 + tmp14;
    const auto tmp16 = std::sqrt( tmp15 );
    const auto tmp17 = 0.3464101615137755 * tmp1;
    const auto tmp18 = 0.2 * tmp12;
    const auto tmp19 = -0.1 + (tmp18 > tmp17 ? tmp16 : tmp9);
    const auto tmp20 = 3 * tmp19;
    const auto tmp21 = tmp20 / 0.1;
    const auto tmp22 = std::tanh( tmp21 );
    const auto tmp23 = -1 * tmp22;
    const auto tmp24 = 1 + tmp23;
    const auto tmp25 = 0.5 * tmp24;
    result[ 0 ] = tmp25;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::cosh;
    using std::pow;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = std::abs( tmp0[ 0 ] );
    const auto tmp2 = 0.2 + tmp1;
    const auto tmp3 = tmp2 * tmp2;
    const auto tmp4 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp5 = tmp4 + tmp3;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -0.5 + tmp7;
    const auto tmp9 = 0.1 + tmp8;
    const auto tmp10 = tmp1 * tmp1;
    const auto tmp11 = std::abs( tmp0[ 1 ] );
    const auto tmp12 = -0.3464101615137755 + tmp11;
    const auto tmp13 = tmp12 * tmp12;
    const auto tmp14 = tmp13 + tmp10;
    const auto tmp15 = 1e-10 + tmp14;
    const auto tmp16 = std::sqrt( tmp15 );
    const auto tmp17 = 0.3464101615137755 * tmp1;
    const auto tmp18 = 0.2 * tmp12;
    const auto tmp19 = -0.1 + (tmp18 > tmp17 ? tmp16 : tmp9);
    const auto tmp20 = 3 * tmp19;
    const auto tmp21 = tmp20 / 0.1;
    const auto tmp22 = 2.0 * tmp21;
    const auto tmp23 = std::cosh( tmp22 );
    const auto tmp24 = 1.0 + tmp23;
    const auto tmp25 = std::cosh( tmp21 );
    const auto tmp26 = 2.0 * tmp25;
    const auto tmp27 = tmp26 / tmp24;
    const auto tmp28 = std::pow( tmp27, 2 );
    const auto tmp29 = 2 * tmp7;
    const auto tmp30 = tmp2 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp31 = tmp30 + tmp30;
    const auto tmp32 = tmp31 / tmp29;
    const auto tmp33 = 2 * tmp16;
    const auto tmp34 = tmp1 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp35 = tmp34 + tmp34;
    const auto tmp36 = tmp35 / tmp33;
    const auto tmp37 = 3 * (tmp18 > tmp17 ? tmp36 : tmp32);
    const auto tmp38 = tmp37 / 0.1;
    const auto tmp39 = tmp38 * tmp28;
    const auto tmp40 = -1 * tmp39;
    const auto tmp41 = 0.5 * tmp40;
    const auto tmp42 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp43 = tmp42 / tmp29;
    const auto tmp44 = tmp12 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp45 = tmp44 + tmp44;
    const auto tmp46 = tmp45 / tmp33;
    const auto tmp47 = 3 * (tmp18 > tmp17 ? tmp46 : tmp43);
    const auto tmp48 = tmp47 / 0.1;
    const auto tmp49 = tmp48 * tmp28;
    const auto tmp50 = -1 * tmp49;
    const auto tmp51 = 0.5 * tmp50;
    (result[ 0 ])[ 0 ] = tmp41;
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
    const auto tmp1 = std::abs( tmp0[ 0 ] );
    const auto tmp2 = 0.2 + tmp1;
    const auto tmp3 = tmp2 * tmp2;
    const auto tmp4 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp5 = tmp4 + tmp3;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -0.5 + tmp7;
    const auto tmp9 = 0.1 + tmp8;
    const auto tmp10 = tmp1 * tmp1;
    const auto tmp11 = std::abs( tmp0[ 1 ] );
    const auto tmp12 = -0.3464101615137755 + tmp11;
    const auto tmp13 = tmp12 * tmp12;
    const auto tmp14 = tmp13 + tmp10;
    const auto tmp15 = 1e-10 + tmp14;
    const auto tmp16 = std::sqrt( tmp15 );
    const auto tmp17 = 0.3464101615137755 * tmp1;
    const auto tmp18 = 0.2 * tmp12;
    const auto tmp19 = -0.1 + (tmp18 > tmp17 ? tmp16 : tmp9);
    const auto tmp20 = 3 * tmp19;
    const auto tmp21 = tmp20 / 0.1;
    const auto tmp22 = 2.0 * tmp21;
    const auto tmp23 = std::cosh( tmp22 );
    const auto tmp24 = 1.0 + tmp23;
    const auto tmp25 = std::cosh( tmp21 );
    const auto tmp26 = 2.0 * tmp25;
    const auto tmp27 = tmp26 / tmp24;
    const auto tmp28 = std::pow( tmp27, 2 );
    const auto tmp29 = 2 * tmp7;
    const auto tmp30 = tmp2 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp31 = tmp30 + tmp30;
    const auto tmp32 = tmp31 / tmp29;
    const auto tmp33 = 2 * tmp32;
    const auto tmp34 = tmp33 * tmp32;
    const auto tmp35 = -1 * tmp34;
    const auto tmp36 = (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1)) * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp37 = tmp36 + tmp36;
    const auto tmp38 = tmp37 + tmp35;
    const auto tmp39 = tmp38 / tmp29;
    const auto tmp40 = 2 * tmp16;
    const auto tmp41 = tmp1 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp42 = tmp41 + tmp41;
    const auto tmp43 = tmp42 / tmp40;
    const auto tmp44 = 2 * tmp43;
    const auto tmp45 = tmp44 * tmp43;
    const auto tmp46 = -1 * tmp45;
    const auto tmp47 = tmp37 + tmp46;
    const auto tmp48 = tmp47 / tmp40;
    const auto tmp49 = 3 * (tmp18 > tmp17 ? tmp48 : tmp39);
    const auto tmp50 = tmp49 / 0.1;
    const auto tmp51 = tmp50 * tmp28;
    const auto tmp52 = 3 * (tmp18 > tmp17 ? tmp43 : tmp32);
    const auto tmp53 = tmp52 / 0.1;
    const auto tmp54 = std::sinh( tmp21 );
    const auto tmp55 = tmp53 * tmp54;
    const auto tmp56 = 2.0 * tmp55;
    const auto tmp57 = std::sinh( tmp22 );
    const auto tmp58 = 2.0 * tmp53;
    const auto tmp59 = tmp58 * tmp57;
    const auto tmp60 = tmp59 * tmp27;
    const auto tmp61 = -1 * tmp60;
    const auto tmp62 = tmp61 + tmp56;
    const auto tmp63 = tmp62 / tmp24;
    const auto tmp64 = 2 * tmp63;
    const auto tmp65 = tmp64 * tmp27;
    const auto tmp66 = tmp65 * tmp53;
    const auto tmp67 = tmp66 + tmp51;
    const auto tmp68 = -1 * tmp67;
    const auto tmp69 = 0.5 * tmp68;
    const auto tmp70 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp71 = tmp70 / tmp29;
    const auto tmp72 = 2 * tmp71;
    const auto tmp73 = tmp72 * tmp32;
    const auto tmp74 = -1 * tmp73;
    const auto tmp75 = tmp74 / tmp29;
    const auto tmp76 = tmp12 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp77 = tmp76 + tmp76;
    const auto tmp78 = tmp77 / tmp40;
    const auto tmp79 = 2 * tmp78;
    const auto tmp80 = tmp79 * tmp43;
    const auto tmp81 = -1 * tmp80;
    const auto tmp82 = tmp81 / tmp40;
    const auto tmp83 = 3 * (tmp18 > tmp17 ? tmp82 : tmp75);
    const auto tmp84 = tmp83 / 0.1;
    const auto tmp85 = tmp84 * tmp28;
    const auto tmp86 = 3 * (tmp18 > tmp17 ? tmp78 : tmp71);
    const auto tmp87 = tmp86 / 0.1;
    const auto tmp88 = tmp87 * tmp54;
    const auto tmp89 = 2.0 * tmp88;
    const auto tmp90 = 2.0 * tmp87;
    const auto tmp91 = tmp90 * tmp57;
    const auto tmp92 = tmp91 * tmp27;
    const auto tmp93 = -1 * tmp92;
    const auto tmp94 = tmp93 + tmp89;
    const auto tmp95 = tmp94 / tmp24;
    const auto tmp96 = 2 * tmp95;
    const auto tmp97 = tmp96 * tmp27;
    const auto tmp98 = tmp97 * tmp53;
    const auto tmp99 = tmp98 + tmp85;
    const auto tmp100 = -1 * tmp99;
    const auto tmp101 = 0.5 * tmp100;
    const auto tmp102 = tmp33 * tmp71;
    const auto tmp103 = -1 * tmp102;
    const auto tmp104 = tmp103 / tmp29;
    const auto tmp105 = tmp44 * tmp78;
    const auto tmp106 = -1 * tmp105;
    const auto tmp107 = tmp106 / tmp40;
    const auto tmp108 = 3 * (tmp18 > tmp17 ? tmp107 : tmp104);
    const auto tmp109 = tmp108 / 0.1;
    const auto tmp110 = tmp109 * tmp28;
    const auto tmp111 = tmp65 * tmp87;
    const auto tmp112 = tmp111 + tmp110;
    const auto tmp113 = -1 * tmp112;
    const auto tmp114 = 0.5 * tmp113;
    const auto tmp115 = tmp72 * tmp71;
    const auto tmp116 = -1 * tmp115;
    const auto tmp117 = 2 + tmp116;
    const auto tmp118 = tmp117 / tmp29;
    const auto tmp119 = tmp79 * tmp78;
    const auto tmp120 = -1 * tmp119;
    const auto tmp121 = (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1)) * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp122 = tmp121 + tmp121;
    const auto tmp123 = tmp122 + tmp120;
    const auto tmp124 = tmp123 / tmp40;
    const auto tmp125 = 3 * (tmp18 > tmp17 ? tmp124 : tmp118);
    const auto tmp126 = tmp125 / 0.1;
    const auto tmp127 = tmp126 * tmp28;
    const auto tmp128 = tmp97 * tmp87;
    const auto tmp129 = tmp128 + tmp127;
    const auto tmp130 = -1 * tmp129;
    const auto tmp131 = 0.5 * tmp130;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp69;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp101;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp114;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp131;
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

} // namespace UFLLocalFunctions_fb15e1ad2c62e6660c67949fcf166d81

PYBIND11_MODULE( localfunction_fb15e1ad2c62e6660c67949fcf166d81_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_fb15e1ad2c62e6660c67949fcf166d81::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_fb15e1ad2c62e6660c67949fcf166d81::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_fb15e1ad2c62e6660c67949fcf166d81_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
