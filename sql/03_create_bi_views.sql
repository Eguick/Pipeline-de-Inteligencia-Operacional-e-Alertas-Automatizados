-- ==============================================================================
-- View 1: Performance Geral por Operador (O Coração do Dashboard)
-- ==============================================================================
CREATE OR ALTER VIEW dw.vw_BI_Performance_Operador AS
SELECT 
    op.Nome AS Operador,
    COUNT(f.Sk_Atendimento) AS Total_Chamadas,
    
    -- Usando a dimensão de status para calcular os indicadores
    SUM(CAST(st.Is_CPC AS INT)) AS Total_CPC,
    SUM(CAST(st.Is_Conversao AS INT)) AS Total_Promessas,
    
    -- Cálculo seguro da Taxa de Conversão (Evita erro de divisão por zero)
    CAST(
        ISNULL(
            (SUM(CAST(st.Is_Conversao AS FLOAT)) / NULLIF(SUM(CAST(st.Is_CPC AS FLOAT)), 0)) * 100
        , 0) 
    AS DECIMAL(10,2)) AS Taxa_Conversao_Perc,
    
    -- Tempo médio de atendimento em segundos
    AVG(f.Duracao_Segundos) AS TMA_Segundos
    
FROM dw.Fato_Atendimentos f
INNER JOIN dw.Dim_Operador op ON f.Sk_Operador = op.Sk_Operador
INNER JOIN dw.Dim_Status st ON f.Sk_Status = st.Sk_Status
GROUP BY op.Nome;
GO

-- ==============================================================================
-- View 2: Curva de Chamadas por Hora (Para o gráfico de linha de tendência)
-- ==============================================================================
CREATE OR ALTER VIEW dw.vw_BI_Volume_Por_Hora AS
SELECT 
    CAST(f.Data_Hora_Chamada AS DATE) AS Data_Chamada,
    DATEPART(HOUR, f.Data_Hora_Chamada) AS Hora_Dia,
    COUNT(f.Sk_Atendimento) AS Volume_Chamadas,
    SUM(CAST(st.Is_CPC AS INT)) AS Volume_CPC
FROM dw.Fato_Atendimentos f
INNER JOIN dw.Dim_Status st ON f.Sk_Status = st.Sk_Status
GROUP BY 
    CAST(f.Data_Hora_Chamada AS DATE),
    DATEPART(HOUR, f.Data_Hora_Chamada);
GO