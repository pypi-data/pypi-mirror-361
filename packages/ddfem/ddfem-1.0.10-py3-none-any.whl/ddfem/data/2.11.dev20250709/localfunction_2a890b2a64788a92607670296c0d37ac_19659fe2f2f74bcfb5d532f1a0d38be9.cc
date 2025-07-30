#ifndef GUARD_2a890b2a64788a92607670296c0d37ac
#define GUARD_2a890b2a64788a92607670296c0d37ac

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

namespace UFLLocalFunctions_2a890b2a64788a92607670296c0d37ac
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
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = std::abs( tmp1 );
    const auto tmp3 = -0.3 + tmp2;
    const auto tmp4 = -0.1 + tmp0[ 0 ];
    const auto tmp5 = std::abs( tmp4 );
    const auto tmp6 = -0.8 + tmp5;
    const auto tmp7 = std::max( tmp6, tmp3 );
    const auto tmp8 = std::max( tmp3, 0.0 );
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = std::max( tmp6, 0.0 );
    const auto tmp11 = tmp10 * tmp10;
    const auto tmp12 = tmp11 + tmp9;
    const auto tmp13 = 1e-10 + tmp12;
    const auto tmp14 = std::sqrt( tmp13 );
    const auto tmp15 = 3 * (tmp7 > 0.0 ? tmp14 : tmp7);
    const auto tmp16 = tmp15 / 0.1;
    const auto tmp17 = std::tanh( tmp16 );
    const auto tmp18 = -1 * tmp17;
    const auto tmp19 = 1 + tmp18;
    const auto tmp20 = 0.5 * tmp19;
    result[ 0 ] = tmp20;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::cosh;
    using std::max;
    using std::pow;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = std::abs( tmp1 );
    const auto tmp3 = -0.3 + tmp2;
    const auto tmp4 = -0.1 + tmp0[ 0 ];
    const auto tmp5 = std::abs( tmp4 );
    const auto tmp6 = -0.8 + tmp5;
    const auto tmp7 = std::max( tmp6, tmp3 );
    const auto tmp8 = std::max( tmp3, 0.0 );
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = std::max( tmp6, 0.0 );
    const auto tmp11 = tmp10 * tmp10;
    const auto tmp12 = tmp11 + tmp9;
    const auto tmp13 = 1e-10 + tmp12;
    const auto tmp14 = std::sqrt( tmp13 );
    const auto tmp15 = 3 * (tmp7 > 0.0 ? tmp14 : tmp7);
    const auto tmp16 = tmp15 / 0.1;
    const auto tmp17 = 2.0 * tmp16;
    const auto tmp18 = std::cosh( tmp17 );
    const auto tmp19 = 1.0 + tmp18;
    const auto tmp20 = std::cosh( tmp16 );
    const auto tmp21 = 2.0 * tmp20;
    const auto tmp22 = tmp21 / tmp19;
    const auto tmp23 = std::pow( tmp22, 2 );
    const auto tmp24 = (tmp6 > tmp3 ? 1 : 0.0) * (tmp4 == 0.0 ? 0.0 : (tmp4 < 0.0 ? -1 : 1));
    const auto tmp25 = 2 * tmp14;
    const auto tmp26 = (tmp6 > 0.0 ? 1 : 0.0) * (tmp4 == 0.0 ? 0.0 : (tmp4 < 0.0 ? -1 : 1));
    const auto tmp27 = tmp26 * tmp10;
    const auto tmp28 = tmp27 + tmp27;
    const auto tmp29 = tmp28 / tmp25;
    const auto tmp30 = 3 * (tmp7 > 0.0 ? tmp29 : tmp24);
    const auto tmp31 = tmp30 / 0.1;
    const auto tmp32 = tmp31 * tmp23;
    const auto tmp33 = -1 * tmp32;
    const auto tmp34 = 0.5 * tmp33;
    const auto tmp35 = -1 * (tmp6 > tmp3 ? 1 : 0.0);
    const auto tmp36 = 1.0 + tmp35;
    const auto tmp37 = tmp36 * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp38 = (tmp3 > 0.0 ? 1 : 0.0) * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp39 = tmp38 * tmp8;
    const auto tmp40 = tmp39 + tmp39;
    const auto tmp41 = tmp40 / tmp25;
    const auto tmp42 = 3 * (tmp7 > 0.0 ? tmp41 : tmp37);
    const auto tmp43 = tmp42 / 0.1;
    const auto tmp44 = tmp43 * tmp23;
    const auto tmp45 = -1 * tmp44;
    const auto tmp46 = 0.5 * tmp45;
    (result[ 0 ])[ 0 ] = tmp34;
    (result[ 0 ])[ 1 ] = tmp46;
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
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = std::abs( tmp1 );
    const auto tmp3 = -0.3 + tmp2;
    const auto tmp4 = -0.1 + tmp0[ 0 ];
    const auto tmp5 = std::abs( tmp4 );
    const auto tmp6 = -0.8 + tmp5;
    const auto tmp7 = std::max( tmp6, tmp3 );
    const auto tmp8 = std::max( tmp3, 0.0 );
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = std::max( tmp6, 0.0 );
    const auto tmp11 = tmp10 * tmp10;
    const auto tmp12 = tmp11 + tmp9;
    const auto tmp13 = 1e-10 + tmp12;
    const auto tmp14 = std::sqrt( tmp13 );
    const auto tmp15 = 3 * (tmp7 > 0.0 ? tmp14 : tmp7);
    const auto tmp16 = tmp15 / 0.1;
    const auto tmp17 = 2.0 * tmp16;
    const auto tmp18 = std::cosh( tmp17 );
    const auto tmp19 = 1.0 + tmp18;
    const auto tmp20 = std::cosh( tmp16 );
    const auto tmp21 = 2.0 * tmp20;
    const auto tmp22 = tmp21 / tmp19;
    const auto tmp23 = std::pow( tmp22, 2 );
    const auto tmp24 = 2 * tmp14;
    const auto tmp25 = (tmp6 > 0.0 ? 1 : 0.0) * (tmp4 == 0.0 ? 0.0 : (tmp4 < 0.0 ? -1 : 1));
    const auto tmp26 = tmp25 * tmp10;
    const auto tmp27 = tmp26 + tmp26;
    const auto tmp28 = tmp27 / tmp24;
    const auto tmp29 = 2 * tmp28;
    const auto tmp30 = tmp29 * tmp28;
    const auto tmp31 = -1 * tmp30;
    const auto tmp32 = tmp25 * tmp25;
    const auto tmp33 = tmp32 + tmp32;
    const auto tmp34 = tmp33 + tmp31;
    const auto tmp35 = tmp34 / tmp24;
    const auto tmp36 = 3 * (tmp7 > 0.0 ? tmp35 : 0.0);
    const auto tmp37 = tmp36 / 0.1;
    const auto tmp38 = tmp37 * tmp23;
    const auto tmp39 = (tmp6 > tmp3 ? 1 : 0.0) * (tmp4 == 0.0 ? 0.0 : (tmp4 < 0.0 ? -1 : 1));
    const auto tmp40 = 3 * (tmp7 > 0.0 ? tmp28 : tmp39);
    const auto tmp41 = tmp40 / 0.1;
    const auto tmp42 = std::sinh( tmp16 );
    const auto tmp43 = tmp41 * tmp42;
    const auto tmp44 = 2.0 * tmp43;
    const auto tmp45 = std::sinh( tmp17 );
    const auto tmp46 = 2.0 * tmp41;
    const auto tmp47 = tmp46 * tmp45;
    const auto tmp48 = tmp47 * tmp22;
    const auto tmp49 = -1 * tmp48;
    const auto tmp50 = tmp49 + tmp44;
    const auto tmp51 = tmp50 / tmp19;
    const auto tmp52 = 2 * tmp51;
    const auto tmp53 = tmp52 * tmp22;
    const auto tmp54 = tmp53 * tmp41;
    const auto tmp55 = tmp54 + tmp38;
    const auto tmp56 = -1 * tmp55;
    const auto tmp57 = 0.5 * tmp56;
    const auto tmp58 = (tmp3 > 0.0 ? 1 : 0.0) * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp59 = tmp58 * tmp8;
    const auto tmp60 = tmp59 + tmp59;
    const auto tmp61 = tmp60 / tmp24;
    const auto tmp62 = 2 * tmp61;
    const auto tmp63 = tmp62 * tmp28;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = tmp64 / tmp24;
    const auto tmp66 = 3 * (tmp7 > 0.0 ? tmp65 : 0.0);
    const auto tmp67 = tmp66 / 0.1;
    const auto tmp68 = tmp67 * tmp23;
    const auto tmp69 = -1 * (tmp6 > tmp3 ? 1 : 0.0);
    const auto tmp70 = 1.0 + tmp69;
    const auto tmp71 = tmp70 * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp72 = 3 * (tmp7 > 0.0 ? tmp61 : tmp71);
    const auto tmp73 = tmp72 / 0.1;
    const auto tmp74 = tmp73 * tmp42;
    const auto tmp75 = 2.0 * tmp74;
    const auto tmp76 = 2.0 * tmp73;
    const auto tmp77 = tmp76 * tmp45;
    const auto tmp78 = tmp77 * tmp22;
    const auto tmp79 = -1 * tmp78;
    const auto tmp80 = tmp79 + tmp75;
    const auto tmp81 = tmp80 / tmp19;
    const auto tmp82 = 2 * tmp81;
    const auto tmp83 = tmp82 * tmp22;
    const auto tmp84 = tmp83 * tmp41;
    const auto tmp85 = tmp84 + tmp68;
    const auto tmp86 = -1 * tmp85;
    const auto tmp87 = 0.5 * tmp86;
    const auto tmp88 = tmp29 * tmp61;
    const auto tmp89 = -1 * tmp88;
    const auto tmp90 = tmp89 / tmp24;
    const auto tmp91 = 3 * (tmp7 > 0.0 ? tmp90 : 0.0);
    const auto tmp92 = tmp91 / 0.1;
    const auto tmp93 = tmp92 * tmp23;
    const auto tmp94 = tmp53 * tmp73;
    const auto tmp95 = tmp94 + tmp93;
    const auto tmp96 = -1 * tmp95;
    const auto tmp97 = 0.5 * tmp96;
    const auto tmp98 = tmp62 * tmp61;
    const auto tmp99 = -1 * tmp98;
    const auto tmp100 = tmp58 * tmp58;
    const auto tmp101 = tmp100 + tmp100;
    const auto tmp102 = tmp101 + tmp99;
    const auto tmp103 = tmp102 / tmp24;
    const auto tmp104 = 3 * (tmp7 > 0.0 ? tmp103 : 0.0);
    const auto tmp105 = tmp104 / 0.1;
    const auto tmp106 = tmp105 * tmp23;
    const auto tmp107 = tmp83 * tmp73;
    const auto tmp108 = tmp107 + tmp106;
    const auto tmp109 = -1 * tmp108;
    const auto tmp110 = 0.5 * tmp109;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp57;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp87;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp97;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp110;
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

} // namespace UFLLocalFunctions_2a890b2a64788a92607670296c0d37ac

PYBIND11_MODULE( localfunction_2a890b2a64788a92607670296c0d37ac_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_2a890b2a64788a92607670296c0d37ac::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_2a890b2a64788a92607670296c0d37ac::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_2a890b2a64788a92607670296c0d37ac_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
