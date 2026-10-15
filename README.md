# Calculadora de mus

Calculadora de probabilidades de mus para cuatro jugadores por parejas.

Este repositorio conserva las dos implementaciones originales:

| Carpeta | Implementacion | Ejecucion |
| --- | --- | --- |
| [`mus-probabilidades`](mus-probabilidades/) |  Python y frontend HTML/JavaScript | Un servidor, puerto 8000 |
| [`mus_probability`](mus_probability/) |  FastAPI y React/TypeScript | Backend en 8001 y frontend en 5173 |


## Ejecutar la primera version 

Requiere Python 3.10 o superior. La aplicacion no necesita dependencias externas.

```sh
git clone https://github.com/javiersaguar/Calculadora_mus.git
cd Calculadora_mus/mus-probabilidades
python -m backend.server --port 8000
```

Abre http://127.0.0.1:8000 en el navegador.

## Ejecutar la segunda version

Consulta la [instalacion y ejecucion](mus_probability/README.md). Requiere Python
y Node.js con npm. Las dos versiones pueden ejecutarse simultaneamente con sus
puertos predeterminados.

## Pruebas de la primera version 

Desde la carpeta `mus-probabilidades`:

```sh
python -m pip install pytest
python -m pytest
```

La simulacion ofrece estimaciones condicionadas a los datos introducidos. El
modelo de preferencias de descarte es heuristico y no esta calibrado con partidas
reales.
