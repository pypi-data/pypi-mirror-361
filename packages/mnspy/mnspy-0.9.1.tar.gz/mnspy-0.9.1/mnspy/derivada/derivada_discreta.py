import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update(plt.rcParamsDefault)

class DerivadaDiscreta:
    """Clase para la implementación de la derivada de puntos discretos.

    Attributes
    ----------
    _x: ndarray
        array con los datos de la variable independiente
    _y: ndarray
        array con los datos de la variable dependiente
    _modo: str
        string con el modo de derivada a realizar
    derivada: ndarray
        array con los valores de la derivada calculada

    Methods
    -------
    _derivar():
        Evalua la derivada de un array de acuerdo al modo seleccionado
    graficar():
        Grafica los datos y la derivada resultante para esos puntos

    Examples
    -------
    from mnspy import DerivadaDiscreta
    import numpy as np

    t = np.array(
        [4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.2, 5.4, 5.6, 5.8, 6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8, 8.0])
    x = np.array(
        [-5.87, -4.23, -2.55, -0.89, 0.67, 2.09, 3.31, 4.31, 5.06, 5.55, 5.78, 5.77, 5.52, 5.08, 4.46, 3.72, 2.88, 2.00,
         1.10, 0.23, -0.59])
    vel = DerivadaDiscreta(t, x, modo='centrada')
    vel.graficar('Derivada x contra t', '$t$', '$x$', '$v$')
    print(vel.derivada)
    """

    def __init__(self, x: np.array, y: np.array, modo: str = 'centrada'):
        """Constructor de la clase DerivadaDiscreta

        Parameters
        ----------
        x: ndarray
            Array con los datos de la variable independiente
        y: ndarray
            Array con los datos de la variable dependiente
        modo: str
            tipo de derivada que se realizará, las opciones son:
            'adelante':
                se deriva hacia adelante los puntos, excepto el último que su derivada se calculará hacia atrás.
            'atrás':
                se deriva hacia atrás los puntos, excepto el primer punto que su derivada se calculará hacia adelante
            'centrada':
                se deriva centrada los puntos, excepto el primer punto que su derivada se calculará hacia adelante
                y el último punto que su derivada se realizará hacia atrás
        """
        self._x = x
        self._y = y
        self._modo = modo
        self.derivada = 0.0
        self._derivar()
        plt.ioff()  # deshabilitada interactividad matplotlib

    def _derivar(self):
        """
        Evalua la derivada de un array de acuaerdo al modo seleccionado y el resultado se almacena
        en el atributo derivada.

        Returns
        -------
        None
        """
        self.derivada = np.array([])
        if self._modo == 'adelante':
            for i in range(len(self._x) - 1):
                self.derivada = np.append(self.derivada, (self._y[i + 1] - self._y[i]) / (self._x[i + 1] - self._x[i]))
            self.derivada = np.append(self.derivada, (self._y[-1] - self._y[-2]) / (self._x[-1] - self._x[-2]))
        elif self._modo == 'atrás':
            self.derivada = np.append(self.derivada, (self._y[1] - self._y[0]) / (self._x[1] - self._x[0]))
            for i in range(1, len(self._x)):
                self.derivada = np.append(self.derivada, (self._y[i] - self._y[i - 1]) / (self._x[i] - self._x[i - 1]))
        elif self._modo == 'centrada':
            self.derivada = np.append(self.derivada, (self._y[1] - self._y[0]) / (self._x[1] - self._x[0]))
            for i in range(1, len(self._x) - 1):
                self.derivada = np.append(self.derivada,
                                          (self._y[i + 1] - self._y[i - 1]) / (self._x[i + 1] - self._x[i - 1]))
            self.derivada = np.append(self.derivada, (self._y[-1] - self._y[-2]) / (self._x[-1] - self._x[-2]))
        else:
            print('nombre de modo de derivada \'' + self._modo + '\' no valido')

    def graficar(self, label_tit: str = '', label_x: str = '', label_y: str = '', label_der: str = '') -> None:
        """
        Grafica los datos y la derivada resultante para esos puntos

        Parameters
        ----------
        label_tit: str
            Título asignado a la gráfica
        label_x: str
            Título asignado al eje x
        label_y: str
            Título asignado al eje y de la función
        label_der: str
            Título asignado al eje y de la derivada

        Returns
        -------
        Gráfica de los datos y la derivada realizada usando el paquete de matplotlib
        """
        fig, axs = plt.subplots(2, 1, sharex=True)
        axs[0].plot(self._x, self._y, 'o-', c='b', lw=2, label='Función')
        axs[0].set_ylabel(label_y)
        axs[0].title.set_text('Datos')
        axs[0].legend()
        axs[0].grid()
        axs[1].plot(self._x, self.derivada, 'o-', c='r', lw=2, label='Derivada')
        axs[1].set_ylabel(label_der)
        axs[1].set_xlabel(label_x)
        axs[1].title.set_text('Derivada modo =  ' + self._modo)
        axs[1].legend()
        axs[1].grid()
        fig.suptitle(label_tit)
        plt.show()

def main():
    t = np.array(
        [4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.2, 5.4, 5.6, 5.8, 6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8, 8.0])
    x = np.array(
        [-5.87, -4.23, -2.55, -0.89, 0.67, 2.09, 3.31, 4.31, 5.06, 5.55, 5.78, 5.77, 5.52, 5.08, 4.46, 3.72, 2.88, 2.00,
         1.10, 0.23, -0.59])
    vel = DerivadaDiscreta(t, x, modo='centrada')
    vel.graficar('Derivada x contra t', '$t$', '$x$', '$v$')
    print(vel.derivada)


if __name__ == '__main__':
    main()