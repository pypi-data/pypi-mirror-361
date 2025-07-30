from mnspy.ecuaciones_diferenciales_parciales.mef import Nodo, Elemento, Rigidez
from mnspy.utilidades import es_notebook, _generar_matrix
from IPython.display import display, Math
from tabulate import tabulate
import numpy as np

class TriangularCST(Elemento):
    def __init__(self, nombre: str, nodo_i: Nodo, nodo_j: Nodo, nodo_m: Nodo, E: float, espesor: float,
                 coef_poisson: float = 0.3):
        super().__init__(nombre, nodo_i, nodo_j, nodo_m)
        self._E = E
        self._t = espesor
        self._coef_poisson = coef_poisson
        x_i, y_i, z = nodo_i.punto
        x_j, y_j, z = nodo_j.punto
        x_m, y_m, z = nodo_m.punto
        # alfa_i = x_j * y_m - y_j * x_m
        # alfa_j = y_i * x_m - x_i * y_m
        # alfa_m = x_i * y_j - y_i * x_j
        beta_i = y_j - y_m
        beta_j = y_m - y_i
        beta_m = y_i - y_j
        gamma_i = x_m - x_j
        gamma_j = x_i - x_m
        gamma_m = x_j - x_i
        self._A = (x_i * (y_j - y_m) + x_j * (y_m - y_i) + x_m * (y_i - y_j)) / 2
        self._B = np.array([[beta_i, 0, beta_j, 0, beta_m, 0],
                            [0, gamma_i, 0, gamma_j, 0, gamma_m],
                            [gamma_i, beta_i, gamma_j, beta_j, gamma_m, beta_m]],
                           dtype=np.double) / 2 / self._A
        self._D = np.array([[1, coef_poisson, 0],
                            [coef_poisson, 1, 0],
                            [0, 0, (1 - coef_poisson) / 2]],
                           dtype=np.double) * E / (1 - coef_poisson ** 2)
        self._k = Rigidez(np.matmul(np.matmul(self._B.transpose(), self._D), self._B) * self._t * abs(self._A),
                          [self._nodo_i, self._nodo_j, self._nodo_m],
                          ['x', 'y'])
        self._fuerzas_i = np.zeros((len(self._k.grados), 1))
        self._fuerzas_j = np.zeros((len(self._k.grados), 1))
        self._fuerzas_m = np.zeros((len(self._k.grados), 1))
        self._nodo_i.grados_libertad['x'].label_reaccion = 'F'
        self._nodo_i.grados_libertad['x'].label_fuerza = 'f'
        self._nodo_i.grados_libertad['y'].label_reaccion = 'F'
        self._nodo_i.grados_libertad['y'].label_fuerza = 'f'
        self._nodo_j.grados_libertad['x'].label_reaccion = 'F'
        self._nodo_j.grados_libertad['x'].label_fuerza = 'f'
        self._nodo_j.grados_libertad['y'].label_reaccion = 'F'
        self._nodo_j.grados_libertad['y'].label_fuerza = 'f'
        self._nodo_m.grados_libertad['x'].label_reaccion = 'F'
        self._nodo_m.grados_libertad['x'].label_fuerza = 'f'
        self._nodo_m.grados_libertad['y'].label_reaccion = 'F'
        self._nodo_m.grados_libertad['y'].label_fuerza = 'f'

    def _repr_latex_(self):
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(), dtype=object).reshape(-1,1)
        vec_f = np.array(self._obtener_etiquetas_fuerzas(), dtype=object).reshape(-1,1)
        texto_latex = r'\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_f,
                                       '{:}') + r'\end{array}\right\}_{\{f\}}=\left[\begin{array}{' + 'c' * \
                       self._k.obtener_matriz().shape[1] + '}'
        texto_latex += _generar_matrix(self._k.obtener_matriz(),
                                       '{:G}') + r'\end{array}\right]_{[k]}\cdot\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}'
        return '$' + texto_latex + '$'

    def __repr__(self):
        """Overload del método __repr__

        Returns
        -------
        Muestra el nombre del elemento
        """
        #self.mostrar_sistema()
        return 'TriangularCST: ' + self.nombre

    def __str__(self):
        """Overload del método __str__
        Returns
        -------
        Información del elemento
        """
        return 'TriangularCST: ' + self.nombre

    def mostrar_sistema(self, reducida: bool = False):
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(reducida), dtype=object).reshape(-1,1)
        vec_f = np.array(self._obtener_etiquetas_fuerzas(reducida), dtype=object).reshape(-1,1)
        if es_notebook():
            texto_latex = r'\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_f,
                                           '{:}') + r'\end{array}\right\}_{\{f\}}=\left[\begin{array}{' + 'c' * \
                           self._k.obtener_matriz(reducida).shape[1] + '}'
            texto_latex += _generar_matrix(self._k.obtener_matriz(reducida),
                                           '{:G}') + r'\end{array}\right]_{[k]}\cdot\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}'
            display(Math(texto_latex))
        else:
            return np.array2string(self._k.obtener_matriz(reducida),
                                   formatter={'float_kind': lambda x: '{:}'.format(x)})

    def _obtener_etiquetas_fuerzas(self, reducida: bool = False):
        etq = [nodo.grados_libertad[gl].label_fuerza + '^{(' + self.nombre + ')}_{' + nodo.nombre + gl + '}' for nodo
               in [self._nodo_i, self._nodo_j, self._nodo_m] for gl in self._k.grados if
               not reducida or nodo.grados_libertad[gl].valor]
        return etq

    def _calcular_esfuerzos(self) -> np.array:
        return np.matmul(np.matmul(self._D, self._B), self._obtener_desplazamientos())

    def _calcular_esfuerzos_principales(self) -> list:
        esfuerzos = self._calcular_esfuerzos()
        s_x = esfuerzos[0, 0]
        s_y = esfuerzos[1, 0]
        t_xy = esfuerzos[2, 0]
        a = np.sqrt(((s_x - s_y) / 2) ** 2 + t_xy ** 2)
        s_1 = (s_x + s_y) / 2 + a
        s_2 = (s_x + s_y) / 2 - a
        if s_x == s_y:
            teta = 45
        else:
            teta = np.degrees(0.5 * np.arctan(2 * t_xy / (s_x - s_y)))
        return [s_1, s_2, teta]

    def esfuerzos(self):
        esfuerzos = self._calcular_esfuerzos()
        if es_notebook():
            indice = ['$' + label + '$' for label in [r'\sigma_{x}', r'\sigma_{y}', r'\tau_{xy}']]
            return tabulate({'Esfuerzos': esfuerzos}, headers='keys', showindex=indice, tablefmt='html')
        else:
            print(esfuerzos)
            return esfuerzos

    def esfuerzos_principales(self):
        s_principales = self._calcular_esfuerzos_principales()
        if es_notebook():
            indice = ['$' + label + '$' for label in [r'\sigma_{max}', r'\sigma_{min}', r'\theta_{p}']]
            return tabulate({'Esfuerzos Principales': s_principales}, headers='keys', showindex=indice, tablefmt='html')
        else:
            print(s_principales)
            return s_principales

    def _calcular_esfuerzo_von_mises(self) -> float:
        s_principales = self._calcular_esfuerzos_principales()
        s_1, s_2, a = s_principales
        s_3 = 0
        return np.sqrt((s_1 - s_2) ** 2 + (s_2 - s_3) ** 2 + (s_3 - s_1) ** 2) / np.sqrt(2)

    def esfuerzo_von_mises(self):
        s_vm = self._calcular_esfuerzo_von_mises()
        if es_notebook():
            indice = [r'$\sigma_{vm}$']
            return tabulate({'Esfuerzo de Von Mises': [s_vm]}, headers='keys', showindex=indice, tablefmt='html')
        else:
            print(s_vm)
            return s_vm

    def _obtener_desplazamientos(self) -> np.ndarray:
        desplazamiento = None
        for item in self._k.lista_nodos:
            d_i = [d.desplazamiento for d in item.grados_libertad.values() if d.gl in self._k.grados]
            if desplazamiento is None:
                desplazamiento = d_i
            else:
                desplazamiento = np.hstack((desplazamiento, d_i))
        return np.array(desplazamiento).reshape(-1,1)
