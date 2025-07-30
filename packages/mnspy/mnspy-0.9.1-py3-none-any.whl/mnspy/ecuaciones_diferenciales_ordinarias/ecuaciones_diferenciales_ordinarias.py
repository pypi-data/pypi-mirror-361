from mnspy.utilidades import es_notebook
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
plt.rcParams.update(plt.rcParamsDefault)

class EcuacionesDiferencialesOrdinarias:
    """
    Clase base para las demás clases que implementan métodos para la solución de ecuaciones diferenciales ordinarias.

    Attributes
    ----------
    _etiquetas: dict[str:list[str], str: bool]
        diccionario con etiquetas de la solución
        key: 'label' contiene una lista de etiquetas de la solución
        key: 'es_latex' un boleano que define si el string es en formato Latex o no
    _f: callable
        ecuación diferencail ordinaria que se va a solucionar (dy/dx=f(x,y)
    _h: float
        paso de la iteración, el valor en que aumenta el x
    _sol_exacta: callable
        solución exacta de la ecuación diferencia, solo es usada en la gráfica para comparar
    x: ndarray
        array con los datos de la variable independiente, creado apartir del x inicial, el x final y el paso
    _x_f: float
        valor del x final
    _x_i: float
        valor de x inicial
    _y_i:float
        condición de frontera, valor de y_i para un valor de x_i
    y: ndarray
        array con los datos de la variable dependiente, corresponde a la solución de la ecuación diferencial
    """
    def __init__(self, f: callable, x_i: float, x_f: float, y_i: float, h: float, sol_exacta: callable = None):
        """Constructor de la clase EcuacionesDiferencialesOrdinarias

        Parameters
        ----------
        f: callable
            ecuación diferencail ordinaria que se va a solucionar (dy/dx=f(x,y)
        x_i: float
            valor de x inicial
        x_f: float
            valor del x final
        y_i: float
            condición de frontera, valor de y_i para un valor de x_i
        h: float
            paso de la iteración, el valor en que aumenta el x
        sol_exacta: callable
            solución exacta de la ecuación diferencia, solo es usada en la gráfica para comparar

        Methods
        -------
        graficar():
            presenta la solución gráfica del sistema de ecuaciones, solo aplica para un sistema de 2x2


        solucion():
            Presenta los resultados de la solución del sistema de ecuaciones
        """
        self._f = f
        self._x_i = x_i
        self._x_f = x_f
        self._y_i = y_i
        self._h = h
        self._sol_exacta = sol_exacta
        self.x = np.arange(self._x_i, self._x_f + self._h, self._h)
        self.y = np.zeros(len(self.x))
        self._etiquetas = None
        plt.ioff()  # deshabilitada interactividad matplotlib

    def ajustar_etiquetas(self, etiquetas: list, es_latex: bool = True):
        """Ajusta el nombre de las etiquetas de la solución

        Parameters
        ----------
        etiquetas: list[str]
            Diccionario con etiquetas de la solución
        es_latex: bool
            Un boleano que define si el string es en formato Latex o no

        Returns
        -------
        None
        """
        self._etiquetas = {'label': etiquetas, 'es_latex': es_latex}

    def solucion(self):
        """Muestra la solución del de la ecuación diferencial de forma discreta

        Returns
        -------
        Tabla de resultados usando el paquete tabulate
        """
        if es_notebook():
            if self._etiquetas is None:
                tabla = {'x': self.x, 'y': self.y}
            else:
                if self._etiquetas['es_latex']:
                    tabla = {'$' + self._etiquetas['label'][0] + '$': self.x,
                             '$' + self._etiquetas['label'][1] + '$': self.y}
                else:
                    tabla = {self._etiquetas['label'][0]: self.x, self._etiquetas['label'][1]: self.y}
            if self._sol_exacta is not None:
                tabla['Solución exacta'] = self._sol_exacta(self.x)
            return tabulate(tabla, tablefmt='html', headers='keys')
        else:
            if self._etiquetas is None:
                tabla = {'x': self.x, 'y': self.y}
            else:
                tabla = {self._etiquetas['label'][0]: self.x, self._etiquetas['label'][1]: self.y}
            if self._sol_exacta is not None:
                tabla['Solución Exacta'] = self._sol_exacta(self.x)
            print(tabulate(tabla, tablefmt='simple', headers='keys'))

    def _graficar_datos(self) -> None:
        """
        Presenta la gráfica de la solución exacta si fue ingresada al crear el objeto

        Returns
        -------
        Gráfica de datos y solución exacta con el paquete matplotlib
        """
        if self._sol_exacta is not None:
            x = np.linspace(self._x_i, self._x_f, 100)
            y = self._sol_exacta(x)
            plt.plot(x, y, c='b', lw=2, label='Solución Exacta')
        plt.grid()
        plt.legend()
        plt.show()
