# 🚀 Pipeline de Inteligência Operacional e Alertas Automatizados

Projeto "End-to-End" focado em Engenharia de Dados e Backend, desenhado para transformar dados operacionais brutos em métricas de decisão em tempo real.

## 🏗️ Arquitetura do Banco de Dados
O banco utiliza um **Star Schema** otimizado para performance analítica.
<img width="3029" height="2771" alt="Fato Atendimentos Data Model-2026-08-17-024330" src="https://github.com/user-attachments/assets/cfa2e810-d3b7-4bc3-bd1d-bcd00d3f5941" />


- **Performance:** Tabela Fato com `CLUSTERED COLUMNSTORE INDEX` para consultas de BI ultra rápidas.
- **Integridade:** Stored Procedures com `TRANSACTION` e `TRY...CATCH`.
- **Inteligência:** Views que encapsulam regras de negócio complexas (TMA, Taxa de Conversão, CPC).

## 🤖 Componentes do Sistema
1. **Pipeline de Dados (Python):** Monitoramento contínuo das views via `pyodbc`.
2. **Integração (Telegram API):** Bot que envia alertas inteligentes com comparativos de performance entre ciclos.
3. **Simulador de Cenários:** Script de carga interativa para testar resiliência (Modos: Normal, Pico, Baixa, Parada).

## 🛠️ Tecnologias
- **SQL Server (T-SQL):** Modelagem e ETL.
- **Python:** Automação, integração e análise.
- **Telegram Bot API:** Entrega de indicadores e alertas.
