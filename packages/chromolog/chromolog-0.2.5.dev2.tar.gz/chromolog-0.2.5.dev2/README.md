# Chromolog

<div align="center" style="display: flex; align-items: center; justify-content: center; margin: 10px 0; gap: 10px; max-height: 48px; height: 48px;">
  <a href="https://github.com/sponsors/tutosrive" target="_blank">
  <img src="https://img.shields.io/badge/Sponsor-%F0%9F%92%96%20Dev2Forge-blue?style=for-the-badge&logo=github" alt="Sponsor me on GitHub">
</a>
  <a href="https://ko-fi.com/D1D61GNZR1" target="_blank">
  <img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Sponsor me on Ko-Fi">
</a>
</div>

---


  <!-- Badges -->
  <div>
    <!-- Total downloads -->
    <a href="https://pepy.tech/projects/chromolog"><img src="https://static.pepy.tech/badge/chromolog" alt="PyPI Downloads"></a>
    <!-- Versión actual -->
    <a href="https://pypi.org/project/chromolog/"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/chromolog?label=chromolog"></a>
    <!-- Python versions supported -->
    <a href="https://python.org/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/chromolog"></a> 
    <!-- Author -->
    <a href="https://github.com/tutosrive"><img alt="Static Badge" src="https://img.shields.io/badge/Tutos%20Rive-Author-brightgreen"></a>
    <!-- Licencia -->
    <a href="https://raw.githubusercontent.com/tutosrive/chromolog/main/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/tutosrive/chromolog"></a>
  </div>

```shell
pip install chromolog
```
---

Imprima mensajes por consola coloridos y distinguidos de los demás, tenga un formato de salida por consola más elegante y vívido según lo prefiera, ya sea un mensaje de `error` o un mensaje de operación finalizada (`success`).

Visite: https://docs.dev2forge.software/chromolog/ para más detalles

> Descarga nuestro nuevo proyecto: [`pip install bridgex`](https://github.com/Dev2Forge/bridgex)
> <div align="center"><img src="https://cdn.jsdelivr.net/gh/tutosrive/images-projects-srm-trg@main/dev2forge/pymd/bridgex/bridgex-logo-animated.webp" width="200"></div>

# Inicialización

1. Importación del módulo
2.  Crear una instancia de la clase `Print` 
3.  Use los [métodos disponibles](#métodos-disponibles).

# Métodos Disponibles
- `err(err:any)`: Indicado para imprimir los errores 😞
- `exc(exc:any)`: Indicado para imprimir información sobre la excepción capturada en bloques `try`
- `inf(inf:any)`: Indicado para imprimir mensajes de información, variables ℹ
- `warn(warn:any)`: Indicado para imprimir mensajes de precacución 😱
- `suc(suc:any)`: Indicado para indicar que la ejecución fue completada con éxito ✅

> Mismos métodos pero con fondo de color
- `err_bg(err:any)`: Indicado para imprimir los errores 😞
- `exc_bg(exc:any)`: Indicado para imprimir información sobre la excepción capturada en bloques `try`
- `inf_bg(inf:any)`: Indicado para imprimir mensajes de información, variables ℹ
- `warn_bg(warn:any)`: Indicado para imprimir mensajes de precacución 😱
- `suc_bg(suc:any)`: Indicado para indicar que la ejecución fue completada con éxito ✅

## Historial de versiones:
- `v0.2.5`: 
  - Corrección de los colores en windows, actualización de la versión de python requerida, y corrección de errores menores.
- `v0.2.4`: 
  - Agregué "_nuevos_" métodos (Misma funcionalidad pero fondo de color .-.)
  - Corrección de enlaces (Cambié mi nombre de usuario en **GitHub**)
- `v0.2.3`: 
  - Errores menores
- `v0.2.2`: 
  - Actualización de versión de python requerida
- `v0.2.1`: 
  - Actualización de links de las páginas de soporte, y mejora de código
- `v0.2.0`: 
  - Mejoras del proyecto, ahora solo debe importar: `import chromolog`.
  - Nuevos métodos:
    - `exc(exc:Exception)`: Específico para imprimir la información precisa de una excepción capturada con el bloque `try`
- `v0.1.1`: Corrección de errores de la página del proyecto en https://pypi.org
- `v0.1.0`: Primera versión funcional.

Si desea conocer más acerca de, visite:
- [Web de soporte](https://docs.dev2forge.software/chromolog/)
- [Web pypi.org](https://pypi.org/project/chromolog/)
- [Github project](https://github.com/Dev2Forge/chromolog/)
