from mnspy.interpolación import Interpolacion
from mnspy.utilidades import es_notebook
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

import sympy as sp

sp.init_printing(use_latex=True)


class InterpolacionNewton(Interpolacion):
    """Clase para la implementación de la interpolación de Newton.

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
        Evalua el la interpolación por el método de Newton, para el valor suministrado
    obtener_polinomio():
        Calcula el polinomio que pasa por los puntos de los datos de la interpolación
    graficar():
        Grafica el polinomio resultante de la interpolación
    _graficar_datos():
        presenta la gráfica de los puntos a interpolar por medio de matplotlib


    Examples
    -------
    from mnspy import InterpolacionNewton
    import numpy as np

    x = np.array([1., 4., 6., 5.])
    y = np.log(x)
    inter = InterpolacionNewton(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)
    inter.mostrar_diferencias_divididas()
    print(inter.obtener_polinomio(expandido=True))
    """
    def __init__(self, x: np.ndarray, y: np.ndarray):
        """Clase para la implementación de la interpolación de Newton

        Parameters
        ----------
        x: ndarray
            Array con los datos de la variable independiente
        y: ndarray
            Array con los datos de la variable dependiente
        """
        super().__init__(x, y)
        self._b = np.zeros((self._n, self._n))
        self._b[:, 0] = np.transpose(self._y)
        for j in range(1, self._n):
            for i in range(self._n - j):
                self._b[i, j] = (self._b[i + 1, j - 1] - self._b[i, j - 1]) / (self._x[i + j] - self._x[i])

    def evaluar(self, x: float) -> float:
        """Evalua el la interpolación por el método de Newton, para el valor suministrado

        Parameters
        ----------
        x: float
            valor x de la variable independiente de a la cual se intepolará

        Returns
        -------
        Un float con el valor interpolado
        """
        x_t = 1
        y_int = self._b[0, 0]
        for j in range(self._n - 1):
            x_t *= (x - self._x[j])
            y_int += self._b[0, j + 1] * x_t
        return y_int

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
        pol = sum([self._b[0][i] * np.prod([(x - self._x[j]) for j in range(i)]) for i in range(self._n)])
        if expandido:
            return sp.expand(pol)
        else:
            return pol

    def mostrar_diferencias_divididas(self):
        """
        Muestra la tabla generada de las diferencias divididas all aplicar el método de interpolación de Newton
        Returns
        -------
        Tabla de la diferencias divididas, usando el paquete tabulate
        """
        tabla = {}
        if es_notebook():
            tabla['$x_{i}$'] = self._x
            tabla['$y_{i}$'] = self._y
            for i in range(self._n - 1):
                dato = list([''] * self._n)
                for j in range(self._n - 1 - i):
                    dato[j] = self._b[j, i + 1]
                tabla['$dif_{' + str(i + 1) + '}$'] = dato
            return tabulate(tabla, headers='keys', tablefmt='html')
        else:
            tabla['x_i'] = self._x
            tabla['y_i'] = self._y
            for i in range(self._n - 1):
                dato = list([''] * self._n)
                for j in range(self._n - 1 - i):
                    dato[j] = self._b[j, i + 1]
                tabla['dif_' + str(i + 1)] = dato
            print(tabulate(tabla, headers='keys', tablefmt='simple'))

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
        y_list = [self.evaluar(val) for val in x_list]
        plt.scatter(x, y, c='r', lw=2, label='Interpolación Newton')
        plt.plot(x_list, y_list, linestyle='dashed', c='k', lw=1, label='Polinomio')
        plt.annotate('$(' + str(x) + r',\,' + str(y) + ')$', (x, y), c='r', alpha=0.9, textcoords="offset points",
                     xytext=(0, 10), ha='center')
        super()._graficar_datos()


def main():
    x = np.array([1., 4., 6., 5.])
    y = np.log(x)
    inter = InterpolacionNewton(x, y)
    print(inter.evaluar(2))
    inter.graficar(2)
    inter.mostrar_diferencias_divididas()


if __name__ == '__main__':
    main()
