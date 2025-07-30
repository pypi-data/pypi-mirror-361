from mnspy.integrales import Integral
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class TrapezoidalDesigual(Integral):
    """
    Clase para la implementación de la integral por el método TrapezoidalDesigual

    Attributes
    ----------
    _x: ndarray
        array con los datos de la variable independiente para una integral de tipo discreto
    _y: ndarray
        array con los datos de la variable dependiente para una integral de tipo discreto
    _n: int
        número de puntos para una integral de tipo discreto, o el número de segmentos en que se dividirá la función en
        para las integrales de Newton-Cotes

    Methods
    -------
    graficar():
        Grafica la resultante de la integración

    Examples
    -------
    from mnspy import TrapezoidalDesigual

    x = np.array([0, 0.12, 0.22, 0.32, 0.36, 0.4, 0.44, 0.54, 0.64, 0.7, 0.8])
    y = np.array([0.2, 1.309729, 1.305241, 1.743393, 2.074903, 2.456, 2.842985, 3.507297, 3.181929, 2.363, 0.232])
    trap = TrapezoidalDesigual(x, y)
    trap.graficar()
    print(trap.integral)
    """

    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Constructor de la clase TrapezoidalDesigual

        Parameters
        ----------
        x: ndarray
            array con los datos de la variable independiente para una integral de tipo discreto
        y: ndarray
            array con los datos de la variable dependiente para una integral de tipo discreto
        """
        super().__init__(x=x, y=y)
        self._calcular()

    def _calcular(self):
        """Calcula la integral por el método Trapezoidal Desigual, el resultado queda guardado en el
        atributo integral

        Returns
        -------
        None
        """
        s = 0
        for i in range(self._n - 1):
            s += (self._x[i + 1] - self._x[i]) * (self._y[i + 1] + self._y[i]) / 2
        self.integral = s

    def graficar(self):
        """
        Grafica la resultante de la integración

        Returns
        -------
        Gráfica del proceso de integración usando el paquete de matplotlib
        """
        plt.stem(self._x, self._y, linefmt='C2--', markerfmt='C0o', basefmt='C2-')
        plt.fill_between(self._x, self._y, color='green', alpha=0.3, label='Regla del Trapecio Desigual')
        plt.title(r'$\int{f(x)}\approx ' + str(self.integral) + '$')
        self._graficar_datos()


def main():
    x = np.array([0, 0.12, 0.22, 0.32, 0.36, 0.4, 0.44, 0.54, 0.64, 0.7, 0.8])
    y = np.array([0.2, 1.309729, 1.305241, 1.743393, 2.074903, 2.456, 2.842985, 3.507297, 3.181929, 2.363, 0.232])
    trap = TrapezoidalDesigual(x, y)
    trap.graficar()
    print(trap.integral)


if __name__ == '__main__':
    main()
