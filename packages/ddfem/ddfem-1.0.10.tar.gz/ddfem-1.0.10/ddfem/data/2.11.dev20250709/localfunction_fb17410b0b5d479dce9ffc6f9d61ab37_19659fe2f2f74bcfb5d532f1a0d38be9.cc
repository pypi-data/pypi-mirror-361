#ifndef GUARD_fb17410b0b5d479dce9ffc6f9d61ab37
#define GUARD_fb17410b0b5d479dce9ffc6f9d61ab37

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

namespace UFLLocalFunctions_fb17410b0b5d479dce9ffc6f9d61ab37
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
    const auto tmp2 = 0.4 + tmp1[ 1 ];
    const auto tmp3 = -0.3 + tmp2;
    const auto tmp4 = std::abs( tmp3 );
    const auto tmp5 = -0.3 + tmp4;
    const auto tmp6 = -0.1 + tmp1[ 0 ];
    const auto tmp7 = std::abs( tmp6 );
    const auto tmp8 = -0.8 + tmp7;
    const auto tmp9 = std::max( tmp8, tmp5 );
    const auto tmp10 = std::max( tmp5, 0.0 );
    const auto tmp11 = tmp10 * tmp10;
    const auto tmp12 = std::max( tmp8, 0.0 );
    const auto tmp13 = tmp12 * tmp12;
    const auto tmp14 = tmp13 + tmp11;
    const auto tmp15 = 1e-10 + tmp14;
    const auto tmp16 = std::sqrt( tmp15 );
    const auto tmp17 = 3 * (tmp9 > 0.0 ? tmp16 : tmp9);
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
    const auto tmp2 = 0.4 + tmp1[ 1 ];
    const auto tmp3 = -0.3 + tmp2;
    const auto tmp4 = std::abs( tmp3 );
    const auto tmp5 = -0.3 + tmp4;
    const auto tmp6 = -0.1 + tmp1[ 0 ];
    const auto tmp7 = std::abs( tmp6 );
    const auto tmp8 = -0.8 + tmp7;
    const auto tmp9 = std::max( tmp8, tmp5 );
    const auto tmp10 = std::max( tmp5, 0.0 );
    const auto tmp11 = tmp10 * tmp10;
    const auto tmp12 = std::max( tmp8, 0.0 );
    const auto tmp13 = tmp12 * tmp12;
    const auto tmp14 = tmp13 + tmp11;
    const auto tmp15 = 1e-10 + tmp14;
    const auto tmp16 = std::sqrt( tmp15 );
    const auto tmp17 = 3 * (tmp9 > 0.0 ? tmp16 : tmp9);
    const auto tmp18 = tmp17 / tmp0;
    const auto tmp19 = 2.0 * tmp18;
    const auto tmp20 = std::cosh( tmp19 );
    const auto tmp21 = 1.0 + tmp20;
    const auto tmp22 = std::cosh( tmp18 );
    const auto tmp23 = 2.0 * tmp22;
    const auto tmp24 = tmp23 / tmp21;
    const auto tmp25 = std::pow( tmp24, 2 );
    const auto tmp26 = (tmp8 > tmp5 ? 1 : 0.0) * (tmp6 == 0.0 ? 0.0 : (tmp6 < 0.0 ? -1 : 1));
    const auto tmp27 = 2 * tmp16;
    const auto tmp28 = (tmp8 > 0.0 ? 1 : 0.0) * (tmp6 == 0.0 ? 0.0 : (tmp6 < 0.0 ? -1 : 1));
    const auto tmp29 = tmp28 * tmp12;
    const auto tmp30 = tmp29 + tmp29;
    const auto tmp31 = tmp30 / tmp27;
    const auto tmp32 = 3 * (tmp9 > 0.0 ? tmp31 : tmp26);
    const auto tmp33 = tmp32 / tmp0;
    const auto tmp34 = tmp33 * tmp25;
    const auto tmp35 = -1 * tmp34;
    const auto tmp36 = 0.5 * tmp35;
    const auto tmp37 = -1 * (tmp8 > tmp5 ? 1 : 0.0);
    const auto tmp38 = 1.0 + tmp37;
    const auto tmp39 = tmp38 * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp40 = (tmp5 > 0.0 ? 1 : 0.0) * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp41 = tmp40 * tmp10;
    const auto tmp42 = tmp41 + tmp41;
    const auto tmp43 = tmp42 / tmp27;
    const auto tmp44 = 3 * (tmp9 > 0.0 ? tmp43 : tmp39);
    const auto tmp45 = tmp44 / tmp0;
    const auto tmp46 = tmp45 * tmp25;
    const auto tmp47 = -1 * tmp46;
    const auto tmp48 = 0.5 * tmp47;
    (result[ 0 ])[ 0 ] = tmp36;
    (result[ 0 ])[ 1 ] = tmp48;
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
    const auto tmp2 = 0.4 + tmp1[ 1 ];
    const auto tmp3 = -0.3 + tmp2;
    const auto tmp4 = std::abs( tmp3 );
    const auto tmp5 = -0.3 + tmp4;
    const auto tmp6 = -0.1 + tmp1[ 0 ];
    const auto tmp7 = std::abs( tmp6 );
    const auto tmp8 = -0.8 + tmp7;
    const auto tmp9 = std::max( tmp8, tmp5 );
    const auto tmp10 = std::max( tmp5, 0.0 );
    const auto tmp11 = tmp10 * tmp10;
    const auto tmp12 = std::max( tmp8, 0.0 );
    const auto tmp13 = tmp12 * tmp12;
    const auto tmp14 = tmp13 + tmp11;
    const auto tmp15 = 1e-10 + tmp14;
    const auto tmp16 = std::sqrt( tmp15 );
    const auto tmp17 = 3 * (tmp9 > 0.0 ? tmp16 : tmp9);
    const auto tmp18 = tmp17 / tmp0;
    const auto tmp19 = 2.0 * tmp18;
    const auto tmp20 = std::cosh( tmp19 );
    const auto tmp21 = 1.0 + tmp20;
    const auto tmp22 = std::cosh( tmp18 );
    const auto tmp23 = 2.0 * tmp22;
    const auto tmp24 = tmp23 / tmp21;
    const auto tmp25 = std::pow( tmp24, 2 );
    const auto tmp26 = 2 * tmp16;
    const auto tmp27 = (tmp8 > 0.0 ? 1 : 0.0) * (tmp6 == 0.0 ? 0.0 : (tmp6 < 0.0 ? -1 : 1));
    const auto tmp28 = tmp27 * tmp12;
    const auto tmp29 = tmp28 + tmp28;
    const auto tmp30 = tmp29 / tmp26;
    const auto tmp31 = 2 * tmp30;
    const auto tmp32 = tmp31 * tmp30;
    const auto tmp33 = -1 * tmp32;
    const auto tmp34 = tmp27 * tmp27;
    const auto tmp35 = tmp34 + tmp34;
    const auto tmp36 = tmp35 + tmp33;
    const auto tmp37 = tmp36 / tmp26;
    const auto tmp38 = 3 * (tmp9 > 0.0 ? tmp37 : 0.0);
    const auto tmp39 = tmp38 / tmp0;
    const auto tmp40 = tmp39 * tmp25;
    const auto tmp41 = (tmp8 > tmp5 ? 1 : 0.0) * (tmp6 == 0.0 ? 0.0 : (tmp6 < 0.0 ? -1 : 1));
    const auto tmp42 = 3 * (tmp9 > 0.0 ? tmp30 : tmp41);
    const auto tmp43 = tmp42 / tmp0;
    const auto tmp44 = std::sinh( tmp18 );
    const auto tmp45 = tmp43 * tmp44;
    const auto tmp46 = 2.0 * tmp45;
    const auto tmp47 = std::sinh( tmp19 );
    const auto tmp48 = 2.0 * tmp43;
    const auto tmp49 = tmp48 * tmp47;
    const auto tmp50 = tmp49 * tmp24;
    const auto tmp51 = -1 * tmp50;
    const auto tmp52 = tmp51 + tmp46;
    const auto tmp53 = tmp52 / tmp21;
    const auto tmp54 = 2 * tmp53;
    const auto tmp55 = tmp54 * tmp24;
    const auto tmp56 = tmp55 * tmp43;
    const auto tmp57 = tmp56 + tmp40;
    const auto tmp58 = -1 * tmp57;
    const auto tmp59 = 0.5 * tmp58;
    const auto tmp60 = (tmp5 > 0.0 ? 1 : 0.0) * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp61 = tmp60 * tmp10;
    const auto tmp62 = tmp61 + tmp61;
    const auto tmp63 = tmp62 / tmp26;
    const auto tmp64 = 2 * tmp63;
    const auto tmp65 = tmp64 * tmp30;
    const auto tmp66 = -1 * tmp65;
    const auto tmp67 = tmp66 / tmp26;
    const auto tmp68 = 3 * (tmp9 > 0.0 ? tmp67 : 0.0);
    const auto tmp69 = tmp68 / tmp0;
    const auto tmp70 = tmp69 * tmp25;
    const auto tmp71 = -1 * (tmp8 > tmp5 ? 1 : 0.0);
    const auto tmp72 = 1.0 + tmp71;
    const auto tmp73 = tmp72 * (tmp3 == 0.0 ? 0.0 : (tmp3 < 0.0 ? -1 : 1));
    const auto tmp74 = 3 * (tmp9 > 0.0 ? tmp63 : tmp73);
    const auto tmp75 = tmp74 / tmp0;
    const auto tmp76 = tmp75 * tmp44;
    const auto tmp77 = 2.0 * tmp76;
    const auto tmp78 = 2.0 * tmp75;
    const auto tmp79 = tmp78 * tmp47;
    const auto tmp80 = tmp79 * tmp24;
    const auto tmp81 = -1 * tmp80;
    const auto tmp82 = tmp81 + tmp77;
    const auto tmp83 = tmp82 / tmp21;
    const auto tmp84 = 2 * tmp83;
    const auto tmp85 = tmp84 * tmp24;
    const auto tmp86 = tmp85 * tmp43;
    const auto tmp87 = tmp86 + tmp70;
    const auto tmp88 = -1 * tmp87;
    const auto tmp89 = 0.5 * tmp88;
    const auto tmp90 = tmp31 * tmp63;
    const auto tmp91 = -1 * tmp90;
    const auto tmp92 = tmp91 / tmp26;
    const auto tmp93 = 3 * (tmp9 > 0.0 ? tmp92 : 0.0);
    const auto tmp94 = tmp93 / tmp0;
    const auto tmp95 = tmp94 * tmp25;
    const auto tmp96 = tmp55 * tmp75;
    const auto tmp97 = tmp96 + tmp95;
    const auto tmp98 = -1 * tmp97;
    const auto tmp99 = 0.5 * tmp98;
    const auto tmp100 = tmp64 * tmp63;
    const auto tmp101 = -1 * tmp100;
    const auto tmp102 = tmp60 * tmp60;
    const auto tmp103 = tmp102 + tmp102;
    const auto tmp104 = tmp103 + tmp101;
    const auto tmp105 = tmp104 / tmp26;
    const auto tmp106 = 3 * (tmp9 > 0.0 ? tmp105 : 0.0);
    const auto tmp107 = tmp106 / tmp0;
    const auto tmp108 = tmp107 * tmp25;
    const auto tmp109 = tmp85 * tmp75;
    const auto tmp110 = tmp109 + tmp108;
    const auto tmp111 = -1 * tmp110;
    const auto tmp112 = 0.5 * tmp111;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp59;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp89;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp99;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp112;
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

} // namespace UFLLocalFunctions_fb17410b0b5d479dce9ffc6f9d61ab37

PYBIND11_MODULE( localfunction_fb17410b0b5d479dce9ffc6f9d61ab37_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_fb17410b0b5d479dce9ffc6f9d61ab37::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_fb17410b0b5d479dce9ffc6f9d61ab37::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_fb17410b0b5d479dce9ffc6f9d61ab37_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
