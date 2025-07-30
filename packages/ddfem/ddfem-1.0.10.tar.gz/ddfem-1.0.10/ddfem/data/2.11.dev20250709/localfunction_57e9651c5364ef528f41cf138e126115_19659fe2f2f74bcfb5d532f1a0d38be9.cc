#ifndef GUARD_57e9651c5364ef528f41cf138e126115
#define GUARD_57e9651c5364ef528f41cf138e126115

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

namespace UFLLocalFunctions_57e9651c5364ef528f41cf138e126115
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
    const auto tmp1 = 0.8090169943749475 * tmp0[ 1 ];
    const auto tmp2 = -0.5877852522924731 * tmp0[ 0 ];
    const auto tmp3 = tmp2 + tmp1;
    const auto tmp4 = -0.3 + tmp3;
    const auto tmp5 = std::abs( tmp4 );
    const auto tmp6 = -0.3 + tmp5;
    const auto tmp7 = 0.5877852522924731 * tmp0[ 1 ];
    const auto tmp8 = 0.8090169943749475 * tmp0[ 0 ];
    const auto tmp9 = tmp8 + tmp7;
    const auto tmp10 = -0.1 + tmp9;
    const auto tmp11 = std::abs( tmp10 );
    const auto tmp12 = -0.8 + tmp11;
    const auto tmp13 = std::max( tmp12, tmp6 );
    const auto tmp14 = std::max( tmp6, 0.0 );
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = std::max( tmp12, 0.0 );
    const auto tmp17 = tmp16 * tmp16;
    const auto tmp18 = tmp17 + tmp15;
    const auto tmp19 = 1e-10 + tmp18;
    const auto tmp20 = std::sqrt( tmp19 );
    result[ 0 ] = (tmp13 > 0.0 ? tmp20 : tmp13);
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::abs;
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = 0.8090169943749475 * tmp0[ 1 ];
    const auto tmp2 = -0.5877852522924731 * tmp0[ 0 ];
    const auto tmp3 = tmp2 + tmp1;
    const auto tmp4 = -0.3 + tmp3;
    const auto tmp5 = std::abs( tmp4 );
    const auto tmp6 = -0.3 + tmp5;
    const auto tmp7 = 0.5877852522924731 * tmp0[ 1 ];
    const auto tmp8 = 0.8090169943749475 * tmp0[ 0 ];
    const auto tmp9 = tmp8 + tmp7;
    const auto tmp10 = -0.1 + tmp9;
    const auto tmp11 = std::abs( tmp10 );
    const auto tmp12 = -0.8 + tmp11;
    const auto tmp13 = 0.8090169943749475 * (tmp10 == 0.0 ? 0.0 : (tmp10 < 0.0 ? -1 : 1));
    const auto tmp14 = tmp13 * (tmp12 > tmp6 ? 1 : 0.0);
    const auto tmp15 = -0.5877852522924731 * (tmp4 == 0.0 ? 0.0 : (tmp4 < 0.0 ? -1 : 1));
    const auto tmp16 = -1 * (tmp12 > tmp6 ? 1 : 0.0);
    const auto tmp17 = 1.0 + tmp16;
    const auto tmp18 = tmp17 * tmp15;
    const auto tmp19 = tmp18 + tmp14;
    const auto tmp20 = std::max( tmp6, 0.0 );
    const auto tmp21 = tmp20 * tmp20;
    const auto tmp22 = std::max( tmp12, 0.0 );
    const auto tmp23 = tmp22 * tmp22;
    const auto tmp24 = tmp23 + tmp21;
    const auto tmp25 = 1e-10 + tmp24;
    const auto tmp26 = std::sqrt( tmp25 );
    const auto tmp27 = 2 * tmp26;
    const auto tmp28 = tmp15 * (tmp6 > 0.0 ? 1 : 0.0);
    const auto tmp29 = tmp28 * tmp20;
    const auto tmp30 = tmp29 + tmp29;
    const auto tmp31 = tmp13 * (tmp12 > 0.0 ? 1 : 0.0);
    const auto tmp32 = tmp31 * tmp22;
    const auto tmp33 = tmp32 + tmp32;
    const auto tmp34 = tmp33 + tmp30;
    const auto tmp35 = tmp34 / tmp27;
    const auto tmp36 = std::max( tmp12, tmp6 );
    const auto tmp37 = 0.5877852522924731 * (tmp10 == 0.0 ? 0.0 : (tmp10 < 0.0 ? -1 : 1));
    const auto tmp38 = tmp37 * (tmp12 > tmp6 ? 1 : 0.0);
    const auto tmp39 = 0.8090169943749475 * (tmp4 == 0.0 ? 0.0 : (tmp4 < 0.0 ? -1 : 1));
    const auto tmp40 = tmp17 * tmp39;
    const auto tmp41 = tmp40 + tmp38;
    const auto tmp42 = tmp39 * (tmp6 > 0.0 ? 1 : 0.0);
    const auto tmp43 = tmp42 * tmp20;
    const auto tmp44 = tmp43 + tmp43;
    const auto tmp45 = tmp37 * (tmp12 > 0.0 ? 1 : 0.0);
    const auto tmp46 = tmp45 * tmp22;
    const auto tmp47 = tmp46 + tmp46;
    const auto tmp48 = tmp47 + tmp44;
    const auto tmp49 = tmp48 / tmp27;
    (result[ 0 ])[ 0 ] = (tmp36 > 0.0 ? tmp35 : tmp19);
    (result[ 0 ])[ 1 ] = (tmp36 > 0.0 ? tmp49 : tmp41);
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::abs;
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = 0.8090169943749475 * tmp0[ 1 ];
    const auto tmp2 = -0.5877852522924731 * tmp0[ 0 ];
    const auto tmp3 = tmp2 + tmp1;
    const auto tmp4 = -0.3 + tmp3;
    const auto tmp5 = std::abs( tmp4 );
    const auto tmp6 = -0.3 + tmp5;
    const auto tmp7 = std::max( tmp6, 0.0 );
    const auto tmp8 = tmp7 * tmp7;
    const auto tmp9 = 0.5877852522924731 * tmp0[ 1 ];
    const auto tmp10 = 0.8090169943749475 * tmp0[ 0 ];
    const auto tmp11 = tmp10 + tmp9;
    const auto tmp12 = -0.1 + tmp11;
    const auto tmp13 = std::abs( tmp12 );
    const auto tmp14 = -0.8 + tmp13;
    const auto tmp15 = std::max( tmp14, 0.0 );
    const auto tmp16 = tmp15 * tmp15;
    const auto tmp17 = tmp16 + tmp8;
    const auto tmp18 = 1e-10 + tmp17;
    const auto tmp19 = std::sqrt( tmp18 );
    const auto tmp20 = 2 * tmp19;
    const auto tmp21 = -0.5877852522924731 * (tmp4 == 0.0 ? 0.0 : (tmp4 < 0.0 ? -1 : 1));
    const auto tmp22 = tmp21 * (tmp6 > 0.0 ? 1 : 0.0);
    const auto tmp23 = tmp22 * tmp7;
    const auto tmp24 = tmp23 + tmp23;
    const auto tmp25 = 0.8090169943749475 * (tmp12 == 0.0 ? 0.0 : (tmp12 < 0.0 ? -1 : 1));
    const auto tmp26 = tmp25 * (tmp14 > 0.0 ? 1 : 0.0);
    const auto tmp27 = tmp26 * tmp15;
    const auto tmp28 = tmp27 + tmp27;
    const auto tmp29 = tmp28 + tmp24;
    const auto tmp30 = tmp29 / tmp20;
    const auto tmp31 = 2 * tmp30;
    const auto tmp32 = tmp31 * tmp30;
    const auto tmp33 = -1 * tmp32;
    const auto tmp34 = tmp22 * tmp22;
    const auto tmp35 = tmp34 + tmp34;
    const auto tmp36 = tmp26 * tmp26;
    const auto tmp37 = tmp36 + tmp36;
    const auto tmp38 = tmp37 + tmp35;
    const auto tmp39 = tmp38 + tmp33;
    const auto tmp40 = tmp39 / tmp20;
    const auto tmp41 = std::max( tmp14, tmp6 );
    const auto tmp42 = 0.8090169943749475 * (tmp4 == 0.0 ? 0.0 : (tmp4 < 0.0 ? -1 : 1));
    const auto tmp43 = tmp42 * (tmp6 > 0.0 ? 1 : 0.0);
    const auto tmp44 = tmp43 * tmp7;
    const auto tmp45 = tmp44 + tmp44;
    const auto tmp46 = 0.5877852522924731 * (tmp12 == 0.0 ? 0.0 : (tmp12 < 0.0 ? -1 : 1));
    const auto tmp47 = tmp46 * (tmp14 > 0.0 ? 1 : 0.0);
    const auto tmp48 = tmp47 * tmp15;
    const auto tmp49 = tmp48 + tmp48;
    const auto tmp50 = tmp49 + tmp45;
    const auto tmp51 = tmp50 / tmp20;
    const auto tmp52 = 2 * tmp51;
    const auto tmp53 = tmp52 * tmp30;
    const auto tmp54 = -1 * tmp53;
    const auto tmp55 = tmp22 * tmp43;
    const auto tmp56 = tmp55 + tmp55;
    const auto tmp57 = tmp47 * tmp26;
    const auto tmp58 = tmp57 + tmp57;
    const auto tmp59 = tmp58 + tmp56;
    const auto tmp60 = tmp59 + tmp54;
    const auto tmp61 = tmp60 / tmp20;
    const auto tmp62 = tmp31 * tmp51;
    const auto tmp63 = -1 * tmp62;
    const auto tmp64 = tmp59 + tmp63;
    const auto tmp65 = tmp64 / tmp20;
    const auto tmp66 = tmp52 * tmp51;
    const auto tmp67 = -1 * tmp66;
    const auto tmp68 = tmp43 * tmp43;
    const auto tmp69 = tmp68 + tmp68;
    const auto tmp70 = tmp47 * tmp47;
    const auto tmp71 = tmp70 + tmp70;
    const auto tmp72 = tmp71 + tmp69;
    const auto tmp73 = tmp72 + tmp67;
    const auto tmp74 = tmp73 / tmp20;
    ((result[ 0 ])[ 0 ])[ 0 ] = (tmp41 > 0.0 ? tmp40 : 0.0);
    ((result[ 0 ])[ 0 ])[ 1 ] = (tmp41 > 0.0 ? tmp61 : 0.0);
    ((result[ 0 ])[ 1 ])[ 0 ] = (tmp41 > 0.0 ? tmp65 : 0.0);
    ((result[ 0 ])[ 1 ])[ 1 ] = (tmp41 > 0.0 ? tmp74 : 0.0);
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

} // namespace UFLLocalFunctions_57e9651c5364ef528f41cf138e126115

PYBIND11_MODULE( localfunction_57e9651c5364ef528f41cf138e126115_19659fe2f2f74bcfb5d532f1a0d38be9, module )
{
  typedef UFLLocalFunctions_57e9651c5364ef528f41cf138e126115::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_57e9651c5364ef528f41cf138e126115::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_57e9651c5364ef528f41cf138e126115_19659fe2f2f74bcfb5d532f1a0d38be9.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::YaspGrid< 2, Dune::EquidistantOffsetCoordinates< double, 2 > >::LeafGridView>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
