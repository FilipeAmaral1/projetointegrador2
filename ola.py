import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime

conn = sqlite3.connect('estoque.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        quantidade INTEGER NOT NULL,
        valor REAL NOT NULL,
        validade TEXT NOT NULL
    );
""")
conn.commit()

class SistemaEstoque:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Estoque")
        self.root.geometry("800x600")
        self.root.configure(bg="#FFA500")
        
        self.nome = tk.StringVar()
        self.quantidade = tk.IntVar()
        self.valor = tk.DoubleVar()
        self.validade = tk.StringVar(value=datetime.today().strftime('%d/%m/%Y'))
        self.produto_selecionado = None
        
        self.create_widgets()
        self.load_data()  # Carregar os dados da tabela ao iniciar

    def create_widgets(self):
        frame = tk.Frame(self.root, bg="#FFA500")
        frame.pack(pady=20)

        tk.Label(frame, text="Nome:", bg="#FFA500", fg="white").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(frame, textvariable=self.nome, width=30).grid(row=0, column=1, padx=10, pady=5)

        tk.Label(frame, text="Quantidade:", bg="#FFA500", fg="white").grid(row=0, column=2, padx=10, pady=5, sticky="e")
        tk.Entry(frame, textvariable=self.quantidade, width=30).grid(row=0, column=3, padx=10, pady=5)

        tk.Label(frame, text="Valor:", bg="#FFA500", fg="white").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(frame, textvariable=self.valor, width=30).grid(row=1, column=1, padx=10, pady=5)

        tk.Label(frame, text="Validade:", bg="#FFA500", fg="white").grid(row=1, column=2, padx=10, pady=5, sticky="e")
        
        self.validade_entry = DateEntry(frame, textvariable=self.validade, width=30, background="darkblue", foreground="white", borderwidth=2)
        self.validade_entry.grid(row=1, column=3, padx=10, pady=5)

        tk.Button(self.root, text="Adicionar Produto", command=self.adicionar_produto).pack(pady=20)

        self.tree = ttk.Treeview(self.root, columns=("id", "nome", "quantidade", "valor", "validade"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("quantidade", text="Quantidade")
        self.tree.heading("valor", text="Valor")
        self.tree.heading("validade", text="Validade")
        self.tree.column("id", width=30)
        self.tree.column("nome", width=150)
        self.tree.column("quantidade", width=100)
        self.tree.column("valor", width=100)
        self.tree.column("validade", width=100)
        self.tree.pack(pady=20)

        button_frame = tk.Frame(self.root, bg="#FFA500")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Excluir Produto", command=self.excluir_produto, bg="white", fg="black").grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Atualizar Produto", command=self.atualizar_produto, bg="white", fg="black").grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text="Fechar", command=self.root.quit, bg="white", fg="black").grid(row=0, column=2, padx=10)

    def adicionar_produto(self):
        nome = self.nome.get()
        quantidade = self.quantidade.get()
        valor = self.valor.get()
        validade = self.validade.get()
        
        if not (nome and quantidade and valor and validade):
            messagebox.showwarning("Atenção", "Todos os campos devem ser preenchidos!")
            return
        
        try:
            cursor.execute("INSERT INTO produtos (nome, quantidade, valor, validade) VALUES (?, ?, ?, ?)",
                           (nome, quantidade, valor, validade))
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
            self.load_data()
            self.limpar_campos()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Erro ao adicionar produto!")
    
    def excluir_produto(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um produto para excluir!")
            return
        
        produto_id = self.tree.item(selected_item, 'values')[0]
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        conn.commit()
        
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='produtos'")
        conn.commit()

        messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
        self.load_data()

    def atualizar_produto(self):
        if not self.produto_selecionado:
            messagebox.showwarning("Atenção", "Selecione um produto para atualizar!")
            return
        
        nome = self.nome.get()
        quantidade = self.quantidade.get()
        valor = self.valor.get()
        validade = self.validade.get()
        
        if not (nome and quantidade and valor and validade):
            messagebox.showwarning("Atenção", "Todos os campos devem ser preenchidos!")
            return
        
        produto_id = self.produto_selecionado
        cursor.execute("""
            UPDATE produtos 
            SET nome = ?, quantidade = ?, valor = ?, validade = ? 
            WHERE id = ?
        """, (nome, quantidade, valor, validade, produto_id))
        conn.commit()
        
        messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
        self.load_data()
        self.limpar_campos()
        self.produto_selecionado = None

    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        cursor.execute("SELECT * FROM produtos")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def limpar_campos(self):
        self.nome.set("")
        self.quantidade.set(0)
        self.valor.set(0.0)
        self.validade.set(datetime.today().strftime('%d/%m/%Y'))

    def selecionar_produto(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            produto_id, nome, quantidade, valor, validade = self.tree.item(selected_item, 'values')
            self.produto_selecionado = produto_id
            self.nome.set(nome)
            self.quantidade.set(quantidade)
            self.valor.set(valor)
            self.validade.set(validade)

root = tk.Tk()
app = SistemaEstoque(root)

app.tree.bind("<ButtonRelease-1>", app.selecionar_produto)

root.mainloop()

conn.close()
