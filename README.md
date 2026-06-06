# Sistema de Gestão de Jardim Zoológico (Bases de Dados)

Repositório do projeto da cadeira Bases de Dados 25/26 no Instituto Superior Técnico. Este projeto tem como objetivo modelar e implementar uma base de dados robusta para a gestão de um Jardim Zoológico, incluindo o alojamento de animais, gestão de recintos, funcionários, venda de bilhetes e controlo de acessos.

---

## Estrutura do Repositório e Tecnologias Utilizadas

### [Projeto 1: Modelação Conceptual e Relacional](./Projeto%201)
Esta pasta contém toda a fase de planeamento, desenho arquitetural e especificação das regras de negócio do sistema.
* **O que contém:**
  * **Enunciado:** Enunciado do primeiro projeto.
  * **Diagramas UML:** Ficheiros com os diagramas de classes iniciais e relações organizados por módulos (Animais, Bilhetes, Recintos, Funcionários).
  * **Modelo Final:** O diagrama estrutural integrado que unifica todas as entidades do sistema (`modelo_final.drawio`).
  * **Relatório:** Documento descritivo detalhando as restrições de integridade, dependências funcionais e decisões de normalização.
* **Tecnologias Utilizadas:**
  * **Modelação Conceptual (Modelo ER):** Utilização de conceitos de Modelação Entidade-Associação para mapear de forma clara os requisitos de negócio do Jardim Zoológico.
  * **Conversão para o Modelo Relacional:** Aplicação de regras formais de mapeamento e transformação do modelo conceptual lógico para esquemas relacionais de tabelas, definição de chaves primárias (PK), chaves estrangeiras (FK) e especificação declarativa de Restrições de Integridade (RI-restrições).
  * **Álgebra Relacional:** Formulação matemática de interrogações complexas sobre o esquema relacional, recorrendo formalmente aos operadores lógicos estruturais (Seleção $\sigma$, Projeção $\pi$, Junção $\bowtie$, Agregação $\mathcal{G}$, etc.) para extração analítica de dados.
  * **Draw.io:** Ferramenta gráfica utilizada para conceber, desenhar e exportar todos os diagramas conceptuais e lógicos do sistema.

### [Projeto 2: Implementação e API Web](./Projeto%202)
Esta pasta contém a concretização física do banco de dados relacional e a camada de software backend necessária para disponibilizar as operações ao utilizador.
* **O que contém:**
  * **Jupyter Notebook (`entrega_bd_02_12.ipynb`):** Script iterativo contendo a execução dos comandos DDL, triggers em PL/pgSQL para controlo de restrições de integridade (RI), scripts otimizados de povoamento massivo e consultas analíticas avançadas com recurso a operadores OLAP, vistas materializadas e índices B-Tree.
  * **Aplicação Web (`/app`):** Um protótipo funcional de RESTful Web Service para o processamento de vendas de múltiplos bilhetes, validação de acessos programáticos e submissão de votos em recintos.
* **Tecnologias Utilizadas:**
  * **PostgreSQL:** O Sistema de Gestão de Bases de Dados Relacionais (RDBMS) utilizado para o motor de persistência e execução de rotinas nativas.
  * **Python 3:** Linguagem base usada tanto no processamento estatístico quanto no desenvolvimento da arquitetura da aplicação.
  * **Jupyter Notebook & JupySQL:** Ferramentas interativas utilizadas para prototipagem rápida e execução em células de comandos SQL embebidos via drivers nativos.
  * **Flask:** Micro-framework Python utilizado para expor os endpoints REST que manipulam objetos JSON em conformidade com as rotas HTTP solicitadas.
  * **Psycopg 3 (`psycopg_pool`):** Driver e adaptador oficial do PostgreSQL para Python, configurado com pool de conexões (`ConnectionPool`) para gerir eficientemente acessos simultâneos e gerir transações com segurança ACID nativa contra injeção de SQL.

---

## Como Executar o Projeto?

Se deseja testar o código, ver a base de dados a funcionar ou interagir com a API, não precisa de instalar e configurar servidores manualmente no seu computador.

 **[Clique aqui para ler o Guia de Execução Passo a Passo no Projeto 2](./Projeto%202/README.md)** 
