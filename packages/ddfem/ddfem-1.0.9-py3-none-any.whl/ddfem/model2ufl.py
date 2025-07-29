from ufl import (
    FacetNormal,
    SpatialCoordinate,
    TestFunction,
    TrialFunction,
    as_vector,
    ds,
    dx,
    grad,
    inner,
)

from .boundary import boundary_validation


def boundaries_ufl(Model, space, t):
    boundary_flux_cs, boundary_flux_vs, boundary_values = boundary_validation(Model)

    u = TrialFunction(space)
    n = FacetNormal(space.cell())
    x = SpatialCoordinate(space.cell())

    boundary_flux_cs = {
        (k(x) if callable(k) else k): f(t, x, u, n) for k, f in boundary_flux_cs.items()
    }
    boundary_flux_vs = {
        (k(x) if callable(k) else k): f(t, x, u, grad(u), n)
        for k, f in boundary_flux_vs.items()
    }
    boundary_values = {
        (k(x) if callable(k) else k): f(t, x, u) for k, f in boundary_values.items()
    }
    hasBoundaryValue = {k: True for k in boundary_values.keys()}

    return (
        boundary_flux_cs,
        boundary_flux_vs,
        boundary_values,
        hasBoundaryValue,
    )


class DirichletBC:
    def __init__(self, space, value, domain=None):
        self.space = space
        self.value = value
        self.domain = domain

    def __str__(self):
        return str(self.value) + str(self.domain)


def model_ufl(Model, space, initialTime=0, DirichletBC=DirichletBC):
    u = TrialFunction(space)
    v = TestFunction(space)
    x = SpatialCoordinate(space.cell())

    t = initialTime

    f_c_model = None
    if hasattr(Model, "F_c"):
        f_c_model = inner(Model.F_c(t, x, u), grad(v)) # -div F_c v
    if hasattr(Model, "S_e"):
        # there is an issue with S_e returning 'zero' and zero*dx leading to UFL error
        se = (
            inner(as_vector(Model.S_e(t, x, u, grad(u))), v)
        )  # (-div F_c + S_e) * v
        if f_c_model is not None:
            f_c_model += se
        else:
            f_c_model = se

    f_v_model = None
    if hasattr(Model, "F_v"):
        f_v_model = inner(Model.F_v(t, x, u, grad(u)), grad(v)) # -div F_v v

    if hasattr(Model, "S_i"):
        si = inner(as_vector(Model.S_i(t, x, u, grad(u))), v) # (-div F_v + S_i) v
        if f_v_model is not None:
            f_v_model += si
        else:
            f_v_model = si

    # need to extract boundary information from Model
    (
        boundary_flux_cs,
        boundary_flux_vs,
        boundary_values,
        hasBoundaryValue,
    ) = boundaries_ufl(Model, space, t)

    dirichletBCs = [
        DirichletBC(space, item[1], item[0]) for item in boundary_values.items()
    ]
    boundary_flux_vs = -sum(
        [inner(item[1], v) * ds(item[0]) for item in boundary_flux_vs.items()]
    )  # keep all forms on left hand side
    boundary_flux_cs = -sum(
        [inner(item[1], v) * ds(item[0]) for item in boundary_flux_cs.items()]
    )  # keep all forms on left hand side

    if f_c_model:
        f_c_model = f_c_model * dx
    if f_v_model:
        f_v_model = f_v_model * dx
    # !!! fix issue with f_?_model==zero not being a form
    return (
        f_c_model,
        f_v_model,
        {
            "dirichletBCs": dirichletBCs,
            "boundary_flux_cs": boundary_flux_cs,
            "boundary_flux_vs": boundary_flux_vs,
            "hasBoundaryValue": hasBoundaryValue,
        },
    )


def model2ufl(
    Model, space, initialTime=0, DirichletBC=DirichletBC, *, returnFull=False
):
    class M(Model):
        if hasattr(Model, "S_e"):

            def S_e(t, x, U, DU):
                return -Model.S_e(t, x, U, DU)

        if hasattr(Model, "S_i"):

            def S_i(t, x, U, DU):
                return -Model.S_i(t, x, U, DU)

        if hasattr(Model, "F_c"):

            def F_c(t, x, U):
                return -Model.F_c(t, x, U)

    f_c_model, f_v_model, boundary_model = model_ufl(M, space, initialTime, DirichletBC)
    boundary_model["boundary_flux_cs"] = -boundary_model["boundary_flux_cs"]
    form = boundary_model["boundary_flux_cs"] + boundary_model["boundary_flux_vs"]
    if f_c_model is not None:
        form += f_c_model
    if f_v_model is not None:
        form += f_v_model

    if not returnFull:
        return [form == 0, *boundary_model["dirichletBCs"]]
    else:
        boundary_model["f_c_model"] = f_c_model
        boundary_model["f_v_model"] = f_v_model
        boundary_model["form"] = form
        return boundary_model
