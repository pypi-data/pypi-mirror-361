from mnspy.utilidades import es_notebook, _generar_matrix, _formato_float_latex
import numpy as np
from IPython.display import display, Math
import sympy as sp

TOL_CERO = 1E-10
FORMATO_NUM = '{:.10g}'
sp.init_printing(use_latex=True)


def longitud(p1: tuple[float, float, float], p2: tuple[float, float, float]) -> float:
    """
    Retorna la distancia entre dos puntos en el espacio

    Parameters
    ----------
    p1: tuple[float, float, float]
        definición del primer punto como tupla de tres floats
    p2: tuple[float, float, float]
        definición del segundo punto como tupla de tres floats

    Returns
    -------
    La distancia entre los dos puntos como float

    """
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2)


class GradoLibertad:
    """Clase para la implementación de grados de libertad.

    Attributes
    ----------
    desplazamiento: float
        desplazamiento o rotación del nodo según el grado de libertad
    fuerza: float
        Fuerza o momento en el nodo según el grado de libertad
    gl: str
        Nombre del grado de libertad, puede ser 'x', 'y', 'z', 'eje_x', 'eje_y', 'eje_z'
    label_desplazamiento: str
        Etiqueta del desplazamiento de acuerdo a su grado de libertad
    label_fuerza: str
        Etiqueta de la fuerza de acuerdo a su grado de libertad
    label_reaccion: str
        Etiqueta de la reacción de acuerdo a su grado de libertad
    reaccion: float
        Fuerza o momento de reacción en el nodo según el grado de libertad
    valor: bool
        Establece el estado del grado de libertad, si es True se puede desplazar en ese grado de libertad,
        en caso contrario el grado de libertad es fijo
    """

    def __init__(self, gl: str, estado: bool = False):
        """Constructor de la clase GradoLibertad

        Parameters
        ----------
        gl: str
            Define el grado de libertad, puede ser 'x', 'y', 'z', 'eje_x', 'eje_y', 'eje_z'

        estado: bool
            Establece el estado del grado de libertad, si es True se puede desplazar en ese grado de libertad,
            en caso contrario el grado de libertad es fijo
        """
        self.gl = gl
        self.valor = estado
        self.label_reaccion = None
        self.reaccion = 0.0 if estado else None
        self.label_fuerza = None
        self.fuerza = 0.0
        self.label_desplazamiento = None
        self.desplazamiento = None if estado else 0.0
        if gl == 'x':
            self.label_desplazamiento = 'u'
        elif gl == 'y':
            self.label_desplazamiento = 'v'
        elif gl == 'z':
            self.label_desplazamiento = 'w'
        elif gl == 'eje_x':
            self.label_desplazamiento = r'\phi'
        elif gl == 'eje_y':
            self.label_desplazamiento = r'\phi'
        elif gl == 'eje_z':
            self.label_desplazamiento = r'\phi'
        else:
            self.label_desplazamiento = '-'

    def __repr__(self):
        """Overload del método __repr__

        Returns
        -------
        Información del grado de libertad en latex para iPython
        """
        return self.__str__()

    #     texto_latex = r'\{' +self.gl +': '
    #     texto_latex += r'm\acute {o}vil' if self.valor else 'fijo'
    #     texto_latex += r'\}'
    #     display(Math(texto_latex))
    #     return ''

    def __str__(self):
        """Overload del método __str__

        Returns
        -------
        Información del grado de libertad en latex para iPython
        """
        texto = 'móvil' if self.valor else 'fijo'
        return texto


class Nodo:
    """Clase para la implementación de Nodo.

    Attributes
    ----------
    nombre: str
        Nombre asignado al nodo
    punto: tuple[float, float, float]
        Punto en el espacio donde se ubica el nodo
    grados_libertad: dict[str, bool]
        Diccionario que relaciona una string (grado de libertad) con su estado (móvil o fijo), los grados de libertad
        pueden ser 'x', 'y', 'z', 'eje_x', 'eje_y', 'eje_z' y el estado puede ser True para móvil y False para fijo
    es_rotula: bool
            Si es pivote se considera que en ese punto el momento es 0 (aplica para vigas)

    Methods
    -------
    agregar_fuerza_externa(carga: float, gl: str):
        Agrega una fuerza externa en el nodo (puede ser fuerza o momento según el grado de libertad), carga corresponde
        al valor y gl al grado de libertad
    ajustar_grado_libertad(gl: str, estado: bool):
        Ajusta el estado de grado de libertad del Nodo

    Examples:
    -------
    from mnspy import Nodo

    n_1 = Nodo('1', 0, 0, grados_libertad={'x': False, 'y': False})
    n_1.agregar_fuerza_externa(80, 'x')
    """

    def __init__(self, nombre: str, x: float = 0.0, y: float = 0.0, z: float = 0.0,
                 grados_libertad: dict[str, bool] = None, es_rotula: bool = False):
        """Constructor de la clase Nodo

        Parameters
        ----------
        nombre: str
            Nombre asignado al nodo
        x: float
            Coordenada x del punto donde se ubica el nodo
        y: float
            Coordenada y del punto donde se ubica el nodo
        z: float
            Coordenada z del punto donde se ubica el nodo
        grados_libertad: dict[str, bool]
            Diccionario que relaciona una string (grado de libertad) con su estado (móvil o fijo), los grados de
            libertad pueden ser 'x', 'y', 'z', 'eje_x', 'eje_y', 'eje_z' y el estado puede ser True para móvil y False para fijo
        """
        self.nombre = nombre
        self.punto = (x, y, z)

        if grados_libertad is None:
            self.grados_libertad = None
        else:
            # Aunque es un diccionario es necesario ordenarlo
            grados_libertad = {g: grados_libertad[g] for g in ['x', 'y', 'z', 'eje_x', 'eje_y', 'eje_z'] if
                               g in grados_libertad.keys()}
            self.grados_libertad = {n: GradoLibertad(n, v) for n, v in grados_libertad.items()}
        self.es_rotula = es_rotula
        self.fuerzas_externas = dict()
        self._tipo_soporte = []

    def get_soporte(self):
        return self._tipo_soporte

    def set_soporte(self, sop: list[int]):
        self._tipo_soporte = sop

    def agregar_fuerza_externa(self, carga: float, gl: str) -> None:
        """Adiciona una fuerza externa (fuerza o momento) al nodo

        Parameters
        ----------
        carga: float
            corresponde al valor de la fuerza o momento
        gl: str
            corresponde al nombre del grado de libertad

        Returns
        -------
        None
        """
        self.grados_libertad[gl].fuerza += carga
        if gl in self.fuerzas_externas.keys():
            self.fuerzas_externas[gl] += carga
        else:
            self.fuerzas_externas[gl] = carga

    def agregar_desplazamiento_inicial(self, delta: float, gl: str) -> None:
        """Adiciona un desplazamiento inicial al nodo

        Parameters
        ----------
        delta: float
            corresponde al valor del desplazamiento
        gl: str
            corresponde al nombre del grado de libertad

        Returns
        -------
        None
        """
        if self.grados_libertad[gl].desplazamiento is None:
            self.grados_libertad[gl].desplazamiento = 0.0
        self.grados_libertad[gl].desplazamiento += delta
        self.grados_libertad[gl].valor = False  # Deber ser restringido

    def ajustar_grado_libertad(self, gl: str, estado: bool) -> None:
        """Ajusta el estado de grado de libertad del Nodo

        Parameters
        ----------
        gl: str
            Define el grado de libertad, puede ser 'x', 'y', 'z', 'eje_x', 'eje_y', 'eje_z'

        estado: bool
            Establece el estado del grado de libertad, si es True se puede desplazar en ese grado de libertad,
            en caso contrario el grado de libertad es fijo

        Returns
        -------
        None
        """
        self.grados_libertad[gl].valor = estado
        self.grados_libertad[gl].reaccion = 0.0 if estado else None
        self.grados_libertad[gl].desplazamiento = None if estado else 0.0

    def __str__(self):
        """Overload del método __str__

        Returns
        -------
        Información del nodo
        """
        return 'Nodo: ' + self.nombre

    def _repr_latex_(self):
        texto_latex = r'\begin{array}{l}'
        texto_latex += 'Nombre &: ' + str(self.nombre) + r'\\'
        texto_latex += 'Punto &:' + str(self.punto) + r'\\'
        if self.grados_libertad is not None:
            texto_latex += 'Grados~de~libertad &: ' + r'\begin{cases}'
            for gl in self.grados_libertad:
                texto_latex += gl + '&: '
                texto_latex += r'm\acute {o}vil' if self.grados_libertad[gl].valor else 'fijo'
                texto_latex += r'\\'
            texto_latex += r'\end{cases}\\'
            texto_latex += 'Fuerzas~externas &: ' + r'\begin{cases}'
            for gl in self.grados_libertad:
                texto_latex += gl + '&: ' + str(self.grados_libertad[gl].fuerza) + r'\\'
            texto_latex += r'\end{cases}\\'
            texto_latex += 'Desplazamientos &: ' + r'\begin{cases}'
            for gl in self.grados_libertad:
                if self.grados_libertad[gl].valor:
                    texto_latex += r'\color{blue}' + gl + '&\color{blue}: ' + str(
                        self.grados_libertad[gl].desplazamiento) + r'\\'
                else:
                    texto_latex += gl + '&: ' + str(self.grados_libertad[gl].desplazamiento) + r'\\'
            texto_latex += r'\end{cases}\\'
            texto_latex += 'Reacciones &: ' + r'\begin{cases}'
            for gl in self.grados_libertad:
                if self.grados_libertad[gl].valor:
                    texto_latex += gl + '&: None' + r'\\'
                else:
                    texto_latex += r'\color{blue}' + gl + '&\color{blue}: ' + str(
                        self.grados_libertad[gl].reaccion) + r'\\'
            texto_latex += r'\end{cases}'
        texto_latex += r'\end{array}'
        return '$' + texto_latex + '$'

    def __repr__(self):
        """Overload del método __repr__

        Returns
        -------
        Información del nodo en latex para iPython
        """
        # texto_latex = r'\begin{array}{l}'
        # texto_latex += 'Nombre &: ' + str(self.nombre) + r'\\'
        # texto_latex += 'Punto &:' + str(self.punto) + r'\\'
        # if self.grados_libertad is not None:
        #     texto_latex += 'Grados~de~libertad &: ' + r'\begin{cases}'
        #     for gl in self.grados_libertad:
        #         texto_latex += gl + '&: '
        #         texto_latex += r'm\acute {o}vil' if self.grados_libertad[gl].valor else 'fijo'
        #         texto_latex += r'\\'
        #     texto_latex += r'\end{cases}\\'
        # if self.grados_libertad is not None:
        #     texto_latex += 'Fuerzas~externas &: ' + r'\begin{cases}'
        #     for gl in self.grados_libertad:
        #         texto_latex += gl + '&: ' + str(self.grados_libertad[gl].fuerza) + r'\\'
        #     texto_latex += r'\end{cases}'
        # texto_latex += r'\end{array}'
        # display(Math(texto_latex))
        return 'Nodo: ' + self.nombre


class Rigidez:
    """Clase para la implementación de Nodo.

    Attributes
    ----------
    grados: list[str]
        Lista de los grados de libertad involucrados
    k: ndarray
        Matriz de rigidez
    lista_nodos: list[Nodo]
        Lista de los nodos involucrados

    Methods
    -------
    mostrar_sistema(reducida: bool):
        Muestra el sistema de ecuaciones generado en forma matricial
    obtener_sistema_reducido():
        Obtiene las matrices y etiquetas del sistema de ecuaciones reducido
    calcular_reacciones(sol_desplazamientos: matrix | ndarray):
        Calcula las reacciones a partir de los desplazamientos suministrados. Los resultados se almacenan
        en cada nodo y es asociado al grado de libertad
    obtener_matriz(reducida: bool):
        Obtiene las matrices y etiquetas del sistema de ecuaciones reducido
    obtener_fuerzas(reducida: bool):
        Obtiene el vector columna de fuerzas
    obtener_desplazamientos(reducida: bool):
        Obtiene el vector columna de desplazamientos
    obtener_etiquetas_desplazamientos(reducida: bool):
        Obtiene la lista de etiquetas de los desplazamientos
    obtener_etiquetas_fuerzas(reducida: bool):
        Obtiene la lista de etiquetas de las fuerzas
    obtener_etiquetas_reacciones(reducida: bool):
        Obtiene la lista de etiquetas de las reacciones
    """

    def __init__(self, k: np.ndarray, lista_nodos: list[Nodo], grados: list[str] = None):
        """Constructor de la clase Rigidez

        Parameters
        ----------
        k: ndarray
            Matriz de rigidez
        lista_nodos: list[Nodo]
            Lista de los nodos involucrados
        grados: list[str]
            Lista de los grados de libertad involucrados
        """
        self.k = k
        self.lista_nodos = lista_nodos
        self.grados = grados

    def __repr__(self):
        """Overload del método __repr__

        Returns
        -------
        Información de la Rigidez nodo en latex para iPython
        """
        vec_d = np.array(self.obtener_etiquetas_desplazamientos(), dtype=object).reshape(-1, 1)
        vec_r = np.array(self.obtener_etiquetas_reacciones(), dtype=object).reshape(-1, 1)
        if es_notebook():
            texto_latex = r'\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_r,
                                           '{:}') + r'\end{array}\right\}_{Reacciones}=\left[\begin{array}{' + 'c' * \
                           self.k.shape[1] + '}'
            texto_latex += _generar_matrix(self.k,
                                           '{:G}') + r'\end{array}\right]_{Rigidez}\cdot\left\{\begin{array}{c}'
            texto_latex += (_generar_matrix(vec_d, '{:}') +
                            r'\end{array}\right\}_{Desplazamientos}-\left\{\begin{array}{c}')
            texto_latex += _generar_matrix(self.obtener_fuerzas(),
                                           '{:}') + r'\end{array}\right\}_{F_{externas}}'
            display(Math(texto_latex))
            return "Sistema de ecuaciones (en azul las incógnitas)"
        else:
            return np.array2string(self.k, formatter={'float_kind': lambda x: '{:}'.format(x)})

    def __add__(self, otro):
        """Overload del comando +

        Parameters
        ----------
        otro: Rigidez
            El otro objeto tipo Rigidez que se sumará

        Returns
        -------
            Objeto tipo Rigidez resultante de la suma
        """
        suma = Rigidez(self.k.copy(), self.lista_nodos.copy())
        for item in otro.lista_nodos:
            if item not in self.lista_nodos:
                suma.k = np.insert(np.insert(suma.k, [suma.k.shape[0]] * len(item.grados_libertad), 0.0, axis=0),
                                   [suma.k.shape[1]] * len(item.grados_libertad), 0.0, axis=1)
                # suma.k = np.hstack((suma.k, np.zeros((suma.k.shape[0], len(item.grados_libertad)))))
                # suma.k = np.vstack((suma.k, np.zeros((len(item.grados_libertad), suma.k.shape[1]))))
                suma.lista_nodos.append(item)
        i_otro = 0
        for item_i in otro.lista_nodos:
            i = 0
            for indice in range(suma.lista_nodos.index(item_i)):
                i += len(suma.lista_nodos[indice].grados_libertad)
            j_otro = 0
            for item_j in otro.lista_nodos:
                j = 0
                for indice in range(suma.lista_nodos.index(item_j)):
                    j += len(suma.lista_nodos[indice].grados_libertad)
                for k_i in otro.grados:
                    for k_j in otro.grados:
                        # suma.k[i + list(item_i.grados_libertad.keys()).index(k_i), j + list(
                        #     item_j.grados_libertad.keys()).index(k_j)] += otro.k[
                        #     i_otro + list(item_i.grados_libertad.keys()).index(k_i), j_otro + list(
                        #         item_j.grados_libertad.keys()).index(k_j)]
                        suma.k[i + list(item_i.grados_libertad.keys()).index(k_i), j + list(
                            item_j.grados_libertad.keys()).index(k_j)] += otro.k[
                            i_otro + otro.grados.index(k_i), j_otro + otro.grados.index(k_j)]
                j_otro += len(otro.grados)
            i_otro += len(otro.grados)
        return suma

    def mostrar_sistema(self, reducida: bool = False):
        """Muestra el sistema de ecuaciones generado en forma matricial

        Parameters
        ----------
        reducida: bool
            Si es True muestra el sistema de ecuaciones generado que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False muestra todo el sistema de ecuaciones generado

        Returns
        -------
        Información del sistema de ecuaciones generado en latex para iPython
        """
        vec_d = np.array(self.obtener_etiquetas_desplazamientos(reducida), dtype=object).reshape(-1, 1)
        vec_r = np.array(self.obtener_etiquetas_reacciones(reducida), dtype=object).reshape(-1, 1)
        if es_notebook():
            texto_latex = r'\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_r,
                                           '{:}') + r'\end{array}\right\}=\left[\begin{array}{' + 'c' * \
                           self.obtener_matriz(reducida).shape[1] + '}'
            texto_latex += _generar_matrix(self.obtener_matriz(reducida),
                                           '{:G}') + r'\end{array}\right]\cdot\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}-\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(self.obtener_fuerzas(reducida),
                                           '{:}') + r'\end{array}\right\}'
            display(Math(texto_latex))
        else:
            return np.array2string(self.obtener_matriz(reducida), formatter={'float_kind': lambda x: '{:}'.format(x)})

    def obtener_sistema_reducido(self) -> tuple[np.ndarray, np.ndarray, list[str]]:
        """Obtiene las matrices y etiquetas del sistema de ecuaciones reducido

        Returns
        -------
        Retorna una Tuple con la matriz de Rigidez reducida (A), el vector columna (b) y  una lista de las
        etiquetas de las variables.
        """
        return self.obtener_matriz(True), self.obtener_fuerzas(True), self.obtener_etiquetas_desplazamientos(True)

    def calcular_reacciones(self, sol_desplazamientos: np.ndarray):
        """Calcula las reacciones a partir de los desplazamientos suministrados. Los resultados se almacenan
        en cada nodo y es asociado al grado de libertad

        Parameters
        ----------
        sol_desplazamientos: matrix | ndarray
            Vector columna con el resultado de los desplazamientos
        Returns
        -------
        None
        """
        indice = 0
        for item in self.lista_nodos:
            for gl in item.grados_libertad.values():
                if gl.valor:
                    gl.desplazamiento = sol_desplazamientos[indice, 0]
                    indice += 1
        reacciones = np.matmul(self.obtener_matriz(), self.obtener_desplazamientos()) - self.obtener_fuerzas()
        indice = 0
        for item in self.lista_nodos:
            for gl in item.grados_libertad.values():
                if not gl.valor:
                    gl.reaccion = reacciones[indice, 0]
                indice += 1

    def obtener_matriz(self, reducida: bool = False) -> np.ndarray:
        """Obtiene la matriz de rigidez

        Parameters
        ----------
        reducida: bool
            Si es True retorna la matriz de rigidez que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False retorna toda la matriz de rigidez

        Returns
        -------
        Retorna una matriz de Rigidez.
        """
        if reducida:
            lista_eliminar = []
            i = 0
            for item in self.lista_nodos:
                if self.grados is None:
                    k = len(item.grados_libertad)
                else:
                    k = len(self.grados)
                for i_gl, gl in enumerate(item.grados_libertad.values()):
                    if not gl.valor:
                        lista_eliminar.append(i + i_gl)
                i += k
            mat_global = np.delete(self.k, lista_eliminar, 0)
            mat_global = np.delete(mat_global, lista_eliminar, 1)
            return mat_global
        else:
            return self.k

    def obtener_fuerzas(self, reducida: bool = False) -> np.ndarray:
        """Obtiene el vector columna de fuerzas

        Parameters
        ----------
        reducida: bool
            Si es True retorna el vector columna de fuerzas que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False retorna todo el vector columna de fuerzas

        Returns
        -------
        Retorna el vector columna de fuerzas.
        """
        fuerza = None
        for item in self.lista_nodos:
            f_i = np.array([[fu.fuerza for fu in item.grados_libertad.values()]]).transpose()
            if fuerza is None:
                fuerza = f_i
            else:
                fuerza = np.vstack((fuerza, f_i))
        if reducida:
            lista_eliminar = []
            i = 0
            for item in self.lista_nodos:
                for i_gl, gl in enumerate(item.grados_libertad.values()):
                    if not gl.valor:
                        lista_eliminar.append(i + i_gl)
                i += len(item.grados_libertad)
            fuerza = np.delete(fuerza, lista_eliminar, 0)
            return fuerza - self.obtener_fuerzas_iniciales_reducidas()  # Se le resta las fuerzas iníciales si hay desplazamiento
        else:
            return fuerza

    def obtener_fuerzas_iniciales_reducidas(self) -> np.ndarray:
        """Obtiene el vector columna de fuerzas inicailes debida a deformaciones previas

        Parameters
        ----------

        Returns
        -------
        Retorna el vector columna de fuerzas iniciales reducidas.
        """
        desplazamiento = None
        for item in self.lista_nodos:
            d_i = np.array(
                [[d.desplazamiento if d.desplazamiento is not None else 0.0 for d in
                  item.grados_libertad.values()]]).transpose()
            if desplazamiento is None:
                desplazamiento = d_i
            else:
                desplazamiento = np.vstack((desplazamiento, d_i))
        d_inicial = np.matmul(self.obtener_matriz(), desplazamiento)
        lista_eliminar = []
        i = 0
        for item in self.lista_nodos:
            for i_gl, gl in enumerate(item.grados_libertad.values()):
                if not gl.valor:
                    lista_eliminar.append(i + i_gl)
            i += len(item.grados_libertad)
        d_inicial = np.delete(d_inicial, lista_eliminar, 0)
        return d_inicial

    def obtener_desplazamientos(self) -> np.ndarray:
        """Obtiene el vector columna de desplazamientos

        Returns
        -------
        Retorna el vector columna de desplazamientos.
        """
        desplazamiento = None
        for item in self.lista_nodos:
            d_i = [d.desplazamiento for d in item.grados_libertad.values()]
            if desplazamiento is None:
                desplazamiento = d_i
            else:
                desplazamiento = np.hstack((desplazamiento, d_i))
        return np.array(desplazamiento).reshape(-1, 1)

    def obtener_etiquetas_desplazamientos(self, reducida: bool = False) -> list[str]:
        """Obtiene la lista de etiquetas de los desplazamientos

        Parameters
        ----------
        reducida: bool
            Si es True retorna la lista de etiquetas de los desplazamientos que involucre solamente incognitas
            de desplazamiento, en caso contrario si es False retorna toda la lista de etiquetas de los desplazamientos

        Returns
        -------
        Retorna la lista de etiquetas de los desplazamientos.
        """
        etiquetas = []
        for item in self.lista_nodos:
            for n, gl in item.grados_libertad.items():
                if reducida and not gl.valor:
                    continue
                if self.grados is not None:
                    if n not in self.grados:
                        continue

                dato = gl.label_desplazamiento + '_{' + item.nombre + '}'
                # dato = dato if gl.desplazamiento is None else dato + '=' + str(gl.desplazamiento)
                dato = dato if gl.desplazamiento is None else dato + '=' + _formato_float_latex(gl.desplazamiento,
                                                                                                TOL_CERO, FORMATO_NUM)
                if gl.valor and es_notebook():
                    etiquetas.append(r'\color{blue}' + dato)
                else:
                    etiquetas.append(dato)
        return etiquetas

    def obtener_etiquetas_fuerzas(self, reducida: bool = False) -> list[str]:
        """Obtiene la lista de etiquetas de las fuerzas

        Parameters
        ----------
        reducida: bool
            Si es True retorna la lista de etiquetas de las fuerzas que involucre solamente incognitas
            de desplazamiento, en caso contrario si es False retorna toda la lista de etiquetas de las fuerzas

        Returns
        -------
        Retorna la lista de etiquetas de las fuerzas.
        """
        etiquetas = []
        for item in self.lista_nodos:
            for n, gl in item.grados_libertad.items():
                if self.grados is not None:
                    if n not in self.grados or (reducida and not gl.valor):
                        continue
                # etiquetas.append(gl.label_fuerzas + '_{' + item.nombre + '}')
                etiquetas.append(gl.label_fuerza)
        return etiquetas

    def obtener_etiquetas_reacciones(self, reducida: bool = False) -> list[str]:
        """Obtiene la lista de etiquetas de las reacciones

        Parameters
        ----------
        reducida: bool
            Si es True retorna la lista de etiquetas de las reacciones que involucre solamente incognitas
            de desplazamiento, en caso contrario si es False retorna toda la lista de etiquetas de las reacciones

        Returns
        -------
        Retorna la lista de etiquetas de las reacciones.
        """
        etiquetas = []
        for item in self.lista_nodos:
            for n, gl in item.grados_libertad.items():
                if reducida and not gl.valor:
                    continue
                if self.grados is not None:
                    if n not in self.grados:
                        continue
                sub = gl.gl if 'eje' not in gl.gl else ''
                dato = gl.label_reaccion + '_{' + item.nombre + sub + '}'
                # dato = dato if gl.valor is None else dato + '=' + str(gl.valor)
                if gl.valor:
                    etiquetas.append(r'\cancel{' + dato + '}')
                else:
                    # dato = dato if gl.reaccion is None else dato + '=' + str(gl.reaccion)
                    dato = dato if gl.reaccion is None else dato + '=' + _formato_float_latex(gl.reaccion, TOL_CERO,
                                                                                              FORMATO_NUM)
                    etiquetas.append(r'\color{blue}' + dato)
        return etiquetas


class Elemento:
    """Clase para la implementación de Elemento.

    Attributes
    ----------
    _L: float
        Longitud del elemento (elemento lineal)
    _fuerzas_i: ndarray
        vector columna de las fuerzas en el nodo i
    _fuerzas_j: ndarray
        vector columna de las fuerzas en el nodo j
    _fuerzas_m: ndarray
        vector columna de las fuerzas en el nodo m
    _k: Rigidez
        Objeto relacionado con la matriz de rigidez
    _nodo_i: Nodo
        Nodo inicial del elemento (elemento lineal)
    _nodo_j: Nodo
        Nodo final del elemento (elemento lineal)
    _nodo_m: Nodo
        Tercer nodo(elemento Triangular)
    nombre: str
            Nombre asignado al Elemento

    Methods
    -------
    obtener_sistema_reducido
    obtener_fuerzas
    calcular_reacciones
    mostrar_sistema
    mostrar_matriz_rigidez

    """

    def __init__(self, nombre: str, nodo_i: Nodo = None, nodo_j: Nodo = None, nodo_m: Nodo = None):
        """Constructor de la clase Elemento

        Parameters
        ----------
        nombre: str
            Nombre asignado al Elemento
        nodo_i: Nodo
            Nodo inicial del elemento (elemento lineal)
        nodo_j: Nodo
            Nodo final del elemento (elemento lineal)
        nodo_m: Nodo
            Tercer nodo(elemento Triangular)
        """
        self.nombre = nombre
        self._k = None
        self._fuerzas_i = None
        self._fuerzas_j = None
        # Si hay una rótula
        self._fuerzas_i_rot = None
        self._fuerzas_j_rot = None

        self._fuerzas_m = None
        self._nodo_i = nodo_i
        self._nodo_j = nodo_j
        self._nodo_m = nodo_m
        if self._nodo_i is None or self._nodo_j is None:
            self._L = None
        else:
            self._L = longitud(nodo_i.punto, nodo_j.punto)
        self._lista_elementos = None
        self._c = None
        self._s = None
        # self._tol_cero_etiquetas = 1E-10

    def _repr_latex_(self):
        vec_d = np.array(self.obtener_rigidez().obtener_etiquetas_desplazamientos(),
                         dtype=object).reshape(-1, 1)
        vec_r = np.array(self.obtener_rigidez().obtener_etiquetas_reacciones(), dtype=object).reshape(-1, 1)
        texto_latex = r'\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_r, '{:}') + r'\end{array}\right\}_{\{R\}}+\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(self.obtener_rigidez().obtener_fuerzas(),
                                       '{:}') + r'\end{array}\right\}_{\{F_{ext.}\}}=\left[\begin{array}{' + 'c' * \
                       self.obtener_rigidez().obtener_matriz().shape[1] + '}'
        texto_latex += _generar_matrix(self.obtener_rigidez().obtener_matriz(),
                                       '{:G}') + r'\end{array}\right]_{[K]}\cdot\left\{\begin{array}{c}'
        texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}'
        return '$' + texto_latex + '$'

    def __repr__(self):
        """Overload del método __repr__

        Returns
        -------
        Muestra el sistema de ecuaciones en forma matricial y en latex para iPython
        """
        # self.mostrar_sistema()
        # return "{R}\t-> Reacciones\n{Fext.}\t-> Fuerzas externas\n[K]\t-> Matriz de rigidez global\n{d}\t-> Deformaciones"
        return 'Elemento: ' + self.nombre

    def __str__(self):
        """Overload del método __str__

        Returns
        -------
        Información del elemento
        """
        return 'Elemento: ' + self.nombre

    def __add__(self, otro):
        """Overload del comando +

        Parameters
        ----------
        otro: Elemento
            El otro objeto tipo Elemento que se sumará

        Returns
        -------
            Objeto tipo Elemento resultante de la suma
        """
        suma = Elemento(self.nombre + '+' + otro.nombre)
        if self._lista_elementos is None:
            lista_1 = [self]
            temp_k = Rigidez(self._k.k.copy(), self._k.lista_nodos, self._k.grados)
            j = 0
            for nodo in self.get_lista_nodos():
                if len(self._k.grados) < len(nodo.grados_libertad.keys()):
                    for i, item in enumerate(nodo.grados_libertad.keys()):
                        if item not in self._k.grados:
                            temp_k.k = np.insert(np.insert(temp_k.k, j + i, 0.0, axis=0), j + i, 0.0, axis=1)
                j += len(nodo.grados_libertad.keys())
            suma._k = temp_k + otro._k
        else:
            lista_1 = self._lista_elementos
            suma._k = self._k + otro._k
        if otro._lista_elementos is None:
            lista_2 = [otro]
        else:
            lista_2 = otro._lista_elementos
        suma._lista_elementos = lista_1 + lista_2
        return suma

    # def obtener_ecuacion_cortante(self):
    #     x = sp.symbols('x')
    #     V = sp.Function('V')(x)
    #     if self._lista_elementos is not None:
    #         arg = []
    #         for elemento in self._lista_elementos:
    #             arg += list(elemento.obtener_ecuacion_cortante().args[1].args)
    #         return sp.Eq(V, sp.Piecewise(*arg))
    #
    # def obtener_ecuacion_momento(self):
    #     x = sp.symbols('x')
    #     M = sp.Function('M')(x)
    #     if self._lista_elementos is not None:
    #         arg = []
    #         for elemento in self._lista_elementos:
    #             arg += list(elemento.obtener_ecuacion_momento().args[1].args)
    #         return sp.Eq(M, sp.Piecewise(*arg))
    #
    # def obtener_ecuacion_angulo(self):
    #     x = sp.symbols('x')
    #     phi = sp.Function('phi')(x)
    #     if self._lista_elementos is not None:
    #         arg = []
    #         for elemento in self._lista_elementos:
    #             arg += list(elemento.obtener_ecuacion_angulo().args[1].args)
    #         return sp.Eq(phi, sp.Piecewise(*arg))
    #
    # def obtener_ecuacion_deflexion(self):
    #     x = sp.symbols('x')
    #     y = sp.Function('y')(x)
    #     if self._lista_elementos is not None:
    #         arg = []
    #         for elemento in self._lista_elementos:
    #             arg += list(elemento.obtener_ecuacion_deflexion().args[1].args)
    #         return sp.Eq(y, sp.Piecewise(*arg))

    # def diagrama_de_cortante(self):
    #     if self._lista_elementos is not None:
    #         for elemento in self._lista_elementos:
    #             l_x, l_y, l_z = elemento.obtener_arrays_cortantes()
    #             plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.9)
    #             for i in l_z:
    #                 pos_y = 5  # offset escritura
    #                 val_x, val_y = i
    #                 if val_y < 0:
    #                     pos_y = -5
    #                 plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
    #                              textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
    #         plt.grid()
    #         plt.title('Diagrama de cortantes')
    #         plt.xlabel('$x$')
    #         plt.ylabel('$V$')
    #         plt.show()
    #
    # def diagrama_de_momento(self):
    #     if self._lista_elementos is not None:
    #         for elemento in self._lista_elementos:
    #             l_x, l_y, l_z = elemento.obtener_arrays_momentos()
    #             plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.9)
    #             for i in l_z:
    #                 pos_y = 5  # offset escritura
    #                 val_x, val_y = i
    #                 if val_y < 0:
    #                     pos_y = -5
    #                 plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
    #                              textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
    #         plt.grid()
    #         plt.title('Diagrama de momentos')
    #         plt.xlabel('$x$')
    #         plt.ylabel('$M$')
    #         plt.show()
    #
    # def diagrama_de_giro(self):
    #     if self._lista_elementos is not None:
    #         for elemento in self._lista_elementos:
    #             l_x, l_y, l_z = elemento.obtener_arrays_angulos()
    #             plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.9)
    #             for i in l_z:
    #                 pos_y = 5  # offset escritura
    #                 val_x, val_y = i
    #                 if val_y < 0:
    #                     pos_y = -5
    #                 plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
    #                              textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
    #         plt.grid()
    #         plt.title('Diagrama de giros')
    #         plt.xlabel('$x$')
    #         plt.ylabel(r'$\phi$')
    #         plt.show()
    #
    # def diagrama_de_deflexion(self):
    #     if self._lista_elementos is not None:
    #         for elemento in self._lista_elementos:
    #             l_x, l_y, l_z = elemento.obtener_arrays_deflexion()
    #             plt.fill_between(l_x, l_y, color='teal', lw=0.5, alpha=0.9)
    #             for i in l_z:
    #                 pos_y = 5  # offset escritura
    #                 val_x, val_y = i
    #                 if val_y < 0:
    #                     pos_y = -5
    #                 plt.annotate(f'${float(val_y):.4G}$', (val_x, val_y), c='black',
    #                              textcoords="offset points", xytext=(0, pos_y), va='center', ha='center', fontsize=8)
    #         plt.grid()
    #         plt.title('Diagrama de deflexión')
    #         plt.xlabel('$x$')
    #         plt.ylabel('$y$')
    #         plt.show()

    def get_lista_nodos(self):
        return self._k.lista_nodos

    def get_nodo_inicial(self) -> Nodo:
        return self._nodo_i

    def get_nodo_final(self) -> Nodo:
        return self._nodo_j

    def get_nodo_medio(self) -> Nodo:
        return self._nodo_m

    def get_seno(self) -> float:
        return self._s

    def get_coseno(self) -> float:
        return self._c

    def get_longitud(self) -> float:
        return self._L

    def get_matriz_rigidez(self):
        return self._k.obtener_matriz()

    def get_matriz_rigidez_local(self):
        return self.get_matriz_rigidez()

    def get_matriz_T(self):
        return np.eye(self.get_matriz_rigidez().shape[0])

    def obtener_rigidez(self) -> Rigidez:
        return self._k

    # def obtener_sistema_reducido(self) -> tuple[np.ndarray, np.ndarray, list[str]]:
    #     """Obtiene las matrices y etiquetas del sistema de ecuaciones reducido
    #
    #     Returns
    #     -------
    #     Retorna una Tuple con la matriz de Rigidez reducida (A), el vector columna (b) y  una lista de las
    #     etiquetas de las variables.
    #     """
    #     return self._k.obtener_sistema_reducido()

    def _obtener_fuerzas(self, reducida: bool = False) -> np.ndarray:
        """Obtiene el vector columna de fuerzas

        Parameters
        ----------
        reducida: bool
            Si es True retorna el vector columna de fuerzas que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False retorna todo el vector columna de fuerzas

        Returns
        -------
        Retorna el vector columna de fuerzas.
        """
        if self._nodo_i is None or self._nodo_j is None:
            self._k.obtener_fuerzas(reducida)
        fuerza = np.vstack((self._fuerzas_i, self._fuerzas_j))
        if reducida:
            lista_eliminar = []
            i = 0
            for item in [self._nodo_i, self._nodo_j]:
                for j, gl in enumerate(self._k.grados):
                    if not item.grados_libertad[gl].valor:
                        lista_eliminar.append(i + j)
                i += len(self._k.grados)
            fuerza = np.delete(fuerza, lista_eliminar, 0)
            return fuerza
        else:
            return fuerza

    def _obtener_fuerzas_por_rotula(self, reducida: bool = False) -> np.ndarray:
        """Obtiene el vector columna de fuerzas debido a la rotula

        Parameters
        ----------
        reducida: bool
            Si es True retorna el vector columna de fuerzas que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False retorna todo el vector columna de fuerzas

        Returns
        -------
        Retorna el vector columna de fuerzas.
        """
        fuerza = np.vstack((self._fuerzas_i_rot, self._fuerzas_j_rot))
        if reducida:
            lista_eliminar = []
            i = 0
            for item in [self._nodo_i, self._nodo_j]:
                for j, gl in enumerate(self._k.grados):
                    if not item.grados_libertad[gl].valor:
                        lista_eliminar.append(i + j)
                i += len(self._k.grados)
            fuerza = np.delete(fuerza, lista_eliminar, 0)
            return fuerza
        else:
            return fuerza

    def mostrar_sistema(self, reducida: bool = False):
        """Muestra el sistema de ecuaciones generado en forma matricial

        Parameters
        ----------
        reducida: bool
            Si es True muestra el sistema de ecuaciones generado que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False muestra todo el sistema de ecuaciones generado

        Returns
        -------
        Información del sistema de ecuaciones generado en latex para iPython
        """
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(reducida), dtype=object).reshape(-1, 1)
        vec_r = np.array(self._k.obtener_etiquetas_reacciones(reducida), dtype=object).reshape(-1, 1)
        if es_notebook():
            texto_latex = r'\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_r, '{:}') + r'\end{array}\right\}_{\{R\}}+\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(self._k.obtener_fuerzas(reducida),
                                           '{:}') + r'\end{array}\right\}_{\{F_{ext.}\}}=\left[\begin{array}{' + 'c' * \
                           self._k.obtener_matriz(reducida).shape[1] + '}'
            texto_latex += _generar_matrix(self._k.obtener_matriz(reducida),
                                           '{:G}') + r'\end{array}\right]_{[K]}\cdot\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}_{\{d\}}'
            display(Math(texto_latex))
        else:
            return np.array2string(self._k.obtener_matriz(reducida),
                                   formatter={'float_kind': lambda x: '{:}'.format(x)})

    def mostrar_matriz_rigidez(self, reducida: bool = False):
        """Obtiene la matriz de rigidez

        Parameters
        ----------
        reducida: bool
            Si es True retorna la matriz de rigidez que involucre solamente incognitas de desplazamiento,
            en caso contrario si es False retorna toda la matriz de rigidez

        Returns
        -------
        Retorna una matriz de Rigidez.
        """
        vec_d = np.array(self._k.obtener_etiquetas_desplazamientos(reducida), dtype=object).reshape(-1, 1)
        if es_notebook():
            texto_latex = r'\left[\begin{array}{' + 'c' * self._k.obtener_matriz(reducida).shape[1] + '}'
            texto_latex += _generar_matrix(self._k.obtener_matriz(reducida),
                                           '{:G}') + r'\end{array}\right]\cdot\left\{\begin{array}{c}'
            texto_latex += _generar_matrix(vec_d, '{:}') + r'\end{array}\right\}'
            display(Math(texto_latex))
        else:
            return np.array2string(self._k.obtener_matriz(reducida),
                                   formatter={'float_kind': lambda x: '{:}'.format(x)})

    def _obtener_cargas(self) -> dict:
        return {}

    def _obtener_arrays_cortantes(self, n_puntos):
        return [], [], []

    def _obtener_arrays_momentos(self, n_puntos):
        return [], [], []

    def _obtener_arrays_angulos(self, n_puntos):
        return [], [], []

    def _obtener_arrays_deflexion(self, n_puntos):
        return [], [], []


def main():
    from resorte import Resorte
    from viga import Viga
    n_1 = Nodo('1', 0, grados_libertad={'y': False, 'eje_z': False})
    n_2 = Nodo('2', 3, grados_libertad={'y': False, 'eje_z': True})
    n_3 = Nodo('3', 6, grados_libertad={'y': True, 'eje_z': True})
    n_4 = Nodo('4', 6, grados_libertad={'y': True})
    # n_3.fuerza=array([[-50],[0]])
    el_1 = Viga('1', n_1, n_2, 210E6, 2E-4)
    el_2 = Viga('2', n_2, n_3, 210E6, 2E-4)
    r_1 = Resorte('3', n_3, n_4, 200, 'y')

    sol = el_1 + el_2 + r_1
    print(sol.mostrar_matriz_rigidez())

    n_1 = Nodo('1', 0, grados_libertad={'y': False, 'eje_z': False})
    n_2 = Nodo('2', 3, grados_libertad={'y': True, 'eje_z': True})
    n_3 = Nodo('3', 6, grados_libertad={'y': False, 'eje_z': True})
    n_4 = Nodo('4', 9, grados_libertad={'y': True, 'eje_z': True})
    n_5 = Nodo('5', 12, grados_libertad={'y': False, 'eje_z': False})

    e_1 = Viga('1', n_1, n_2, E=210E6, I=2E-4)
    e_2 = Viga('2', n_2, n_3, E=210E6, I=2E-4)
    e_3 = Viga('3', n_3, n_4, E=210E6, I=2E-4)
    e_4 = Viga('4', n_4, n_5, E=210E6, I=2E-4)

    n_2.agregar_fuerza_externa(-50, 'y')
    n_4.agregar_fuerza_externa(-50, 'y')

    mg = e_1 + e_2 + e_3 + e_4
    print(mg.mostrar_matriz_rigidez())


if __name__ == '__main__':
    main()
