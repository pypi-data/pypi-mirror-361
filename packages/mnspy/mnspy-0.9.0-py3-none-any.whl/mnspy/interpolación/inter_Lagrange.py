from mnspy.interpolación import Interpolacion
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

sp.init_printing(use_latex=True)

plt.rcParams.update(plt.rcParamsDefault)

class InterpolacionLagrange(Interpolacion):
    """Clase para la implementación de la interpolación de Lagrange.

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
        Evalua el la interpolación por el método de Lagrange, para el valor suministrado
    obtener_polinomio():
        Calcula el polinomio que pasa por los puntos de los datos de la interpolación
    graficar():
        Grafica el polinomio resultante de la interpolación
    _graficar_datos():
        presenta la gráfica de los puntos a interpolar por medio de matplotlib


    Examples
    -------
    from mnspy import InterpolacionLagrange
    import numpy as np

    x = np.array([1., 4., 6., 5.])
    y = np.log(x)
    inter = InterpolacionLagrange(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)
    print(inter.obtener_polinomio(expandido=True))
    """

    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Clase para la implementación de la interpolación de Lagrange

        Parameters
        ----------
        x: ndarray
            Array con los datos de la variable independiente
        y: ndarray
            Array con los datos de la variable dependiente
        """
        super().__init__(x, y)

    def evaluar(self, x: float) -> float:
        """Evalua el la interpolación por el método de Lagrange, para el valor suministrado

        Parameters
        ----------
        x: float
            valor x de la variable independiente de a la cual se intepolará

        Returns
        -------
        Un float con el valor interpolado
        """
        s = 0
        for i in range(self._n):
            p = self._y[i]
            for j in range(self._n):
                if i != j:
                    p *= (x - self._x[j]) / (self._x[i] - self._x[j])
            s += p
        return s

    def obtener_polinomio(self, expandido: bool = False):
        """
        Calcula el polinomio que pasa por los puntos de los datos de la interpolación

        Parameters
        ----------
        expandido: bool
            Si es verdadero, retorna el polinomio expandido, en caso contrario muestra el polinomio en forma
            no standard, si no el resultado de aplicar el método.

        Returns
        -------
        Retorna el polinomio que pasa por los puntos de los datos de la interpolación
        """
        x = sp.symbols('x')
        pol = sum(
            [self._y[i] * np.prod([(x - self._x[j]) / (self._x[i] - self._x[j]) for j in range(self._n) if i != j]) for
             i in
             range(self._n)])
        if expandido:
            return sp.expand(pol)
        else:
            return pol

    def graficar(self, x: float) -> None:
        """
        Grafica el polinomio resultante de la interpolación

        Parameters
        ----------
        x: float
            valor x de la variable independiente a la que se interpolará y mostrará en la gráfica.

        Returns
        -------
        Grafica de la interpolación realizada usando el paquete de matplotlib
        """
        y = self.evaluar(x)
        x_min = min(self._x)
        x_max = max(self._x)
        x_list = np.linspace(x_min, x_max, 1000)
        # y_list = self.evaluar(x_list)
        y_list = [self.evaluar(val) for val in x_list]
        plt.scatter(x, y, c='r', lw=2, label='Interpolación Lagrange')
        plt.plot(x_list, y_list, linestyle='dashed', c='k', lw=1, label='Polinomio')
        plt.annotate('$(' + str(x) + r',\,' + str(y) + ')$', (x, y), c='r', alpha=0.9, textcoords="offset points",
                     xytext=(0, 10), ha='center')
        super()._graficar_datos()


def main():
    x = np.array([1., 4., 6., 5.])
    y = np.log(x)
    inter = InterpolacionLagrange(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)
    print(inter.obtener_polinomio(expandido=True))


if __name__ == '__main__':
    main()
