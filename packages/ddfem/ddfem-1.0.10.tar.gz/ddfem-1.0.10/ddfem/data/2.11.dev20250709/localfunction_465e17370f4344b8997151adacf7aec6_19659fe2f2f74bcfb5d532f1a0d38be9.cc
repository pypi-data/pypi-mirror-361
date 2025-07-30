#ifndef GUARD_465e17370f4344b8997151adacf7aec6
#define GUARD_465e17370f4344b8997151adacf7aec6

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

namespace UFLLocalFunctions_465e17370f4344b8997151adacf7aec6
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
    using std::tanh;
    const auto tmp0 = std::max( 0.1, 0.1 );
    const auto tmp1 = std::max( tmp0, 0.1 );
    GlobalCoordinateType tmp2 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp3 = -0.3 + tmp2[ 1 ];
    const auto tmp4 = tmp3 * tmp3;
    const auto tmp5 = -0.1 + tmp2[ 0 ];
    const auto tmp6 = tmp5 * tmp5;
    const auto tmp7 = tmp6 + tmp4;
    const auto tmp8 = 1e-10 + tmp7;
    const auto tmp9 = std::sqrt( tmp8 );
    const auto tmp10 = -0.5 + tmp9;
    const auto tmp11 = -1 * tmp10;
    const auto tmp12 = std::abs( tmp3 );
    const auto tmp13 = -0.3 + tmp12;
    const auto tmp14 = std::abs( tmp5 );
    const auto tmp15 = -0.8 + tmp14;
    const auto tmp16 = std::max( tmp15, tmp13 );
    const auto tmp17 = std::max( tmp13, 0.0 );
    const auto tmp18 = tmp17 * tmp17;
    const auto tmp19 = std::max( tmp15, 0.0 );
    const auto tmp20 = tmp19 * tmp19;
    const auto tmp21 = tmp20 + tmp18;
    const auto tmp22 = 1e-10 + tmp21;
    const auto tmp23 = std::sqrt( tmp22 );
    const auto tmp24 = std::max( tmp16 > 0.0 ? tmp23 : tmp16, tmp11 );
    const auto tmp25 = 3 * tmp24;
    const auto tmp26 = tmp25 / tmp1;
    const auto tmp27 = std::tanh( tmp26 );
    const auto tmp28 = -1 * tmp27;
    const auto tmp29 = 1 + tmp28;
    const auto tmp30 = 0.5 * tmp29;
    result[ 0 ] = tmp30;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::cosh;
    using std::max;
    using std::pow;
    using std::sqrt;
    const auto tmp0 = std::max( 0.1, 0.1 );
    const auto tmp1 = std::max( tmp0, 0.1 );
    GlobalCoordinateType tmp2 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp3 = -0.3 + tmp2[ 1 ];
    const auto tmp4 = tmp3 * tmp3;
    const auto tmp5 = -0.1 + tmp2[ 0 ];
    const auto tmp6 = tmp5 * tmp5;
    const auto tmp7 = tmp6 + tmp4;
    const auto tmp8 = 1e-10 + tmp7;
    const auto tmp9 = std::sqrt( tmp8 );
    const auto tmp10 = -0.5 + tmp9;
    const auto tmp11 = -1 * tmp10;
    const auto tmp12 = std::abs( tmp3 );
    const auto tmp13 = -0.3 + tmp12;
    const auto tmp14 = std::abs( tmp5 );
    const auto tmp15 = -0.8 + tmp14;
    const auto tmp16 = std::max( tmp15, tmp13 );
    const auto tmp17 = std::max( tmp13, 0.0 );
    const auto tmp18 = tmp17 * tmp17;
    const auto tmp19 = std::max( tmp15, 0.0 );
    const auto tmp20 = tmp19 * tmp19;
    const auto tmp21 = tmp20 + tmp18;
    const auto tmp22 = 1e-10 + tmp21;
    const auto tmp23 = std::sqrt( tmp22 );
    const auto tmp24 = std::max( tmp16 > 0.0 ? tmp23 : tmp16, tmp11 );
    const auto tmp25 = 3 * tmp24;
    const auto tmp26 = tmp25 / tmp1;
    const auto tmp27 = 2.0 * tmp26;
    const auto tmp28 = std::cosh( tmp27 );
    const auto tmp29 = 1.0 + tmp28;
    const auto tmp30 = std::cosh( tmp26 );
    const auto tmp31 = 2.0 * tmp30;
    const auto tmp32 = tmp31 / tmp29;
    const auto tmp33 = std::pow( tmp32, 2 );
    const auto tmp34 = (tmp15 > tmp13 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp35 = 2 * tmp23;
    const auto tmp36 = (tmp15 > 0.0 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp37 = tmp36 * tmp19;
    const auto tmp38 = tmp37 + tmp37;
    const auto tmp39 = tmp38 / tmp35;
    const auto tmp40 = ((tmp16 > 0.0 ? tmp23 : tmp16) > tmp11 ? 1 : 0.0) * (tmp16 > 0.0 ? tmp39 : tmp34);
    const auto tmp41 = 2 * tmp9;
    const auto tmp42 = tmp5 + tmp5;
    const auto tmp43 = tmp42 / tmp41;
    const auto tmp44 = -1 * tmp43;
    const auto tmp45 = -1 * ((tmp16 > 0.0 ? tmp23 : tmp16) > tmp11 ? 1 : 0.0);
    const auto tmp46 = 1.0 + tmp45;
    const auto tmp47 = tmp46 * tmp44;
    const auto tmp48 = tmp47 + tmp40;
    const auto tmp49 = 3 * tmp48;
    const auto tmp50 = tmp49 / tmp1;
    const auto tmp51 = tmp50 * tmp33;
    const auto tmp52 = -1 * tmp51;
    const auto tmp53 = 0.5 * tmp52;
    const auto tmp54 = -1 * (tmp15 > tmp13 ? 1 : 0.0);
    const auto tmp55 = 1.0 + tmp54;
    const auto tmp56 = tmp55 * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp57 = (tmp13 > 0.0 ? 1 : 0.0) * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp58 = tmp57 * tmp17;
    const auto tmp59 = tmp58 + tmp58;
    const auto tmp60 = tmp59 / tmp35;
    const auto tmp61 = ((tmp16 > 0.0 ? tmp23 : tmp16) > tmp11 ? 1 : 0.0) * (tmp16 > 0.0 ? tmp60 : tmp56);
    const auto tmp62 = tmp3 + tmp3;
    const auto tmp63 = tmp62 / tmp41;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = tmp46 * tmp64;
    const auto tmp66 = tmp65 + tmp61;
    const auto tmp67 = 3 * tmp66;
    const auto tmp68 = tmp67 / tmp1;
    const auto tmp69 = tmp68 * tmp33;
    const auto tmp70 = -1 * tmp69;
    const auto tmp71 = 0.5 * tmp70;
    (result[ 0 ])[ 0 ] = tmp53;
    (result[ 0 ])[ 1 ] = tmp71;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::abs;
    using std::cosh;
    using std::max;
    using std::pow;
    using std::sinh;
    using std::sqrt;
    const auto tmp0 = std::max( 0.1, 0.1 );
    const auto tmp1 = std::max( tmp0, 0.1 );
    GlobalCoordinateType tmp2 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp3 = -0.3 + tmp2[ 1 ];
    const auto tmp4 = tmp3 * tmp3;
    const auto tmp5 = -0.1 + tmp2[ 0 ];
    const auto tmp6 = tmp5 * tmp5;
    const auto tmp7 = tmp6 + tmp4;
    const auto tmp8 = 1e-10 + tmp7;
    const auto tmp9 = std::sqrt( tmp8 );
    const auto tmp10 = -0.5 + tmp9;
    const auto tmp11 = -1 * tmp10;
    const auto tmp12 = std::abs( tmp3 );
    const auto tmp13 = -0.3 + tmp12;
    const auto tmp14 = std::abs( tmp5 );
    const auto tmp15 = -0.8 + tmp14;
    const auto tmp16 = std::max( tmp15, tmp13 );
    const auto tmp17 = std::max( tmp13, 0.0 );
    const auto tmp18 = tmp17 * tmp17;
    const auto tmp19 = std::max( tmp15, 0.0 );
    const auto tmp20 = tmp19 * tmp19;
    const auto tmp21 = tmp20 + tmp18;
    const auto tmp22 = 1e-10 + tmp21;
    const auto tmp23 = std::sqrt( tmp22 );
    const auto tmp24 = std::max( tmp16 > 0.0 ? tmp23 : tmp16, tmp11 );
    const auto tmp25 = 3 * tmp24;
    const auto tmp26 = tmp25 / tmp1;
    const auto tmp27 = 2.0 * tmp26;
    const auto tmp28 = std::cosh( tmp27 );
    const auto tmp29 = 1.0 + tmp28;
    const auto tmp30 = std::cosh( tmp26 );
    const auto tmp31 = 2.0 * tmp30;
    const auto tmp32 = tmp31 / tmp29;
    const auto tmp33 = std::pow( tmp32, 2 );
    const auto tmp34 = 2 * tmp23;
    const auto tmp35 = (tmp15 > 0.0 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp36 = tmp35 * tmp19;
    const auto tmp37 = tmp36 + tmp36;
    const auto tmp38 = tmp37 / tmp34;
    const auto tmp39 = 2 * tmp38;
    const auto tmp40 = tmp39 * tmp38;
    const auto tmp41 = -1 * tmp40;
    const auto tmp42 = tmp35 * tmp35;
    const auto tmp43 = tmp42 + tmp42;
    const auto tmp44 = tmp43 + tmp41;
    const auto tmp45 = tmp44 / tmp34;
    const auto tmp46 = ((tmp16 > 0.0 ? tmp23 : tmp16) > tmp11 ? 1 : 0.0) * (tmp16 > 0.0 ? tmp45 : 0.0);
    const auto tmp47 = 2 * tmp9;
    const auto tmp48 = tmp5 + tmp5;
    const auto tmp49 = tmp48 / tmp47;
    const auto tmp50 = 2 * tmp49;
    const auto tmp51 = tmp50 * tmp49;
    const auto tmp52 = -1 * tmp51;
    const auto tmp53 = 2 + tmp52;
    const auto tmp54 = tmp53 / tmp47;
    const auto tmp55 = -1 * tmp54;
    const auto tmp56 = -1 * ((tmp16 > 0.0 ? tmp23 : tmp16) > tmp11 ? 1 : 0.0);
    const auto tmp57 = 1.0 + tmp56;
    const auto tmp58 = tmp57 * tmp55;
    const auto tmp59 = tmp58 + tmp46;
    const auto tmp60 = 3 * tmp59;
    const auto tmp61 = tmp60 / tmp1;
    const auto tmp62 = tmp61 * tmp33;
    const auto tmp63 = (tmp15 > tmp13 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp64 = ((tmp16 > 0.0 ? tmp23 : tmp16) > tmp11 ? 1 : 0.0) * (tmp16 > 0.0 ? tmp38 : tmp63);
    const auto tmp65 = -1 * tmp49;
    const auto tmp66 = tmp57 * tmp65;
    const auto tmp67 = tmp66 + tmp64;
    const auto tmp68 = 3 * tmp67;
    const auto tmp69 = tmp68 / tmp1;
    const auto tmp70 = std::sinh( tmp26 );
    const auto tmp71 = tmp69 * tmp70;
    const auto tmp72 = 2.0 * tmp71;
    const auto tmp73 = std::sinh( tmp27 );
    const auto tmp74 = 2.0 * tmp69;
    const auto tmp75 = tmp74 * tmp73;
    const auto tmp76 = tmp75 * tmp32;
    const auto tmp77 = -1 * tmp76;
    const auto tmp78 = tmp77 + tmp72;
    const auto tmp79 = tmp78 / tmp29;
    const auto tmp80 = 2 * tmp79;
    const auto tmp81 = tmp80 * tmp32;
    const auto tmp82 = tmp81 * tmp69;
    const auto tmp83 = tmp82 + tmp62;
    const auto tmp84 = -1 * tmp83;
    const auto tmp85 = 0.5 * tmp84;
    const auto tmp86 = (tmp13 > 0.0 ? 1 : 0.0) * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp87 = tmp86 * tmp17;
    const auto tmp88 = tmp87 + tmp87;
    const auto tmp89 = tmp88 / tmp34;
    const auto tmp90 = 2 * tmp89;
    const auto tmp91 = tmp90 * tmp38;
    const auto tmp92 = -1 * tmp91;
    const auto tmp93 = tmp92 / tmp34;
    const auto tmp94 = ((tmp16 > 0.0 ? tmp23 : tmp16) > tmp11 ? 1 : 0.0) * (tmp16 > 0.0 ? tmp93 : 0.0);
    const auto tmp95 = tmp3 + tmp3;
    const auto tmp96 = tmp95 / tmp47;
    const auto tmp97 = 2 * tmp96;
    const auto tmp98 = tmp97 * tmp49;
    const auto tmp99 = -1 * tmp98;
    const auto tmp100 = tmp99 / tmp47;
    const auto tmp101 = -1 * tmp100;
    const auto tmp102 = tmp57 * tmp101;
    const auto tmp103 = tmp102 + tmp94;
    const auto tmp104 = 3 * tmp103;
    const auto tmp105 = tmp104 / tmp1;
    const auto tmp106 = tmp105 * tmp33;
    const auto tmp107 = -1 * (tmp15 > tmp13 ? 1 : 0.0);
    const auto tmp108 = 1.0 + tmp107;
    const auto tmp109 = tmp108 * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp110 = ((tmp16 > 0.0 ? tmp23 : tmp16) > tmp11 ? 1 : 0.0) * (tmp16 > 0.0 ? tmp89 : tmp109);
    const auto tmp111 = -1 * tmp96;
    const auto tmp112 = tmp57 * tmp111;
    const auto tmp113 = tmp112 + tmp110;
    const auto tmp114 = 3 * tmp113;
    const auto tmp115 = tmp114 / tmp1;
    const auto tmp116 = tmp115 * tmp70;
    const auto tmp117 = 2.0 * tmp116;
    const auto tmp118 = 2.0 * tmp115;
    const auto tmp119 = tmp118 * tmp73;
    const auto tmp120 = tmp119 * tmp32;
    const auto tmp121 = -1 * tmp120;
    const auto tmp122 = tmp121 + tmp117;
    const auto tmp123 = tmp122 / tmp29;
    const auto tmp124 = 2 * tmp123;
    const auto tmp125 = tmp124 * tmp32;
    const auto tmp126 = tmp125 * tmp69;
    const auto tmp127 = tmp126 + tmp106;
    const auto tmp128 = -1 * tmp127;
    const auto tmp129 = 0.5 * tmp128;
    const auto tmp130 = tmp39 * tmp89;
    const auto tmp131 = -1 * tmp130;
    const auto tmp132 = tmp131 / tmp34;
    const auto tmp133 = ((tmp16 > 0.0 ? tmp23 : tmp16) > tmp11 ? 1 : 0.0) * (tmp16 > 0.0 ? tmp132 : 0.0);
    const auto tmp134 = tmp50 * tmp96;
    const auto tmp135 = -1 * tmp134;
    const auto tmp136 = tmp135 / tmp47;
    const auto tmp137 = -1 * tmp136;
    const auto tmp138 = tmp57 * tmp137;
    const auto tmp139 = tmp138 + tmp133;
    const auto tmp140 = 3 * tmp139;
    const auto tmp141 = tmp140 / tmp1;
    const auto tmp142 = tmp141 * tmp33;
    const auto tmp143 = tmp81 * tmp115;
    const auto tmp144 = tmp143 + tmp142;
    const auto tmp145 = -1 * tmp144;
    const auto tmp146 = 0.5 * tmp145;
    const auto tmp147 = tmp90 * tmp89;
    const auto tmp148 = -1 * tmp147;
    const auto tmp149 = tmp86 * tmp86;
    const auto tmp150 = tmp149 + tmp149;
    const auto tmp151 = tmp150 + tmp148;
    const auto tmp152 = tmp151 / tmp34;
    const auto tmp153 = ((tmp16 > 0.0 ? tmp23 : tmp16) > tmp11 ? 1 : 0.0) * (tmp16 > 0.0 ? tmp152 : 0.0);
    const auto tmp154 = tmp97 * tmp96;
    const auto tmp155 = -1 * tmp154;
    const auto tmp156 = 2 + tmp155;
    const auto tmp157 = tmp156 / tmp47;
    const auto tmp158 = -1 * tmp157;
    const auto tmp159 = tmp57 * tmp158;
    const auto tmp160 = tmp159 + tmp153;
    const auto tmp161 = 3 * tmp160;
    const auto tmp162 = tmp161 / tmp1;
    const auto tmp163 = tmp162 * tmp33;
    const auto tmp164 = tmp125 * tmp115;
    const auto tmp165 = tmp164 + tmp163;
    const auto tmp166 = -1 * tmp165;
    const auto tmp167 = 0.5 * tmp166;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp85;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp129;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp146;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp167;
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

} // namespace UFLLocalFunctions_465e17370f4344b8997151adacf7aec6

PYBIND11_MODULE( localfunction_465e17370f4344b8997151adacf7aec6_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_465e17370f4344b8997151adacf7aec6::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_465e17370f4344b8997151adacf7aec6::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_465e17370f4344b8997151adacf7aec6_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
