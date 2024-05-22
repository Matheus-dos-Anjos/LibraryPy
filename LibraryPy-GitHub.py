import pyodbc # Connects to a SQL database using pyodbc
import uuid
# Connect to the database.
def conectar_banco():
  print("---- Connecting to the Library Server ----")
  # Please obtain the credentials for the database.
  connection_data = (
    "Driver = {SQL Server};"
    "Server = HostName/IP;"
    "Database = your DataBase;"
  )
  try:
    connection = pyodbc.connect(connection_data)
    print("\n---- Successful connection ----")
    return connection.cursor()
  except pyodbc.Error as e:
    print("There was an error in connecting to the database:", e)
    return None
# Etapa 1 - Lists all the books in the library.
def listar_livros(cursor):
    print("A list of books from the library.")
    try:
        cursor.execute("SELECT titulo, autor FROM biblioteca")
        books = cursor.fetchall()
        for ordem, book in enumerate(books, start=1):
            print(ordem, "-", "\n--- Titulo:", book[0], "\n--- Autor:", book[1])
    except pyodbc.Error as e:
        print("Book listing error:", e)
# Etapa 2 - Check if the library has the book.
def verificar_disponibilidade(cursor):
    title = input("Enter the book title: ").lower()
    try:
        cursor.execute("SELECT titulo, disponibilidade FROM biblioteca WHERE LOWER(titulo) = ?", (title,))
        book = cursor.fetchone()
        if book:
            if book[1].lower() == "sim":
                print(f"\nThe book '{book[0]}' is available.")
            else:
                print(f"\nThe book '{book[0]}' is not available.")
        else:
            print(f"\nBook '{title}' is not registered in the library.")
    except pyodbc.Error as e:
        print("Checking availability:", e)
# Etapa 3 - Allows student to reserve book.
def reservar_livro(cursor):
    name = input("Enter the student's name: ").lower()
    try:
        cursor.execute("SELECT id, nome FROM usuarios WHERE LOWER(nome) = ?", (name,))
        aluno = cursor.fetchone()
        if aluno:
            aluno_id = aluno[0]
        else:
            aluno_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO usuarios (id, nome) VALUES (?, ?)", (aluno_id, name))
            cursor.connection.commit()
            print(f"\nO Aluno {name} foi cadastrado com sucesso.")
    except pyodbc.Error as e:
        print("Erro ao cadastrar usuário:", e)
        return

    titulo_livro = input("\nDigite o Título do Livro que deseja reservar: ").lower()
    try:
        cursor.execute("SELECT titulo, disponibilidade FROM biblioteca WHERE LOWER(titulo) = ?", (titulo_livro,))
        livro = cursor.fetchone()
        if livro:
            if livro[1].lower() == "sim":
                cursor.execute("UPDATE biblioteca SET disponibilidade = 'não' WHERE LOWER(titulo) = ?", (titulo_livro,))
                cursor.connection.commit()
                cursor.execute("INSERT INTO reservas (id, livro) VALUES (?, ?)", (aluno_id, livro[0]))
                cursor.connection.commit()
                print(f"\nO livro '{titulo_livro}' foi reservado com sucesso.")
            else:
                print(f"\nO livro '{livro[0]}' não está disponível para reserva no momento.")
        else:
            print(f"\nO Livro '{titulo_livro}' não está cadastrado na biblioteca.")
    except pyodbc.Error as e:
        print("Erro ao reservar livro:", e)
# Etapa 4 - Permite o aluno devolver um livro reservado.
def devolucao_livro(cursor):
    nome = input("Insira o nome completo do Aluno: ").lower()
    try:
        cursor.execute("SELECT id, nome FROM usuarios WHERE LOWER(nome) = ?", (nome,))
        aluno = cursor.fetchone()
        if aluno:
            aluno_id = aluno[0]
            titulo_livro = input("\nDigite o Título do Livro que deseja devolver: ").lower()
            try:
                cursor.execute("SELECT id, livro FROM reservas WHERE id = ? AND LOWER(livro) = ?", (aluno_id, titulo_livro))
                livro = cursor.fetchone()
                if livro:
                    cursor.execute("UPDATE biblioteca SET disponibilidade = 'sim' WHERE LOWER(titulo) = ?", (titulo_livro,))
                    cursor.connection.commit()
                    cursor.execute("DELETE FROM reservas WHERE id = ? AND LOWER(livro) = ?", (aluno_id, titulo_livro))
                    cursor.connection.commit()
                    print(f"\nO livro '{livro[1]}' foi devolvido com sucesso para a biblioteca.")
                else:
                    print(f"\nO livro '{titulo_livro}' não está reservado pelo aluno {nome}.")
            except pyodbc.Error as e:
                print("Erro ao devolver livro:", e)
        else:
            print(f"\nO Aluno {nome} não possui cadastro no sistema.")
    except pyodbc.Error as e:
        print("Erro ao fazer consulta:", e)
# Etapa 5 - Adiciona um novo livro à biblioteca.
def adicionar_livro(cursor):
    titulo = input("Digite o Título do Livro: ").lower()
    autor = input("Digite o nome do Autor do Livro: ").lower()
    while True:
        disponibilidade = input("O Livro está disponível? (Sim/Não): ").lower()
        if disponibilidade in ["sim", "não"]:
            break
        else:
            print("Por favor, insira 'Sim' ou 'Não'.")
    data = input("Digite a data de hoje (DD/MM/AAAA): ")
    try:
        cursor.execute(
            "INSERT INTO biblioteca (titulo, autor, disponibilidade, data_add) VALUES (?, ?, ?, ?)",
            (titulo, autor, disponibilidade, data)
        )
        cursor.connection.commit()
        print(f"\nO Livro '{titulo}' foi adicionado com sucesso!")
    except pyodbc.Error as e:
        print("Erro ao adicionar livro:", e)
# Etapa 6 - Remove um livro da biblioteca.
def remover_livro(cursor):
    titulo = input("Digite o Título do livro a ser removido: ").lower()
    try:
        cursor.execute("SELECT titulo FROM biblioteca WHERE LOWER(titulo) = ?", (titulo,))
        livro = cursor.fetchone()
        if livro:
            cursor.execute("DELETE FROM biblioteca WHERE LOWER(titulo) = ?", (titulo,))
            cursor.connection.commit()
            print(f"\nO livro '{livro[0]}' foi removido da biblioteca com sucesso.")
        else:
            print(f"\nO livro '{titulo}' não está cadastrado na biblioteca.")
    except pyodbc.Error as e:
        print("Erro ao remover livro:", e)
# Etapa 0 - Exibe o menu e gerencia as opções do usuário.
def menu():
    cursor = conectar_banco()
    if not cursor:
        return
    while True:
        print("\nMenu: ")
        print("1. Listar Livros")
        print("2. Verificar Disponibilidades")
        print("3. Reservar Livro")
        print("4. Devolver Livro")
        print("5. Adicionar Livro")
        print("6. Remover Livro")
        print("0. Sair")
        opcao = input("Digite o número da opção desejada: ")
        if opcao == '1':
            listar_livros(cursor)
        elif opcao == '2':
            verificar_disponibilidade(cursor)
        elif opcao == '3':
            reservar_livro(cursor)
        elif opcao == '4':
            devolucao_livro(cursor)
        elif opcao == '5':
            adicionar_livro(cursor)
        elif opcao == '6':
            remover_livro(cursor)
        elif opcao == '0':
            print("Saindo do Programa...")
            break
        else:
            print("\nOpção inválida. Tente novamente, escolha uma opção válida.")
# Inicia o programa
menu()

#References:
#https://mayurbirle.medium.com/uuids-with-python-b133cead1b4c
#https://learn.microsoft.com/pt-br/sql/connect/python/pyodbc/python-sql-driver-pyodbc?view=sql-server-ver16