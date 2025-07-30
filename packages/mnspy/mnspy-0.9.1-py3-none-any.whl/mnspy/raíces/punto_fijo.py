from mnspy.raíces import Raices
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class PuntoFijo(Raices):
    """Clase para la implementación del cálculo de raíces por el método abierto de Newton-Raphson.

    Attributes
    ----------.
    f: callable
        función a la que se le hallará las raíces
    x: float
        valor de x, por defecto es 0
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
        Realiza los cálculos iterativos del método de PuntoFijo.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Realiza la gráfica del cálculo de la raíz por el método de PuntoFijo.

    Examples
    -------
    from mnspy import PuntoFijo
    import numpy as np

    def f(x):
        return 2 * np.sin(np.sqrt(x))

    pf = PuntoFijo(f, 0.5, 0.0001, tipo_error="%")
    pf.generar_tabla()
    pf.graficar()
    pf.solucion()
    """
    def __init__(self, f: callable, x: float = 0, tol: float | int = 1e-3, max_iter: int = 20, tipo_error='%'):
        """
        Constructor de la clase PuntoFijo.

        Parameters
        ----------
        f: callable
            función a la que se le hallará las raíces
        x: float
            valor de x, por defecto es 0
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
        self._x_0 = self.x = x
        self._calcular()

    def _calcular(self):
        """
        Realiza los cálculos iterativos del método de PuntoFijo.

        Returns
        -------
        None
        """
        self.x += self._f(self.x) - self.x
        if self._fin_iteracion():
            return
        else:
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = True,
                 n_puntos: int = 100):
        """
        Realiza la gráfica del cálculo de la raíz por el método de PuntoFijo.

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
            plt.axline((0, 0), slope=1, linestyle='-', c='k', lw=2, label='$y=x$')
            l_x = self._tabla['x'].copy()
            l_x.insert(0, self._x_0)
            for i, x in enumerate(l_x[:-1]):
                y = self._f(x)
                plt.plot([x, x], [0, y], linestyle='dashed', c='purple', lw=1)
                plt.plot([x, y], [y, y], linestyle='dashed', c='purple', lw=1)
        plt.title('x= ' + str(self.x))
        if self._error_porcentual:
            plt.suptitle('Método de Punto Fijo (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle('Método de Punto Fijo (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    def f(x):
        # return 2 * sin(sqrt(x)) - x
        return 2 * np.sin(np.sqrt(x))

    pf = PuntoFijo(f, 0.5, 0.0001, tipo_error="%")
    pf.generar_tabla()
    pf.graficar()
    pf.solucion()


if __name__ == '__main__':
    main()
