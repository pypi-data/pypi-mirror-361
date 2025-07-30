#ifndef GUARD_1460b632dc5919e94a2147108f4f34f4
#define GUARD_1460b632dc5919e94a2147108f4f34f4

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

namespace UFLLocalFunctions_1460b632dc5919e94a2147108f4f34f4
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
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = std::abs( tmp0[ 0 ] );
    const auto tmp2 = 0.5877852522924731 * tmp1;
    const auto tmp3 = 0.8090169943749475 * tmp0[ 1 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = std::max( tmp4, 0.0 );
    const auto tmp6 = std::min( tmp5, 0.5 );
    const auto tmp7 = 0.5877852522924731 * tmp6;
    const auto tmp8 = -1 * tmp7;
    const auto tmp9 = tmp8 + tmp1;
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = 0.8090169943749475 * tmp6;
    const auto tmp12 = -1 * tmp11;
    const auto tmp13 = tmp0[ 1 ] + tmp12;
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp14 + tmp10;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = 0.8090169943749475 * tmp1;
    const auto tmp19 = 0.5877852522924731 * tmp0[ 1 ];
    const auto tmp20 = -1 * tmp19;
    const auto tmp21 = tmp20 + tmp18;
    const auto tmp22 = (tmp21 > 0.0 ? 1 : -1) * tmp17;
    const auto tmp23 = tmp1 * tmp1;
    const auto tmp24 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp25 = tmp24 + tmp23;
    const auto tmp26 = 1e-10 + tmp25;
    const auto tmp27 = std::sqrt( tmp26 );
    const auto tmp28 = -0.5 + tmp27;
    const auto tmp29 = std::max( tmp28, tmp22 );
    const auto tmp30 = 3 * tmp29;
    const auto tmp31 = tmp30 / 0.1;
    const auto tmp32 = std::tanh( tmp31 );
    const auto tmp33 = -1 * tmp32;
    const auto tmp34 = 1 + tmp33;
    const auto tmp35 = 0.5 * tmp34;
    result[ 0 ] = tmp35;
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
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = std::abs( tmp0[ 0 ] );
    const auto tmp2 = 0.5877852522924731 * tmp1;
    const auto tmp3 = 0.8090169943749475 * tmp0[ 1 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = std::max( tmp4, 0.0 );
    const auto tmp6 = std::min( tmp5, 0.5 );
    const auto tmp7 = 0.5877852522924731 * tmp6;
    const auto tmp8 = -1 * tmp7;
    const auto tmp9 = tmp8 + tmp1;
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = 0.8090169943749475 * tmp6;
    const auto tmp12 = -1 * tmp11;
    const auto tmp13 = tmp0[ 1 ] + tmp12;
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp14 + tmp10;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = 0.8090169943749475 * tmp1;
    const auto tmp19 = 0.5877852522924731 * tmp0[ 1 ];
    const auto tmp20 = -1 * tmp19;
    const auto tmp21 = tmp20 + tmp18;
    const auto tmp22 = (tmp21 > 0.0 ? 1 : -1) * tmp17;
    const auto tmp23 = tmp1 * tmp1;
    const auto tmp24 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp25 = tmp24 + tmp23;
    const auto tmp26 = 1e-10 + tmp25;
    const auto tmp27 = std::sqrt( tmp26 );
    const auto tmp28 = -0.5 + tmp27;
    const auto tmp29 = std::max( tmp28, tmp22 );
    const auto tmp30 = 3 * tmp29;
    const auto tmp31 = tmp30 / 0.1;
    const auto tmp32 = 2.0 * tmp31;
    const auto tmp33 = std::cosh( tmp32 );
    const auto tmp34 = 1.0 + tmp33;
    const auto tmp35 = std::cosh( tmp31 );
    const auto tmp36 = 2.0 * tmp35;
    const auto tmp37 = tmp36 / tmp34;
    const auto tmp38 = std::pow( tmp37, 2 );
    const auto tmp39 = 2 * tmp27;
    const auto tmp40 = tmp1 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp41 = tmp40 + tmp40;
    const auto tmp42 = tmp41 / tmp39;
    const auto tmp43 = tmp42 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp44 = 2 * tmp17;
    const auto tmp45 = 0.5877852522924731 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp46 = tmp45 * (tmp4 > 0.0 ? 1 : 0.0);
    const auto tmp47 = tmp46 * (tmp5 < 0.5 ? 1 : 0.0);
    const auto tmp48 = 0.8090169943749475 * tmp47;
    const auto tmp49 = -1 * tmp48;
    const auto tmp50 = tmp13 * tmp49;
    const auto tmp51 = tmp50 + tmp50;
    const auto tmp52 = 0.5877852522924731 * tmp47;
    const auto tmp53 = -1 * tmp52;
    const auto tmp54 = tmp53 + (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp55 = tmp9 * tmp54;
    const auto tmp56 = tmp55 + tmp55;
    const auto tmp57 = tmp56 + tmp51;
    const auto tmp58 = tmp57 / tmp44;
    const auto tmp59 = tmp58 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp60 = -1 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp61 = 1.0 + tmp60;
    const auto tmp62 = tmp61 * tmp59;
    const auto tmp63 = tmp62 + tmp43;
    const auto tmp64 = 3 * tmp63;
    const auto tmp65 = tmp64 / 0.1;
    const auto tmp66 = tmp65 * tmp38;
    const auto tmp67 = -1 * tmp66;
    const auto tmp68 = 0.5 * tmp67;
    const auto tmp69 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp70 = tmp69 / tmp39;
    const auto tmp71 = tmp70 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp72 = 0.8090169943749475 * (tmp4 > 0.0 ? 1 : 0.0);
    const auto tmp73 = tmp72 * (tmp5 < 0.5 ? 1 : 0.0);
    const auto tmp74 = 0.5877852522924731 * tmp73;
    const auto tmp75 = -1 * tmp74;
    const auto tmp76 = tmp9 * tmp75;
    const auto tmp77 = tmp76 + tmp76;
    const auto tmp78 = 0.8090169943749475 * tmp73;
    const auto tmp79 = -1 * tmp78;
    const auto tmp80 = 1 + tmp79;
    const auto tmp81 = tmp80 * tmp13;
    const auto tmp82 = tmp81 + tmp81;
    const auto tmp83 = tmp82 + tmp77;
    const auto tmp84 = tmp83 / tmp44;
    const auto tmp85 = tmp84 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp86 = tmp61 * tmp85;
    const auto tmp87 = tmp86 + tmp71;
    const auto tmp88 = 3 * tmp87;
    const auto tmp89 = tmp88 / 0.1;
    const auto tmp90 = tmp89 * tmp38;
    const auto tmp91 = -1 * tmp90;
    const auto tmp92 = 0.5 * tmp91;
    (result[ 0 ])[ 0 ] = tmp68;
    (result[ 0 ])[ 1 ] = tmp92;
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
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = std::abs( tmp0[ 0 ] );
    const auto tmp2 = 0.5877852522924731 * tmp1;
    const auto tmp3 = 0.8090169943749475 * tmp0[ 1 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = std::max( tmp4, 0.0 );
    const auto tmp6 = std::min( tmp5, 0.5 );
    const auto tmp7 = 0.5877852522924731 * tmp6;
    const auto tmp8 = -1 * tmp7;
    const auto tmp9 = tmp8 + tmp1;
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = 0.8090169943749475 * tmp6;
    const auto tmp12 = -1 * tmp11;
    const auto tmp13 = tmp0[ 1 ] + tmp12;
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp14 + tmp10;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = 0.8090169943749475 * tmp1;
    const auto tmp19 = 0.5877852522924731 * tmp0[ 1 ];
    const auto tmp20 = -1 * tmp19;
    const auto tmp21 = tmp20 + tmp18;
    const auto tmp22 = (tmp21 > 0.0 ? 1 : -1) * tmp17;
    const auto tmp23 = tmp1 * tmp1;
    const auto tmp24 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp25 = tmp24 + tmp23;
    const auto tmp26 = 1e-10 + tmp25;
    const auto tmp27 = std::sqrt( tmp26 );
    const auto tmp28 = -0.5 + tmp27;
    const auto tmp29 = std::max( tmp28, tmp22 );
    const auto tmp30 = 3 * tmp29;
    const auto tmp31 = tmp30 / 0.1;
    const auto tmp32 = 2.0 * tmp31;
    const auto tmp33 = std::cosh( tmp32 );
    const auto tmp34 = 1.0 + tmp33;
    const auto tmp35 = std::cosh( tmp31 );
    const auto tmp36 = 2.0 * tmp35;
    const auto tmp37 = tmp36 / tmp34;
    const auto tmp38 = std::pow( tmp37, 2 );
    const auto tmp39 = 2 * tmp27;
    const auto tmp40 = tmp1 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp41 = tmp40 + tmp40;
    const auto tmp42 = tmp41 / tmp39;
    const auto tmp43 = 2 * tmp42;
    const auto tmp44 = tmp43 * tmp42;
    const auto tmp45 = -1 * tmp44;
    const auto tmp46 = (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1)) * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp47 = tmp46 + tmp46;
    const auto tmp48 = tmp47 + tmp45;
    const auto tmp49 = tmp48 / tmp39;
    const auto tmp50 = tmp49 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp51 = 2 * tmp17;
    const auto tmp52 = 0.5877852522924731 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp53 = tmp52 * (tmp4 > 0.0 ? 1 : 0.0);
    const auto tmp54 = tmp53 * (tmp5 < 0.5 ? 1 : 0.0);
    const auto tmp55 = 0.8090169943749475 * tmp54;
    const auto tmp56 = -1 * tmp55;
    const auto tmp57 = tmp13 * tmp56;
    const auto tmp58 = tmp57 + tmp57;
    const auto tmp59 = 0.5877852522924731 * tmp54;
    const auto tmp60 = -1 * tmp59;
    const auto tmp61 = tmp60 + (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp62 = tmp9 * tmp61;
    const auto tmp63 = tmp62 + tmp62;
    const auto tmp64 = tmp63 + tmp58;
    const auto tmp65 = tmp64 / tmp51;
    const auto tmp66 = 2 * tmp65;
    const auto tmp67 = tmp66 * tmp65;
    const auto tmp68 = -1 * tmp67;
    const auto tmp69 = tmp56 * tmp56;
    const auto tmp70 = tmp69 + tmp69;
    const auto tmp71 = tmp61 * tmp61;
    const auto tmp72 = tmp71 + tmp71;
    const auto tmp73 = tmp72 + tmp70;
    const auto tmp74 = tmp73 + tmp68;
    const auto tmp75 = tmp74 / tmp51;
    const auto tmp76 = tmp75 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp77 = -1 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp78 = 1.0 + tmp77;
    const auto tmp79 = tmp78 * tmp76;
    const auto tmp80 = tmp79 + tmp50;
    const auto tmp81 = 3 * tmp80;
    const auto tmp82 = tmp81 / 0.1;
    const auto tmp83 = tmp82 * tmp38;
    const auto tmp84 = tmp42 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp85 = tmp65 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp86 = tmp78 * tmp85;
    const auto tmp87 = tmp86 + tmp84;
    const auto tmp88 = 3 * tmp87;
    const auto tmp89 = tmp88 / 0.1;
    const auto tmp90 = std::sinh( tmp31 );
    const auto tmp91 = tmp89 * tmp90;
    const auto tmp92 = 2.0 * tmp91;
    const auto tmp93 = std::sinh( tmp32 );
    const auto tmp94 = 2.0 * tmp89;
    const auto tmp95 = tmp94 * tmp93;
    const auto tmp96 = tmp95 * tmp37;
    const auto tmp97 = -1 * tmp96;
    const auto tmp98 = tmp97 + tmp92;
    const auto tmp99 = tmp98 / tmp34;
    const auto tmp100 = 2 * tmp99;
    const auto tmp101 = tmp100 * tmp37;
    const auto tmp102 = tmp101 * tmp89;
    const auto tmp103 = tmp102 + tmp83;
    const auto tmp104 = -1 * tmp103;
    const auto tmp105 = 0.5 * tmp104;
    const auto tmp106 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp107 = tmp106 / tmp39;
    const auto tmp108 = 2 * tmp107;
    const auto tmp109 = tmp108 * tmp42;
    const auto tmp110 = -1 * tmp109;
    const auto tmp111 = tmp110 / tmp39;
    const auto tmp112 = tmp111 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp113 = 0.8090169943749475 * (tmp4 > 0.0 ? 1 : 0.0);
    const auto tmp114 = tmp113 * (tmp5 < 0.5 ? 1 : 0.0);
    const auto tmp115 = 0.5877852522924731 * tmp114;
    const auto tmp116 = -1 * tmp115;
    const auto tmp117 = tmp9 * tmp116;
    const auto tmp118 = tmp117 + tmp117;
    const auto tmp119 = 0.8090169943749475 * tmp114;
    const auto tmp120 = -1 * tmp119;
    const auto tmp121 = 1 + tmp120;
    const auto tmp122 = tmp121 * tmp13;
    const auto tmp123 = tmp122 + tmp122;
    const auto tmp124 = tmp123 + tmp118;
    const auto tmp125 = tmp124 / tmp51;
    const auto tmp126 = 2 * tmp125;
    const auto tmp127 = tmp126 * tmp65;
    const auto tmp128 = -1 * tmp127;
    const auto tmp129 = tmp121 * tmp56;
    const auto tmp130 = tmp129 + tmp129;
    const auto tmp131 = tmp61 * tmp116;
    const auto tmp132 = tmp131 + tmp131;
    const auto tmp133 = tmp132 + tmp130;
    const auto tmp134 = tmp133 + tmp128;
    const auto tmp135 = tmp134 / tmp51;
    const auto tmp136 = tmp135 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp137 = tmp78 * tmp136;
    const auto tmp138 = tmp137 + tmp112;
    const auto tmp139 = 3 * tmp138;
    const auto tmp140 = tmp139 / 0.1;
    const auto tmp141 = tmp140 * tmp38;
    const auto tmp142 = tmp107 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp143 = tmp125 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp144 = tmp78 * tmp143;
    const auto tmp145 = tmp144 + tmp142;
    const auto tmp146 = 3 * tmp145;
    const auto tmp147 = tmp146 / 0.1;
    const auto tmp148 = tmp147 * tmp90;
    const auto tmp149 = 2.0 * tmp148;
    const auto tmp150 = 2.0 * tmp147;
    const auto tmp151 = tmp150 * tmp93;
    const auto tmp152 = tmp151 * tmp37;
    const auto tmp153 = -1 * tmp152;
    const auto tmp154 = tmp153 + tmp149;
    const auto tmp155 = tmp154 / tmp34;
    const auto tmp156 = 2 * tmp155;
    const auto tmp157 = tmp156 * tmp37;
    const auto tmp158 = tmp157 * tmp89;
    const auto tmp159 = tmp158 + tmp141;
    const auto tmp160 = -1 * tmp159;
    const auto tmp161 = 0.5 * tmp160;
    const auto tmp162 = tmp43 * tmp107;
    const auto tmp163 = -1 * tmp162;
    const auto tmp164 = tmp163 / tmp39;
    const auto tmp165 = tmp164 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp166 = tmp66 * tmp125;
    const auto tmp167 = -1 * tmp166;
    const auto tmp168 = tmp133 + tmp167;
    const auto tmp169 = tmp168 / tmp51;
    const auto tmp170 = tmp169 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp171 = tmp78 * tmp170;
    const auto tmp172 = tmp171 + tmp165;
    const auto tmp173 = 3 * tmp172;
    const auto tmp174 = tmp173 / 0.1;
    const auto tmp175 = tmp174 * tmp38;
    const auto tmp176 = tmp101 * tmp147;
    const auto tmp177 = tmp176 + tmp175;
    const auto tmp178 = -1 * tmp177;
    const auto tmp179 = 0.5 * tmp178;
    const auto tmp180 = tmp108 * tmp107;
    const auto tmp181 = -1 * tmp180;
    const auto tmp182 = 2 + tmp181;
    const auto tmp183 = tmp182 / tmp39;
    const auto tmp184 = tmp183 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp185 = tmp126 * tmp125;
    const auto tmp186 = -1 * tmp185;
    const auto tmp187 = tmp116 * tmp116;
    const auto tmp188 = tmp187 + tmp187;
    const auto tmp189 = tmp121 * tmp121;
    const auto tmp190 = tmp189 + tmp189;
    const auto tmp191 = tmp190 + tmp188;
    const auto tmp192 = tmp191 + tmp186;
    const auto tmp193 = tmp192 / tmp51;
    const auto tmp194 = tmp193 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp195 = tmp78 * tmp194;
    const auto tmp196 = tmp195 + tmp184;
    const auto tmp197 = 3 * tmp196;
    const auto tmp198 = tmp197 / 0.1;
    const auto tmp199 = tmp198 * tmp38;
    const auto tmp200 = tmp157 * tmp147;
    const auto tmp201 = tmp200 + tmp199;
    const auto tmp202 = -1 * tmp201;
    const auto tmp203 = 0.5 * tmp202;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp105;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp161;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp179;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp203;
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

} // namespace UFLLocalFunctions_1460b632dc5919e94a2147108f4f34f4

PYBIND11_MODULE( localfunction_1460b632dc5919e94a2147108f4f34f4_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_1460b632dc5919e94a2147108f4f34f4::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_1460b632dc5919e94a2147108f4f34f4::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_1460b632dc5919e94a2147108f4f34f4_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
