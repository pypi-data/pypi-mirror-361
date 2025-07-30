from mnspy.integrales import Integral
from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Simpson13(Integral):
    """Clase para la implementación de la integral por el método de Simpson 1/3

    Attributes
    ----------
    _f: callable
        función a la que se integrará
    _a: float
        valor inicial de la integral para la variable independiente
    _b: float
        valor final de la integral para la variable independiente
    _n: int
        número de segmentos, debe ser múltiplo de 2, no existe verificación de dato sea correcto

    Methods
    -------
    graficar():
        Grafica la resultante de la integración

    Examples
    -------
    from mnspy import Simpson13

    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    sim = Simpson13(g, 0, 0.8, 2)
    sim.graficar()
    print(sim.integral)
    """
    def __init__(self, f: callable, a: float, b: float, n: int = 100):
        """Constructor de la clase Simpson13

        Parameters
        ----------
        f: callable
            función a la que se integrará
        a: float
            valor inicial de la integral para la variable independiente
        b: float
            valor final de la integral para la variable independiente
        n: int
            número de segmentos, debe ser múltiplo de 2, no existe verificación de dato sea correcto
        """
        super().__init__(f=f, a=a, b=b, n=n)
        self._calcular()

    def _calcular(self):
        """Calcula la integral por el método de Simpson 1/3, el resultado queda guardado en el
        atributo integral

        Returns
        -------
        None
        """
        x = self._a
        h = (self._b - self._a) / self._n
        s = self._f(self._a)
        for i in range(self._n - 1):
            x += h
            if (i % 2) == 1:
                s += 2 * self._f(x)
            else:
                s += 4 * self._f(x)
        s += self._f(self._b)
        self.integral = (self._b - self._a) * s / 3 / self._n

    def graficar(self):
        """
        Grafica la resultante de la integración

        Returns
        -------
        Gráfica del proceso de integración usando el paquete de matplotlib
        """
        x = np.linspace(self._a, self._b, self._n + 1)
        y = self._f(x)
        xvals = np.linspace(self._a, self._b, 100)
        spl = interp1d(x, y, kind='quadratic')
        y_smooth = spl(xvals)
        plt.stem(x, y, linefmt='C2--', markerfmt='C0o', basefmt='C2-')
        plt.fill_between(xvals, y_smooth, color='green', alpha=0.3, label='Regla Simpson 1/3')
        plt.title(r'$\int{f(x)}\approx ' + str(self.integral) + '$')
        self._graficar_datos()


def main():
    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    sim = Simpson13(g, 0, 0.8, 2)
    sim.graficar()
    print(sim.integral)


if __name__ == '__main__':
    main()
