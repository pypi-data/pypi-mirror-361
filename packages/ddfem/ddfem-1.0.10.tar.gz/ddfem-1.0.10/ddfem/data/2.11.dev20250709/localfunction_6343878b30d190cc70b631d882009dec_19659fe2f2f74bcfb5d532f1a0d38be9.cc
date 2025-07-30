#ifndef GUARD_6343878b30d190cc70b631d882009dec
#define GUARD_6343878b30d190cc70b631d882009dec

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

namespace UFLLocalFunctions_6343878b30d190cc70b631d882009dec
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
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = -0.1 + tmp0[ 0 ];
    const auto tmp4 = tmp3 * tmp3;
    const auto tmp5 = tmp4 + tmp2;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -0.5 + tmp7;
    const auto tmp9 = std::abs( tmp1 );
    const auto tmp10 = -0.3 + tmp9;
    const auto tmp11 = std::abs( tmp3 );
    const auto tmp12 = -0.8 + tmp11;
    const auto tmp13 = std::max( tmp12, tmp10 );
    const auto tmp14 = std::max( tmp10, 0.0 );
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = std::max( tmp12, 0.0 );
    const auto tmp17 = tmp16 * tmp16;
    const auto tmp18 = tmp17 + tmp15;
    const auto tmp19 = 1e-10 + tmp18;
    const auto tmp20 = std::sqrt( tmp19 );
    const auto tmp21 = std::max( tmp13 > 0.0 ? tmp20 : tmp13, tmp8 );
    const auto tmp22 = -1 * tmp21;
    const auto tmp23 = std::min( tmp13 > 0.0 ? tmp20 : tmp13, tmp8 );
    const auto tmp24 = std::max( tmp23, tmp22 );
    result[ 0 ] = tmp24;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::max;
    using std::min;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = -0.1 + tmp0[ 0 ];
    const auto tmp4 = tmp3 * tmp3;
    const auto tmp5 = tmp4 + tmp2;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -0.5 + tmp7;
    const auto tmp9 = std::abs( tmp1 );
    const auto tmp10 = -0.3 + tmp9;
    const auto tmp11 = std::abs( tmp3 );
    const auto tmp12 = -0.8 + tmp11;
    const auto tmp13 = std::max( tmp12, tmp10 );
    const auto tmp14 = std::max( tmp10, 0.0 );
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = std::max( tmp12, 0.0 );
    const auto tmp17 = tmp16 * tmp16;
    const auto tmp18 = tmp17 + tmp15;
    const auto tmp19 = 1e-10 + tmp18;
    const auto tmp20 = std::sqrt( tmp19 );
    const auto tmp21 = std::max( tmp13 > 0.0 ? tmp20 : tmp13, tmp8 );
    const auto tmp22 = -1 * tmp21;
    const auto tmp23 = std::min( tmp13 > 0.0 ? tmp20 : tmp13, tmp8 );
    const auto tmp24 = (tmp12 > tmp10 ? 1 : 0.0) * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp25 = 2 * tmp20;
    const auto tmp26 = (tmp12 > 0.0 ? 1 : 0.0) * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp27 = tmp26 * tmp16;
    const auto tmp28 = tmp27 + tmp27;
    const auto tmp29 = tmp28 / tmp25;
    const auto tmp30 = ((tmp13 > 0.0 ? tmp20 : tmp13) < tmp8 ? 1 : 0.0) * (tmp13 > 0.0 ? tmp29 : tmp24);
    const auto tmp31 = 2 * tmp7;
    const auto tmp32 = tmp3 + tmp3;
    const auto tmp33 = tmp32 / tmp31;
    const auto tmp34 = -1 * ((tmp13 > 0.0 ? tmp20 : tmp13) < tmp8 ? 1 : 0.0);
    const auto tmp35 = 1.0 + tmp34;
    const auto tmp36 = tmp35 * tmp33;
    const auto tmp37 = tmp36 + tmp30;
    const auto tmp38 = tmp37 * (tmp23 > tmp22 ? 1 : 0.0);
    const auto tmp39 = ((tmp13 > 0.0 ? tmp20 : tmp13) > tmp8 ? 1 : 0.0) * (tmp13 > 0.0 ? tmp29 : tmp24);
    const auto tmp40 = -1 * ((tmp13 > 0.0 ? tmp20 : tmp13) > tmp8 ? 1 : 0.0);
    const auto tmp41 = 1.0 + tmp40;
    const auto tmp42 = tmp41 * tmp33;
    const auto tmp43 = tmp42 + tmp39;
    const auto tmp44 = -1 * tmp43;
    const auto tmp45 = -1 * (tmp23 > tmp22 ? 1 : 0.0);
    const auto tmp46 = 1.0 + tmp45;
    const auto tmp47 = tmp46 * tmp44;
    const auto tmp48 = tmp47 + tmp38;
    const auto tmp49 = -1 * (tmp12 > tmp10 ? 1 : 0.0);
    const auto tmp50 = 1.0 + tmp49;
    const auto tmp51 = tmp50 * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp52 = (tmp10 > 0.0 ? 1 : 0.0) * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp53 = tmp52 * tmp14;
    const auto tmp54 = tmp53 + tmp53;
    const auto tmp55 = tmp54 / tmp25;
    const auto tmp56 = ((tmp13 > 0.0 ? tmp20 : tmp13) < tmp8 ? 1 : 0.0) * (tmp13 > 0.0 ? tmp55 : tmp51);
    const auto tmp57 = tmp1 + tmp1;
    const auto tmp58 = tmp57 / tmp31;
    const auto tmp59 = tmp35 * tmp58;
    const auto tmp60 = tmp59 + tmp56;
    const auto tmp61 = tmp60 * (tmp23 > tmp22 ? 1 : 0.0);
    const auto tmp62 = ((tmp13 > 0.0 ? tmp20 : tmp13) > tmp8 ? 1 : 0.0) * (tmp13 > 0.0 ? tmp55 : tmp51);
    const auto tmp63 = tmp41 * tmp58;
    const auto tmp64 = tmp63 + tmp62;
    const auto tmp65 = -1 * tmp64;
    const auto tmp66 = tmp46 * tmp65;
    const auto tmp67 = tmp66 + tmp61;
    (result[ 0 ])[ 0 ] = tmp48;
    (result[ 0 ])[ 1 ] = tmp67;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::abs;
    using std::max;
    using std::min;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = -0.1 + tmp0[ 0 ];
    const auto tmp4 = tmp3 * tmp3;
    const auto tmp5 = tmp4 + tmp2;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -0.5 + tmp7;
    const auto tmp9 = std::abs( tmp1 );
    const auto tmp10 = -0.3 + tmp9;
    const auto tmp11 = std::abs( tmp3 );
    const auto tmp12 = -0.8 + tmp11;
    const auto tmp13 = std::max( tmp12, tmp10 );
    const auto tmp14 = std::max( tmp10, 0.0 );
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = std::max( tmp12, 0.0 );
    const auto tmp17 = tmp16 * tmp16;
    const auto tmp18 = tmp17 + tmp15;
    const auto tmp19 = 1e-10 + tmp18;
    const auto tmp20 = std::sqrt( tmp19 );
    const auto tmp21 = std::max( tmp13 > 0.0 ? tmp20 : tmp13, tmp8 );
    const auto tmp22 = -1 * tmp21;
    const auto tmp23 = std::min( tmp13 > 0.0 ? tmp20 : tmp13, tmp8 );
    const auto tmp24 = 2 * tmp20;
    const auto tmp25 = (tmp12 > 0.0 ? 1 : 0.0) * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp26 = tmp25 * tmp16;
    const auto tmp27 = tmp26 + tmp26;
    const auto tmp28 = tmp27 / tmp24;
    const auto tmp29 = 2 * tmp28;
    const auto tmp30 = tmp29 * tmp28;
    const auto tmp31 = -1 * tmp30;
    const auto tmp32 = tmp25 * tmp25;
    const auto tmp33 = tmp32 + tmp32;
    const auto tmp34 = tmp33 + tmp31;
    const auto tmp35 = tmp34 / tmp24;
    const auto tmp36 = ((tmp13 > 0.0 ? tmp20 : tmp13) < tmp8 ? 1 : 0.0) * (tmp13 > 0.0 ? tmp35 : 0.0);
    const auto tmp37 = 2 * tmp7;
    const auto tmp38 = tmp3 + tmp3;
    const auto tmp39 = tmp38 / tmp37;
    const auto tmp40 = 2 * tmp39;
    const auto tmp41 = tmp40 * tmp39;
    const auto tmp42 = -1 * tmp41;
    const auto tmp43 = 2 + tmp42;
    const auto tmp44 = tmp43 / tmp37;
    const auto tmp45 = -1 * ((tmp13 > 0.0 ? tmp20 : tmp13) < tmp8 ? 1 : 0.0);
    const auto tmp46 = 1.0 + tmp45;
    const auto tmp47 = tmp46 * tmp44;
    const auto tmp48 = tmp47 + tmp36;
    const auto tmp49 = tmp48 * (tmp23 > tmp22 ? 1 : 0.0);
    const auto tmp50 = ((tmp13 > 0.0 ? tmp20 : tmp13) > tmp8 ? 1 : 0.0) * (tmp13 > 0.0 ? tmp35 : 0.0);
    const auto tmp51 = -1 * ((tmp13 > 0.0 ? tmp20 : tmp13) > tmp8 ? 1 : 0.0);
    const auto tmp52 = 1.0 + tmp51;
    const auto tmp53 = tmp52 * tmp44;
    const auto tmp54 = tmp53 + tmp50;
    const auto tmp55 = -1 * tmp54;
    const auto tmp56 = -1 * (tmp23 > tmp22 ? 1 : 0.0);
    const auto tmp57 = 1.0 + tmp56;
    const auto tmp58 = tmp57 * tmp55;
    const auto tmp59 = tmp58 + tmp49;
    const auto tmp60 = (tmp10 > 0.0 ? 1 : 0.0) * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp61 = tmp60 * tmp14;
    const auto tmp62 = tmp61 + tmp61;
    const auto tmp63 = tmp62 / tmp24;
    const auto tmp64 = 2 * tmp63;
    const auto tmp65 = tmp64 * tmp28;
    const auto tmp66 = -1 * tmp65;
    const auto tmp67 = tmp66 / tmp24;
    const auto tmp68 = ((tmp13 > 0.0 ? tmp20 : tmp13) < tmp8 ? 1 : 0.0) * (tmp13 > 0.0 ? tmp67 : 0.0);
    const auto tmp69 = tmp1 + tmp1;
    const auto tmp70 = tmp69 / tmp37;
    const auto tmp71 = 2 * tmp70;
    const auto tmp72 = tmp71 * tmp39;
    const auto tmp73 = -1 * tmp72;
    const auto tmp74 = tmp73 / tmp37;
    const auto tmp75 = tmp46 * tmp74;
    const auto tmp76 = tmp75 + tmp68;
    const auto tmp77 = tmp76 * (tmp23 > tmp22 ? 1 : 0.0);
    const auto tmp78 = ((tmp13 > 0.0 ? tmp20 : tmp13) > tmp8 ? 1 : 0.0) * (tmp13 > 0.0 ? tmp67 : 0.0);
    const auto tmp79 = tmp52 * tmp74;
    const auto tmp80 = tmp79 + tmp78;
    const auto tmp81 = -1 * tmp80;
    const auto tmp82 = tmp57 * tmp81;
    const auto tmp83 = tmp82 + tmp77;
    const auto tmp84 = tmp29 * tmp63;
    const auto tmp85 = -1 * tmp84;
    const auto tmp86 = tmp85 / tmp24;
    const auto tmp87 = ((tmp13 > 0.0 ? tmp20 : tmp13) < tmp8 ? 1 : 0.0) * (tmp13 > 0.0 ? tmp86 : 0.0);
    const auto tmp88 = tmp40 * tmp70;
    const auto tmp89 = -1 * tmp88;
    const auto tmp90 = tmp89 / tmp37;
    const auto tmp91 = tmp46 * tmp90;
    const auto tmp92 = tmp91 + tmp87;
    const auto tmp93 = tmp92 * (tmp23 > tmp22 ? 1 : 0.0);
    const auto tmp94 = ((tmp13 > 0.0 ? tmp20 : tmp13) > tmp8 ? 1 : 0.0) * (tmp13 > 0.0 ? tmp86 : 0.0);
    const auto tmp95 = tmp52 * tmp90;
    const auto tmp96 = tmp95 + tmp94;
    const auto tmp97 = -1 * tmp96;
    const auto tmp98 = tmp57 * tmp97;
    const auto tmp99 = tmp98 + tmp93;
    const auto tmp100 = tmp64 * tmp63;
    const auto tmp101 = -1 * tmp100;
    const auto tmp102 = tmp60 * tmp60;
    const auto tmp103 = tmp102 + tmp102;
    const auto tmp104 = tmp103 + tmp101;
    const auto tmp105 = tmp104 / tmp24;
    const auto tmp106 = ((tmp13 > 0.0 ? tmp20 : tmp13) < tmp8 ? 1 : 0.0) * (tmp13 > 0.0 ? tmp105 : 0.0);
    const auto tmp107 = tmp71 * tmp70;
    const auto tmp108 = -1 * tmp107;
    const auto tmp109 = 2 + tmp108;
    const auto tmp110 = tmp109 / tmp37;
    const auto tmp111 = tmp46 * tmp110;
    const auto tmp112 = tmp111 + tmp106;
    const auto tmp113 = tmp112 * (tmp23 > tmp22 ? 1 : 0.0);
    const auto tmp114 = ((tmp13 > 0.0 ? tmp20 : tmp13) > tmp8 ? 1 : 0.0) * (tmp13 > 0.0 ? tmp105 : 0.0);
    const auto tmp115 = tmp52 * tmp110;
    const auto tmp116 = tmp115 + tmp114;
    const auto tmp117 = -1 * tmp116;
    const auto tmp118 = tmp57 * tmp117;
    const auto tmp119 = tmp118 + tmp113;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp59;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp83;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp99;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp119;
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

} // namespace UFLLocalFunctions_6343878b30d190cc70b631d882009dec

PYBIND11_MODULE( localfunction_6343878b30d190cc70b631d882009dec_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_6343878b30d190cc70b631d882009dec::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_6343878b30d190cc70b631d882009dec::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_6343878b30d190cc70b631d882009dec_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
