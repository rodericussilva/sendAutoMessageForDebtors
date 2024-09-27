from new_data import search_debtors

def test_database_connection():
    try:
        clientes = search_debtors()
        total_clientes = len(clientes)  # Contando o total de clientes retornados
        if total_clientes > 0:
            print("Conexão com o banco de dados e extração de dados bem-sucedida!")
            for cliente in clientes:
                # Adicionando a data de vencimento ao print
                print(f"Cliente: {cliente['name']}, Telefone: {cliente['number']}, "
                      f"Dias de Atraso: {cliente['days_late']}, Data de Vencimento: {cliente['due_date']}")
            # Exibindo o total de clientes
            print(f"\nTotal de clientes inadimplentes: {total_clientes}")
        else:
            print("Nenhum cliente inadimplente encontrado.")
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")

if __name__ == "__main__":
    test_database_connection()