#ifndef GUARD_d40efa41ac661ff77278d2ae4812b06d
#define GUARD_d40efa41ac661ff77278d2ae4812b06d

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

namespace UFLLocalFunctions_d40efa41ac661ff77278d2ae4812b06d
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
    GlobalCoordinateType tmp1 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp2 = 0.8090169943749475 * tmp1[ 1 ];
    const auto tmp3 = -0.5877852522924731 * tmp1[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = -0.3 + tmp4;
    const auto tmp6 = std::abs( tmp5 );
    const auto tmp7 = -0.3 + tmp6;
    const auto tmp8 = 0.5877852522924731 * tmp1[ 1 ];
    const auto tmp9 = 0.8090169943749475 * tmp1[ 0 ];
    const auto tmp10 = tmp9 + tmp8;
    const auto tmp11 = -0.1 + tmp10;
    const auto tmp12 = std::abs( tmp11 );
    const auto tmp13 = -0.8 + tmp12;
    const auto tmp14 = std::max( tmp13, tmp7 );
    const auto tmp15 = std::max( tmp7, 0.0 );
    const auto tmp16 = tmp15 * tmp15;
    const auto tmp17 = std::max( tmp13, 0.0 );
    const auto tmp18 = tmp17 * tmp17;
    const auto tmp19 = tmp18 + tmp16;
    const auto tmp20 = 1e-10 + tmp19;
    const auto tmp21 = std::sqrt( tmp20 );
    const auto tmp22 = 3 * (tmp14 > 0.0 ? tmp21 : tmp14);
    const auto tmp23 = tmp22 / tmp0;
    const auto tmp24 = std::tanh( tmp23 );
    const auto tmp25 = -1 * tmp24;
    const auto tmp26 = 1 + tmp25;
    const auto tmp27 = 0.5 * tmp26;
    result[ 0 ] = tmp27;
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
    GlobalCoordinateType tmp1 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp2 = 0.8090169943749475 * tmp1[ 1 ];
    const auto tmp3 = -0.5877852522924731 * tmp1[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = -0.3 + tmp4;
    const auto tmp6 = std::abs( tmp5 );
    const auto tmp7 = -0.3 + tmp6;
    const auto tmp8 = 0.5877852522924731 * tmp1[ 1 ];
    const auto tmp9 = 0.8090169943749475 * tmp1[ 0 ];
    const auto tmp10 = tmp9 + tmp8;
    const auto tmp11 = -0.1 + tmp10;
    const auto tmp12 = std::abs( tmp11 );
    const auto tmp13 = -0.8 + tmp12;
    const auto tmp14 = std::max( tmp13, tmp7 );
    const auto tmp15 = std::max( tmp7, 0.0 );
    const auto tmp16 = tmp15 * tmp15;
    const auto tmp17 = std::max( tmp13, 0.0 );
    const auto tmp18 = tmp17 * tmp17;
    const auto tmp19 = tmp18 + tmp16;
    const auto tmp20 = 1e-10 + tmp19;
    const auto tmp21 = std::sqrt( tmp20 );
    const auto tmp22 = 3 * (tmp14 > 0.0 ? tmp21 : tmp14);
    const auto tmp23 = tmp22 / tmp0;
    const auto tmp24 = 2.0 * tmp23;
    const auto tmp25 = std::cosh( tmp24 );
    const auto tmp26 = 1.0 + tmp25;
    const auto tmp27 = std::cosh( tmp23 );
    const auto tmp28 = 2.0 * tmp27;
    const auto tmp29 = tmp28 / tmp26;
    const auto tmp30 = std::pow( tmp29, 2 );
    const auto tmp31 = 0.8090169943749475 * (tmp11 == 0.0 ? 0.0 : (tmp11 < 0.0 ? -1 : 1));
    const auto tmp32 = tmp31 * (tmp13 > tmp7 ? 1 : 0.0);
    const auto tmp33 = -0.5877852522924731 * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp34 = -1 * (tmp13 > tmp7 ? 1 : 0.0);
    const auto tmp35 = 1.0 + tmp34;
    const auto tmp36 = tmp35 * tmp33;
    const auto tmp37 = tmp36 + tmp32;
    const auto tmp38 = 2 * tmp21;
    const auto tmp39 = tmp33 * (tmp7 > 0.0 ? 1 : 0.0);
    const auto tmp40 = tmp39 * tmp15;
    const auto tmp41 = tmp40 + tmp40;
    const auto tmp42 = tmp31 * (tmp13 > 0.0 ? 1 : 0.0);
    const auto tmp43 = tmp42 * tmp17;
    const auto tmp44 = tmp43 + tmp43;
    const auto tmp45 = tmp44 + tmp41;
    const auto tmp46 = tmp45 / tmp38;
    const auto tmp47 = 3 * (tmp14 > 0.0 ? tmp46 : tmp37);
    const auto tmp48 = tmp47 / tmp0;
    const auto tmp49 = tmp48 * tmp30;
    const auto tmp50 = -1 * tmp49;
    const auto tmp51 = 0.5 * tmp50;
    const auto tmp52 = 0.5877852522924731 * (tmp11 == 0.0 ? 0.0 : (tmp11 < 0.0 ? -1 : 1));
    const auto tmp53 = tmp52 * (tmp13 > tmp7 ? 1 : 0.0);
    const auto tmp54 = 0.8090169943749475 * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp55 = tmp35 * tmp54;
    const auto tmp56 = tmp55 + tmp53;
    const auto tmp57 = tmp54 * (tmp7 > 0.0 ? 1 : 0.0);
    const auto tmp58 = tmp57 * tmp15;
    const auto tmp59 = tmp58 + tmp58;
    const auto tmp60 = tmp52 * (tmp13 > 0.0 ? 1 : 0.0);
    const auto tmp61 = tmp60 * tmp17;
    const auto tmp62 = tmp61 + tmp61;
    const auto tmp63 = tmp62 + tmp59;
    const auto tmp64 = tmp63 / tmp38;
    const auto tmp65 = 3 * (tmp14 > 0.0 ? tmp64 : tmp56);
    const auto tmp66 = tmp65 / tmp0;
    const auto tmp67 = tmp66 * tmp30;
    const auto tmp68 = -1 * tmp67;
    const auto tmp69 = 0.5 * tmp68;
    (result[ 0 ])[ 0 ] = tmp51;
    (result[ 0 ])[ 1 ] = tmp69;
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
    GlobalCoordinateType tmp1 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp2 = 0.8090169943749475 * tmp1[ 1 ];
    const auto tmp3 = -0.5877852522924731 * tmp1[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = -0.3 + tmp4;
    const auto tmp6 = std::abs( tmp5 );
    const auto tmp7 = -0.3 + tmp6;
    const auto tmp8 = 0.5877852522924731 * tmp1[ 1 ];
    const auto tmp9 = 0.8090169943749475 * tmp1[ 0 ];
    const auto tmp10 = tmp9 + tmp8;
    const auto tmp11 = -0.1 + tmp10;
    const auto tmp12 = std::abs( tmp11 );
    const auto tmp13 = -0.8 + tmp12;
    const auto tmp14 = std::max( tmp13, tmp7 );
    const auto tmp15 = std::max( tmp7, 0.0 );
    const auto tmp16 = tmp15 * tmp15;
    const auto tmp17 = std::max( tmp13, 0.0 );
    const auto tmp18 = tmp17 * tmp17;
    const auto tmp19 = tmp18 + tmp16;
    const auto tmp20 = 1e-10 + tmp19;
    const auto tmp21 = std::sqrt( tmp20 );
    const auto tmp22 = 3 * (tmp14 > 0.0 ? tmp21 : tmp14);
    const auto tmp23 = tmp22 / tmp0;
    const auto tmp24 = 2.0 * tmp23;
    const auto tmp25 = std::cosh( tmp24 );
    const auto tmp26 = 1.0 + tmp25;
    const auto tmp27 = std::cosh( tmp23 );
    const auto tmp28 = 2.0 * tmp27;
    const auto tmp29 = tmp28 / tmp26;
    const auto tmp30 = std::pow( tmp29, 2 );
    const auto tmp31 = 2 * tmp21;
    const auto tmp32 = -0.5877852522924731 * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp33 = tmp32 * (tmp7 > 0.0 ? 1 : 0.0);
    const auto tmp34 = tmp33 * tmp15;
    const auto tmp35 = tmp34 + tmp34;
    const auto tmp36 = 0.8090169943749475 * (tmp11 == 0.0 ? 0.0 : (tmp11 < 0.0 ? -1 : 1));
    const auto tmp37 = tmp36 * (tmp13 > 0.0 ? 1 : 0.0);
    const auto tmp38 = tmp37 * tmp17;
    const auto tmp39 = tmp38 + tmp38;
    const auto tmp40 = tmp39 + tmp35;
    const auto tmp41 = tmp40 / tmp31;
    const auto tmp42 = 2 * tmp41;
    const auto tmp43 = tmp42 * tmp41;
    const auto tmp44 = -1 * tmp43;
    const auto tmp45 = tmp33 * tmp33;
    const auto tmp46 = tmp45 + tmp45;
    const auto tmp47 = tmp37 * tmp37;
    const auto tmp48 = tmp47 + tmp47;
    const auto tmp49 = tmp48 + tmp46;
    const auto tmp50 = tmp49 + tmp44;
    const auto tmp51 = tmp50 / tmp31;
    const auto tmp52 = 3 * (tmp14 > 0.0 ? tmp51 : 0.0);
    const auto tmp53 = tmp52 / tmp0;
    const auto tmp54 = tmp53 * tmp30;
    const auto tmp55 = tmp36 * (tmp13 > tmp7 ? 1 : 0.0);
    const auto tmp56 = -1 * (tmp13 > tmp7 ? 1 : 0.0);
    const auto tmp57 = 1.0 + tmp56;
    const auto tmp58 = tmp57 * tmp32;
    const auto tmp59 = tmp58 + tmp55;
    const auto tmp60 = 3 * (tmp14 > 0.0 ? tmp41 : tmp59);
    const auto tmp61 = tmp60 / tmp0;
    const auto tmp62 = std::sinh( tmp23 );
    const auto tmp63 = tmp61 * tmp62;
    const auto tmp64 = 2.0 * tmp63;
    const auto tmp65 = std::sinh( tmp24 );
    const auto tmp66 = 2.0 * tmp61;
    const auto tmp67 = tmp66 * tmp65;
    const auto tmp68 = tmp67 * tmp29;
    const auto tmp69 = -1 * tmp68;
    const auto tmp70 = tmp69 + tmp64;
    const auto tmp71 = tmp70 / tmp26;
    const auto tmp72 = 2 * tmp71;
    const auto tmp73 = tmp72 * tmp29;
    const auto tmp74 = tmp73 * tmp61;
    const auto tmp75 = tmp74 + tmp54;
    const auto tmp76 = -1 * tmp75;
    const auto tmp77 = 0.5 * tmp76;
    const auto tmp78 = 0.8090169943749475 * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp79 = tmp78 * (tmp7 > 0.0 ? 1 : 0.0);
    const auto tmp80 = tmp79 * tmp15;
    const auto tmp81 = tmp80 + tmp80;
    const auto tmp82 = 0.5877852522924731 * (tmp11 == 0.0 ? 0.0 : (tmp11 < 0.0 ? -1 : 1));
    const auto tmp83 = tmp82 * (tmp13 > 0.0 ? 1 : 0.0);
    const auto tmp84 = tmp83 * tmp17;
    const auto tmp85 = tmp84 + tmp84;
    const auto tmp86 = tmp85 + tmp81;
    const auto tmp87 = tmp86 / tmp31;
    const auto tmp88 = 2 * tmp87;
    const auto tmp89 = tmp88 * tmp41;
    const auto tmp90 = -1 * tmp89;
    const auto tmp91 = tmp33 * tmp79;
    const auto tmp92 = tmp91 + tmp91;
    const auto tmp93 = tmp83 * tmp37;
    const auto tmp94 = tmp93 + tmp93;
    const auto tmp95 = tmp94 + tmp92;
    const auto tmp96 = tmp95 + tmp90;
    const auto tmp97 = tmp96 / tmp31;
    const auto tmp98 = 3 * (tmp14 > 0.0 ? tmp97 : 0.0);
    const auto tmp99 = tmp98 / tmp0;
    const auto tmp100 = tmp99 * tmp30;
    const auto tmp101 = tmp82 * (tmp13 > tmp7 ? 1 : 0.0);
    const auto tmp102 = tmp57 * tmp78;
    const auto tmp103 = tmp102 + tmp101;
    const auto tmp104 = 3 * (tmp14 > 0.0 ? tmp87 : tmp103);
    const auto tmp105 = tmp104 / tmp0;
    const auto tmp106 = tmp105 * tmp62;
    const auto tmp107 = 2.0 * tmp106;
    const auto tmp108 = 2.0 * tmp105;
    const auto tmp109 = tmp108 * tmp65;
    const auto tmp110 = tmp109 * tmp29;
    const auto tmp111 = -1 * tmp110;
    const auto tmp112 = tmp111 + tmp107;
    const auto tmp113 = tmp112 / tmp26;
    const auto tmp114 = 2 * tmp113;
    const auto tmp115 = tmp114 * tmp29;
    const auto tmp116 = tmp115 * tmp61;
    const auto tmp117 = tmp116 + tmp100;
    const auto tmp118 = -1 * tmp117;
    const auto tmp119 = 0.5 * tmp118;
    const auto tmp120 = tmp42 * tmp87;
    const auto tmp121 = -1 * tmp120;
    const auto tmp122 = tmp95 + tmp121;
    const auto tmp123 = tmp122 / tmp31;
    const auto tmp124 = 3 * (tmp14 > 0.0 ? tmp123 : 0.0);
    const auto tmp125 = tmp124 / tmp0;
    const auto tmp126 = tmp125 * tmp30;
    const auto tmp127 = tmp73 * tmp105;
    const auto tmp128 = tmp127 + tmp126;
    const auto tmp129 = -1 * tmp128;
    const auto tmp130 = 0.5 * tmp129;
    const auto tmp131 = tmp88 * tmp87;
    const auto tmp132 = -1 * tmp131;
    const auto tmp133 = tmp79 * tmp79;
    const auto tmp134 = tmp133 + tmp133;
    const auto tmp135 = tmp83 * tmp83;
    const auto tmp136 = tmp135 + tmp135;
    const auto tmp137 = tmp136 + tmp134;
    const auto tmp138 = tmp137 + tmp132;
    const auto tmp139 = tmp138 / tmp31;
    const auto tmp140 = 3 * (tmp14 > 0.0 ? tmp139 : 0.0);
    const auto tmp141 = tmp140 / tmp0;
    const auto tmp142 = tmp141 * tmp30;
    const auto tmp143 = tmp115 * tmp105;
    const auto tmp144 = tmp143 + tmp142;
    const auto tmp145 = -1 * tmp144;
    const auto tmp146 = 0.5 * tmp145;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp77;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp119;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp130;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp146;
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

} // namespace UFLLocalFunctions_d40efa41ac661ff77278d2ae4812b06d

PYBIND11_MODULE( localfunction_d40efa41ac661ff77278d2ae4812b06d_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_d40efa41ac661ff77278d2ae4812b06d::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_d40efa41ac661ff77278d2ae4812b06d::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_d40efa41ac661ff77278d2ae4812b06d_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
