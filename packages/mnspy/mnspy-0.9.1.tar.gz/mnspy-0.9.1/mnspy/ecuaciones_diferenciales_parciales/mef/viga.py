from mnspy.ecuaciones_diferenciales_parciales.mef import Nodo, Elemento, Rigidez
from mnspy.utilidades import es_notebook, _generar_matrix
from mnspy.ecuaciones_algebraicas_lineales import Gauss
from IPython.display import display, Math
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.transforms as transforms
import sympy as sp

TOL_CERO = 1E-10
sp.init_printing(use_latex=True)

# plt.rcParams.update({
#     "text.usetex": True,
#     "font.family": "sans-serif",
#     "font.sans-serif": "Helvetica",
# })
plt.rcParams.update(plt.rcParamsDefault)


class Viga(Elemento):
    def __init__(self, nombre: str, nodo_i: Nodo, nodo_j: Nodo, E: float, I: float):
        super().__init__(nombre, nodo_i, nodo_j)
        if nodo_j.es_rotula:
            self._k = Rigidez(np.array([[1, self._L, -1, 0],
                                        [self._L, self._L ** 2, -self._L, 0],
                                        [-1, -self._L, 1, 0],
                                        [0, 0, 0, 0]],
                                       dtype=np.double) * 3 * E * I / self._L ** 3, [self._nodo_i, self._nodo_j],
                              ['y', 'eje_z'])
        else:
            self._k = Rigidez(np.array([[12, 6 * self._L, -12, 6 * self._L],
                                        [6 * self._L, 4 * self._L ** 2, -6 * self._L, 2 * self._L ** 2],
                                        [-12, -6 * self._L, 12, -6 * self._L],
                                        [6 * self._L, 2 * self._L ** 2, -6 * self._L, 4 * self._L ** 2]],
                                       dtype=np.double) * E * I / self._L ** 3, [self._nodo_i, self._nodo_j],
                              ['y', 'eje_z'])
        self._fuerzas_i = np.zeros((len(self._k.grados), 1))
        self._fuerzas_j = np.zeros((len(self._k.grados), 1))
        # Si hay una rótula
        self._fuerzas_i_rot = np.zeros((len(self._k.grados), 1))
        self._fuerzas_j_rot = np.zeros((len(self._k.grados), 1))
        self._nodo_i.grados_libertad['y'].label_reaccion = 'F'
        self._nodo_i.grados_libertad['y'].label_fuerza = 'f'
        self._nodo_i.grados_libertad['eje_z'].label_reaccion = 'M'
        self._nodo_i.grados_libertad['eje_z'].label_fuerza = 'm'
        self._nodo_j.grados_libertad['y'].label_reaccion = 'F'
        self._nodo_j.grados_libertad['y'].label_fuerza = 'f'
        self._nodo_j.grados_libertad['eje_z'].label_reaccion = 'M'
        self._nodo_j.grados_libertad['eje_z'].label_fuerza = 'm'
        self._cargas = {'distribuida': [], 'puntual': [],
                        'momento': []}  # distribuida [q_1, q_2], momento o puntual [q a]
        self._coef = {'A': 0.0, 'B': 0.0, 'c_1': 0.0, 'c_2': 0.0, 'c_3': 0.0, 'c_4': 0.0}
        self._E = E
        self._I = I

    def _repr_latex_(self):
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(), dtype=object).reshape(-1, 1)
        vec_f = np.array(self._obtener_etiquetas_fuerzas(), dtype=object).reshape(-1, 1)
        texto_latex = r'\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_f,
                                       '{:}') + r'\end{array}\right\}_{\{f\}}=\left[\begin{array}{' + 'c' * \
                       self._k.obtener_matriz().shape[1] + '}'
        texto_latex += _generar_matrix(self._k.obtener_matriz(),
                                       '{:G}') + r'\end{array}\right]_{[k]}\cdot\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}-\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(self._obtener_fuerzas(),
                                       '{:}') + r'\end{array}\right\}_{\{f_{o}\}}'
        if self._nodo_j.es_rotula:
            texto_latex += r'-\left\{\begin{array}{c}' + _generar_matrix(self._obtener_fuerzas_por_rotula(),
                                                                         '{:}') + r'\end{array}\right\}_{\{f_{rot}\}}'
        return '$' + texto_latex + '$'

    def __repr__(self):
        """Overload del método __repr__

        Returns
        -------
        Muestra el sistema de ecuaciones en forma matricial y en latex para iPython
        """
        # self.mostrar_sistema()
        # return "{f}\t-> Fuerzas internas\n[k]\t-> Matriz de rigidez local\n{d}\t-> Deformaciones\n{fo}\t-> Fuerzas nodales equivalentes"
        return 'Viga: ' + self.nombre

    def agregar_carga_distribuida(self, q: float):
        self._nodo_i.grados_libertad['y'].fuerza += q * self._L / 2
        self._fuerzas_i[0, 0] += q * self._L / 2
        self._nodo_i.grados_libertad['eje_z'].fuerza += q * self._L ** 2 / 12
        self._fuerzas_i[1, 0] += q * self._L ** 2 / 12
        self._nodo_j.grados_libertad['y'].fuerza += q * self._L / 2
        self._fuerzas_j[0, 0] += q * self._L / 2
        self._nodo_j.grados_libertad['eje_z'].fuerza += -q * self._L ** 2 / 12
        self._fuerzas_j[1, 0] += -q * self._L ** 2 / 12

        self._cargas['distribuida'].append([q, q])

        if self._nodo_j.es_rotula:
            self._nodo_i.grados_libertad['y'].fuerza -= (-q * self._L ** 2 / 12) * 3.0 / (2.0 * self._L)
            self._fuerzas_i_rot[0, 0] -= (-q * self._L ** 2 / 12) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['eje_z'].fuerza -= 0.5 * (-q * self._L ** 2 / 12)
            self._fuerzas_i_rot[1, 0] -= 0.5 * (-q * self._L ** 2 / 12)
            self._nodo_j.grados_libertad['y'].fuerza -= -(-q * self._L ** 2 / 12) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[0, 0] -= -(-q * self._L ** 2 / 12) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['eje_z'].fuerza -= -q * self._L ** 2 / 12
            self._fuerzas_j_rot[1, 0] -= -q * self._L ** 2 / 12

    def agregar_carga_trapezoidal(self, q_1: float, q_2: float):
        self._nodo_i.grados_libertad['y'].fuerza += q_1 * self._L / 2 + 3 * (q_2 - q_1) * self._L / 20
        self._fuerzas_i[0, 0] += q_1 * self._L / 2 + 3 * (q_2 - q_1) * self._L / 20
        self._nodo_i.grados_libertad['eje_z'].fuerza += q_1 * self._L ** 2 / 12 + (q_2 - q_1) * self._L ** 2 / 30
        self._fuerzas_i[1, 0] += q_1 * self._L ** 2 / 12 + (q_2 - q_1) * self._L ** 2 / 30
        self._nodo_j.grados_libertad['y'].fuerza += q_1 * self._L / 2 + 7 * (q_2 - q_1) * self._L / 20
        self._fuerzas_j[0, 0] += q_1 * self._L / 2 + 7 * (q_2 - q_1) * self._L / 20
        self._nodo_j.grados_libertad['eje_z'].fuerza += -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20
        self._fuerzas_j[1, 0] += -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20

        self._cargas['distribuida'].append([q_1, q_2])

        if self._nodo_j.es_rotula:
            self._nodo_i.grados_libertad['y'].fuerza -= (-q_1 * self._L ** 2 / 12 - (
                    q_2 - q_1) * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._fuerzas_i_rot[0, 0] -= (-q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20) * 3.0 / (
                    2.0 * self._L)
            self._nodo_i.grados_libertad['eje_z'].fuerza -= 0.5 * (
                    -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20)
            self._fuerzas_i_rot[1, 0] -= 0.5 * (-q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20)
            self._nodo_j.grados_libertad['y'].fuerza -= -(
                    -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[0, 0] -= -(-q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20) * 3.0 / (
                    2.0 * self._L)
            self._nodo_j.grados_libertad['eje_z'].fuerza -= -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20
            self._fuerzas_j_rot[1, 0] -= -q_1 * self._L ** 2 / 12 - (q_2 - q_1) * self._L ** 2 / 20

    def agregar_carga_puntual(self, p: float, a: float = None):
        if a is None:
            a = self._L / 2
        self._nodo_i.grados_libertad['y'].fuerza += p * (self._L - a) ** 2 * (self._L + 2 * a) / self._L ** 3
        self._fuerzas_i[0, 0] += p * (self._L - a) ** 2 * (self._L + 2 * a) / self._L ** 3
        self._nodo_i.grados_libertad['eje_z'].fuerza += p * a * (self._L - a) ** 2 / self._L ** 2
        self._fuerzas_i[1, 0] += p * a * (self._L - a) ** 2 / self._L ** 2
        self._nodo_j.grados_libertad['y'].fuerza += p * a ** 2 * (self._L + 2 * (self._L - a)) / self._L ** 3
        self._fuerzas_j[0, 0] += p * a ** 2 * (self._L + 2 * (self._L - a)) / self._L ** 3
        self._nodo_j.grados_libertad['eje_z'].fuerza += -p * (self._L - a) * a ** 2 / self._L ** 2
        self._fuerzas_j[1, 0] += -p * (self._L - a) * a ** 2 / self._L ** 2

        self._cargas['puntual'].append([p, a])
        self._cargas['puntual'].sort(key=lambda l: l[1])

        if self._nodo_j.es_rotula:
            self._nodo_i.grados_libertad['y'].fuerza -= (-p * (self._L - a) * a ** 2 / self._L ** 2) * 3.0 / (
                    2.0 * self._L)
            self._fuerzas_i_rot[0, 0] -= (-p * (self._L - a) * a ** 2 / self._L ** 2) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['eje_z'].fuerza -= 0.5 * (-p * (self._L - a) * a ** 2 / self._L ** 2)
            self._fuerzas_i_rot[1, 0] -= 0.5 * (-p * (self._L - a) * a ** 2 / self._L ** 2)
            self._nodo_j.grados_libertad['y'].fuerza -= -(-p * (self._L - a) * a ** 2 / self._L ** 2) * 3.0 / (
                    2.0 * self._L)
            self._fuerzas_j_rot[0, 0] -= -(-p * (self._L - a) * a ** 2 / self._L ** 2) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['eje_z'].fuerza -= -p * (self._L - a) * a ** 2 / self._L ** 2
            self._fuerzas_j_rot[1, 0] -= -p * (self._L - a) * a ** 2 / self._L ** 2

    def agregar_momento(self, m: float, a: float = None):
        m *= -1
        if a is None:
            a = self._L / 2
        self._nodo_i.grados_libertad['y'].fuerza += 6 * m * a * (self._L - a) / self._L ** 3
        self._fuerzas_i[0, 0] += 6 * m * a * (self._L - a) / self._L ** 3
        self._nodo_i.grados_libertad['eje_z'].fuerza += m * (self._L - a) * (3 * a - self._L) / self._L ** 2
        self._fuerzas_i[1, 0] += m * (self._L - a) * (3 * a - self._L) / self._L ** 2
        self._nodo_j.grados_libertad['y'].fuerza += - 6 * m * a * (self._L - a) / self._L ** 3
        self._fuerzas_j[0, 0] += - 6 * m * a * (self._L - a) / self._L ** 3
        self._nodo_j.grados_libertad['eje_z'].fuerza += m * a * (2 * self._L - 3 * a) / self._L ** 2
        self._fuerzas_j[1, 0] += m * a * (2 * self._L - 3 * a) / self._L ** 2

        self._cargas['momento'].append([-m, a])
        self._cargas['momento'].sort(key=lambda l: l[1])

        if self._nodo_j.es_rotula:
            self._nodo_i.grados_libertad['y'].fuerza -= (m * a * (2 * self._L - 3 * a) / self._L ** 2) * 3.0 / (
                    2.0 * self._L)
            self._fuerzas_i_rot[0, 0] -= (m * a * (2 * self._L - 3 * a) / self._L ** 2) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['eje_z'].fuerza -= 0.5 * (m * a * (2 * self._L - 3 * a) / self._L ** 2)
            self._fuerzas_i_rot[1, 0] -= 0.5 * (m * a * (2 * self._L - 3 * a) / self._L ** 2)
            self._nodo_j.grados_libertad['y'].fuerza -= -(m * a * (2 * self._L - 3 * a) / self._L ** 2) * 3.0 / (
                    2.0 * self._L)
            self._fuerzas_j_rot[0, 0] -= -(m * a * (2 * self._L - 3 * a) / self._L ** 2) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['eje_z'].fuerza -= m * a * (2 * self._L - 3 * a) / self._L ** 2
            self._fuerzas_j_rot[1, 0] -= m * a * (2 * self._L - 3 * a) / self._L ** 2

    def agregar_carga_triangular_descendente(self, q: float):
        self._nodo_i.grados_libertad['y'].fuerza += 7 * q * self._L / 20
        self._fuerzas_i[0, 0] += 7 * q * self._L / 20
        self._nodo_i.grados_libertad['eje_z'].fuerza += q * self._L ** 2 / 20
        self._fuerzas_i[1, 0] += q * self._L ** 2 / 20
        self._nodo_j.grados_libertad['y'].fuerza += 3 * q * self._L / 20
        self._fuerzas_j[0, 0] += 3 * q * self._L / 20
        self._nodo_j.grados_libertad['eje_z'].fuerza += -q * self._L ** 2 / 30
        self._fuerzas_j[1, 0] += -q * self._L ** 2 / 30

        self._cargas['distribuida'].append([q, 0])

        if self._nodo_j.es_rotula:
            self._nodo_i.grados_libertad['y'].fuerza -= (-q * self._L ** 2 / 30) * 3.0 / (2.0 * self._L)
            self._fuerzas_i_rot[0, 0] -= (-q * self._L ** 2 / 30) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['eje_z'].fuerza -= 0.5 * (-q * self._L ** 2 / 30)
            self._fuerzas_i_rot[1, 0] -= 0.5 * (-q * self._L ** 2 / 30)
            self._nodo_j.grados_libertad['y'].fuerza -= -(-q * self._L ** 2 / 30) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[0, 0] -= -(-q * self._L ** 2 / 30) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['eje_z'].fuerza -= -q * self._L ** 2 / 30
            self._fuerzas_j_rot[1, 0] -= -q * self._L ** 2 / 30

    def agregar_carga_triangular_ascendente(self, q: float):
        self._nodo_i.grados_libertad['y'].fuerza += 3 * q * self._L / 20
        self._fuerzas_i[0, 0] += 3 * q * self._L / 20
        self._nodo_i.grados_libertad['eje_z'].fuerza += q * self._L ** 2 / 30
        self._fuerzas_i[1, 0] += q * self._L ** 2 / 30
        self._nodo_j.grados_libertad['y'].fuerza += 7 * q * self._L / 20
        self._fuerzas_j[0, 0] += 7 * q * self._L / 20
        self._nodo_j.grados_libertad['eje_z'].fuerza += -q * self._L ** 2 / 20
        self._fuerzas_j[1, 0] += -q * self._L ** 2 / 20

        self._cargas['distribuida'].append([0, q])

        if self._nodo_j.es_rotula:
            self._nodo_i.grados_libertad['y'].fuerza -= (-q * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._fuerzas_i_rot[0, 0] -= (-q * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._nodo_i.grados_libertad['eje_z'].fuerza -= 0.5 * (-q * self._L ** 2 / 20)
            self._fuerzas_i_rot[1, 0] -= 0.5 * (-q * self._L ** 2 / 20)
            self._nodo_j.grados_libertad['y'].fuerza -= -(-q * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._fuerzas_j_rot[0, 0] -= -(-q * self._L ** 2 / 20) * 3.0 / (2.0 * self._L)
            self._nodo_j.grados_libertad['eje_z'].fuerza -= -q * self._L ** 2 / 20
            self._fuerzas_j_rot[1, 0] -= -q * self._L ** 2 / 20

    def _obtener_cargas(self) -> dict:
        return self._cargas

    def ecuacion_de_cortante(self):
        x = sp.symbols('x')
        V = sp.Function('V')(x)
        self._calcular_coeficientes_diagramas()
        x_1 = self._nodo_i.punto[0]
        x_2 = self._nodo_j.punto[0]
        ec = -self._coef['A'] * x ** 2 / 2 - self._coef['B'] * x + self._coef['c_1']
        if len(self._cargas['puntual']) == 0:
            return sp.Eq(V, sp.Piecewise((ec, (x >= x_1) & (x <= x_2))))
        else:
            dis = [float(x_1)] + [float(x_1 + c[1]) for c in self._cargas['puntual']] + [float(x_2)]
            car = [ec]
            for c in self._cargas['puntual']:
                car.append(car[-1] + c[0])
            tramos = []
            for i in range(len(dis) - 1):
                tramos.append((car[i], (dis[i] <= x) & (x <= dis[i + 1])))
            return sp.Eq(V, sp.Piecewise(*tramos))

    def ecuacion_de_momento(self):
        x = sp.symbols('x')
        M = sp.Function('M')(x)
        self._calcular_coeficientes_diagramas()
        x_1 = self._nodo_i.punto[0]
        x_2 = self._nodo_j.punto[0]
        ec = -self._coef['A'] * x ** 3 / 6 - self._coef['B'] * x ** 2 / 2 + self._coef['c_1'] * x + self._coef[
            'c_2']
        if len(self._cargas['puntual']) == 0 and len(self._cargas['momento']) == 0:
            return sp.Eq(M, sp.Piecewise((ec, (x >= x_1) & (x <= x_2))))
        else:
            cargas_ele = dict()
            for c in self._cargas['puntual']:
                cargas_ele[c[1]] = sp.expand(c[0] * (x - (x_1 + c[1])))
            for m in self._cargas['momento']:
                cargas_ele[m[1]] = sp.expand(cargas_ele.get(m[1], 0.0) - m[0])
            if len(cargas_ele) > 0:
                cargas_ele = dict(sorted(cargas_ele.items(), key=lambda item: item[0]))
            dis = [float(x_1)] + [float(x_1 + c) for c in cargas_ele.keys()] + [float(x_2)]
            # dis = [float(x_1)] + [float(x_1 + c[1]) for c in self._cargas['puntual']] + [float(x_2)]
            car = [ec]
            for c in cargas_ele.values():
                car.append(sp.expand(car[-1] + c))
            tramos = []
            for i in range(len(dis) - 1):
                tramos.append((car[i], (dis[i] <= x) & (x <= dis[i + 1])))
            return sp.Eq(M, sp.Piecewise(*tramos))

    def ecuacion_de_giro(self):
        x = sp.symbols('x')
        phi = sp.Function('phi')(x)
        self._calcular_coeficientes_diagramas()
        x_1 = self._nodo_i.punto[0]
        x_2 = self._nodo_j.punto[0]
        ec = (-self._coef['A'] * x ** 4 / 24 - self._coef['B'] * x ** 3 / 6 + self._coef['c_1'] * x ** 2 / 2 +
              self._coef['c_2'] * x + self._coef['c_3']) / self._E / self._I
        if len(self._cargas['puntual']) == 0 and len(self._cargas['momento']) == 0:
            return sp.Eq(phi, sp.Piecewise((ec, (x >= x_1) & (x <= x_2))))
        else:
            cargas_ele = dict()
            for c in self._cargas['puntual']:
                cargas_ele[c[1]] = sp.expand((c[0] * (x - (x_1 + c[1])) ** 2 / 2) / self._E / self._I)
            for m in self._cargas['momento']:
                cargas_ele[m[1]] = sp.expand(cargas_ele.get(m[1], 0.0) - m[0] * (x - (x_1 + m[1])) / self._E / self._I)
            if len(cargas_ele) > 0:
                cargas_ele = dict(sorted(cargas_ele.items(), key=lambda item: item[0]))
            dis = [float(x_1)] + [float(x_1 + c) for c in cargas_ele.keys()] + [float(x_2)]
            # dis = [float(x_1)] + [float(x_1 + c[1]) for c in self._cargas['puntual']] + [float(x_2)]
            car = [ec]
            for c in cargas_ele.values():
                car.append(sp.expand(car[-1] + c))
            # for c in self._cargas['puntual']:
            #     car.append(sp.expand(car[-1] + (c[0] * (x - (x_1 + c[1])) ** 2 / 2) / self._E / self._I))
            tramos = []
            for i in range(len(dis) - 1):
                tramos.append((car[i], (dis[i] <= x) & (x <= dis[i + 1])))
            return sp.Eq(phi, sp.Piecewise(*tramos))

    def ecuacion_de_deflexion(self):
        x = sp.symbols('x')
        y = sp.Function('y')(x)
        self._calcular_coeficientes_diagramas()
        x_1 = self._nodo_i.punto[0]
        x_2 = self._nodo_j.punto[0]
        ec = (-self._coef['A'] * x ** 5 / 120 - self._coef['B'] * x ** 4 / 24 + self._coef['c_1'] * x ** 3 / 6 +
              self._coef['c_2'] * x ** 2 / 2 + self._coef['c_3'] * x + self._coef['c_4']) / self._E / self._I
        x = sp.symbols('x')
        if len(self._cargas['puntual']) == 0 and len(self._cargas['momento']) == 0:
            return sp.Eq(y, sp.Piecewise((ec, (x >= x_1) & (x <= x_2))))
        else:
            cargas_ele = dict()
            for c in self._cargas['puntual']:
                cargas_ele[c[1]] = sp.expand((c[0] * (x - (x_1 + c[1])) ** 3 / 6) / self._E / self._I)
            for m in self._cargas['momento']:
                cargas_ele[m[1]] = sp.expand(
                    cargas_ele.get(m[1], 0.0) - (m[0] * (x - (x_1 + m[1])) ** 2 / 2) / self._E / self._I)
            if len(cargas_ele) > 0:
                cargas_ele = dict(sorted(cargas_ele.items(), key=lambda item: item[0]))
            dis = [float(x_1)] + [float(x_1 + c) for c in cargas_ele.keys()] + [float(x_2)]
            # dis = [float(x_1)] + [float(x_1 + c[1]) for c in self._cargas['puntual']] + [float(x_2)]
            car = [ec]
            for c in cargas_ele.values():
                car.append(sp.expand(car[-1] + c))

            # car = [ec]
            # for c in self._cargas['puntual']:
            #     car.append(sp.expand(car[-1] + (c[0] * (x - (x_1 + c[1])) ** 3 / 6) / self._E / self._I))
            tramos = []
            for i in range(len(dis) - 1):
                tramos.append((car[i], (dis[i] <= x) & (x <= dis[i + 1])))
            return sp.Eq(y, sp.Piecewise(*tramos))

    def _calcular_coeficientes_diagramas(self):
        x_1 = self._nodo_i.punto[0]
        x_2 = self._nodo_j.punto[0]
        q_1 = q_2 = 0
        for c in self._cargas['distribuida']:
            q_1 += c[0]
            q_2 += c[1]
        q = [0.0, 0.0]
        for c in self._cargas['puntual']:
            q[0] -= c[0] * (self._L - c[1]) ** 3 / 6
            q[1] -= c[0] * (self._L - c[1]) ** 2 / 2
        for m in self._cargas['momento']:
            q[0] -= -m[0] * (self._L - m[1]) ** 2 / 2
            q[1] -= -m[0] * (self._L - m[1])
        self._coef['A'] = -(q_2 - q_1) / (x_2 - x_1)
        self._coef['B'] = -q_1 - self._coef['A'] * x_1
        A = np.array([[x_1 ** 3 / 6.0, x_1 ** 2 / 2.0, x_1, 1.0], [x_1 ** 2 / 2.0, x_1, 1.0, 0.0],
                      [x_2 ** 3 / 6.0, x_2 ** 2 / 2.0, x_2, 1.0], [x_2 ** 2 / 2.0, x_2, 1.0, 0.0]], dtype=np.double)
        b = self._obtener_desplazamientos() * self._E * self._I
        b += np.array([[self._coef['A'] * x_1 ** 5 / 120 + self._coef['B'] * x_1 ** 4 / 24],
                       [self._coef['A'] * x_1 ** 4 / 24 + self._coef['B'] * x_1 ** 3 / 6],
                       [self._coef['A'] * x_2 ** 5 / 120 + self._coef['B'] * x_2 ** 4 / 24 + q[0]],
                       [self._coef['A'] * x_2 ** 4 / 24 + self._coef['B'] * x_2 ** 3 / 6 + q[1]]])
        sol = Gauss(A, b, pivote_parcial=True)
        sol.x[abs(sol.x) < TOL_CERO] = 0.0
        self._coef['c_1'] = sol.x[0, 0]
        self._coef['c_2'] = sol.x[1, 0]
        self._coef['c_3'] = sol.x[2, 0]
        self._coef['c_4'] = sol.x[3, 0]

    def _obtener_arrays_cortantes(self, n_puntos: int = 100):
        x = sp.symbols('x')
        f = self.ecuacion_de_cortante()
        x_1 = self._nodo_i.punto[0]
        x_2 = self._nodo_j.punto[0]
        lista_x = np.linspace(x_1, x_2, n_puntos)
        ev = sp.lambdify(x, f.args[1], 'numpy')
        lista_v = ev(lista_x)
        der = sp.diff(f.args[1])
        p_crit = []
        for i in der.args:
            if sp.degree(i[0]) >= 1:
                p_crit += sp.real_roots(i[0], x)
        # lista_p = [[x_1 + c[1], ev(x_1 + c[1])] for c in self._cargas['puntual']]
        lista_p = []
        for c in self._cargas['puntual']:
            for fun in f.args[1].args:
                val, b = fun.subs(x, x_1 + c[1])
                if b:
                    lista_p.append((x_1 + c[1], val.evalf()))
        lista_p = [(x_1, ev(x_1))] + lista_p + [(x_2, ev(x_2))]
        for item in p_crit:
            lista_p.append((item, f.args[1].subs(x, item).evalf()))
        lista_p = np.array(lista_p, dtype=float)
        lista_p[:, 1][abs(lista_p[:, 1]) < TOL_CERO] = 0.0
        return lista_x, lista_v, lista_p

    def _obtener_arrays_momentos(self, n_puntos: int = 100):
        x = sp.symbols('x')
        f = self.ecuacion_de_momento()
        x_1 = self._nodo_i.punto[0]
        x_2 = self._nodo_j.punto[0]
        lista_x = np.linspace(x_1, x_2, n_puntos)
        ev = sp.lambdify(x, f.args[1], 'numpy')
        lista_m = ev(lista_x)
        der = sp.diff(f.args[1])
        p_crit = []
        for i in der.args:
            if sp.degree(i[0]) >= 1:
                p_crit += sp.real_roots(i[0], x)
        lista_p = [(x_1 + c[1], ev(x_1 + c[1])) for c in self._cargas['puntual']]
        # lista_p = []
        for m in self._cargas['momento']:
            for fun in f.args[1].args:
                val, b = fun.subs(x, x_1 + m[1])
                if b:
                    lista_p.append((x_1 + m[1], val.evalf()))
        lista_p = [(x_1, ev(x_1))] + lista_p + [(x_2, ev(x_2))]
        for item in p_crit:
            lista_p.append((item, f.args[1].subs(x, item).evalf()))
        lista_p = np.array(lista_p, dtype=float)
        lista_p[:, 1][abs(lista_p[:, 1]) < TOL_CERO] = 0.0
        return lista_x, lista_m, lista_p

    def _obtener_arrays_angulos(self, n_puntos: int = 100):
        x = sp.symbols('x')
        f = self.ecuacion_de_giro()
        x_1 = self._nodo_i.punto[0]
        x_2 = self._nodo_j.punto[0]
        lista_x = np.linspace(x_1, x_2, n_puntos)
        ev = sp.lambdify(x, f.args[1], 'numpy')
        lista_o = ev(lista_x)
        der = sp.diff(f.args[1])
        p_crit = []
        for i in der.args:
            if sp.degree(i[0]) >= 1:
                p_crit += sp.real_roots(i[0], x)
        lista_p = [[x_1 + c[1], ev(x_1 + c[1])] for c in self._cargas['puntual']]
        lista_p += [(x_1 + m[1], ev(x_1 + m[1])) for m in self._cargas['momento']]
        # lista_p = []
        # for c in self._cargas['puntual']:
        #     for fun in f.args[1].args:
        #         val, b = fun.subs(x, x_1 + c[1])
        #         if b:
        #             lista_p.append((x_1 + c[1], val.evalf()))
        lista_p = [(x_1, ev(x_1))] + lista_p + [(x_2, ev(x_2))]
        for item in p_crit:
            lista_p.append((item, f.args[1].subs(x, item).evalf()))
        lista_p = np.array(lista_p, dtype=float)
        lista_p[:, 1][abs(lista_p[:, 1]) < TOL_CERO] = 0.0
        return lista_x, lista_o, lista_p

    def _obtener_arrays_deflexion(self, n_puntos: int = 100):
        x = sp.symbols('x')
        f = self.ecuacion_de_deflexion()
        x_1 = self._nodo_i.punto[0]
        x_2 = self._nodo_j.punto[0]
        lista_x = np.linspace(x_1, x_2, n_puntos)
        ev = sp.lambdify(x, f.args[1], 'numpy')
        lista_y = ev(lista_x)
        der = sp.diff(f.args[1])
        p_crit = []
        for i in der.args:
            if sp.degree(i[0]) >= 1:
                p_crit += sp.real_roots(i[0], x)
        lista_p = [[x_1 + c[1], ev(x_1 + c[1])] for c in self._cargas['puntual']]
        lista_p += [(x_1 + m[1], ev(x_1 + m[1])) for m in self._cargas['momento']]
        # lista_p = []
        # for c in self._cargas['puntual']:
        #     for fun in f.args[1].args:
        #         val, b = fun.subs(x, x_1 + c[1])
        #         if b:
        #             lista_p.append((x_1 + c[1], val.evalf()))
        lista_p = [(x_1, ev(x_1))] + lista_p + [(x_2, ev(x_2))]
        for item in p_crit:
            lista_p.append((item, f.args[1].subs(x, item).evalf()))
        lista_p = np.array(lista_p, dtype=float)
        lista_p[:, 1][abs(lista_p[:, 1]) < TOL_CERO] = 0.0
        return lista_x, lista_y, lista_p

    def diagrama_de_cortante(self, n_puntos: int = 500):
        l_x, l_y, l_z = self._obtener_arrays_cortantes(n_puntos)
        plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.5)
        for i in l_z:
            pos_y = 5  # offset escritura
            val_x, val_y = i
            if val_y < 0:
                pos_y = -5
            plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                         textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
        plt.grid()
        plt.title('Diagrama de cortante')
        plt.xlabel('$x$')
        plt.ylabel('$V$')
        plt.show()

    def diagrama_de_momento(self, n_puntos: int = 500):
        l_x, l_y, l_z = self._obtener_arrays_momentos(n_puntos)
        plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.5)
        for i in l_z:
            pos_y = 5  # offset escritura
            val_x, val_y = i
            if val_y < 0:
                pos_y = -5
            plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                         textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
        plt.grid()
        plt.title('Diagrama de momento')
        plt.xlabel('$x$')
        plt.ylabel('$M$')
        plt.show()

    def diagrama_de_giro(self, n_puntos: int = 500):
        l_x, l_y, l_z = self._obtener_arrays_angulos(n_puntos)
        plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.5)
        for i in l_z:
            pos_y = 5  # offset escritura
            val_x, val_y = i
            if val_y < 0:
                pos_y = -5
            plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                         textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
        plt.grid()
        plt.title('Diagrama de giro')
        plt.xlabel('$x$')
        plt.ylabel(r'$\phi$')
        plt.show()

    def diagrama_de_deflexion(self, n_puntos: int = 500):
        l_x, l_y, l_z = self._obtener_arrays_deflexion(n_puntos)
        plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.5)
        for i in l_z:
            pos_y = 5  # offset escritura
            val_x, val_y = i
            if val_y < 0:
                pos_y = -5
            plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
                         textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
        plt.grid()
        plt.title('Diagrama de deflexión')
        plt.xlabel('$x$')
        plt.ylabel('$y$')
        plt.show()

    def fuerzas_internas(self):
        fuerzas_internas = np.matmul(self._k.k,
                                     self._obtener_desplazamientos()) - self._obtener_fuerzas() - self._obtener_fuerzas_por_rotula()
        fuerzas_internas[abs(fuerzas_internas) < TOL_CERO] = 0.0
        if es_notebook():
            indice = ['$' + label + '$' for label in self._obtener_etiquetas_fuerzas()]
            return tabulate({'Fuerzas internas': fuerzas_internas}, headers='keys', showindex=indice, tablefmt='html')
        else:
            print(fuerzas_internas)

    def _obtener_etiquetas_fuerzas(self, reducida: bool = False):
        def ajustar_cadena(s: str) -> str:
            if s == 'eje_z':
                return ''
            else:
                return s

        etq = [nodo.grados_libertad[
                   gl].label_fuerza + '^{(' + self.nombre + ')}_{' + nodo.nombre + ajustar_cadena(gl) + '}'
               for nodo in [self._nodo_i, self._nodo_j] for gl in self._k.grados if
               not reducida or nodo.grados_libertad[gl].valor]
        return etq

    def mostrar_sistema(self, reducida: bool = False):
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(reducida), dtype=object).reshape(-1, 1)
        vec_f = np.array(self._obtener_etiquetas_fuerzas(reducida), dtype=object).reshape(-1, 1)
        if es_notebook():
            texto_latex = r'\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_f,
                                           '{:}') + r'\end{array}\right\}_{\{f\}}=\left[\begin{array}{' + 'c' * \
                           self._k.obtener_matriz(reducida).shape[1] + '}'
            texto_latex += _generar_matrix(self._k.obtener_matriz(reducida),
                                           '{:G}') + r'\end{array}\right]_{[k]}\cdot\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}-\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(self._obtener_fuerzas(reducida),
                                           '{:}') + r'\end{array}\right\}_{\{f_{o}\}}'
            display(Math(texto_latex))
        else:
            return np.array2string(self._k.obtener_matriz(reducida),
                                   formatter={'float_kind': lambda x: '{:}'.format(x)})

    def _obtener_desplazamientos(self) -> np.ndarray:
        desplazamiento = None
        for item in self._k.lista_nodos:
            d_i = [d.desplazamiento for d in item.grados_libertad.values() if d.gl in self._k.grados]
            if desplazamiento is None:
                desplazamiento = d_i
            else:
                desplazamiento = np.hstack((desplazamiento, d_i))
        b = np.array(desplazamiento).reshape(-1, 1)
        # Si hay una rotula en el nodo derecho, se ajusta el ángulo
        if self._nodo_j.es_rotula:
            b[3] = (self._fuerzas_j[1] * self._L ** 3 / self._E / self._I - np.matmul(np.array(
                [[6 * self._L, 2 * self._L ** 2, - 6 * self._L]]), b[0:3, ])) / 4 / self._L ** 2
        return b

    def __obtener_path_elemento(self, espesor: float) -> Path:
        t = espesor
        x_1, y_1, Z_1 = self._nodo_i.punto
        x_2, y_2, Z_2 = self._nodo_j.punto
        vertices = np.array([(x_1, y_1 - 0.5 * t), (x_2, y_2 - 0.5 * t), (x_2, y_2 + 0.5 * t), (x_1, y_1 + 0.5 * t),
                             (x_1, y_1 - 0.5 * t)])
        codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
        return Path(vertices, codes)

    def diagrama_fuerzas_internas(self):
        def dibujar_momento(p: tuple[float, float], r: float, teta_1: float = 0, teta_2: float = 90, ejes=None,
                            **kwargs):
            c_x, c_y = p
            r /= 72
            alfa = 0
            teta_flecha = teta_2
            if teta_2 < teta_1:
                teta_1, teta_2 = (teta_2, teta_1)
                alfa = 180
                teta_flecha = teta_1
            trans = (fig.dpi_scale_trans + transforms.ScaledTranslation(c_x, c_y, ejes.transData))
            arc = patches.Arc((0, 0), r, r, angle=0, theta1=teta_1, theta2=teta_2, transform=trans
                              , capstyle='round', linestyle='-', **kwargs)
            ejes.add_patch(arc)
            p_x = (r / 2) * np.cos(np.radians(teta_flecha))
            p_y = (r / 2) * np.sin(np.radians(teta_flecha))
            ejes.add_patch(
                patches.RegularPolygon(xy=(p_x, p_y), numVertices=3, radius=r / 20,
                                       orientation=np.radians(teta_flecha + alfa), transform=trans, **kwargs))

        #############
        # if self._nodo_j.es_rotula:
        #     fo_rotula = np.array(
        #         [[3.0 / (2.0 * self._L)], [0.5], [-3.0 / (2.0 * self._L)]])
        #     fo_rotula = np.vstack((fo_rotula, np.array([[0.0]]))) * self._fuerzas_j[1]
        #     fuerzas_internas = np.matmul(self._k.k,
        #                                  self._obtener_desplazamientos()) - self._obtener_fuerzas() + fo_rotula
        # else:
        #    fuerzas_internas = np.matmul(self._k.k, self._obtener_desplazamientos()) - self._obtener_fuerzas()
        #############
        fuerzas_internas = np.matmul(self._k.k,
                                     self._obtener_desplazamientos()) - self._obtener_fuerzas() - self._obtener_fuerzas_por_rotula()
        fuerzas_internas[abs(fuerzas_internas) < TOL_CERO] = 0.0
        etq = self._obtener_etiquetas_fuerzas()
        fig, ax = plt.subplots()
        ax.add_patch(patches.PathPatch(self.__obtener_path_elemento(self._L / 20), edgecolor='royalblue',
                                       facecolor='lightsteelblue', lw=0.2))
        fuerza = fuerzas_internas[0, 0]
        if fuerza <= 0.0:
            pos = -50
            ali = 'top'
            sentido = '<-'
        else:
            pos = -50
            ali = 'top'
            sentido = '->'
        ax.annotate('$' + etq[0] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_i.punto[0:2]), xycoords='data',
                    xytext=(0, pos), textcoords='offset points', va=ali, ha='center', size=12,
                    arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))
        fuerza = fuerzas_internas[1, 0]
        if fuerza <= 0.0:
            dibujar_momento((self._nodo_i.punto[0], self._nodo_i.punto[1]), 50, 255, 30, ejes=ax, color='b', lw=2)
            pos = -20
            ali = 'right'
        else:
            dibujar_momento((self._nodo_i.punto[0], self._nodo_i.punto[1]), 50, -75, 150, ejes=ax, color='b', lw=2)
            pos = 20
            ali = 'left'
        ax.annotate('$' + etq[1] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_i.punto[0:2]), xycoords='data',
                    xytext=(pos, 20), textcoords='offset points', va='bottom', ha=ali, size=12)
        fuerza = fuerzas_internas[2, 0]
        if fuerza <= 0.0:
            pos = 50
            ali = 'bottom'
            sentido = '->'
        else:
            pos = 50
            ali = 'bottom'
            sentido = '<-'
        ax.annotate('$' + etq[2] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(0, pos), textcoords='offset points', va=ali, ha='center', size=12,
                    arrowprops=dict(arrowstyle=sentido, connectionstyle="arc3"))

        fuerza = fuerzas_internas[3, 0]
        if fuerza <= 0.0:
            dibujar_momento((self._nodo_j.punto[0], self._nodo_j.punto[1]), 50, 255, 30, ejes=ax, color='b', lw=2)
            pos = -20
            ali = 'right'
        else:
            dibujar_momento((self._nodo_j.punto[0], self._nodo_j.punto[1]), 50, -75, 150, ejes=ax, color='b', lw=2)
            pos = 20
            ali = 'left'
        ax.annotate('$' + etq[3] + '=' + '{:G}$'.format(abs(fuerza)),
                    xy=(self._nodo_j.punto[0:2]), xycoords='data',
                    xytext=(pos, 20), textcoords='offset points', va='bottom', ha=ali, size=12)
        ax.scatter([self._nodo_i.punto[0], self._nodo_j.punto[0]], [self._nodo_i.punto[1], self._nodo_j.punto[1]],
                   c='navy', marker='o')

        ax.axis('equal')
        ax.axis('off')
        ax.set_xmargin(0.15)
        ax.set_ymargin(0.15)
        plt.show()


def main():
    n_1 = Nodo('1', 0, grados_libertad={'y': False, 'eje_z': True})
    n_2 = Nodo('2', 6, grados_libertad={'y': False, 'eje_z': True})

    e_1 = Viga('1', n_1, n_2, E=200E6, I=1E-4)
    e_1.agregar_carga_trapezoidal(-30, -90)
    from mnspy import Ensamble
    mg = Ensamble([e_1])
    mg.diagrama_cargas()
    mg.solucionar_por_gauss_y_calcular_reacciones()
    mg.solucion()
    mg.diagrama_de_cortante()
    mg.diagrama_de_momento()


if __name__ == '__main__':
    main()
