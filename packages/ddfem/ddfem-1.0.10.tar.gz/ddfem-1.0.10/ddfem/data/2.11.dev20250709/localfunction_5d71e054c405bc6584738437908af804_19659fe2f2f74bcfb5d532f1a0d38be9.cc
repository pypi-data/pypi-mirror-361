#ifndef GUARD_5d71e054c405bc6584738437908af804
#define GUARD_5d71e054c405bc6584738437908af804

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

namespace UFLLocalFunctions_5d71e054c405bc6584738437908af804
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
    result[ 0 ] = tmp29;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::max;
    using std::min;
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
    const auto tmp29 = 2 * tmp27;
    const auto tmp30 = tmp1 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp31 = tmp30 + tmp30;
    const auto tmp32 = tmp31 / tmp29;
    const auto tmp33 = tmp32 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp34 = 2 * tmp17;
    const auto tmp35 = 0.5877852522924731 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp36 = tmp35 * (tmp4 > 0.0 ? 1 : 0.0);
    const auto tmp37 = tmp36 * (tmp5 < 0.5 ? 1 : 0.0);
    const auto tmp38 = 0.8090169943749475 * tmp37;
    const auto tmp39 = -1 * tmp38;
    const auto tmp40 = tmp13 * tmp39;
    const auto tmp41 = tmp40 + tmp40;
    const auto tmp42 = 0.5877852522924731 * tmp37;
    const auto tmp43 = -1 * tmp42;
    const auto tmp44 = tmp43 + (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp45 = tmp9 * tmp44;
    const auto tmp46 = tmp45 + tmp45;
    const auto tmp47 = tmp46 + tmp41;
    const auto tmp48 = tmp47 / tmp34;
    const auto tmp49 = tmp48 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp50 = -1 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp51 = 1.0 + tmp50;
    const auto tmp52 = tmp51 * tmp49;
    const auto tmp53 = tmp52 + tmp33;
    const auto tmp54 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp55 = tmp54 / tmp29;
    const auto tmp56 = tmp55 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp57 = 0.8090169943749475 * (tmp4 > 0.0 ? 1 : 0.0);
    const auto tmp58 = tmp57 * (tmp5 < 0.5 ? 1 : 0.0);
    const auto tmp59 = 0.5877852522924731 * tmp58;
    const auto tmp60 = -1 * tmp59;
    const auto tmp61 = tmp9 * tmp60;
    const auto tmp62 = tmp61 + tmp61;
    const auto tmp63 = 0.8090169943749475 * tmp58;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = 1 + tmp64;
    const auto tmp66 = tmp65 * tmp13;
    const auto tmp67 = tmp66 + tmp66;
    const auto tmp68 = tmp67 + tmp62;
    const auto tmp69 = tmp68 / tmp34;
    const auto tmp70 = tmp69 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp71 = tmp51 * tmp70;
    const auto tmp72 = tmp71 + tmp56;
    (result[ 0 ])[ 0 ] = tmp53;
    (result[ 0 ])[ 1 ] = tmp72;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::abs;
    using std::max;
    using std::min;
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
    const auto tmp29 = 2 * tmp27;
    const auto tmp30 = tmp1 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp31 = tmp30 + tmp30;
    const auto tmp32 = tmp31 / tmp29;
    const auto tmp33 = 2 * tmp32;
    const auto tmp34 = tmp33 * tmp32;
    const auto tmp35 = -1 * tmp34;
    const auto tmp36 = (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1)) * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp37 = tmp36 + tmp36;
    const auto tmp38 = tmp37 + tmp35;
    const auto tmp39 = tmp38 / tmp29;
    const auto tmp40 = tmp39 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp41 = 2 * tmp17;
    const auto tmp42 = 0.5877852522924731 * (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp43 = tmp42 * (tmp4 > 0.0 ? 1 : 0.0);
    const auto tmp44 = tmp43 * (tmp5 < 0.5 ? 1 : 0.0);
    const auto tmp45 = 0.8090169943749475 * tmp44;
    const auto tmp46 = -1 * tmp45;
    const auto tmp47 = tmp13 * tmp46;
    const auto tmp48 = tmp47 + tmp47;
    const auto tmp49 = 0.5877852522924731 * tmp44;
    const auto tmp50 = -1 * tmp49;
    const auto tmp51 = tmp50 + (tmp0[ 0 ] == 0.0 ? 0.0 : (tmp0[ 0 ] < 0.0 ? -1 : 1));
    const auto tmp52 = tmp9 * tmp51;
    const auto tmp53 = tmp52 + tmp52;
    const auto tmp54 = tmp53 + tmp48;
    const auto tmp55 = tmp54 / tmp41;
    const auto tmp56 = 2 * tmp55;
    const auto tmp57 = tmp56 * tmp55;
    const auto tmp58 = -1 * tmp57;
    const auto tmp59 = tmp46 * tmp46;
    const auto tmp60 = tmp59 + tmp59;
    const auto tmp61 = tmp51 * tmp51;
    const auto tmp62 = tmp61 + tmp61;
    const auto tmp63 = tmp62 + tmp60;
    const auto tmp64 = tmp63 + tmp58;
    const auto tmp65 = tmp64 / tmp41;
    const auto tmp66 = tmp65 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp67 = -1 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp68 = 1.0 + tmp67;
    const auto tmp69 = tmp68 * tmp66;
    const auto tmp70 = tmp69 + tmp40;
    const auto tmp71 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp72 = tmp71 / tmp29;
    const auto tmp73 = 2 * tmp72;
    const auto tmp74 = tmp73 * tmp32;
    const auto tmp75 = -1 * tmp74;
    const auto tmp76 = tmp75 / tmp29;
    const auto tmp77 = tmp76 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp78 = 0.8090169943749475 * (tmp4 > 0.0 ? 1 : 0.0);
    const auto tmp79 = tmp78 * (tmp5 < 0.5 ? 1 : 0.0);
    const auto tmp80 = 0.5877852522924731 * tmp79;
    const auto tmp81 = -1 * tmp80;
    const auto tmp82 = tmp9 * tmp81;
    const auto tmp83 = tmp82 + tmp82;
    const auto tmp84 = 0.8090169943749475 * tmp79;
    const auto tmp85 = -1 * tmp84;
    const auto tmp86 = 1 + tmp85;
    const auto tmp87 = tmp86 * tmp13;
    const auto tmp88 = tmp87 + tmp87;
    const auto tmp89 = tmp88 + tmp83;
    const auto tmp90 = tmp89 / tmp41;
    const auto tmp91 = 2 * tmp90;
    const auto tmp92 = tmp91 * tmp55;
    const auto tmp93 = -1 * tmp92;
    const auto tmp94 = tmp86 * tmp46;
    const auto tmp95 = tmp94 + tmp94;
    const auto tmp96 = tmp51 * tmp81;
    const auto tmp97 = tmp96 + tmp96;
    const auto tmp98 = tmp97 + tmp95;
    const auto tmp99 = tmp98 + tmp93;
    const auto tmp100 = tmp99 / tmp41;
    const auto tmp101 = tmp100 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp102 = tmp68 * tmp101;
    const auto tmp103 = tmp102 + tmp77;
    const auto tmp104 = tmp33 * tmp72;
    const auto tmp105 = -1 * tmp104;
    const auto tmp106 = tmp105 / tmp29;
    const auto tmp107 = tmp106 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp108 = tmp56 * tmp90;
    const auto tmp109 = -1 * tmp108;
    const auto tmp110 = tmp98 + tmp109;
    const auto tmp111 = tmp110 / tmp41;
    const auto tmp112 = tmp111 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp113 = tmp68 * tmp112;
    const auto tmp114 = tmp113 + tmp107;
    const auto tmp115 = tmp73 * tmp72;
    const auto tmp116 = -1 * tmp115;
    const auto tmp117 = 2 + tmp116;
    const auto tmp118 = tmp117 / tmp29;
    const auto tmp119 = tmp118 * (tmp28 > tmp22 ? 1 : 0.0);
    const auto tmp120 = tmp91 * tmp90;
    const auto tmp121 = -1 * tmp120;
    const auto tmp122 = tmp81 * tmp81;
    const auto tmp123 = tmp122 + tmp122;
    const auto tmp124 = tmp86 * tmp86;
    const auto tmp125 = tmp124 + tmp124;
    const auto tmp126 = tmp125 + tmp123;
    const auto tmp127 = tmp126 + tmp121;
    const auto tmp128 = tmp127 / tmp41;
    const auto tmp129 = tmp128 * (tmp21 > 0.0 ? 1 : -1);
    const auto tmp130 = tmp68 * tmp129;
    const auto tmp131 = tmp130 + tmp119;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp70;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp103;
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

} // namespace UFLLocalFunctions_5d71e054c405bc6584738437908af804

PYBIND11_MODULE( localfunction_5d71e054c405bc6584738437908af804_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_5d71e054c405bc6584738437908af804::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_5d71e054c405bc6584738437908af804::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_5d71e054c405bc6584738437908af804_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
