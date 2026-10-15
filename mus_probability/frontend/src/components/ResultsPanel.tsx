import type { CalculateResponse } from "../types";

const LANCE_LABELS: Record<keyof CalculateResponse["lances"], string> = {
  grande: "Grande",
  chica: "Chica",
  pares: "Pares",
  juego: "Juego",
  punto: "Punto",
};

const LANCE_DESCRIPTIONS: Record<keyof CalculateResponse["lances"], string> = {
  grande: "Tener las cartas más altas",
  chica: "Tener las cartas más bajas",
  pares: "Tener parejas, medias o duples",
  juego: "Sumar 31 o más",
  punto: "Acercarse más a 30 (si nadie tiene juego)",
};

interface Props {
  data: CalculateResponse | null;
  loading: boolean;
  error: string | null;
}

function fmtPct(p: number, digits = 1): string {
  return `${(p * 100).toFixed(digits)}%`;
}

function classifyWinProb(p: number): string {
  if (p >= 0.7) return "result--strong";
  if (p >= 0.5) return "result--favored";
  if (p >= 0.3) return "result--marginal";
  return "result--weak";
}

export function ResultsPanel({ data, loading, error }: Props) {
  if (loading) {
    return (
      <div className="results-panel results-panel--loading">
        <div className="spinner" />
        <p>Calculando probabilidades…</p>
      </div>
    );
  }
  if (error) {
    return (
      <div className="results-panel results-panel--error">
        <h3>Error</h3>
        <p>{error}</p>
      </div>
    );
  }
  if (!data) {
    return (
      <div className="results-panel results-panel--empty">
        <p>Selecciona 4 cartas y pulsa calcular para ver las probabilidades.</p>
      </div>
    );
  }

  const lances = Object.entries(data.lances) as [
    keyof CalculateResponse["lances"],
    CalculateResponse["lances"]["grande"],
  ][];

  return (
    <div className="results-panel">
      <div className="results-header">
        <h2>Probabilidades de ganar</h2>
        <span className="results-meta">{data.n_sims.toLocaleString()} simulaciones</span>
      </div>
      <div className="results-grid">
        {lances.map(([key, r]) => (
          <div key={key} className={`result-card ${classifyWinProb(r.win_prob)}`}>
            <div className="result-card__header">
              <h3>{LANCE_LABELS[key]}</h3>
              <span className="result-card__desc">{LANCE_DESCRIPTIONS[key]}</span>
            </div>
            <div className="result-card__main">
              <span className="result-card__pct">{fmtPct(r.win_prob)}</span>
              <span className="result-card__ci">±{fmtPct(r.ci95, 1)}</span>
            </div>
            <div className="result-bar">
              <div
                className="result-bar__fill"
                style={{ width: `${Math.round(r.win_prob * 100)}%` }}
              />
            </div>
            <div className="result-card__meta">
              {key === "pares" || key === "juego" || key === "punto" ? (
                <span>
                  Relevante en {fmtPct(r.play_prob, 0)} de las manos
                </span>
              ) : (
                <span>Siempre se juega</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
