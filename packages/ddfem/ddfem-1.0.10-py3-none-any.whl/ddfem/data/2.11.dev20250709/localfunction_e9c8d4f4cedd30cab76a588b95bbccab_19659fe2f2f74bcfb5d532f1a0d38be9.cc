#ifndef GUARD_e9c8d4f4cedd30cab76a588b95bbccab
#define GUARD_e9c8d4f4cedd30cab76a588b95bbccab

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

namespace UFLLocalFunctions_e9c8d4f4cedd30cab76a588b95bbccab
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
    const auto tmp2 = -0.3 + tmp1[ 1 ];
    const auto tmp3 = std::abs( tmp2 );
    const auto tmp4 = -0.3 + tmp3;
    const auto tmp5 = -0.1 + tmp1[ 0 ];
    const auto tmp6 = std::abs( tmp5 );
    const auto tmp7 = -0.8 + tmp6;
    const auto tmp8 = std::max( tmp7, tmp4 );
    const auto tmp9 = std::max( tmp4, 0.0 );
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = std::max( tmp7, 0.0 );
    const auto tmp12 = tmp11 * tmp11;
    const auto tmp13 = tmp12 + tmp10;
    const auto tmp14 = 1e-10 + tmp13;
    const auto tmp15 = std::sqrt( tmp14 );
    const auto tmp16 = -1 * (tmp8 > 0.0 ? tmp15 : tmp8);
    const auto tmp17 = 3 * tmp16;
    const auto tmp18 = tmp17 / tmp0;
    const auto tmp19 = std::tanh( tmp18 );
    const auto tmp20 = -1 * tmp19;
    const auto tmp21 = 1 + tmp20;
    const auto tmp22 = 0.5 * tmp21;
    result[ 0 ] = tmp22;
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
    const auto tmp2 = -0.3 + tmp1[ 1 ];
    const auto tmp3 = std::abs( tmp2 );
    const auto tmp4 = -0.3 + tmp3;
    const auto tmp5 = -0.1 + tmp1[ 0 ];
    const auto tmp6 = std::abs( tmp5 );
    const auto tmp7 = -0.8 + tmp6;
    const auto tmp8 = std::max( tmp7, tmp4 );
    const auto tmp9 = std::max( tmp4, 0.0 );
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = std::max( tmp7, 0.0 );
    const auto tmp12 = tmp11 * tmp11;
    const auto tmp13 = tmp12 + tmp10;
    const auto tmp14 = 1e-10 + tmp13;
    const auto tmp15 = std::sqrt( tmp14 );
    const auto tmp16 = -1 * (tmp8 > 0.0 ? tmp15 : tmp8);
    const auto tmp17 = 3 * tmp16;
    const auto tmp18 = tmp17 / tmp0;
    const auto tmp19 = 2.0 * tmp18;
    const auto tmp20 = std::cosh( tmp19 );
    const auto tmp21 = 1.0 + tmp20;
    const auto tmp22 = std::cosh( tmp18 );
    const auto tmp23 = 2.0 * tmp22;
    const auto tmp24 = tmp23 / tmp21;
    const auto tmp25 = std::pow( tmp24, 2 );
    const auto tmp26 = (tmp7 > tmp4 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp27 = 2 * tmp15;
    const auto tmp28 = (tmp7 > 0.0 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp29 = tmp28 * tmp11;
    const auto tmp30 = tmp29 + tmp29;
    const auto tmp31 = tmp30 / tmp27;
    const auto tmp32 = -1 * (tmp8 > 0.0 ? tmp31 : tmp26);
    const auto tmp33 = 3 * tmp32;
    const auto tmp34 = tmp33 / tmp0;
    const auto tmp35 = tmp34 * tmp25;
    const auto tmp36 = -1 * tmp35;
    const auto tmp37 = 0.5 * tmp36;
    const auto tmp38 = -1 * (tmp7 > tmp4 ? 1 : 0.0);
    const auto tmp39 = 1.0 + tmp38;
    const auto tmp40 = tmp39 * (tmp2 == 0.0 ? 0.0 : (tmp2 < 0.0 ? -1 : 1));
    const auto tmp41 = (tmp4 > 0.0 ? 1 : 0.0) * (tmp2 == 0.0 ? 0.0 : (tmp2 < 0.0 ? -1 : 1));
    const auto tmp42 = tmp41 * tmp9;
    const auto tmp43 = tmp42 + tmp42;
    const auto tmp44 = tmp43 / tmp27;
    const auto tmp45 = -1 * (tmp8 > 0.0 ? tmp44 : tmp40);
    const auto tmp46 = 3 * tmp45;
    const auto tmp47 = tmp46 / tmp0;
    const auto tmp48 = tmp47 * tmp25;
    const auto tmp49 = -1 * tmp48;
    const auto tmp50 = 0.5 * tmp49;
    (result[ 0 ])[ 0 ] = tmp37;
    (result[ 0 ])[ 1 ] = tmp50;
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
    const auto tmp2 = -0.3 + tmp1[ 1 ];
    const auto tmp3 = std::abs( tmp2 );
    const auto tmp4 = -0.3 + tmp3;
    const auto tmp5 = -0.1 + tmp1[ 0 ];
    const auto tmp6 = std::abs( tmp5 );
    const auto tmp7 = -0.8 + tmp6;
    const auto tmp8 = std::max( tmp7, tmp4 );
    const auto tmp9 = std::max( tmp4, 0.0 );
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = std::max( tmp7, 0.0 );
    const auto tmp12 = tmp11 * tmp11;
    const auto tmp13 = tmp12 + tmp10;
    const auto tmp14 = 1e-10 + tmp13;
    const auto tmp15 = std::sqrt( tmp14 );
    const auto tmp16 = -1 * (tmp8 > 0.0 ? tmp15 : tmp8);
    const auto tmp17 = 3 * tmp16;
    const auto tmp18 = tmp17 / tmp0;
    const auto tmp19 = 2.0 * tmp18;
    const auto tmp20 = std::cosh( tmp19 );
    const auto tmp21 = 1.0 + tmp20;
    const auto tmp22 = std::cosh( tmp18 );
    const auto tmp23 = 2.0 * tmp22;
    const auto tmp24 = tmp23 / tmp21;
    const auto tmp25 = std::pow( tmp24, 2 );
    const auto tmp26 = 2 * tmp15;
    const auto tmp27 = (tmp7 > 0.0 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp28 = tmp27 * tmp11;
    const auto tmp29 = tmp28 + tmp28;
    const auto tmp30 = tmp29 / tmp26;
    const auto tmp31 = 2 * tmp30;
    const auto tmp32 = tmp31 * tmp30;
    const auto tmp33 = -1 * tmp32;
    const auto tmp34 = tmp27 * tmp27;
    const auto tmp35 = tmp34 + tmp34;
    const auto tmp36 = tmp35 + tmp33;
    const auto tmp37 = tmp36 / tmp26;
    const auto tmp38 = -1 * (tmp8 > 0.0 ? tmp37 : 0.0);
    const auto tmp39 = 3 * tmp38;
    const auto tmp40 = tmp39 / tmp0;
    const auto tmp41 = tmp40 * tmp25;
    const auto tmp42 = (tmp7 > tmp4 ? 1 : 0.0) * (tmp5 == 0.0 ? 0.0 : (tmp5 < 0.0 ? -1 : 1));
    const auto tmp43 = -1 * (tmp8 > 0.0 ? tmp30 : tmp42);
    const auto tmp44 = 3 * tmp43;
    const auto tmp45 = tmp44 / tmp0;
    const auto tmp46 = std::sinh( tmp18 );
    const auto tmp47 = tmp45 * tmp46;
    const auto tmp48 = 2.0 * tmp47;
    const auto tmp49 = std::sinh( tmp19 );
    const auto tmp50 = 2.0 * tmp45;
    const auto tmp51 = tmp50 * tmp49;
    const auto tmp52 = tmp51 * tmp24;
    const auto tmp53 = -1 * tmp52;
    const auto tmp54 = tmp53 + tmp48;
    const auto tmp55 = tmp54 / tmp21;
    const auto tmp56 = 2 * tmp55;
    const auto tmp57 = tmp56 * tmp24;
    const auto tmp58 = tmp57 * tmp45;
    const auto tmp59 = tmp58 + tmp41;
    const auto tmp60 = -1 * tmp59;
    const auto tmp61 = 0.5 * tmp60;
    const auto tmp62 = (tmp4 > 0.0 ? 1 : 0.0) * (tmp2 == 0.0 ? 0.0 : (tmp2 < 0.0 ? -1 : 1));
    const auto tmp63 = tmp62 * tmp9;
    const auto tmp64 = tmp63 + tmp63;
    const auto tmp65 = tmp64 / tmp26;
    const auto tmp66 = 2 * tmp65;
    const auto tmp67 = tmp66 * tmp30;
    const auto tmp68 = -1 * tmp67;
    const auto tmp69 = tmp68 / tmp26;
    const auto tmp70 = -1 * (tmp8 > 0.0 ? tmp69 : 0.0);
    const auto tmp71 = 3 * tmp70;
    const auto tmp72 = tmp71 / tmp0;
    const auto tmp73 = tmp72 * tmp25;
    const auto tmp74 = -1 * (tmp7 > tmp4 ? 1 : 0.0);
    const auto tmp75 = 1.0 + tmp74;
    const auto tmp76 = tmp75 * (tmp2 == 0.0 ? 0.0 : (tmp2 < 0.0 ? -1 : 1));
    const auto tmp77 = -1 * (tmp8 > 0.0 ? tmp65 : tmp76);
    const auto tmp78 = 3 * tmp77;
    const auto tmp79 = tmp78 / tmp0;
    const auto tmp80 = tmp79 * tmp46;
    const auto tmp81 = 2.0 * tmp80;
    const auto tmp82 = 2.0 * tmp79;
    const auto tmp83 = tmp82 * tmp49;
    const auto tmp84 = tmp83 * tmp24;
    const auto tmp85 = -1 * tmp84;
    const auto tmp86 = tmp85 + tmp81;
    const auto tmp87 = tmp86 / tmp21;
    const auto tmp88 = 2 * tmp87;
    const auto tmp89 = tmp88 * tmp24;
    const auto tmp90 = tmp89 * tmp45;
    const auto tmp91 = tmp90 + tmp73;
    const auto tmp92 = -1 * tmp91;
    const auto tmp93 = 0.5 * tmp92;
    const auto tmp94 = tmp31 * tmp65;
    const auto tmp95 = -1 * tmp94;
    const auto tmp96 = tmp95 / tmp26;
    const auto tmp97 = -1 * (tmp8 > 0.0 ? tmp96 : 0.0);
    const auto tmp98 = 3 * tmp97;
    const auto tmp99 = tmp98 / tmp0;
    const auto tmp100 = tmp99 * tmp25;
    const auto tmp101 = tmp57 * tmp79;
    const auto tmp102 = tmp101 + tmp100;
    const auto tmp103 = -1 * tmp102;
    const auto tmp104 = 0.5 * tmp103;
    const auto tmp105 = tmp66 * tmp65;
    const auto tmp106 = -1 * tmp105;
    const auto tmp107 = tmp62 * tmp62;
    const auto tmp108 = tmp107 + tmp107;
    const auto tmp109 = tmp108 + tmp106;
    const auto tmp110 = tmp109 / tmp26;
    const auto tmp111 = -1 * (tmp8 > 0.0 ? tmp110 : 0.0);
    const auto tmp112 = 3 * tmp111;
    const auto tmp113 = tmp112 / tmp0;
    const auto tmp114 = tmp113 * tmp25;
    const auto tmp115 = tmp89 * tmp79;
    const auto tmp116 = tmp115 + tmp114;
    const auto tmp117 = -1 * tmp116;
    const auto tmp118 = 0.5 * tmp117;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp61;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp93;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp104;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp118;
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

} // namespace UFLLocalFunctions_e9c8d4f4cedd30cab76a588b95bbccab

PYBIND11_MODULE( localfunction_e9c8d4f4cedd30cab76a588b95bbccab_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_e9c8d4f4cedd30cab76a588b95bbccab::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_e9c8d4f4cedd30cab76a588b95bbccab::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_e9c8d4f4cedd30cab76a588b95bbccab_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
