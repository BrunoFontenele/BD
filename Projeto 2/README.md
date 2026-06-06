# Guia Completo de Execução do Projeto (A Partir do Zero)

Este guia foi desenhado para quem **não tem qualquer ferramenta instalada no computador**. Se o seu PC está "limpo", basta seguir estes passos um a um para ter o projeto de Bases de Dados (PostgreSQL, Python, Jupyter e API Web) a funcionar na perfeição.

---

## Passo 1: Instalar as Ferramentas Necessárias

Antes de aceder ao código, o seu computador precisa de 3 programas base:

### 1.1. Instalar o Git
O Git permite-lhe descarregar (clonar) o código deste projeto diretamente para a sua máquina.
* Aceda a [https://git-scm.com/install/](https://git-scm.com/install/) e instale a versão para o seu sistema operativo. Pode deixar todas as opções padrão ("Next" até ao fim).

### 1.2. Instalar o WSL 2 (Apenas para utilizadores Windows)
O Docker precisa de um subsistema Linux para funcionar no Windows.
1. Clique no menu Iniciar do Windows, escreva `cmd`, clique com o botão direito sobre "Linha de Comandos" e escolha **"Executar como administrador"**.
2. Escreva o seguinte comando e pressione `Enter`:
   ```cmd
   wsl --install
   ```
3. Se pedir para reiniciar o computador, reinicie. (Se já tiver o WSL, pode usar `wsl --update`).

### 1.3. Instalar o Docker Desktop
O Docker é o que vai criar todo o ambiente (Base de dados, Servidor Web, etc.) sem que tenha de instalar e configurar cada um manualmente.
1. Aceda a [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/) e instale o programa.
2. Após a instalação, **abra o Docker Desktop**. É provável que tenha de aceitar os termos. Deixe o programa aberto (vai ver um ícone de uma baleia na barra de tarefas). Ele precisa de estar a correr no fundo.

---

## Passo 2: Descarregar e Iniciar o Projeto

Agora que tem as ferramentas, vamos buscar o projeto e ligá-lo.

1. Abra um terminal normal (No Windows: menu iniciar -> escreva `cmd` -> abra a "Linha de Comandos").
2. Descarregue a pasta do ambiente executando:
   ```cmd
   git clone https://github.com/bdist/bdist-workspace.git
   ```
   *(Nota: Coloque aqui o link do seu próprio repositório Github se tiver feito um fork ou um repositório próprio)*
3. Entre na pasta que acabou de descarregar:
   ```cmd
   cd bdist-workspace
   ```
4. Ligue os motores do projeto com o comando:
   ```cmd
   docker compose up
   ```
   *Atenção: A primeira vez vai demorar um pouco (pode demorar minutos), pois ele está a transferir o PostgreSQL, o Jupyter e o Python.*

---

## Passo 3: Abrir o Jupyter e a Base de Dados

1. Olhe para as letras que estão a aparecer no terminal onde executou o comando anterior. Procure por um link que se pareça com isto:
   `http://127.0.0.1:9999/lab?token=EXEMPLO12345`
2. **Copie esse link completo** e cole-o no seu navegador de internet (Chrome, Safari, Edge).
3. Acabou de entrar no ambiente Jupyter! Do lado esquerdo, clique na pasta do projeto e abra o ficheiro `entrega_bd_02_12.ipynb`.

### 3.1. Executar o Código Python e SQL
1. No ficheiro que abriu, vai ver blocos de código (células). Clique no primeiro bloco e pressione **`Shift + Enter`** no teclado para correr esse bloco. Faça isso bloco a bloco.
2. **Atenção a um passo manual:** Numa das células (a de Geração de Vendas), o código vai criar um ficheiro chamado `povoamento_vendas_otimizado.sql`.
   * No menu do Jupyter (em cima à esquerda), vá a **File > New > Terminal**.
   * No ecrã preto que se abre, escreva: `psql -h postgres -U app` e pressione Enter.
   * Quando pedir a password, escreva `app` (as letras não aparecem no ecrã por segurança) e pressione Enter.
   * Escreva `\i povoamento_vendas_otimizado.sql` e pressione Enter. Isto vai carregar os dados das vendas.
   * Quando terminar, pode voltar ao separador do ficheiro `.ipynb` e continuar a correr as restantes células com `Shift + Enter` até ao fim.

---

## Passo 4: Testar a Aplicação / API Web

O seu projeto também tem um servidor Web. Para o ligar:

1. Abra uma **nova** janela da Linha de Comandos (deixe a outra que tem o Docker a correr quieta).
2. Vá para a mesma pasta:
   ```cmd
   cd bdist-workspace
   ```
   *(Ou se a pasta app estiver fora do workspace, navegue para o local correto, seguindo a estrutura do seu projeto)*
3. Execute o servidor Web com o comando:
   ```cmd
   docker compose -f docker-compose..app.yml up
   ```
4. Agora a sua API está online! Abra o navegador e teste os seguintes endereços:
   * **Para ver os recintos da zona 1:** Vá a `http://127.0.0.1:8080/zona/1`
   * Para testar Votos e Compras (Transações), pode utilizar programas como o Postman para enviar pedidos `POST` para `http://127.0.0.1:8080/venda/`.

---

## Passo 5: Desligar Tudo

Quando terminar de explorar o projeto, deve desligar os motores do Docker para não gastar recursos do seu PC.

1. Numa janela de terminal aberta na pasta do projeto, escreva:
   ```cmd
   docker compose stop
   ```
2. Após uns segundos, tudo estará desligado com segurança.
