from mnspy.integrales import Integral
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)
class GaussLegendre(Integral):
    """Clase para la implementación de la integral por el método de Gauss-Legendre

    Attributes
    ----------
    _f: callable
        función a la que se integrará
    _a: float
        valor inicial de la integral para la variable independiente
    _b: float
        valor final de la integral para la variable independiente

    Methods
    -------
    graficar():
        Grafica la resultante de la integración

    Examples
    -------
    from mnspy import GaussLegendre

    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    gl = GaussLegendre(g, 0, 0.8, 6)
    gl.graficar()
    print(gl.integral)
    """
    def __init__(self, f: callable, a: float, b: float, n: int = 2):
        """Constructor de la clase GaussLegendre

        Parameters
        ----------
        f: callable
            función a la que se integrará
        a: float
            valor inicial de la integral para la variable independiente
        b: float
            valor final de la integral para la variable independiente
        n: int
            número de puntos utilizados para realizar la integral, los valores aceptados son 2, 3, 4, 5, 6. En caso
            de ingresar otro entero diferente se calculará con dos puntos.
        """
        super().__init__(f=f, a=a, b=b, n=n)
        if self._n == 2:
            self._c = [1, 1]
            self._x = [-0.577350269, 0.577350269]
        elif self._n == 3:
            self._c = [0.5555556, 0.8888889, 0.5555556]
            self._x = [-0.774596669, 0, 0.774596669]
        elif self._n == 4:
            self._c = [0.3478548, 0.6521452, 0.6521452, 0.3478548]
            self._x = [-0.861136312, -0.339981044, 0.339981044, 0.861136312]
        elif self._n == 5:
            self._c = [0.2369269, 0.4786287, 0.5688889, 0.4786287, 0.2369269]
            self._x = [-0.906179846, -0.538469310, 0, 0.538469310, 0.906179846]
        elif self._n == 6:
            self._c = [0.1713245, 0.3607616, 0.4679139, 0.4679139, 0.3607616, 0.1713245]
            self._x = [-0.932469514, -0.661209386, -0.238619186, 0.238619186, 0.661209386, 0.932469514]
        else:
            self._n = 2
            self._c = [1, 1]
            self._x = [-0.577350269, 0.577350269]
        self._calcular()

    def _calcular(self):
        """Calcula la integral por el método de Gauss-Legendre, el resultado queda guardado en el
        atributo integral

        Returns
        -------
        None
        """
        s = 0
        for i in range(self._n):
            s += self._c[i] * self._f(0.5 * (self._b - self._a) * self._x[i] + 0.5 * (self._b + self._a))
        s *= 0.5 * (self._b - self._a)
        self.integral = s

    def graficar(self):
        """
        Grafica la resultante de la integración

        Returns
        -------
        Gráfica del proceso de integración usando el paquete de matplotlib
        """
        x = list((0.5 * (self._b - self._a) * x_i + 0.5 * (self._b + self._a) for x_i in self._x))
        y = list((self._f(x_i) for x_i in x))
        plt.stem(x, y, linefmt='C2--', markerfmt='C0o', basefmt='C2-', label='Gauss-Legrende')
        plt.title('$\\int{f(x)}\\approx ' + str(self.integral) + '$')
        self._graficar_datos()


def main():
    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    gl = GaussLegendre(g, 0, 0.8, 6)
    gl.graficar()
    print(gl.integral)


if __name__ == '__main__':
    main()
