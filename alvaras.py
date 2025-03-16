import json
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import os
import pyperclip


CAMINHO_DOCUMENTOS = os.path.join(os.path.expanduser("~"), "Documents")
ARQUIVO_DADOS = os.path.join(CAMINHO_DOCUMENTOS, "alvaras.json")
CAMINHO_ICONE = os.path.join(os.path.dirname(__file__), "alvara.ico")
QRCODE_PIX = os.path.join(os.path.dirname(__file__), "qrcode_pix.png")


if not os.path.exists(CAMINHO_DOCUMENTOS):
    os.makedirs(CAMINHO_DOCUMENTOS)

if not os.path.exists(CAMINHO_ICONE):
    print(f"Erro: O arquivo de ícone '{CAMINHO_ICONE}' não foi encontrado.")
else:
    print(f"Ícone encontrado: {CAMINHO_ICONE}")


def carregar_dados():
    try:
        with open(ARQUIVO_DADOS, "r") as f:
            dados = json.load(f)
            for item in dados:
                for key in item:
                    if isinstance(item[key], (str, int)):
                        item[key] = str(item[key]).strip()
            return dados
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(dados, f, indent=4)


def formatar_cnpj(cnpj):
    """Formata o CNPJ no padrão XX.XXX.XXX/XXXX-XX."""
    cnpj = "".join(filter(str.isdigit, str(cnpj)))  # Remove caracteres não numéricos
    if len(cnpj) != 14:
        return cnpj  # Retorna sem formatação se não tiver 14 dígitos
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def formatar_cnpj_input(event):
    """Formata o CNPJ enquanto o usuário digita."""
    cnpj = event.widget.get()
    cnpj = "".join(filter(str.isdigit, cnpj))  # Remove caracteres não numéricos
    if len(cnpj) > 14:
        cnpj = cnpj[:14]  # Limita a 14 dígitos
    if len(cnpj) >= 12:
        cnpj = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    elif len(cnpj) >= 8:
        cnpj = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:]}"
    elif len(cnpj) >= 5:
        cnpj = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:]}"
    elif len(cnpj) >= 2:
        cnpj = f"{cnpj[:2]}.{cnpj[2:]}"
    event.widget.delete(0, tk.END)
    event.widget.insert(0, cnpj)


def abrir_janela_adicionar():
    janela = tk.Toplevel(root)
    janela.iconbitmap(CAMINHO_ICONE)
    janela.title("Adicionar Alvará")
    janela.configure(bg="#2E2E2E")
    janela.geometry("350x250")  # Ajustei a altura para acomodar melhor os campos

    labels = ["Empresa", "CNPJ", "Prefeitura", "Tipo de Alvará", "Data de Vencimento"]
    entradas = []

    # Configuração das colunas e linhas para expansão
    janela.columnconfigure(
        1, weight=1
    )  # Expande a segunda coluna (onde estão os campos de entrada)
    janela.rowconfigure(
        len(labels), weight=1
    )  # Expande a última linha (onde está o botão)

    for i, label in enumerate(labels):
        lbl = ttk.Label(janela, text=label, background="#2E2E2E", foreground="white")
        lbl.grid(row=i, column=0, padx=5, pady=5, sticky="e")

        if label == "Tipo de Alvará":
            entrada = ttk.Combobox(
                janela, values=["Localização", "Vigilância", "Bombeiros", "Policial"]
            )
        elif label == "Data de Vencimento":
            entrada = DateEntry(
                janela, date_pattern="dd/MM/yyyy", background="#444", foreground="white"
            )
        elif label == "CNPJ":
            entrada = ttk.Entry(janela)
            entrada.bind("<KeyRelease>", formatar_cnpj_input)
        else:
            entrada = ttk.Entry(janela)

        entrada.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
        entradas.append(entrada)

    def salvar_alvara():
        valores = [
            e.get().strip() if isinstance(e, tk.Entry) else e.get() for e in entradas
        ]
        empresa, cnpj, prefeitura, tipo_alvara, data_vencimento = valores

        if not all(valores):
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos!")
            return

        # Formata o CNPJ antes de salvar
        cnpj_formatado = formatar_cnpj(cnpj)

        dados = carregar_dados()
        dados.append(
            {
                "Empresa": empresa,
                "CNPJ": cnpj_formatado,  # Salva o CNPJ formatado
                "Prefeitura": prefeitura,
                "Tipo de Alvará": tipo_alvara,
                "Data de Vencimento": data_vencimento,
            }
        )
        salvar_dados(dados)
        atualizar_lista()
        janela.destroy()
        messagebox.showinfo("Sucesso", "Alvará cadastrado com sucesso!")

    # Botão Salvar centralizado e ocupando toda a largura
    btn_salvar = ttk.Button(janela, text="Salvar", command=salvar_alvara)
    btn_salvar.grid(
        row=len(labels), column=0, columnspan=2, padx=10, pady=10, sticky="ew"
    )


def excluir_alvara():
    selecionado = tree.selection()
    if not selecionado:
        messagebox.showerror("Erro", "Selecione um alvará para excluir!")
        return

    for item_id in selecionado:
        item = tree.item(item_id)
        valores = item["values"]

        dados = carregar_dados()
        dados = [
            d
            for d in dados
            if not (
                d["Empresa"].strip() == str(valores[0]).strip()
                and d["CNPJ"].strip()
                == str(valores[1]).strip()  # CNPJ já está formatado
                and d["Prefeitura"].strip() == str(valores[2]).strip()
                and d["Tipo de Alvará"].strip() == str(valores[3]).strip()
                and d["Data de Vencimento"].strip() == str(valores[4]).strip()
            )
        ]

        salvar_dados(dados)

    atualizar_lista()
    messagebox.showinfo("Sucesso", "Alvará(s) excluído(s) com sucesso!")


def filtrar_alvaras(event=None):
    termo = entrada_pesquisa.get().lower()
    atualizar_lista(termo)


def atualizar_lista(termo_pesquisa=None):
    tree.delete(*tree.get_children())
    dados = carregar_dados()
    hoje = datetime.date.today()

    dados.sort(
        key=lambda x: datetime.datetime.strptime(x["Data de Vencimento"], "%d/%m/%Y")
    )

    if termo_pesquisa:
        dados = [
            d
            for d in dados
            if any(termo_pesquisa in str(valor).lower() for valor in d.values())
        ]

    for alvara in dados:
        data_vencimento = datetime.datetime.strptime(
            alvara["Data de Vencimento"], "%d/%m/%Y"
        ).date()
        dias_para_vencer = (data_vencimento - hoje).days

        if dias_para_vencer < 10:
            cor = "#FF4C4C"
        elif dias_para_vencer <= 25:
            cor = "#FFC107"
        else:
            cor = "#28A745"

        # Exibe o CNPJ formatado diretamente
        tree.insert(
            "",
            "end",
            values=(
                alvara["Empresa"],
                alvara["CNPJ"],  # Já está formatado
                alvara["Prefeitura"],
                alvara["Tipo de Alvará"],
                alvara["Data de Vencimento"],
            ),
            tags=(cor,),
        )

    tree.tag_configure("#FF4C4C", background="#FF4C4C", foreground="white")
    tree.tag_configure("#FFC107", background="#FFC107")
    tree.tag_configure("#28A745", background="#28A745", foreground="white")


def copiar_texto():
    texto_para_copiar = "00020126860014BR.GOV.BCB.PIX0136b5dd0b88-eea8-47ed-bea4-82cde93a2b480224Obrigado! Att. SalvaCode520400005303986540520.005802BR5918Douglas Luis Dutra6009SAO PAULO621405106ssonFb3r3630418D7"  # Substitua pelo código PIX real
    try:
        pyperclip.copy(texto_para_copiar)
        messagebox.showinfo(
            "Sucesso", "Código PIX copiado para a área de transferência!"
        )
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao copiar o código PIX: {e}")


def abrir_janela_donate():
    janela = tk.Toplevel(root)
    janela.iconbitmap(CAMINHO_ICONE)
    janela.title("Informações")
    janela.configure(bg="#2E2E2E")
    janela.geometry("325x490")

    frame = ttk.Frame(janela)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Mensagem principal
    mensagem = ttk.Label(
        frame,
        text="Este app te ajudou?\nAjude o desenvolvedor com um PIX!",
        background="#2E2E2E",
        foreground="white",
        font=("Arial", 12, "bold"),
    )
    mensagem.grid(row=0, column=0, columnspan=2, pady=10)

    # Instruções para o PIX
    instrucoes = ttk.Label(
        frame,
        text="1. Abra o app do seu banco.\n2. Escolha a opção PIX.\n3. Aponte a câmera para o QR Code abaixo. \n4. Faça uma sugestão e doe um valor.",
        background="#2E2E2E",
        foreground="white",
        font=("Arial", 10),
    )
    instrucoes.grid(row=1, column=0, columnspan=2, pady=10)

    # QR Code
    qrcode = tk.PhotoImage(file=QRCODE_PIX)  # Substitua pelo caminho do seu QR Code PIX
    lbl_qrcode = ttk.Label(frame, image=qrcode, background="#2E2E2E")
    lbl_qrcode.image = qrcode  # Mantém uma referência para evitar garbage collection
    lbl_qrcode.grid(row=2, column=0, columnspan=2, pady=10)

    # Botão para copiar o texto do QR Code
    btn_copiar = ttk.Button(
        frame, text="Copiar Código PIX", command=copiar_texto, width=20
    )  # Ajuste a largura do botão
    btn_copiar.grid(row=3, column=0, columnspan=2, pady=10)

    # Créditos
    creditos = ttk.Label(
        frame,
        text="Desenvolvido por douglasluisdutra@gmail.com",
        background="#2E2E2E",
        foreground="white",
        font=("Arial", 10),
    )
    creditos.grid(row=4, column=0, columnspan=2, pady=10)


# Configuração da interface
root = tk.Tk()
root.iconbitmap(CAMINHO_ICONE)
root.title("Gerenciador de Alvarás")
root.configure(bg="#2E2E2E")


style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background="#2E2E2E")
style.configure("TLabel", background="#2E2E2E", foreground="white")
style.configure("TButton", background="#007BFF", foreground="white")
style.map("TButton", background=[("active", "#0056b3")])
style.configure(
    "Treeview", background="#444", fieldbackground="#444", foreground="white"
)
style.configure("Treeview.Heading", background="#2E2E2E", foreground="white")
style.map("Treeview", background=[("selected", "#007BFF")])

# Botão Donate
btn_donate = ttk.Button(root, text="Informações", command=abrir_janela_donate)
btn_donate.pack(side="top", anchor="ne", padx=10, pady=10)

# Frame de botões
frame_botoes = ttk.Frame(root)
frame_botoes.pack(pady=10, padx=10, fill="x")

btn_novo = ttk.Button(frame_botoes, text="Novo Alvará", command=abrir_janela_adicionar)
btn_novo.pack(side="left", padx=5)

btn_excluir = ttk.Button(
    frame_botoes, text="Excluir Alvará", command=excluir_alvara, style="Red.TButton"
)
btn_excluir.pack(side="left", padx=5)

# Estilo personalizado para o botão excluir
style.configure("Red.TButton", background="#FF4C4C", foreground="white")
style.map("Red.TButton", background=[("active", "#CC0000")])

# Frame de pesquisa
frame_pesquisa = ttk.Frame(root)
frame_pesquisa.pack(pady=5, padx=10, fill="x")

ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side="left", padx=5)
entrada_pesquisa = ttk.Entry(frame_pesquisa)
entrada_pesquisa.pack(side="left", padx=5, fill="x", expand=True)
entrada_pesquisa.bind("<KeyRelease>", filtrar_alvaras)

# Treeview
colunas = ("Empresa", "CNPJ", "Prefeitura", "Tipo de Alvará", "Data de Vencimento")
tree = ttk.Treeview(root, columns=colunas, show="headings", height=15)
for col in colunas:
    tree.heading(col, text=col)
    tree.column(col, width=150)
tree.pack(pady=10, padx=10, fill="both", expand=True)

atualizar_lista()
root.mainloop()
