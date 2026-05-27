// ===== NAVEGAÇÃO =====
function mostrarPagina(id) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));

  document.getElementById("page-" + id).classList.add("active");
  const link = document.querySelector(`[data-page="${id}"]`);
  if (link) link.classList.add("active");

  if (id === "ranking") carregarGrafico();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ===== CARREGAR ESTADOS NO SELECT =====
async function carregarEstados() {
  try {
    const resp = await fetch("/estados");
    const estados = await resp.json();
    const select = document.getElementById("select-estado");
    estados.forEach(e => {
      const opt = document.createElement("option");
      opt.value = e.uf;
      opt.textContent = `${e.nome} (${e.uf})`;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error("Erro ao carregar estados:", err);
  }
}

// ===== ANALISAR ESTADO =====
async function analisarEstado() {
  const uf = document.getElementById("select-estado").value;
  const btn = document.getElementById("btn-analisar");
  const resultado = document.getElementById("resultado");
  const erroBox = document.getElementById("erro-box");

  if (!uf) {
    mostrarErro("Selecione um estado para continuar.");
    return;
  }

  btn.disabled = true;
  btn.textContent = "Analisando...";
  resultado.classList.add("hidden");
  erroBox.classList.add("hidden");

  try {
    const resp = await fetch("/analisar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ uf }),
    });

    const dados = await resp.json();

    if (!resp.ok) {
      mostrarErro(dados.erro || "Erro ao analisar a região.");
      return;
    }

    exibirResultado(dados);
  } catch (err) {
    mostrarErro("Falha de conexão: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Analisar risco";
  }
}

function exibirResultado(dados) {
  const { estado, clima, risco, casos_2024 } = dados;

  const casosFormatados = casos_2024
    ? casos_2024.toLocaleString("pt-BR")
    : "Não disponível";

  document.getElementById("resultado-inner").innerHTML = `
    <div class="res-local">📍 ${estado.nome} — ${estado.capital}</div>

    <div class="nivel-badge ${risco.cor}">
      <div class="score">${risco.score}</div>
      <div class="label">Risco ${risco.nivel}</div>
    </div>

    <div class="dados-grid">
      <div class="dado-item">
        <div class="valor">${clima.chuva.toFixed(1)}</div>
        <div class="rotulo">mm de chuva</div>
      </div>
      <div class="dado-item">
        <div class="valor">${clima.temperatura.toFixed(1)}°</div>
        <div class="rotulo">temperatura</div>
      </div>
      <div class="dado-item">
        <div class="valor">${clima.umidade.toFixed(0)}%</div>
        <div class="rotulo">umidade</div>
      </div>
    </div>

    <p class="detalhes-titulo">Fatores analisados</p>
    <ul class="detalhes-lista">
      ${risco.detalhes.map(d => `<li>${d}</li>`).join("")}
    </ul>

    ${casos_2024 ? `
    <div class="casos-box">
      📊 Em 2024, ${estado.nome} registrou <strong>${casosFormatados} casos</strong> confirmados de dengue (SVS/MS)
    </div>` : ""}
  `;

  document.getElementById("resultado").classList.remove("hidden");
}

function mostrarErro(msg) {
  const erroBox = document.getElementById("erro-box");
  erroBox.textContent = "⚠️ " + msg;
  erroBox.classList.remove("hidden");
}

// ===== GRÁFICO =====
let graficoInstance = null;

async function carregarGrafico() {
  if (graficoInstance) return; // já foi carregado

  try {
    const resp = await fetch("/ranking");
    const dados = await resp.json();

    const labels = dados.map(d => d.uf);
    const valores = dados.map(d => d.casos);
    const nomes = dados.map(d => d.nome);

    const maxVal = Math.max(...valores);
    const cores = valores.map(v => {
      const pct = v / maxVal;
      if (pct > 0.7) return "rgba(239, 68, 68, 0.85)";
      if (pct > 0.4) return "rgba(234, 179, 8, 0.85)";
      return "rgba(34, 197, 94, 0.75)";
    });

    const ctx = document.getElementById("grafico-ranking").getContext("2d");

    graficoInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "Casos confirmados (2024)",
          data: valores,
          backgroundColor: cores,
          borderRadius: 6,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: (items) => nomes[items[0].dataIndex],
              label: (item) =>
                ` ${item.raw.toLocaleString("pt-BR")} casos confirmados`,
            },
            backgroundColor: "#1e2d45",
            titleColor: "#f0f4ff",
            bodyColor: "#8b9ab5",
            borderColor: "rgba(255,255,255,0.08)",
            borderWidth: 1,
            padding: 12,
            titleFont: { family: "Syne", weight: "700", size: 13 },
          },
        },
        scales: {
          x: {
            ticks: { color: "#8b9ab5", font: { family: "DM Sans", size: 12 } },
            grid: { color: "rgba(255,255,255,0.04)" },
          },
          y: {
            ticks: {
              color: "#8b9ab5",
              font: { family: "DM Sans", size: 11 },
              callback: (val) => {
                if (val >= 1_000_000) return (val / 1_000_000).toFixed(1) + "M";
                if (val >= 1_000) return (val / 1_000).toFixed(0) + "k";
                return val;
              },
            },
            grid: { color: "rgba(255,255,255,0.05)" },
          },
        },
      },
    });
  } catch (err) {
    console.error("Erro ao carregar gráfico:", err);
  }
}

// ===== INIT =====
document.addEventListener("DOMContentLoaded", () => {
  carregarEstados();
});