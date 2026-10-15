# Calculadora de mus

Calculadora de probabilidades de mus para cuatro jugadores por parejas.

El proyecto se encuentra en [`mus-probabilidades`](mus-probabilidades/).

## Ejecutar

Requiere Python 3.10 o superior. La aplicacion no necesita dependencias externas.

```sh
git clone https://github.com/javiersaguar/Calculadora_mus.git
cd Calculadora_mus/mus-probabilidades
python -m backend.server --port 8000
```

Abre http://127.0.0.1:8000 en el navegador.

## Pruebas

Desde la carpeta `mus-probabilidades`:

```sh
python -m pip install pytest
python -m pytest
```

La simulacion ofrece estimaciones condicionadas a los datos introducidos. El
modelo de preferencias de descarte es heuristico y no esta calibrado con partidas
reales.
