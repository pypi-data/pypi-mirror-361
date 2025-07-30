from mnspy.raíces import Raices
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class NewtonRaphson(Raices):
    """Clase para la implementación del cálculo de raíces por el método abierto de Newton-Raphson.

    Attributes
    ----------.
    f: callable
        función a la que se le hallará las raíces
    df: callable
        derivada de función a la que se le hallará las raíces, si es None, se calculará la
        derivada númerica, como el método de la secante
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
        Realiza los cálculos iterativos del método de NewtonRaphson.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Realiza la gráfica del cálculo de la raíz por el método de NewtonRaphson.

    Examples
    -------
    from mnspy import NewtonRaphson

    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    def df(x):
        return 3 * x ** 2 - 20 * x

    nr = NewtonRaphson(f, x=10, tol=4, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()

    nr = NewtonRaphson(f, df=df, x=10, tol=4, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()

    nr = NewtonRaphson(f, x=10, tol=5, tipo_error='%')
    nr.generar_tabla()
    nr.graficar()

    nr = NewtonRaphson(f, df=df, x=10, tol=5, tipo_error='%')
    nr.generar_tabla()
    nr.graficar()

    def g(x):
        return x ** 2 - 2

    def dg(x):
        return 2 * x

    nr = NewtonRaphson(g, df=dg, x=1, tol=4, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()

    def f(x):
        return x ** 4 - 6.4 * x ** 3 + 6.45 * x ** 2 + 20.538 * x - 31.752

    def df(x):
        return 4.0 * x ** 3 - 19.2 * x ** 2 + 12.9 * x + 20.538

    nr = NewtonRaphson(f, df=df, x=2, tol=6, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()
    """
    def __init__(self, f: callable, df: callable = None, x: float = 0, tol: float | int = 1e-3, max_iter: int = 20,
                 tipo_error='%'):
        """
        Constructor de la clase NewtonRaphson.

        Parameters
        ----------
        f: callable
            función a la que se le hallará las raíces
        df: callable
            derivada de función a la que se le hallará las raíces, si es None, se calculará la
            derivada númerica, como el método de la secante
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
        if df is None:
            self._df = self._derivada
        else:
            self._df = df
        super().__init__(f, None, None, tol, max_iter, tipo_error)
        self.x = x
        self._x_0 = x
        self._calcular()

    def _calcular(self):
        """
        Realiza los cálculos iterativos del método de NewtonRaphson.

        Returns
        -------
        None
        """
        self.x -= self._f(self.x) / self._df(self.x)
        if self._fin_iteracion():
            return
        else:
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = True,
                 n_puntos: int = 100):
        """
        Realiza la gráfica del cálculo de la raíz por el método de NewtonRaphson.

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
            l_x = self._tabla['x'].copy()
            l_x.insert(0, self._x_0)
            for i, x in enumerate(l_x[:-1]):
                y = self._f(x)
                plt.axline((x, y), slope=self._df(x), linestyle='dashed', c='purple', lw=1)
                x_next = l_x[i + 1]
                plt.plot([x_next, x_next], [0, self._f(x_next)], linestyle='dashed', c='purple', lw=1)
        plt.title('x= ' + str(self.x))
        if self._error_porcentual:
            plt.suptitle('Método de Newton-Raphson (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle('Método de Newton-Raphson (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    def df(x):
        return 3 * x ** 2 - 20 * x

    nr = NewtonRaphson(f, x=10, tol=4, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()

    nr = NewtonRaphson(f, df=df, x=10, tol=4, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()

    nr = NewtonRaphson(f, x=10, tol=5, tipo_error='%')
    nr.generar_tabla()
    nr.graficar()

    nr = NewtonRaphson(f, df=df, x=10, tol=5, tipo_error='%')
    nr.generar_tabla()
    nr.graficar()

    def g(x):
        return x ** 2 - 2

    def dg(x):
        return 2 * x

    nr = NewtonRaphson(g, df=dg, x=1, tol=4, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()

    def f(x):
        return x ** 4 - 6.4 * x ** 3 + 6.45 * x ** 2 + 20.538 * x - 31.752

    def df(x):
        return 4.0 * x ** 3 - 19.2 * x ** 2 + 12.9 * x + 20.538

    nr = NewtonRaphson(f, df=df, x=2, tol=6, tipo_error='n')
    nr.generar_tabla()
    nr.graficar()


if __name__ == '__main__':
    main()
