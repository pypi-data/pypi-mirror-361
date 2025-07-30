import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class Derivada:
    """Clase para la implementación de la derivada.

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
    from mnspy import Derivada
    import numpy as np

    def g(x):
        return (x + 7) * (x + 2) * (x - 4) * (x - 12) / 100

    der = Derivada(g, orden='h1', n=4)
    der.derivar(2)
    print(der.derivada)
    der = Derivada(g, orden='h1', modo='atrás', n=4)
    der.derivar(2)
    print(der.derivada)
    der = Derivada(g, orden='h', modo='atrás', h=0.4)
    der.derivar(2)
    print(der.derivada)
    der.graficar(2, 1.5, 2.5)
    print(der.derivada)
    """
    def __init__(self, f: callable, n: int = 1, h: float = 1e-3, orden: str = 'h', modo: str = 'adelante'):
        """Clase para la implementación de la derivada

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
        self._f = f
        self._n = n
        self._h = h
        self._orden = orden
        self._modo = modo
        self.derivada = 0.0
        plt.ioff()  # deshabilitada interactividad matplotlib

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
        if self._modo == 'adelante':
            if self._n == 1:
                if self._orden == 'h':
                    self.derivada = (self._f(x + self._h) - self._f(x)) / self._h
                else:
                    self.derivada = (-self._f(x + 2 * self._h) + 4 * self._f(x + self._h) - 3 * self._f(x)) / (
                            2 * self._h)
            elif self._n == 2:
                if self._orden == 'h':
                    self.derivada = (self._f(x + 2 * self._h) - 2 * self._f(x + self._h) + self._f(x)) / (
                            self._h ** 2)
                else:
                    self.derivada = (-self._f(x + 3 * self._h) + 4 * self._f(x + 2 * self._h) - 5 * self._f(
                        x + self._h) + 2 * self._f(x)) / (self._h ** 2)
            elif self._n == 3:
                if self._orden == 'h':
                    self.derivada = (self._f(x + 3 * self._h) - 3 * self._f(x + 2 * self._h) + 3 * self._f(
                        x + self._h) - self._f(x)) / (self._h ** 3)
                else:
                    self.derivada = (-3 * self._f(x + 4 * self._h) + 14 * self._f(x + 3 * self._h) - 24 * self._f(
                        x + 2 * self._h) + 18 * self._f(x + self._h) - 5 * self._f(x)) / (2 * self._h ** 3)
            else:
                if self._orden == 'h':
                    self.derivada = (self._f(x + 4 * self._h) - 4 * self._f(x + 3 * self._h) + 6 * self._f(
                        x + 2 * self._h) - 4 * self._f(x + self._h) + self._f(x)) / (self._h ** 4)
                else:
                    self.derivada = (- 2 * self._f(x + 5 * self._h) + 11 * self._f(x + 4 * self._h) - 24 * self._f(
                        x + 3 * self._h) + 26 * self._f(x + 2 * self._h) - 14 * self._f(x + self._h) + 3 * self._f(
                        x)) / (
                                            self._h ** 4)
        elif self._modo == 'atrás':
            if self._n == 1:
                if self._orden == 'h':
                    self.derivada = (self._f(x) - self._f(x - self._h)) / self._h
                else:
                    self.derivada = (3 * self._f(x) - 4 * self._f(x - self._h) + self._f(x - 2 * self._h)) / (
                            2 * self._h)
            elif self._n == 2:
                if self._orden == 'h':
                    self.derivada = (self._f(x) - 2 * self._f(x - self._h) + self._f(x - 2 * self._h)) / (
                            self._h ** 2)
                else:
                    self.derivada = (2 * self._f(x) - 5 * self._f(x - self._h) + 4 * self._f(
                        x - 2 * self._h) - self._f(
                        x - 3 * self._h)) / (self._h ** 2)
            elif self._n == 3:
                if self._orden == 'h':
                    self.derivada = (self._f(x) - 3 * self._f(x - self._h) + 3 * self._f(x - 2 * self._h) - self._f(
                        x - 3 * self._h)) / (self._h ** 3)
                else:
                    self.derivada = (5 * self._f(x) - 18 * self._f(x - self._h) + 24 * self._f(
                        x - 2 * self._h) - 14 * self._f(x - 3 * self._h) + 3 * self._f(x - 4 * self._h)) / (
                                            2 * self._h ** 3)
            else:
                if self._orden == 'h':
                    self.derivada = (self._f(x) - 4 * self._f(x - self._h) + 6 * self._f(
                        x - 2 * self._h) - 4 * self._f(
                        x - 3 * self._h) + self._f(x - 4 * self._h)) / (self._h ** 4)
                else:
                    self.derivada = (3 * self._f(x) - 14 * self._f(x - self._h) + 26 * self._f(
                        x - 2 * self._h) - 24 * self._f(x - 3 * self._h) + 11 * self._f(
                        x - 4 * self._h) - 2 * self._f(
                        x - 5 * self._h)) / (self._h ** 4)
        else:
            self._modo = 'centrada'
            if self._n == 1:
                if self._orden == 'h2':
                    self.derivada = (self._f(x + self._h) - self._f(x - self._h)) / (2 * self._h)
                else:
                    self.derivada = (-self._f(x + 2 * self._h) + 8 * self._f(x + self._h) - 8 * self._f(
                        x - self._h) + self._f(
                        x - 2 * self._h)) / (12 * self._h)
            elif self._n == 2:
                if self._orden == 'h2':
                    self.derivada = (self._f(x + self._h) - 2 * self._f(x) + self._f(x - self._h)) / (self._h ** 2)
                else:
                    self.derivada = (-self._f(x + 2 * self._h) + 16 * self._f(x + self._h) - 30 * self._f(
                        x) + 16 * self._f(
                        x - self._h) - self._f(x - 2 * self._h)) / (12 * self._h ** 2)
            elif self._n == 3:
                if self._orden == 'h2':
                    self.derivada = (self._f(x + 2 * self._h) - 2 * self._f(x + self._h) + 2 * self._f(
                        x - self._h) - self._f(
                        x - 2 * self._h)) / (2 * self._h ** 3)
                else:
                    self.derivada = (-self._f(x + 3 * self._h) + 8 * self._f(x + 2 * self._h) - 13 * self._f(
                        x + self._h) + 13 * self._f(x - self._h) - 8 * self._f(x - 2 * self._h) + self._f(
                        x - 3 * self._h)) / (
                                            8 * self._h ** 3)
            else:
                if self._orden == 'h2':
                    self.derivada = (self._f(x + 2 * self._h) - 4 * self._f(x + self._h) + 6 * self._f(
                        x) - 4 * self._f(
                        x - self._h) + self._f(x - 2 * self._h)) / (self._h ** 4)
                else:
                    self.derivada = (-self._f(x + 3 * self._h) + 12 * self._f(x + 2 * self._h) - 39 * self._f(
                        x + self._h) + 56 * self._f(x) - 39 * self._f(x - self._h) + 12 * self._f(
                        x - 2 * self._h) - self._f(
                        x - 3 * self._h)) / (6 * self._h ** 4)

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
        plt.suptitle('h = ' + str(self._h) + ', modo = ' + self._modo + ', orden = ' + orden)
        plt.axline((x, y), slope=self.derivada, linestyle='dashed', c='r', lw=2,
                   label='Derivada')
        plt.grid()
        plt.legend()
        plt.show()



def main():
    def g(x):
        return (x + 7) * (x + 2) * (x - 4) * (x - 12) / 100

    der = Derivada(g, orden='h1', n=4)
    der.derivar(2)
    print(der.derivada)
    der = Derivada(g, orden='h1', modo='atrás', n=4)
    der.derivar(2)
    print(der.derivada)
    der = Derivada(g, orden='h', modo='atrás', h=0.4)
    der.derivar(2)
    print(der.derivada)
    der.graficar(2, 1.5, 2.5)
    print(der.derivada)


if __name__ == '__main__':
    main()
