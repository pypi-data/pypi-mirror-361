from mnspy.integrales import Integral
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class CuadraturaAdaptativa(Integral):
    """Clase para la implementación de la integral por el método de Cuadratura Adaptativa

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
    from mnspy import CuadraturaAdaptativa

    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    gl = CuadraturaAdaptativa(g, 0, 0.8)
    gl.graficar()
    print(gl.integral)
    """
    def __init__(self, f: callable, a: float, b: float, tol: float = 1.e-8):
        """Constructor de la clase CuadraturaAdaptativa

        Parameters
        ----------
        f: callable
            función a la que se integrará
        a: float
            valor inicial de la integral para la variable independiente
        b: float
            valor final de la integral para la variable independiente
        tol: float
            tolerancia permitida de error
        """
        super().__init__(f=f, a=a, b=b)
        self._puntos = set()
        self._tol = tol
        f_a = self._f(self._a)
        f_c = self._f(0.5 * (self._a + self._b))
        f_b = self._f(self._b)
        self.integral = self._iterar(self._a, self._b, f_a, f_c, f_b)

    def _iterar(self, a, b, f_a, f_c, f_b) -> float:
        """Proceso iterativo para la el cálculo de la integral con el método de la cuadratura adapatativa

        Parameters
        ----------
        a: float
            valor inferior de la integral
        b: float
            valor superior de la integral
        f_a:
            valor de la función en a
        f_c:
            valor de la función en (a+b)/2
        f_b:
            valor de la función en b

        Returns
        -------
        valor de la integral después de un proceso iterativo
        """
        h = b - a
        c = 0.5 * (a + b)
        f_d = self._f(0.5 * (a + c))
        f_e = self._f(0.5 * (c + b))
        q_1 = h / 6 * (f_a + 4 * f_c + f_b)
        q_2 = h / 12 * (f_a + 4 * f_d + 2 * f_c + 4 * f_e + f_b)
        self._puntos.update({a})
        self._puntos.update({c})
        self._puntos.update({b})
        self._puntos.update({0.5 * (a + c)})
        self._puntos.update({0.5 * (c + b)})
        if abs(q_1 - q_2) < self._tol:
            q = q_2 + (q_2 - q_1) / 15
        else:
            q_a = self._iterar(a, c, f_a, f_d, f_c)
            q_b = self._iterar(c, b, f_c, f_e, f_b)
            q = q_a + q_b
        return q

    def graficar(self):
        """
        Grafica la resultante de la integración

        Returns
        -------
        Gráfica del proceso de integración usando el paquete de matplotlib
        """
        x = list(self._puntos)
        y = list((self._f(x_i) for x_i in x))
        plt.stem(x, y, linefmt='C2--', markerfmt='C0o', basefmt='C2-', label='Cuadratura Adaptativa')
        plt.title(r'$\int{f(x)}\approx ' + str(self.integral) + '$')
        self._graficar_datos()


def main():
    def g(x):
        return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5

    gl = CuadraturaAdaptativa(g, 0, 0.8)
    gl.graficar()
    print(gl.integral)


if __name__ == '__main__':
    main()
