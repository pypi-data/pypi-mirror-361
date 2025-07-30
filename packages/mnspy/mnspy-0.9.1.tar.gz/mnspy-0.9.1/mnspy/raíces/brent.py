from mnspy.raíces import Raices
import numpy as np
import matplotlib.pyplot as plt
import sys
plt.rcParams.update(plt.rcParamsDefault)

class Brent(Raices):
    """Clase para la implementación del cálculo de raíces por el método cerrado de Brent.

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
            Realiza los cálculos iterativos del método de Brent.
        graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
            Realiza la gráfica del cálculo de la raíz por el método de Brent.

        Examples
        -------
        from mnspy import Brent
        import numpy as np

        def f(x):
            return (x ** 3 + 7 * x ** 2 - 40 * x - 100) / 50

        br = Brent(f, 0.0, 8.0, 0.0001, tipo_error="%")
        br.generar_tabla()
        br.graficar()
        br.solucion()
        """
    def __init__(self, f: callable, x_min: float = 0.0, x_max: float = 0.0, tol: float | int = 1e-3, max_iter: int = 20,
                 tipo_error='%'):
        """
        Constructor de la clase Brent.

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
        self._val = list([x_min, x_max])
        self._val_f = [self._f(x_min), self._f(x_max)]
        if np.sign(self._val_f[0]) == np.sign(self._val_f[1]):
            print(
                "No hay cambio de signo entre los límites. El método de Brent requiere que los límites tengan "
                "signos diferentes")
            sys.exit()
        if abs(self._f(x_min)) < abs(self._f(x_max)):
            self._val.reverse()
            self._val_f.reverse()
        self._val.append(self._val[0])
        self._val_f.append(self._val_f[0])
        self._biseccion_usada = True
        self._calcular()

    def _calcular(self):
        """
        Realiza los cálculos iterativos del método de Brent.

        Returns
        -------
        None
        """
        if np.sign(self._val_f[0]) == np.sign(self._val_f[1]):
            print(
                "No hay cambio de signo entre los límites. El método de Brent requiere que los límites tengan "
                "signos diferentes")
            sys.exit()
        x_a, x_b, x_c = self._val
        y_a, y_b, y_c = self._val_f
        x_d = 0
        self._x_min = min([x_a, x_b])
        self._x_max = max([x_a, x_b])
        if len(self._val_f) == len(set(self._val_f)):
            # si los y son diferentes se usa el método de la cuadrática inversa
            self.x = x_a * y_b * y_c / ((y_a - y_b) * (y_a - y_c)) + x_b * y_a * y_c / (
                    (y_b - y_a) * (y_b - y_c)) + x_c * y_a * y_b / ((y_c - y_a) * (y_c - y_b))
        else:
            # Se usa el método de la falsa posición
            self.x = (y_a * x_b - y_b * x_a) / (y_a - y_b)
        if (self.x - (3 * x_a + x_b) / 4) * (self.x - x_b) >= 0 or (
                self._biseccion_usada and abs(self.x - x_b) >= abs(x_b - x_c) / 2) or (
                not self._biseccion_usada and abs(self.x - x_b) >= abs(x_c - x_d) / 2):
            self.x = (x_a + x_b) / 2
            self._biseccion_usada = True
        else:
            self._biseccion_usada = False
        y_x = self._f(self.x)
        # x_d = x_c     # TODO Revisar el código esta variable porque no se usa
        x_c = x_b
        y_c = y_b
        if np.sign(y_a) == np.sign(y_x):
            x_a = self.x
            y_a = y_x
        else:
            x_b = self.x
            y_b = y_x
        if abs(y_a) < abs(y_b):
            x_t = x_a
            y_t = y_a
            x_a = x_b
            y_a = y_b
            x_b = x_t
            y_b = y_t
        self._val = x_a, x_b, x_c
        self._val_f = y_a, y_b, y_c
        if self._fin_iteracion():
            return
        else:
            self._calcular()

    def graficar(self, mostrar_sol: bool = True, mostrar_iter: bool = True, mostrar_lin_iter: bool = False,
                 n_puntos: int = 100):
        """
        Realiza la gráfica del cálculo de la raíz por el método de Brent.

        Parameters
        ----------
        mostrar_sol: bool
            si es verdadero muestra el punto donde se encontró la solución
            por defecto es True
        mostrar_iter: bool
            si es verdadero muestra los puntos obtenidos de cada iteración
            por defecto es True
        mostrar_lin_iter: False
            No implementado
        n_puntos: int
            Número de puntos de la gráfica por defecto 100

        Returns
        -------
        gráfica usando el paquete matplotlib
        """
        plt.title('x= ' + str(self.x))
        if self._error_porcentual:
            plt.suptitle('Método de Brent (tol= ' + str(self._tol) + '%)')
        else:
            plt.suptitle('Método de Brent (tol= ' + str(self._tol) + ')')
        super().graficar(mostrar_sol, mostrar_iter, mostrar_lin_iter, n_puntos)


def main():
    def f(x):
        return (x ** 3 + 7 * x ** 2 - 40 * x - 100) / 50

    br = Brent(f, 0.0, 8.0, 0.0001, tipo_error="%")
    br.generar_tabla()
    br.graficar()
    br.solucion()


if __name__ == '__main__':
    main()
