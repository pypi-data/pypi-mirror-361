from mnspy.integrales import Integral
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class TrapezoidalDesigualAcumulado(Integral):
    """
    Clase para la implementación de la integral por el método TrapezoidalDesigualAcumulado

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
    from mnspy import TrapezoidalDesigualAcumulado

    x = np.linspace(0, 2 * np.pi, 40)
    y = np.cos(x)
    trap = TrapezoidalDesigualAcumulado(x, y)
    trap.graficar()
    print(trap.integral)
    """
    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Constructor de la clase TrapezoidalDesigualAcumulado

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
        """Calcula la integral por el método Trapezoidal Desigual Acumulado, el resultado queda guardado en el
        atributo integral

        Returns
        -------
        None
        """
        s = np.zeros(self._n)
        for i in range(1, self._n):
            s[i] = s[i - 1] + (self._x[i] - self._x[i - 1]) * (self._y[i] + self._y[i - 1]) / 2
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
        plt.stem(self._x, self.integral, linefmt='C3--', markerfmt='C3o', basefmt='C3-')
        plt.fill_between(self._x, self.integral, color='red', alpha=0.3, label='Regla del Trapecio Desigual Acumulado')

        plt.title(r'$\int{f(x)}\approx ' + str(self.integral[-1]) + '$')
        self._graficar_datos()


def main():
    x = np.linspace(0, 2 * np.pi, 40)
    y = np.cos(x)
    trap = TrapezoidalDesigualAcumulado(x, y)
    trap.graficar()
    print(trap.integral)


if __name__ == '__main__':
    main()
