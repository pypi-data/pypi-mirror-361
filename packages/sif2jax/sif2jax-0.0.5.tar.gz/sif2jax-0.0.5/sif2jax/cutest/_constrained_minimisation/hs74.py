import jax.numpy as jnp

from ..._problem import AbstractConstrainedMinimisation


class HS74(AbstractConstrainedMinimisation):
    """Problem 74 from the Hock-Schittkowski test collection.

    A 4-variable nonlinear objective function with two inequality constraints, three
    equality constraints and bounds.

    f(x) = 3*x₁ + 1.E-6*x₁³ + 2*x₂ + (2/3)*E-6*x₂³

    Subject to:
        x₄ - x₃ + a₁ ≥ 0
        x₃ - x₄ + a₁ ≥ 0
        1000*sin(-x₂ - 0.25) + 1000*sin(-x₄ - 0.25) + 894.8 - x₁ = 0
        1000*sin(x₃ - 0.25) + 1000*sin(x₃ - x₄ - 0.25) + 894.8 - x₂ = 0
        1000*sin(x₄ - 0.25) + 1000*sin(x₄ - x₃ - 0.25) + 1294.8 = 0
        0 ≤ x₁ ≤ 1200, i=1,2
        -a₁ ≤ xᵢ ≤ a₁, i=3,4

    where a₁ = 0.55

    Source: problem 74 in
    W. Hock and K. Schittkowski,
    "Test examples for nonlinear programming codes",
    Lectures Notes in Economics and Mathematical Systems 187, Springer
    Verlag, Heidelberg, 1981.

    Also cited: Beuneu [9]

    Classification: PGR-P1-(1,2)
    """

    y0_iD: int = 0
    provided_y0s: frozenset = frozenset({0})

    def objective(self, y, args):
        x1, x2, x3, x4 = y
        return 3 * x1 + 1.0e-6 * x1**3 + 2 * x2 + (2.0 / 3.0) * 1.0e-6 * x2**3

    def y0(self):
        return jnp.array([0.0, 0.0, 0.0, 0.0])  # not feasible according to the problem

    def args(self):
        return None

    def expected_result(self):
        return jnp.array([679.9453, 1026.067, 0.1188764, -0.3962336])

    def expected_objective_value(self):
        return jnp.array(5126.4981)

    def bounds(self):
        # Problem parameter
        a1 = 0.55
        return (jnp.array([0.0, 0.0, -a1, -a1]), jnp.array([1200.0, 1200.0, a1, a1]))

    def constraint(self, y):
        x1, x2, x3, x4 = y
        # Problem parameter
        a1 = 0.55

        # Inequality constraints (g(x) ≥ 0)
        ineq1 = x4 - x3 + a1
        ineq2 = x3 - x4 + a1

        # Equality constraints
        eq1 = 1000 * jnp.sin(-x2 - 0.25) + 1000 * jnp.sin(-x4 - 0.25) + 894.8 - x1
        eq2 = 1000 * jnp.sin(x3 - 0.25) + 1000 * jnp.sin(x3 - x4 - 0.25) + 894.8 - x2
        eq3 = 1000 * jnp.sin(x4 - 0.25) + 1000 * jnp.sin(x4 - x3 - 0.25) + 1294.8

        equality_constraints = jnp.array([eq1, eq2, eq3])
        inequality_constraints = jnp.array([ineq1, ineq2])
        return equality_constraints, inequality_constraints
