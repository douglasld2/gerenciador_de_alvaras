import json
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sys
import os
import pyperclip
from tkinter import filedialog
import subprocess
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import DatePickerDialog

CAMINHO_DOCUMENTOS = os.path.join(os.path.expanduser("~"), "Documents")
ARQUIVO_DADOS = os.path.join(CAMINHO_DOCUMENTOS, "alvaras.json")
CAMINHO_ICONE = os.path.join(os.path.dirname(__file__), "alvara.ico")
QRCODE_PIX = os.path.join(os.path.dirname(__file__), "qrcode_pix.png")


if not os.path.exists(CAMINHO_DOCUMENTOS):
    os.makedirs(CAMINHO_DOCUMENTOS)

def carregar_dados():
    try:
        with open(ARQUIVO_DADOS, "r") as f:
            dados = json.load(f)
            for item in dados:
                # Garante que os novos campos existam
                item.setdefault("Notas", "")
                item.setdefault("Arquivos", [])
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
    janela = tb.Toplevel(root)
    janela.iconbitmap(CAMINHO_ICONE)
    janela.title("Adicionar Alvará")
    janela.geometry("350x300")  # Aumentei a altura para melhor visualização

    labels = ["Empresa", "CNPJ", "Prefeitura", "Tipo de Alvará", "Data de Vencimento"]
    entradas = []

    # Configuração do grid
    janela.columnconfigure(1, weight=1)
    for i in range(len(labels)+1):
        janela.rowconfigure(i, weight=1)

    for i, label in enumerate(labels):
        lbl = tb.Label(janela, text=label)
        lbl.grid(row=i, column=0, padx=5, pady=5, sticky="e")

        if label == "Tipo de Alvará":
            entrada = tb.Combobox(
                janela, 
                values=["Localização", "Vigilância", "Bombeiros", "Policial", "Meio Ambiente"],
            
            )
            entrada.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            
        elif label == "Data de Vencimento":
            entrada = tb.DateEntry(janela)
            entrada.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            
        elif label == "CNPJ":
            entrada = tb.Entry(janela)
            entrada.bind("<KeyRelease>", formatar_cnpj_input)
            entrada.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            
        else:
            entrada = tb.Entry(janela)
            entrada.grid(row=i, column=1, padx=5, pady=5, sticky="ew")

        entradas.append(entrada)

    def salvar_alvara():
        valores = []
        for e in entradas:
            if isinstance(e, tb.Entry):
                valores.append(e.get().strip())
            elif isinstance(e, tb.Combobox):
                valores.append(e.get())
            elif isinstance(e, tb.DateEntry):
                valores.append(e.entry.get())  # Acesso ao Entry interno
                    
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
                "Notas": "",
                "Arquivos": []
            }
        )
        salvar_dados(dados)
        atualizar_lista()
        janela.destroy()
        messagebox.showinfo("Sucesso", "Alvará cadastrado com sucesso!")

    # Botão Salvar centralizado e ocupando toda a largura
    btn_salvar = ttk.Button(janela, text="Salvar", command=salvar_alvara, bootstyle=SUCCESS)
    btn_salvar.grid(
        row=len(labels), column=0, columnspan=2, padx=10, pady=10, sticky="ew"
    )

def excluir_alvara():
    selecionado = tree.selection()
    if not selecionado:
        messagebox.showinfo("Erro", "⚠️ Selecione um alvará para excluir!")
        return

    dados = carregar_dados()  # Carrega os dados do arquivo ou banco de dados
    dados_originais = len(dados)
    
    # Loop para percorrer os itens selecionados na treeview
    for item_id in selecionado:
        item = tree.item(item_id)
        valores = item["values"]
        
        # Garantir que os valores são strings antes de aplicar strip()
        empresa = str(valores[1]).strip() if valores[1] else ""
        cnpj = str(valores[2]).strip() if valores[2] else ""
        prefeitura = str(valores[3]).strip() if valores[3] else ""
        tipo_alvara = str(valores[4]).strip() if valores[4] else ""
        data_vencimento = str(valores[5]).strip() if valores[5] else ""

        # Filtra os dados removendo os itens com as mesmas informações
        dados = [
            d for d in dados
            if not (
                str(d["Empresa"]).strip() == empresa and
                str(d["CNPJ"]).strip() == cnpj and
                str(d["Prefeitura"]).strip() == prefeitura and
                str(d["Tipo de Alvará"]).strip() == tipo_alvara and
                str(d["Data de Vencimento"]).strip() == data_vencimento
            )
        ]
    
    # Verifica se houve alguma exclusão
    if len(dados) < dados_originais:
        salvar_dados(dados)  # Salva os dados atualizados
        atualizar_lista()  # Atualiza a interface com a nova lista de alvarás
        messagebox.showinfo("Sucesso!", f"✅ {dados_originais - len(dados)} alvará(s) excluído(s)!")
    else:
        messagebox.showinfo("Erro", "⚠️ Nenhum alvará foi excluído!")



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

        # Combina os dois ícones em uma única coluna
        # Combina os dois ícones em uma única coluna
        acoes = f"       ℹ️               📁({len(alvara['Arquivos'])})"  # 4 espaços        
        item = tree.insert("", "end", values=(
            acoes,
            alvara["Empresa"],
            alvara["CNPJ"],
            alvara["Prefeitura"],
            alvara["Tipo de Alvará"],
            alvara["Data de Vencimento"],      
        ), tags=(cor, ))

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
    janela.geometry("325x490")

    frame = ttk.Frame(janela)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Mensagem principal
    mensagem = ttk.Label(
        frame,
        text="Este app te ajudou?\nAjude o desenvolvedor com um PIX!",
        foreground="white",
        font=("Arial", 12, "bold"),
    )
    mensagem.grid(row=0, column=0, columnspan=2, pady=10)

    # Instruções para o PIX
    instrucoes = ttk.Label(
        frame,
        text="1. Abra o app do seu banco.\n2. Escolha a opção PIX.\n3. Aponte a câmera para o QR Code abaixo. \n4. Faça uma sugestão e doe um valor.",
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
        foreground="white",
        font=("Arial", 10),
    )
    creditos.grid(row=4, column=0, columnspan=2, pady=10)

def abrir_editor_notas(alvara):
    def salvar_notas():
        notas = txt_notas.get("1.0", tk.END).strip()
        dados = carregar_dados()
        
        # Encontra e atualiza o alvará correto
        for d in dados:
            if (d["Empresa"] == alvara["Empresa"] and 
                d["CNPJ"] == alvara["CNPJ"] and
                d["Prefeitura"] == alvara["Prefeitura"] and
                d["Tipo de Alvará"] == alvara["Tipo de Alvará"] and
                d["Data de Vencimento"] == alvara["Data de Vencimento"]):
                
                d["Notas"] = notas
                break
                
        salvar_dados(dados)
        atualizar_lista()
        janela.destroy()
        messagebox.showinfo("Sucesso", "Notas salvas com sucesso!")

    janela = tk.Toplevel(root)
    janela.title("Editor de Notas")
    txt_notas = tk.Text(janela, width=50, height=10)
    txt_notas.pack(padx=10, pady=10)
    txt_notas.insert("1.0", alvara["Notas"])
    ttk.Button(janela, text="Salvar", command=salvar_notas).pack(pady=5)

def gerenciar_documentos(alvara):
    def adicionar_documento():
        caminho = filedialog.askopenfilename(title="Selecione o Alvará Digitalizado")
        if not caminho:
            return

        def confirmar():
            try:
                # Obter datas formatadas
                emissao = cal_emissao.entry.get()
                vencimento = cal_vencimento.entry.get()
                descricao = entry_descricao.get().strip()

                # Validar datas
                datetime.datetime.strptime(emissao, "%d/%m/%Y")
                datetime.datetime.strptime(vencimento, "%d/%m/%Y")
                
                # Validar se a descrição foi preenchida
                if not descricao:
                    messagebox.showerror("Erro", "A descrição do documento é obrigatória!")
                    return
                
                novo_doc = {
                    "descricao": descricao,  # Adicionando descrição ao documento
                    "caminho": caminho,
                    "emissao": emissao,
                    "vencimento": vencimento
                }
                
                # Atualizar dados
                dados = carregar_dados()
                for d in dados:
                    if (d["Empresa"] == alvara["Empresa"] and 
                        d["CNPJ"] == alvara["CNPJ"] and
                        d["Prefeitura"] == alvara["Prefeitura"] and
                        d["Tipo de Alvará"] == alvara["Tipo de Alvará"] and
                        d["Data de Vencimento"] == alvara["Data de Vencimento"]):
                        
                        d["Arquivos"].append(novo_doc)
                        d["Arquivos"].sort(
                            key=lambda x: datetime.datetime.strptime(x["emissao"], "%d/%m/%Y"), 
                            reverse=True
                        )
                        break
                
                salvar_dados(dados)
                atualizar_lista()
                janela_add.destroy()
                atualizar_lista_docs()
                messagebox.showinfo("Sucesso!", "Arquivo adicionado com sucesso!")

            except ValueError:
                messagebox.showerror("Erro", "Datas inválidas! Use o formato DD/MM/AAAA")

        # Janela para adicionar documento
        janela_add = tb.Toplevel(janela)
        janela_add.title("Adicionar Documento")

        # Campo de Descrição
        tb.Label(janela_add, text="Descrição:").grid(row=0, column=0, padx=5, pady=5)
        entry_descricao = tb.Entry(janela_add, width=30)
        entry_descricao.grid(row=0, column=1, padx=5, pady=5)

        # Data de Emissão
        tb.Label(janela_add, text="Data de Emissão:").grid(row=1, column=0, padx=5, pady=5)
        cal_emissao = tb.DateEntry(janela_add)
        cal_emissao.grid(row=1, column=1, padx=5, pady=5)
        
        # Data de Vencimento
        tb.Label(janela_add, text="Data de Vencimento:").grid(row=2, column=0, padx=5, pady=5)
        cal_vencimento = tb.DateEntry(janela_add)
        cal_vencimento.grid(row=2, column=1, padx=5, pady=5)
        
        # Botão Confirmar
        tb.Button(
            janela_add, 
            text="Confirmar", 
            command=confirmar,
            bootstyle="success"
        ).grid(row=3, columnspan=2, pady=10)

    def abrir_documento(event):
        item = tree_docs.selection()[0]
        caminho = tree_docs.item(item, "values")[0]
        os.startfile(caminho)  # Método mais confiável para abrir arquivos

    def atualizar_lista_docs():
        tree_docs.delete(*tree_docs.get_children())
        dados = carregar_dados()
        for d in dados:
            if (d["Empresa"] == alvara["Empresa"] and 
                d["CNPJ"] == alvara["CNPJ"] and
                d["Prefeitura"] == alvara["Prefeitura"] and
                d["Tipo de Alvará"] == alvara["Tipo de Alvará"] and
                d["Data de Vencimento"] == alvara["Data de Vencimento"]):
                
                for doc in d["Arquivos"]:
                    tree_docs.insert("", "end", values=(doc["descricao"], doc["caminho"], doc["emissao"], doc["vencimento"]))
                break

    # Janela principal de gerenciamento
    janela = tb.Toplevel(root)
    janela.title("Gerenciar Documentos")
    
    colunas_2=("Descrição", "Caminho", "Emissão", "Vencimento")
    tree_docs = ttk.Treeview(janela, columns=colunas_2, show="headings", height=15)
    for col in colunas_2:
        tree_docs.heading(col, text=col,  anchor=tk.CENTER)
        tree_docs.column(col, width=150,  anchor=tk.CENTER)
    tree_docs.pack(pady=10, padx=10, fill="both", expand=True)
    
    # Botão Adicionar
    btn_add = tb.Button(
        janela, 
        text="Adicionar Documento", 
        command=adicionar_documento,
        bootstyle="success"
    )
    btn_add.pack(pady=5)
    
    # Evento de duplo clique
    tree_docs.bind("<Double-1>", abrir_documento)
    
    # Carregar documentos existentes
    atualizar_lista_docs()



def on_tree_click(event):
    item = tree.identify_row(event.y)
    col = tree.identify_column(event.x)
    
    if item and col == "#1":  # Coluna de Ações combinada
        # Obtém a posição X do clique dentro da célula
        x = event.x - tree.bbox(item, col)[0]
        
        dados = carregar_dados()
        alvara = dados[tree.index(item)]
        
        # Se o clique foi na primeira metade da célula (ícone de notas)
        if x < tree.bbox(item, col)[2] / 2:
            abrir_editor_notas(alvara)
        else:  # Se foi na segunda metade (ícone de documentos)
            gerenciar_documentos(alvara)


# Configuração da interface
root = tk.Tk()
root.iconbitmap(CAMINHO_ICONE)
root.title("Gerenciador de Alvarás")
style = tb.Style(theme="darkly")
style.configure("Treeview", rowheight=30)  # Ajuste o valor conforme necessário (30, 40, 50...)

# Botão Donate
btn_donate = ttk.Button(root, text="Informações", command=abrir_janela_donate)
btn_donate.pack(side="top", anchor="ne", padx=10, pady=10)

# Frame de botões
frame_botoes = ttk.Frame(root)
frame_botoes.pack(pady=10, padx=10, fill="x")

btn_novo = ttk.Button(frame_botoes, text="Novo Alvará", command=abrir_janela_adicionar, bootstyle=SUCCESS)
btn_novo.pack(side="left", padx=5)

btn_excluir = ttk.Button(
    frame_botoes, text="Excluir Alvará", command=excluir_alvara, bootstyle=DANGER
)
btn_excluir.pack(side="left", padx=5)

# Frame de pesquisa
frame_pesquisa = ttk.Frame(root)
frame_pesquisa.pack(pady=5, padx=10, fill="x")

ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side="left", padx=5)
entrada_pesquisa = ttk.Entry(frame_pesquisa)
entrada_pesquisa.pack(side="left", padx=5, fill="x", expand=True)
entrada_pesquisa.bind("<KeyRelease>", filtrar_alvaras)

# Treeview
colunas = ("Ações", "Empresa", "CNPJ", "Prefeitura", "Tipo de Alvará", "Data de Vencimento" )
tree = ttk.Treeview(root, columns=colunas, show="headings", height=15)
tree.bind("<Button-1>", on_tree_click)
for col in colunas:
    tree.heading(col, text=col, anchor=tk.CENTER)
    tree.column(col, width=150, anchor=tk.CENTER)
tree.pack(pady=10, padx=10, fill="both", expand=True)

atualizar_lista()
root.mainloop()
