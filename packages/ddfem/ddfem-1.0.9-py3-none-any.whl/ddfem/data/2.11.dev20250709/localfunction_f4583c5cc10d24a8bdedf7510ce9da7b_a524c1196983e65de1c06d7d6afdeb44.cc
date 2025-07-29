#ifndef GUARD_f4583c5cc10d24a8bdedf7510ce9da7b
#define GUARD_f4583c5cc10d24a8bdedf7510ce9da7b

#define USING_DUNE_PYTHON 1
#include <config.h>
#include <dune/alugrid/dgf.hh>
#include <dune/alugrid/grid.hh>
#include <dune/fem/gridpart/adaptiveleafgridpart.hh>
#include <dune/fem/gridpart/filter/simple.hh>
#include <dune/fem/gridpart/filteredgridpart.hh>
#include <dune/fempy/py/gridview.hh>
#include <dune/python/grid/gridview.hh>
#include <dune/python/grid/hierarchical.hh>
#include <dune/fem/function/localfunction/bindable.hh>
#include <dune/fem/common/intersectionside.hh>
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/extensions.h>
#include <dune/fempy/py/grid/gridpart.hh>
#include <dune/common/exceptions.hh>
#include <dune/fempy/function/virtualizedgridfunction.hh>
#include <dune/fempy/py/ufllocalfunction.hh>

namespace UFLLocalFunctions_f4583c5cc10d24a8bdedf7510ce9da7b
{

  // UFLLocalFunction
// ----------------

template< class GridPart, class Coeffbndproj, class Coeffddm, class Coeffsdfprojfull, class Coeffphidomain >
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
  typedef std::tuple< Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 2 > >, Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 1 > >, Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 1 > >, Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 1 > > > CoefficientFunctionSpaceTupleType;
  typedef std::tuple< Coeffbndproj, Coeffddm, Coeffsdfprojfull, Coeffphidomain > CoefficientTupleType;
  template< std::size_t i >
  using CoefficientFunctionSpaceType = std::tuple_element_t< i, CoefficientFunctionSpaceTupleType >;
  template< std::size_t i >
  using CoefficientRangeType = typename CoefficientFunctionSpaceType< i >::RangeType;
  template< std::size_t i >
  using CoefficientJacobianRangeType = typename CoefficientFunctionSpaceType< i >::JacobianRangeType;
  static constexpr bool gridPartValid = Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffbndproj>>() && Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffddm>>() && Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffsdfprojfull>>() && Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffphidomain>>();
  template< std::size_t i >
  using CoefficientType = std::tuple_element_t< i, CoefficientTupleType >;
  template< std::size_t i >
  using ConstantType = typename std::tuple_element_t< i, ConstantTupleType >::element_type;
  using BaseType::entity;
  using BaseType::geometry;

  UFLLocalFunction ( const GridPartType &gridPart, const std::string &name, int order, const Coeffbndproj &coeffbndproj, const Coeffddm &coeffddm, const Coeffsdfprojfull &coeffsdfprojfull, const Coeffphidomain &coeffphidomain, const Dune::Fem::ParameterReader &parameter = Dune::Fem::Parameter::container() )
    : BaseType(gridPart,name,order),
      coefficients_( Dune::Fem::ConstLocalFunction< Coeffbndproj >( coeffbndproj ), Dune::Fem::ConstLocalFunction< Coeffddm >( coeffddm ), Dune::Fem::ConstLocalFunction< Coeffsdfprojfull >( coeffsdfprojfull ), Dune::Fem::ConstLocalFunction< Coeffphidomain >( coeffphidomain ) )
  {}

  void bind ( const IntersectionType &intersection, Side side )
  {
    BaseType::bind(intersection, side);
    std::get< 0 >( coefficients_ ).bind( this->entity() );
    std::get< 1 >( coefficients_ ).bind( this->entity() );
    std::get< 2 >( coefficients_ ).bind( this->entity() );
    std::get< 3 >( coefficients_ ).bind( this->entity() );
  }

  void bind ( const EntityType &entity )
  {
    BaseType::bind(entity);
    std::get< 0 >( coefficients_ ).bind( this->entity() );
    std::get< 1 >( coefficients_ ).bind( this->entity() );
    std::get< 2 >( coefficients_ ).bind( this->entity() );
    std::get< 3 >( coefficients_ ).bind( this->entity() );
  }

  void unbind ()
  {
    BaseType::unbind();
    std::get< 0 >( coefficients_ ).unbind();
    std::get< 1 >( coefficients_ ).unbind();
    std::get< 2 >( coefficients_ ).unbind();
    std::get< 3 >( coefficients_ ).unbind();
  }

  template< class Point >
  void evaluate ( const Point &x, typename FunctionSpaceType::RangeType &result ) const
  {
    using std::sin;
    typename CoefficientFunctionSpaceType< 3 >::RangeType tmp0 = evaluateCoefficient< 3 >( x );
    typename CoefficientFunctionSpaceType< 2 >::RangeType tmp1 = evaluateCoefficient< 2 >( x );
    const auto tmp2 = 1e-10 + tmp1[ 0 ];
    typename CoefficientFunctionSpaceType< 0 >::RangeType tmp3 = evaluateCoefficient< 0 >( x );
    const auto tmp4 = 3.141592653589793 * tmp3[ 1 ];
    const auto tmp5 = std::sin( tmp4 );
    const auto tmp6 = 3.141592653589793 * tmp3[ 0 ];
    const auto tmp7 = std::sin( tmp6 );
    const auto tmp8 = tmp7 * tmp5;
    const auto tmp9 = -1 * tmp8;
    typename CoefficientFunctionSpaceType< 1 >::RangeType tmp10 = evaluateCoefficient< 1 >( x );
    const auto tmp11 = tmp10[ 0 ] + tmp9;
    const auto tmp12 = tmp1[ 0 ] * tmp11;
    const auto tmp13 = tmp12 / tmp2;
    typename CoefficientFunctionSpaceType< 3 >::JacobianRangeType tmp14 = jacobianCoefficient< 3 >( x );
    const auto tmp15 = (tmp14[ 0 ])[ 1 ] * tmp13;
    const auto tmp16 = tmp15 / tmp0[ 0 ];
    typename CoefficientFunctionSpaceType< 1 >::JacobianRangeType tmp17 = jacobianCoefficient< 1 >( x );
    const auto tmp18 = (tmp17[ 0 ])[ 1 ] + tmp16;
    const auto tmp19 = tmp18 * tmp18;
    const auto tmp20 = (tmp14[ 0 ])[ 0 ] * tmp13;
    const auto tmp21 = tmp20 / tmp0[ 0 ];
    const auto tmp22 = (tmp17[ 0 ])[ 0 ] + tmp21;
    const auto tmp23 = tmp22 * tmp22;
    const auto tmp24 = tmp23 + tmp19;
    result[ 0 ] = tmp24;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::cos;
    using std::sin;
    typename CoefficientFunctionSpaceType< 3 >::RangeType tmp0 = evaluateCoefficient< 3 >( x );
    typename CoefficientFunctionSpaceType< 2 >::RangeType tmp1 = evaluateCoefficient< 2 >( x );
    const auto tmp2 = 1e-10 + tmp1[ 0 ];
    typename CoefficientFunctionSpaceType< 0 >::RangeType tmp3 = evaluateCoefficient< 0 >( x );
    const auto tmp4 = 3.141592653589793 * tmp3[ 1 ];
    const auto tmp5 = std::sin( tmp4 );
    const auto tmp6 = 3.141592653589793 * tmp3[ 0 ];
    const auto tmp7 = std::sin( tmp6 );
    const auto tmp8 = tmp7 * tmp5;
    const auto tmp9 = -1 * tmp8;
    typename CoefficientFunctionSpaceType< 1 >::RangeType tmp10 = evaluateCoefficient< 1 >( x );
    const auto tmp11 = tmp10[ 0 ] + tmp9;
    const auto tmp12 = tmp1[ 0 ] * tmp11;
    const auto tmp13 = tmp12 / tmp2;
    typename CoefficientFunctionSpaceType< 3 >::JacobianRangeType tmp14 = jacobianCoefficient< 3 >( x );
    const auto tmp15 = (tmp14[ 0 ])[ 1 ] * tmp13;
    const auto tmp16 = tmp15 / tmp0[ 0 ];
    typename CoefficientFunctionSpaceType< 1 >::JacobianRangeType tmp17 = jacobianCoefficient< 1 >( x );
    const auto tmp18 = (tmp17[ 0 ])[ 1 ] + tmp16;
    const auto tmp19 = (tmp14[ 0 ])[ 0 ] * tmp16;
    const auto tmp20 = -1 * tmp19;
    typename CoefficientFunctionSpaceType< 3 >::HessianRangeType tmp21 = hessianCoefficient< 3 >( x );
    const auto tmp22 = ((tmp21[ 0 ])[ 1 ])[ 0 ] * tmp13;
    typename CoefficientFunctionSpaceType< 2 >::JacobianRangeType tmp23 = jacobianCoefficient< 2 >( x );
    const auto tmp24 = (tmp23[ 0 ])[ 0 ] * tmp13;
    const auto tmp25 = -1 * tmp24;
    const auto tmp26 = (tmp23[ 0 ])[ 0 ] * tmp11;
    const auto tmp27 = std::cos( tmp6 );
    typename CoefficientFunctionSpaceType< 0 >::JacobianRangeType tmp28 = jacobianCoefficient< 0 >( x );
    const auto tmp29 = 3.141592653589793 * (tmp28[ 0 ])[ 0 ];
    const auto tmp30 = tmp29 * tmp27;
    const auto tmp31 = tmp30 * tmp5;
    const auto tmp32 = std::cos( tmp4 );
    const auto tmp33 = 3.141592653589793 * (tmp28[ 1 ])[ 0 ];
    const auto tmp34 = tmp33 * tmp32;
    const auto tmp35 = tmp34 * tmp7;
    const auto tmp36 = tmp35 + tmp31;
    const auto tmp37 = -1 * tmp36;
    const auto tmp38 = (tmp17[ 0 ])[ 0 ] + tmp37;
    const auto tmp39 = tmp1[ 0 ] * tmp38;
    const auto tmp40 = tmp39 + tmp26;
    const auto tmp41 = tmp40 + tmp25;
    const auto tmp42 = tmp41 / tmp2;
    const auto tmp43 = (tmp14[ 0 ])[ 1 ] * tmp42;
    const auto tmp44 = tmp43 + tmp22;
    const auto tmp45 = tmp44 + tmp20;
    const auto tmp46 = tmp45 / tmp0[ 0 ];
    typename CoefficientFunctionSpaceType< 1 >::HessianRangeType tmp47 = hessianCoefficient< 1 >( x );
    const auto tmp48 = ((tmp47[ 0 ])[ 1 ])[ 0 ] + tmp46;
    const auto tmp49 = tmp48 * tmp18;
    const auto tmp50 = tmp18 * tmp48;
    const auto tmp51 = tmp50 + tmp49;
    const auto tmp52 = (tmp14[ 0 ])[ 0 ] * tmp13;
    const auto tmp53 = tmp52 / tmp0[ 0 ];
    const auto tmp54 = (tmp17[ 0 ])[ 0 ] + tmp53;
    const auto tmp55 = (tmp14[ 0 ])[ 0 ] * tmp53;
    const auto tmp56 = -1 * tmp55;
    const auto tmp57 = ((tmp21[ 0 ])[ 0 ])[ 0 ] * tmp13;
    const auto tmp58 = (tmp14[ 0 ])[ 0 ] * tmp42;
    const auto tmp59 = tmp58 + tmp57;
    const auto tmp60 = tmp59 + tmp56;
    const auto tmp61 = tmp60 / tmp0[ 0 ];
    const auto tmp62 = ((tmp47[ 0 ])[ 0 ])[ 0 ] + tmp61;
    const auto tmp63 = tmp62 * tmp54;
    const auto tmp64 = tmp54 * tmp62;
    const auto tmp65 = tmp64 + tmp63;
    const auto tmp66 = tmp65 + tmp51;
    const auto tmp67 = (tmp14[ 0 ])[ 1 ] * tmp16;
    const auto tmp68 = -1 * tmp67;
    const auto tmp69 = ((tmp21[ 0 ])[ 1 ])[ 1 ] * tmp13;
    const auto tmp70 = (tmp23[ 0 ])[ 1 ] * tmp13;
    const auto tmp71 = -1 * tmp70;
    const auto tmp72 = (tmp23[ 0 ])[ 1 ] * tmp11;
    const auto tmp73 = 3.141592653589793 * (tmp28[ 0 ])[ 1 ];
    const auto tmp74 = tmp73 * tmp27;
    const auto tmp75 = tmp74 * tmp5;
    const auto tmp76 = 3.141592653589793 * (tmp28[ 1 ])[ 1 ];
    const auto tmp77 = tmp76 * tmp32;
    const auto tmp78 = tmp77 * tmp7;
    const auto tmp79 = tmp78 + tmp75;
    const auto tmp80 = -1 * tmp79;
    const auto tmp81 = (tmp17[ 0 ])[ 1 ] + tmp80;
    const auto tmp82 = tmp1[ 0 ] * tmp81;
    const auto tmp83 = tmp82 + tmp72;
    const auto tmp84 = tmp83 + tmp71;
    const auto tmp85 = tmp84 / tmp2;
    const auto tmp86 = (tmp14[ 0 ])[ 1 ] * tmp85;
    const auto tmp87 = tmp86 + tmp69;
    const auto tmp88 = tmp87 + tmp68;
    const auto tmp89 = tmp88 / tmp0[ 0 ];
    const auto tmp90 = ((tmp47[ 0 ])[ 1 ])[ 1 ] + tmp89;
    const auto tmp91 = tmp90 * tmp18;
    const auto tmp92 = tmp18 * tmp90;
    const auto tmp93 = tmp92 + tmp91;
    const auto tmp94 = (tmp14[ 0 ])[ 1 ] * tmp53;
    const auto tmp95 = -1 * tmp94;
    const auto tmp96 = ((tmp21[ 0 ])[ 0 ])[ 1 ] * tmp13;
    const auto tmp97 = (tmp14[ 0 ])[ 0 ] * tmp85;
    const auto tmp98 = tmp97 + tmp96;
    const auto tmp99 = tmp98 + tmp95;
    const auto tmp100 = tmp99 / tmp0[ 0 ];
    const auto tmp101 = ((tmp47[ 0 ])[ 0 ])[ 1 ] + tmp100;
    const auto tmp102 = tmp101 * tmp54;
    const auto tmp103 = tmp54 * tmp101;
    const auto tmp104 = tmp103 + tmp102;
    const auto tmp105 = tmp104 + tmp93;
    (result[ 0 ])[ 0 ] = tmp66;
    (result[ 0 ])[ 1 ] = tmp105;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    DUNE_THROW(Dune::NotImplemented,"hessian method could not be generated for local function (TooHighDerivative('CodeGenerator does not allow for third order derivatives, yet.'))");
    result=typename FunctionSpaceType::HessianRangeType(0);
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

  template< std::size_t i, class Point >
  typename CoefficientFunctionSpaceType< i >::RangeType evaluateCoefficient ( const Point &x ) const
  {
    typename CoefficientFunctionSpaceType< i >::RangeType result;
    std::get< i >( coefficients_ ).evaluate( x, result );;
    return result;
  }

  template< std::size_t i, class Point >
  typename CoefficientFunctionSpaceType< i >::JacobianRangeType jacobianCoefficient ( const Point &x ) const
  {
    typename CoefficientFunctionSpaceType< i >::JacobianRangeType result;
    std::get< i >( coefficients_ ).jacobian( x, result );;
    return result;
  }

  template< std::size_t i, class Point >
  typename CoefficientFunctionSpaceType< i >::HessianRangeType hessianCoefficient ( const Point &x ) const
  {
    typename CoefficientFunctionSpaceType< i >::HessianRangeType result;
    std::get< i >( coefficients_ ).hessian( x, result );;
    return result;
  }
  ConstantTupleType constants_;
  std::tuple< Dune::Fem::ConstLocalFunction< Coeffbndproj >, Dune::Fem::ConstLocalFunction< Coeffddm >, Dune::Fem::ConstLocalFunction< Coeffsdfprojfull >, Dune::Fem::ConstLocalFunction< Coeffphidomain > > coefficients_;
};

} // namespace UFLLocalFunctions_f4583c5cc10d24a8bdedf7510ce9da7b

PYBIND11_MODULE( localfunction_f4583c5cc10d24a8bdedf7510ce9da7b_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_f4583c5cc10d24a8bdedf7510ce9da7b::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_f4583c5cc10d24a8bdedf7510ce9da7b::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_f4583c5cc10d24a8bdedf7510ce9da7b_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > &coeffbndproj, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > &coeffddm, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > &coeffsdfprojfull, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > &coeffphidomain ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order, coeffbndproj, coeffddm, coeffsdfprojfull, coeffphidomain); } ), pybind11::keep_alive< 1, 2 >(), pybind11::keep_alive< 1, 3 >(), pybind11::keep_alive< 1, 4 >(), pybind11::keep_alive< 1, 5 >(), pybind11::keep_alive< 1, 6 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
