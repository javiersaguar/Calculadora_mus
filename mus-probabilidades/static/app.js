const ranks = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12];
const suits = [
  { code: "O", label: "Oros" },
  { code: "C", label: "Copas" },
  { code: "E", label: "Espadas" },
  { code: "B", label: "Bastos" },
];

const rankLabels = {
  1: "As",
  2: "2",
  3: "3",
  4: "4",
  5: "5",
  6: "6",
  7: "7",
  10: "Sota",
  11: "Caballo",
  12: "Rey",
};

const compactRankLabels = {
  ...rankLabels,
  11: "Cab.",
};

const compactSuitLabels = {
  O: "Oros",
  C: "Copas",
  E: "Esp.",
  B: "Bastos",
};

const lanceLabels = {
  grande: "Grande",
  chica: "Chica",
  pares: "Pares",
  juego: "Juego",
  punto: "Punto",
};

const state = {
  heroHand: [],
  playerIndex: 0,
  manoIndex: 0,
  lanceFilter: "all",
  totalDealtCards: "unknown",
  discardCounts: ["unknown", "unknown", "unknown", "unknown"],
  pairDeclarations: ["unknown", "unknown", "unknown", "unknown"],
  gameDeclarations: ["unknown", "unknown", "unknown", "unknown"],
  latestResult: null,
};

const els = {};

document.addEventListener("DOMContentLoaded", () => {
  bindElements();
  renderDeck();
  renderHand();
  renderPlayerRows();
  updateSeatLabels();
  renderEmptyResults();
  bindEvents();
});

function bindElements() {
  Object.assign(els, {
    deckGrid: document.querySelector("#deckGrid"),
    selectedHand: document.querySelector("#selectedHand"),
    handCount: document.querySelector("#handCount"),
    playerIndex: document.querySelector("#playerIndex"),
    manoIndex: document.querySelector("#manoIndex"),
    totalDealtCards: document.querySelector("#totalDealtCards"),
    variantToggle: document.querySelector("#variantToggle"),
    discardModel: document.querySelector("#discardModel"),
    samples: document.querySelector("#samples"),
    simulationLabel: document.querySelector("#simulationLabel"),
    playerRows: document.querySelector("#playerRows"),
    calculateButton: document.querySelector("#calculateButton"),
    resetButton: document.querySelector("#resetButton"),
    formMessage: document.querySelector("#formMessage"),
    resultsTitle: document.querySelector("#resultsTitle"),
    samplesMeta: document.querySelector("#samplesMeta"),
    resultsGrid: document.querySelector("#resultsGrid"),
    heroSummary: document.querySelector("#heroSummary"),
    notesPanel: document.querySelector("#notesPanel"),
    qualityPill: document.querySelector("#qualityPill"),
    lanceFilter: document.querySelector("#lanceFilter"),
  });
}

function bindEvents() {
  els.playerIndex.addEventListener("change", () => {
    state.playerIndex = Number(els.playerIndex.value);
    state.pairDeclarations[state.playerIndex] = "unknown";
    state.gameDeclarations[state.playerIndex] = "unknown";
    updateSeatLabels();
    renderPlayerRows();
  });

  els.manoIndex.addEventListener("change", () => {
    state.manoIndex = Number(els.manoIndex.value);
    updateSeatLabels();
  });

  els.totalDealtCards.addEventListener("input", () => {
    const value = els.totalDealtCards.value.trim();
    state.totalDealtCards = value === "" ? "unknown" : value;
  });

  els.samples.addEventListener("input", () => {
    els.simulationLabel.textContent = `${Number(els.samples.value).toLocaleString("es-ES")} simulaciones`;
  });

  els.calculateButton.addEventListener("click", calculate);
  els.resetButton.addEventListener("click", resetAll);

  els.lanceFilter.addEventListener("click", (event) => {
    const button = event.target.closest("[data-lance]");
    if (!button) return;
    state.lanceFilter = button.dataset.lance;
    document.querySelectorAll(".segment").forEach((segment) => {
      segment.classList.toggle("active", segment === button);
    });
    if (state.latestResult) {
      renderResults(state.latestResult);
    }
  });
}

function makeDeck() {
  return suits.flatMap((suit) =>
    ranks.map((rank) => ({
      code: `${rank}-${suit.code}`,
      rank,
      rankLabel: rankLabels[rank],
      suit: suit.code,
      suitLabel: suit.label,
    })),
  );
}

function renderDeck() {
  els.deckGrid.innerHTML = "";
  const deck = makeDeck();
  for (const card of deck) {
    const button = document.createElement("button");
    const isSelected = state.heroHand.includes(card.code);
    button.type = "button";
    button.className = `deck-card ${isSelected ? "selected" : ""}`;
    button.disabled = isSelected || state.heroHand.length >= 4;
    button.dataset.code = card.code;
    button.innerHTML = cardMarkup(card, true);
    button.addEventListener("click", () => addCard(card.code));
    els.deckGrid.appendChild(button);
  }
}

function renderHand() {
  els.selectedHand.innerHTML = "";
  els.handCount.textContent = `${state.heroHand.length}/4`;

  for (let index = 0; index < 4; index += 1) {
    const code = state.heroHand[index];
    if (!code) {
      const slot = document.createElement("div");
      slot.className = "hand-slot";
      slot.textContent = "Libre";
      els.selectedHand.appendChild(slot);
      continue;
    }

    const card = cardFromCode(code);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "deck-card";
    button.title = "Quitar carta";
    button.innerHTML = cardMarkup(card);
    button.addEventListener("click", () => removeCard(code));
    els.selectedHand.appendChild(button);
  }

  els.calculateButton.disabled = state.heroHand.length !== 4;
  els.formMessage.textContent =
    state.heroHand.length === 4 ? "" : "Faltan cartas para completar la mano.";
}

function cardMarkup(card, compact = false) {
  const rankLabel = compact ? compactRankLabels[card.rank] : card.rankLabel;
  const suitLabel = compact ? compactSuitLabels[card.suit] : card.suitLabel;
  return `
    <span class="card-face suit-${card.suit} ${compact ? "is-compact" : ""}">
      <span class="card-corner">
        <strong>${escapeHtml(rankLabel)}</strong>
        <small>${escapeHtml(suitLabel)}</small>
      </span>
      ${cardArtMarkup(card, compact)}
    </span>
  `;
}

function cardArtMarkup(card, compact) {
  if (card.rank >= 10) {
    return `
      <span class="card-art court-card" aria-hidden="true">
        <span class="court-emblem">${suitIconSvg(card.suit)}</span>
        <span class="court-title">${escapeHtml(card.rankLabel)}</span>
      </span>
    `;
  }

  return `
    <span class="card-art pip-card" aria-hidden="true">
      ${pipLayout(card.rank, compact)
        .map(
          ([x, y, scale]) => `
            <span class="pip" style="left:${x}%; top:${y}%; --pip-scale:${scale};">
              ${suitIconSvg(card.suit)}
            </span>
          `,
        )
        .join("")}
    </span>
  `;
}

function pipLayout(rank, compact) {
  const layouts = {
    1: [[50, 50, compact ? 1.7 : 2.05]],
    2: [
      [50, 29, 1],
      [50, 71, 1],
    ],
    3: [
      [50, 25, 0.95],
      [50, 50, 0.95],
      [50, 75, 0.95],
    ],
    4: [
      [34, 29, 0.86],
      [66, 29, 0.86],
      [34, 71, 0.86],
      [66, 71, 0.86],
    ],
    5: [
      [34, 27, 0.82],
      [66, 27, 0.82],
      [50, 50, 0.82],
      [34, 73, 0.82],
      [66, 73, 0.82],
    ],
    6: [
      [34, 24, 0.78],
      [66, 24, 0.78],
      [34, 50, 0.78],
      [66, 50, 0.78],
      [34, 76, 0.78],
      [66, 76, 0.78],
    ],
    7: [
      [34, 22, 0.72],
      [66, 22, 0.72],
      [34, 45, 0.72],
      [66, 45, 0.72],
      [50, 58, 0.72],
      [34, 78, 0.72],
      [66, 78, 0.72],
    ],
  };
  return layouts[rank] || layouts[1];
}

function suitIconSvg(suit) {
  const icons = {
    O: `
      <svg class="suit-icon" viewBox="0 0 100 100" focusable="false">
        <circle cx="50" cy="50" r="34" fill="currentColor" opacity="0.94"></circle>
        <circle cx="50" cy="50" r="23" fill="none" stroke="#fff8df" stroke-width="8" opacity="0.72"></circle>
        <circle cx="50" cy="50" r="8" fill="#fff8df" opacity="0.9"></circle>
        <path d="M50 12v13M50 75v13M12 50h13M75 50h13" stroke="#fff8df" stroke-width="6" stroke-linecap="round" opacity="0.78"></path>
      </svg>
    `,
    C: `
      <svg class="suit-icon" viewBox="0 0 100 100" focusable="false">
        <path d="M28 20h44l-7 36c-2 12-10 19-15 19s-13-7-15-19L28 20Z" fill="currentColor"></path>
        <path d="M36 29h28l-5 24c-1 7-5 11-9 11s-8-4-9-11l-5-24Z" fill="#fff8df" opacity="0.56"></path>
        <path d="M50 74v11M34 88h32" stroke="currentColor" stroke-width="9" stroke-linecap="round"></path>
        <path d="M28 22c8 7 36 7 44 0" fill="none" stroke="#fff8df" stroke-width="5" stroke-linecap="round" opacity="0.8"></path>
      </svg>
    `,
    E: `
      <svg class="suit-icon" viewBox="0 0 100 100" focusable="false">
        <path d="M50 7 64 46 50 76 36 46 50 7Z" fill="currentColor"></path>
        <path d="M50 18v49" stroke="#fff8df" stroke-width="5" stroke-linecap="round" opacity="0.64"></path>
        <path d="M29 67h42" stroke="currentColor" stroke-width="9" stroke-linecap="round"></path>
        <path d="M50 69v19" stroke="currentColor" stroke-width="9" stroke-linecap="round"></path>
        <circle cx="50" cy="91" r="6" fill="currentColor"></circle>
      </svg>
    `,
    B: `
      <svg class="suit-icon" viewBox="0 0 100 100" focusable="false">
        <path d="M58 9c8 4 12 13 8 22L43 84c-3 7-10 10-16 7s-8-10-5-17l23-53c3-8 8-13 13-12Z" fill="currentColor"></path>
        <path d="M57 17 30 80" stroke="#fff8df" stroke-width="6" stroke-linecap="round" opacity="0.55"></path>
        <path d="M48 32c14-1 25 4 31 14M38 55c-12 1-21-3-27-11" stroke="currentColor" stroke-width="8" stroke-linecap="round"></path>
      </svg>
    `,
  };
  return icons[suit] || icons.O;
}

function addCard(code) {
  if (state.heroHand.length >= 4 || state.heroHand.includes(code)) return;
  state.heroHand.push(code);
  renderDeck();
  renderHand();
}

function removeCard(code) {
  state.heroHand = state.heroHand.filter((cardCode) => cardCode !== code);
  renderDeck();
  renderHand();
}

function cardFromCode(code) {
  const [rankText, suitCode] = code.split("-");
  const suit = suits.find((candidate) => candidate.code === suitCode);
  return {
    code,
    rank: Number(rankText),
    rankLabel: rankLabels[Number(rankText)],
    suit: suitCode,
    suitLabel: suit ? suit.label : suitCode,
  };
}

function renderPlayerRows() {
  els.playerRows.innerHTML = "";
  for (let index = 0; index < 4; index += 1) {
    const row = document.createElement("div");
    row.className = "player-row";
    row.innerHTML = `
      <div class="player-name">
        <div>${escapeHtml(playerLabel(index))}<span>${escapeHtml(playerRole(index))}</span></div>
      </div>
      <label>
        <span>Último descarte</span>
        <select data-field="discard" data-player="${index}">
          ${discardOptions(state.discardCounts[index])}
        </select>
      </label>
      <label>
        <span>Pares</span>
        <select data-field="pairs" data-player="${index}" ${index === state.playerIndex ? "disabled" : ""}>
          ${declarationOptions(index === state.playerIndex ? "unknown" : state.pairDeclarations[index])}
        </select>
      </label>
      <label>
        <span>Juego</span>
        <select data-field="game" data-player="${index}" ${index === state.playerIndex ? "disabled" : ""}>
          ${declarationOptions(index === state.playerIndex ? "unknown" : state.gameDeclarations[index])}
        </select>
      </label>
    `;
    els.playerRows.appendChild(row);
  }

  els.playerRows.querySelectorAll("select").forEach((select) => {
    select.addEventListener("change", () => {
      const player = Number(select.dataset.player);
      const field = select.dataset.field;
      if (field === "discard") state.discardCounts[player] = select.value;
      if (field === "pairs") state.pairDeclarations[player] = select.value;
      if (field === "game") state.gameDeclarations[player] = select.value;
    });
  });
}

function discardOptions(selected) {
  const options = [
    ["unknown", "No lo sé"],
    ["0", "0"],
    ["1", "1"],
    ["2", "2"],
    ["3", "3"],
    ["4", "4"],
  ];
  return options
    .map(([value, label]) => `<option value="${value}" ${selected === value ? "selected" : ""}>${label}</option>`)
    .join("");
}

function declarationOptions(selected) {
  const options = [
    ["unknown", "No lo sé"],
    ["yes", "Sí"],
    ["no", "No"],
  ];
  return options
    .map(([value, label]) => `<option value="${value}" ${selected === value ? "selected" : ""}>${label}</option>`)
    .join("");
}

function updateSeatLabels() {
  for (let index = 0; index < 4; index += 1) {
    const seat = document.querySelector(`#seat${index}`);
    seat.textContent = `${playerLabel(index)}${index === state.manoIndex ? " · mano" : ""}`;
    seat.classList.toggle("is-you", index === state.playerIndex);
    seat.classList.toggle("is-partner", index === (state.playerIndex + 2) % 4);
    seat.classList.toggle("is-mano", index === state.manoIndex);
  }
}

function playerLabel(index) {
  return `Jugador ${index + 1}`;
}

function playerRole(index) {
  if (index === state.playerIndex) return "Tú";
  if (index === (state.playerIndex + 2) % 4) return "Compañero";
  return "Rival";
}

function resetAll() {
  state.heroHand = [];
  state.latestResult = null;
  state.totalDealtCards = "unknown";
  els.totalDealtCards.value = "";
  state.discardCounts = ["unknown", "unknown", "unknown", "unknown"];
  state.pairDeclarations = ["unknown", "unknown", "unknown", "unknown"];
  state.gameDeclarations = ["unknown", "unknown", "unknown", "unknown"];
  els.formMessage.textContent = "";
  els.qualityPill.textContent = "Sin cálculo";
  renderDeck();
  renderHand();
  renderPlayerRows();
  renderEmptyResults();
}

async function calculate() {
  if (state.heroHand.length !== 4) return;
  setLoading(true);
  const knownHands = [[], [], [], []];
  knownHands[state.playerIndex] = [...state.heroHand];
  const pairs = [...state.pairDeclarations];
  const game = [...state.gameDeclarations];
  pairs[state.playerIndex] = "unknown";
  game[state.playerIndex] = "unknown";

  const payload = {
    heroHand: [...state.heroHand],
    knownHands,
    playerIndex: state.playerIndex,
    manoIndex: state.manoIndex,
    samples: Number(els.samples.value),
    variant: { eightKingsAndAces: els.variantToggle.checked },
    discardModel: els.discardModel.checked ? "heuristic" : "neutral",
    totalDealtCards: state.totalDealtCards === "unknown" ? "unknown" : Number(state.totalDealtCards),
    discardCounts: [...state.discardCounts],
    declarations: { pairs, game },
  };

  try {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "No se pudo calcular.");
    }
    state.latestResult = data;
    renderResults(data);
    els.formMessage.textContent = "";
  } catch (error) {
    els.formMessage.textContent = error.message;
  } finally {
    setLoading(false);
  }
}

function setLoading(isLoading) {
  els.calculateButton.disabled = isLoading || state.heroHand.length !== 4;
  els.calculateButton.textContent = isLoading ? "Calculando..." : "Calcular probabilidades";
}

function renderEmptyResults() {
  els.resultsTitle.textContent = "Selecciona tus 4 cartas";
  els.samplesMeta.textContent = "Esperando mano";
  els.heroSummary.innerHTML = "";
  els.notesPanel.innerHTML = "";
  els.resultsGrid.innerHTML = `<div class="empty-results">La mesa queda lista al completar la mano.</div>`;
}

function renderResults(data) {
  const meta = data.meta;
  els.resultsTitle.textContent = "Probabilidades de tu pareja";
  const dealt = meta.totalDealtCards ? ` · ${meta.totalDealtCards} cartas repartidas` : "";
  els.samplesMeta.textContent = `${meta.acceptedSamples.toLocaleString("es-ES")} muestras · calidad ${meta.quality}${dealt}`;
  els.qualityPill.textContent = `Calidad ${meta.quality}`;

  renderHeroSummary(data.heroHand);
  renderLanceCards(data.metrics);
  renderNotes(data.notes || []);
}

function renderHeroSummary(hand) {
  const cards = hand.cards.map((card) => card.label).join(" · ");
  els.heroSummary.innerHTML = `
    <span class="summary-chip">${escapeHtml(cards)}</span>
    <span class="summary-chip">${escapeHtml(hand.pairs.kind)}</span>
    <span class="summary-chip">${escapeHtml(hand.game.label)}</span>
  `;
}

function renderLanceCards(metrics) {
  const order = ["grande", "chica", "pares", "juego", "punto"];
  const visible = state.lanceFilter === "all" ? order : order.filter((lance) => lance === state.lanceFilter);
  els.resultsGrid.innerHTML = visible.map((lance) => resultCard(lance, metrics[lance])).join("");
}

function resultCard(lance, metric) {
  const teamWin = metric.teamWin || 0;
  const activeLabel =
    lance === "punto"
      ? `Se llega a punto: ${formatPct(metric.reachesPoint || metric.active)}`
      : `Lance activo: ${formatPct(metric.active)}`;
  return `
    <article class="result-card">
      <h3>${lanceLabels[lance]}</h3>
      <div class="big-percent">${formatPct(teamWin)}</div>
      <div class="meter" aria-hidden="true"><span style="--value:${Math.round(teamWin * 100)}%"></span></div>
      <p class="result-detail">Tú ${formatPct(metric.heroWin)} · compañero ${formatPct(metric.partnerWin)} · rivales ${formatPct(metric.opponentsWin)}</p>
      <p class="result-detail">${activeLabel} · apostable ${formatPct(metric.bettable)}</p>
    </article>
  `;
}

function renderNotes(notes) {
  els.notesPanel.innerHTML = notes.map((note) => `<p class="note-line">${escapeHtml(note)}</p>`).join("");
}

function formatPct(value) {
  const number = Number.isFinite(value) ? value : 0;
  return `${(number * 100).toLocaleString("es-ES", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  })}%`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
