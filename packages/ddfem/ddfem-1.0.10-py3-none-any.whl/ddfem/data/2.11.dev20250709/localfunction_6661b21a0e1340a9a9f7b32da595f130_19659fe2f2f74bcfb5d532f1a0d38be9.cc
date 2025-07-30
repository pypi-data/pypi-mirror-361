#ifndef GUARD_6661b21a0e1340a9a9f7b32da595f130
#define GUARD_6661b21a0e1340a9a9f7b32da595f130

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

namespace UFLLocalFunctions_6661b21a0e1340a9a9f7b32da595f130
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
    using std::min;
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
    const auto tmp11 = std::abs( tmp3 );
    const auto tmp12 = -0.3 + tmp11;
    const auto tmp13 = std::abs( tmp5 );
    const auto tmp14 = -0.8 + tmp13;
    const auto tmp15 = std::max( tmp14, tmp12 );
    const auto tmp16 = std::max( tmp12, 0.0 );
    const auto tmp17 = tmp16 * tmp16;
    const auto tmp18 = std::max( tmp14, 0.0 );
    const auto tmp19 = tmp18 * tmp18;
    const auto tmp20 = tmp19 + tmp17;
    const auto tmp21 = 1e-10 + tmp20;
    const auto tmp22 = std::sqrt( tmp21 );
    const auto tmp23 = std::max( tmp15 > 0.0 ? tmp22 : tmp15, tmp10 );
    const auto tmp24 = -1 * tmp23;
    const auto tmp25 = std::min( tmp15 > 0.0 ? tmp22 : tmp15, tmp10 );
    const auto tmp26 = std::max( tmp25, tmp24 );
    const auto tmp27 = 3 * tmp26;
    const auto tmp28 = tmp27 / tmp1;
    const auto tmp29 = std::tanh( tmp28 );
    const auto tmp30 = -1 * tmp29;
    const auto tmp31 = 1 + tmp30;
    const auto tmp32 = 0.5 * tmp31;
    result[ 0 ] = tmp32;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::cosh;
    using std::max;
    using std::min;
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
    const auto tmp11 = std::abs( tmp3 );
    const auto tmp12 = -0.3 + tmp11;
    const auto tmp13 = std::abs( tmp5 );
    const auto tmp14 = -0.8 + tmp13;
    const auto tmp15 = std::max( tmp14, tmp12 );
    const auto tmp16 = std::max( tmp12, 0.0 );
    const auto tmp17 = tmp16 * tmp16;
    const auto tmp18 = std::max( tmp14, 0.0 );
    const auto tmp19 = tmp18 * tmp18;
    const auto tmp20 = tmp19 + tmp17;
    const auto tmp21 = 1e-10 + tmp20;
    const auto tmp22 = std::sqrt( tmp21 );
    const auto tmp23 = std::max( tmp15 > 0.0 ? tmp22 : tmp15, tmp10 );
    const auto tmp24 = -1 * tmp23;
    const auto tmp25 = std::min( tmp15 > 0.0 ? tmp22 : tmp15, tmp10 );
    const auto tmp26 = std::max( tmp25, tmp24 );
    const auto tmp27 = 3 * tmp26;
    const auto tmp28 = tmp27 / tmp1;
    const auto tmp29 = 2.0 * tmp28;
    const auto tmp30 = std::cosh( tmp29 );
    const auto tmp31 = 1.0 + tmp30;
    const auto tmp32 = std::cosh( tmp28 );
    const auto tmp33 = 2.0 * tmp32;
    const auto tmp34 = tmp33 / tmp31;
    const auto tmp35 = std::pow( tmp34, 2 );
    const auto tmp36 = (tmp14 > tmp12 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp37 = 2 * tmp22;
    const auto tmp38 = (tmp14 > 0.0 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp39 = tmp38 * tmp18;
    const auto tmp40 = tmp39 + tmp39;
    const auto tmp41 = tmp40 / tmp37;
    const auto tmp42 = ((tmp15 > 0.0 ? tmp22 : tmp15) < tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp41 : tmp36);
    const auto tmp43 = 2 * tmp9;
    const auto tmp44 = tmp5 + tmp5;
    const auto tmp45 = tmp44 / tmp43;
    const auto tmp46 = -1 * ((tmp15 > 0.0 ? tmp22 : tmp15) < tmp10 ? 1 : 0.0);
    const auto tmp47 = 1.0 + tmp46;
    const auto tmp48 = tmp47 * tmp45;
    const auto tmp49 = tmp48 + tmp42;
    const auto tmp50 = tmp49 * (tmp25 > tmp24 ? 1 : 0.0);
    const auto tmp51 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp41 : tmp36);
    const auto tmp52 = -1 * ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0);
    const auto tmp53 = 1.0 + tmp52;
    const auto tmp54 = tmp53 * tmp45;
    const auto tmp55 = tmp54 + tmp51;
    const auto tmp56 = -1 * tmp55;
    const auto tmp57 = -1 * (tmp25 > tmp24 ? 1 : 0.0);
    const auto tmp58 = 1.0 + tmp57;
    const auto tmp59 = tmp58 * tmp56;
    const auto tmp60 = tmp59 + tmp50;
    const auto tmp61 = 3 * tmp60;
    const auto tmp62 = tmp61 / tmp1;
    const auto tmp63 = tmp62 * tmp35;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = 0.5 * tmp64;
    const auto tmp66 = -1 * (tmp14 > tmp12 ? 1 : 0.0);
    const auto tmp67 = 1.0 + tmp66;
    const auto tmp68 = tmp67 * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp69 = (tmp12 > 0.0 ? 1 : 0.0) * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp70 = tmp69 * tmp16;
    const auto tmp71 = tmp70 + tmp70;
    const auto tmp72 = tmp71 / tmp37;
    const auto tmp73 = ((tmp15 > 0.0 ? tmp22 : tmp15) < tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp72 : tmp68);
    const auto tmp74 = tmp3 + tmp3;
    const auto tmp75 = tmp74 / tmp43;
    const auto tmp76 = tmp47 * tmp75;
    const auto tmp77 = tmp76 + tmp73;
    const auto tmp78 = tmp77 * (tmp25 > tmp24 ? 1 : 0.0);
    const auto tmp79 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp72 : tmp68);
    const auto tmp80 = tmp53 * tmp75;
    const auto tmp81 = tmp80 + tmp79;
    const auto tmp82 = -1 * tmp81;
    const auto tmp83 = tmp58 * tmp82;
    const auto tmp84 = tmp83 + tmp78;
    const auto tmp85 = 3 * tmp84;
    const auto tmp86 = tmp85 / tmp1;
    const auto tmp87 = tmp86 * tmp35;
    const auto tmp88 = -1 * tmp87;
    const auto tmp89 = 0.5 * tmp88;
    (result[ 0 ])[ 0 ] = tmp65;
    (result[ 0 ])[ 1 ] = tmp89;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::abs;
    using std::cosh;
    using std::max;
    using std::min;
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
    const auto tmp11 = std::abs( tmp3 );
    const auto tmp12 = -0.3 + tmp11;
    const auto tmp13 = std::abs( tmp5 );
    const auto tmp14 = -0.8 + tmp13;
    const auto tmp15 = std::max( tmp14, tmp12 );
    const auto tmp16 = std::max( tmp12, 0.0 );
    const auto tmp17 = tmp16 * tmp16;
    const auto tmp18 = std::max( tmp14, 0.0 );
    const auto tmp19 = tmp18 * tmp18;
    const auto tmp20 = tmp19 + tmp17;
    const auto tmp21 = 1e-10 + tmp20;
    const auto tmp22 = std::sqrt( tmp21 );
    const auto tmp23 = std::max( tmp15 > 0.0 ? tmp22 : tmp15, tmp10 );
    const auto tmp24 = -1 * tmp23;
    const auto tmp25 = std::min( tmp15 > 0.0 ? tmp22 : tmp15, tmp10 );
    const auto tmp26 = std::max( tmp25, tmp24 );
    const auto tmp27 = 3 * tmp26;
    const auto tmp28 = tmp27 / tmp1;
    const auto tmp29 = 2.0 * tmp28;
    const auto tmp30 = std::cosh( tmp29 );
    const auto tmp31 = 1.0 + tmp30;
    const auto tmp32 = std::cosh( tmp28 );
    const auto tmp33 = 2.0 * tmp32;
    const auto tmp34 = tmp33 / tmp31;
    const auto tmp35 = std::pow( tmp34, 2 );
    const auto tmp36 = 2 * tmp22;
    const auto tmp37 = (tmp14 > 0.0 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp38 = tmp37 * tmp18;
    const auto tmp39 = tmp38 + tmp38;
    const auto tmp40 = tmp39 / tmp36;
    const auto tmp41 = 2 * tmp40;
    const auto tmp42 = tmp41 * tmp40;
    const auto tmp43 = -1 * tmp42;
    const auto tmp44 = tmp37 * tmp37;
    const auto tmp45 = tmp44 + tmp44;
    const auto tmp46 = tmp45 + tmp43;
    const auto tmp47 = tmp46 / tmp36;
    const auto tmp48 = ((tmp15 > 0.0 ? tmp22 : tmp15) < tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp47 : 0.0);
    const auto tmp49 = 2 * tmp9;
    const auto tmp50 = tmp5 + tmp5;
    const auto tmp51 = tmp50 / tmp49;
    const auto tmp52 = 2 * tmp51;
    const auto tmp53 = tmp52 * tmp51;
    const auto tmp54 = -1 * tmp53;
    const auto tmp55 = 2 + tmp54;
    const auto tmp56 = tmp55 / tmp49;
    const auto tmp57 = -1 * ((tmp15 > 0.0 ? tmp22 : tmp15) < tmp10 ? 1 : 0.0);
    const auto tmp58 = 1.0 + tmp57;
    const auto tmp59 = tmp58 * tmp56;
    const auto tmp60 = tmp59 + tmp48;
    const auto tmp61 = tmp60 * (tmp25 > tmp24 ? 1 : 0.0);
    const auto tmp62 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp47 : 0.0);
    const auto tmp63 = -1 * ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0);
    const auto tmp64 = 1.0 + tmp63;
    const auto tmp65 = tmp64 * tmp56;
    const auto tmp66 = tmp65 + tmp62;
    const auto tmp67 = -1 * tmp66;
    const auto tmp68 = -1 * (tmp25 > tmp24 ? 1 : 0.0);
    const auto tmp69 = 1.0 + tmp68;
    const auto tmp70 = tmp69 * tmp67;
    const auto tmp71 = tmp70 + tmp61;
    const auto tmp72 = 3 * tmp71;
    const auto tmp73 = tmp72 / tmp1;
    const auto tmp74 = tmp73 * tmp35;
    const auto tmp75 = (tmp14 > tmp12 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp76 = ((tmp15 > 0.0 ? tmp22 : tmp15) < tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp40 : tmp75);
    const auto tmp77 = tmp58 * tmp51;
    const auto tmp78 = tmp77 + tmp76;
    const auto tmp79 = tmp78 * (tmp25 > tmp24 ? 1 : 0.0);
    const auto tmp80 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp40 : tmp75);
    const auto tmp81 = tmp64 * tmp51;
    const auto tmp82 = tmp81 + tmp80;
    const auto tmp83 = -1 * tmp82;
    const auto tmp84 = tmp69 * tmp83;
    const auto tmp85 = tmp84 + tmp79;
    const auto tmp86 = 3 * tmp85;
    const auto tmp87 = tmp86 / tmp1;
    const auto tmp88 = std::sinh( tmp28 );
    const auto tmp89 = tmp87 * tmp88;
    const auto tmp90 = 2.0 * tmp89;
    const auto tmp91 = std::sinh( tmp29 );
    const auto tmp92 = 2.0 * tmp87;
    const auto tmp93 = tmp92 * tmp91;
    const auto tmp94 = tmp93 * tmp34;
    const auto tmp95 = -1 * tmp94;
    const auto tmp96 = tmp95 + tmp90;
    const auto tmp97 = tmp96 / tmp31;
    const auto tmp98 = 2 * tmp97;
    const auto tmp99 = tmp98 * tmp34;
    const auto tmp100 = tmp99 * tmp87;
    const auto tmp101 = tmp100 + tmp74;
    const auto tmp102 = -1 * tmp101;
    const auto tmp103 = 0.5 * tmp102;
    const auto tmp104 = (tmp12 > 0.0 ? 1 : 0.0) * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp105 = tmp104 * tmp16;
    const auto tmp106 = tmp105 + tmp105;
    const auto tmp107 = tmp106 / tmp36;
    const auto tmp108 = 2 * tmp107;
    const auto tmp109 = tmp108 * tmp40;
    const auto tmp110 = -1 * tmp109;
    const auto tmp111 = tmp110 / tmp36;
    const auto tmp112 = ((tmp15 > 0.0 ? tmp22 : tmp15) < tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp111 : 0.0);
    const auto tmp113 = tmp3 + tmp3;
    const auto tmp114 = tmp113 / tmp49;
    const auto tmp115 = 2 * tmp114;
    const auto tmp116 = tmp115 * tmp51;
    const auto tmp117 = -1 * tmp116;
    const auto tmp118 = tmp117 / tmp49;
    const auto tmp119 = tmp58 * tmp118;
    const auto tmp120 = tmp119 + tmp112;
    const auto tmp121 = tmp120 * (tmp25 > tmp24 ? 1 : 0.0);
    const auto tmp122 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp111 : 0.0);
    const auto tmp123 = tmp64 * tmp118;
    const auto tmp124 = tmp123 + tmp122;
    const auto tmp125 = -1 * tmp124;
    const auto tmp126 = tmp69 * tmp125;
    const auto tmp127 = tmp126 + tmp121;
    const auto tmp128 = 3 * tmp127;
    const auto tmp129 = tmp128 / tmp1;
    const auto tmp130 = tmp129 * tmp35;
    const auto tmp131 = -1 * (tmp14 > tmp12 ? 1 : 0.0);
    const auto tmp132 = 1.0 + tmp131;
    const auto tmp133 = tmp132 * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp134 = ((tmp15 > 0.0 ? tmp22 : tmp15) < tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp107 : tmp133);
    const auto tmp135 = tmp58 * tmp114;
    const auto tmp136 = tmp135 + tmp134;
    const auto tmp137 = tmp136 * (tmp25 > tmp24 ? 1 : 0.0);
    const auto tmp138 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp107 : tmp133);
    const auto tmp139 = tmp64 * tmp114;
    const auto tmp140 = tmp139 + tmp138;
    const auto tmp141 = -1 * tmp140;
    const auto tmp142 = tmp69 * tmp141;
    const auto tmp143 = tmp142 + tmp137;
    const auto tmp144 = 3 * tmp143;
    const auto tmp145 = tmp144 / tmp1;
    const auto tmp146 = tmp145 * tmp88;
    const auto tmp147 = 2.0 * tmp146;
    const auto tmp148 = 2.0 * tmp145;
    const auto tmp149 = tmp148 * tmp91;
    const auto tmp150 = tmp149 * tmp34;
    const auto tmp151 = -1 * tmp150;
    const auto tmp152 = tmp151 + tmp147;
    const auto tmp153 = tmp152 / tmp31;
    const auto tmp154 = 2 * tmp153;
    const auto tmp155 = tmp154 * tmp34;
    const auto tmp156 = tmp155 * tmp87;
    const auto tmp157 = tmp156 + tmp130;
    const auto tmp158 = -1 * tmp157;
    const auto tmp159 = 0.5 * tmp158;
    const auto tmp160 = tmp41 * tmp107;
    const auto tmp161 = -1 * tmp160;
    const auto tmp162 = tmp161 / tmp36;
    const auto tmp163 = ((tmp15 > 0.0 ? tmp22 : tmp15) < tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp162 : 0.0);
    const auto tmp164 = tmp52 * tmp114;
    const auto tmp165 = -1 * tmp164;
    const auto tmp166 = tmp165 / tmp49;
    const auto tmp167 = tmp58 * tmp166;
    const auto tmp168 = tmp167 + tmp163;
    const auto tmp169 = tmp168 * (tmp25 > tmp24 ? 1 : 0.0);
    const auto tmp170 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp162 : 0.0);
    const auto tmp171 = tmp64 * tmp166;
    const auto tmp172 = tmp171 + tmp170;
    const auto tmp173 = -1 * tmp172;
    const auto tmp174 = tmp69 * tmp173;
    const auto tmp175 = tmp174 + tmp169;
    const auto tmp176 = 3 * tmp175;
    const auto tmp177 = tmp176 / tmp1;
    const auto tmp178 = tmp177 * tmp35;
    const auto tmp179 = tmp99 * tmp145;
    const auto tmp180 = tmp179 + tmp178;
    const auto tmp181 = -1 * tmp180;
    const auto tmp182 = 0.5 * tmp181;
    const auto tmp183 = tmp108 * tmp107;
    const auto tmp184 = -1 * tmp183;
    const auto tmp185 = tmp104 * tmp104;
    const auto tmp186 = tmp185 + tmp185;
    const auto tmp187 = tmp186 + tmp184;
    const auto tmp188 = tmp187 / tmp36;
    const auto tmp189 = ((tmp15 > 0.0 ? tmp22 : tmp15) < tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp188 : 0.0);
    const auto tmp190 = tmp115 * tmp114;
    const auto tmp191 = -1 * tmp190;
    const auto tmp192 = 2 + tmp191;
    const auto tmp193 = tmp192 / tmp49;
    const auto tmp194 = tmp58 * tmp193;
    const auto tmp195 = tmp194 + tmp189;
    const auto tmp196 = tmp195 * (tmp25 > tmp24 ? 1 : 0.0);
    const auto tmp197 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp188 : 0.0);
    const auto tmp198 = tmp64 * tmp193;
    const auto tmp199 = tmp198 + tmp197;
    const auto tmp200 = -1 * tmp199;
    const auto tmp201 = tmp69 * tmp200;
    const auto tmp202 = tmp201 + tmp196;
    const auto tmp203 = 3 * tmp202;
    const auto tmp204 = tmp203 / tmp1;
    const auto tmp205 = tmp204 * tmp35;
    const auto tmp206 = tmp155 * tmp145;
    const auto tmp207 = tmp206 + tmp205;
    const auto tmp208 = -1 * tmp207;
    const auto tmp209 = 0.5 * tmp208;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp103;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp159;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp182;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp209;
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

} // namespace UFLLocalFunctions_6661b21a0e1340a9a9f7b32da595f130

PYBIND11_MODULE( localfunction_6661b21a0e1340a9a9f7b32da595f130_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_6661b21a0e1340a9a9f7b32da595f130::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_6661b21a0e1340a9a9f7b32da595f130::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_6661b21a0e1340a9a9f7b32da595f130_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
