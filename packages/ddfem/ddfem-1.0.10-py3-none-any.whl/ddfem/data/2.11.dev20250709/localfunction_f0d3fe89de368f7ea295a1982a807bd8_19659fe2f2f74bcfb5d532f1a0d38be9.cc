#ifndef GUARD_f0d3fe89de368f7ea295a1982a807bd8
#define GUARD_f0d3fe89de368f7ea295a1982a807bd8

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

namespace UFLLocalFunctions_f0d3fe89de368f7ea295a1982a807bd8
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
    const auto tmp21 = std::min( tmp13 > 0.0 ? tmp20 : tmp13, tmp8 );
    result[ 0 ] = tmp21;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.1 + tmp0[ 0 ];
    const auto tmp2 = -0.3 + tmp0[ 1 ];
    const auto tmp3 = std::abs( tmp2 );
    const auto tmp4 = -0.3 + tmp3;
    const auto tmp5 = std::abs( tmp1 );
    const auto tmp6 = -0.8 + tmp5;
    const auto tmp7 = (tmp6 > tmp4 ? 1 : 0.0) * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp8 = std::max( tmp4, 0.0 );
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = std::max( tmp6, 0.0 );
    const auto tmp11 = tmp10 * tmp10;
    const auto tmp12 = tmp11 + tmp9;
    const auto tmp13 = 1e-10 + tmp12;
    const auto tmp14 = std::sqrt( tmp13 );
    const auto tmp15 = 2 * tmp14;
    const auto tmp16 = (tmp6 > 0.0 ? 1 : 0.0) * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp17 = tmp16 * tmp10;
    const auto tmp18 = tmp17 + tmp17;
    const auto tmp19 = tmp18 / tmp15;
    const auto tmp20 = std::max( tmp6, tmp4 );
    const auto tmp21 = tmp2 * tmp2;
    const auto tmp22 = tmp1 * tmp1;
    const auto tmp23 = tmp22 + tmp21;
    const auto tmp24 = 1e-10 + tmp23;
    const auto tmp25 = std::sqrt( tmp24 );
    const auto tmp26 = -0.5 + tmp25;
    const auto tmp27 = ((tmp20 > 0.0 ? tmp14 : tmp20) < tmp26 ? 1 : 0.0) * (tmp20 > 0.0 ? tmp19 : tmp7);
    const auto tmp28 = 2 * tmp25;
    const auto tmp29 = tmp1 + tmp1;
    const auto tmp30 = tmp29 / tmp28;
    const auto tmp31 = -1 * ((tmp20 > 0.0 ? tmp14 : tmp20) < tmp26 ? 1 : 0.0);
    const auto tmp32 = 1.0 + tmp31;
    const auto tmp33 = tmp32 * tmp30;
    const auto tmp34 = tmp33 + tmp27;
    const auto tmp35 = -1 * (tmp6 > tmp4 ? 1 : 0.0);
    const auto tmp36 = 1.0 + tmp35;
    const auto tmp37 = tmp36 * (tmp2 == 0.0 ? 0.0 : (tmp2 < 0.0 ? -1 : 1));
    const auto tmp38 = (tmp4 > 0.0 ? 1 : 0.0) * (tmp2 == 0.0 ? 0.0 : (tmp2 < 0.0 ? -1 : 1));
    const auto tmp39 = tmp38 * tmp8;
    const auto tmp40 = tmp39 + tmp39;
    const auto tmp41 = tmp40 / tmp15;
    const auto tmp42 = ((tmp20 > 0.0 ? tmp14 : tmp20) < tmp26 ? 1 : 0.0) * (tmp20 > 0.0 ? tmp41 : tmp37);
    const auto tmp43 = tmp2 + tmp2;
    const auto tmp44 = tmp43 / tmp28;
    const auto tmp45 = tmp32 * tmp44;
    const auto tmp46 = tmp45 + tmp42;
    (result[ 0 ])[ 0 ] = tmp34;
    (result[ 0 ])[ 1 ] = tmp46;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::abs;
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.3 + tmp0[ 1 ];
    const auto tmp2 = std::abs( tmp1 );
    const auto tmp3 = -0.3 + tmp2;
    const auto tmp4 = std::max( tmp3, 0.0 );
    const auto tmp5 = tmp4 * tmp4;
    const auto tmp6 = -0.1 + tmp0[ 0 ];
    const auto tmp7 = std::abs( tmp6 );
    const auto tmp8 = -0.8 + tmp7;
    const auto tmp9 = std::max( tmp8, 0.0 );
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = tmp10 + tmp5;
    const auto tmp12 = 1e-10 + tmp11;
    const auto tmp13 = std::sqrt( tmp12 );
    const auto tmp14 = 2 * tmp13;
    const auto tmp15 = (tmp8 > 0.0 ? 1 : 0.0) * (tmp6 == 0.0 ? 0.0 : (tmp6 < 0.0 ? -1 : 1));
    const auto tmp16 = tmp15 * tmp9;
    const auto tmp17 = tmp16 + tmp16;
    const auto tmp18 = tmp17 / tmp14;
    const auto tmp19 = 2 * tmp18;
    const auto tmp20 = tmp19 * tmp18;
    const auto tmp21 = -1 * tmp20;
    const auto tmp22 = tmp15 * tmp15;
    const auto tmp23 = tmp22 + tmp22;
    const auto tmp24 = tmp23 + tmp21;
    const auto tmp25 = tmp24 / tmp14;
    const auto tmp26 = std::max( tmp8, tmp3 );
    const auto tmp27 = tmp1 * tmp1;
    const auto tmp28 = tmp6 * tmp6;
    const auto tmp29 = tmp28 + tmp27;
    const auto tmp30 = 1e-10 + tmp29;
    const auto tmp31 = std::sqrt( tmp30 );
    const auto tmp32 = -0.5 + tmp31;
    const auto tmp33 = ((tmp26 > 0.0 ? tmp13 : tmp26) < tmp32 ? 1 : 0.0) * (tmp26 > 0.0 ? tmp25 : 0.0);
    const auto tmp34 = 2 * tmp31;
    const auto tmp35 = tmp6 + tmp6;
    const auto tmp36 = tmp35 / tmp34;
    const auto tmp37 = 2 * tmp36;
    const auto tmp38 = tmp37 * tmp36;
    const auto tmp39 = -1 * tmp38;
    const auto tmp40 = 2 + tmp39;
    const auto tmp41 = tmp40 / tmp34;
    const auto tmp42 = -1 * ((tmp26 > 0.0 ? tmp13 : tmp26) < tmp32 ? 1 : 0.0);
    const auto tmp43 = 1.0 + tmp42;
    const auto tmp44 = tmp43 * tmp41;
    const auto tmp45 = tmp44 + tmp33;
    const auto tmp46 = (tmp3 > 0.0 ? 1 : 0.0) * (tmp1 == 0.0 ? 0.0 : (tmp1 < 0.0 ? -1 : 1));
    const auto tmp47 = tmp46 * tmp4;
    const auto tmp48 = tmp47 + tmp47;
    const auto tmp49 = tmp48 / tmp14;
    const auto tmp50 = 2 * tmp49;
    const auto tmp51 = tmp50 * tmp18;
    const auto tmp52 = -1 * tmp51;
    const auto tmp53 = tmp52 / tmp14;
    const auto tmp54 = ((tmp26 > 0.0 ? tmp13 : tmp26) < tmp32 ? 1 : 0.0) * (tmp26 > 0.0 ? tmp53 : 0.0);
    const auto tmp55 = tmp1 + tmp1;
    const auto tmp56 = tmp55 / tmp34;
    const auto tmp57 = 2 * tmp56;
    const auto tmp58 = tmp57 * tmp36;
    const auto tmp59 = -1 * tmp58;
    const auto tmp60 = tmp59 / tmp34;
    const auto tmp61 = tmp43 * tmp60;
    const auto tmp62 = tmp61 + tmp54;
    const auto tmp63 = tmp19 * tmp49;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = tmp64 / tmp14;
    const auto tmp66 = ((tmp26 > 0.0 ? tmp13 : tmp26) < tmp32 ? 1 : 0.0) * (tmp26 > 0.0 ? tmp65 : 0.0);
    const auto tmp67 = tmp37 * tmp56;
    const auto tmp68 = -1 * tmp67;
    const auto tmp69 = tmp68 / tmp34;
    const auto tmp70 = tmp43 * tmp69;
    const auto tmp71 = tmp70 + tmp66;
    const auto tmp72 = tmp50 * tmp49;
    const auto tmp73 = -1 * tmp72;
    const auto tmp74 = tmp46 * tmp46;
    const auto tmp75 = tmp74 + tmp74;
    const auto tmp76 = tmp75 + tmp73;
    const auto tmp77 = tmp76 / tmp14;
    const auto tmp78 = ((tmp26 > 0.0 ? tmp13 : tmp26) < tmp32 ? 1 : 0.0) * (tmp26 > 0.0 ? tmp77 : 0.0);
    const auto tmp79 = tmp57 * tmp56;
    const auto tmp80 = -1 * tmp79;
    const auto tmp81 = 2 + tmp80;
    const auto tmp82 = tmp81 / tmp34;
    const auto tmp83 = tmp43 * tmp82;
    const auto tmp84 = tmp83 + tmp78;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp45;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp62;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp71;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp84;
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

} // namespace UFLLocalFunctions_f0d3fe89de368f7ea295a1982a807bd8

PYBIND11_MODULE( localfunction_f0d3fe89de368f7ea295a1982a807bd8_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_f0d3fe89de368f7ea295a1982a807bd8::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_f0d3fe89de368f7ea295a1982a807bd8::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_f0d3fe89de368f7ea295a1982a807bd8_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
