from database import search_debtors

def test_database_connection():
    try:
        clientes = search_debtors()
        total_clientes = len(clientes)
        
        if total_clientes > 0:
            print("Conexão com o banco de dados e extração de dados bem-sucedida!")
            count_valid_clients = 0
            
            for cliente in clientes:
                print(f"Cliente: {cliente['name']}, Telefone: {cliente['number']}, "
                      f"Dias de Atraso: {cliente['days_late']}, Data de Vencimento: {cliente['due_date']}, email: {cliente['email']}")
                count_valid_clients += 1

            print(f"\nTotal de clientes com débitos entre 3 e 60 dias de atraso: {count_valid_clients}")
        else:
            print("Nenhum cliente inadimplente encontrado.")
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")

if __name__ == "__main__":
    test_database_connection()