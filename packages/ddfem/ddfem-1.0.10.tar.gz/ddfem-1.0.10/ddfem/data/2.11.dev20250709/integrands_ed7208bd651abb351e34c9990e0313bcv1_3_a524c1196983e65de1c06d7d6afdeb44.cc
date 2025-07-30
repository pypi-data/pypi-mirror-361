#ifndef GuardIntegrands_ed7208bd651abb351e34c9990e0313bcv1_3
#define GuardIntegrands_ed7208bd651abb351e34c9990e0313bcv1_3
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
#include <cmath>
#include <tuple>
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/extensions.h>
#include <dune/fempy/py/grid/gridpart.hh>
#include <dune/fempy/geometry/edgelength.hh>
#include <dune/fempy/py/integrands.hh>

namespace Integrands_ed7208bd651abb351e34c9990e0313bcv1_3
{




  // Integrands
  // ----------

  template< class GridPart >
  struct Integrands
  {
    typedef GridPart GridPartType;
    typedef typename GridPartType::GridViewType GridView;
    typedef typename GridView::ctype ctype;
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

    Integrands ( const Dune::Fem::ParameterReader &parameter = Dune::Fem::Parameter::container() )
    {}

    bool init ( const EntityType &entity )
    {
      entity_ = entity;
      geometry_.emplace( this->entity().geometry() );
      return true;
    }

    void unbind ()
    {}

    bool init ( const IntersectionType &intersection )
    {
      intersection_ = intersection;
      return (intersection.boundary() && init( intersection.inside() ));
    }
    typedef std::tuple< Dune::FieldVector< double, 1 >, Dune::FieldMatrix< double, 1, 2 > > DomainValueType;
    typedef std::tuple< Dune::FieldVector< double, 1 >, Dune::FieldMatrix< double, 1, 2 > > RangeValueType;
    static constexpr bool _nonlinear = false;

    bool nonlinear () const
    {
      return _nonlinear;
    }

    template< class Point >
    RangeValueType interior ( const Point &x, const DomainValueType &u ) const
    {
      using std::cosh;
      using std::pow;
      using std::sqrt;
      using std::tanh;
      GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
      const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
      const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
      const auto tmp3 = tmp2 + tmp1;
      const auto tmp4 = 1e-10 + tmp3;
      const auto tmp5 = std::sqrt( tmp4 );
      const auto tmp6 = 2 * tmp5;
      const auto tmp7 = tmp0[ 1 ] + tmp0[ 1 ];
      const auto tmp8 = tmp7 / tmp6;
      const auto tmp9 = -1 * tmp8;
      const auto tmp10 = -1 + tmp5;
      const auto tmp11 = tmp10 * tmp9;
      const auto tmp12 = tmp0[ 1 ] + tmp11;
      const auto tmp13 = tmp12 * tmp12;
      const auto tmp14 = tmp0[ 0 ] + tmp0[ 0 ];
      const auto tmp15 = tmp14 / tmp6;
      const auto tmp16 = -1 * tmp15;
      const auto tmp17 = tmp10 * tmp16;
      const auto tmp18 = tmp0[ 0 ] + tmp17;
      const auto tmp19 = tmp18 * tmp18;
      const auto tmp20 = tmp19 + tmp13;
      const auto tmp21 = 1e-10 + tmp20;
      const auto tmp22 = std::sqrt( tmp21 );
      const auto tmp23 = -1 + tmp22;
      const auto tmp24 = 3 * tmp23;
      const auto tmp25 = tmp24 / 0.225;
      const auto tmp26 = std::tanh( tmp25 );
      const auto tmp27 = -1 * tmp26;
      const auto tmp28 = 1 + tmp27;
      const auto tmp29 = 0.5 * tmp28;
      const auto tmp30 = -1 * tmp29;
      const auto tmp31 = 1 + tmp30;
      const auto tmp32 = tmp31 * tmp29;
      const auto tmp33 = 1e-10 + tmp32;
      const auto tmp34 = 3 * tmp10;
      const auto tmp35 = tmp34 / 0.225;
      const auto tmp36 = 2.0 * tmp35;
      const auto tmp37 = std::cosh( tmp36 );
      const auto tmp38 = 1.0 + tmp37;
      const auto tmp39 = std::cosh( tmp35 );
      const auto tmp40 = 2.0 * tmp39;
      const auto tmp41 = tmp40 / tmp38;
      const auto tmp42 = std::pow( tmp41, 2 );
      const auto tmp43 = 3 * tmp8;
      const auto tmp44 = tmp43 / 0.225;
      const auto tmp45 = tmp44 * tmp42;
      const auto tmp46 = -1 * tmp45;
      const auto tmp47 = 0.5 * tmp46;
      const auto tmp48 = 0.9999999999 * tmp47;
      const auto tmp49 = -1 * tmp48;
      const auto tmp50 = tmp49 * tmp49;
      const auto tmp51 = 3 * tmp15;
      const auto tmp52 = tmp51 / 0.225;
      const auto tmp53 = tmp52 * tmp42;
      const auto tmp54 = -1 * tmp53;
      const auto tmp55 = 0.5 * tmp54;
      const auto tmp56 = 0.9999999999 * tmp55;
      const auto tmp57 = -1 * tmp56;
      const auto tmp58 = tmp57 * tmp57;
      const auto tmp59 = tmp58 + tmp50;
      const auto tmp60 = std::sqrt( tmp59 );
      const auto tmp61 = 10 * tmp18;
      const auto tmp62 = tmp12 * tmp61;
      const auto tmp63 = std::tanh( tmp62 );
      const auto tmp64 = tmp63 / 2;
      const auto tmp65 = -1 * tmp64;
      const auto tmp66 = tmp32 * tmp65;
      const auto tmp67 = tmp66 * tmp60;
      const auto tmp68 = -1 * tmp67;
      const auto tmp69 = tmp68 / tmp33;
      const auto tmp70 = -1 * tmp69;
      const auto tmp71 = -1 * tmp70;
      const auto tmp72 = tmp64 * tmp60;
      const auto tmp73 = -1 * tmp72;
      const auto tmp74 = tmp32 * tmp73;
      const auto tmp75 = tmp74 / tmp33;
      const auto tmp76 = -1 * tmp75;
      const auto tmp77 = std::tanh( tmp35 );
      const auto tmp78 = -1 * tmp77;
      const auto tmp79 = 1 + tmp78;
      const auto tmp80 = 0.5 * tmp79;
      const auto tmp81 = 0.9999999999 * tmp80;
      const auto tmp82 = 1e-10 + tmp81;
      const auto tmp83 = std::get< 0 >( u );
      const auto tmp84 = 0.01 * tmp83[ 0 ];
      const auto tmp85 = -1 * tmp84;
      const auto tmp86 = -1 * (tmp10 <= 0.0 ? 1 : 0.0);
      const auto tmp87 = 1 + tmp86;
      const auto tmp88 = tmp87 * tmp11;
      const auto tmp89 = tmp0[ 1 ] + tmp88;
      const auto tmp90 = tmp89 * tmp89;
      const auto tmp91 = tmp87 * tmp17;
      const auto tmp92 = tmp0[ 0 ] + tmp91;
      const auto tmp93 = tmp92 * tmp92;
      const auto tmp94 = tmp93 + tmp90;
      const auto tmp95 = -1 * tmp94;
      const auto tmp96 = 1 + tmp95;
      const auto tmp97 = 0.1 * tmp96;
      const auto tmp98 = tmp97 + tmp85;
      const auto tmp99 = tmp98 * tmp82;
      const auto tmp100 = tmp99 + tmp76;
      const auto tmp101 = -1 * tmp100;
      const auto tmp102 = tmp101 + tmp71;
      const auto tmp103 = 3 * tmp89;
      const auto tmp104 = tmp83[ 0 ] * tmp103;
      const auto tmp105 = tmp82 * tmp104;
      const auto tmp106 = -1 * tmp105;
      const auto tmp107 = 0.05 * tmp94;
      const auto tmp108 = -1 * tmp107;
      const auto tmp109 = 0.1 + tmp108;
      const auto tmp110 = std::get< 1 >( u );
      const auto tmp111 = (tmp110[ 0 ])[ 0 ] * tmp109;
      const auto tmp112 = tmp82 * tmp111;
      const auto tmp113 = tmp112 + tmp106;
      const auto tmp114 = -1 * tmp92;
      const auto tmp115 = 3 * tmp114;
      const auto tmp116 = tmp83[ 0 ] * tmp115;
      const auto tmp117 = tmp82 * tmp116;
      const auto tmp118 = -1 * tmp117;
      const auto tmp119 = (tmp110[ 0 ])[ 1 ] * tmp109;
      const auto tmp120 = tmp82 * tmp119;
      const auto tmp121 = tmp120 + tmp118;
      return RangeValueType{ { tmp102 }, { { tmp113, tmp121 } } };
    }

    template< class Point >
    auto linearizedInterior ( const Point &x, const DomainValueType &u ) const
    {
      using std::sqrt;
      using std::tanh;
      GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
      const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
      const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
      const auto tmp3 = tmp2 + tmp1;
      const auto tmp4 = 1e-10 + tmp3;
      const auto tmp5 = std::sqrt( tmp4 );
      const auto tmp6 = -1 + tmp5;
      const auto tmp7 = 3 * tmp6;
      const auto tmp8 = tmp7 / 0.225;
      const auto tmp9 = std::tanh( tmp8 );
      const auto tmp10 = -1 * tmp9;
      const auto tmp11 = 1 + tmp10;
      const auto tmp12 = 0.5 * tmp11;
      const auto tmp13 = 0.9999999999 * tmp12;
      const auto tmp14 = 1e-10 + tmp13;
      const auto tmp15 = -0.01 * tmp14;
      const auto tmp16 = -1 * tmp15;
      const auto tmp17 = 2 * tmp5;
      const auto tmp18 = tmp0[ 1 ] + tmp0[ 1 ];
      const auto tmp19 = tmp18 / tmp17;
      const auto tmp20 = -1 * tmp19;
      const auto tmp21 = tmp6 * tmp20;
      const auto tmp22 = -1 * (tmp6 <= 0.0 ? 1 : 0.0);
      const auto tmp23 = 1 + tmp22;
      const auto tmp24 = tmp23 * tmp21;
      const auto tmp25 = tmp0[ 1 ] + tmp24;
      const auto tmp26 = 3 * tmp25;
      const auto tmp27 = tmp14 * tmp26;
      const auto tmp28 = -1 * tmp27;
      const auto tmp29 = tmp0[ 0 ] + tmp0[ 0 ];
      const auto tmp30 = tmp29 / tmp17;
      const auto tmp31 = -1 * tmp30;
      const auto tmp32 = tmp6 * tmp31;
      const auto tmp33 = tmp23 * tmp32;
      const auto tmp34 = tmp0[ 0 ] + tmp33;
      const auto tmp35 = -1 * tmp34;
      const auto tmp36 = 3 * tmp35;
      const auto tmp37 = tmp14 * tmp36;
      const auto tmp38 = -1 * tmp37;
      const auto tmp39 = tmp25 * tmp25;
      const auto tmp40 = tmp34 * tmp34;
      const auto tmp41 = tmp40 + tmp39;
      const auto tmp42 = 0.05 * tmp41;
      const auto tmp43 = -1 * tmp42;
      const auto tmp44 = 0.1 + tmp43;
      const auto tmp45 = tmp44 * tmp14;
      return [ tmp16, tmp28, tmp38, tmp45 ] ( const DomainValueType &phi ) {
          return RangeValueType{ { tmp16 * (std::get< 0 >( phi ))[ 0 ] }, { { tmp28 * (std::get< 0 >( phi ))[ 0 ] + tmp45 * ((std::get< 1 >( phi ))[ 0 ])[ 0 ], tmp38 * (std::get< 0 >( phi ))[ 0 ] + tmp45 * ((std::get< 1 >( phi ))[ 0 ])[ 1 ] } } };
        };
    }

    template< class Point >
    RangeValueType boundary ( const Point &x, const DomainValueType &u ) const
    {
      using std::cosh;
      using std::pow;
      using std::sqrt;
      using std::tanh;
      GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
      const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
      const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
      const auto tmp3 = tmp2 + tmp1;
      const auto tmp4 = 1e-10 + tmp3;
      const auto tmp5 = std::sqrt( tmp4 );
      const auto tmp6 = 2 * tmp5;
      const auto tmp7 = tmp0[ 1 ] + tmp0[ 1 ];
      const auto tmp8 = tmp7 / tmp6;
      const auto tmp9 = -1 * tmp8;
      const auto tmp10 = -1 + tmp5;
      const auto tmp11 = tmp10 * tmp9;
      const auto tmp12 = tmp0[ 1 ] + tmp11;
      const auto tmp13 = tmp12 * tmp12;
      const auto tmp14 = tmp0[ 0 ] + tmp0[ 0 ];
      const auto tmp15 = tmp14 / tmp6;
      const auto tmp16 = -1 * tmp15;
      const auto tmp17 = tmp10 * tmp16;
      const auto tmp18 = tmp0[ 0 ] + tmp17;
      const auto tmp19 = tmp18 * tmp18;
      const auto tmp20 = tmp19 + tmp13;
      const auto tmp21 = 1e-10 + tmp20;
      const auto tmp22 = std::sqrt( tmp21 );
      const auto tmp23 = -1 + tmp22;
      const auto tmp24 = 3 * tmp23;
      const auto tmp25 = tmp24 / 0.225;
      const auto tmp26 = std::tanh( tmp25 );
      const auto tmp27 = -1 * tmp26;
      const auto tmp28 = 1 + tmp27;
      const auto tmp29 = 0.5 * tmp28;
      const auto tmp30 = -1 * tmp29;
      const auto tmp31 = 1 + tmp30;
      const auto tmp32 = tmp31 * tmp29;
      const auto tmp33 = 1e-10 + tmp32;
      const auto tmp34 = 3 * tmp10;
      const auto tmp35 = tmp34 / 0.225;
      const auto tmp36 = 2.0 * tmp35;
      const auto tmp37 = std::cosh( tmp36 );
      const auto tmp38 = 1.0 + tmp37;
      const auto tmp39 = std::cosh( tmp35 );
      const auto tmp40 = 2.0 * tmp39;
      const auto tmp41 = tmp40 / tmp38;
      const auto tmp42 = std::pow( tmp41, 2 );
      const auto tmp43 = 3 * tmp8;
      const auto tmp44 = tmp43 / 0.225;
      const auto tmp45 = tmp44 * tmp42;
      const auto tmp46 = -1 * tmp45;
      const auto tmp47 = 0.5 * tmp46;
      const auto tmp48 = 0.9999999999 * tmp47;
      const auto tmp49 = -1 * tmp48;
      const auto tmp50 = tmp49 * tmp49;
      const auto tmp51 = 3 * tmp15;
      const auto tmp52 = tmp51 / 0.225;
      const auto tmp53 = tmp52 * tmp42;
      const auto tmp54 = -1 * tmp53;
      const auto tmp55 = 0.5 * tmp54;
      const auto tmp56 = 0.9999999999 * tmp55;
      const auto tmp57 = -1 * tmp56;
      const auto tmp58 = tmp57 * tmp57;
      const auto tmp59 = tmp58 + tmp50;
      const auto tmp60 = std::sqrt( tmp59 );
      const auto tmp61 = 10 * tmp18;
      const auto tmp62 = tmp12 * tmp61;
      const auto tmp63 = std::tanh( tmp62 );
      const auto tmp64 = tmp63 / 2;
      const auto tmp65 = tmp64 * tmp60;
      const auto tmp66 = -1 * tmp65;
      const auto tmp67 = tmp32 * tmp66;
      const auto tmp68 = tmp67 / tmp33;
      const auto tmp69 = -1 * tmp68;
      const auto tmp70 = -1 * tmp69;
      const auto tmp71 = -1 * tmp64;
      const auto tmp72 = tmp32 * tmp71;
      const auto tmp73 = tmp72 * tmp60;
      const auto tmp74 = -1 * tmp73;
      const auto tmp75 = tmp74 / tmp33;
      const auto tmp76 = -1 * tmp75;
      const auto tmp77 = -1 * tmp76;
      const auto tmp78 = -1 * tmp77;
      const auto tmp79 = tmp78 + tmp70;
      return RangeValueType{ { tmp79 }, { { 0, 0 } } };
    }

    template< class Point >
    auto linearizedBoundary ( const Point &x, const DomainValueType &u ) const
    {
      return [] ( const DomainValueType &phi ) {
          return RangeValueType{ { 0 }, { { 0, 0 } } };
        };
    }
    typedef Dune::FieldVector< double, 1 >  RRangeType;
    typedef Dune::FieldMatrix< double, 1, GridPartType::dimension >  RJacobianRangeType;
    typedef Dune::Fem::BoundaryIdProvider< typename GridPartType::GridType > BoundaryIdProviderType;
    typedef std::array<int,1> DirichletComponentType;

    bool hasDirichletBoundary () const
    {
      return false;
    }

    bool isDirichletIntersection ( const IntersectionType &intersection, DirichletComponentType &dirichletComponent ) const
    {
      return false;
    }

    template< class Point >
    void dirichlet ( int bndId, const Point &x, RRangeType &result ) const
    {}

    template< class Point >
    void dDirichlet ( int bndId, const Point &x, RJacobianRangeType &result ) const
    {}

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

    const EntityType &entity () const
    {
      return entity_;
    }

    const Geometry &geometry () const
    {
      return *geometry_;
    }
    EntityType entity_;
    IntersectionType intersection_;
    std::optional< Geometry > geometry_;
    ConstantTupleType constants_;
    std::tuple<  > coefficients_;
  };

} // namespace Integrands_ed7208bd651abb351e34c9990e0313bcv1_3

PYBIND11_MODULE( integrands_ed7208bd651abb351e34c9990e0313bcv1_3_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > GridPart;
  typedef Integrands_ed7208bd651abb351e34c9990e0313bcv1_3::Integrands< GridPart > Integrands;
  if constexpr( Integrands::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<Integrands>(module,"Integrands",Dune::Python::GenerateTypeName("Integrands_ed7208bd651abb351e34c9990e0313bcv1_3::Integrands< GridPart >"), Dune::Python::IncludeFiles({"python/dune/generated/integrands_ed7208bd651abb351e34c9990e0313bcv1_3_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerIntegrands< Integrands >( module, cls );
      cls.def( pybind11::init( [] () { return new Integrands(); } ) );
      cls.def_property_readonly( "virtualized", [] ( Integrands& ) -> bool { return true;});
      cls.def_property_readonly( "hasDirichletBoundary", [] ( Integrands& ) -> bool { return false;});
  }
}
#endif // GuardIntegrands_ed7208bd651abb351e34c9990e0313bcv1_3
