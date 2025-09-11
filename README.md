# School.ai
💻 Built a School Management System in Python with Tkinter &amp; SQLite3 — managing students, classes, and data with an intuitive interface!


🚀 School Management System Project

I developed a desktop application using Python (Tkinter + SQLite3) to manage students and classes in a simple and efficient way.

🔹 Key Features:

Create and manage classes dynamically.

Register students with details such as name, gender, age, and average grade.

Assign students to specific classes.

Search functionality to filter students by name or class.

Intuitive interface designed to make data visualization easy and clear.

This project demonstrates my skills in:
✅ Python development (Tkinter for GUI, SQLite3 for database management)
✅ Designing user-friendly interfaces
✅ Handling CRUD operations efficiently
✅ Building scalable and practical solutions

📌 I created this project as part of my journey to strengthen my skills in software development and database-driven applications, aiming to bring real-world solutions to educational contexts.

Fullcode:



    import customtkinter as ctk
    import sqlite3
    
    def inicializar_banco():
        con = sqlite3.connect("escola.db")
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS turmas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                genero TEXT,
                idade INT,
                nota_media REAL,
                turma_id INT,
                FOREIGN KEY(turma_id) REFERENCES turmas(id)
            )
        """)
        con.commit()
        con.close()
    
    inicializar_banco()
    
    
    def atualizar_turmas():
        con = sqlite3.connect("escola.db")
        cur = con.cursor()
        cur.execute("SELECT id, nome FROM turmas")
        turmas = cur.fetchall()
        con.close()
        turma_combo.set("")  # limpa seleção
        turma_combo.configure(values=[t[1] for t in turmas])
        turma_dict.clear()
        turma_dict.update({t[1]: t[0] for t in turmas})
    
    def criar_turma():
        nome = campo_nova_turma.get().strip()
        if not nome:
            resultado_feedback.configure(text="Digite o nome da turma.", text_color="red")
            return
        con = sqlite3.connect("escola.db")
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO turmas (nome) VALUES (?)", (nome,))
            con.commit()
            resultado_feedback.configure(text=f"Turma '{nome}' criada com sucesso!", text_color="green")
        except sqlite3.IntegrityError:
            resultado_feedback.configure(text=f"Turma '{nome}' já existe!", text_color="red")
        finally:
            con.close()
        campo_nova_turma.delete(0, "end")
        atualizar_turmas()
    
    def adicionar_aluno():
        nome = campo_nome.get().strip()
        genero = campo_genero.get().strip()
        idade = campo_idade.get().strip()
        nota = campo_nota.get().strip()
        turma_nome = turma_combo.get().strip()
    
        if not nome or not genero or not idade or not nota or not turma_nome:
            resultado_feedback.configure(text="Preencha todos os campos e escolha uma turma!", text_color="red")
            return
    
        try:
            idade = int(idade)
            nota = float(nota)
        except ValueError:
            resultado_feedback.configure(text="Idade deve ser um número inteiro e a nota um número decimal!", text_color="red")
            return
    
        if idade < 0:
            resultado_feedback.configure(text="Idade não pode ser negativa!", text_color="red")
            return
        if nota < 0 or nota > 10:
            resultado_feedback.configure(text="Nota deve estar entre 0 e 10!", text_color="red")
            return
    
        turma_id = turma_dict.get(turma_nome)
        con = sqlite3.connect("escola.db")
        cur = con.cursor()
        try:
            cur.execute("""
                INSERT INTO alunos (nome, genero, idade, nota_media, turma_id)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, genero, idade, nota, turma_id))
            con.commit()
            resultado_feedback.configure(text=f"Aluno '{nome}' adicionado à turma '{turma_nome}'!", text_color="green")
        except Exception as e:
            resultado_feedback.configure(text=f"Erro ao adicionar aluno: {e}", text_color="red")
        finally:
            con.close()
        campo_nome.delete(0, "end")
        campo_genero.delete(0, "end")
        campo_idade.delete(0, "end")
        campo_nota.delete(0, "end")
        # Limpa a consulta para não confundir o usuário
        campo_consulta.delete(0, "end")
    
    def consultar():
        busca = campo_consulta.get().strip()
        con = sqlite3.connect("escola.db")
        cur = con.cursor()
    
        if not busca:
            resultado_texto.configure(state="normal")
            resultado_texto.delete("1.0", "end")
            resultado_texto.insert("end", "Digite um nome ou turma para pesquisar.")
            resultado_texto.configure(state="disabled")
            return
    
        cur.execute("""
            SELECT a.nome, a.genero, a.idade, a.nota_media, t.nome
            FROM alunos a
            LEFT JOIN turmas t ON a.turma_id = t.id
            WHERE a.nome LIKE ? OR t.nome LIKE ?
        """, (f"%{busca}%", f"%{busca}%"))
        dados = cur.fetchall()
        con.close()
    
        resultado_texto.configure(state="normal")
        resultado_texto.delete("1.0", "end")
        if dados:
            header = f"{'Nome':<20}{'Gênero':<10}{'Idade':<6}{'Nota':<6}{'Turma':<15}\n"
            resultado_texto.insert("end", header)
            resultado_texto.insert("end", "-"*65 + "\n")
            for aluno in dados:
                linha = f"{aluno[0]:<20}{aluno[1]:<10}{aluno[2]:<6}{aluno[3]:<6}{aluno[4]:<15}\n"
                resultado_texto.insert("end", linha)
        else:
            resultado_texto.insert("end", "Nenhum registro encontrado.")
        resultado_texto.configure(state="disabled")
        app = ctk.CTk()
        app.title("Sistema Escolar")
        app.geometry("1000x550")
    
    turma_dict = {}
    
    
    frame_esquerda = ctk.CTkFrame(app, corner_radius=10)
    frame_esquerda.pack(side="left", fill="both", expand=True, padx=(20,10), pady=20)
    
    frame_direita = ctk.CTkFrame(app, corner_radius=10)
    frame_direita.pack(side="right", fill="both", expand=True, padx=(10,20), pady=20)
    
    
    
    
    frame_criar_turma = ctk.CTkFrame(frame_esquerda)
    frame_criar_turma.pack(fill="x", pady=(0,15))
    ctk.CTkLabel(frame_criar_turma, text="Criar nova turma", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
    campo_nova_turma = ctk.CTkEntry(frame_criar_turma, placeholder_text='Nome da turma')
    campo_nova_turma.pack(pady=5, fill="x")
    botao_nova_turma = ctk.CTkButton(frame_criar_turma, text="Criar turma", command=criar_turma)
    botao_nova_turma.pack(pady=5)
    
    
    resultado_feedback = ctk.CTkLabel(frame_esquerda, text="", fg_color="transparent")
    resultado_feedback.pack(pady=5)
    
    
    frame_cadastro_aluno = ctk.CTkFrame(frame_esquerda)
    frame_cadastro_aluno.pack(fill="both", expand=True)
    ctk.CTkLabel(frame_cadastro_aluno, text="Cadastrar novo aluno", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
    
    campo_nome = ctk.CTkEntry(frame_cadastro_aluno, placeholder_text='Nome')
    campo_nome.pack(pady=5, fill="x")
    campo_genero = ctk.CTkEntry(frame_cadastro_aluno, placeholder_text='Gênero')
    campo_genero.pack(pady=5, fill="x")
    campo_idade = ctk.CTkEntry(frame_cadastro_aluno, placeholder_text='Idade')
    campo_idade.pack(pady=5, fill="x")
    campo_nota = ctk.CTkEntry(frame_cadastro_aluno, placeholder_text='Nota média (0 a 10)')
    campo_nota.pack(pady=5, fill="x")
    turma_combo = ctk.CTkComboBox(frame_cadastro_aluno, values=[])
    turma_combo.pack(pady=5, fill="x")
    botao_cadastrar = ctk.CTkButton(frame_cadastro_aluno, text='Adicionar aluno', command=adicionar_aluno)
    botao_cadastrar.pack(pady=10)
    
    atualizar_turmas()
    
    frame_consulta = ctk.CTkFrame(frame_direita)
    frame_consulta.pack(fill="both", expand=True)
    
    ctk.CTkLabel(frame_consulta, text="Consultar alunos por nome ou turma", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
    campo_consulta = ctk.CTkEntry(frame_consulta, placeholder_text='Nome ou Turma')
    campo_consulta.pack(pady=5, fill="x")
    botao_consultar = ctk.CTkButton(frame_consulta, text='Pesquisar', command=consultar)
    botao_consultar.pack(pady=5)
    resultado_texto = ctk.CTkTextbox(frame_consulta, width=400, height=400)
    resultado_texto.pack(pady=10, fill="both", expand=True)
    resultado_texto.configure(state="disabled")
    
    app.mainloop()




<img width="985" height="570" alt="Captura de tela 2025-09-11 075621" src="https://github.com/user-attachments/assets/19f0b35d-b68c-4593-a0ba-69e9e4bd347b" />
<img width="995" height="577" alt="Captura de tela 2025-09-11 075316" src="https://github.com/user-attachments/assets/72551668-5230-4d86-9e9a-8cf29cbdacf1" />
<img width="875" height="681" alt="Captura de tela 2025-09-11 075202" src="https://github.com/user-attachments/assets/9321dd68-8329-4246-92c0-978678890dda" />

