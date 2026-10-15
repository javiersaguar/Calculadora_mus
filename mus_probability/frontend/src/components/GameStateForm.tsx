import type { DiscardRound, PlayerDiscards, Position } from "../types";
import { POSITION_NAMES } from "../types";

interface Props {
  position: Position;
  onPositionChange: (pos: Position) => void;
  nSims: number;
  onNSimsChange: (n: number) => void;
  discards: PlayerDiscards[];
  onDiscardsChange: (d: PlayerDiscards[]) => void;
  rounds: number;
  onRoundsChange: (r: number) => void;
}

const N_SIM_PRESETS = [10000, 50000, 200000, 1000000];

export function GameStateForm(props: Props) {
  const {
    position,
    onPositionChange,
    nSims,
    onNSimsChange,
    discards,
    onDiscardsChange,
    rounds,
    onRoundsChange,
  } = props;

  const opponentPositions = ([0, 1, 2, 3] as Position[]).filter(
    (p) => p !== position && p !== ((position + 2) % 4 as Position)
  );

  const partnerPos = ((position + 2) % 4) as Position;

  const updatePlayerRound = (
    playerPos: Position,
    roundIdx: number,
    field: "discarded" | "kept_after",
    value: number | null
  ) => {
    let updated = [...discards];
    let entry = updated.find((d) => d.player_position === playerPos);
    if (!entry) {
      entry = { player_position: playerPos, rounds: [] };
      updated.push(entry);
    }
    while (entry.rounds.length <= roundIdx) {
      entry.rounds.push({ discarded: 0, kept_after: null });
    }
    if (field === "discarded") {
      entry.rounds[roundIdx].discarded = value as number;
    } else {
      entry.rounds[roundIdx].kept_after = value;
    }
    // Trim trailing default rounds
    updated = updated.map((d) => ({
      ...d,
      rounds: d.rounds.slice(0, rounds),
    }));
    onDiscardsChange(updated);
  };

  const getPlayerRound = (playerPos: Position, roundIdx: number): DiscardRound => {
    const entry = discards.find((d) => d.player_position === playerPos);
    return entry?.rounds[roundIdx] ?? { discarded: 0, kept_after: null };
  };

  return (
    <div className="game-state-form">
      <div className="form-row">
        <label className="form-label">Tu posición</label>
        <div className="button-row">
          {([0, 1, 2, 3] as Position[]).map((p) => (
            <button
              key={p}
              type="button"
              className={`pos-btn ${position === p ? "pos-btn--active" : ""}`}
              onClick={() => onPositionChange(p)}
            >
              {POSITION_NAMES[p]}
              {p === 0 && <span className="pos-btn__hint">(habla 1º)</span>}
              {p === 3 && <span className="pos-btn__hint">(reparte)</span>}
            </button>
          ))}
        </div>
        <div className="form-hint">
          Tu compañero juega en <strong>{POSITION_NAMES[partnerPos]}</strong>.
        </div>
      </div>

      <div className="form-row">
        <label className="form-label">Precisión (simulaciones Monte Carlo)</label>
        <div className="button-row">
          {N_SIM_PRESETS.map((n) => (
            <button
              key={n}
              type="button"
              className={`sim-btn ${nSims === n ? "sim-btn--active" : ""}`}
              onClick={() => onNSimsChange(n)}
            >
              {n >= 1000000 ? "1M" : `${n / 1000}k`}
            </button>
          ))}
        </div>
        <div className="form-hint">
          {nSims >= 1000000
            ? "Máxima precisión, tarda más"
            : nSims >= 200000
              ? "Alta precisión"
              : nSims >= 50000
                ? "Precisión recomendada (~±0.4%)"
                : "Rápido pero menos preciso"}
        </div>
      </div>

      <details className="discards-section">
        <summary>Descartes de los oponentes (opcional)</summary>
        <p className="form-hint">
          Esta información se guarda para futuras versiones del cálculo. En el modelo
          actual los descartes no alteran la probabilidad (asumimos descartes
          uniformes).
        </p>
        <div className="form-row">
          <label className="form-label">Rondas de mus antes del corte</label>
          <input
            type="number"
            min={0}
            max={5}
            value={rounds}
            onChange={(e) => onRoundsChange(Math.max(0, Math.min(5, parseInt(e.target.value) || 0)))}
            className="number-input"
          />
        </div>
        {rounds > 0 && (
          <div className="discards-table">
            <div className="discards-header">
              <div>Jugador</div>
              {Array.from({ length: rounds }).map((_, i) => (
                <div key={i}>Ronda {i + 1}</div>
              ))}
            </div>
            {opponentPositions.map((p) => (
              <div key={p} className="discards-row">
                <div className="discards-player">
                  <strong>{POSITION_NAMES[p]}</strong>
                  <span className="discards-team">(oponente)</span>
                </div>
                {Array.from({ length: rounds }).map((_, i) => {
                  const r = getPlayerRound(p, i);
                  return (
                    <div key={i} className="discards-cell">
                      <label>
                        Tiró:
                        <select
                          value={r.discarded}
                          onChange={(e) =>
                            updatePlayerRound(p, i, "discarded", parseInt(e.target.value))
                          }
                        >
                          {[0, 1, 2, 3, 4].map((n) => (
                            <option key={n} value={n}>
                              {n}
                            </option>
                          ))}
                        </select>
                      </label>
                      <label>
                        Conservó:
                        <select
                          value={r.kept_after === null ? "unknown" : r.kept_after}
                          onChange={(e) => {
                            const v = e.target.value;
                            updatePlayerRound(
                              p,
                              i,
                              "kept_after",
                              v === "unknown" ? null : parseInt(v)
                            );
                          }}
                        >
                          <option value="unknown">No lo sé</option>
                          {[0, 1, 2, 3, 4].map((n) => (
                            <option key={n} value={n}>
                              {n}
                            </option>
                          ))}
                        </select>
                      </label>
                    </div>
                  );
                })}
              </div>
            ))}
            {/* Partner */}
            <div className="discards-row discards-row--partner">
              <div className="discards-player">
                <strong>{POSITION_NAMES[partnerPos]}</strong>
                <span className="discards-team">(tu compañero)</span>
              </div>
              {Array.from({ length: rounds }).map((_, i) => {
                const r = getPlayerRound(partnerPos, i);
                return (
                  <div key={i} className="discards-cell">
                    <label>
                      Tiró:
                      <select
                        value={r.discarded}
                        onChange={(e) =>
                          updatePlayerRound(partnerPos, i, "discarded", parseInt(e.target.value))
                        }
                      >
                        {[0, 1, 2, 3, 4].map((n) => (
                          <option key={n} value={n}>
                            {n}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label>
                      Conservó:
                      <select
                        value={r.kept_after === null ? "unknown" : r.kept_after}
                        onChange={(e) => {
                          const v = e.target.value;
                          updatePlayerRound(
                            partnerPos,
                            i,
                            "kept_after",
                            v === "unknown" ? null : parseInt(v)
                          );
                        }}
                      >
                        <option value="unknown">No lo sé</option>
                        {[0, 1, 2, 3, 4].map((n) => (
                          <option key={n} value={n}>
                            {n}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </details>
    </div>
  );
}
