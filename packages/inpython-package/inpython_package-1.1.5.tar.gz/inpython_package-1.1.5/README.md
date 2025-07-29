# README

Ce projet **inpython-package** rassemble tous les packages et modules python exploités par Integrix .

## sub-package **inpython.ingraph**

package pour la gestion avec MS-Graph en exploitant le module 'msal' (Microsoft Authentication Library).

## How do I get set up?

* Les bases de u2Python c.f. [wiki sys/proc/install u2Python](https://wiki.infodata.lu/sys/proc/install_u2python)
* [U2Python par RocketSoftware](https://docs.rocketsoftware.com/bundle/UniVerse_PythonUserGuide_V1134/resource/UniVerse_PythonUserGuide_V1134.pdf)
* Vérifier la version de u2Python, au TCL uv

```python
>python 
import sys
print(sys.version)
print(sys.executable) # -> 'C:\\U2\\UV\\BIN\\uv.exe' uvbin !!
print('\n'.join(sys.path)) # les path en cours
exit()
```

## Install inPackages into U2python

* `pip3 install inpython-package`

## Manage Package

* c.f. [devREADME](devREADME.md)
