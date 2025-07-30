import numpy as np
import matplotlib.pyplot as plt
from mnspy.utilidades import es_notebook
from tabulate import tabulate
import math
import sys
plt.rcParams.update(plt.rcParamsDefault)

class Raices:
    """
    Clase base para las demás clases que implementan métodos para el cálculo de raíces de ecuaciones.

    Attributes
    ----------
    _f: callable
        función a la que se le hallará las raíces
    _x_min: float
        mínimo valor de x, por defecto es None y solo aplica en métodos cerrados
    _x_max: float
        máximo valor de x, por defecto es None y solo aplica en métodos cerrados
    _tol: float | int
        máxima tolerancia del error
    _max_iter: int
        número máximo de iteraciones permitido para hallar la raíz
    _error_porcentual : bool
            si es verdadero corresponde al error aproximado relativo porcentual, en caso contrario corresponde a
            un error aproximado relativo.

    Methods
    -------
    formato_tabla(llave: str, fmt: str):
        Ajusta el formato de presentación de los datos en las tablas.
    generar_tabla(tablefmt:str = None):
        Genera una tabla con las iteraciones realizadas.
    _agregar_iteracion():
        Agrega los datos de la iteración a un atributo de la clase llamado tabla.
    _fin_iteracion():
        Retorna un booleano de acuerdo si debe finalizar las iteraciones
    graficar(mostrar_sol: bool, mostrar_iter: bool, mostrar_lin_iter: bool, n_puntos: int):
        Realiza la gráfica del cálculo de la raíz según el método.
    _derivada(x: float, h: float):
        Cálculo de la derivada numérica de la función.
    solucion():
        Presenta los resultados finales de la iteración

    Examples:
    -------
    from mnspy import Raices
    import numpy as np

    def f(x):
        return 667.38 * (1 - np.exp(-0.146843 * x)) / x - 40

    graf = Raices(f, 12, 16)
    graf.generar_tabla()
    graf.graficar()

    def z(x):
        return x ** 2 - 9

    graf = Raices(z, 0, 5)
    graf.graficar()
    """

    def __init__(self, f: callable, x_min: float = None, x_max: float = None, tol: float | int = 1e-3,
                 max_iter: int = 20, tipo_error: str = '%'):
        """
        Constructor de la clase base raíces.

        Parameters
        ----------
        f: callable
            función a la que se le hallará las raíces
        x_min: float
            mínimo valor de x, por defecto es None y solo aplica en métodos cerrados
        x_max: float
            máximo valor de x, por defecto es None y solo aplica en métodos cerrados
        tol: float | int
            máxima tolerancia del error
        max_iter: int
            número máximo de iteraciones permitido para hallar la raíz
        tipo_error: str
            tipo de error '%' corresponde al error aproximado relativo porcentual εa = 100*error_aproximado/aproximación
            tipo de error '/' corresponde al error aproximado relativo εa = error_aproximado/aproximación
            tipo de error 'n' corresponde a n cifras significativas εs = (0.5 * 10^(2-n)) %  (Scarborough, 1966)
        """
        self._f = f
        self._tol = tol
        # tipo de error es '%' , '/' o 'n'
        match tipo_error:
            case "%":
                self._error_porcentual = True
            case "/":
                self._error_porcentual = False
            case "n":
                self._tol = 0.5 * 10 ** (2 - tol)
                self._error_porcentual = True
            case _:
                print("Tipo de error no valido, las opciones son: '%', '/', 'n'")
                sys.exit()
        self._max_iter = max_iter
        self._x_min = x_min
        self._x_max = x_max
        self.x = 0
        self._x_0 = None
        self._x_1 = None
        self._tabla = {'x_min': [], 'x_max': [], 'x': [], 'Ea': []}
        self._fmt = {'iter': 'd', 'x_l': '.5f', 'x_u': '.5f', 'x': '.10f', 'f': '.8f', 'E_a': '0.5%', 'E_t': '0.5%'}
        self._converge = False
        self._rango = x_min, x_max
        plt.ioff()  # deshabilitada interactividad matplotlib

    def formato_tabla(self, col: str, fmt: str) -> None:
        """
        Ajusta el formato de presentación de los datos en las tablas.

        Por defecto el formato es
        {'iter': 'd', 'x_l': '.5f', 'x_u': '.5f', 'x': '.10f', 'f': '.8f', 'E_a': '0.5%', 'E_t': '0.5%'}

        Parameters
        ----------
        col: str
            nombre de la columna que desea ajustarle el formato
        fmt: str
            formato de los datos presentados

        Returns
        -------
        None
        """
        if col == 'x_r' or col == 'x_i':
            col = 'x'
        self._fmt[col] = fmt

    def generar_tabla(self, valor_real: float = None, tablefmt=None):
        """
        Genera una tabla con las iteraciones realizadas.

        Parameters
        ----------
        valor_real: float
            si se ingresa este valor, la tabla muestra el error porcentual real
        tablefmt: str
            formato de la tabla de acuertdo al paquete tabulate, por defecto es None y si está en notebook
            lo presenta en formato 'html', en caso contario el formato por defecto es 'simple'

        Returns
        -------
        display renderizado de la tabla (solo en notebook) o la impresión de la tabla.
        """
        if type(self) is Raices:  # Si la clase es Raíces, no tiene método asociado y solo sirve para graficar
            print('No se generó tabla')
            return
        render_notebook = ['html', 'unsafehtml']
        if self._x_min is not None:
            valores = np.array(
                [self._tabla['x_min'], self._tabla['x_max'], self._tabla['x'], [self._f(val) for val in self._tabla['x']],
                 self._tabla['Ea']]).transpose()
            if es_notebook() and (tablefmt is None or tablefmt in render_notebook):
                if tablefmt is None:
                    tablefmt = 'html'
                if valor_real is None:
                    return tabulate(valores, ['Iteración', '$x_{l}$', '$x_{u}$', '$x_{r}$', r'$f\left(x_{r}\right)$',
                                              r'$\varepsilon_{a}$'], showindex=list(range(1, len(self._tabla['x']) + 1)),
                                    tablefmt=tablefmt, floatfmt=(
                            self._fmt['iter'], self._fmt['x_l'], self._fmt['x_u'], self._fmt['x'], self._fmt['f'],
                            self._fmt['E_a']), colalign=("center",))
                else:
                    e_t = abs((np.array([self._tabla['x']]).transpose() - valor_real) / valor_real)
                    valores = np.hstack((valores, e_t))
                    return tabulate(valores, ['Iteración', '$x_{l}$', '$x_{u}$', '$x_{r}$', r'$f\left(x_{r}\right)$',
                                              r'$\varepsilon_{a}$', r'$\varepsilon_{t}$'],
                                    showindex=list(range(1, len(self._tabla['x']) + 1)), tablefmt=tablefmt, floatfmt=(
                            self._fmt['iter'], self._fmt['x_l'], self._fmt['x_u'], self._fmt['x'], self._fmt['f'],
                            self._fmt['E_a'], self._fmt['E_t']), colalign=("center",))
            else:
                if tablefmt is None:
                    tablefmt = 'simple'
                if valor_real is None:
                    print(tabulate(valores, ['Iteración', 'x_l', 'x_u', 'x_r', 'f(x_r)', 'E_a'],
                                   showindex=list(range(1, len(self._tabla['x']) + 1)), tablefmt=tablefmt,
                                   floatfmt=(
                                       self._fmt['iter'], self._fmt['x_l'], self._fmt['x_u'], self._fmt['x'], self._fmt['f'],
                                       self._fmt['E_a']), colalign=("center",)))
                else:
                    e_t = abs((np.array([self._tabla['x']]).transpose() - valor_real) / valor_real)
                    valores = np.hstack((valores, e_t))
                    print(tabulate(valores, ['Iteración', 'x_l', 'x_u', 'x_r', 'f(x_r)', 'E_a', 'E_t'],
                                   showindex=list(range(1, len(self._tabla['x']) + 1)), tablefmt=tablefmt,
                                   floatfmt=(
                                       self._fmt['iter'], self._fmt['x_l'], self._fmt['x_u'], self._fmt['x'], self._fmt['f'],
                                       self._fmt['E_a'], self._fmt['E_t']), colalign=("center",)))
        else:
            valores = np.array([self._tabla['x'], self._f(np.array(self._tabla['x'])), self._tabla['Ea']]).transpose()
            if es_notebook() and (tablefmt is None or tablefmt in render_notebook):
                if tablefmt is None:
                    tablefmt = 'html'
                if valor_real is None:
                    return tabulate(valores, ['Iteración', '$x_{i}$', r'$f\left(x_{i}\right)$', r'$\varepsilon_{a}$'],
                                    showindex=list(range(1, len(self._tabla['x']) + 1)), tablefmt=tablefmt,
                                    floatfmt=(self._fmt['iter'], self._fmt['x'], self._fmt['f'], self._fmt['E_a']),
                                    colalign=("center",))
                else:
                    e_t = abs((np.array([self._tabla['x']]).transpose() - valor_real) / valor_real)
                    valores = np.hstack((valores, e_t))
                    return tabulate(valores, ['Iteración', '$x_{i}$', r'$f\left(x_{i}\right)$', r'$\varepsilon_{a}$',
                                              r'$\varepsilon_{t}$'], showindex=list(range(1, len(self._tabla['x']) + 1)),
                                    tablefmt=tablefmt,
                                    floatfmt=(
                                        self._fmt['iter'], self._fmt['x'], self._fmt['f'], self._fmt['E_a'],
                                        self._fmt['E_t']),
                                    colalign=("center",))
            else:
                if tablefmt is None:
                    tablefmt = 'simple'
                if valor_real is None:
                    print(tabulate(valores, ['Iteración', 'x_i', 'f(x_i)', 'E_a'],
                                   showindex=list(range(1, len(self._tabla['x']) + 1)), tablefmt=tablefmt,
                                   floatfmt=(self._fmt['iter'], self._fmt['x'], self._fmt['f'], self._fmt['E_a']),
                                   colalign=("center",)))
                else:
                    e_t = abs((np.array([self._tabla['x']]).transpose() - valor_real) / valor_real)
                    valores = np.hstack((valores, e_t))
                    print(tabulate(valores, ['Iteración', 'x_i', 'f(x_i)', 'E_a', 'E_t'],
                                   showindex=list(range(1, len(self._tabla['x']) + 1)), tablefmt=tablefmt,
                                   floatfmt=(
                                       self._fmt['iter'], self._fmt['x'], self._fmt['f'], self._fmt['E_a'],
                                       self._fmt['E_t']),
                                   colalign=("center",)))

    def _agregar_iteracion(self) -> None:
        """
        Agrega los datos de la iteración a un atributo de la clase llamado tabla.

        Returns
        -------
        None
        """
        self._tabla['x_min'].append(self._x_min)
        self._tabla['x_max'].append(self._x_max)
        self._tabla['x'].append(self.x)
        if len(self._tabla['x']) > 1:
            self._tabla['Ea'].append(math.fabs((self._tabla['x'][-1] - self._tabla['x'][-2]) / self._tabla['x'][-1]))
        else:
            self._tabla['Ea'].append(math.nan)

    def _fin_iteracion(self) -> bool:
        """
        Retorna un booleano de acuerdo si debe finalizar las iteraciones

        Solo finaliza si alcanzó el error permitido o llegó al máximo de iteraciones.

        Returns
        -------
        bool con la condición si debe finalizar la iteración
        """
        lon = len(self._tabla['x'])
        if lon >= self._max_iter:
            self._converge = False
            return True
        self._agregar_iteracion()
        if self._error_porcentual:
            lon = len(self._tabla['x'])
            if lon > 1:
                if self._tabla['Ea'][-1] * 100 < self._tol:
                    self._converge = True
                    return True
                else:
                    return False
            else:
                return False
        else:
            lon = len(self._tabla['x'])
            if lon > 1:
                if self._tabla['Ea'][-1] < self._tol:
                    self._converge = True
                    return True
                else:
                    return False
            else:
                return False

    def graficar(self, mostrar_sol: bool = False, mostrar_iter: bool = False, mostrar_lin_iter: bool = False,
                 n_puntos: int = 100):
        """
        Realiza la gráfica del cálculo de la raíz según el método.

        Parameters
        ----------
        mostrar_sol: bool
            si es verdadero muestra el punto donde se encontró la solución
            por defecto es False
        mostrar_iter: bool
            si es verdadero muestra los puntos obtenidos de cada iteración
            por defecto es False
        mostrar_lin_iter: bool
            si es verdadero muestra las líneas auxiliares que se usan para obtener la solución
            por defecto es False
        n_puntos: int
            Número de puntos de la gráfica por defecto 100

        Returns
        -------
        gráfica usando el paquete matplotlib
        """
        if self._rango[0] is None or self._rango[1] is None:
            if self._x_1 is None:
                x = np.linspace(min(self._tabla['x'] + [self._x_0]), max(self._tabla['x'] + [self._x_0]), n_puntos)
            else:
                x = np.linspace(min(self._tabla['x'] + [self._x_0, self._x_1]),
                                max(self._tabla['x'] + [self._x_0, self._x_1]),
                                100)
        else:
            x = np.linspace(self._rango[0], self._rango[1], n_puntos)
        y = [self._f(val) for val in x]
        plt.plot(x, y, c='b', lw=2, label='Función')
        if mostrar_iter and len(self._tabla['x']) > 0:
            plt.scatter(self._tabla['x'], [self._f(val) for val in self._tabla['x']], c='g', alpha=0.5,
                        label='Iteraciones', zorder=3)
            for i, dato in enumerate(self._tabla['x']):
                plt.annotate(str(i + 1), (dato, self._f(dato)), c='g', alpha=0.95, textcoords="offset points",
                             xytext=(0, 10),
                             ha='center', zorder=3)
        if mostrar_sol and len(self._tabla['x']) > 0:
            plt.scatter(self.x, self._f(self.x), c='r', marker='o', label='Solución', zorder=4)
        if mostrar_lin_iter:
            if self._x_0 is not None and self._x_1 is None:
                plt.scatter(self._x_0, self._f(self._x_0), c='purple', marker='X', label='Punto inicial', zorder=3)
            if self._x_0 is not None and self._x_1 is not None:
                plt.scatter([self._x_0, self._x_1], [self._f(self._x_0), self._f(self._x_1)], c='purple', marker='X',
                            label='Puntos iniciales', zorder=3)
        plt.grid()
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.axhline(color='black')
        plt.legend()
        plt.show()

    def _derivada(self, x: float, h: float = 0.001) -> float:
        """
        Cálculo de la derivada numérica de la función.

        Solo se usa en el método de Newton Raphson en el caso de que no se entre el valor de la derivada.
        Parameters
        ----------
        x: float
            valor de la ordenada donde se realizará la derivada
        h: float
            delta del valor de x para el cálculo de la derivada

        Returns
        -------
        derivada de la función en el punto x
        """
        return (self._f(x + h) - self._f(x)) / h

    def solucion(self):
        """
        Presenta los resultados finales de la iteración

        Returns
        -------
        Tabla con los resultados finales de la iteración.
        """
        if self._converge:
            if es_notebook():
                valores = [['$x$:', self.x], ['$f(x)$:', self._f(self.x)],
                           ['$\\varepsilon_{a}[\\%]$:', self._tabla['Ea'][-1] * 100],
                           ['Número de iteraciones:', len(self._tabla['x'])]]
                return tabulate(valores, tablefmt='html', colalign=('right', 'left'))
            else:
                valores = [['x:', self.x], ['f(x)', self._f(self.x)],
                           ['εa [%]:', self._tabla['Ea'][-1] * 100],
                           ['Número de iteraciones:', len(self._tabla['x'])]]
                print(tabulate(valores, tablefmt='simple', colalign=('right', 'left')))
        else:
            print("***** No converge a una solución en el máximo de iteraciones definidas *****")


def main():
    def f(x):
        return 667.38 * (1 - np.exp(-0.146843 * x)) / x - 40

    graf = Raices(f, 12, 16)
    graf.generar_tabla()
    graf.graficar()

    def z(x):
        return x ** 2 - 9

    graf = Raices(z, 0, 5)
    graf.graficar()


if __name__ == '__main__':
    main()
