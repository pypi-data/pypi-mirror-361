#ifndef GUARD_e69118a51208cfab8a028711e966e76c
#define GUARD_e69118a51208cfab8a028711e966e76c

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

namespace UFLLocalFunctions_e69118a51208cfab8a028711e966e76c
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
    using std::min;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = 0.2 + tmp0[ 0 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = -0.2 + tmp0[ 0 ];
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = tmp3 + tmp9;
    const auto tmp11 = 1e-10 + tmp10;
    const auto tmp12 = std::sqrt( tmp11 );
    const auto tmp13 = -0.5 + tmp12;
    const auto tmp14 = std::min( tmp13, tmp7 );
    result[ 0 ] = tmp14;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = 0.2 + tmp0[ 0 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = -0.2 + tmp0[ 0 ];
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = tmp3 + tmp9;
    const auto tmp11 = 1e-10 + tmp10;
    const auto tmp12 = std::sqrt( tmp11 );
    const auto tmp13 = -0.5 + tmp12;
    const auto tmp14 = 2 * tmp12;
    const auto tmp15 = tmp8 + tmp8;
    const auto tmp16 = tmp15 / tmp14;
    const auto tmp17 = tmp16 * (tmp13 < tmp7 ? 1 : 0.0);
    const auto tmp18 = 2 * tmp6;
    const auto tmp19 = tmp1 + tmp1;
    const auto tmp20 = tmp19 / tmp18;
    const auto tmp21 = -1 * (tmp13 < tmp7 ? 1 : 0.0);
    const auto tmp22 = 1.0 + tmp21;
    const auto tmp23 = tmp22 * tmp20;
    const auto tmp24 = tmp23 + tmp17;
    const auto tmp25 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp26 = tmp25 / tmp14;
    const auto tmp27 = tmp26 * (tmp13 < tmp7 ? 1 : 0.0);
    const auto tmp28 = tmp25 / tmp18;
    const auto tmp29 = tmp22 * tmp28;
    const auto tmp30 = tmp29 + tmp27;
    (result[ 0 ])[ 0 ] = tmp24;
    (result[ 0 ])[ 1 ] = tmp30;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = 0.2 + tmp0[ 0 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = -0.2 + tmp0[ 0 ];
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = tmp3 + tmp9;
    const auto tmp11 = 1e-10 + tmp10;
    const auto tmp12 = std::sqrt( tmp11 );
    const auto tmp13 = -0.5 + tmp12;
    const auto tmp14 = 2 * tmp12;
    const auto tmp15 = tmp8 + tmp8;
    const auto tmp16 = tmp15 / tmp14;
    const auto tmp17 = 2 * tmp16;
    const auto tmp18 = tmp17 * tmp16;
    const auto tmp19 = -1 * tmp18;
    const auto tmp20 = 2 + tmp19;
    const auto tmp21 = tmp20 / tmp14;
    const auto tmp22 = tmp21 * (tmp13 < tmp7 ? 1 : 0.0);
    const auto tmp23 = 2 * tmp6;
    const auto tmp24 = tmp1 + tmp1;
    const auto tmp25 = tmp24 / tmp23;
    const auto tmp26 = 2 * tmp25;
    const auto tmp27 = tmp26 * tmp25;
    const auto tmp28 = -1 * tmp27;
    const auto tmp29 = 2 + tmp28;
    const auto tmp30 = tmp29 / tmp23;
    const auto tmp31 = -1 * (tmp13 < tmp7 ? 1 : 0.0);
    const auto tmp32 = 1.0 + tmp31;
    const auto tmp33 = tmp32 * tmp30;
    const auto tmp34 = tmp33 + tmp22;
    const auto tmp35 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp36 = tmp35 / tmp14;
    const auto tmp37 = 2 * tmp36;
    const auto tmp38 = tmp37 * tmp16;
    const auto tmp39 = -1 * tmp38;
    const auto tmp40 = tmp39 / tmp14;
    const auto tmp41 = tmp40 * (tmp13 < tmp7 ? 1 : 0.0);
    const auto tmp42 = tmp35 / tmp23;
    const auto tmp43 = 2 * tmp42;
    const auto tmp44 = tmp43 * tmp25;
    const auto tmp45 = -1 * tmp44;
    const auto tmp46 = tmp45 / tmp23;
    const auto tmp47 = tmp32 * tmp46;
    const auto tmp48 = tmp47 + tmp41;
    const auto tmp49 = tmp17 * tmp36;
    const auto tmp50 = -1 * tmp49;
    const auto tmp51 = tmp50 / tmp14;
    const auto tmp52 = tmp51 * (tmp13 < tmp7 ? 1 : 0.0);
    const auto tmp53 = tmp26 * tmp42;
    const auto tmp54 = -1 * tmp53;
    const auto tmp55 = tmp54 / tmp23;
    const auto tmp56 = tmp32 * tmp55;
    const auto tmp57 = tmp56 + tmp52;
    const auto tmp58 = tmp37 * tmp36;
    const auto tmp59 = -1 * tmp58;
    const auto tmp60 = 2 + tmp59;
    const auto tmp61 = tmp60 / tmp14;
    const auto tmp62 = tmp61 * (tmp13 < tmp7 ? 1 : 0.0);
    const auto tmp63 = tmp43 * tmp42;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = 2 + tmp64;
    const auto tmp66 = tmp65 / tmp23;
    const auto tmp67 = tmp32 * tmp66;
    const auto tmp68 = tmp67 + tmp62;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp34;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp48;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp57;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp68;
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

} // namespace UFLLocalFunctions_e69118a51208cfab8a028711e966e76c

PYBIND11_MODULE( localfunction_e69118a51208cfab8a028711e966e76c_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_e69118a51208cfab8a028711e966e76c::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_e69118a51208cfab8a028711e966e76c::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_e69118a51208cfab8a028711e966e76c_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
