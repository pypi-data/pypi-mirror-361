from mnspy.raíces import Raices
import numpy as np
import matplotlib.pyplot as plt
import sys
plt.rcParams.update(plt.rcParamsDefault)

class FalsaPosicion(Raices):
    """Clase para la implementación del cálculo de raíces por el método cerrado de la Falsa Posición.

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
        Realiza los cálculos iterativos del método de la Falsa Posición.
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Realiza la gráfica del cálculo de la raíz por el método de la Falsa Posición.

    Examples
    -------
    from mnspy import FalsaPosicion

    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    fp = FalsaPosicion(f, 0, 1, tol=4, tipo_error='n')
    fp.generar_tabla()
    fp.graficar()

    fp = FalsaPosicion(f, 0, 1, tol=5, tipo_error='%')
    fp.generar_tabla()
    fp.graficar()
    """
    def __init__(self, f: callable, x_min: float = 0, x_max: float = 0, tol: float | int = 1e-3, max_iter: int = 20,
                 tipo_error='%'):
        """
        Constructor de la clase FalsaPosicion.

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
        Realiza los cálculos iterativos del método de la FalsaPosicion.

        Returns
        -------
        None
        """
        if np.sign(self._f(self._x_min)) == np.sign(self._f(self._x_max)):
            print("La raíz no está dentro de este rango, pruebe con otro rango de datos")
            sys.exit()
        self.x = self._x_max - (self._f(self._x_max) * (self._x_min - self._x_max)) / (
                self._f(self._x_min) - self._f(self._x_max))
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
        Realiza la gráfica del cálculo de la raíz por el método de la Falsa Posición.

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
            for i, x in enumerate(self._tabla['x']):
                y = self._f(x)
                a = self._tabla['x_min'][i]
                b = self._tabla['x_max'][i]
                plt.plot([x, x], [0, y], linestyle='dashed', c='purple', lw=1)
                plt.plot([a, b], [self._f(a), self._f(b)], linestyle='dashed', c='purple', lw=1)
        plt.title('x= ' + str(self.x))
        if self._error_porcentual:
            plt.suptitle('Método de la Falsa Posición (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle('Método de la Falsa Posición (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    def f(x):
        return x ** 3 - 10 * x ** 2 + 5

    fp = FalsaPosicion(f, 0, 1, tol=4, tipo_error='n')
    fp.generar_tabla()
    fp.graficar()

    fp = FalsaPosicion(f, 0, 1, tol=5, tipo_error='%')
    fp.generar_tabla()
    fp.graficar()


if __name__ == '__main__':
    main()
