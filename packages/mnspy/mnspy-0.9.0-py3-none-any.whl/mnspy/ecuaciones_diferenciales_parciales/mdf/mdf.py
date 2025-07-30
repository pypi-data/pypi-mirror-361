from mnspy.ecuaciones_diferenciales_parciales import EcuacionesDiferencialesParciales
from mnspy.ecuaciones_algebraicas_lineales import Gauss
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class DiferenciasFinitas(EcuacionesDiferencialesParciales):
    """
    Clase para implementación de la solución de ecuaciones diferenciales parciales por el método de Liebmann.

    Attributes
    ----------
    sel: Gauss
        Objeto tipo Gauss usado para la solución del sistema de ecuaciones resultante del método de Diferencias Finitas.
        EL método usado es el de Gauss con pivote parcial.

    Methods
    -------
    _calcular():
        Se ejecuta los cálculos por el método de Diferencias Finitas.

    graficar():
        Se grafica los resultados interpolados de la solución del método, para ello se utiliza el paquete matplotlib

    graficar_campos():
        Se grafica los resultados secundarios interpolados de la solución del método, que corresponde a los campos,
        para ello se utiliza el paquete matplotlib

    Examples:
    -------
    from mnspy import DiferenciasFinitas

    df = DiferenciasFinitas((5, 5), {'norte': 100.0, 'sur': 0.0, 'oeste': 75.0, 'este': 50.0})
    df.graficar()
    df.graficar_valores()
    df.graficar_coordenadas()
    """
    def __init__(self, n: int | tuple[int, int], frontera: dict[str, float | str | list[float]], k_x: float = 1.0,
                 k_y: float = 1.0):
        """Constructor de la clase DiferenciasFinitas

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
        k_x: float
            coeficiente de conductividad térmica en dirección x
        k_y: float
            coeficiente de conductividad térmica en dirección y
        """
        super().__init__(n, frontera, 0.0, k_x, k_y)
        self.sel = None
        self._calcular()

    def _calcular(self):
        """Se ejecuta los cálculos por el método de Diferencias Finitas.

        Returns
        -------
        None
        """
        n = self._n - 2
        m = self._m - 2
        if self._frontera['sur'] == 'aislado':
            n += 1
        if self._frontera['norte'] == 'aislado':
            n += 1
        if self._frontera['oeste'] == 'aislado':
            m += 1
        if self._frontera['este'] == 'aislado':
            m += 1
        A = np.zeros((n * m, n * m))
        for i in range(n * m):
            for j in range(n * m):
                if i == j:
                    A[i, j] = 4
                elif j == i + m:
                    A[i, j] = -1
                elif i == j + m:
                    A[i, j] = -1
                elif j == i + 1 and j % m:
                    A[i, j] = -1
                elif j == i - 1 and i % m:
                    A[i, j] = -1
        b = np.zeros(n * m)
        ini_i = ini_j = 1
        if self._frontera['sur'] == 'aislado':
            ini_j = 0
            for i in range(m):
                A[i, m + i] -= 1
        else:
            b[:m] += self._frontera['sur']
        if self._frontera['norte'] == 'aislado':
            for i in range(m):
                A[m * (n - 1) + i, m * (n - 2) + i] -= 1
        else:
            b[m * (n - 1):] += self._frontera['norte']
        if self._frontera['oeste'] == 'aislado':
            ini_i = 0
            for i in range(n):
                A[m * i, m * i + 1] -= 1
        else:
            b[::m] += self._frontera['oeste']
        if self._frontera['este'] == 'aislado':
            for i in range(n):
                A[m * (i + 1) - 1, m * (i + 1) - 2] -= 1
        else:
            b[m - 1::m] += self._frontera['este']
        self.sel = Gauss(np.matrix(A), np.matrix(b).transpose(), True)
        self.sel.ajustar_etiquetas(
            ['T_{' + str(i % m + ini_i) + ',' + str(int(i / m) + ini_j) + '}' for i in range(n * m)],
            es_latex=True)
        self._U[ini_j:n + ini_j, ini_i:m + ini_i] = self.sel.x.reshape(n, m)
        if self._frontera['sur'] == 'aislado':
            self._q_x[0, 1:self._m - 1] = -(self._U[0, 2:self._m] - self._U[0, :self._m - 2]) / 2
        if self._frontera['norte'] == 'aislado':
            self._q_x[self._n - 1, 1:self._m - 1] = -(self._U[self._n - 1, 2:self._m] - self._U[self._n - 1, :self._m - 2]) / 2
        if self._frontera['oeste'] == 'aislado':
            self._q_y[1:self._n - 1, 0] = -(self._U[2:self._n, 0] - self._U[:self._n - 2, 0]) / 2
        if self._frontera['este'] == 'aislado':
            self._q_y[1:self._n - 1, self._m - 1] = -(self._U[2:self._n, self._m - 1] - self._U[:self._n - 2, self._m - 1]) / 2
        self._calcular_campos()

    def graficar(self):
        """
        Se grafica los resultados interpolados de la solución del método, para ello se utiliza el paquete matplotlib

        Returns
        -------
        Gráfica de los resultados interpolados usando el pquete matplotlib
        """
        plt.axes().set_aspect('equal')
        plt.suptitle('Método de Diferencias Finitas')
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
        plt.suptitle('Método de Diferencias Finitas')
        super()._graficar_campos()


def main():
    df = DiferenciasFinitas((5, 5), {'norte': 100.0, 'sur': 0.0, 'oeste': 75.0, 'este': 50.0})
    df.graficar()
    df.graficar_valores()
    df.graficar_coordenadas()


if __name__ == '__main__':
    main()
