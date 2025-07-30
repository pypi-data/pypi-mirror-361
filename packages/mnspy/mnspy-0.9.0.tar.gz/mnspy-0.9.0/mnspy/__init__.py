"""mnspy - Métodos numéricos y simulación en Python

mnspy es una biblioteca Python diseñada con fines didácticos para explicar los
métodos numéricos y la simulación a estudiantes de ingeniería.

La biblioteca implementa métodos numéricos comunes utilizando programación
orientada a objetos en Python. Se divide en los siguientes módulos:

- raices: encontrar raíces de ecuaciones
- algebra_lineal: resolver sistemas de ecuaciones lineales
- interpolacion: interpolación polinomial
- integrales: métodos numéricos de integración
- derivadas: cálculo numérico de derivadas
- edos: resolver ecuaciones diferenciales ordinarias
- edps: resolver ecuaciones diferenciales parciales

mnspy pretende ser una herramienta didáctica para que los estudiantes
comprendan mejor los conceptos fundamentales detrás de los métodos numéricos
y la simulación científica.

"""
from .derivada import *
from .ecuaciones_diferenciales_ordinarias import *
from .ecuaciones_diferenciales_parciales import *
from .ecuaciones_diferenciales_parciales.mdf import *
from .ecuaciones_diferenciales_parciales.mef import *
from .ecuaciones_diferenciales_parciales.mvf import *
from .ecuaciones_algebraicas_lineales import *
from .integrales import *
from .interpolación import *
from .raíces import *
from .utilidades import *
