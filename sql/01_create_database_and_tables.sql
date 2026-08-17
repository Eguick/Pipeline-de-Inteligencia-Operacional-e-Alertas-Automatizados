-- 1. Criação do Banco de Dados
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'InteligenciaOperacional')
BEGIN
    CREATE DATABASE InteligenciaOperacional;
END
GO

USE InteligenciaOperacional;
GO

-- 2. Criação dos Schemas
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'stg')
    EXEC('CREATE SCHEMA stg');
GO

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'dw')
    EXEC('CREATE SCHEMA dw');
GO

-- =======================================================================
-- CAMADA STAGING (Ingestão Bruta)
-- =======================================================================
IF OBJECT_ID('stg.Chamadas_Bruto', 'U') IS NOT NULL DROP TABLE stg.Chamadas_Bruto;
CREATE TABLE stg.Chamadas_Bruto (
    Cpf_Operador VARCHAR(50),
    Nome_Operador VARCHAR(150),
    Telefone_Discado VARCHAR(50),
    Data_Hora_Inicio VARCHAR(50),
    Tempo_Falado_Segundos VARCHAR(50),
    Status_Tabulacao VARCHAR(100)
);
GO

-- =======================================================================
-- CAMADA DATA WAREHOUSE (Modelagem Dimensional)
-- =======================================================================

-- Dimensão Operador
IF OBJECT_ID('dw.Dim_Operador', 'U') IS NOT NULL DROP TABLE dw.Dim_Operador;
CREATE TABLE dw.Dim_Operador (
    Sk_Operador INT IDENTITY(1,1) PRIMARY KEY,
    Cpf VARCHAR(11) NOT NULL UNIQUE,
    Nome VARCHAR(150) NOT NULL,
    Data_Atualizacao DATETIME DEFAULT GETDATE()
);

-- Dimensão Status (Para categorizar o que é conversão, CPC, etc)
IF OBJECT_ID('dw.Dim_Status', 'U') IS NOT NULL DROP TABLE dw.Dim_Status;
CREATE TABLE dw.Dim_Status (
    Sk_Status INT IDENTITY(1,1) PRIMARY KEY,
    Descricao VARCHAR(100) NOT NULL,
    Is_CPC BIT NOT NULL, -- Flag para facilitar o cálculo de CPC no BI
    Is_Conversao BIT NOT NULL
);

-- Tabela Fato de Atendimentos
IF OBJECT_ID('dw.Fato_Atendimentos', 'U') IS NOT NULL DROP TABLE dw.Fato_Atendimentos;
CREATE TABLE dw.Fato_Atendimentos (
    Sk_Atendimento BIGINT IDENTITY(1,1) PRIMARY KEY,
    Sk_Operador INT FOREIGN KEY REFERENCES dw.Dim_Operador(Sk_Operador),
    Sk_Status INT FOREIGN KEY REFERENCES dw.Dim_Status(Sk_Status),
    Telefone_Discado VARCHAR(15),
    Data_Hora_Chamada DATETIME NOT NULL,
    Duracao_Segundos INT,
    
    -- Índice Columnstore para performance extrema em consultas analíticas (BI)
    INDEX CIX_Fato_Atendimentos CLUSTERED COLUMNSTORE
);
GO

-- 3. Carga Inicial da Dimensão de Status
INSERT INTO dw.Dim_Status (Descricao, Is_CPC, Is_Conversao)
VALUES 
    ('Alô - Desliga', 0, 0),
    ('Caixa Postal', 0, 0),
    ('Mudo', 0, 0),
    ('Telefone Inexistente', 0, 0),
    ('CPC - Recado', 1, 0),
    ('CPC - Promessa de Pagamento', 1, 1),
    ('CPC - Negociação Concluída', 1, 1);
GO