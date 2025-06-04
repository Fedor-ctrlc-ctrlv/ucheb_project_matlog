import sympy as sp
import pandas as pd
from itertools import product
import tkinter as tk
from tkinter import filedialog, messagebox
import re


def get_truth_table(expr, variables):
    truth_table = []
    for values in product([0, 1], repeat=len(variables)):
        assignment = {var: val for var, val in zip(variables, values)}
        truth_value = expr.subs(assignment).simplify()
        truth_value = "True" if truth_value else "False"  
        truth_table.append((assignment, truth_value))
    return truth_table


def generate_sdnf(truth_table, variables):
    sdnf_terms = []

    for assignment, value in truth_table:
        if value == "True":  
            term = []
            for var in variables:
                if assignment[var] == 1:
                    term.append(var)  
                else:
                    term.append(~var)  
            sdnf_terms.append(sp.And(*term))  

    return sdnf_terms

def format_sdnf(sdnf_terms):
    if not sdnf_terms:
        return "0"

    formatted_terms = []
    for term in sdnf_terms:
        formatted_terms.append(" & ".join([str(factor) for factor in term.args]))

    return " or ".join(formatted_terms)

def calculate_expression(expr, variables):
    truth_table = get_truth_table(expr, variables)

    df = pd.DataFrame(truth_table, columns=["Переменные", "Значение"])
    
    sdnf_terms = generate_sdnf(truth_table, variables)
    if sdnf_terms:
        final_sdnf = sp.Or(*sdnf_terms)
    else:
        final_sdnf = "0"

    formatted_sdnf = format_sdnf(sdnf_terms)  

    return df, formatted_sdnf
def save_expressions_to_file(expressions, file_path):
    with open(file_path, 'w') as f:
        for variables, expression in expressions:
            f.write(f"{','.join(variables)}\n")
            f.write(f"{expression}\n")

def load_expressions_from_file(file_path):
    expressions = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines), 2):
            variables = lines[i].strip().split(",")
            expression = lines[i + 1].strip()
            expressions.append((variables, expression))
    return expressions

def on_calculate_button_click():
    try:
        var_names = var_input.get()
        
        if not re.match(r'^[a-zA-Z0-9,]+$', var_names):
            messagebox.showwarning("Неверный ввод", "Переменные должны быть разделены запятой без пробелов или других символов.")
            return

        variables = [sp.symbols(var.strip()) for var in var_names.split(",")]

        user_input = expr_input.get()
        user_input = user_input.replace('≡', '==') 
        user_input = user_input.replace('==', 'Equivalent')  

        expr = sp.sympify(user_input)
        
        df, formatted_sdnf = calculate_expression(expr, variables)
        
        result_label.config(text=f"Сгенерированная СДНФ: {formatted_sdnf}")
        
        truth_table_text.delete(1.0, tk.END)  
        truth_table_text.insert(tk.END, df.to_string(index=False))
        
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при вычислении: {e}")

def on_save_button_click():
    expression = expr_input.get()
    variables = var_input.get()
    if not expression or not variables:
        messagebox.showwarning("Предупреждение", "Нет выражения или переменных для сохранения!")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        expressions = load_expressions_from_file(file_path) if file_path else []
        expressions.append((variables.split(','), expression))
        save_expressions_to_file(expressions, file_path)
        messagebox.showinfo("Информация", "Выражение и переменные сохранены успешно!")

def on_load_button_click():
    file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        expressions = load_expressions_from_file(file_path)
        
        expression_listbox.delete(0, tk.END)
        for idx, (vars, expr) in enumerate(expressions):
            expression_listbox.insert(tk.END, f"{','.join(vars)}: {expr}")
        
        messagebox.showinfo("Информация", "Выражения загружены успешно!")

def on_select_expression(event):
    selected = expression_listbox.curselection()
    if selected:
        selected_expr = expression_listbox.get(selected[0])
        variables, expression = selected_expr.split(": ")
        var_input.delete(0, tk.END)
        var_input.insert(tk.END, variables)
        expr_input.delete(0, tk.END)
        expr_input.insert(tk.END, expression)

def insert_symbol(symbol):
    current_text = expr_input.get()
    cursor_position = expr_input.index(tk.INSERT)  # Получаем положение курсора
    new_text = current_text[:cursor_position] + symbol + current_text[cursor_position:]  # Вставляем символ
    expr_input.delete(0, tk.END)  # Очищаем текущее текстовое поле
    expr_input.insert(0, new_text)  # Вставляем обновленный текст
    expr_input.icursor(cursor_position + len(symbol))  # Перемещаем курсор сразу после вставленного символа

def insert_variable(variable):
    current_text = var_input.get()
    cursor_position = var_input.index(tk.INSERT)  # Получаем положение курсора
    new_text = current_text[:cursor_position] + (',' if current_text else '') + variable + current_text[cursor_position:]  # Вставляем переменную
    var_input.delete(0, tk.END)  # Очищаем текущее текстовое поле
    var_input.insert(0, new_text)  # Вставляем обновленный текст
    var_input.icursor(cursor_position + len(variable) + (1 if current_text else 0))  # Перемещаем курсор

def insert_equivalent(symbol):
    current_text = expr_input.get()
    cursor_position = expr_input.index(tk.INSERT)  # Получаем положение курсора
    new_text = current_text[:cursor_position] + "Equivalent(,)" + current_text[cursor_position:]  # Вставляем "Equivalent(,)"
    expr_input.delete(0, tk.END)  # Очищаем текущее текстовое поле
    expr_input.insert(0, new_text)  # Вставляем обновленный текст
    expr_input.icursor(cursor_position + len("Equivalent(,)"))  # Перемещаем курсор
    


root = tk.Tk()
root.title("Калькулятор логических выражений")


tk.Label(root, text="Введите имена переменных через запятую (например, A,B,C):").pack()
var_input = tk.Entry(root, width=50)
var_input.pack()


tk.Label(root, text="Кнопки для ввода переменных:").pack()
var_button_frame = tk.Frame(root)
var_button_frame.pack()

for var in ['A', 'B', 'C', 'D']:
    button = tk.Button(var_button_frame, text=var, width=5, command=lambda v=var: insert_variable(v))
    button.pack(side=tk.LEFT)


tk.Label(root, text="Введите логическое выражение:").pack()
expr_input = tk.Entry(root, width=50)
expr_input.pack()


tk.Label(root, text="Кнопки для ввода логических выражений:").pack()
button_frame = tk.Frame(root)
button_frame.pack()

for symbol in ['~', '&', '|', ',', '==','A', 'B', 'C', 'D']:
    button = tk.Button(button_frame, text=symbol, width=5, command=lambda s=symbol: insert_symbol(s) if s != '==' else insert_equivalent(s))
    button.pack(side=tk.LEFT)


calculate_button = tk.Button(root, text="Рассчитать", command=on_calculate_button_click)
calculate_button.pack()


result_label = tk.Label(root, text="Сгенерированная СДНФ: ")
result_label.pack()


truth_table_text = tk.Text(root, height=10, width=50)
truth_table_text.pack()


save_button = tk.Button(root, text="Сохранить выражение", command=on_save_button_click)
save_button.pack()

load_button = tk.Button(root, text="Загрузить выражения", command=on_load_button_click)
load_button.pack()


expression_listbox = tk.Listbox(root, width=50, height=10)
expression_listbox.pack()
expression_listbox.bind("<Double-1>", on_select_expression)


root.mainloop()


