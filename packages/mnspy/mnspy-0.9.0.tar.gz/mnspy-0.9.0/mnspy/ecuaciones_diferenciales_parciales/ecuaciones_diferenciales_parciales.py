import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update(plt.rcParamsDefault)

class EcuacionesDiferencialesParciales:
    """
    Clase base para las demás clases que implementan métodos para el cálculo de ecuaciones algebraícas lineales.

    Attributes
    ----------
    _U: ndarray
        Array con los resultados obtenidos de la iteración
    _X: ndarray
        Array con las coordenadas en x de los puntos de la placa
    _Y: ndarray
        Array con las coordenadas en y de los puntos de la placa
    _frontera: dict[str, float | str | list[float]]
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
    _k_x: float
        coeficiente de conductividad térmica en dirección x
    _k_y: float
        coeficiente de conductividad térmica en dirección y
    _n: int
        número de filas en que se divide la placa
    _m: int
        número de columnas en que se divide la placa
    _q_x: ndarray
        Array con los resultados secundarios del campo en x obtenidos de la iteración
    _q_y: ndarray
        Array con los resultados secundarios del campo en y obtenidos de la iteración
    _v_inicial: float
        Valor inicial que tendrá cada uno de los puntos de la placa

    Methods
    -------
    _calcular_campos():
        Calcula los resultados secundarios del campo, a partir delos resultados principales
    _graficar_datos():
        Se grafica los resultados interpolados de la solución del método, para ello se utiliza el paquete matplotlib
    graficar_valores():
        Se grafica la placa con los valores resultantes en cada punto
    graficar_coordenadas():
        Se grafica la placa con los valores de coordenadas en cada punto
    _graficar_campos():
        Se grafica los resultados secundarios interpolados de la solución del método, que corresponde a los campos,
        para ello se utiliza el paquete matplotlib


    """
    def __init__(self, n: int | tuple[int, int], frontera: dict[str, float | str | list[float]], val_inicial: float,
                 k_x: float = 1, k_y: float = 1):
        """Constructor de la clase EcuacionesDiferencialesParciales

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
        k_x: float
            coeficiente de conductividad térmica en dirección x
        k_y: float
            coeficiente de conductividad térmica en dirección y
        """
        if isinstance(n, tuple):
            self._n, self._m = n
        else:
            self._n = self._m = n
        self._X, self._Y = np.meshgrid(np.arange(0, self._m), np.arange(0, self._n))
        self._v_inicial = val_inicial
        self._U = np.full((self._n, self._m), self._v_inicial, dtype=float)
        self._q_x = np.zeros((self._n, self._m), dtype=float)
        self._q_y = np.zeros((self._n, self._m), dtype=float)
        self._k_x = k_x
        self._k_y = k_y
        self._frontera = frontera
        if not self._frontera['norte'] == 'aislado':
            if isinstance(self._frontera['norte'], list):
                self._U[self._n - 1:, :] = np.matrix(self._frontera['norte'])
            else:
                self._U[self._n - 1:, :] = self._frontera['norte']
        if not self._frontera['sur'] == 'aislado':
            if isinstance(self._frontera['sur'], list):
                self._U[:1, :] = np.matrix(self._frontera['sur'])
            else:
                self._U[:1, :] = self._frontera['sur']
        if not self._frontera['oeste'] == 'aislado':
            if isinstance(self._frontera['oeste'], list):
                self._U[:, :1] = np.matrix(self._frontera['oeste']).transpose()
            else:
                self._U[:, :1] = self._frontera['oeste']
        if not self._frontera['este'] == 'aislado':
            if isinstance(self._frontera['este'], list):
                self._U[:, self._m - 1:] = np.matrix(self._frontera['este']).transpose()
            else:
                self._U[:, self._m - 1:] = self._frontera['este']
        plt.ioff()  # deshabilitada interactividad matplotlib

    def _calcular_campos(self):
        """Calcula los resultados secundarios del campo, a partir delos resultados principales

        Returns
        -------
        None
        """
        for i in range(1, self._n - 1):
            for j in range(1, self._m - 1):
                self._q_x[i, j] = -self._k_x * (self._U[i, j + 1] - self._U[i, j - 1]) / 2
                self._q_y[i, j] = -self._k_y * (self._U[i + 1, j] - self._U[i - 1, j]) / 2

    def _graficar_datos(self):
        """Se grafica los resultados interpolados de la solución del método, para ello se utiliza el paquete matplotlib

        Returns
        -------
        Grafica los resultados interpolados, para ello se utiliza el paquete matplotlib
        """
        plt.contourf(self._X, self._Y, self._U, 25, cmap=plt.jet())
        plt.colorbar()
        plt.xlabel('Sur')
        plt.ylabel('Oeste')
        plt.show()

    def graficar_valores(self):
        """Se grafica la placa con los valores resultantes en cada punto

        Returns
        -------
        Grafica los valores resultantes en cada punto, para ello se utiliza el paquete matplotlib
        """
        plt.scatter(self._X, self._Y)
        plt.margins(0.1)
        for i in range(self._n):
            for j in range(self._m):
                plt.annotate('{:.2f}'.format(self._U[i, j]), (j, i), xytext=(0, 4), textcoords='offset points',
                         ha='center', va='bottom')
        plt.xlabel('Sur')
        plt.ylabel('Oeste')
        plt.show()

    def graficar_coordenadas(self):
        """Se grafica la placa con los valores de coordenadas en cada punto

        Returns
        -------
        Grafica las coordenadas en cada punto, para ello se utiliza el paquete matplotlib
        """
        plt.scatter(self._X, self._Y)
        plt.margins(0.1)
        for i in range(self._n):
            for j in range(self._m):
                plt.annotate('(' + str(i) + ',' + str(j) + ')', (i, j), xytext=(0, 4), textcoords='offset points',
                         ha='center', va='bottom')
        plt.xlabel('Sur')
        plt.ylabel('Oeste')
        plt.show()

    def _graficar_campos(self):
        """Se grafica los resultados secundarios interpolados de la solución del método, que corresponde a los campos,
        para ello se utiliza el paquete matplotlib

        Returns
        -------
        Grafica los resultados secundarios interpolados, para ello se utiliza el paquete matplotlib
        """
        plt.quiver(self._X, self._Y, self._q_x, self._q_y, color='g', pivot='mid')
        plt.xlabel('Sur')
        plt.ylabel('Oeste')
        plt.show()
