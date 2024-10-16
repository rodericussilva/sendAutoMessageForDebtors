# Sistema de Automação de Cobrança via WhatsApp

Este projeto tem como objetivo automatizar o processo de cobrança de clientes inadimplentes utilizando Python, Selenium, integração com o banco de dados MySQL, e uma interface gráfica para controle de operações e reagendamentos. A solução busca consolidar os boletos em aberto, enviar notificações personalizadas via WhatsApp, e facilitar a gestão de clientes através de uma interface amigável.

## Objetivo Geral

Automatizar o processo de cobrança de clientes inadimplentes, garantindo eficiência e precisão, com foco em:
- Extração de dados dos clientes inadimplentes diretamente do banco de dados.
- Envio de mensagens automáticas via WhatsApp Web.
- Notificação por e-mail em casos de falhas.
- Reagendamento de cobranças sem necessidade de criar novas tabelas no banco de dados.

## Componentes e Funcionalidades Implementadas

1. **Extração de Dados**:
   - Conexão com o banco de dados Infarma usando `pyodbc` para extrair os dados dos clientes inadimplentes.

2. **Envio de Mensagens Automáticas via WhatsApp**:
   - Uso do **Selenium** para automatizar o envio de mensagens personalizadas para clientes com atrasos.

3. **Notificação em Caso de Número Não Ser WhatsApp**:
   - Se o número não for WhatsApp, o script envia um alerta por e-mail para o cliente e para que o funcionário entre em contato com o cliente e atualize o cadastro.

4. **Reagendamento de Pagamento**:
   - Implementação de reagendamento sem a criação de nova tabela, utilizando um arquivo JSON para armazenar temporariamente os reagendamentos.
   - O script verifica se o cliente está reagendado e pula o cliente até que a nova data de vencimento seja alcançada.

5. **Interface Gráfica com Tkinter**:
   - Criação de uma interface gráfica que permite ao usuário iniciar/parar o script de cobrança e realizar reagendamentos de forma intuitiva.

## Fluxo de Operação

1. **Início**: O sistema verifica se há clientes inadimplentes e se conecta ao banco de dados.
2. **Envio de Mensagens**: Para cada cliente, verifica se há reagendamentos. Se houver, e a nova data não tiver sido alcançada, o cliente é ignorado.
3. **Controle de Reagendamentos**: A interface gráfica permite ao usuário adicionar ou atualizar reagendamentos sem necessidade de modificar o código.
4. **Agrupamento de Boletos**: Consolidando boletos de um mesmo cliente, enviando uma única mensagem com a soma de todos os boletos em aberto.

## Estrutura do Projeto

```bash
projeto_cobranca/
├── main.py                  # Script principal que coordena a execução do fluxo de cobranças
├── database.py              # Conexão com o banco de dados e consultas SQL
├── whatsapp.py              # Envio de mensagens via WhatsApp utilizando Selenium
├── notifications.py         # Envio de alertas ou e-mails
├── rescheduling.py          # Gerenciamento de reagendamentos usando arquivo JSON
├── interface.py             # Interface gráfica para controle do sistema
├── log_success.txt          # Log de mensagens enviadas com sucesso
├── log_failure.txt          # Log de falhas de envio
├── .env                     # Variáveis de ambiente para configurações do sistema
├── rescheduling.json        # Arquivo para armazenar os reagendamentos temporários
├── requirements.txt         # Lista de dependências do projeto
└── README.md                # Documentação do projeto
```

## Requisitos
- Python 3.10
- SQL Server
- Google Chrome (para uso com WhatsApp Web)
- ChromeDriver
- Bibliotecas Python (detalhadas abaixo)

## Instalação
1. Clone o repositório:
```
git clone https://github.com/rodericussilva/sendAutoMessageForDebtors.git
cd sendAutoMessageForDebtors
```
2. Crie um ambiente virtual e instale as dependências:
```
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```
3. Crie um arquivo .env com as configurações do seu banco de dados e email:
```
DB_SERVER=seu_servidor
DB_DATABASE=sua_base_de_dados
DB_UID=seu_usuario
DB_PWD=sua_senha
SMTP_SERVER=smtp.seuemail.com
SMTP_PORT=587
EMAIL_LOGIN=seu_email
EMAIL_PASSWORD=sua_senha_de_email
FINANCIAL_EMAIL=email_do_financeiro
```
4. Verifique se o ChromeDriver está instalado e compatível com sua versão do Google Chrome. Ele será baixado automaticamente por webdriver_manager.
## Uso
### Executar o Sistema de Cobrança
Para iniciar o sistema, execute o seguinte comando:
```
python interface.py

```
Isso abrirá a interface gráfica, onde você pode iniciar o envio de mensagens, reagendar clientes e visualizar os reagendamentos.
## Bibliotecas Utilizadas
### Conexão com Banco de Dados (SQL Server)
- `pyodbc:`  Conexão com o SQL Server usando ODBC.
```
pip install pyodbc

```
### Automação com Selenium
- `selenium:` Automação de navegadores para enviar mensagens via WhatsApp.
 ```
pip install selenium

```
- `webdriver-manager:` Gerenciamento automático do ChromeDriver.
  
  ```
  pip install webdriver-manager
  
  ```
### Envio de E-mails
- `smtplib:` Biblioteca padrão para envio de emails (já incluída no Python).
### Interface Gráfica
- `tkinter:` Biblioteca padrão do Python para criação de interfaces gráficas.
- `customtkinter:` Interface gráfica mais moderna e customizável.
  
  ```
  pip install customtkinter
  
  ```
### Manipulação de Arquivos e JSON
- `json`, `os:` Bibliotecas padrão para manipulação de arquivos e diretórios.
### Manipulação de Datas
- `´datetime:` Biblioteca padrão para manipulação de datas e horas.
## Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.
## Licença
Este projeto está licenciado sob a MIT License.
```

Este `README.md` está formatado corretamente e pode ser copiado diretamente para um repositório no GitHub, fornecendo toda a documentação necessária para o uso e desenvolvimento do projeto.

```
