from mnspy.integrales import Integral
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Trapezoidal(Integral):
    """Clase para la implementación de la integral por el método Trapezoidal

    Attributes
    ----------
    _f: callable
        función a la que se integrará
    _a: float
        valor inicial de la integral para la variable independiente
    _b: float
        valor final de la integral para la variable independiente
    _n: int
        número de segmentos, debe ser múltiplo de 3, no existe verificación de dato sea correcto

    Methods
    -------
    graficar():
        Grafica la resultante de la integración

    Examples
    -------
    from mnspy import Trapezoidal

    def f(x):
        return (x + 1 / x) ** 2

    trap = Trapezoidal(f, 1, 2, 6)
    trap.graficar()
    print(trap.integral)
    """

    def __init__(self, f: callable, a: float, b: float, n: int = 100):
        """Constructor de la clase Trapezoidal

        Parameters
        ----------
        f: callable
            función a la que se integrará
        a: float
            valor inicial de la integral para la variable independiente
        b: float
            valor final de la integral para la variable independiente
        n: int
            número de segmentos, debe ser múltiplo de 3, no existe verificación de dato sea correcto
        """
        super().__init__(f=f, a=a, b=b, n=n)
        self._calcular()

    def _calcular(self):
        """Calcula la integral por el método Trapezoidal, el resultado queda guardado en el
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
            s += 2 * self._f(x)
        s += self._f(self._b)
        self.integral = (self._b - self._a) * s / 2 / self._n

    def graficar(self):
        """
        Grafica la resultante de la integración

        Returns
        -------
        Gráfica del proceso de integración usando el paquete de matplotlib
        """
        x = np.linspace(self._a, self._b, self._n + 1)
        y = self._f(x)
        plt.stem(x, y, linefmt='C2--', markerfmt='C0o', basefmt='C2-')
        plt.fill_between(x, y, color='green', alpha=0.3, label='Regla del Trapecio')
        plt.title(r'$\int{f(x)}\approx ' + str(self.integral) + '$')
        self._graficar_datos()


def main():
    def f(x):
        return (x + 1 / x) ** 2

    trap = Trapezoidal(f, 1, 2, 6)
    trap.graficar()
    print(trap.integral)


if __name__ == '__main__':
    main()
