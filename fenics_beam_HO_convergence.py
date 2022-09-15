import numpy as np
import ufl

from petsc4py import PETSc
from mpi4py import MPI
from dolfinx import fem, mesh, plot
from gmsh_helpers import read_from_msh

import gmsh

steps = np.arange(940, 1600, 100)
for nz in steps:
    # gmsh.initialize()

    element = "tetra"
    order = 1
    L, W, H = 80.0, 7.5, 7.5
    nx, ny = 10, 10
    domain = mesh.create_box(MPI.COMM_WORLD, [[-H, -W, 0.0], [H, W, L]], [nx, ny, nz], mesh.CellType.tetrahedron)

    if element == "hexa":
        V = fem.VectorFunctionSpace(domain, ("S", order))
    else:
        V = fem.VectorFunctionSpace(domain, ("Lagrange", order))


    def left(x):
        return np.isclose(x[2], 0)


    def right(x):
        return np.isclose(x[2], L)


    fdim = domain.topology.dim - 1
    left_facets = mesh.locate_entities_boundary(domain, fdim, left)

    right_facets = mesh.locate_entities_boundary(domain, fdim, right)

    # Concatenate and sort the arrays based on facet indices. Left facets marked with 1, right facets with two
    marked_facets = np.hstack([left_facets, right_facets])
    marked_values = np.hstack([np.full(len(left_facets), 1, dtype=np.int32), np.full(len(right_facets), 2, dtype=np.int32)])
    sorted_facets = np.argsort(marked_facets)
    facet_tag = mesh.meshtags(domain, fdim, marked_facets[sorted_facets], marked_values[sorted_facets])

    left_dofs = fem.locate_dofs_topological(V, facet_tag.dim, facet_tag.indices[facet_tag.values == 1])
    if element == "hexa" and order == 2:
        bcs = [fem.dirichletbc(fem.Function(V), left_dofs)]
    else:
        u_bc = np.array((0,) * domain.geometry.dim, dtype=PETSc.ScalarType)
        bcs = [fem.dirichletbc(u_bc, left_dofs, V)]

    B = fem.Constant(domain, PETSc.ScalarType((0, 0, 0)))
    T = fem.Constant(domain, PETSc.ScalarType((0, 0, 0)))
    v = ufl.TestFunction(V)
    u = fem.Function(V)

    # Spatial dimension
    d = len(u)
    I = ufl.Identity(d)  # Identity tensor
    F = ufl.variable(I + ufl.grad(u))  # Deformation gradient
    C = ufl.variable(F.T * F)  # Right Cauchy-Green tensor
    J = ufl.det(F)
    I1 = ufl.tr(C)

    # Elasticity parameters
    bulk_modulus = fem.Constant(domain, PETSc.ScalarType(10e8))
    a = fem.Constant(domain, PETSc.ScalarType(1e6))
    b = fem.Constant(domain, PETSc.ScalarType(5))
    a_f = fem.Constant(domain, PETSc.ScalarType(16e4))
    b_f = fem.Constant(domain, PETSc.ScalarType(12.8))
    a_s = fem.Constant(domain, PETSc.ScalarType(18e4))
    b_s = fem.Constant(domain, PETSc.ScalarType(10))
    a_fs = fem.Constant(domain, PETSc.ScalarType(9e3))
    b_fs = fem.Constant(domain, PETSc.ScalarType(12))

    f_0 = ufl.as_vector([0.0, 1.0 / ufl.sqrt(2), 1.0 / ufl.sqrt(2)])
    s_0 = ufl.as_vector([0.0, 1.0 / ufl.sqrt(2), -1.0 / ufl.sqrt(2)])

    I_4_f_0 = ufl.dot(C * f_0, f_0)
    I_4_s_0 = ufl.dot(C * s_0, s_0)
    I_8_f_0_s_0 = ufl.dot(C * s_0, f_0)

    W_vol = bulk_modulus * (J ** 2 - 1.0 - 2.0 * ufl.ln(J)) / 4.0
    W_1 = a * ufl.exp((I1 - 3.0) * b) / (2.0 * b)

    I_4_f_0 = I_4_f_0 - 1.0
    I_4_s_0 = I_4_s_0 - 1.0

    W_4f = a_f * (ufl.exp(((I_4_f_0) ** 2) * b_f) - 1.0) / (2.0 * b_f)
    W_4s = a_s * (ufl.exp(((I_4_s_0) ** 2) * b_s) - 1.0) / (2.0 * b_s)

    W_8_fs = a_fs * (ufl.exp((I_8_f_0_s_0 ** 2) * b_fs) - 1.0) / (2.0 * b_fs)

    # Stored strain energy density (Ogden)
    psi = W_vol + W_1 + W_4f + W_4s + W_8_fs

    P = ufl.diff(psi, F)

    metadata = {"quadrature_degree": 2}
    ds = ufl.Measure('ds', domain=domain, subdomain_data=facet_tag, metadata=metadata)
    dx = ufl.Measure("dx", domain=domain, metadata=metadata)

    F = ufl.inner(ufl.grad(v), P) * dx - ufl.inner(v, B) * dx - ufl.inner(v, T) * ds(2)
    #
    problem = fem.petsc.NonlinearProblem(F, u, bcs)

    from dolfinx import nls

    solver = nls.petsc.NewtonSolver(domain.comm, problem)

    # Set Newton solver options
    solver.atol = 1e-05
    solver.rtol = 1e-10
    solver.convergence_criterion = "incremental"

    from dolfinx import log

    log.set_log_level(log.LogLevel.INFO)

    # single loading
    tval0 = -10
    T.value[1] = tval0
    num_its, converged = solver.solve(u)
    assert (converged)
    u.x.scatter_forward()

    print(np.min(u.x.array.reshape(((nx + 1) * (ny + 1) * (nz + 1), 3))[:, 2]))
    with open('./convergence_study/beam/displacement_' + str(u.x.array.shape[0]) + ".txt", 'w') as f:
        f.write(str(np.min(u.x.array.reshape(((nx + 1) * (ny + 1) * (nz + 1), 3))[:, 2])))

    ## export for visualization    
    # import dolfinx.io
    # with dolfinx.io.XDMFFile(MPI.COMM_WORLD, "./liver_solution.xdmf",
    #                          "w") as xdmf:
    #     xdmf.write_mesh(domain)
    #     xdmf.write_function(u, 0)

    # with dolfinx.io.VTKFile(MPI.COMM_WORLD, "output.pvd", "w") as vtk:
    #     vtk.write_function(u, 0.)
