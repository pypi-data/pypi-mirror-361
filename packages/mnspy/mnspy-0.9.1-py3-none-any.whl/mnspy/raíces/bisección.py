from mnspy.raíces import Raices
import numpy as np
import matplotlib.pyplot as plt
import sys
plt.rcParams.update(plt.rcParamsDefault)

class Biseccion(Raices):
    """Clase para la implementación del cálculo de raíces por el método cerrado de la Bisección.

    Attributes
    ----------.
    f: callable
        función a la que se le hallará las raíces
    x_min: float
        mínimo valor de x
    x_max: float
        máximo valor de x
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
        Realiza los cálculos iterativos del método de la bisección.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Realiza la gráfica del cálculo de la raíz por el método de la bisección.

    Examples
    -------
    from mnspy import Biseccion
    import numpy as np

    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    bis = Biseccion(f, 0, 1, tol=4, tipo_error='n')
    bis.generar_tabla()
    bis.graficar()
    bis.solucion()

    bis = Biseccion(f, 0, 1, tol=5, tipo_error='%')
    bis.generar_tabla()
    bis.graficar()
    bis.solucion()
    """

    def __init__(self, f: callable, x_min: float = 0, x_max: float = 0, tol: float | int = 1e-3, max_iter: int = 20,
                 tipo_error='%'):
        """
        Constructor de la clase Biseccion.

        Parameters
        ----------
        f: callable
            función a la que se le hallará las raíces
        x_min: float
            mínimo valor de x, por defecto es 0
        x_max: float
            máximo valor de x, por defecto es 0
        tol: float | int
            máxima tolerancia del error
        max_iter: int
            número máximo de iteraciones permitido para hallar la raíz
        tipo_error: str
            tipo de error '%' corresponde al error aproximado relativo porcentual εa = 100*error_aproximado/aproximación
            tipo de error '/' corresponde al error aproximado relativo εa = error_aproximado/aproximación
            tipo de error 'n' corresponde a n cifras significativas εs = (0.5 * 10^(2-n)) %  (Scarborough, 1966)
        """
        super().__init__(f, x_min, x_max, tol, max_iter, tipo_error)
        self._calcular()

    def _calcular(self):
        """
        Realiza los cálculos iterativos del método de la bisección.

        Returns
        -------
        None
        """
        if np.sign(self._f(self._x_min)) == np.sign(self._f(self._x_max)):
            print("La raíz no está dentro de este rango, pruebe con otro rango de datos")
            sys.exit()
        self.x = (self._x_min + self._x_max) / 2
        if self._fin_iteracion():
            return
        elif np.sign(self._f(self._x_min)) == np.sign(self._f(self.x)):
            self._x_min = self.x
            self._calcular()
        elif np.sign(self._f(self._x_max)) == np.sign(self._f(self.x)):
            self._x_max = self.x
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = True,
                 n_puntos: int = 100):
        """
        Realiza la gráfica del cálculo de la raíz por el método de la bisección.

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
        if mostrar_lin_iter and len(self._tabla['x']) > 0:
            y = [self._f(val) for val in np.linspace(self._rango[0], self._rango[1], n_puntos)]
            y_min = min(y)
            y_max = max(y)
            delta_y = (y_max - y_min) / 40.0
            for i, x in enumerate(self._tabla['x']):
                y = self._f(x)
                ind_color = 'C' + str(i % 10)
                datos = plt.stem(x, y, linefmt=ind_color + '--', markerfmt=ind_color, basefmt=ind_color + '-',
                                 bottom=y_min - (i + 1) * delta_y)
                linea_base = datos[2]
                plt.setp(linea_base, 'linewidth', 2, 'marker', '.')
                linea_base.set_xdata([self._tabla['x_min'][i], self._tabla['x_max'][i]])
        plt.title('x= ' + str(self.x))
        if self._error_porcentual:
            plt.suptitle('Método de la Bisección (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle('Método de la Bisección (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    bis = Biseccion(f, 0, 1, tol=4, tipo_error='n')
    bis.generar_tabla()
    bis.graficar()
    bis.solucion()

    bis = Biseccion(f, 0, 1, tol=5, tipo_error='%')
    bis.generar_tabla()
    bis.graficar()
    bis.solucion()


if __name__ == '__main__':
    main()
