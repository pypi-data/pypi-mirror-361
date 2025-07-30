
# v0.2.5
"""Micromódulo para imprimir mensajes en consola con texto de colores.

Este módulo permite personalizar mensajes dinámicos en consola, incluyendo
texto en diferentes colores.

Historial de versiones:
- `v0.2.5`: Corrección de errores menores y actualización de enlaces.
- `v0.2.4`: Añadí "nuevos" métodos `sug_bg`, `warn_bg`, `err_bg`, `exc_bg`, `inf_bg` los cuales y actualicé los links
- `v0.2.3`: Errores menores
- `v0.2.2`: Actualización la versión de python requerida
- `v0.2.1`: Actualización de enlaces
- `v0.2.0`: Mejoras del proyecto, ahora solo debe importar: `import chromolog`.
- `v0.1.1`: Corrección de errores de la página del proyecto en https://pypi.org
- `v0.1.0`: Primera versión funcional.

Revise el historial completo aquí: [Historial completo de veriones](https://github.com/Dev2Forge/chromolog/#historial-de-versiones)

@author Tutos Rive

Si desea conocer más acerca de, visite:
- [Web de soporte](https://docs.dev2forge.software/chromolog/)
- [Web pypi.org](https://pypi.org/project/chromolog/)
- [Github project](https://github.com/Dev2Forge/chromolog/)
"""

# Soluciona el problema de colores en Windows
import colorama
colorama.init()

__version__ = "0.2.5"
__author__ = "Tutos Rive"

class Print:
    """Imprimir mensajes por consola con color de texto (`error`, `warning`, `succes`, `info`)
    """
    def __init__(self) -> None:
        self.RES = '\033[0m' # Resetear color
        self.RED = '\033[31m'
        self.YELLOW = '\033[33m'
        self.BLUE = '\033[34m'
        self.GREEN = '\033[32m'
        self.BG_RED = '\033[41m' # Fondo rojo
        self.BG_BLUE = '\033[44m' # Fondo azul
        self.BG_YELLOW = '\033[43m' # Fondo amarillo
        self.BG_GREEN = '\033[42m' # Fondo verde

    def __str__(self):
        return f'Módulo: chromolog\nClase principal: `Print`\nVersión: {__version__}\nAutor: {__author__}'

    def err(self, err:any) -> None:
        """Imprimir errores (Color Texto: Rojo)

        Args:
            `err:any`: Error que se imprimirá
        """
        self.__w(f'{self.RED}{err}{self.RES}')
    
    def err_bg(self, err: any) -> None:
        """Imprimir errores (Color Texto: Blanco, Color Fondo: Rojo)

        Args:
            `err:any`: Error que se imprimirá
        """
        self.__w(f'{self.BG_RED}{err}{self.RES}')
    
    def exc(self, exc: Exception) -> None:
        """Imprimir errores de Excepciones específicas (Color Texto: Rojo)

        Args:
            `exc:Exception`: Excepción capturada con bloque try
        """
        trace:dict = self.__traceback(exc)
        self.err(f'Exception: {exc.__class__.__name__}\nFile: {trace.get("path")}\nErrorLine: {trace.get("line")}\nMesssage: {exc}')

    def exc_bg(self, exc: Exception) -> None:
        """Imprimir errores de Excepciones específicas (Color Texto: Blanco, Color Fondo: Rojo)

        Args:
            `exc:Exception`: Excepción capturada con bloque try
        """
        trace:dict = self.__traceback(exc)
        self.err_bg(f'Exception: {exc.__class__.__name__}\nFile: {trace.get("path")}\nErrorLine: {trace.get("line")}\nMesssage: {exc}')

    def inf(self, inf:any) -> None:
        """Imprimir información (Color Texto: Azul)

        Args:
            `inf:any`: Información que se imprimirá
        """
        self.__w(f'{self.BLUE}{inf}{self.RES}')

    def inf_bg(self, inf: any) -> None:
        """Imprimir información (Color Texto: (Por defecto, según contraste), Color Fondo: Azul)

        Args:
            `inf:any`: Información que se imprimirá
        """
        self.__w(f'{self.BG_BLUE}{inf}{self.RES}')

    def warn(self, warn:any) -> None:
        """Imprimir mensajes de precaución (Color Texto: Amarillo)

        Args:
            `warn:any`: Mensaje que se imprimirá
        """
        self.__w(f'{self.YELLOW}{warn}{self.RES}')

    def warn_bg(self, warn: any) -> None:
        """Imprimir mensajes de precaución (Color Texto: (Por defecto, según contraste), Color Fondo: Amarillo)  
           Args:
               `warn:any`: Mensaje que se imprimirá
        """
        self.__w(f'{self.BG_YELLOW}{warn}{self.RES}')

    def suc(self, suc:any) -> None:
        """Imprimir mensajes de éxito (Final de ejecución, podría ser...) (Color Texto: Verde)

        Args:
            `suc:any`: Mensaje que se imprimirá
        """
        self.__w(f'{self.GREEN}{suc}{self.RES}')

    def suc_bg(self, suc:any) -> None:
        """Imprimir mensajes de éxito (Final de ejecución, podría ser...) (Color Texto: (Por defecto, según contraste), Color Fondo: Verde)

        Args:
            `suc:any`: Mensaje que se imprimirá
        """
        self.__w(f'{self.BG_GREEN}{suc}{self.RES}')

    def __w(self, msg:any) -> None:
        """Imprimir mensaje con colores

        Args:
            `msg:any`: Mensaje que se imprimirá
        """
        print(msg)
    
    def __traceback(self, e:Exception) -> dict:
        """Obtener un registro preciso de la excepción

        Args:
            `e:Exception`: Excepción con la cual se trabajará

        Returns:
            `dict`: Diccionario con claves: {`line`: (Línea del error),`path`: (Ruta del archivo de error)}
        """
        import traceback
        trace_back = traceback.extract_tb(e.__traceback__)
        return {'line': trace_back[-1][1], 'path': trace_back[-1][0]}

    def test(self) -> None:
        """Ejecutar prueba
        """
        try:
            a = ''
            a += 12
        except TypeError as e:
            self.exc(e)
        self.inf('inf(inf) -> Hello World')
        self.err(f'err(err) -> Ha ocurrido un error menor')
        self.warn('warn(warn) -> Precaución, tenga cuidado')
        self.suc('suc(suc) -> Ejecución finalizada...')
        self.inf('-------\nFondos de colores')
        try:
            a = ''
            a += 12
        except TypeError as e:
            self.exc_bg(e)
        self.inf_bg('inf(inf) -> Hello World')
        self.err_bg(f'err(err) -> Ha ocurrido un error menor')
        self.warn_bg('warn(warn) -> Precaución, tenga cuidado')
        self.suc_bg('suc(suc) -> Ejecución finalizada...')

if __name__ == '__main__':
    p = Print()
    p.test()