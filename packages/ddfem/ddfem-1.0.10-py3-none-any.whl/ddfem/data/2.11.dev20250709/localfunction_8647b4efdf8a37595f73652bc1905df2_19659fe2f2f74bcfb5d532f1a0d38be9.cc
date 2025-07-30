#ifndef GUARD_8647b4efdf8a37595f73652bc1905df2
#define GUARD_8647b4efdf8a37595f73652bc1905df2

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

namespace UFLLocalFunctions_8647b4efdf8a37595f73652bc1905df2
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
    const auto tmp2 = tmp1[ 1 ] / 0.5;
    const auto tmp3 = -0.3 + tmp2;
    const auto tmp4 = std::abs( tmp3 );
    const auto tmp5 = -0.3 + tmp4;
    const auto tmp6 = tmp1[ 0 ] / 0.5;
    const auto tmp7 = -0.1 + tmp6;
    const auto tmp8 = std::abs( tmp7 );
    const auto tmp9 = -0.8 + tmp8;
    const auto tmp10 = std::max( tmp9, tmp5 );
    const auto tmp11 = std::max( tmp5, 0.0 );
    const auto tmp12 = tmp11 * tmp11;
    const auto tmp13 = std::max( tmp9, 0.0 );
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp14 + tmp12;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = 0.5 * (tmp10 > 0.0 ? tmp17 : tmp10);
    const auto tmp19 = 3 * tmp18;
    const auto tmp20 = tmp19 / tmp0;
    const auto tmp21 = std::tanh( tmp20 );
    const auto tmp22 = -1 * tmp21;
    const auto tmp23 = 1 + tmp22;
    const auto tmp24 = 0.5 * tmp23;
    result[ 0 ] = tmp24;
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
    const auto tmp2 = tmp1[ 1 ] / 0.5;
    const auto tmp3 = -0.3 + tmp2;
    const auto tmp4 = std::abs( tmp3 );
    const auto tmp5 = -0.3 + tmp4;
    const auto tmp6 = tmp1[ 0 ] / 0.5;
    const auto tmp7 = -0.1 + tmp6;
    const auto tmp8 = std::abs( tmp7 );
    const auto tmp9 = -0.8 + tmp8;
    const auto tmp10 = std::max( tmp9, tmp5 );
    const auto tmp11 = std::max( tmp5, 0.0 );
    const auto tmp12 = tmp11 * tmp11;
    const auto tmp13 = std::max( tmp9, 0.0 );
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp14 + tmp12;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = 0.5 * (tmp10 > 0.0 ? tmp17 : tmp10);
    const auto tmp19 = 3 * tmp18;
    const auto tmp20 = tmp19 / tmp0;
    const auto tmp21 = 2.0 * tmp20;
    const auto tmp22 = std::cosh( tmp21 );
    const auto tmp23 = 1.0 + tmp22;
    const auto tmp24 = std::cosh( tmp20 );
    const auto tmp25 = 2.0 * tmp24;
    const auto tmp26 = tmp25 / tmp23;
    const auto tmp27 = std::pow( tmp26, 2 );
    const auto tmp28 = 2.0 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp29 = tmp28 * (tmp9 > tmp5 ? 1 : 0.0);
    const auto tmp30 = 2 * tmp17;
    const auto tmp31 = tmp28 * (tmp9 > 0.0 ? 1 : 0.0);
    const auto tmp32 = tmp31 * tmp13;
    const auto tmp33 = tmp32 + tmp32;
    const auto tmp34 = tmp33 / tmp30;
    const auto tmp35 = 0.5 * (tmp10 > 0.0 ? tmp34 : tmp29);
    const auto tmp36 = 3 * tmp35;
    const auto tmp37 = tmp36 / tmp0;
    const auto tmp38 = tmp37 * tmp27;
    const auto tmp39 = -1 * tmp38;
    const auto tmp40 = 0.5 * tmp39;
    const auto tmp41 = 2.0 * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp42 = -1 * (tmp9 > tmp5 ? 1 : 0.0);
    const auto tmp43 = 1.0 + tmp42;
    const auto tmp44 = tmp43 * tmp41;
    const auto tmp45 = tmp41 * (tmp5 > 0.0 ? 1 : 0.0);
    const auto tmp46 = tmp45 * tmp11;
    const auto tmp47 = tmp46 + tmp46;
    const auto tmp48 = tmp47 / tmp30;
    const auto tmp49 = 0.5 * (tmp10 > 0.0 ? tmp48 : tmp44);
    const auto tmp50 = 3 * tmp49;
    const auto tmp51 = tmp50 / tmp0;
    const auto tmp52 = tmp51 * tmp27;
    const auto tmp53 = -1 * tmp52;
    const auto tmp54 = 0.5 * tmp53;
    (result[ 0 ])[ 0 ] = tmp40;
    (result[ 0 ])[ 1 ] = tmp54;
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
    const auto tmp2 = tmp1[ 1 ] / 0.5;
    const auto tmp3 = -0.3 + tmp2;
    const auto tmp4 = std::abs( tmp3 );
    const auto tmp5 = -0.3 + tmp4;
    const auto tmp6 = tmp1[ 0 ] / 0.5;
    const auto tmp7 = -0.1 + tmp6;
    const auto tmp8 = std::abs( tmp7 );
    const auto tmp9 = -0.8 + tmp8;
    const auto tmp10 = std::max( tmp9, tmp5 );
    const auto tmp11 = std::max( tmp5, 0.0 );
    const auto tmp12 = tmp11 * tmp11;
    const auto tmp13 = std::max( tmp9, 0.0 );
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp14 + tmp12;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = 0.5 * (tmp10 > 0.0 ? tmp17 : tmp10);
    const auto tmp19 = 3 * tmp18;
    const auto tmp20 = tmp19 / tmp0;
    const auto tmp21 = 2.0 * tmp20;
    const auto tmp22 = std::cosh( tmp21 );
    const auto tmp23 = 1.0 + tmp22;
    const auto tmp24 = std::cosh( tmp20 );
    const auto tmp25 = 2.0 * tmp24;
    const auto tmp26 = tmp25 / tmp23;
    const auto tmp27 = std::pow( tmp26, 2 );
    const auto tmp28 = 2 * tmp17;
    const auto tmp29 = 2.0 * (tmp7 == 0.0 ? 0.0 : (tmp7 < 0.0 ? -1 : 1));
    const auto tmp30 = tmp29 * (tmp9 > 0.0 ? 1 : 0.0);
    const auto tmp31 = tmp30 * tmp13;
    const auto tmp32 = tmp31 + tmp31;
    const auto tmp33 = tmp32 / tmp28;
    const auto tmp34 = 2 * tmp33;
    const auto tmp35 = tmp34 * tmp33;
    const auto tmp36 = -1 * tmp35;
    const auto tmp37 = tmp30 * tmp30;
    const auto tmp38 = tmp37 + tmp37;
    const auto tmp39 = tmp38 + tmp36;
    const auto tmp40 = tmp39 / tmp28;
    const auto tmp41 = 0.5 * (tmp10 > 0.0 ? tmp40 : 0.0);
    const auto tmp42 = 3 * tmp41;
    const auto tmp43 = tmp42 / tmp0;
    const auto tmp44 = tmp43 * tmp27;
    const auto tmp45 = tmp29 * (tmp9 > tmp5 ? 1 : 0.0);
    const auto tmp46 = 0.5 * (tmp10 > 0.0 ? tmp33 : tmp45);
    const auto tmp47 = 3 * tmp46;
    const auto tmp48 = tmp47 / tmp0;
    const auto tmp49 = std::sinh( tmp20 );
    const auto tmp50 = tmp48 * tmp49;
    const auto tmp51 = 2.0 * tmp50;
    const auto tmp52 = std::sinh( tmp21 );
    const auto tmp53 = 2.0 * tmp48;
    const auto tmp54 = tmp53 * tmp52;
    const auto tmp55 = tmp54 * tmp26;
    const auto tmp56 = -1 * tmp55;
    const auto tmp57 = tmp56 + tmp51;
    const auto tmp58 = tmp57 / tmp23;
    const auto tmp59 = 2 * tmp58;
    const auto tmp60 = tmp59 * tmp26;
    const auto tmp61 = tmp60 * tmp48;
    const auto tmp62 = tmp61 + tmp44;
    const auto tmp63 = -1 * tmp62;
    const auto tmp64 = 0.5 * tmp63;
    const auto tmp65 = 2.0 * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp66 = tmp65 * (tmp5 > 0.0 ? 1 : 0.0);
    const auto tmp67 = tmp66 * tmp11;
    const auto tmp68 = tmp67 + tmp67;
    const auto tmp69 = tmp68 / tmp28;
    const auto tmp70 = 2 * tmp69;
    const auto tmp71 = tmp70 * tmp33;
    const auto tmp72 = -1 * tmp71;
    const auto tmp73 = tmp72 / tmp28;
    const auto tmp74 = 0.5 * (tmp10 > 0.0 ? tmp73 : 0.0);
    const auto tmp75 = 3 * tmp74;
    const auto tmp76 = tmp75 / tmp0;
    const auto tmp77 = tmp76 * tmp27;
    const auto tmp78 = -1 * (tmp9 > tmp5 ? 1 : 0.0);
    const auto tmp79 = 1.0 + tmp78;
    const auto tmp80 = tmp79 * tmp65;
    const auto tmp81 = 0.5 * (tmp10 > 0.0 ? tmp69 : tmp80);
    const auto tmp82 = 3 * tmp81;
    const auto tmp83 = tmp82 / tmp0;
    const auto tmp84 = tmp83 * tmp49;
    const auto tmp85 = 2.0 * tmp84;
    const auto tmp86 = 2.0 * tmp83;
    const auto tmp87 = tmp86 * tmp52;
    const auto tmp88 = tmp87 * tmp26;
    const auto tmp89 = -1 * tmp88;
    const auto tmp90 = tmp89 + tmp85;
    const auto tmp91 = tmp90 / tmp23;
    const auto tmp92 = 2 * tmp91;
    const auto tmp93 = tmp92 * tmp26;
    const auto tmp94 = tmp93 * tmp48;
    const auto tmp95 = tmp94 + tmp77;
    const auto tmp96 = -1 * tmp95;
    const auto tmp97 = 0.5 * tmp96;
    const auto tmp98 = tmp34 * tmp69;
    const auto tmp99 = -1 * tmp98;
    const auto tmp100 = tmp99 / tmp28;
    const auto tmp101 = 0.5 * (tmp10 > 0.0 ? tmp100 : 0.0);
    const auto tmp102 = 3 * tmp101;
    const auto tmp103 = tmp102 / tmp0;
    const auto tmp104 = tmp103 * tmp27;
    const auto tmp105 = tmp60 * tmp83;
    const auto tmp106 = tmp105 + tmp104;
    const auto tmp107 = -1 * tmp106;
    const auto tmp108 = 0.5 * tmp107;
    const auto tmp109 = tmp70 * tmp69;
    const auto tmp110 = -1 * tmp109;
    const auto tmp111 = tmp66 * tmp66;
    const auto tmp112 = tmp111 + tmp111;
    const auto tmp113 = tmp112 + tmp110;
    const auto tmp114 = tmp113 / tmp28;
    const auto tmp115 = 0.5 * (tmp10 > 0.0 ? tmp114 : 0.0);
    const auto tmp116 = 3 * tmp115;
    const auto tmp117 = tmp116 / tmp0;
    const auto tmp118 = tmp117 * tmp27;
    const auto tmp119 = tmp93 * tmp83;
    const auto tmp120 = tmp119 + tmp118;
    const auto tmp121 = -1 * tmp120;
    const auto tmp122 = 0.5 * tmp121;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp64;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp97;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp108;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp122;
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

} // namespace UFLLocalFunctions_8647b4efdf8a37595f73652bc1905df2

PYBIND11_MODULE( localfunction_8647b4efdf8a37595f73652bc1905df2_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_8647b4efdf8a37595f73652bc1905df2::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_8647b4efdf8a37595f73652bc1905df2::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_8647b4efdf8a37595f73652bc1905df2_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
