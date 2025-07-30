"""Paquete ecuaciones_diferenciales_ordinarias - Métodos numéricos y simulación en Python

El paquete ecuaciones_diferenciales_ordinarias es un submódulo de mnspy, enfocada en la solución de
ecuaciones diferenciales ordinarias

"""
from .ecuaciones_diferenciales_ordinarias import EcuacionesDiferencialesOrdinarias
from .euler import Euler
from .heun import Heun
from .punto_medio import PuntoMedio
from .runge_kutta import RungeKutta
