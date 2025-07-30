from mnspy.ecuaciones_diferenciales_ordinarias import EcuacionesDiferencialesOrdinarias
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class RungeKutta(EcuacionesDiferencialesOrdinarias):
    """
    Clase para implementación de la solución de ecuaciones diferenciales ordinarias por el método de RungeKutta.

    Attributes
    ----------
    _etiquetas: dict[str:list[str], str: bool]
        diccionario con etiquetas de la solución
        key: 'label' contiene una lista de etiquetas de la solución
        key: 'es_latex' un boleano que define si el string es en formato Latex o no
    _f: callable
        ecuación diferencail ordinaria que se va a solucionar (dy/dx=f(x,y)
    _h: float
        paso de la iteración, el valor en que aumenta el x
    _sol_exacta: callable
        solución exacta de la ecuación diferencia, solo es usada en la gráfica para comparar
    x: ndarray
        array con los datos de la variable independiente, creado apartir del x inicial, el x final y el paso
    _x_f: float
        valor del x final
    _x_i: float
        valor de x inicial
    _y_i:float
        condición de frontera, valor de y_i para un valor de x_i
    y: ndarray
        array con los datos de la variable dependiente, corresponde a la solución de la ecuación diferencial
    _a_2: float
        valor de la variable a_2 ene el método de RungeKutta
    _metodo: str
        Nombre del método de Runge  Kutta usado
    _orden: int
        Orden del método de Runge Kutta utilizado, los valores posibles son: 2, 3, 4, 5

    Methods
    -------
    _calcular():
        Soluciona ecuación diferencial ordinaria por el método de Euler

    graficar():
        Presenta la gráfica de la solución de la ecuación diferencial ordinaria

    Examples:
    -------
    from mnspy import RungeKutta
    import numpy as np

    def g(x, y):
        return -2 * x ** 3 + 12 * x ** 2 - 20 * x + 8.5

    def exac_g(x):
        return -0.5 * x ** 4 + 4 * x ** 3 - 10 * x ** 2 + 8.5 * x + 1

    rk = RungeKutta(g, 0, 4, 1, 0.5, a_2='punto_medio', sol_exacta=exac_g)
    rk.graficar()
    print(rk.y)

    rk = RungeKutta(g, 0, 4, 1, 0.5, orden=5, sol_exacta=exac_g)
    rk.graficar()
    print(rk.y)

    def f(x, y):
        return 4 * np.exp(0.8 * x) - 0.5 * y

    def exac_f(x):
        return (4 / 1.3) * (np.exp(0.8 * x) - np.exp(-0.5 * x)) + 2 * np.exp(-0.5 * x)

    rk = RungeKutta(f, 0, 4, 2, 1, a_2='punto_medio', sol_exacta=exac_f)
    rk.graficar()
    print(rk.y)

    def f(x, y):
        return -2 * x * y

    def ex(x):
        return 2 * np.exp(-x ** 2)

    rk = RungeKutta(f, 0, 3, 2, 0.25, orden=4, sol_exacta=ex)
    rk.graficar()
    print(rk.y)
    """

    def __init__(self, f: callable, x_i: float, x_f: float, y_i: float, h: float, orden: int = 2,
                 a_2: float | str = 'ralston', sol_exacta: callable = None):
        """Constructor de la clase RungeKutta

        Parameters
        ----------
        f: callable
            ecuación diferencail ordinaria que se va a solucionar (dy/dx=f(x,y)
        x_i: float
            valor de x inicial
        x_f: float
            valor del x final
        y_i: float
            condición de frontera, valor de y_i para un valor de x_i
        h: float
            paso de la iteración, el valor en que aumenta el x
        orden: int
            Orden del método de Runge Kutta utilizado, los valores posibles son: 2, 3, 4, 5
        a_2:  float
            valor de la variable a_2 ene el método de RungeKutta
        sol_exacta: callable
            solución exacta de la ecuación diferencia, solo es usada en la gráfica para comparar
        """
        super().__init__(f=f, x_i=x_i, x_f=x_f, y_i=y_i, h=h, sol_exacta=sol_exacta)
        self._orden = orden
        if self._orden == 2:
            if a_2 == 'heun':
                self._a_2 = 1 / 2
                self._metodo = 'Heun, a2 = 1/2'
            elif a_2 == 'punto_medio':
                self._a_2 = 1
                self._metodo = 'Punto medio, a2 = 1'
            elif a_2 == 'ralston':
                self._a_2 = 2 / 3
                self._metodo = 'Ralston, a2 = 2 / 3'
            elif isinstance(a_2, (int, float)):
                self._a_2 = a_2
                self._metodo = 'a2 = ' + str(a_2)
            else:
                print('Nombre de método no valido')
                quit()
        else:
            self._metodo = 'orden = ' + str(self._orden)
        self._calcular()

    def _calcular(self):
        """Soluciona ecuación diferencial ordinaria por el método de RungeKutta y la solución queda guardada en el
        atributo y, el valor de las abcisas quedan guardadas en el atributo x

        Returns
        -------
        None
        """
        self.y[0] = self._y_i
        if self._orden == 2:
            a_1 = 1 - self._a_2
            p_1 = 1 / 2 / self._a_2
            q_11 = p_1
            for i in range(len(self.x) - 1):
                k_1 = self._f(self.x[i], self.y[i])
                k_2 = self._f(self.x[i] + p_1 * self._h, self.y[i] + q_11 * k_1 * self._h)
                self.y[i + 1] = self.y[i] + (a_1 * k_1 + self._a_2 * k_2) * self._h
        elif self._orden == 3:
            for i in range(len(self.x) - 1):
                k_1 = self._f(self.x[i], self.y[i])
                k_2 = self._f(self.x[i] + self._h / 2, self.y[i] + k_1 * self._h / 2)
                k_3 = self._f(self.x[i] + self._h, self.y[i] - k_1 * self._h + 2 * k_2 * self._h)
                self.y[i + 1] = self.y[i] + (k_1 + 4 * k_2 + k_3) * self._h / 6
        elif self._orden == 4:
            for i in range(len(self.x) - 1):
                k_1 = self._f(self.x[i], self.y[i])
                k_2 = self._f(self.x[i] + self._h / 2, self.y[i] + k_1 * self._h / 2)
                k_3 = self._f(self.x[i] + self._h / 2, self.y[i] + k_2 * self._h / 2)
                k_4 = self._f(self.x[i] + self._h, self.y[i] + k_3 * self._h)
                self.y[i + 1] = self.y[i] + (k_1 + 2 * k_2 + 2 * k_3 + k_4) * self._h / 6
        elif self._orden == 5:
            for i in range(len(self.x) - 1):
                k_1 = self._f(self.x[i], self.y[i])
                k_2 = self._f(self.x[i] + self._h / 4, self.y[i] + k_1 * self._h / 4)
                k_3 = self._f(self.x[i] + self._h / 4, self.y[i] + k_1 * self._h / 8 + k_2 * self._h / 8)
                k_4 = self._f(self.x[i] + self._h / 2, self.y[i] - k_2 * self._h / 2 + k_3 * self._h)
                k_5 = self._f(self.x[i] + 3 * self._h / 4, self.y[i] + 3 * k_1 * self._h / 16 + 9 * k_4 * self._h / 16)
                k_6 = self._f(self.x[i] + self._h, self.y[i] - 3 * k_1 * self._h / 7 + 2 * k_2 * self._h / 7 +
                              12 * k_3 * self._h / 7 - 12 * k_4 * self._h / 7 + 8 * k_5 * self._h / 7)
                self.y[i + 1] = self.y[i] + (7 * k_1 + 32 * k_3 + 12 * k_4 + 32 * k_5 + 7 * k_6) * self._h / 90
        else:
            print('Orden de RK no valido')
            quit()

    def graficar(self):
        """
        Presenta la gráfica de la solución de la ecuación diferencial ordinaria

        Returns
        -------
        Gráfica de datos y solución de la ecuación diferencial ordinaria con el paquete matplotlib
        """
        plt.plot(self.x, self.y, color='g', lw=2, marker='o',
                 label='Método de Runge Kutta orden = ' + str(self._orden))
        plt.title('Método de Runge Kutta ' + '(' + self._metodo + ')')
        self._graficar_datos()


def main():
    def g(x, y):
        return -2 * x ** 3 + 12 * x ** 2 - 20 * x + 8.5

    def exac_g(x):
        return -0.5 * x ** 4 + 4 * x ** 3 - 10 * x ** 2 + 8.5 * x + 1

    rk = RungeKutta(g, 0, 4, 1, 0.5, a_2='punto_medio', sol_exacta=exac_g)
    rk.graficar()
    print(rk.y)

    rk = RungeKutta(g, 0, 4, 1, 0.5, orden=5, sol_exacta=exac_g)
    rk.graficar()
    print(rk.y)

    def f(x, y):
        return 4 * np.exp(0.8 * x) - 0.5 * y

    def exac_f(x):
        return (4 / 1.3) * (np.exp(0.8 * x) - np.exp(-0.5 * x)) + 2 * np.exp(-0.5 * x)

    rk = RungeKutta(f, 0, 4, 2, 1, a_2='punto_medio', sol_exacta=exac_f)
    rk.graficar()
    print(rk.y)

    def f(x, y):
        return -2 * x * y

    def ex(x):
        return 2 * np.exp(-x ** 2)

    rk = RungeKutta(f, 0, 3, 2, 0.25, orden=4, sol_exacta=ex)
    rk.graficar()
    print(rk.y)


if __name__ == '__main__':
    main()
