# Mus Probabilidades

Calculadora local para estimar probabilidades de ganar lances de mus a 4 jugadores por parejas.

## Ejecutar

```powershell
cd "C:\Users\Javier\Documents\New project\mus-probabilidades"
python -m backend.server --port 8000
```

Despues abre:

```text
http://127.0.0.1:8000
```

## Que incluye el MVP

- Baraja espanola de 40 cartas.
- Variante de 8 reyes y 8 ases.
- Evaluacion de grande, chica, pares, juego y punto.
- Desempates por posicion de mano.
- Declaraciones de pares y juego por jugador.
- Cartas tiradas por jugador en el ultimo descarte conocido, con opcion "no lo se".
- Cartas repartidas en total en la mano actual: reparto inicial mas cartas dadas tras muses.
- Simulacion Monte Carlo neutral o con modelo realista de descarte.
- Modelo realista que favorece manos que un jugador tenderia a conservar: reyes, caballos, pares y juego fuerte.
- Frontend tematico servido por el mismo backend.

## Pruebas

```powershell
cd "C:\Users\Javier\Documents\New project\mus-probabilidades"
python -m pytest
```

