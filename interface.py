import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from datetime import datetime
from main import main
from rescheduling import load_rescheduling, save_rescheduling
from database import check_payment_status

browser = None

def start_system():
    messagebox.showinfo("Iniciar", "Sitema de envio de mensagens iniciado.")
    main()

def stop_system():
    messagebox.showinfo("Parar", "Sistema de envio de mensagens encerrado.")
    root.quit()

def reschedule_customer():
    """
    Reagenda o cliente com as informações fornecidas e salva no JSON.
    """
    name_customer = input_name.get()
    number_customer = input_number.get()
    new_date = input_date.get()

    # Validação de entradas
    if not name_customer and not number_customer:
        messagebox.showerror("Erro", "Por favor, insira o nome ou o número do cliente a ser reagendado.")
        return
    
    if not new_date:
        messagebox.showerror("Erro", "Por favor, informe a nova data de reagendamento.")
        return
    
    try:
        new_date_obj = datetime.strptime(new_date, "%d/%m/%Y")
        new_date_intern = new_date_obj.strftime("%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira uma data no formato DD/MM/AAAA")
        return
    
    rescheduling = load_rescheduling()

    # Adiciona ou atualiza reagendamento
    customer_scheduled = False

    for reschedule in rescheduling:
        if reschedule['name'] == name_customer or reschedule['number'] == number_customer:
            reschedule['new_date_reschedule'] = new_date_intern
            customer_scheduled = True
            break

    if not customer_scheduled:
        # Se não houver reagendamento existente, cria um novo
        reschedule = {
            "name": name_customer,
            "number": number_customer,
            "new_date_reschedule": new_date_intern
        }
        rescheduling.append(reschedule)

    save_rescheduling(rescheduling)
    update_reschedule_table()

    # Limpa os campos após reagendamento
    messagebox.showinfo("Reagendado", f"Cliente {name_customer or number_customer} reagendado para {new_date_obj.date()}.")
    input_name.delete(0, tk.END)
    input_number.delete(0, tk.END)
    input_date.delete(0, tk.END)

def update_reschedule_table():
    """
    Atualiza a tabela com as informações de reagendamento.
    """
    rescheduling = load_rescheduling()
    rescheduling_updated = []

    # Limpa a tabela antes de atualizá-la
    for item in table.get_children():
        table.delete(item)

    for reschedule in rescheduling:
        name = reschedule['name']
        number = reschedule['number']
        date_reschedule = datetime.strptime(reschedule['new_date_reschedule'], "%Y-%m-%d").date()

        # Verifica se o cliente pagou o boleto
        if check_payment_status(name_customer=name, number_customer=number):
            print(f"Cliente {name} pagou o boleto, removendo da lista.")
            continue  # Remove cliente que pagou o boleto

        # Apenas adiciona à tabela se a data de reagendamento não tiver passado
        if date_reschedule >= datetime.now().date():
            table.insert("", "end", values=(name, number, date_reschedule))
            rescheduling_updated.append(reschedule)
    
    # Salva as mudanças no arquivo JSON
    save_rescheduling(rescheduling_updated)

def check_expired_schedules():
    """
    Verifica e atualiza reagendamentos periodicamente.
    """
    update_reschedule_table()
    root.after(60000, check_expired_schedules)  # Verifica a cada 60 segundos

# Configuração da interface gráfica
root = tk.Tk()
root.configure(bg='#04488E')
root.title("Sistema de Cobrança Automatizado")

# Configura o logo e o layout da interface
logo_image = Image.open("images/logo.png")
logo_image = logo_image.resize((150, 130))
logo = ImageTk.PhotoImage(logo_image)

label_logo = tk.Label(root, image=logo, bg='#04488E')
label_logo.pack(pady=10)

root.geometry("690x630")

title = tk.Label(root, text="Automação de Cobrança", font=("Helvetica", 16), bg='#04488E', fg='white')
title.pack(pady=10)

button_frame = tk.Frame(root, bg='#04488E')
button_frame.pack(pady=10)

# Botões de iniciar e encerrar com bordas arredondadas e hover
start_btn = ctk.CTkButton(button_frame, text="Iniciar", command=start_system, fg_color="green", hover_color="#007f00", corner_radius=15, width=150)
start_btn.grid(row=0, column=0, padx=5)

stop_btn = ctk.CTkButton(button_frame, text="Encerrar", command=stop_system, fg_color="red", hover_color="#bf0000", corner_radius=15, width=150)
stop_btn.grid(row=0, column=1, padx=5)

# Campos de entrada para reagendamento
label_reschedule = tk.Label(root, text="Reagendar Cliente", font=("Helvetica", 14), bg='#04488E', fg='white')
label_reschedule.pack(pady=10)

label_name = tk.Label(root, text="Nome do cliente", bg='#04488E', fg='white')
label_name.pack(pady=5)
input_name = tk.Entry(root, width=30)
input_name.pack()

label_number = tk.Label(root, text="Número do cliente", bg='#04488E', fg='white')
label_number.pack(pady=5)
input_number = tk.Entry(root, width=30)
input_number.pack()

label_date = tk.Label(root, text="Nova data (DD/MM/AAAA)", bg='#04488E', fg='white')
label_date.pack(pady=5)
input_date = tk.Entry(root, width=30)
input_date.pack()

btn_frame = tk.Frame(root, bg='#04488E')
btn_frame.pack(pady=10)

btn_reschedule = ctk.CTkButton(btn_frame, text="Reagendar", command=reschedule_customer, fg_color="green", hover_color="#007f00", corner_radius=15, width=150)
btn_reschedule.pack(pady=10)

# Tabela para mostrar reagendamentos
columns = ("Nome", "Telefone", "Data de Reagendamento")
table = ttk.Treeview(root, columns=columns, show="headings")

table.heading("Nome", text="Nome")
table.heading("Telefone", text="Telefone")
table.heading("Data de Reagendamento", text="Data de Reagendamento")

table.column("Nome", width=150, anchor="center")
table.column("Telefone", width=150, anchor="center")
table.column("Data de Reagendamento", width=150, anchor="center")

# Exibe a tabela
table.pack(pady=10)

# Atualiza e verifica reagendamentos expirados
update_reschedule_table()
check_expired_schedules()

root.mainloop()
