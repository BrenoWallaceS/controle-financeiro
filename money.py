import sqlite3
from datetime import date

# Abre (ou cria, se não existir) o arquivo do banco de dados.
conn = sqlite3.connect("transacoes.db")


def criar_tabela():
    # CREATE TABLE IF NOT EXISTS: só cria a tabela se ela ainda não existir,
    # então pode rodar toda vez que o programa abrir sem problema.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- número único, gerado sozinho
            data TEXT NOT NULL,                    -- guardada como 'AAAA-MM-DD'
            tipo TEXT NOT NULL,                    -- 'entrada' ou 'saida'
            valor INTEGER NOT NULL                 -- em CENTAVOS, evita erro de float
        )
    """)
    conn.commit()  # confirma a alteração no arquivo


def inserir(tipo, valor):
    # Os "?" são espaços reservados que o sqlite3 preenche com segurança.
    # NUNCA monte o SQL concatenando texto (f-string): isso abre brecha
    # para SQL injection.
    conn.execute(
        "INSERT INTO transacoes (data, tipo, valor) VALUES (?, ?, ?)",
        (date.today().isoformat(), tipo, round(valor * 100)),
    )
    conn.commit()  # sem commit, o dado não é gravado de verdade


def total(tipo):
    # SUM faz a soma direto no banco. COALESCE troca None por 0
    # (acontece quando ainda não há nenhuma transação desse tipo).
    linha = conn.execute(
        "SELECT COALESCE(SUM(valor), 0) FROM transacoes WHERE tipo = ?",
        (tipo,),
    ).fetchone()
    return linha[0] / 100  # volta de centavos para reais


def listar():
    # Devolve as transações da mais nova para a mais antiga.
    return conn.execute(
        "SELECT id, data, tipo, valor FROM transacoes ORDER BY data DESC, id DESC"
    ).fetchall()


def menu():
    return input(
        "\nO que deseja fazer?\n"
        "1 - Entrada de dinheiro\n"
        "2 - Saída de dinheiro\n"
        "3 - Relatório\n"
        "4 - Listar transações\n"
        "0 - Sair\n"
        "Opção: "
    )


def ler_valor(texto):
    # Repete até o usuário digitar um número válido (trata o erro com try/except).
    while True:
        try:
            return float(input(texto).replace(",", "."))
        except ValueError:
            print("Valor inválido, tente de novo.")


def executar(opcao):
    match opcao:
        case "1":
            inserir("entrada", ler_valor("Valor da entrada: "))
        case "2":
            inserir("saida", ler_valor("Valor da saída: "))
        case "3":
            entradas = total("entrada")
            saidas = total("saida")
            print(f"\nEntradas: R$ {entradas:.2f}")
            print(f"Saídas:   R$ {saidas:.2f}")
            print(f"Saldo:    R$ {entradas - saidas:.2f}")
        case "4":
            for id_, data, tipo, valor in listar():
                print(f"\n{id_:>3} | {data} | {tipo:<7} | R$ {valor / 100:.2f}\n")
        case "0":
            return False
        case _:
            print("Opção inválida.")
    return True


# Programa principal
criar_tabela()
rodando = True
while rodando:
    rodando = executar(menu())

conn.close()  # fecha a conexão ao sair