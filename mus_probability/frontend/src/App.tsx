import { useState } from "react";

import "./App.css";
import { calculate } from "./api";
import { CardPicker } from "./components/CardPicker";
import { GameStateForm } from "./components/GameStateForm";
import { PlayingCard } from "./components/PlayingCard";
import { ResultsPanel } from "./components/ResultsPanel";
import type {
  CalculateResponse,
  CardSpec,
  PlayerDiscards,
  Position,
} from "./types";

export default function App() {
  const [cards, setCards] = useState<CardSpec[]>([]);
  const [position, setPosition] = useState<Position>(0);
  const [nSims, setNSims] = useState(50000);
  const [discards, setDiscards] = useState<PlayerDiscards[]>([]);
  const [rounds, setRounds] = useState(0);
  const [result, setResult] = useState<CalculateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canCalculate = cards.length === 4 && !loading;

  async function handleCalculate() {
    setLoading(true);
    setError(null);
    try {
      const res = await calculate({
        my_cards: cards,
        my_position: position,
        n_sims: nSims,
        discards,
      });
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Calculadora de Mus</h1>
        <p className="app-subtitle">Probabilidades de ganar cada lance — variante 8 reyes</p>
      </header>

      <main className="app-main">
        <section className="panel">
          <h2 className="panel-title">
            Tus cartas
            <span className="panel-counter">{cards.length}/4</span>
          </h2>
          <div className="my-hand">
            {cards.length === 0 && (
              <p className="my-hand__empty">Selecciona 4 cartas abajo ↓</p>
            )}
            {cards.map((c) => (
              <PlayingCard
                key={`${c.rank}-${c.suit}`}
                card={c}
                size="lg"
                selected
                onClick={() =>
                  setCards(cards.filter((x) => !(x.rank === c.rank && x.suit === c.suit)))
                }
              />
            ))}
          </div>
          <CardPicker selected={cards} onChange={setCards} />
        </section>

        <section className="panel">
          <h2 className="panel-title">Estado del juego</h2>
          <GameStateForm
            position={position}
            onPositionChange={setPosition}
            nSims={nSims}
            onNSimsChange={setNSims}
            discards={discards}
            onDiscardsChange={setDiscards}
            rounds={rounds}
            onRoundsChange={setRounds}
          />
        </section>

        <section className="panel panel--cta">
          <button
            type="button"
            className="calculate-btn"
            disabled={!canCalculate}
            onClick={handleCalculate}
          >
            {loading ? "Calculando…" : "Calcular probabilidades"}
          </button>
          {cards.length < 4 && (
            <p className="cta-hint">Necesitas seleccionar 4 cartas.</p>
          )}
        </section>

        <section className="panel">
          <ResultsPanel data={result} loading={loading} error={error} />
        </section>
      </main>

      <footer className="app-footer">
        <p>
          Variante 8 reyes · Monte Carlo con descartes uniformes · {nSims.toLocaleString()}{" "}
          simulaciones
        </p>
      </footer>
    </div>
  );
}
