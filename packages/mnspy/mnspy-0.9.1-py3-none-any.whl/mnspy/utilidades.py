from IPython.core.getipython import get_ipython
from IPython.display import display, Math, DisplayHandle
from numpy import matrix, ndarray, array2string, isclose


def es_notebook() -> bool:
    """
    Verifica si el paquete está ejecutandose en un notebook

    Returns
    -------
    True:
        Si está ejecutandose en un notebook
    False:
        Si no se está ejecutandose en un notebook
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True  # Jupyter notebook o qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal ejecutando IPython
        else:
            return False  # ¿otro tipo?
    except NameError:
        return False  # Probablemente otro intérprete standard de Python


def mostrar_matrix(m: ndarray, n_decimal: int = None, aumentada: int =None) -> DisplayHandle | None:
    """Convierte una matrix para su visualización en Latex si se encuentra en un notebook

    Parameters
    ----------
    m: ndarray
        Matrix a mostrar
    n_decimal: int
        Número de decimales
    aumentada: int
        Agrega una línea vertical a la matrix en la columna con el índice de "aumentada"
        contada apartir de la última columna

    Returns
    -------
    Render en latex de la matrix si se encuentra en un notebook, en caso contrario retorna la matrix en formato texto
    """
    m = matrix(m)
    if n_decimal is None:
        fmt = '{:}'
    else:
        fmt = '{:.' + str(n_decimal) + 'f}'
    if aumentada is None:
        texto_latex = r'\left[\begin{array}{' + 'c' * m.shape[1] + '}'
    else:
        texto_latex = r'\left[\begin{array}{' + 'c' * (m.shape[1] - aumentada) + '|' + 'c' * aumentada + '}'
    if es_notebook():
        texto_latex += _generar_matrix(m, fmt) + r'\end{array}\right]'
        return display(Math(texto_latex))
    else:
        print(array2string(m, formatter={'float_kind': lambda x: fmt.format(x)}))


def _generar_matrix(m: ndarray, fmt: str) -> str:
    """
    Convierte una matrix en na secuancia de datos en formato Latex

    Parameters
    ----------
    m: ndarray
        Matrix a mostrar
    fmt:
        formato aplicado a los elementos

    Returns
    -------
    String con la secuencia de datos de la matrix
    """
    ni, nj = m.shape
    texto_latex = ''
    for i in range(ni):
        for j in range(nj):
            texto_latex += fmt.format(m[i, j])
            if j != (nj - 1):
                texto_latex += '&'
        if i != (ni - 1):
            texto_latex += r'\\'
    return texto_latex

def _formato_float_latex(num: float, tol_cero: float = 1E-10, formato: str ='{:.10g}'):
    num = num if not isclose(num, 0.0, tol_cero, tol_cero) else 0.0
    cad = formato.format(num)
    if 'e' in cad:
        significando, exponente = cad.split('e')
        return r"{} \times 10^{{{}}}".format(significando, int(exponente))
    elif 'E' in cad:
        significando, exponente = cad.split('E')
        return r"{} \times 10^{{{}}}".format(significando, int(exponente))
    return cad