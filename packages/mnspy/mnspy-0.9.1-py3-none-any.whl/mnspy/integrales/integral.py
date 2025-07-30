import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Integral:
    """
    Clase base para las demás clases que implementan métodos de Integrales.

    Attributes
    ----------
    _x: ndarray
        array con los datos de la variable independiente para una integral de tipo discreto
    _y: ndarray
        array con los datos de la variable dependiente para una integral de tipo discreto
    _n: int
        número de puntos para una integral de tipo discreto, o el número de segmentos en que se dividirá la función en
        para las integrales de Newton-Cotes
    _a: float
        valor inicial de la integral para la variable independiente
    _b: float
        valor final de la integral para la variable independiente
    _f: callable
        función a la que se integrará

    Methods
    -------
    _graficar_datos():
        presenta la gráfica de los puntos a interpolar por medio de matplotlib
    """
    def __init__(self, x: np.ndarray = None, y: np.ndarray = None, f: callable = None, a: float = None,
                 b: float = None, n: int = 100):
        """Constructor de la clase base Integral

        Parameters
        ----------
        x: ndarray
            array con los datos de la variable independiente para una integral de tipo discreto
        y: ndarray
            array con los datos de la variable dependiente para una integral de tipo discreto
        f: callable
            función a la que se integrará
        a: float
            valor inicial de la integral para la variable independiente
        b: float
            valor final de la integral para la variable independiente
        n: int
            número de puntos para una integral de tipo discreto, o el número de segmentos en que se dividirá la función en
            para las integrales de Newton-Cotes
        """
        self._tipo = 'ninguno'
        if x is not None and y is not None:
            self._tipo = 'discreto'
            self._x = x
            self._y = y
            self._n = len(x)
        elif f is not None and a is not None and b is not None:
            self._tipo = 'función'
            self._f = f
            self._a = a
            self._b = b
            self._n = n
        self.integral = 0
        plt.ioff()  # deshabilitada interactividad matplotlib

    def _graficar_datos(self) -> None:
        """
        Presenta la gráfica de los puntos o función a integar por medio de matplotlib

        Returns
        -------
        Gráfica los puntos o función con el paquete matplotlib
        """
        if self._tipo == 'discreto':
            plt.scatter(self._x, self._y, marker='o', c='b', lw=1, label='Puntos')
        elif self._tipo == 'función':
            x = np.linspace(self._a, self._b)
            y = self._f(x)
            plt.plot(x, y, c='b', lw=2, label='Función')
        plt.grid()
        plt.legend()
        plt.show()
