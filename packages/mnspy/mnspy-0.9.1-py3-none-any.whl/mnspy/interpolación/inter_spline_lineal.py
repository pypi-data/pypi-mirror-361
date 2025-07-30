from mnspy.interpolación import Interpolacion
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Math
plt.rcParams.update(plt.rcParamsDefault)

class SplineLineal(Interpolacion):
    """Clase para la implementación de la interpolación Spline Lineal.

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
    evaluar(x: float):
        Evalua el la interpolación por el método Spline Lineal, para el valor suministrado
    obtener_polinomio():
        Calcula el polinomio que pasa por los puntos de los datos de la interpolación
    graficar():
        Grafica el polinomio resultante de la interpolación
    _graficar_datos():
        presenta la gráfica de los puntos a interpolar por medio de matplotlib


    Examples
    -------
    from mnspy import SplineLineal
    import numpy as np

    T = np.array([-40., 0., 20., 50., 100, 150, 200, 250, 300, 400, 500])
    rho = np.array([1.52, 1.29, 1.2, 1.09, 0.95, 0.84, 0.75, 0.68, 0.62, 0.53, 0.46])
    sc = SplineLineal(T, rho)
    print(sc.evaluar(350))
    sc.graficar(350)

    x = np.array([1., 4., 5, 6.])
    y = np.log(x)
    inter = SplineLineal(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)
    """
    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Clase para la implementación de la interpolación Spline Lineal

        Parameters
        ----------
        x: ndarray
            Array con los datos de la variable independiente
        y: ndarray
            Array con los datos de la variable dependiente
        """
        super().__init__(x, y)

    def evaluar(self, x: float) -> float | str:
        """Evalua el la interpolación por el método de Spline Lineal, para el valor suministrado

        Parameters
        ----------
        x: float
            valor x de la variable independiente de a la cual se intepolará

        Returns
        -------
        Un float con el valor interpolado
        """
        if (x < self._x[0]) or (x > self._x[self._n - 1]):
            return "Valor de entrada fuera del rango de la tabla"
        i_0 = 0
        for i in range(self._n):
            if x == self._x[i]:
                return float(self._y[i])
            elif self._x[i] > x:
                i_0 = i - 1
                break
        y_int = self._y[i_0] + (x - self._x[i_0]) * (self._y[i_0 + 1] - self._y[i_0]) / (
                    self._x[i_0 + 1] - self._x[i_0])
        return float(y_int)

    def obtener_polinomio(self):
        """
        Calcula el polinomio que pasa por los puntos de los datos de la interpolación

        Returns
        -------
        Retorna la lista de polinomios de grado 3 que pasa por los puntos de los datos de la interpolación
        """
        texto_latex = r'\begin{cases}'
        for i in range(self._n - 1):
            m = (self._y[i + 1] - self._y[i]) / (self._x[i + 1] - self._x[i])
            b = self._y[i] - m * self._x[i]
            sb_0 = '+'
            if b < 0:
                sb_0 = ''
            if m != 0:
                texto_latex += '{:.8G}'.format(m) + 'x'
            if b != 0:
                texto_latex += sb_0 + '{:.8G}'.format(b)
            if i == self._n - 2:
                texto_latex += r' & ' + str(self._x[i]) + r' \leq  x \leq ' + str(self._x[i + 1]) + r'\\'
            else:
                texto_latex += r' & ' + str(self._x[i]) + r' \leq  x < ' + str(self._x[i + 1]) + r'\\'
        texto_latex += r'\end{cases}'
        return display(Math(texto_latex))

    def graficar(self, x: float) -> None:
        """
        Grafica los polinomios resultantes de la interpolación Spline Lineal

        Parameters
        ----------
        x: float
            valor x de la variable independiente a la que se interpolará y mostrará en la gráfica.

        Returns
        -------
        Grafica de la interpolación realizada usando el paquete de matplotlib
        """
        y = self.evaluar(x)
        x_min = float(min(self._x))
        x_max = float(max(self._x))
        x_list = np.linspace(x_min, x_max, 100)
        y_list = list(map(self.evaluar, x_list))
        plt.scatter(x, y, c='r', lw=2, label='Interpolación Spline Lineal')
        plt.plot(x_list, y_list, linestyle='dashed', c='k', lw=1, label='Polinomio')
        plt.annotate('$(' + str(x) + r',\,' + str(y) + ')$', (x, y), c='r', alpha=0.9, textcoords="offset points",
                     xytext=(0, 10), ha='center')
        super()._graficar_datos()


def main():
    T = np.array([-40., 0., 20., 50., 100, 150, 200, 250, 300, 400, 500])
    rho = np.array([1.52, 1.29, 1.2, 1.09, 0.95, 0.84, 0.75, 0.68, 0.62, 0.53, 0.46])
    sc = SplineLineal(T, rho)
    print(sc.evaluar(350))
    sc.graficar(350)

    x = np.array([1., 4., 5, 6.])
    y = np.log(x)
    inter = SplineLineal(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)


if __name__ == '__main__':
    main()
