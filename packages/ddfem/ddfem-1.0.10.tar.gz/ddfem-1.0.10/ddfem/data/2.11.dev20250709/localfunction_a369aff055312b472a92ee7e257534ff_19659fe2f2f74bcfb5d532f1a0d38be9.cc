#ifndef GUARD_a369aff055312b472a92ee7e257534ff
#define GUARD_a369aff055312b472a92ee7e257534ff

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

namespace UFLLocalFunctions_a369aff055312b472a92ee7e257534ff
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
    const auto tmp24 = 3 * tmp23;
    const auto tmp25 = tmp24 / tmp1;
    const auto tmp26 = std::tanh( tmp25 );
    const auto tmp27 = -1 * tmp26;
    const auto tmp28 = 1 + tmp27;
    const auto tmp29 = 0.5 * tmp28;
    result[ 0 ] = tmp29;
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
    const auto tmp24 = 3 * tmp23;
    const auto tmp25 = tmp24 / tmp1;
    const auto tmp26 = 2.0 * tmp25;
    const auto tmp27 = std::cosh( tmp26 );
    const auto tmp28 = 1.0 + tmp27;
    const auto tmp29 = std::cosh( tmp25 );
    const auto tmp30 = 2.0 * tmp29;
    const auto tmp31 = tmp30 / tmp28;
    const auto tmp32 = std::pow( tmp31, 2 );
    const auto tmp33 = (tmp14 > tmp12 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp34 = 2 * tmp22;
    const auto tmp35 = (tmp14 > 0.0 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp36 = tmp35 * tmp18;
    const auto tmp37 = tmp36 + tmp36;
    const auto tmp38 = tmp37 / tmp34;
    const auto tmp39 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp38 : tmp33);
    const auto tmp40 = 2 * tmp9;
    const auto tmp41 = tmp5 + tmp5;
    const auto tmp42 = tmp41 / tmp40;
    const auto tmp43 = -1 * ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0);
    const auto tmp44 = 1.0 + tmp43;
    const auto tmp45 = tmp44 * tmp42;
    const auto tmp46 = tmp45 + tmp39;
    const auto tmp47 = 3 * tmp46;
    const auto tmp48 = tmp47 / tmp1;
    const auto tmp49 = tmp48 * tmp32;
    const auto tmp50 = -1 * tmp49;
    const auto tmp51 = 0.5 * tmp50;
    const auto tmp52 = -1 * (tmp14 > tmp12 ? 1 : 0.0);
    const auto tmp53 = 1.0 + tmp52;
    const auto tmp54 = tmp53 * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp55 = (tmp12 > 0.0 ? 1 : 0.0) * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp56 = tmp55 * tmp16;
    const auto tmp57 = tmp56 + tmp56;
    const auto tmp58 = tmp57 / tmp34;
    const auto tmp59 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp58 : tmp54);
    const auto tmp60 = tmp3 + tmp3;
    const auto tmp61 = tmp60 / tmp40;
    const auto tmp62 = tmp44 * tmp61;
    const auto tmp63 = tmp62 + tmp59;
    const auto tmp64 = 3 * tmp63;
    const auto tmp65 = tmp64 / tmp1;
    const auto tmp66 = tmp65 * tmp32;
    const auto tmp67 = -1 * tmp66;
    const auto tmp68 = 0.5 * tmp67;
    (result[ 0 ])[ 0 ] = tmp51;
    (result[ 0 ])[ 1 ] = tmp68;
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
    const auto tmp24 = 3 * tmp23;
    const auto tmp25 = tmp24 / tmp1;
    const auto tmp26 = 2.0 * tmp25;
    const auto tmp27 = std::cosh( tmp26 );
    const auto tmp28 = 1.0 + tmp27;
    const auto tmp29 = std::cosh( tmp25 );
    const auto tmp30 = 2.0 * tmp29;
    const auto tmp31 = tmp30 / tmp28;
    const auto tmp32 = std::pow( tmp31, 2 );
    const auto tmp33 = 2 * tmp22;
    const auto tmp34 = (tmp14 > 0.0 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp35 = tmp34 * tmp18;
    const auto tmp36 = tmp35 + tmp35;
    const auto tmp37 = tmp36 / tmp33;
    const auto tmp38 = 2 * tmp37;
    const auto tmp39 = tmp38 * tmp37;
    const auto tmp40 = -1 * tmp39;
    const auto tmp41 = tmp34 * tmp34;
    const auto tmp42 = tmp41 + tmp41;
    const auto tmp43 = tmp42 + tmp40;
    const auto tmp44 = tmp43 / tmp33;
    const auto tmp45 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp44 : 0.0);
    const auto tmp46 = 2 * tmp9;
    const auto tmp47 = tmp5 + tmp5;
    const auto tmp48 = tmp47 / tmp46;
    const auto tmp49 = 2 * tmp48;
    const auto tmp50 = tmp49 * tmp48;
    const auto tmp51 = -1 * tmp50;
    const auto tmp52 = 2 + tmp51;
    const auto tmp53 = tmp52 / tmp46;
    const auto tmp54 = -1 * ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0);
    const auto tmp55 = 1.0 + tmp54;
    const auto tmp56 = tmp55 * tmp53;
    const auto tmp57 = tmp56 + tmp45;
    const auto tmp58 = 3 * tmp57;
    const auto tmp59 = tmp58 / tmp1;
    const auto tmp60 = tmp59 * tmp32;
    const auto tmp61 = (tmp14 > tmp12 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp62 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp37 : tmp61);
    const auto tmp63 = tmp55 * tmp48;
    const auto tmp64 = tmp63 + tmp62;
    const auto tmp65 = 3 * tmp64;
    const auto tmp66 = tmp65 / tmp1;
    const auto tmp67 = std::sinh( tmp25 );
    const auto tmp68 = tmp66 * tmp67;
    const auto tmp69 = 2.0 * tmp68;
    const auto tmp70 = std::sinh( tmp26 );
    const auto tmp71 = 2.0 * tmp66;
    const auto tmp72 = tmp71 * tmp70;
    const auto tmp73 = tmp72 * tmp31;
    const auto tmp74 = -1 * tmp73;
    const auto tmp75 = tmp74 + tmp69;
    const auto tmp76 = tmp75 / tmp28;
    const auto tmp77 = 2 * tmp76;
    const auto tmp78 = tmp77 * tmp31;
    const auto tmp79 = tmp78 * tmp66;
    const auto tmp80 = tmp79 + tmp60;
    const auto tmp81 = -1 * tmp80;
    const auto tmp82 = 0.5 * tmp81;
    const auto tmp83 = (tmp12 > 0.0 ? 1 : 0.0) * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp84 = tmp83 * tmp16;
    const auto tmp85 = tmp84 + tmp84;
    const auto tmp86 = tmp85 / tmp33;
    const auto tmp87 = 2 * tmp86;
    const auto tmp88 = tmp87 * tmp37;
    const auto tmp89 = -1 * tmp88;
    const auto tmp90 = tmp89 / tmp33;
    const auto tmp91 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp90 : 0.0);
    const auto tmp92 = tmp3 + tmp3;
    const auto tmp93 = tmp92 / tmp46;
    const auto tmp94 = 2 * tmp93;
    const auto tmp95 = tmp94 * tmp48;
    const auto tmp96 = -1 * tmp95;
    const auto tmp97 = tmp96 / tmp46;
    const auto tmp98 = tmp55 * tmp97;
    const auto tmp99 = tmp98 + tmp91;
    const auto tmp100 = 3 * tmp99;
    const auto tmp101 = tmp100 / tmp1;
    const auto tmp102 = tmp101 * tmp32;
    const auto tmp103 = -1 * (tmp14 > tmp12 ? 1 : 0.0);
    const auto tmp104 = 1.0 + tmp103;
    const auto tmp105 = tmp104 * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp106 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp86 : tmp105);
    const auto tmp107 = tmp55 * tmp93;
    const auto tmp108 = tmp107 + tmp106;
    const auto tmp109 = 3 * tmp108;
    const auto tmp110 = tmp109 / tmp1;
    const auto tmp111 = tmp110 * tmp67;
    const auto tmp112 = 2.0 * tmp111;
    const auto tmp113 = 2.0 * tmp110;
    const auto tmp114 = tmp113 * tmp70;
    const auto tmp115 = tmp114 * tmp31;
    const auto tmp116 = -1 * tmp115;
    const auto tmp117 = tmp116 + tmp112;
    const auto tmp118 = tmp117 / tmp28;
    const auto tmp119 = 2 * tmp118;
    const auto tmp120 = tmp119 * tmp31;
    const auto tmp121 = tmp120 * tmp66;
    const auto tmp122 = tmp121 + tmp102;
    const auto tmp123 = -1 * tmp122;
    const auto tmp124 = 0.5 * tmp123;
    const auto tmp125 = tmp38 * tmp86;
    const auto tmp126 = -1 * tmp125;
    const auto tmp127 = tmp126 / tmp33;
    const auto tmp128 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp127 : 0.0);
    const auto tmp129 = tmp49 * tmp93;
    const auto tmp130 = -1 * tmp129;
    const auto tmp131 = tmp130 / tmp46;
    const auto tmp132 = tmp55 * tmp131;
    const auto tmp133 = tmp132 + tmp128;
    const auto tmp134 = 3 * tmp133;
    const auto tmp135 = tmp134 / tmp1;
    const auto tmp136 = tmp135 * tmp32;
    const auto tmp137 = tmp78 * tmp110;
    const auto tmp138 = tmp137 + tmp136;
    const auto tmp139 = -1 * tmp138;
    const auto tmp140 = 0.5 * tmp139;
    const auto tmp141 = tmp87 * tmp86;
    const auto tmp142 = -1 * tmp141;
    const auto tmp143 = tmp83 * tmp83;
    const auto tmp144 = tmp143 + tmp143;
    const auto tmp145 = tmp144 + tmp142;
    const auto tmp146 = tmp145 / tmp33;
    const auto tmp147 = ((tmp15 > 0.0 ? tmp22 : tmp15) > tmp10 ? 1 : 0.0) * (tmp15 > 0.0 ? tmp146 : 0.0);
    const auto tmp148 = tmp94 * tmp93;
    const auto tmp149 = -1 * tmp148;
    const auto tmp150 = 2 + tmp149;
    const auto tmp151 = tmp150 / tmp46;
    const auto tmp152 = tmp55 * tmp151;
    const auto tmp153 = tmp152 + tmp147;
    const auto tmp154 = 3 * tmp153;
    const auto tmp155 = tmp154 / tmp1;
    const auto tmp156 = tmp155 * tmp32;
    const auto tmp157 = tmp120 * tmp110;
    const auto tmp158 = tmp157 + tmp156;
    const auto tmp159 = -1 * tmp158;
    const auto tmp160 = 0.5 * tmp159;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp82;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp124;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp140;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp160;
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

} // namespace UFLLocalFunctions_a369aff055312b472a92ee7e257534ff

PYBIND11_MODULE( localfunction_a369aff055312b472a92ee7e257534ff_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_a369aff055312b472a92ee7e257534ff::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_a369aff055312b472a92ee7e257534ff::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_a369aff055312b472a92ee7e257534ff_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
