# Calculadora de Mus

Calculadora de probabilidades de ganar cada lance en el juego de cartas Mus
(variante 8 reyes). Frontend en React + TypeScript con tema visual de tapete
de mus, backend en Python + FastAPI con simulador Monte Carlo.

## Estructura

```
mus_probability/
├── backend/           # FastAPI + lógica de mus + Monte Carlo
│   ├── app/
│   │   ├── models/    # Card, Hand, posiciones
│   │   ├── engine/    # Evaluadores de lances y comparador
│   │   ├── probability/ # Simulador Monte Carlo
│   │   ├── api/       # Schemas Pydantic y routes
│   │   └── main.py
│   ├── tests/         # 44 tests pytest
│   └── requirements.txt
└── frontend/          # Vite + React + TS
    └── src/
        ├── components/  # CardPicker, GameStateForm, ResultsPanel...
        ├── api.ts       # cliente fetch
        └── App.tsx
```

## Instalación

Desde esta carpeta, prepara las dependencias una vez antes del primer arranque:

```powershell
python -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
cd frontend
npm ci
cd ..
```

## Arranque rápido

```powershell
# Desde la raíz del proyecto
.\run.ps1
```

Abre dos ventanas: backend (FastAPI con autoreload) y frontend (Vite dev server).

- Frontend: <http://localhost:5173>
- Backend:  <http://localhost:8001>
- Docs:     <http://localhost:8001/docs>

## Arranque manual

### Backend

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### Frontend

```powershell
cd frontend
npm run dev
```

## Tests del backend

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

## Modelo de probabilidad

El backend usa Monte Carlo con 50.000 simulaciones por defecto (configurable
hasta 1M en la UI).

Para cada simulación:

1. Se toma la mano del usuario como dato fijo.
2. Las 36 cartas restantes se reparten uniformemente entre los 3 oponentes.
3. Se evalúan los 5 lances (grande, chica, pares, juego, punto) para todas
   las manos.
4. Se determina el ganador de cada lance teniendo en cuenta el desempate por
   mano (en empate gana el jugador más cercano a la mano).

Para cada lance se devuelven cuatro cifras:

- `win_prob`: probabilidad condicional de que mi pareja gane el lance dado
  que se juega.
- `play_prob`: probabilidad de que el lance llegue a jugarse (siempre 1 en
  grande y chica; menor que 1 en pares/juego/punto).
- `expected_win`: `win_prob * play_prob`.
- `ci95`: anchura del intervalo de confianza al 95% en torno a `win_prob`.

## Limitaciones del MVP

- **Modelo de descartes uniforme**: la información de cuántas cartas tiró
  cada oponente en cada ronda se guarda pero no afecta al cálculo. En la
  siguiente fase se añadirá un prior racional (p. ej. "si descartó 3, prob.
  alta de que conservara una carta alta").
- Sólo variante 8 reyes (2 → as, 3 → rey). La clásica está pendiente.
- No modela apuestas ni órdago — sólo la probabilidad de ganar el lance.
