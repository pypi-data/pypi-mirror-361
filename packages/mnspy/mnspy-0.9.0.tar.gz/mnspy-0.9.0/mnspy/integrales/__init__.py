"""Paquete integrales - Métodos numéricos y simulación en Python

El paquete integrales es un submódulo de mnspy, enfocada en cáculo de integrales de funciones y datos discretos

"""
from .integral import *
from .trapezoidal import *
from .trapezoidal_desigual import *
from .simpson_1_3 import Simpson13
from .simpson_3_8 import Simpson38
from .trapezoidal_desigual_acumulado import TrapezoidalDesigualAcumulado
from .romberg import Romberg
from .gauss_legendre import GaussLegendre
from .cuadratura_adaptativa import CuadraturaAdaptativa
