from mnspy.ecuaciones_diferenciales_ordinarias import EcuacionesDiferencialesOrdinarias
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Euler(EcuacionesDiferencialesOrdinarias):
    """
    Clase para implementación de la solución de ecuaciones diferenciales ordinarias por el método de Euler.

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

    Methods
    -------
    _calcular():
        Soluciona ecuación diferencial ordinaria por el método de Euler

    graficar():
        Presenta la gráfica de la solución de la ecuación diferencial ordinaria

    Examples:
    -------
    from mnspy import Euler
    import numpy as np

    def g(x, y):
        return -2 * x ** 3 + 12 * x ** 2 - 20 * x + 8.5

    def exac_g(x):
        return -0.5 * x ** 4 + 4 * x ** 3 - 10 * x ** 2 + 8.5 * x + 1

    eu = Euler(g, 0, 4, 1, 0.5, exac_g)
    eu.graficar()
    eu.solucion()

    def f(x, y):
        return 4 * np.exp(0.8 * x) - 0.5 * y

    def exac_f(x):
        return (4 / 1.3) * (np.exp(0.8 * x) - np.exp(-0.5 * x)) + 2 * np.exp(-0.5 * x)

    eu = Euler(f, 0, 4, 2, 1, exac_f)
    eu.graficar()
    print(eu.y)
    """
    def __init__(self, f: callable, x_i: float, x_f: float, y_i: float, h: float, sol_exacta: callable = None):
        """Constructor de la clase Euler

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
        """
        super().__init__(f, x_i, x_f, y_i, h, sol_exacta)
        self._calcular()

    def _calcular(self):
        """Soluciona ecuación diferencial ordinaria por el método de Euler y la solución queda guardada en el
        atributo y, el valor de las abcisas quedan guardadas en el atributo x

        Returns
        -------
        None
        """
        self.y[0] = self._y_i
        for i in range(len(self.x) - 1):
            self.y[i + 1] = self.y[i] + self._f(self.x[i], self.y[i]) * self._h

    def graficar(self):
        """
        Presenta la gráfica de la solución de la ecuación diferencial ordinaria

        Returns
        -------
        Gráfica de datos y solución de la ecuación diferencial ordinaria con el paquete matplotlib
        """
        plt.plot(self.x, self.y, color='g', lw=2, marker='o', label='Método de Euler')
        plt.title('Método de Euler')
        self._graficar_datos()


def main():
    def g(x, y):
        return -2 * x ** 3 + 12 * x ** 2 - 20 * x + 8.5

    def exac_g(x):
        return -0.5 * x ** 4 + 4 * x ** 3 - 10 * x ** 2 + 8.5 * x + 1

    eu = Euler(g, 0, 4, 1, 0.5, exac_g)
    eu.graficar()
    eu.solucion()

    def f(x, y):
        return 4 * np.exp(0.8 * x) - 0.5 * y

    def exac_f(x):
        return (4 / 1.3) * (np.exp(0.8 * x) - np.exp(-0.5 * x)) + 2 * np.exp(-0.5 * x)

    eu = Euler(f, 0, 4, 2, 1, exac_f)
    eu.graficar()
    print(eu.y)


if __name__ == '__main__':
    main()
