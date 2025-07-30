from mnspy.integrales import Trapezoidal
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Romberg(Trapezoidal):
    """Clase para la implementación de la integral por el método de Romberg

    Attributes
    ----------
    _f: callable
        función a la que se integrará
    _a: float
        valor inicial de la integral para la variable independiente
    _b: float
        valor final de la integral para la variable independiente
    _error_deseado: float
        máximo error porcentual permitido de la integral
    _max_iter: int
        número máximo de iteraciones permitidas

    Methods
    -------
    graficar():
        Grafica la resultante de la integración

    Examples
    -------
    from mnspy import Romberg

    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    ro = Romberg(g, 0, 0.8)
    ro.graficar()
    print(ro.integral)
    """

    def __init__(self, f: callable, a: float, b: float, error_deseado: float = 1.e-8, max_iter: int = 30):
        """Constructor de la clase Romberg

        Parameters
        ----------
        f: callable
            función a la que se integrará
        a: float
            valor inicial de la integral para la variable independiente
        b: float
            valor final de la integral para la variable independiente
        error_deseado: float
            máximo error porcentual permitido de la integral
        max_iter: int
            número máximo de iteraciones permitidas
        """
        super().__init__(f=f, a=a, b=b, n=1)
        self._error_deseado = error_deseado
        self._max_iter = max_iter
        self._error = 0
        self._iter = 0
        self._iterar()

    def _iterar(self):
        """Proceso iterativo para la el cálculo de la integral con el método Romberg

        Returns
        -------
        None
        """
        self._n = 1
        I = np.zeros((2 * self._max_iter, self._max_iter + 1))
        super()._calcular()
        I[0, 0] = self.integral
        for self._iter in range(1, self._max_iter + 1):
            self._n = 2 ** self._iter
            super()._calcular()
            I[self._iter, 0] = self.integral
            for k in range(1, self._iter + 1):
                j = self._iter - k
                I[j, k] = (4 ** k * I[j + 1, k - 1] - I[j, k - 1]) / (4 ** k - 1)
            self._error = abs((I[0, self._iter] - I[1, self._iter - 1]) * 100 / I[0, self._iter])
            if self._error <= self._error_deseado:
                break
        self.integral = I[0, self._iter]

    def _agregar_datos(self):
        """
        Agrega datos a la gráfica que se presentará al graficar, corresponde a una integral trapezoidal para
        cierta cantidad de datos

        Returns
        -------
        None
        """
        for i in range(self._iter + 1):
            x = np.linspace(self._a, self._b, (2 ** i) + 1)
            y = self._f(x)
            ind_color = 'C' + str(i)
            plt.stem(x, y, linefmt='C0--', markerfmt='C0o', basefmt='C0-')
            plt.fill_between(x, y, color=ind_color, alpha=0.3, label='Regla de Romberg' + ' n=' + str((2 ** i)))

    def graficar(self):
        """
        Grafica la resultante de la integración

        Returns
        -------
        Gráfica del proceso de integración usando el paquete de matplotlib
        """
        self._agregar_datos()
        plt.title(r'$\int{f(x)}\approx ' + str(self.integral) + '$')
        self._graficar_datos()


def main():
    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    ro = Romberg(g, 0, 0.8)
    ro.graficar()
    print(ro.integral)


if __name__ == '__main__':
    main()
