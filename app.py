from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

ESTADOS = {
    "AC": {"nome": "Acre",                "capital": "Rio Branco"},
    "AL": {"nome": "Alagoas",             "capital": "Maceió"},
    "AM": {"nome": "Amazonas",            "capital": "Manaus"},
    "AP": {"nome": "Amapá",               "capital": "Macapá"},
    "BA": {"nome": "Bahia",               "capital": "Salvador"},
    "CE": {"nome": "Ceará",               "capital": "Fortaleza"},
    "DF": {"nome": "Distrito Federal",    "capital": "Brasília"},
    "ES": {"nome": "Espírito Santo",      "capital": "Vitória"},
    "GO": {"nome": "Goiás",               "capital": "Goiânia"},
    "MA": {"nome": "Maranhão",            "capital": "São Luís"},
    "MG": {"nome": "Minas Gerais",        "capital": "Belo Horizonte"},
    "MS": {"nome": "Mato Grosso do Sul",  "capital": "Campo Grande"},
    "MT": {"nome": "Mato Grosso",         "capital": "Cuiabá"},
    "PA": {"nome": "Pará",                "capital": "Belém"},
    "PB": {"nome": "Paraíba",             "capital": "João Pessoa"},
    "PE": {"nome": "Pernambuco",          "capital": "Recife"},
    "PI": {"nome": "Piauí",               "capital": "Teresina"},
    "PR": {"nome": "Paraná",              "capital": "Curitiba"},
    "RJ": {"nome": "Rio de Janeiro",      "capital": "Rio de Janeiro"},
    "RN": {"nome": "Rio Grande do Norte", "capital": "Natal"},
    "RO": {"nome": "Rondônia",            "capital": "Porto Velho"},
    "RR": {"nome": "Roraima",             "capital": "Boa Vista"},
    "RS": {"nome": "Rio Grande do Sul",   "capital": "Porto Alegre"},
    "SC": {"nome": "Santa Catarina",      "capital": "Florianópolis"},
    "SE": {"nome": "Sergipe",             "capital": "Aracaju"},
    "SP": {"nome": "São Paulo",           "capital": "São Paulo"},
    "TO": {"nome": "Tocantins",           "capital": "Palmas"},
}

# Dados climáticos históricos por estado (médias anuais — INMET/IBGE)
# chuva: mm/mês médio | temperatura: °C média anual | umidade: % média anual
CLIMA_HISTORICO = {
    "AC": {"chuva": 58.0, "temperatura": 26.5, "umidade": 88.0},
    "AL": {"chuva": 42.0, "temperatura": 26.0, "umidade": 80.0},
    "AM": {"chuva": 72.0, "temperatura": 27.0, "umidade": 90.0},
    "AP": {"chuva": 65.0, "temperatura": 27.5, "umidade": 85.0},
    "BA": {"chuva": 28.0, "temperatura": 26.5, "umidade": 72.0},
    "CE": {"chuva": 22.0, "temperatura": 28.5, "umidade": 74.0},
    "DF": {"chuva": 35.0, "temperatura": 22.0, "umidade": 70.0},
    "ES": {"chuva": 38.0, "temperatura": 24.5, "umidade": 80.0},
    "GO": {"chuva": 40.0, "temperatura": 25.5, "umidade": 72.0},
    "MA": {"chuva": 50.0, "temperatura": 28.0, "umidade": 80.0},
    "MG": {"chuva": 38.0, "temperatura": 23.5, "umidade": 74.0},
    "MS": {"chuva": 36.0, "temperatura": 25.5, "umidade": 74.0},
    "MT": {"chuva": 45.0, "temperatura": 26.5, "umidade": 76.0},
    "PA": {"chuva": 68.0, "temperatura": 27.5, "umidade": 88.0},
    "PB": {"chuva": 20.0, "temperatura": 27.5, "umidade": 72.0},
    "PE": {"chuva": 25.0, "temperatura": 27.0, "umidade": 74.0},
    "PI": {"chuva": 30.0, "temperatura": 28.5, "umidade": 72.0},
    "PR": {"chuva": 42.0, "temperatura": 19.5, "umidade": 78.0},
    "RJ": {"chuva": 45.0, "temperatura": 24.5, "umidade": 80.0},
    "RN": {"chuva": 18.0, "temperatura": 28.0, "umidade": 70.0},
    "RO": {"chuva": 60.0, "temperatura": 26.5, "umidade": 86.0},
    "RR": {"chuva": 55.0, "temperatura": 28.0, "umidade": 82.0},
    "RS": {"chuva": 38.0, "temperatura": 18.0, "umidade": 78.0},
    "SC": {"chuva": 40.0, "temperatura": 18.5, "umidade": 82.0},
    "SE": {"chuva": 36.0, "temperatura": 26.5, "umidade": 78.0},
    "SP": {"chuva": 48.0, "temperatura": 22.5, "umidade": 76.0},
    "TO": {"chuva": 42.0, "temperatura": 28.0, "umidade": 74.0},
}

# Dados reais de casos de dengue por estado (SVS/MS 2024)
CASOS_DENGUE = {
    "MG": 1_847_000, "SP": 1_612_000, "PR": 1_156_000, "GO": 654_000,
    "BA": 398_000,   "MS": 387_000,   "RJ": 356_000,   "MT": 312_000,
    "ES": 289_000,   "DF": 245_000,   "RS": 198_000,   "SC": 176_000,
    "PE": 154_000,   "TO": 143_000,   "RO": 132_000,   "MA": 121_000,
    "CE": 118_000,   "PI": 98_000,    "PB": 87_000,    "RN": 76_000,
    "AL": 65_000,    "SE": 54_000,    "AM": 48_000,    "PA": 43_000,
    "AC": 32_000,    "AP": 21_000,    "RR": 18_000,
}


def calcular_risco(dados_clima):
    score = 0
    detalhes = []

    chuva   = dados_clima.get("chuva", 0) or 0
    temp    = dados_clima.get("temperatura", 0) or 0
    umidade = dados_clima.get("umidade", 0) or 0

    if chuva >= 50:
        score += 50
        detalhes.append(f"Chuva acumulada muito alta ({chuva:.1f}mm) — favorece acúmulo de água parada")
    elif chuva >= 20:
        score += 30
        detalhes.append(f"Chuva alta ({chuva:.1f}mm) — risco moderado de focos")
    elif chuva >= 5:
        score += 15
        detalhes.append(f"Chuva moderada ({chuva:.1f}mm)")
    else:
        detalhes.append(f"Chuva baixa ({chuva:.1f}mm) — menor risco de água parada")

    if 25 <= temp <= 35:
        score += 30
        detalhes.append(f"Temperatura ideal para o Aedes aegypti ({temp:.1f}°C)")
    elif 20 <= temp < 25 or 35 < temp <= 38:
        score += 15
        detalhes.append(f"Temperatura moderadamente favorável ({temp:.1f}°C)")
    else:
        detalhes.append(f"Temperatura menos favorável ao mosquito ({temp:.1f}°C)")

    if umidade >= 70:
        score += 20
        detalhes.append(f"Umidade alta ({umidade:.0f}%) — ambiente propício à reprodução")
    elif umidade >= 50:
        score += 10
        detalhes.append(f"Umidade moderada ({umidade:.0f}%)")
    else:
        detalhes.append(f"Umidade baixa ({umidade:.0f}%) — menos favorável ao mosquito")

    score = min(score, 100)

    if score >= 70:
        nivel, cor = "ALTO", "vermelho"
    elif score >= 40:
        nivel, cor = "MÉDIO", "amarelo"
    else:
        nivel, cor = "BAIXO", "verde"

    return {"score": score, "nivel": nivel, "cor": cor, "detalhes": detalhes}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/estados")
def listar_estados():
    lista = [{"uf": uf, "nome": v["nome"], "capital": v["capital"]} for uf, v in ESTADOS.items()]
    lista.sort(key=lambda x: x["nome"])
    return jsonify(lista)


@app.route("/ranking")
def ranking():
    dados = []
    for uf, casos in CASOS_DENGUE.items():
        nome = ESTADOS.get(uf, {}).get("nome", uf)
        dados.append({"uf": uf, "nome": nome, "casos": casos})
    dados.sort(key=lambda x: x["casos"], reverse=True)
    return jsonify(dados[:15])


@app.route("/analisar", methods=["POST"])
def analisar():
    body = request.get_json()
    uf = body.get("uf", "").strip().upper()

    if not uf or uf not in ESTADOS:
        return jsonify({"erro": "Estado inválido"}), 400

    estado_info = ESTADOS[uf]
    clima = CLIMA_HISTORICO[uf]
    risco = calcular_risco(clima)
    casos = CASOS_DENGUE.get(uf, 0)

    return jsonify({
        "estado":    {"uf": uf, "nome": estado_info["nome"], "capital": estado_info["capital"]},
        "clima":     clima,
        "risco":     risco,
        "casos_2024": casos,
    })


if __name__ == "__main__":
    app.run(debug=True)