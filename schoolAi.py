import customtkinter as ctk
import sqlite3
from tkinter import messagebox, filedialog
from PIL import Image
import os

# --- 1. BANCO DE DATOS ---
def init_db():
    conn = sqlite3.connect("sistema.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, turma TEXT, foto TEXT, professor_id INTEGER,
            FOREIGN KEY (professor_id) REFERENCES usuarios (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER,
            valor REAL,
            FOREIGN KEY (aluno_id) REFERENCES alunos (id)
        )
    """)
    conn.commit()
    conn.close()

# --- 2. JANELA DA FICHA DO ALUNO (COM LISTA DE NOTAS) ---
class FichaAluno(ctk.CTkToplevel):
    def __init__(self, aluno_id, nome_aluno):
        super().__init__()
        self.aluno_id = aluno_id
        self.title(f"Ficha: {nome_aluno}")
        self.geometry("500x750")
        self.grab_set()

        # Foto
        self.label_foto = ctk.CTkLabel(self, text="Sem Foto", width=180, height=180, fg_color="gray20", corner_radius=10)
        self.label_foto.pack(pady=15)
        ctk.CTkButton(self, text="Selecionar Foto", command=self.salvar_foto).pack()

        # Média
        self.label_media = ctk.CTkLabel(self, text="Média Atual: 0.0", font=("Roboto", 22, "bold"), text_color="#2fa572")
        self.label_media.pack(pady=15)

        # Entrada de Notas
        self.frame_add = ctk.CTkFrame(self)
        self.frame_add.pack(pady=10, padx=20, fill="x")
        self.entry_nota = ctk.CTkEntry(self.frame_add, placeholder_text="Nota (Ex: 8.5)")
        self.entry_nota.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        ctk.CTkButton(self.frame_add, text="Adicionar", width=100, command=self.salvar_nota).pack(side="left", padx=10)

        # --- LISTA DE NOTAS (NOVIDADE) ---
        ctk.CTkLabel(self, text="Histórico de Notas:", font=("Roboto", 14, "italic")).pack(pady=(10, 0))
        self.scroll_notas = ctk.CTkScrollableFrame(self, height=250, label_text="Notas Lançadas")
        self.scroll_notas.pack(pady=10, padx=20, fill="both", expand=True)

        self.atualizar_tela_inteira()

    def salvar_foto(self):
        caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png *.jpeg")])
        if caminho:
            conn = sqlite3.connect("sistema.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE alunos SET foto = ? WHERE id = ?", (caminho, self.aluno_id))
            conn.commit()
            conn.close()
            self.atualizar_tela_inteira()

    def salvar_nota(self):
        try:
            valor = float(self.entry_nota.get().replace(',', '.'))
            conn = sqlite3.connect("sistema.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO notas (aluno_id, valor) VALUES (?, ?)", (self.aluno_id, valor))
            conn.commit()
            conn.close()
            self.entry_nota.delete(0, 'end')
            self.atualizar_tela_inteira()
        except ValueError:
            messagebox.showerror("Erro", "Formato de nota inválido!")

    def remover_nota(self, nota_id):
        if messagebox.askyesno("Confirmar", "Deseja excluir esta nota?"):
            conn = sqlite3.connect("sistema.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notas WHERE id = ?", (nota_id,))
            conn.commit()
            conn.close()
            self.atualizar_tela_inteira()

    def editar_nota(self, nota_id):
        novo_valor = ctk.CTkInputDialog(text="Digite a nova nota:", title="Editar").get_input()
        if novo_valor:
            try:
                valor_f = float(novo_valor.replace(',', '.'))
                conn = sqlite3.connect("sistema.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE notas SET valor = ? WHERE id = ?", (valor_f, nota_id))
                conn.commit()
                conn.close()
                self.atualizar_tela_inteira()
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido!")

    def atualizar_tela_inteira(self):
        conn = sqlite3.connect("sistema.db")
        cursor = conn.cursor()

        # 1. Carregar Foto
        cursor.execute("SELECT foto FROM alunos WHERE id = ?", (self.aluno_id,))
        res_foto = cursor.fetchone()
        if res_foto and res_foto[0] and os.path.exists(res_foto[0]):
            img = ctk.CTkImage(Image.open(res_foto[0]), size=(180, 180))
            self.label_foto.configure(image=img, text="")

        # 2. Calcular Média
        cursor.execute("SELECT AVG(valor) FROM notas WHERE aluno_id = ?", (self.aluno_id,))
        media = cursor.fetchone()[0]
        self.label_media.configure(text=f"Média Atual: {media:.2f}" if media else "Média Atual: 0.0")

        # 3. Listar Notas individuais
        for w in self.scroll_notas.winfo_children(): w.destroy()
        cursor.execute("SELECT id, valor FROM notas WHERE aluno_id = ?", (self.aluno_id,))
        for n_id, n_val in cursor.fetchall():
            f = ctk.CTkFrame(self.scroll_notas)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=f"Nota: {n_val}").pack(side="left", padx=10)
            ctk.CTkButton(f, text="Editar", width=50, command=lambda id=n_id: self.editar_nota(id)).pack(side="right", padx=5)
            ctk.CTkButton(f, text="X", width=30, fg_color="#922", command=lambda id=n_id: self.remover_nota(id)).pack(side="right", padx=5)
        
        conn.close()

# --- 3. DASHBOARD ---
class Dashboard(ctk.CTkToplevel):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.title("School.Ai - Painel")
        self.after(0, lambda: self.state('zoomed'))

        # Header
        ctk.CTkLabel(self, text=f"Prof(a). {user_data[1]}", font=("Roboto", 24)).pack(pady=10)

        # Cadastro
        frame_cad = ctk.CTkFrame(self)
        frame_cad.pack(pady=10, fill="x", padx=20)
        self.en_nome = ctk.CTkEntry(frame_cad, placeholder_text="Nome do Aluno")
        self.en_nome.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        self.en_turma = ctk.CTkEntry(frame_cad, placeholder_text="Turma")
        self.en_turma.pack(side="left", padx=10)
        ctk.CTkButton(frame_cad, text="+ Cadastrar", command=self.add_aluno).pack(side="left", padx=10)

        # Lista
        self.scroll = ctk.CTkScrollableFrame(self, label_text="Lista de Alunos")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)
        self.atualizar_lista()

    def add_aluno(self):
        n, t = self.en_nome.get(), self.en_turma.get()
        if n and t:
            conn = sqlite3.connect("sistema.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO alunos (nome, turma, professor_id) VALUES (?, ?, ?)", (n, t, self.user_data[0]))
            conn.commit(); conn.close()
            self.en_nome.delete(0, 'end'); self.en_turma.delete(0, 'end')
            self.atualizar_lista()

    def atualizar_lista(self):
        for w in self.scroll.winfo_children(): w.destroy()
        conn = sqlite3.connect("sistema.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, turma FROM alunos WHERE professor_id = ?", (self.user_data[0],))
        for alu in cursor.fetchall():
            ctk.CTkButton(self.scroll, text=f"{alu[1]} - Turma: {alu[2]}", anchor="w", 
                          command=lambda id=alu[0], nome=alu[1]: FichaAluno(id, nome)).pack(fill="x", pady=2)
        conn.close()

# --- 4. TELA DE LOGIN ---
def entrar():
    conn = sqlite3.connect("sistema.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (en_u.get(), en_s.get()))
    res = cursor.fetchone()
    if res:
        app.withdraw()
        Dashboard(res).protocol("WM_DELETE_WINDOW", lambda: app.quit())
    else: messagebox.showerror("Erro", "Login incorreto")

def cadastrar():
    try:
        conn = sqlite3.connect("sistema.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, password) VALUES (?,?)", (en_u.get(), en_s.get()))
        conn.commit(); conn.close()
        messagebox.showinfo("OK", "Professor criado!")
    except: messagebox.showerror("Erro", "Nome de usuário já existe")

init_db()
app = ctk.CTk()
app.geometry("400x400")
ctk.CTkLabel(app, text="School.Ai", font=("Roboto", 28)).pack(pady=30)
en_u = ctk.CTkEntry(app, placeholder_text="Usuário"); en_u.pack(pady=10)
en_s = ctk.CTkEntry(app, placeholder_text="Senha", show="*"); en_s.pack(pady=10)
ctk.CTkButton(app, text="Entrar", command=entrar).pack(pady=10)
ctk.CTkButton(app, text="Criar Conta", fg_color="gray30", command=cadastrar).pack()
app.mainloop()
