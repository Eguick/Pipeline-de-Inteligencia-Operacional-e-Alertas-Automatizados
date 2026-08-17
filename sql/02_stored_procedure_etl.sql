-- ==============================================================================
-- Alterando a Procedure para corrigir a conversão de Data
-- ==============================================================================
CREATE OR ALTER PROCEDURE dw.sp_Carga_Fato_Atendimentos
AS
BEGIN
    SET NOCOUNT ON; 

    BEGIN TRY
        BEGIN TRANSACTION;

        PRINT 'Atualizando Dimensão de Operadores...';
        INSERT INTO dw.Dim_Operador (Cpf, Nome)
        SELECT DISTINCT s.Cpf_Operador, s.Nome_Operador
        FROM stg.Chamadas_Bruto s
        WHERE NOT EXISTS (
            SELECT 1 FROM dw.Dim_Operador d WHERE d.Cpf = s.Cpf_Operador
        );

        PRINT 'Carregando Fato de Atendimentos...';
        INSERT INTO dw.Fato_Atendimentos (
            Sk_Operador, 
            Sk_Status, 
            Telefone_Discado, 
            Data_Hora_Chamada, 
            Duracao_Segundos
        )
        SELECT 
            op.Sk_Operador,
            st.Sk_Status,
            s.Telefone_Discado,
            -- CORREÇÃO: Usando CONVERT com estilo 120 (yyyy-mm-dd hh:mi:ss)
            CONVERT(DATETIME, s.Data_Hora_Inicio, 120),
            CAST(s.Tempo_Falado_Segundos AS INT)
        FROM stg.Chamadas_Bruto s
        INNER JOIN dw.Dim_Operador op ON s.Cpf_Operador = op.Cpf
        INNER JOIN dw.Dim_Status st ON s.Status_Tabulacao = st.Descricao;

        COMMIT TRANSACTION;
        PRINT 'Processo de ETL concluído com SUCESSO!';

    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH
END;
GO

-- ==============================================================================
-- Executando a Procedure atualizada
-- ==============================================================================
EXEC dw.sp_Carga_Fato_Atendimentos;
GO