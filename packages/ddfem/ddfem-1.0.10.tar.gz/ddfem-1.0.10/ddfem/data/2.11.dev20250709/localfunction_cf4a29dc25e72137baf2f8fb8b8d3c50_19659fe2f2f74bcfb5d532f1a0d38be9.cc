#ifndef GUARD_cf4a29dc25e72137baf2f8fb8b8d3c50
#define GUARD_cf4a29dc25e72137baf2f8fb8b8d3c50

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

namespace UFLLocalFunctions_cf4a29dc25e72137baf2f8fb8b8d3c50
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
    using std::sqrt;
    using std::tanh;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = -0.1 + tmp0[ 0 ];
    const auto tmp4 = tmp3 * tmp3;
    const auto tmp5 = tmp4 + tmp2;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -0.5 + tmp7;
    const auto tmp9 = 3 * tmp8;
    const auto tmp10 = tmp9 / 0.1;
    const auto tmp11 = std::tanh( tmp10 );
    const auto tmp12 = -1 * tmp11;
    const auto tmp13 = 1 + tmp12;
    const auto tmp14 = 0.5 * tmp13;
    result[ 0 ] = tmp14;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::cosh;
    using std::pow;
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
    const auto tmp9 = 3 * tmp8;
    const auto tmp10 = tmp9 / 0.1;
    const auto tmp11 = 2.0 * tmp10;
    const auto tmp12 = std::cosh( tmp11 );
    const auto tmp13 = 1.0 + tmp12;
    const auto tmp14 = std::cosh( tmp10 );
    const auto tmp15 = 2.0 * tmp14;
    const auto tmp16 = tmp15 / tmp13;
    const auto tmp17 = std::pow( tmp16, 2 );
    const auto tmp18 = 2 * tmp7;
    const auto tmp19 = tmp3 + tmp3;
    const auto tmp20 = tmp19 / tmp18;
    const auto tmp21 = 3 * tmp20;
    const auto tmp22 = tmp21 / 0.1;
    const auto tmp23 = tmp22 * tmp17;
    const auto tmp24 = -1 * tmp23;
    const auto tmp25 = 0.5 * tmp24;
    const auto tmp26 = tmp1 + tmp1;
    const auto tmp27 = tmp26 / tmp18;
    const auto tmp28 = 3 * tmp27;
    const auto tmp29 = tmp28 / 0.1;
    const auto tmp30 = tmp29 * tmp17;
    const auto tmp31 = -1 * tmp30;
    const auto tmp32 = 0.5 * tmp31;
    (result[ 0 ])[ 0 ] = tmp25;
    (result[ 0 ])[ 1 ] = tmp32;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::cosh;
    using std::pow;
    using std::sinh;
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
    const auto tmp9 = 3 * tmp8;
    const auto tmp10 = tmp9 / 0.1;
    const auto tmp11 = 2.0 * tmp10;
    const auto tmp12 = std::cosh( tmp11 );
    const auto tmp13 = 1.0 + tmp12;
    const auto tmp14 = std::cosh( tmp10 );
    const auto tmp15 = 2.0 * tmp14;
    const auto tmp16 = tmp15 / tmp13;
    const auto tmp17 = std::pow( tmp16, 2 );
    const auto tmp18 = 2 * tmp7;
    const auto tmp19 = tmp3 + tmp3;
    const auto tmp20 = tmp19 / tmp18;
    const auto tmp21 = 2 * tmp20;
    const auto tmp22 = tmp21 * tmp20;
    const auto tmp23 = -1 * tmp22;
    const auto tmp24 = 2 + tmp23;
    const auto tmp25 = tmp24 / tmp18;
    const auto tmp26 = 3 * tmp25;
    const auto tmp27 = tmp26 / 0.1;
    const auto tmp28 = tmp27 * tmp17;
    const auto tmp29 = 3 * tmp20;
    const auto tmp30 = tmp29 / 0.1;
    const auto tmp31 = std::sinh( tmp10 );
    const auto tmp32 = tmp30 * tmp31;
    const auto tmp33 = 2.0 * tmp32;
    const auto tmp34 = std::sinh( tmp11 );
    const auto tmp35 = 2.0 * tmp30;
    const auto tmp36 = tmp35 * tmp34;
    const auto tmp37 = tmp36 * tmp16;
    const auto tmp38 = -1 * tmp37;
    const auto tmp39 = tmp38 + tmp33;
    const auto tmp40 = tmp39 / tmp13;
    const auto tmp41 = 2 * tmp40;
    const auto tmp42 = tmp41 * tmp16;
    const auto tmp43 = tmp42 * tmp30;
    const auto tmp44 = tmp43 + tmp28;
    const auto tmp45 = -1 * tmp44;
    const auto tmp46 = 0.5 * tmp45;
    const auto tmp47 = tmp1 + tmp1;
    const auto tmp48 = tmp47 / tmp18;
    const auto tmp49 = 2 * tmp48;
    const auto tmp50 = tmp49 * tmp20;
    const auto tmp51 = -1 * tmp50;
    const auto tmp52 = tmp51 / tmp18;
    const auto tmp53 = 3 * tmp52;
    const auto tmp54 = tmp53 / 0.1;
    const auto tmp55 = tmp54 * tmp17;
    const auto tmp56 = 3 * tmp48;
    const auto tmp57 = tmp56 / 0.1;
    const auto tmp58 = tmp57 * tmp31;
    const auto tmp59 = 2.0 * tmp58;
    const auto tmp60 = 2.0 * tmp57;
    const auto tmp61 = tmp60 * tmp34;
    const auto tmp62 = tmp61 * tmp16;
    const auto tmp63 = -1 * tmp62;
    const auto tmp64 = tmp63 + tmp59;
    const auto tmp65 = tmp64 / tmp13;
    const auto tmp66 = 2 * tmp65;
    const auto tmp67 = tmp66 * tmp16;
    const auto tmp68 = tmp67 * tmp30;
    const auto tmp69 = tmp68 + tmp55;
    const auto tmp70 = -1 * tmp69;
    const auto tmp71 = 0.5 * tmp70;
    const auto tmp72 = tmp21 * tmp48;
    const auto tmp73 = -1 * tmp72;
    const auto tmp74 = tmp73 / tmp18;
    const auto tmp75 = 3 * tmp74;
    const auto tmp76 = tmp75 / 0.1;
    const auto tmp77 = tmp76 * tmp17;
    const auto tmp78 = tmp42 * tmp57;
    const auto tmp79 = tmp78 + tmp77;
    const auto tmp80 = -1 * tmp79;
    const auto tmp81 = 0.5 * tmp80;
    const auto tmp82 = tmp49 * tmp48;
    const auto tmp83 = -1 * tmp82;
    const auto tmp84 = 2 + tmp83;
    const auto tmp85 = tmp84 / tmp18;
    const auto tmp86 = 3 * tmp85;
    const auto tmp87 = tmp86 / 0.1;
    const auto tmp88 = tmp87 * tmp17;
    const auto tmp89 = tmp67 * tmp57;
    const auto tmp90 = tmp89 + tmp88;
    const auto tmp91 = -1 * tmp90;
    const auto tmp92 = 0.5 * tmp91;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp46;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp71;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp81;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp92;
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

} // namespace UFLLocalFunctions_cf4a29dc25e72137baf2f8fb8b8d3c50

PYBIND11_MODULE( localfunction_cf4a29dc25e72137baf2f8fb8b8d3c50_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_cf4a29dc25e72137baf2f8fb8b8d3c50::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_cf4a29dc25e72137baf2f8fb8b8d3c50::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_cf4a29dc25e72137baf2f8fb8b8d3c50_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
