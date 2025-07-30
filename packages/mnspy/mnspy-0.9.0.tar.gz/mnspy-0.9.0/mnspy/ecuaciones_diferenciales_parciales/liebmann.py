from mnspy.ecuaciones_diferenciales_parciales import EcuacionesDiferencialesParciales
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Liebmann(EcuacionesDiferencialesParciales):
    """
    Clase para implementación de la solución de ecuaciones diferenciales parciales por el método de Liebmann.

    Attributes
    ----------
    _converge: bool
        Atributo donde se almacena el estado de convergencia al final de la iteración. Si es True, la solución
        tuvo convergencia para el porcentaje de tolerancia establecida _tol_porc, en caso contrario no se tiene
        convergencia
    _factor_lambda: float
        Factor de sobrerrelajación en los cáculos del proceso iterativo
    _iter: int
        Número de iteraciones realizadas
    _iter_max: int
        Máximo número de iteraciones permitidas, en el caso de que se supere, el procedimento parará y establecerá como
        False el atributo _converge
    _tol_porc: float
        Máximo porcentaje de tolerancia permitido en la iteración, para considerar que converge.

    Methods
    -------
    _calcular():
        Se ejecuta los cálculos iterativos de Liebman, de acuerdo a los criterios de convergencia suministrados.

    graficar():
        Se grafica los resultados interpolados de la solución del método, para ello se utiliza el paquete matplotlib

    graficar_campos():
        Se grafica los resultados secundarios interpolados de la solución del método, que corresponde a los campos,
        para ello se utiliza el paquete matplotlib

    Examples:
    -------
    from mnspy import Liebmann

    lp = Liebmann((10, 10), {'norte': 80.0, 'sur': 20.0, 'oeste': 20.0, 'este': 0.0}, 5, tol_porc=1)
    lp.graficar()
    lp.graficar_campos()

    """
    def __init__(self, n: int | tuple[int, int], frontera: dict[str, float | str | list[float]], val_inicial: float,
                 tol_porc: float = 0.1, factor_lambda: float = 1, iter_max: int = 200, k_x: float = 1, k_y: float = 1):
        """Constructor de la clase Liebmann

        Parameters
        ----------
        n: int | tuple[int, int]
            Número de divisiones que tendrá la placa, si se ingresa un entero n la placa estará dividida en n x n.
            En caso de que se ingrese una tupla (n, m), la placa estara dividida en n x m
        frontera: dict[str, float | str | list[float]]
            Condiciones de frontera de la placa con las siguientes llaves permitidas:
                'norte': float | str | list[float]
                    valores en la frontera norte de la placa, con los siguientes tipos de datos permitidos:
                        float: si es float, todos los puntos de la frontera tendrán el valor ingresado. Corresponde
                            a la condición de frontera de 'Dirichlet'
                        str: si es una string, aplica la condición de frontera de 'Neumann', el único dato permitido
                            es 'aislado' que corresponde a la condición de frontera natural
                        list[float]: si es una lista de float, todos los puntos de la frontera tendrán el valor
                            ingresado en la lista, el tamaño de la lista debe cser igual al número de divisiones en
                            esa frontera. Corresponde a la condición de frontera de 'Dirichlet'
                'sur': float | str | list[float]
                    valores en la frontera norte de la placa, con los siguientes tipos de datos permitidos:
                        float: si es float, todos los puntos de la frontera tendrán el valor ingresado. Corresponde
                            a la condición de frontera de 'Dirichlet'
                        str: si es una string, aplica la condición de frontera de 'Neumann', el único dato permitido
                            es 'aislado' que corresponde a la condición de frontera natural
                        list[float]: si es una lista de float, todos los puntos de la frontera tendrán el valor
                            ingresado en la lista, el tamaño de la lista debe cser igual al número de divisiones en
                            esa frontera. Corresponde a la condición de frontera de 'Dirichlet'
                'este': float | str | list[float]
                    valores en la frontera norte de la placa, con los siguientes tipos de datos permitidos:
                        float: si es float, todos los puntos de la frontera tendrán el valor ingresado. Corresponde
                            a la condición de frontera de 'Dirichlet'
                        str: si es una string, aplica la condición de frontera de 'Neumann', el único dato permitido
                            es 'aislado' que corresponde a la condición de frontera natural
                        list[float]: si es una lista de float, todos los puntos de la frontera tendrán el valor
                            ingresado en la lista, el tamaño de la lista debe cser igual al número de divisiones en
                            esa frontera. Corresponde a la condición de frontera de 'Dirichlet'
                'oeste': float | str | list[float]
                    valores en la frontera norte de la placa, con los siguientes tipos de datos permitidos:
                        float: si es float, todos los puntos de la frontera tendrán el valor ingresado. Corresponde
                            a la condición de frontera de 'Dirichlet'
                        str: si es una string, aplica la condición de frontera de 'Neumann', el único dato permitido
                            es 'aislado' que corresponde a la condición de frontera natural
                        list[float]: si es una lista de float, todos los puntos de la frontera tendrán el valor
                            ingresado en la lista, el tamaño de la lista debe cser igual al número de divisiones en
                            esa frontera. Corresponde a la condición de frontera de 'Dirichlet'
        val_inicial: float
            Valor inicial que tendrá cada uno de los puntos de la placa
        tol_porc: float
            Máximo porcentaje de tolerancia permitido en la iteración, para considerar que converge
        factor_lambda: float
            Factor de sobrerrelajación en los cáculos del proceso iterativo
        iter_max: int
            Máximo número de iteraciones permitidas, en el caso de que se supere, el procedimento parará y establecerá
            como False el atributo _converge
        k_x: float
            coeficiente de conductividad térmica en dirección x
        k_y: float
            coeficiente de conductividad térmica en dirección y
        """
        super().__init__(n, frontera, val_inicial, k_x, k_y)
        self._iter_max = iter_max
        self._factor_lambda = factor_lambda
        self._tol_porc = tol_porc
        self._converge = True
        self._iter = 0
        self._calcular()

    def _calcular(self):
        """Se ejecuta los cálculos iterativos de Liebman, de acuerdo a los criterios de convergencia suministrados.

        Returns
        -------
        None
        """
        for k in range(self._iter_max):
            self._iter = k + 1
            self._converge = True
            if self._frontera['norte'] == 'aislado':
                self._U[self._n - 1, 1:self._m - 1] = (self._U[self._n - 2, 1:self._m - 1] / 2 +
                                                       self._U[self._n - 1, :self._m - 2] / 4 + self._U[self._n - 1,
                                                                                          2:self._m] / 4)
                self._q_x[self._n - 1, 1:self._m - 1] = -(self._U[self._n - 1, 2:self._m] - self._U[self._n - 1,
                                                                                      :self._m - 2]) / 2
            if self._frontera['sur'] == 'aislado':
                self._U[0, 1:self._m - 1] = (self._U[1, 1:self._m - 1] / 2 + self._U[0, :self._m - 2] / 4 +
                                             self._U[0, 2:self._m] / 4)
                self._q_x[0, 1:self._m - 1] = -(self._U[0, 2:self._m] - self._U[0, :self._m - 2]) / 2

            if self._frontera['oeste'] == 'aislado':
                self._U[1:self._n - 1, 0] = (
                        self._U[1:self._n - 1, 1] / 2 + self._U[2:self._n, 0] / 4 + self._U[:self._n - 2, 0] / 4)
                self._q_y[1:self._n - 1, 0] = -(self._U[2:self._n, 0] - self._U[:self._n - 2, 0]) / 2

            if self._frontera['este'] == 'aislado':
                self._U[1:self._n - 1, self._m - 1] = (
                        self._U[1:self._n - 1, self._m - 2] / 2 + self._U[2:self._n, self._m - 1] / 4 + self._U[
                                                                                                  :self._n - 2,
                                                                                                        self._m - 1] / 4)
                self._q_y[1:self._n - 1, self._m - 1] = -(self._U[2:self._n, self._m - 1] - self._U[:self._n - 2,
                                                                                            self._m - 1]) / 2

            for i in range(1, self._n - 1):
                for j in range(1, self._m - 1):
                    last_val = self._U[i, j]
                    self._U[i, j] = self._factor_lambda * (
                            self._U[i + 1, j] + self._U[i - 1, j] + self._U[i, j + 1] + self._U[i, j - 1]) / 4 + (
                                           1 - self._factor_lambda) * last_val
                    if self._U[i, j] == 0.0:
                        cumple = False
                    else:
                        cumple = abs((self._U[i, j] - last_val) / self._U[i, j]) < self._tol_porc / 100.0
                    self._converge = self._converge and cumple
            if self._converge:
                break
        self._calcular_campos()

    def graficar(self):
        """
        Se grafica los resultados interpolados de la solución del método, para ello se utiliza el paquete matplotlib

        Returns
        -------
        Gráfica de los resultados interpolados usando el pquete matplotlib
        """
        plt.axes().set_aspect('equal')
        plt.suptitle('Método de Liebmann')
        if self._converge:
            plt.title('Tolerancia= ' + str(self._tol_porc) + ' %,' + ' N iteraciones= ' + str(self._iter))
        else:
            plt.title('No converge, N iteraciones= ' + str(self._iter))
        super()._graficar_datos()

    def graficar_campos(self):
        """
        Se grafica los resultados secundarios interpolados de la solución del método, que corresponde a los campos,
        para ello se utiliza el paquete matplotlib

        Returns
        -------
        Gráfica de los resultados secundarios interpolados usando el pquete matplotlib
        """
        plt.axes().set_aspect('equal')
        plt.suptitle('Método de Liebmann')
        super()._graficar_campos()


def main():
    lp = Liebmann((10, 10), {'norte': 80.0, 'sur': 20.0, 'oeste': 20.0, 'este': 0.0}, 5, tol_porc=1)
    lp.graficar()
    lp.graficar_campos()


if __name__ == '__main__':
    main()
