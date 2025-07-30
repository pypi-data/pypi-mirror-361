# Diffuse Domain Finite Element Methods

This is a Python package that implements a framework for transforming PDEs defined on
a complex domains using the Diffuse Domain Method to reformulate the problem on a simple domain.
This method avoids traditional challenges by embedding the original geometry with a phase-field function representation.

Our aim is to make the application of a variety of Diffuse Domain approaches more accessible and straightforward to use. We have designed the package to have a wide compatibility with existing finite element solvers, as all transformations are performed only using the Unified Form Language,
[UFL][2].

Furthermore, we provide a new approach to combine multiple boundary conditions of different types on distinct boundary segments.

The `geometry` subpackage provides several simple signed distance functions (SDF),
and operators to allow an easy definition of the complex domain. The `transfromers` subpackes implements a number of different diffuse domain approaches including some novel ones which we
will describe in detail in an upcoming paper.

While not required, we recommend using [Dune-Fem][1] as it enables some optimisations for form compiling and has been used for testing the package and for the examples throughout
our [Documentation][0].

## Getting started

Using `pip` and a virtual environment is the easiest way to get started with`ddfem`:

```bash
pip install ddfem
```

will install the basic package. We have mainly tested it with `dune` as solver backend and provide some extra features when used with `dune`. Currently the code relies on a pre-release version and the best way to guarantee compatibility is to use

```bash
pip install ddfem[dune]
```

On most machine you will also need to run

```bash
pip install mpi4py
```

The main example `intro` file in our tutorial can be obtained easily by running

```
python -m ddfem
```

This step can take some time (so do it before a coffee break) since it precompiles all required modules. This is done in parallel using `4` processes by default. Change that by adding a parameter to the above call, e.g., to use `8` processes run

```
python -m ddfem 8
```

After this step has completed you should find the two files `intro.py` and `intro_nb.ipynb` in your folder.

Enjoy - and let use know of any [issues][3] you encountered 




[0]: https://ddfem.readthedocs.io/en/latest/index.html
[1]: https://www.dune-project.org/modules/dune-fem/
[2]: https://github.com/FEniCS/ufl
[3]: https://gitlab.dune-project.org/dune-fem/ddfem/-/issues

