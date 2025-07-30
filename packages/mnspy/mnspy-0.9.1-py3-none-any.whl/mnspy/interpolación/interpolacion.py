import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Interpolacion:
    """
    Clase base para las demás clases que implementan métodos de Interpolación.

    Attributes
    ----------
    _x: ndarray
        array con los datos de la variable independiente
    _y: ndarray
        array con los datos de la variable dependiente
    _n: int
        número de puntos de interpolación

    Methods
    -------
    _graficar_datos():
        presenta la gráfica de los puntos a interpolar por medio de matplotlib

    """

    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Clase para la implementación de la interpolación de datos

        Parameters
        ----------
        x: ndarray
            Array con los datos de la variable independiente
        y: ndarray
            Array con los datos de la variable dependiente
        """
        self._x = x
        self._y = y
        self._n = len(self._x)
        if len(self._y) != self._n:
            print('la longitud de x e y deben ser iguales')
        plt.ioff()  # deshabilitada interactividad matplotlib

    def _graficar_datos(self) -> None:
        """
        Presenta la gráfica de los puntos a interpolar por medio de matplotlib

        Returns
        -------
        Gráfica de datos con el paquete matplotlib
        """
        plt.scatter(self._x, self._y, marker='o', c='b', lw=1, label='datos')
        plt.grid()
        plt.legend()
        plt.show()
