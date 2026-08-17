import time
import pyodbc
import pandas as pd
import requests

TOKEN = "1234:xxx" #seu token bot aqui
CHAT_ID = "-1234" #chat telegram ID

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Mensagem enviada com sucesso para o Telegram!")
        else:
            print(f"⚠️ Erro ao enviar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro de conexão com Telegram: {e}")

def formatar_tempo(segundos):
    minutos = segundos // 60
    seg_restantes = segundos % 60
    if minutos > 0:
        return f"{minutos} min e {seg_restantes} seg"
    return f"{seg_restantes} seg"

def formatar_milhar(valor):
    return f"{valor:,.0f}".replace(",", ".")

def monitorar():
    conn_str = (r"DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;"
                r"DATABASE=InteligenciaOperacional;Trusted_Connection=yes;TrustServerCertificate=yes;")
    
    chamadas_anterior = -1
    cpc_anterior = -1
    tma_anterior = -1
    
    diff_chamadas_anterior = None
    diff_cpc_anterior = None
    
    alerta_ativo = False
    primeira_execucao = True
    
    print("Monitoramento ATIVO. Aguardando ciclos...")
    
    while True:
        try:
            conn = pyodbc.connect(conn_str)
            query = """
                SELECT 
                    COUNT(*) as Total_Chamadas, 
                    SUM(CASE WHEN st.Is_CPC = 1 THEN 1 ELSE 0 END) as Total_CPC,
                    CAST(AVG(f.Duracao_Segundos) AS INT) as TMA_Medio
                FROM dw.Fato_Atendimentos f
                INNER JOIN dw.Dim_Status st ON f.Sk_Status = st.Sk_Status
            """
            cursor = conn.cursor()
            cursor.execute(query)
            colunas = [column[0] for column in cursor.description]
            df = pd.DataFrame.from_records(cursor.fetchall(), columns=colunas)
            conn.close()

            chamadas_atual = int(df['Total_Chamadas'].values[0])
            cpc_atual = int(df['Total_CPC'].values[0])
            tma_segundos = int(df['TMA_Medio'].values[0]) if pd.notna(df['TMA_Medio'].values[0]) else 0
            tma_formatado = formatar_tempo(tma_segundos)
            
            if primeira_execucao:
                chamadas_anterior = chamadas_atual
                cpc_anterior = cpc_atual
                tma_anterior = tma_segundos
                comparativo_texto = ""
                status_pipeline = "✅ *Status do Pipeline:* Operando normalmente via Staging e Data Warehouse local."
                primeira_execucao = False
            else:
                diff_chamadas_atual = chamadas_atual - chamadas_anterior
                diff_cpc_atual = cpc_atual - cpc_anterior
                diff_tma_atual = tma_segundos - tma_anterior
                
                if diff_chamadas_anterior is not None:
                    if diff_chamadas_anterior > 0:
                        perc_chamadas = ((diff_chamadas_atual - diff_chamadas_anterior) / diff_chamadas_anterior) * 100
                    else:
                        perc_chamadas = 100.0 if diff_chamadas_atual > 0 else 0.0
                    
                    var_chamadas = diff_chamadas_atual - diff_chamadas_anterior
                    seta_cham = "📈" if var_chamadas > 0 else "📉" if var_chamadas < 0 else "➡️"
                else:
                    perc_chamadas = (diff_chamadas_atual / chamadas_anterior) * 100 if chamadas_anterior > 0 else 0
                    seta_cham = "📈" if diff_chamadas_atual > 0 else "📉" if diff_chamadas_atual < 0 else "➡️"

                if diff_cpc_anterior is not None:
                    if diff_cpc_anterior > 0:
                        perc_cpc = ((diff_cpc_atual - diff_cpc_anterior) / diff_cpc_anterior) * 100
                    else:
                        perc_cpc = 100.0 if diff_cpc_atual > 0 else 0.0
                        
                    var_cpc = diff_cpc_atual - diff_cpc_anterior
                    seta_cpc = "📈" if var_cpc > 0 else "📉" if var_cpc < 0 else "➡️"
                else:
                    perc_cpc = (diff_cpc_atual / cpc_anterior) * 100 if cpc_anterior > 0 else 0
                    seta_cpc = "📈" if diff_cpc_atual > 0 else "📉" if diff_cpc_atual < 0 else "➡️"

                perc_tma = (diff_tma_atual / tma_anterior) * 100 if tma_anterior > 0 else 0
                seta_tma = "📈" if diff_tma_atual > 0 else "📉" if diff_tma_atual < 0 else "➡️"

                if diff_chamadas_atual == 0 and chamadas_atual > 0:
                    if not alerta_ativo:
                        enviar_telegram("⛔ *ALERTA: OPERAÇÃO PARADA!* (Nenhum novo atendimento computado)")
                        alerta_ativo = True
                    status_pipeline = "⚠️ *Status do Pipeline:* Operação travada ou sem fluxo de dados."
                else:
                    if alerta_ativo:
                        enviar_telegram("✅ *OPERAÇÃO RETOMADA!* O fluxo de chamadas voltou ao normal.")
                        alerta_ativo = False
                    status_pipeline = "✅ *Status do Pipeline:* Operando normalmente via Staging e Data Warehouse local."

                comparativo_texto = (
                    f"\n🔄 *Comparativo Detalhado (Ciclo Atual vs. Anterior):*\n"
                    f"• Total de Chamadas: `{formatar_milhar(chamadas_atual)}` ({seta_cham} {formatar_milhar(abs(diff_chamadas_atual))} | `{perc_chamadas:+.2f}%`)\n"
                    f"• Contatos Úteis (CPC): `{formatar_milhar(cpc_atual)}` ({seta_cpc} {formatar_milhar(abs(diff_cpc_atual))} | `{perc_cpc:+.2f}%`)\n"
                    f"• TMA Médio: `{tma_formatado}` ({seta_tma} `{diff_tma_atual:+d}s` | `{perc_tma:+.2f}%`)\n"
                )

            msg = (
                f"🚨 *RELATÓRIO AUTOMÁTICO - INTELIGÊNCIA OPERACIONAL* 🚨\n\n"
                f"📊 *Métricas Atuais da Operação:*\n"
                f"• Total de Chamadas: `{formatar_milhar(chamadas_atual)}`\n"
                f"• Contatos Úteis (CPC): `{formatar_milhar(cpc_atual)}`\n"
                f"• TMA Médio: `{tma_formatado}`\n"
                f"{comparativo_texto}\n"
                f"{status_pipeline}"
            )
            
            enviar_telegram(msg)
            
            chamadas_anterior = chamadas_atual
            cpc_anterior = cpc_atual
            tma_anterior = tma_segundos
            
            if not primeira_execucao and comparativo_texto != "":
                diff_chamadas_anterior = diff_chamadas_atual
                diff_cpc_anterior = diff_cpc_atual
            
        except Exception as e:
            print(f"Erro geral no loop: {e}")
            
        time.sleep(30) #30 segundos apenas para o teste dos alertas

if __name__ == "__main__":
    monitorar()