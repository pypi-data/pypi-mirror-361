#ifndef GUARD_639a3f3873411f43337e687cb070368f
#define GUARD_639a3f3873411f43337e687cb070368f

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

namespace UFLLocalFunctions_639a3f3873411f43337e687cb070368f
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
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = tmp0[ 1 ] / 0.5;
    const auto tmp2 = -0.3 + tmp1;
    const auto tmp3 = std::abs( tmp2 );
    const auto tmp4 = -0.3 + tmp3;
    const auto tmp5 = tmp0[ 0 ] / 0.5;
    const auto tmp6 = -0.1 + tmp5;
    const auto tmp7 = std::abs( tmp6 );
    const auto tmp8 = -0.8 + tmp7;
    const auto tmp9 = std::max( tmp8, tmp4 );
    const auto tmp10 = std::max( tmp4, 0.0 );
    const auto tmp11 = tmp10 * tmp10;
    const auto tmp12 = std::max( tmp8, 0.0 );
    const auto tmp13 = tmp12 * tmp12;
    const auto tmp14 = tmp13 + tmp11;
    const auto tmp15 = 1e-10 + tmp14;
    const auto tmp16 = std::sqrt( tmp15 );
    const auto tmp17 = 0.5 * (tmp9 > 0.0 ? tmp16 : tmp9);
    result[ 0 ] = tmp17;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = tmp0[ 1 ] / 0.5;
    const auto tmp2 = -0.3 + tmp1;
    const auto tmp3 = std::abs( tmp2 );
    const auto tmp4 = -0.3 + tmp3;
    const auto tmp5 = tmp0[ 0 ] / 0.5;
    const auto tmp6 = -0.1 + tmp5;
    const auto tmp7 = std::abs( tmp6 );
    const auto tmp8 = -0.8 + tmp7;
    const auto tmp9 = 2.0 * (tmp6 == 0.0 ? 0.0 : (tmp6 < 0.0 ? -1 : 1));
    const auto tmp10 = tmp9 * (tmp8 > tmp4 ? 1 : 0.0);
    const auto tmp11 = std::max( tmp4, 0.0 );
    const auto tmp12 = tmp11 * tmp11;
    const auto tmp13 = std::max( tmp8, 0.0 );
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp14 + tmp12;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = 2 * tmp17;
    const auto tmp19 = tmp9 * (tmp8 > 0.0 ? 1 : 0.0);
    const auto tmp20 = tmp19 * tmp13;
    const auto tmp21 = tmp20 + tmp20;
    const auto tmp22 = tmp21 / tmp18;
    const auto tmp23 = std::max( tmp8, tmp4 );
    const auto tmp24 = 0.5 * (tmp23 > 0.0 ? tmp22 : tmp10);
    const auto tmp25 = 2.0 * (tmp2 == 0.0 ? 0.0 : (tmp2 < 0.0 ? -1 : 1));
    const auto tmp26 = -1 * (tmp8 > tmp4 ? 1 : 0.0);
    const auto tmp27 = 1.0 + tmp26;
    const auto tmp28 = tmp27 * tmp25;
    const auto tmp29 = tmp25 * (tmp4 > 0.0 ? 1 : 0.0);
    const auto tmp30 = tmp29 * tmp11;
    const auto tmp31 = tmp30 + tmp30;
    const auto tmp32 = tmp31 / tmp18;
    const auto tmp33 = 0.5 * (tmp23 > 0.0 ? tmp32 : tmp28);
    (result[ 0 ])[ 0 ] = tmp24;
    (result[ 0 ])[ 1 ] = tmp33;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::abs;
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = tmp0[ 1 ] / 0.5;
    const auto tmp2 = -0.3 + tmp1;
    const auto tmp3 = std::abs( tmp2 );
    const auto tmp4 = -0.3 + tmp3;
    const auto tmp5 = std::max( tmp4, 0.0 );
    const auto tmp6 = tmp5 * tmp5;
    const auto tmp7 = tmp0[ 0 ] / 0.5;
    const auto tmp8 = -0.1 + tmp7;
    const auto tmp9 = std::abs( tmp8 );
    const auto tmp10 = -0.8 + tmp9;
    const auto tmp11 = std::max( tmp10, 0.0 );
    const auto tmp12 = tmp11 * tmp11;
    const auto tmp13 = tmp12 + tmp6;
    const auto tmp14 = 1e-10 + tmp13;
    const auto tmp15 = std::sqrt( tmp14 );
    const auto tmp16 = 2 * tmp15;
    const auto tmp17 = 2.0 * (tmp8 == 0.0 ? 0.0 : (tmp8 < 0.0 ? -1 : 1));
    const auto tmp18 = tmp17 * (tmp10 > 0.0 ? 1 : 0.0);
    const auto tmp19 = tmp18 * tmp11;
    const auto tmp20 = tmp19 + tmp19;
    const auto tmp21 = tmp20 / tmp16;
    const auto tmp22 = 2 * tmp21;
    const auto tmp23 = tmp22 * tmp21;
    const auto tmp24 = -1 * tmp23;
    const auto tmp25 = tmp18 * tmp18;
    const auto tmp26 = tmp25 + tmp25;
    const auto tmp27 = tmp26 + tmp24;
    const auto tmp28 = tmp27 / tmp16;
    const auto tmp29 = std::max( tmp10, tmp4 );
    const auto tmp30 = 0.5 * (tmp29 > 0.0 ? tmp28 : 0.0);
    const auto tmp31 = 2.0 * (tmp2 == 0.0 ? 0.0 : (tmp2 < 0.0 ? -1 : 1));
    const auto tmp32 = tmp31 * (tmp4 > 0.0 ? 1 : 0.0);
    const auto tmp33 = tmp32 * tmp5;
    const auto tmp34 = tmp33 + tmp33;
    const auto tmp35 = tmp34 / tmp16;
    const auto tmp36 = 2 * tmp35;
    const auto tmp37 = tmp36 * tmp21;
    const auto tmp38 = -1 * tmp37;
    const auto tmp39 = tmp38 / tmp16;
    const auto tmp40 = 0.5 * (tmp29 > 0.0 ? tmp39 : 0.0);
    const auto tmp41 = tmp22 * tmp35;
    const auto tmp42 = -1 * tmp41;
    const auto tmp43 = tmp42 / tmp16;
    const auto tmp44 = 0.5 * (tmp29 > 0.0 ? tmp43 : 0.0);
    const auto tmp45 = tmp36 * tmp35;
    const auto tmp46 = -1 * tmp45;
    const auto tmp47 = tmp32 * tmp32;
    const auto tmp48 = tmp47 + tmp47;
    const auto tmp49 = tmp48 + tmp46;
    const auto tmp50 = tmp49 / tmp16;
    const auto tmp51 = 0.5 * (tmp29 > 0.0 ? tmp50 : 0.0);
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp30;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp40;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp44;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp51;
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

} // namespace UFLLocalFunctions_639a3f3873411f43337e687cb070368f

PYBIND11_MODULE( localfunction_639a3f3873411f43337e687cb070368f_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_639a3f3873411f43337e687cb070368f::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_639a3f3873411f43337e687cb070368f::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_639a3f3873411f43337e687cb070368f_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
