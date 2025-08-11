from flask import Flask, render_template, request
import io

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Campos esperados no formulário
        campos = [
            "debito_maquina", "credito_maquina", "qrcode_maquina",
            "dinheiro_contado", "dinheiro_consumer",  # Incluído dinheiro_consumer
            "debito_consumer", "credito_consumer",
            "qrcode_consumer", "pix_consumer", "despesas"
        ]

        # Captura e converte os dados para float, ou zero se vazio
        dados = {campo: float(request.form.get(campo) or 0) for campo in campos}
        dados["data"] = request.form.get("data") or ""

        # Soma total das vendas incluindo dinheiro_consumer
        total_vendas = sum([
            dados["debito_maquina"], dados["credito_maquina"], dados["qrcode_maquina"],
            dados["dinheiro_contado"], dados["dinheiro_consumer"],
            dados["debito_consumer"], dados["credito_consumer"],
            dados["qrcode_consumer"], dados["pix_consumer"]
        ])

        liquido = total_vendas - dados["despesas"]

        # Calcula as diferenças
        diferencas = {
            "Débito": round(dados["debito_consumer"] - dados["debito_maquina"], 2),
            "Crédito": round(dados["credito_consumer"] - dados["credito_maquina"], 2),
            "QR Code": round(dados["qrcode_consumer"] - dados["qrcode_maquina"], 2),
            "Dinheiro": round(dados["dinheiro_consumer"] - dados["dinheiro_contado"], 2)  # corrigido
        }

        # Filtra as diferenças significativas (> 0.009 em módulo)
        diferencas_existentes = {k: v for k, v in diferencas.items() if abs(v) > 0.009}

        # Monta o texto do fechamento
        txt = io.StringIO()
        txt.write("********** FECHAMENTO DE CAIXA **********\n")
        txt.write(f"Data: {dados['data']}\n")
        txt.write("-----------------------------------------\n")
        txt.write(f"Débito Máquina....: R$ {dados['debito_maquina']:.2f}\n")
        txt.write(f"Débito Consumer...: R$ {dados['debito_consumer']:.2f}\n")
        txt.write("\n")
        txt.write(f"Crédito Máquina...: R$ {dados['credito_maquina']:.2f}\n")
        txt.write(f"Crédito Consumer..: R$ {dados['credito_consumer']:.2f}\n")
        txt.write("\n")
        txt.write(f"QR Code Máquina...: R$ {dados['qrcode_maquina']:.2f}\n")
        txt.write(f"QR Code Consumer..: R$ {dados['qrcode_consumer']:.2f}\n")
        txt.write("\n")
        txt.write(f"Pix Chave........: R$ {dados['pix_consumer']:.2f}\n")
        txt.write(f"Dinheiro no Consumer.: R$ {dados['dinheiro_contado']:.2f}\n")
        txt.write(f"Dinheiro no Caixa.: R$ {dados['dinheiro_consumer']:.2f}\n")
        txt.write("\n")
        txt.write(f"Despesas..........: R$ {dados['despesas']:.2f}\n")
        txt.write("-----------------------------------------\n")
        txt.write(f"TOTAL VENDAS......: R$ {total_vendas:.2f}\n")
        txt.write(f"VALOR LÍQUIDO.....: R$ {liquido:.2f}\n")
        txt.write("-----------------------------------------\n")

        if diferencas_existentes:
            txt.write("\nDiferenças:\n")
            for k, v in diferencas_existentes.items():
                txt.write(f"- {k}: R$ {v:.2f}\n")

        txt.write("*****************************************\n")

        return f"<pre>{txt.getvalue()}</pre>"

    return render_template("form.html", caixa=None)


if __name__ == "__main__":
    app.run(debug=True)
