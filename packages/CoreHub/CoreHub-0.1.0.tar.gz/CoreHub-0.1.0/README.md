# CoreHub

Librería para buscar usuarios mediante nuestra base de datos (módulo finder).

## Uso

```python
from corehub import Finder

finder = Finder()
resultado = finder.find("hola")

if "error" in resultado:
    print(resultado["error"])
else:
    print(resultado["results"])
