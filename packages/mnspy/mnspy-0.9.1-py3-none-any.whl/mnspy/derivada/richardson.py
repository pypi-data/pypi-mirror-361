from mnspy.derivada import Derivada
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Richardson(Derivada):
    """Clase para la implementación de la derivada Richardson.

    Attributes
    ----------
    _f: callable
            Función a la que derivará.
    _h: float
            Valor del incrmento de las abcisas para el cáculo de la derivada
    _modo: str
        string con el modo de derivada a realizar
    _orden: str
            puede ser ‘h’, ‘h2’ y ‘h4’
                - para el modo ‘adelante’ y ‘atrás’ el orden solo puede ser ‘h’ o ‘h2’
                - para el modo ‘centrada’ el orden solo puede ser ‘h2’ o ‘h4’
    derivada: float
        valor de la derivada en el punto suministrado

    Methods
    -------
    derivar(x: float):
        Evalua la derivada en el punto x de acuerdo al modo seleccionado
    graficar():
        Grafica la derivada resultante para punto dado

    Examples
    -------
    from mnspy import Richardson
    import numpy as np

    def g(x):
        return (x + 7) * (x + 2) * (x - 4) * (x - 12) / 100

    der = Derivada(g, orden='h2')
    der.derivar(2)
    print(der.derivada)

    ri = Richardson(g, orden='h2')
    ri.derivar(2)
    ri.graficar(2)
    print(ri.derivada)
    """
    def __init__(self, f: callable, n: int = 1, h: float = 1e-3, orden: str = 'h', modo: str = 'adelante'):
        """Clase para la implementación de la derivada Richardson

        Parameters
        ----------
        f: callable
            Función a la que derivará.
        n: int
            Es el grado de la derivada puede ser 1, 2, 3 y 4 (por defecto es 1 que es la primera derivada)
        h: float
            Valor del incrmento de las abcisas para el cáculo de la derivada
        orden: str
            puede ser ‘h’, ‘h2’ y ‘h4’
                - para el modo ‘adelante’ y ‘atrás’ el orden solo puede ser ‘h’ o ‘h2’
                - para el modo ‘centrada’ el orden solo puede ser ‘h2’ o ‘h4’
        modo: str
            puede se ‘adelante’, ‘atrás’ y ‘centrada’
        """
        super().__init__(f, n, h, orden, modo)

    def derivar(self, x: float):
        """
        Evalua la derivada en el punto x de acuerdo al modo seleccionado

        Parameters
        ----------
        x: float
            posición en x en que se evaluará la derivada, el resultado se almacenará en el atributo derivada

        Returns
        -------
        None
        """
        s = 0
        self._h *= 0.5
        super().derivar(x)
        s += 4 * self.derivada / 3
        self._h *= 2
        super().derivar(x)
        s -= self.derivada / 3
        self.derivada = s

    def graficar(self, x: float, x_min: float = None, x_max: float = None, delta: float = 10) -> None:
        """
        Grafica la derivada en la posición x seleccionada

        Parameters
        ----------
        x: float
            posición en x en que se dibujará la derivada
        x_min: float
            valor mínimo de la gráfica en x
        x_max: float
            valor máximo de la gráfica en x
        delta: float
            rango de la gráfica en x (x_max - x_min)

        Returns
        -------
        Gráfica de la derivada de la función en la posición x suministrada.
        Se usa el paquete matplotlib para la gráfica.
        """
        n = self._n
        self._n = 1
        self.derivar(x)
        self._n = n
        if x_min is None:
            x_min = x - delta
        if x_max is None:
            x_max = x + delta
        if self._orden == 'h':
            orden = r'$\mathcal{O}(h)$'
        elif self._orden == 'h2':
            orden = r'$\mathcal{O}(h^{2})$'
        else:
            orden = r'$\mathcal{O}(h^{4})$'
        y = self._f(x)
        x_list = np.linspace(x_min, x_max, 100)
        y_list = self._f(x_list)
        plt.scatter(x, y, c='r', lw=2, label='Punto (' + str(x) + ', ' + str(self._f(x)) + ')')
        plt.plot(x_list, y_list, linestyle='-', c='b', lw=2, label='Función')
        plt.title('Derivada = ' + str(self.derivada))
        plt.suptitle('Derivada Richardson, $h_{1}$ = ' + str(self._h) + ', $h_{2}$ = ' + str(
            self._h / 2) + ', modo = ' + self._modo + ', orden = ' + orden)
        plt.axline((x, y), slope=self.derivada, linestyle='dashed', c='r', lw=2,
                   label='Derivada')
        plt.grid()
        plt.legend()
        plt.show()


def main():
    def g(x):
        return (x + 7) * (x + 2) * (x - 4) * (x - 12) / 100

    der = Derivada(g, orden='h2')
    der.derivar(2)
    print(der.derivada)

    ri = Richardson(g, orden='h2')
    ri.derivar(2)
    ri.graficar(2)
    print(ri.derivada)


if __name__ == '__main__':
    main()
