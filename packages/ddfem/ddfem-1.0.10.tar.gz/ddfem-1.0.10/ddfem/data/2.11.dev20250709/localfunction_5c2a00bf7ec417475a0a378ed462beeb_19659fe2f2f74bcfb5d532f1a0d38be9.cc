#ifndef GUARD_5c2a00bf7ec417475a0a378ed462beeb
#define GUARD_5c2a00bf7ec417475a0a378ed462beeb

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

namespace UFLLocalFunctions_5c2a00bf7ec417475a0a378ed462beeb
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
    const auto tmp21 = 3 * tmp20;
    const auto tmp22 = tmp21 / 0.1;
    const auto tmp23 = std::tanh( tmp22 );
    const auto tmp24 = -1 * tmp23;
    const auto tmp25 = 1 + tmp24;
    const auto tmp26 = 0.5 * tmp25;
    result[ 0 ] = tmp26;
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
    const auto tmp21 = 3 * tmp20;
    const auto tmp22 = tmp21 / 0.1;
    const auto tmp23 = 2.0 * tmp22;
    const auto tmp24 = std::cosh( tmp23 );
    const auto tmp25 = 1.0 + tmp24;
    const auto tmp26 = std::cosh( tmp22 );
    const auto tmp27 = 2.0 * tmp26;
    const auto tmp28 = tmp27 / tmp25;
    const auto tmp29 = std::pow( tmp28, 2 );
    const auto tmp30 = 2 * tmp7;
    const auto tmp31 = tmp2 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp32 = tmp31 + tmp31;
    const auto tmp33 = tmp32 / tmp30;
    const auto tmp34 = 2 * tmp16;
    const auto tmp35 = tmp1 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp36 = tmp35 + tmp35;
    const auto tmp37 = tmp36 / tmp34;
    const auto tmp38 = -1 * tmp37;
    const auto tmp39 = 3 * (tmp19 > tmp18 ? tmp38 : tmp33);
    const auto tmp40 = tmp39 / 0.1;
    const auto tmp41 = tmp40 * tmp29;
    const auto tmp42 = -1 * tmp41;
    const auto tmp43 = 0.5 * tmp42;
    const auto tmp44 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp45 = tmp44 / tmp30;
    const auto tmp46 = tmp12 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp47 = tmp46 + tmp46;
    const auto tmp48 = tmp47 / tmp34;
    const auto tmp49 = -1 * tmp48;
    const auto tmp50 = 3 * (tmp19 > tmp18 ? tmp49 : tmp45);
    const auto tmp51 = tmp50 / 0.1;
    const auto tmp52 = tmp51 * tmp29;
    const auto tmp53 = -1 * tmp52;
    const auto tmp54 = 0.5 * tmp53;
    (result[ 0 ])[ 0 ] = tmp43;
    (result[ 0 ])[ 1 ] = tmp54;
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
    const auto tmp21 = 3 * tmp20;
    const auto tmp22 = tmp21 / 0.1;
    const auto tmp23 = 2.0 * tmp22;
    const auto tmp24 = std::cosh( tmp23 );
    const auto tmp25 = 1.0 + tmp24;
    const auto tmp26 = std::cosh( tmp22 );
    const auto tmp27 = 2.0 * tmp26;
    const auto tmp28 = tmp27 / tmp25;
    const auto tmp29 = std::pow( tmp28, 2 );
    const auto tmp30 = 2 * tmp7;
    const auto tmp31 = tmp2 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp32 = tmp31 + tmp31;
    const auto tmp33 = tmp32 / tmp30;
    const auto tmp34 = 2 * tmp33;
    const auto tmp35 = tmp34 * tmp33;
    const auto tmp36 = -1 * tmp35;
    const auto tmp37 = (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1)) * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp38 = tmp37 + tmp37;
    const auto tmp39 = tmp38 + tmp36;
    const auto tmp40 = tmp39 / tmp30;
    const auto tmp41 = 2 * tmp16;
    const auto tmp42 = tmp1 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp43 = tmp42 + tmp42;
    const auto tmp44 = tmp43 / tmp41;
    const auto tmp45 = 2 * tmp44;
    const auto tmp46 = tmp45 * tmp44;
    const auto tmp47 = -1 * tmp46;
    const auto tmp48 = tmp38 + tmp47;
    const auto tmp49 = tmp48 / tmp41;
    const auto tmp50 = -1 * tmp49;
    const auto tmp51 = 3 * (tmp19 > tmp18 ? tmp50 : tmp40);
    const auto tmp52 = tmp51 / 0.1;
    const auto tmp53 = tmp52 * tmp29;
    const auto tmp54 = -1 * tmp44;
    const auto tmp55 = 3 * (tmp19 > tmp18 ? tmp54 : tmp33);
    const auto tmp56 = tmp55 / 0.1;
    const auto tmp57 = std::sinh( tmp22 );
    const auto tmp58 = tmp56 * tmp57;
    const auto tmp59 = 2.0 * tmp58;
    const auto tmp60 = std::sinh( tmp23 );
    const auto tmp61 = 2.0 * tmp56;
    const auto tmp62 = tmp61 * tmp60;
    const auto tmp63 = tmp62 * tmp28;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = tmp64 + tmp59;
    const auto tmp66 = tmp65 / tmp25;
    const auto tmp67 = 2 * tmp66;
    const auto tmp68 = tmp67 * tmp28;
    const auto tmp69 = tmp68 * tmp56;
    const auto tmp70 = tmp69 + tmp53;
    const auto tmp71 = -1 * tmp70;
    const auto tmp72 = 0.5 * tmp71;
    const auto tmp73 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp74 = tmp73 / tmp30;
    const auto tmp75 = 2 * tmp74;
    const auto tmp76 = tmp75 * tmp33;
    const auto tmp77 = -1 * tmp76;
    const auto tmp78 = tmp77 / tmp30;
    const auto tmp79 = tmp12 * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp80 = tmp79 + tmp79;
    const auto tmp81 = tmp80 / tmp41;
    const auto tmp82 = 2 * tmp81;
    const auto tmp83 = tmp82 * tmp44;
    const auto tmp84 = -1 * tmp83;
    const auto tmp85 = tmp84 / tmp41;
    const auto tmp86 = -1 * tmp85;
    const auto tmp87 = 3 * (tmp19 > tmp18 ? tmp86 : tmp78);
    const auto tmp88 = tmp87 / 0.1;
    const auto tmp89 = tmp88 * tmp29;
    const auto tmp90 = -1 * tmp81;
    const auto tmp91 = 3 * (tmp19 > tmp18 ? tmp90 : tmp74);
    const auto tmp92 = tmp91 / 0.1;
    const auto tmp93 = tmp92 * tmp57;
    const auto tmp94 = 2.0 * tmp93;
    const auto tmp95 = 2.0 * tmp92;
    const auto tmp96 = tmp95 * tmp60;
    const auto tmp97 = tmp96 * tmp28;
    const auto tmp98 = -1 * tmp97;
    const auto tmp99 = tmp98 + tmp94;
    const auto tmp100 = tmp99 / tmp25;
    const auto tmp101 = 2 * tmp100;
    const auto tmp102 = tmp101 * tmp28;
    const auto tmp103 = tmp102 * tmp56;
    const auto tmp104 = tmp103 + tmp89;
    const auto tmp105 = -1 * tmp104;
    const auto tmp106 = 0.5 * tmp105;
    const auto tmp107 = tmp34 * tmp74;
    const auto tmp108 = -1 * tmp107;
    const auto tmp109 = tmp108 / tmp30;
    const auto tmp110 = tmp45 * tmp81;
    const auto tmp111 = -1 * tmp110;
    const auto tmp112 = tmp111 / tmp41;
    const auto tmp113 = -1 * tmp112;
    const auto tmp114 = 3 * (tmp19 > tmp18 ? tmp113 : tmp109);
    const auto tmp115 = tmp114 / 0.1;
    const auto tmp116 = tmp115 * tmp29;
    const auto tmp117 = tmp68 * tmp92;
    const auto tmp118 = tmp117 + tmp116;
    const auto tmp119 = -1 * tmp118;
    const auto tmp120 = 0.5 * tmp119;
    const auto tmp121 = tmp75 * tmp74;
    const auto tmp122 = -1 * tmp121;
    const auto tmp123 = 2 + tmp122;
    const auto tmp124 = tmp123 / tmp30;
    const auto tmp125 = tmp82 * tmp81;
    const auto tmp126 = -1 * tmp125;
    const auto tmp127 = (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1)) * (tmp0[ 1 ] == 0.0 ? 0.0 : (tmp0[ 1 ] < 0.0 ? -1 : 1));
    const auto tmp128 = tmp127 + tmp127;
    const auto tmp129 = tmp128 + tmp126;
    const auto tmp130 = tmp129 / tmp41;
    const auto tmp131 = -1 * tmp130;
    const auto tmp132 = 3 * (tmp19 > tmp18 ? tmp131 : tmp124);
    const auto tmp133 = tmp132 / 0.1;
    const auto tmp134 = tmp133 * tmp29;
    const auto tmp135 = tmp102 * tmp92;
    const auto tmp136 = tmp135 + tmp134;
    const auto tmp137 = -1 * tmp136;
    const auto tmp138 = 0.5 * tmp137;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp72;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp106;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp120;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp138;
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

} // namespace UFLLocalFunctions_5c2a00bf7ec417475a0a378ed462beeb

PYBIND11_MODULE( localfunction_5c2a00bf7ec417475a0a378ed462beeb_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_5c2a00bf7ec417475a0a378ed462beeb::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_5c2a00bf7ec417475a0a378ed462beeb::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_5c2a00bf7ec417475a0a378ed462beeb_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
