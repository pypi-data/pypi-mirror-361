from mnspy.raíces import Raices
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class SecanteModificada(Raices):
    """Clase para la implementación del cálculo de raíces por el método abierto de la Secante Modificada.

    Attributes
    ----------.
    f: callable
        función a la que se le hallará las raíces
    x_0: float
        valor del primer x inicial para cálculo de la secante
    x_1: float
        valor del segundo x inicial para cálculo de la secante
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
        Realiza los cálculos iterativos del método de la Secante Modificada.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Realiza la gráfica del cálculo de la raíz por el método de la Secante Modificada.

    Examples
    -------
    from mnspy import SecanteModificada

        def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    se = SecanteModificada(f, 0.2, delta=0.1, tol=0.01, tipo_error="%")
    se.generar_tabla()
    se.graficar()
    se.solucion()
    """
    def __init__(self, f: callable, x: float = 0, delta: float = 1e-6, tol: float | int = 1e-3, max_iter: int = 20,
                 tipo_error='%'):
        """
        Constructor de la clase SecanteModificada.

        Parameters
        ----------
        f: callable
            función a la que se le hallará las raíces
        x: float
            valor del x inicial para cálculo de la secante modificada
        delta: float
            valor del delta que se suma al x inicial para hallar el segundo x para el cálculo de
            la secante modificada
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
        self._delta = delta
        self._calcular()

    def _calcular(self):
        """
        Realiza los cálculos iterativos del método de la SecanteModificada.

        Returns
        -------
        None
        """
        self.x -= (self._f(self.x) * self._delta) / (
                self._f(self.x + self._delta) - self._f(self.x))
        if self._fin_iteracion():
            return
        else:
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = True,
                 n_puntos: int = 100):
        """
        Realiza la gráfica del cálculo de la raíz por el método de la Secante Modificada.

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
            # fun = vectorize(self.f)
            l_x = self._tabla['x'].copy()
            l_x.insert(0, self._x_0)
            for i, x in enumerate(l_x[:-1]):
                y = self._f(x)
                x_next = l_x[i + 1]
                plt.axline((x, y), slope=(self._f(x + self._delta) - self._f(x)) / self._delta, linestyle='dashed',
                           c='purple',
                           lw=1)
                plt.plot([x_next, x_next], [0, self._f(x_next)], linestyle='dashed', c='purple', lw=1)
        plt.title('x= ' + str(self.x))
        if self._error_porcentual:
            plt.suptitle(
                r'Método de la Secante Modificada, $\delta$ = ' + str(self._delta) + ' (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle(
                r'Método de la Secante Modificada, $\delta$ = ' + str(self._delta) + ' (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    se = SecanteModificada(f, 0.2, delta=0.1, tol=0.01, tipo_error="%")
    se.generar_tabla()
    se.graficar()
    se.solucion()


if __name__ == '__main__':
    main()
