"""Paquete interpolación - Métodos numéricos y simulación en Python

El paquete interpolación es un submódulo de mnspy, enfocada en el cálculo de interpolaciones.

"""
from .interpolacion import Interpolacion
from .inter_Newton import InterpolacionNewton
from .inter_Lagrange import InterpolacionLagrange
from .inter_spline_lineal import SplineLineal
from .inter_spline_cubica import SplineCubica
