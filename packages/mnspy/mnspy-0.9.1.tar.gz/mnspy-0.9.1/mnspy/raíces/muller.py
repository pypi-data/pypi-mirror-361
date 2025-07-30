from mnspy.raíces import Raices
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Muller(Raices):
    """Clase para la implementación del cálculo de raíces por el método abierto de Muller.

    Attributes
    ----------.
    f: callable
            función a la que se le hallará las raíces
        x: float
            valor de x, por defecto es 0
        h: float
            valor del delta x que se sumara y restará al x incial, para crear los tres puntos iniciales,
            por defecto es 0.1
        tol: float | int
            máxima tolerancia del error
        max_iter: int
            número máximo de iteraciones permitido para hallar la raíz
        tipo_error: str
            tipo de error '%' corresponde al error aproximado relativo porcentual εa = 100*error_aproximado/aproximación
            tipo de error '/' corresponde al error aproximado relativo εa = error_aproximado/aproximación
            tipo de error 'n' corresponde a n cifras significativas εs = (0.5 * 10^(2-n)) %  (Scarborough, 1966)

    Methods
    -------
    _calcular():
        Realiza los cálculos iterativos del método de Muller.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Realiza la gráfica del cálculo de la raíz por el método de Muller.

    Examples
    -------
    from mnspy import Muller
    import numpy as np

    def f(x):
        return np.sin(x)

    mu = Muller(f, 5, tol=0.01, tipo_error="%")
    mu.generar_tabla()
    mu.graficar()
    mu.solucion()
    """
    def __init__(self, f: callable, x: float = 0, h: float = 1e-1, tol: float | int = 1e-3, max_iter: int = 20,
                 tipo_error='%'):
        """
        Constructor de la clase Muller.

        Parameters
        ----------
        f: callable
            función a la que se le hallará las raíces
        x: float
            valor de x, por defecto es 0
        h: float
            valor del delta x que se sumara y restará al x incial, para crear los tres puntos iniciales,
            por defecto es 0.1
        tol: float | int
            máxima tolerancia del error
        max_iter: int
            número máximo de iteraciones permitido para hallar la raíz
        tipo_error: str
            tipo de error '%' corresponde al error aproximado relativo porcentual εa = 100*error_aproximado/aproximación
            tipo de error '/' corresponde al error aproximado relativo εa = error_aproximado/aproximación
            tipo de error 'n' corresponde a n cifras significativas εs = (0.5 * 10^(2-n)) %  (Scarborough, 1966)
        """
        super().__init__(f, None, None, tol, max_iter, tipo_error)
        self.x = x
        self._x_2_i = self._x_0 = self.x
        self._x_1_i = self.x + h
        self._x_0_i = self.x - h
        self._a_0 = []
        self._a_1 = []
        self._a_2 = []
        self._list_x_0 = []
        self._list_x_1 = []
        self._list_x_2 = []
        self._calcular()

    def _calcular(self):
        """
        Realiza los cálculos iterativos del método de Muller.

        Returns
        -------
        None
        """
        h_0 = self._x_1_i - self._x_0_i
        h_1 = self._x_2_i - self._x_1_i
        d_0 = (self._f(self._x_1_i) - self._f(self._x_0_i)) / h_0
        d_1 = (self._f(self._x_2_i) - self._f(self._x_1_i)) / h_1
        a = (d_1 - d_0) / (h_1 + h_0)
        b = a * h_1 + d_1
        c = self._f(self._x_2_i)
        # ***
        self._a_2 += [a]
        self._a_1 += [d_0]
        self._a_0 += [self._f(self._x_0_i)]
        self._list_x_0 += [self._x_0_i]
        self._list_x_1 += [self._x_1_i]
        self._list_x_2 += [self._x_2_i]
        # ***
        rad = np.sqrt(b ** 2 - 4 * a * c)
        if abs(b + rad) > abs(b - rad):
            den = b + rad
        else:
            den = b - rad
        self.x = self._x_2_i - 2 * c / den
        if self._fin_iteracion():
            return
        else:
            self._x_0_i = self._x_1_i
            self._x_1_i = self._x_2_i
            self._x_2_i = self.x
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = True,
                 n_puntos: int = 100):
        """
        Realiza la gráfica del cálculo de la raíz por el método de Muller.

        Parameters
        ----------
        mostrar_sol: bool
            si es verdadero muestra el punto donde se encontró la solución
            por defecto es True
        mostrar_iter: bool
            si es verdadero muestra los puntos obtenidos de cada iteración
            por defecto es True
        mostrar_lin_iter: bool
            si es verdadero muestra las líneas auxiliares que se usan para obtener la solución
            por defecto es True
        n_puntos: int
            Número de puntos de la gráfica por defecto 100

        Returns
        -------
        gráfica usando el paquete matplotlib
        """
        plt.autoscale(False)
        if mostrar_lin_iter and len(self._tabla['x']) > 0:
            x = np.linspace(min(self._tabla['x'] + [self._x_0]), max(self._tabla['x'] + [self._x_0]), n_puntos)
            for i in range(len(self._tabla['x'])):
                y = self._a_2[i] * (x - self._list_x_0[i]) * (x - self._list_x_1[i]) + self._a_1[i] * (
                        x - self._list_x_0[i]) + self._a_0[i]
                plt.plot(x, y, linestyle='dashed', c='purple', lw=1)
                plt.plot([self._tabla['x'][i], self._tabla['x'][i]], [0, self._f(self._tabla['x'][i])], linestyle='dashed',
                         c='purple', lw=1)
        plt.autoscale(True)
        plt.title('x= ' + str(self.x))
        if self._error_porcentual:
            plt.suptitle('Método de Müller (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle('Método de Müller (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    def f(x):
        # return x ** 3 - 13 * x - 12
        return np.sin(x)

    mu = Muller(f, 5, tol=0.01, tipo_error="%")
    mu.generar_tabla()
    mu.graficar()
    mu.solucion()


if __name__ == '__main__':
    main()
