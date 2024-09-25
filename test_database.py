
from new_data import search_debtors

def test_database_connection():
    try:
        clientes = search_debtors()
        if clientes:
            print("Conexão com o banco de dados e extração de dados bem-sucedida!")
            for cliente in clientes:
                print(f"Cliente: {cliente['name']}, Telefone: {cliente['number']}, Dias de Atraso: {cliente['days_late']}")
        else:
            print("Nenhum cliente inadimplente encontrado.")
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")

if __name__ == "__main__":
    test_database_connection()