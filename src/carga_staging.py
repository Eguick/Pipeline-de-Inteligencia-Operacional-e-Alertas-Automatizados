import pyodbc
import random
from datetime import datetime

conn_str = (r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;"
            r"DATABASE=InteligenciaOperacional;Trusted_Connection=yes;TrustServerCertificate=yes;")

def simular_carga(tipo_cenario):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    if tipo_cenario == 'normal':
        qtd = random.randint(150, 300)
    elif tipo_cenario == 'pico':
        qtd = random.randint(800, 1500)
    elif tipo_cenario == 'baixa':
        qtd = random.randint(5, 15) # volume muito baixo para causar queda
    elif tipo_cenario == 'parada':
        qtd = 0
        print("⛔ Simulando parada (nenhum registro novo inserido)...")
        conn.close()
        return
    else:
        print("⚠️ Comando inválido!")
        conn.close()
        return

    dados = []
    for _ in range(qtd):
        dados.append((datetime.now(), random.randint(1, 5), random.randint(30, 300)))

    if qtd > 0:
        cursor.executemany("""
            INSERT INTO dw.Fato_Atendimentos (Data_Hora_Chamada, Sk_Status, Duracao_Segundos)
            VALUES (?, ?, ?)
        """, dados)
        conn.commit()
        print(f"✅ Inseridos {qtd} novos registros com cenário '{tipo_cenario.upper()}' na base.")
    
    conn.close()

if __name__ == "__main__":
    print("--- SIMULADOR INTERATIVO DE CARGA ---")
    print("Comandos: [normal] | [pico] | [baixa] | [parada] | [sair]")
    print("-" * 50)
    
    while True:
        comando = input("\nDigite o cenário desejado: ").strip().lower()
        
        if comando == 'sair':
            break
        elif comando in ['normal', 'pico', 'baixa', 'parada']:
            simular_carga(comando)
        else:
            print("❌ Comando não reconhecido.")