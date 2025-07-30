# nsj-queue-lib
Biblioteca para facilitar a implementação de filas e workers, com quatro principais vantagens:

* Enfileiramento transacionado com o processo (alteração de banco) que deu origem à mensagem na fila (isso é, a inserção na fila, é garantidamente na mesma transação do trabalho que deu origem à demanda de processamento assíncrono, dispensando protocolos complexos, como o protocolo three-phase commit).
* Retirada da fila transacionada com o processo de consumo em si, para cada mensagem (vantangem complementar à anterior, garantido que algo só sai realmente da fila, quando plenamente consumido).
* Evita IO para publicação nas filas (em filas usando o protocolo AMQP, normalmente se faz uma requisição Rest no meio de um processo, gerando IO; embora isso não seja um problema por si só, pode porém se tornar um, quando é deixada uma transação de banco em aberto, enquanto se faz esse tipo de IO, por conta de uma eventual tentativa de transacionar as tratativas da fila com o processamento).
* Permitir monitoramento da fila direto pelo banco de dados (soluções de fila normalmente não permite acesso direto aos dados na fila, dificultando rotinas de monitoramento detalhadas; o que gera, muitas vezes, redundancia das informações entre a fila e o BD; nessa ferramenta, a fila fica no banco de dados, viabilizando monitoramento por ferramentas como DundasBI ou Redash).

Por conta desses requisitos, esse biblioteca de filas foi desenvolvida, mas, seu uso não é uma obrigratoriedade, pois também há contras:

* Todas as informações da fila ficam em banco de dados, que é um dos armazenamentos mais nobres (e caros) disponíveis para os sistemas web (inclusive o payload das mensagens fica no banco).
* A fila acaba por trazer mais peso de processamento para o servidor do banco de dados (visto que o mesmo figura não apenas como mero armazenador de informações, mas acaba sofrendo algum nível de pooling, com o fim de controle da fila).
  * Obs.: Diversas técnicas foram utilizadas para diminuir o impacto sobre o banco de dados, e convida-se o leitor a consulta a sessão "Técnicas para Diminuir o Processamento no SGBD".

Portanto, cada analista deve verificar seu respectivo caso de uso, para decidir que tipo de enfileiramento utilizar (escolhendo entre esta biblioteca, e outra solução que implemente o protocolo AMQP - como o RabbitMQ).

**Obs.: Essa ferramenta, por hora, só funciona com os bancos de dados Postgres, MySQL e Singlestore.**

## Como Usar a biblioteca?

A biblioteca dá suporte a três tipos básicos de worker. São eles:

* **Enfileiramento simples**
  * Fila que entrega mensagens a um worker, desenvolvido para processamento assíncrono.
* **PubSub**
  * Fila que conta com um identificador de processo, e uma tabela de assinantes dos processos.
  * A ideia é que cada mensagem enfileirada é replicada para cada assinante, de modo que os assinantes terão processamentos independentes, com status final independente, e podendo realizar lógicas plenamente distintas.
* **Webhook**
  * Caso especial de PubSub, que, no entanto, não demanda nenhuma implementação adicional de código para uso, antes é só necessário configurar (nas próprias assinaturas), a URL a ser chamada para disparo do webhook (além de outros parâmetros da chamada, como método HTTP, headers, etc).

No entanto, independente do uso desejado pelo programador, todo o trabalho é organizado numa tabela de fila, configurada por meio de variáveis de ambiente.

Mesmo assim, um programador pode implementar quantas filas quiser em seu projeto, bastando criar várias tabelas de controle, e instanciar vários workers (ou usar uma mesma tabela com diferentes valores na coluna ```processo```, para o caso de filas PubSub).

Na prática, cada worker será uma máquina virtual, ou POD, rodando no ambiente de produção, com diferentes variáveis de ambiente, e diferentes entrypoints. Mas, todo o código pode estar num único repositório (que instale a biblioteca do nsj-queue-lib, por meio do PyPi).

Obs.: Quando se utiliza o conceito da coluna ```processo```, um mesmo POD poderá fazer o trabalho de diferentes workers.

### Passos para criar um novo Worker

1. Adicionar a biblioteca `nsj-queue-lib` como dependencia de seu projeto (disponível no pypi.org).
2. Criar a estrutura de banco, que deve ser similar ao exemplo contido no arquivo ```database/dump/0001 - fila teste.sql``` (ou no arquivo ```database/0001 - fila teste SingleStore.sql```, quando se desejar usar o MySQL ou o Singlestore), bastando renomear a tabela de fila, a tabela de assinantes (caso seja usada), os índices, a trigger, a função da trigger e o nome do canal que concentrará as notificações (por intermédio da trigger).
   1. Para facilitar esse passo, foi implementado um utilitário na biblioteca, que pode ser executado por meio do comando a seguir (que imprime o modelo de banco gerado, no padrão Postgres):

```sh
python -m nsj_queue_lib.db_gen <schema> <nome_fila>
```

3. Estender alguma das classes base de worker (no caso de webhooks, não é preciso estender nenhuma classe), e implementar o código de processamento das tarefas.
   1. Pode-se usar os módulos `woker_fila_teste.py` e `worker_pub_sub_teste.py` como exemplos para esse passo.
4. Definir uma imagem com o entrypoint apontando para o worker implementado (ou para o worker de webhook), conforme exemplificado no arquivo `docker-compose.yml`.
5. Executar o worker.
   1. Ver as variáveis de ambiente necessárias na [sessão correspondente](#variáveis-de-ambiente).
6. Inserir tarefas na fila.
   1. Sugere-se utiliza o módulo `queue_client.py` para facilitar a inserção de tarefas na fila, mas, o insert direto na tabela de filas também funcionará (devendo-se respeitar o significado de cada coluna, conforme explicado em sessão à frente).

Obs.: Se for utilizar a biblioteca em modo cliente servidor (ver [seção correspondente](#modo-cliente-x-servidor) à frente), antes do passo 5, devem-se considerar os passos adicionais abaixo:

1. Definir uma imagem com o entrypoint apontando para o server conforme exemplificado no arquivo `docker-compose.yml` (seção `server`).
2. Executar o server.
   1. Ver as variáveis de ambiente necessárias na [sessão correspondente](#variáveis-de-ambiente).

### Como implementar o código do seu novo Worker

#### Workers de enfileiramento simples

Basta estender a classe `WorkerBase`, contida no arquivo `worker_base.py`, e implementar o método `execute`, com seu código customizado.

Além disso, é necessário que seu módulo seja passível de execução, chamando o método `run` da classe pai, utilizando o padrão do python, conforme linhas a seguir:

```python
if __name__ == "__main__":
    ClasseDoSeuWorker().run()
```

Sugere-se utilizar o arquivo `worker_fila_teste.py` como exemplo de implementação para seu worker personalizado. E considere a configuração do `worker`, contido no arquivo `docker-compose.yml`.

#### Worker PubSub

O funcionamento dos workers do tipo PubSub é similiar ao anterior. A diferença é que a implementação não é única, mas sim de acordo com o ID de cada assinante da fila.

Explicando melhor, cada tarefa colocada numa fila PubSub é replicada para todos os seus assinantes. E, cada assinante, pode ser destinado a um trabalho diferente (tendo um código diferente).

Um exemplo, é quando se deseja fazer uma fila para considerar atualizações sobre uma entidade, atualizando um índice local, e também chamando uma aplicação externa.

No caso do exemplo, uma das assinaturas da fila será só para atualizar o índice, e outra só para chamar a aplicação externa (de fato, uma falha num dos pontos, não deve impactar o outro ponto, nem causar processamento repetido, por exemplo).

Assim, os códigos são exclusivos de cada implementação (de cada ID de assinante).

Portanto, estenda a classe `WorkerPubSubBase`, contida no arquivo `worker_pub_sub_base.py`, e implemente cada método, com uma assinatura compatível com:

```python
@Subscriber("teste")
def execute_subscriber_teste(
    self,
    payload: dict[str, any],
    subscription: dict[str, any],
    tarefa: dict[str, any],
    bd_conn,
) -> str:
    pass
```

Note no decorator `Subscriber` contido na declaração do método acima. É este decorator que recebe o identificador da assinatura da fila, para a qual a implementação se destina.

Além disso, para cada assinatura da fila, pode-se definir um método para processamento da fila de mortos:

```python
@DeadSubscriber("teste")
def execute_dead_subscriber_teste(
    self,
    payload: dict[str, any],
    subscription: dict[str, any],
    tarefa: dict[str, any],
    bd_conn,
) -> str:
    pass
```

Note que apenas o decorator muda, e não os parâmetros do método.

Por fim, considere o arquivo `worker_pub_sub_teste.py` como exemplo desse tipo de implementação, e o `worker_pubsub`, contido no arquivo `docker-compose.yml`.

#### Worker de Webhook

Para workers destinados ao disparo de webhooks, não é necessário nenhum tipo de implementação.

Para casos assim, basta criar uma imagem de worker, cujo entrypoint aponte para o arquivo `worker_webhook.py`.

Esse módulo python já está preparado para considerar as configurações a seguir, contidas na tabela de assinantes de uma fila PubSub (lembrando que uma fila de webhook é um tipo especial de PubSub):

* url: Define a URL a ser chamada pelo no disparo do webhook.
* http_method: Define o método HTTP a ser usado na chamada (suportanto GET, POST e PUT).
* headers: Json de headers a serem incluídos na chamada.

Considere como exemplo o `worker_webhook` contido no arquivo `docker-compose.yml`.

### Como enfileirar tarefas para execução?

Foi implementada a classe `QueueClient`, no arquivo `queue_client.py`, que servirá como SDK para integração com o sistema de filas.

Essa classe, ao ser instanciada, recebe uma conexão de banco, o nome da tabela de fila desejada, e, opcionalmente, o nome da tabela de assinaturas da fila.

Assim, a classe está preparada para as seguintes manipulações (organizadas pelos nomes dos métodos):

* `insert_task`: Insere uma tarefa para enfileiramento simples.
* `list_equivalent_task`: Lista as tarefas equivalentes já contidas na fila (auxilia o não enfileiramento de tarefas repetidas).
* `insert_task_pub_sub`: Insere uma tarefa para processamento no estilo PubSub.
* `insert_task_webhook`: Insere uma taerfa para processamento no estilo Webhook.

Assim, uma vez instalada a dependência com a biblioteca `nsj-queue-lib`, em seu projeto, será simples interagir com a fila.

**Obs.: A inserção de tarefas na fila não faz nenhum tratamento de transações, logo, chame esse método em meio a sua própria transação de banco (e tanto a fila, quanto seu processamento, estarão contidos numa única transação).**

## Ambiente de Desenvolvimento

### Montando o ambiente
Siga os passos a seguir para montar o ambiente de desenvolvimento:

1. Faça uma copia do arquivo `.env.dist` com nome `.env`.
2. Ajuste a variável PYTHONPATH contida no arquivo `.env`, para apontar para a raiz do repositório clonado em sua máquina.
3. Crie um ambiente virtual do python (para isolamento dos projetos):
> python3 -m venv .venv
4. Inicie o ambiente virtual:
> source ./.venv/bin/activate
5. Instale as dependências, no ambiente virtual:
> pip install -r requirements.txt
6. Construa a imagem docker de base dos workers, e dos testes:
> docker build -t worker_teste .
7. Inicie o banco de dados de exemplo:
> docker-compose up -d postgres
8. Inicie o worker de consumo da fila:
> docker-compose up -d worker
9. Execute os testes automáticos, para garantir que esteja tudo rodando:
> docker-compose up tests

Após concluir o desenvolvimento, sugere-se parar e remover as imagens criadas (para não ficarem rodando de modo indefinido, consumindo recursos de sua máquina):
> make stop
> make remove

Obs.: Os comandos detalhados no passo a passo de construção do ambiente, podem ser executados pelo make (simplificando um pouco). Mas, foram apresentados os detalhes, para dar real noção do que é utilizado em ambiente de desenvolvimento.

### Testes automatizados

#### Testando no modelo padrão (não cliente X servidor)
Por hora, três casos de teste básicos estão implementados, a saber, contemplando o fluxo básico de filas, o fluxo pub_sub e o fluxo de webhooks.

No entanto, esses testes não podem rodar juntos, de modo que será necessária a seguinte sequência de comandos:

* Preparação

> make postgres

* Teste básico

> make tests

* Teste pub_sub

> make stop
> make tests_pubsub

* Teste webhook

> make stop
> make tests_webhook

#### Testando no modelo Cliente X Servidor

Os testes no modelo cliente servidor são equivalentes ao modelo anterior, porém, com dois passos predecessores adicionais:

1) Trocar o valor da variável de ambiente abaixo:

> CLIENT_SERVER_MODE=True

2) Iniciar o banco de dados

> make postgres

3) Rode os comandos abaixo por teste

* Teste básico

> make tests_server

* Teste pub_sub

> make stop
> make tests_pubsub_server

* Teste webhook

> make stop
> make tests_webhook_server

### Versionando o projeto

Pré-requisito:
> make install_to_pkg

Passos para construir e enviar uma nova versão ao PyPi:

1. make build_pkg
2. make upload_pkg

## Detalhes Internos de Implementação

### Organização do Repositório

Devido a simplicidade da biblioteca, foi utilizada uma divisão dos arquivos em apenas três pacotes:

* `nsj_queue_lib`: Pacote principal e mais genérico, contendo os arquivos de interesse para uso da biblioteca por terceiros.
* `nsj_queue_lib.client`: Pacote contendo os arquivos com a implementação necessárias para os workers, que, na configuração cliente servidor, atuam como lado cliente (na configuração padrão, onde não se usa o servidor e as conexões via socket, mesmo assim, esse lado é o cliente, enquanto o POSTGRES faz trabalho de servidor de banco e das notificações push).
* `nsj_queue_lib.server`: Pacote contendo os arquivos com a implementação necessárias para o lado servidor (quando ser utiliza a configuração cliente X servidor), o qual desempenha as funções de notificar os workers de novo trabalho, e controlar os locks necessários ao bom tratamento das concorrências.

Os principais arquivos a citar são:

* `nsj_queue_lib.queue_client.py`: Contém class SDK para aplicações cliente.
* `nsj_queue_lib.client.main_thread.py`: Implementação base da thread responsável pela execução real das tarefas na fila (execução genérica, ainda não customizada).
* `nsj_queue_lib.client.notify_thread.py`: Thread para notificação de tarefas agendadas.
* `nsj_queue_lib.client.purge_thread.py`: Thread para limpeza de lixo (tarefas antigas).
* `nsj_queue_lib.client.retry_thread.py`: Thread para retentativa de processos mortos.
* `nsj_queue_lib.server.server_main.py`: Thread principal do lado servidor (responsável por receber novos clients).
* `nsj_queue_lib.server.lock_service_thread.py`: Thread que figura como serviço de controle do locks (usada apenas para lock das ações auxiliares, e que podem ocorrer em momentos "aleatórios", como purge, retry, notify, etc).
* `nsj_queue_lib.server.listener_thread.py`: Thread de controle de uma tarefa em execução (instanciada e iniciada, a cada vez que se acorda um worker).
* `nsj_queue_lib.server.rpc_interpreter.py`: Classe auxiliar, responsável pela interpretação das chamadas ao servidor (atuando como um tipo de Remote Procedure Call).

### Técnicas para Diminuir o Processamento no SGBD

Algumas técnicas foram utilizadas para diminuir a carga de processamento sobre o banco:

#### Postgres Notify

O Postgres suporta nativamente um recurso de notificação, capaz de disparar mensagens para conexões registradas como ouvintes de um canal (sugere-se leitura da [documentação do banco de dados](https://www.postgresql.org/docs/current/sql-notify.html)).

Esse tipo de notificação foi usado, junto com o recuro de triggers, de modo que cada insert, numa tabela de fila, "acorda" os workers registrados, não necessitando de pooling em intervalos demasiado curtos, para localizar uma tarefa recém adicionada (e permitindo funcionamento no padrão push notification).

**Obs. 1: As notificações são transacionadas e unificadas pelo postgres (só são disparadas após o commmit, e, não são disparadas duplicatas, mesmo que haja dois notifies iguais). O que se adequou muito bem ao caso de uso do controle de filas.**

**Obs. 2: Esse mecanismo não é utilizado quando se utiliza a execução em modo cliente x servidor.**

#### Try Advisory Lock

O postgres suporta nativamente um tipo de mutex, por meio do qual uma query pode "travar" e "devolver" um número inteiro, usando-o como semáforo. Ao mesmo tempo que, se um número estiver travado, e outro processo pede pelo mesmo, esse segundo processo recebe imediatamente um False, podendo continuar seu trabalho (sem travar esperando pela liberação do semáforo).

Esse recurso foi utilizado de diversas maneiras, principalmente:

* Garantir que cada tarefa só está em processamento por um único worker
* Garantir que os processos que fazem pooling no BD, são realizados por apenas um worker por vez (processos: retentativa de processamento de mortos, purge de lixo da fila e notificação de tarefas agendadas, tratados em outra sessão).

**Obs.: Em modo cliente x servidor, é um usado um tipo de lock muito semelhante, mas, sem necessidade do postgres. Na prática, usamos um estrutura de dados em memória (e um semáforo para controlar o acesso à mesma), porém, para os workers o processo é equivalente (a diferença é que o lock é pedido por socket, e não por comando SQL por meio da conexão com o banco de dados).**

#### Sincronia de pooling no estilo Linux Crontab

Além do advisory lock, as threads que realizam pooling no BD também ficam agendadas para execução num mesmo minuto do relógio (exemplo, a thread de purge, por padrão, roda a cada hora redonda, isto é, no minuto 0 de cada hora).

Essa técnica aumenta a probabilidade dos workers tentarem o pooling de modo concorrente, e, pelo uso do advisory lock, a maioria desiste do pooling, e apenas um worker consegue realizar esse processo (diminuindo a carga inútil sobre o BD).

### Funcionamento Básico

#### Workers auto gerenciados
O gestor de filas trabalha como uma equipe de workers auto gerenciados, porém limitada ao consumo de uma única fila.

Não há um worker centralizador reponsável pela distribuição das tarefas, mas, cada worker coopera tanto para executar as tarefas, quanto para realizar as atividades administrativas, que são:

* Purge: Rotina executada de hora em hora (por padrão), responsável por excluir as tarefas contidas na fila há mais de 60 dias (intervalo padrão, passível de configuração via variável de ambiente).
* Retentativa de processos mortos: Rotina executada há cada 5 minutos, responsável por checar se há tarefas marcadas como "processando", mas que, na verdade, não tem mais lock ativo (significando que a conexão de BD - ou socket -, que originou o lock, morreu). Caso se identifique uma tarefa morta, a mesma é atualizada como "falha", e enfileirada para nova tentativa.
* Notificação de tarefas agendadas:
  * No caso de uma retentativa de tarefa, ou no caso de um tarefa ser inserida para execução futura (agendada); ou mesmo no caso em que uma tarefa já constava na fila, antes de qualquer worker estar ativo, então essa tarefa não irá gerar uma notificação que acione os workers.
    * Existe ainda o caso raro de uma notificação ser disparada no exato intervalo em que todos os workers estavam nos milésimos de segundos de intervalo, durante o qual o worker para de ouvir uma conexão, e retoma sua espera (estratégia de manipulação dos descritores de arquivo, que evita uma espera ocupada indefinida, mas que gera milésimos de segundos de "surdez").
  * Essa rotina é, por tanto, responsável por identificar esses casos, atualizar seus status para "pendente" (se necessário), e disparar a notificação que ativa os workers.

Assim, os workers sozinhos mantem a fila em funcionamento (dispensando um nó centralizador).

**Obs.: Como veremos à frente, existe um diferença sutil, porém importante, no modo cliente x servidor.**

#### Fila em uma única tabela
Por decisão de design, cada fila é contida numa única tabela. Assim, não há uma tabela de tentativas, e outra de "cabeçalho" das tentativas. Em vez disso, um única tabela guarda todas as tentativas.

* O ponto positivo dessa decisão, é a simplicidade de implementação e modelagem do BD.
* O ponto negativo, é que as queries, para identificar o status atual de cada execução, podem ser mais complexas.

Sendo assim, é importante atentar no significado de cada coluna da tabela de fila:

|       Coluna       | Descrição                                                                                                                                                                                                                                                                                                                                                                  |
| :----------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|         id         | Identificador numérico (auto incremental) de cada tentativa (tarefa).                                                                                                                                                                                                                                                                                                      |
|     id_inicial     | Identificador da primeira tentativa de uma tarefa                                                                                                                                                                                                                                                                                                                          |
| data_hora_inicial  | Data e hora da primiera tentativa de uma tarefa na fila.                                                                                                                                                                                                                                                                                                                   |
|     data_hora      | Data e hora estimada da execução da tentativa corrente.                                                                                                                                                                                                                                                                                                                    |
|       origem       | String simples, destinada ao usuário, para identificar a origem de uma tarefa (é pouco usada no controle das tarefas; só se aplica na identificação de tarefas equivalentes, na classe de SDK para os clientes da fila).                                                                                                                                                   |
|      destino       | String simples, destinada ao usuário, identificando o destino de uma tarefa.                                                                                                                                                                                                                                                                                               |
|      processo      | String idenitificando o tipo de processo sendo executado. Esse idenitifcador é útil tanto para o usuário, quanto para o controle de tarefas no estilo pub_sub, pois, o mesmo identificador é utilizado para localizar os assinantes de um processo.                                                                                                                        |
|   chave_externa    | String para identificação de uma tarefa, conforme sistema externo (por exemplo, o número de um pedido a ser faturado).                                                                                                                                                                                                                                                     |
| proxima_tentativa  | Data e hora estimada da próxima tentativa (coluna só preenchida em caso de falha, quando uma nova tentativa é inserida; é importante notar que o valor dessa coluna será igual ao da coluna data_hora da próxima tentativa). Obs.: A data e hora da próxima tentativa é calculada como: ```número de tentativas * intervalo entre tentativas```- ver variáeis de ambiente. |
|     tentativa      | Número da tentativa (contador). Há uma variável de ambiente para definir o número máximo de tentativas.                                                                                                                                                                                                                                                                    |
|       status       | Status da tentativa, podendo ser: ```agendada, pendente, falha, sucesso```                                                                                                                                                                                                                                                                                                 |
|   reenfileirado    | Flag auxiliar indicando que uma tentativa já foi reenfileirada (uso interno).                                                                                                                                                                                                                                                                                              |
| estouro_tentativas | Flag auxiliar indicando que já houve estouro do número de tentativas.                                                                                                                                                                                                                                                                                                      |
|      mensagem      | Mensagem preenchida após processamento da tentativa (podendo indicar falha, ou sucesso).                                                                                                                                                                                                                                                                                   |
|    id_anterior     | ID da tentativa anterior.                                                                                                                                                                                                                                                                                                                                                  |
| data_hora_anterior | Data e hora da tentativa anterior.                                                                                                                                                                                                                                                                                                                                         |
|  status_anterior   | Status da tentativa anterior.                                                                                                                                                                                                                                                                                                                                              |
| mensagem_anterior  | Mensagem da tentativa anterior.                                                                                                                                                                                                                                                                                                                                            |
|      payload       | Payload da mensagem enfileirada, usada como entrada para o processamento da tarefa. **Importa destacar que, no banco de dados, apenas a primiera tentativa terá seu payload preenchido, para economizar espaço em disco.***                                                                                                                                                |
|       tenant       | Tenant da tarefa (opcional).                                                                                                                                                                                                                                                                                                                                               |
| grupo_empresarial  | Grpuo empresarial da tarefa (opcional).                                                                                                                                                                                                                                                                                                                                    |
|    payload_hash    | Hash do payload da tarefa (útil para identificar tarefas equivalentes).                                                                                                                                                                                                                                                                                                    |
|      pub_sub       | Flag, de uso interno, indicando que essa tarefa é uma entrada do funcionamento pub_sub, e que, portanto, será replicada para cada assinante do processo (ou  mesmo descartada, em caso de não haver assinantes).                                                                                                                                                           |
|   publication_id   | ID da tarefa pub_sub, que foi replicada para os assinantes (quando a entrada na tavbela representa uma das replicações).                                                                                                                                                                                                                                                   |
|   subscriber_id    | ID, da tabela Subscriber, apontando para a assinatura pub_sub que deu origem à tarefa corrente.                                                                                                                                                                                                                                                                            |
|        dead        | Flag de controle indicando que essa tarefa entro no estado da fila de mortos (por exceder o número de tentativas).                                                                                                                                                                                                                                                         |
|      live_id       | ID da tarefa inicial, que deu origem à todo o processo, antes de se chagar à fila de mortos.                                                                                                                                                                                                                                                                               |
|     prioridade     | Inteiro (valor padrão "50") que indica a prioridade dessa tarefa. A saber, na recuperação do banco, das tarefas a serem executadas, a ordenação é de acordo com essa coluna, e com a coluna "data_hora" (de modo que as tarefas são recuperadas por prioridade e antiguidadade).                                                                                           |


#### PubSub

Para o funcionamento no estilo PubSub, tanto as tarefas de publicação, quanto as tarefas de execução, são todas contidas na mesma tabela da fila.

Portanto, é preciso ter especial cuidado no significado (já apresentado acima) de cada coluna, para um eventual monitoramento do status atual da fila.

Além disso, para que uma publicação realmente vá a efeito, é preciso haver ao menos um assinante para um determinado processo. A saber, os assinantes são para cada processo, e, adicionalmente, podem também ser para um tenant e grupo_empresarial específico (o que é opcional).

Portanto, considere também o formato da tabela de assinantes:

|      Coluna       | Descrição                                                                                                      |
| :---------------: | -------------------------------------------------------------------------------------------------------------- |
|        id         | String de identificação do assinante (útil para distinguir entre os códigos de processamento em filas PubSub). |
|      tenant       | Tenant do assinante (opcional).                                                                                |
| grupo_empresarial | Grpuo empresarial do assinante (opcional).                                                                     |
|     processo      | Código do processo assinado.                                                                                   |
|        url        | URL a ser chamada (opcional e útil para tarefas do tipo webhook).                                              |
|    http_method    | Método HTTP a ser usado na chamada (opcional e útil para tarefas do tipo webhook).                             |
|      headers      | Headers HTTP a serem adicionados na chamada (opcional e útil para tarefas do tipo webhook).                    |
|       ativo       | Flag indicando se a assinatura será mesmo considerada.                                                         |
|    created_at     | Data e hora da criaçaõ do registro.                                                                            |

#### Fila de mortos

Após estourada a quantidade máxima de tentativas de processamento de uma tarefa (seja ela de que tipo for), a tarefa é reefileirada não como uma tentativa nova, mas sim como um novo processo, com mesmo payload, porém marcado com a flag `dead=true` no banco de dados.

Essa execução em modo _dead_ é, por si só, uma nova execução enfileirada, tendo o mesmo máximo de tentativas, e respeitando o mesmo conjunto de status. **Mas, com código de execução distinto (ver método `execute_dead` da classe `WorkerBase`).**

Logo, o status `sucesso`, por exemplo, não deve ser interpretado como se a tarefa tivesse sido concluída conforme seu processamento padrão, mas, sim como uma afirmação de que, embora a tarefa deu erro e estourou o máximo de tentativas, mesmo assim o tratamento da fila de mortos foi aplicado nessa tarefa com sucesso.

Como a execução da tarefa morta é como um novo enfileiramento (do zero), a identificação da tarefa original correspondente (ainda na fila de vivos), fica à cargo da coluna `live_id`, da tabela da fila.

**Obs.: Note que é preciso ter cuidado com a coluna `dead` na implementação de queries de monitoramento da fila.**

#### Modo Cliente X Servidor

A partir da versão 1.0.0 dessa biblioteca, foi adicionado o modo Cliente X Servidor.

Esse modo consiste numa melhoria que permite dispensar o Postgres como Servidor das funcionalidades: _Try Lock Advisory_ e _Notify_. Viabilizando que os workers sejam usados em SGBDs que não disponham desses recursos (inicialmente MySQL e Singlestore).

No entanto, para dispensar o Postgres foi necessário implementar um aplicativo capaz de prover os mesmos serviços, mas aceitando conexões via socket. E, por isso (conforme se pode ver na estrutura de diretórios) foi criado um pacote chamado `server` junto a toda uma lógica de comunicação via rede.

De modo geral, não foram realizadas grandes mudanças na lógica de funcionamento dos workers, nem nas estratégias de execução da biblioteca. Apenas os serviços _Try Lock Advisory_ e _Notify_ que passam a ser providos de outra maneira.

Em resumo, quando habilitado o modo cliente X servidor, por meio da variável de ambiente `CLIENT_SERVER_MODE`, as seguintes alterações de funcionamento ocorrem nos workers:

* Os workers passam a se conectar, via socket, no servidor localizado no host definido na variável `SERVER_HOST` e na porta `NOTIFY_SERVICE_PORT`.
* Há também uma conexão, a cada 5 minutos, na porta `LOCK_SERVICE_PORT`, no mesmo host (para suportar as tarefas administrativas dos workers).
  * O serviço mais demandado nessas conexões, se destina a solicitação de locks.
* Os workers, no entanto, continuam dependendo de um banco de dados, visto que a fila em si continua na mesma estrutura de tabelas.

Quanto ao servidor, pode-se considerar a lógica de funcionamento, conforme seção abaixo.

##### Funcionamento do Servidor

A aplicação servidora conta com 4 principais threads, que controlam todo seu funcionamento:

###### server_main.py (thread principal)
Fica sempre aguardando uma nova conexão de worker, para guardar as referências do mesmo numa estrutura de dados.

* A primeira comunicação com um worker será para notificar uma tarefa (conforme explicado na thread `check_tasks_thread.py`, a seguir), logo, após conexão, é o worker que fica ouvindo o socket (e não o servidor, que seria o mais comum).
  * O efeito negativo dessa decisão, é que não sabemos, de imediato, quando um worker (parado) cai. Mas, isso não causa prejuízos, por conta do que será explicado na observação da thread `check_tasks_thread.py`.
  * Obs.: Porém, sempre sabemos de imediato quando um worker ativo cai.

###### lock_service_thread.py
Thread que fica sempre aguardando conexões de curta duração, para fornecer locks. Esses locks não são de controle das tarefas, mas sim aqueles necessários às rotinas administrativas dos workers (purge, retry, etc).

* Assim, ainda é possível garantir que apenas um worker faz uma rotina administrativa por vez.
* Obs.: É interessante notar que aqui também se utilizou o pacote "select" do python, para simplificar o controle das conexões (evitando abrir novas threads por conexão), e evitando uma espera ocupada.

###### check_tasks_thread.py
Thread que faz pooling no banco de dados, num intervalo definido pela variável de ambiente `CHECK_TASKS_INTERVAL`(com valor default 15 segundos), para verificar se há novas tarefas a executar.

* Essa é a principal diferença prática frente ao modelo com o Postgres (fazendo o papel de servidor), pois, já que não se pode contar com o `pg_notify` é preciso fazer pooling (de modo que o funcionamento não é exatamente igual ao de push notifications, mas, é muito próximo disso).
* Toda vez que uma há uma tarefa para executar, todos os workers são acordados (é enviado um notify via socket), exatamente como acontecia no caso do postgres. Mas, assim como no postgres (por conta do lock do número das tarefas), apenas um worker pega uma tarefa por vez.
* Obs.: Como não ouvimos os workers ativamente (pois, enquanto parado é ele quem aguarda o notify do server), caso se perceba que um dos workers não está mais disponível (ao se tentar enviar o notify), então o mesmo é removido da lista de workers disponíveis.

###### listener_thread.py
Essa thread não está rodando desde o início, mas, todas as vezes que um worker é acordado, é criada uma thread desse tipo para acompanhar sua execução.

Em resumo, essa thread servirá de ouvinte para as solicitações de um worker durante a execução de uma tarefa (em geral, serve apenas para travar e destravar locks).

* É importante destacar que, se a conexão cair, todos os locks desse worker são imediatamente liberados (a semelhança do que ocorre com o lock do postgres).
* Também é importante notar que, por questões de simplicidade, a lógica de retentativa de tarefas mortas (onde o worker morreu durante o processamento, e que, portanto, ficam com status `processando` no BD) não foi alterada. E, as novas tentativas dependerão da thread administrativa `retry_thread.py` (que roda de tempos em tempos, em algum dos workers).

#### Enfileiramento Multi-Banco

A partir da versão 1.2.0, o queue-lib passou a ter suporte ao enfileiramente multi-banco.

Na prática, isso significa que, de acordo com o tenant da tarefa enfileirada, e de acordo com algumas variáveis de ambiente de configuração (apresentadas mais abaixo), antes da execução de uma tarefa, o worker abrirá uma conexão para o BD correspondente, e passará essa conexão para seu código customizado.

Assim, a assinatura dos métodos de execução das tarefas passam a contar com um parâmetro adicional `multi_db_conn`, conforme sintaxe abaixo:

```python
def execute(self, payload: str, tarefa: dict[str, any], bd_conn, multi_db_conn) -> str:
  pass
```

OU

```python
def execute_dead(self, payload: str, tarefa: dict[str, any], bd_conn, multi_db_conn) -> str:
  pass
```

O MESMO VALE PARA WORKERS PUB_SUB:

```python
def execute_subscriber_teste(
      self,
      payload: dict[str, any],
      subscription: dict[str, any],
      tarefa: dict[str, any],
      bd_conn,
      multi_db_conn,
  ) -> str:
  pass
```

E, portanto, você pode centralizar uma fila, para vários clientes/tenants, a qual, porém, na execução real das tarefas, irá conectar no banco de dados do próprio cliente, permitindo que as alterações sejam realizadas direto nos dados do ERP.

##### Variáveis exclusivas dos workers multi-banco

Para suporte a execução multi-banco, foram criadas as seguintes variáveis:

|                        Variável                         | Descrição                                                                                                         | Valor Padrão                                                                 |
| :-----------------------------------------------------: | ----------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
|                MULTI_DATABASE (opcional)                | Se true, indica que o worker funcionará em modo multi-banco (Abrindo conexão de acordo com o tenant das tarefas). | False                                                                        |
|   MULTI_DATABASE_USER (opcional, se não multi-banco)    | Conta Nasajon utilizada na recuperação das credenciais do BD do ERP.                                              | None                                                                         |
| MULTI_DATABASE_PASSWORD (opcional, se não multi-banco)  | Senha da conta Nasajon utilizada na recuperação das credenciais do BD do ERP.                                     | None                                                                         |
|   MULTI_DATABASE_USER (opcional, se não multi-banco)    | Conta Nasajon utilizada na recuperação das credenciais do BD do ERP.                                              | None                                                                         |
| MULTI_DATABASE_CLIENT_ID (opcional, se não multi-banco) | client_id utilizado na recuperação dos tokens da conta Nasajon.                                                   | None                                                                         |
|      MULTI_DATABASE_API_CREDETIALS_URL (opcional)       | URL da rota de recuperação de das credenciais do BD do ERP.                                                       | https://api.sre.nasajon.com.br/erp/credentials                               |
|               OAUTH_TOKEN_URL (opcional)                | URL da rota de recuperação de novos access_tokens (OAuth + Keycloak).                                             | https://auth.nasajon.com.br/auth/realms/master/protocol/openid-connect/token |


### Variáveis de Ambiente

Seguem as principais variáveis de ambiente a serem consideradas na implementação de uma fila (obrigatórias em seu projeto):

|             Variável              | Descrição                                                                                                                          |
| :-------------------------------: | ---------------------------------------------------------------------------------------------------------------------------------- |
|     DB_HOST ou DATABASE_HOST      | IP ou nome do host de banco de dados.                                                                                              |
|     DB_PORT ou DATABASE_PORT      | Porta do banco de dados.                                                                                                           |
|     DB_BASE ou DATABASE_NAME      | Nome da base de dados.                                                                                                             |
|     DB_USER ou DATABASE_USER      | Usuário para acesso ao banco de dados.                                                                                             |
|     DB_PASS ou DATABASE_PASS      | Seenha para acesso ao banco de dados.                                                                                              |
|            QUEUE_NAME             | Nome da fila (não precisa ser igual ao nome da tabela, mas, pode ser; na prática representa o canal sobre o qual rodará o notify). |
|            QUEUE_TABLE            | Nome da tabela da fila no banco de dados.                                                                                          |
| QUEUE_SUBSCRIBER_TABLE (opcional) | Nome da tabela de assinaturas, para filas PubSub no banco de dados.                                                                |

Seguem, agora, as variáveis opcionais, que permitem customização mais avançada sobre o controle das filas:

|          Variável          | Descrição                                                                                                                                                         | Padrão                                              |
| :------------------------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
|         LOG_DEBUG          | Flag para indicar se os logs de debug serão impressos ou não.                                                                                                     | False                                               |
|      QUEUE_MAX_RETRY       | Máximo de tentativas de uma tarefa na fila.                                                                                                                       | 100                                                 |
| QUEUE_BASE_INTERVAL_RETRY  | Intervalo base das retentativas (a ser multiplicado pelo número de tentativas, no caso de reagendamento).                                                         | 5 (minutos)                                         |
| QUEUE_MINUTE_RETRY_THREAD  | Minutos nos quais a thread será executada.                                                                                                                        | 0,5,10,15,20,25,30,35,40,45,50,55                   |
| QUEUE_MINUTE_PURGE_THREAD  | Minutos nos quais a thread será executada.                                                                                                                        | 0                                                   |
| QUEUE_MINUTE_NOTIFY_THREAD | Minutos nos quais a thread será executada.                                                                                                                        | 0,5,10,15,20,25,30,35,40,45,50,55                   |
|    QUEUE_PURGE_MAX_AGE     | Idade máxima (em dias) de um registro na fila (depois é excluído).                                                                                                | 60                                                  |
|     QUEUE_PURGE_LIMIT      | Tamanho do bloco de exclusão utilizado pela thread de purge (o padrão é exlcuir de 1000 em 1000 registros).                                                       | 1000                                                |
| QUEUE_WAIT_NOTIFY_INTERVAL | Intervalo máximo que uma tarefa pode ficar pendente no BD, sem ser pega por um worker, e sem sofrer novo notify (para evitar notifies perdidos por conscidência). | 30 (segundos)                                       |
|  DEFAULT_WEBHOOK_TIMEOUT   | Timeout das chamadas de webhook (para as URLs configuradas nas assinaturas).                                                                                      | 20 (segundos)                                       |
|            ENV             | Ambiente utilizado para separação dos logs no grafana.                                                                                                            | DEV                                                 |
|        GRAFANA_URL         |                                                                                                                                                                   | Nulo (isto é, sem integração de logs com o Grafana) |

#### Variáveis específicas quando se usa a solução Cliente X Servidor

##### Lado cliente (worker)
|           Variável            | Descrição                                                                                                      | Valor Padrão |
| :---------------------------: | -------------------------------------------------------------------------------------------------------------- | ------------ |
| CLIENT_SERVER_MODE (opcional) | Se true, indica que os workers esperam se conectar no servidor dedicado, via socket.                           | False        |
|    SERVER_HOST (opcional)     | Endereço de host do servidor, para conexão via socket (deve ser o IP da máquina servidor, ou POD de controle). | 127.0.0.1    |

##### Lado servidor
|                  Variável                  | Descrição                                                                                                                                               | Valor Padrão |
| :----------------------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
|       MAX_CLIENT_THREADS (opcional)        | Quantidade máxima de clientes que o servidor aceita receber.                                                                                            | 50           |
|      CHECK_TASKS_INTERVAL (opcional)       | Intervalo, em segundos, para pooling do servidor no BD, buscando por novas tarefas.                                                                     | 15           |
| LOCK_SERVICE_WAIT_CONN_INTERVAL (opcional) | Interface, em segundos, que o serviço de Lock aguarda um novo cliente, antes de desisistir, e tentar novamente (estratégia para evitar espera ocupada). | 30           |

##### Ambos os lados
|             Variável              | Descrição                                                                                                                           | Valor Padrão |
| :-------------------------------: | ----------------------------------------------------------------------------------------------------------------------------------- | ------------ |
|  NOTIFY_SERVICE_PORT (opcional)   | Porta do serviço principal do servidor (por onde se recebem as notificações de novas tarefas), para conexão via socket.             | 8770         |
|   LOCK_SERVICE_PORT (opcional)    | Porta do serviço de lock do servidor (por onde se controla o lock exclusivo das tarefas sendo consumidas), para conexão via socket. | 8970         |
| TIMEOUT_SOCKET_MESSAGE (opcional) | Intervalo, em segundos, para timeout de qualquer mensagem trocada entre cliente e servidor (não importanto a direção).              | 5            |

