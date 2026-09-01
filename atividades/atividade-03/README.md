# Especificação do Gerenciamento de Processos

**Disciplina:** Sistemas Operacionais (so-262) · **Atividade-03**
**Equipe:** Gabriel Leite Pasqualli e Diego Sales Novelli
**Base teórica:** Capítulo 2 — Processos e Threads

---

## 1. Visão Geral e Arquitetura do Simulador

O simulador é um programa em C, executado inteiramente em modo usuário, que imita por software o
gerenciamento de processos de um núcleo de SO. Nada é delegado ao sistema hospedeiro: CPU, relógio,
processos e dispositivos são estruturas de dados nossas. O tempo avança em **ticks** (unidades
lógicas), e a simulação é determinística — a mesma entrada produz sempre a mesma saída.

**Dentro do escopo:** PCB, tabela de processos, os três estados clássicos e suas transições,
escalonamento de CPU, surtos de CPU e de E/S, coleta de estatísticas.
**Fora do escopo:** memória virtual, sistema de arquivos, rede real, IPC e threads.

### 1.1 Hardware simulado

| Componente | Descrição |
|---|---|
| CPU virtual | Executa no máximo um processo por tick. |
| `PC` | Índice da operação atual do processo. |
| `ACC` | Acumulador; existe para demonstrar salvamento e restauração de contexto. |
| `EFLAG` | Bit de modo (usuário/núcleo) e bit de interrupção pendente. |
| Relógio | Contador inteiro `relogio`, começa em 0 e é incrementado ao fim de cada iteração do laço. |
| Timer | Gera a interrupção de fim de quantum quando `quantum_restante` chega a zero. |
| Dispositivos | Dois dispositivos fictícios: `disco` e `rede`, cada um com fila própria e latência fixa vinda do arquivo de tarefas. |

### 1.2 Módulos

| Módulo | Responsabilidade |
|---|---|
| Carregador | Ler e validar `tarefas.txt` e criar os PCBs iniciais. |
| Gerenciador de processos | Criar, encerrar e transicionar processos. É o único módulo que escreve no campo `estado`. |
| Escalonador | Escolher qual processo pronto vai para a CPU (política intercambiável — §4). |
| Despachante | Salvar o contexto do processo que sai, restaurar o do que entra e recarregar o quantum. |
| Subsistema de E/S | Manter as filas dos dispositivos e contar o tempo restante de cada requisição. |
| Relatórios | Gerar o Gantt textual, o log de transições e as estatísticas finais. |

### 1.3 Fluxo geral de execução

Cada iteração do laço principal corresponde a exatamente um tick:

```
enquanto existir processo não terminado:
    1. admite os processos com tempo_chegada == relogio        -> PRONTO
    2. se a CPU está ociosa, o escalonador escolhe um processo  -> EXECUTANDO
    3. executa 1 tick do processo corrente (restante_surto--, quantum_restante--)
    4. avança a E/S: decrementa cada requisição; as concluídas  -> PRONTO
    5. trata o evento gerado pelo passo 3, nesta precedência:
         EXIT  >  solicitação de E/S  >  FORK  >  fim de quantum
    6. atualiza contadores (espera, bloqueio) e grava a coluna do Gantt
    7. relogio++
```

Duas decisões que valem registrar, porque afetam os resultados:

1. O escalonamento ocorre **antes** da execução, então um processo admitido no tick `t` só pode
   ocupar a CPU a partir de `t+1` (a menos que a CPU esteja ociosa naquele mesmo tick).
2. Se o surto de CPU acabar no mesmo tick em que o quantum expira, vale o evento do processo
   (`EXIT`, E/S ou `FORK`) — não faz sentido preemptar um processo que já saiu da CPU sozinho.

---

## 2. PCB e Tabela de Processos

### 2.1 Campos do PCB

| Campo | Tipo | Descrição |
|---|---|---|
| `pid` | int | Identificador único, sequencial a partir de 1, nunca reaproveitado. |
| `ppid` | int | PID do pai; `0` para os processos criados pelo carregador. |
| `nome` | string | Rótulo usado nos relatórios. |
| `estado` | enum | `PRONTO`, `EXECUTANDO`, `BLOQUEADO`, `TERMINADO`. |
| `prioridade_base` | int | Prioridade da entrada, de 0 (maior) a 9 (menor). |
| `prioridade_atual` | int | Prioridade efetiva, alterada pela elevação periódica (§4.3). |
| `pc`, `acc`, `eflag` | int | Registradores salvos na troca de contexto. |
| `ops`, `n_ops` | vetor | Sequência de operações do processo (§5.1). |
| `restante_surto` | int | Ticks que faltam no surto corrente, de CPU ou de E/S. |
| `quantum_restante` | int | Ticks restantes da fatia de tempo. |
| `dispositivo` | string | Dispositivo aguardado quando `estado == BLOQUEADO`; vazio nos demais casos. |
| `tempo_chegada` | int | Tick de admissão. |
| `t_cpu`, `t_espera`, `t_bloqueado` | int | Ticks acumulados em cada situação. |
| `t_primeira_exec`, `t_termino` | int | Ticks marcantes; `-1` enquanto não ocorreram. |
| `n_despachos` | int | Quantas vezes o processo foi para a CPU (equivale às trocas de contexto). |

O tempo de retorno é `t_termino - tempo_chegada` e o tempo de resposta é
`t_primeira_exec - tempo_chegada`. Ambos são calculados no relatório final, não armazenados.

### 2.2 Estruturas em C

```c
#define MAX_PROC  32
#define MAX_OPS   32
#define MAX_NOME  16

typedef enum { PRONTO, EXECUTANDO, BLOQUEADO, TERMINADO } estado_t;
typedef enum { OP_CPU, OP_IO, OP_FORK, OP_EXIT }          tipo_op_t;

typedef struct {
    tipo_op_t tipo;
    int       duracao;              /* usado por OP_CPU e OP_IO            */
    char      alvo[MAX_NOME];       /* dispositivo (OP_IO) ou nome (OP_FORK) */
} operacao_t;

typedef struct {
    int        pid, ppid;
    char       nome[MAX_NOME];
    estado_t   estado;
    int        prioridade_base, prioridade_atual;
    int        pc, acc, eflag;
    operacao_t ops[MAX_OPS];
    int        n_ops;
    int        restante_surto, quantum_restante;
    char       dispositivo[MAX_NOME];
    int        tempo_chegada, t_cpu, t_espera, t_bloqueado;
    int        t_primeira_exec, t_termino, n_despachos;
    int        espera_desde_boost;  /* usado pela elevação periódica */
} pcb_t;

typedef struct {
    pcb_t tabela[MAX_PROC];
    int   ocupado[MAX_PROC];
    int   n_ativos, proximo_pid;
} tab_proc_t;
```

### 2.3 Operações e invariantes

A tabela é um vetor de slots com busca linear — com `MAX_PROC = 32` não compensa complicar. Três
operações bastam: `tp_iniciar()`, que zera os slots e faz `proximo_pid = 1`; `tp_alocar()`, que
devolve o primeiro slot livre já com PID novo, ou `NULL` se a tabela estiver cheia; e
`tp_buscar(pid)`. O slot só é liberado depois que as estatísticas finais são coletadas.

Invariantes verificados a cada tick:

1. No máximo um PCB com `estado == EXECUTANDO`.
2. Todo PCB `BLOQUEADO` tem `dispositivo` preenchido e `restante_surto > 0`.
3. Um `FORK` com a tabela cheia falha, é registrado no log e não derruba a simulação — o pai segue
   normalmente para a próxima operação.

---

## 3. Ciclo de Vida e Grafo de Transição de Estados

| Estado | Significado |
|---|---|
| **PRONTO** | Pode executar; espera apenas a CPU. |
| **EM EXECUÇÃO** | Ocupa a CPU virtual neste tick. |
| **BLOQUEADO** | Espera a conclusão de uma E/S; não é candidato ao escalonador. |

`TERMINADO` é um estado auxiliar: o PCB continua na tabela só para o relatório final.

```
        criação / fork (T1)
                |
                v
          +-----------+   despacho (T2)    +--------------+
          |  PRONTO   | -----------------> | EM EXECUÇÃO  |
          |           | <----------------- |              |
          +-----------+  fim de quantum    +--------------+
             ^                (T3)            |        |
             |                                |        | exit (T6)
             | E/S concluída (T5)   E/S (T4)  |        v
             |                                |   [TERMINADO]
          +-------------+ <------------------+
          | BLOQUEADO   |
          +-------------+
```

| # | Transição | Evento | Ações |
|---|---|---|---|
| T1 | — → `PRONTO` | Chegada pelo arquivo de tarefas ou execução de `FORK` pelo pai | Alocar PCB, gerar PID, gravar `ppid`, copiar as operações do modelo, `pc = 0`, `prioridade_atual = prioridade_base`, enfileirar |
| T2 | `PRONTO` → `EXECUTANDO` | Despacho pelo escalonador com a CPU ociosa | Restaurar contexto, `quantum_restante = quantum`, `n_despachos++`, gravar `t_primeira_exec` se ainda for `-1`, zerar `espera_desde_boost` |
| T3 | `EXECUTANDO` → `PRONTO` | Interrupção de relógio (quantum esgotado) ou preempção por prioridade | Salvar contexto, liberar a CPU, reinserir o processo no fim da fila correspondente |
| T4 | `EXECUTANDO` → `BLOQUEADO` | Solicitação de E/S | Salvar contexto, gravar `dispositivo` e `restante_surto`, inserir na fila do dispositivo, `pc++`, liberar a CPU |
| T5 | `BLOQUEADO` → `PRONTO` | E/S concluída (`restante_surto == 0`) | Limpar `dispositivo`, enfileirar em prontos; a CPU **não** é devolvida automaticamente |
| T6 | `EXECUTANDO` → `TERMINADO` | Operação `EXIT` ou fim da lista de operações | Gravar `t_termino`, liberar a CPU, consolidar métricas, reparentar filhos ativos com `ppid = 0` |

Transições proibidas: `PRONTO → BLOQUEADO`, `BLOQUEADO → EXECUTANDO` e qualquer saída de
`TERMINADO`. Se ocorrerem, a simulação aborta com erro de invariante.

**Log de transições** (uma linha por transição, em `saida/transicoes.log`):

```
[0012] pid=3 compilador  PRONTO      -> EXECUTANDO  despacho     quantum=4
[0016] pid=3 compilador  EXECUTANDO  -> PRONTO      quantum      restante=3
[0019] pid=1 editor      EXECUTANDO  -> BLOQUEADO   e/s          disco dur=5
[0024] pid=1 editor      BLOQUEADO   -> PRONTO      e/s_concluida
```

---

## 4. Especificação do Escalonador de CPU

O simulador implementa duas políticas intercambiáveis, escolhidas por configuração e sem
recompilação. O núcleo só conversa com o escalonador pela interface abaixo, então trocar de
política é apontar um ponteiro para outra estrutura.

```c
typedef enum { ENT_NOVO, ENT_QUANTUM, ENT_IO } motivo_t;

typedef struct {
    const char *nome;
    void   (*iniciar)(void);
    void   (*adicionar)(pcb_t *p, motivo_t motivo);
    pcb_t *(*escolher)(void);        /* NULL se não houver prontos */
    void   (*ao_fim_do_tick)(void);  /* elevação periódica, contadores */
} politica_t;
```

### 4.1 Política A — Circular (Round Robin)

Uma única fila FIFO de prontos. O processo escolhido recebe `quantum` ticks; quando
`quantum_restante` chega a zero com surto de CPU ainda pendente, ocorre T3 e ele volta para o
**fim** da fila. Prioridade é ignorada nesta política.

Quando um processo volta de E/S (T5) e outro é preemptado por quantum (T3) no mesmo tick, o que
volta da E/S entra primeiro na fila. É uma escolha deliberada: favorece processos orientados a E/S,
que tendem a soltar a CPU rápido, e melhora a utilização dos dispositivos.

```
escolher():
    se fila vazia: retorna NULL
    p = desenfileira(fila)
    p.quantum_restante = quantum
    retorna p
```

### 4.2 Política B — Prioridades

Dez filas FIFO, uma por nível de prioridade (0 = mais alta, 9 = mais baixa). O escalonador pega o
primeiro processo da fila não vazia de menor índice, e o quantum continua valendo para dividir a CPU
entre processos de mesma prioridade.

Com `boost = 0`, a prioridade é **estática**: `prioridade_atual` nunca muda e a política se comporta
como prioridades puras — é justamente o modo que usamos para demonstrar a inanição no CT-04.

Se `preempcao = 1` (padrão), a chegada de um processo em `PRONTO` (por T1 ou T5) com
`prioridade_atual` estritamente menor que a do processo em execução provoca preempção imediata,
registrada no log com motivo `preempcao_prioridade`.

### 4.3 Prevenção de inanição — elevação periódica

Em vez de envelhecer cada processo por um contador individual, optamos por uma varredura periódica,
mais simples de implementar e de conferir na saída: a cada `boost` ticks (padrão 15), o simulador
percorre as filas de prontos e sobe um nível todo processo que não executou desde a varredura
anterior.

```
ao_fim_do_tick():
    se relogio > 0 e relogio % boost == 0:
        para cada p em estado PRONTO:
            se p.espera_desde_boost > 0 e p.prioridade_atual > 0:
                move p para a fila (p.prioridade_atual - 1)
                p.prioridade_atual--
            p.espera_desde_boost = 0
```

O campo `espera_desde_boost` é incrementado a cada tick em que o processo permanece pronto e zerado
quando ele é despachado (T2). Como cada varredura sobe no máximo um nível, um processo com
prioridade base p chega ao topo em no máximo `p × boost` ticks, e a espera fica limitada — nenhum
processo espera indefinidamente. Ao ser despachado, `prioridade_atual` volta ao valor de
`prioridade_base` se `reset = 1` (padrão), para que o ganho não seja permanente.

### 4.4 Parâmetros de configuração

| Parâmetro | Valores | Padrão | Descrição |
|---|---|---|---|
| `politica` | `rr`, `prio` | `rr` | Política ativa. |
| `quantum` | inteiro ≥ 1 | `4` | Fatia de tempo, em ticks. |
| `boost` | inteiro ≥ 0 | `15` | Intervalo da elevação periódica; `0` desativa (prioridade estática). |
| `preempcao` | `0`, `1` | `1` | Preempção por prioridade (só afeta `prio`). |
| `reset` | `0`, `1` | `1` | Restaura `prioridade_base` no despacho. |

---

## 5. Entradas, Casos de Teste e Diretrizes de Entrega

### 5.1 Arquivo de tarefas

Arquivo de texto orientado a linhas. Linhas em branco e iniciadas por `#` são ignoradas. Há dois
tipos de linha:

```
config <chave>=<valor> ...
proc   <nome> <chegada> <prioridade> <op> <op> ...
```

As operações são tokens de um caractere seguidos de argumento, o que deixa o arquivo curto e o
parser trivial:

| Token | Significado |
|---|---|
| `C<n>` | Surto de CPU de `n` ticks. |
| `D<n>` | E/S no disco, com duração `n`. |
| `R<n>` | E/S na rede, com duração `n`. |
| `F:<nome>` | Cria uma instância do modelo `<nome>` (simulação de `fork`). |
| `X` | `exit`. |

**Exemplo (`tarefas.txt`):**

```
# cenário misto: CPU-bound, E/S-bound e fork
config politica=rr quantum=4 boost=15 preempcao=1

proc editor      0  2  C5 D4 C3 X
proc compilador  2  1  C9 D2 C6 X
proc daemon      3  7  C12 X
proc shell       4  0  C2 F:filho C4 X
proc filho      -1  3  C3 R2 X
```

Regras de validação:

1. `chegada = -1` marca um **modelo**: o processo não é admitido pelo carregador, só passa a existir
   quando algum `F:<nome>` o instancia, e cada instância recebe um PID próprio.
2. A lista de operações deve terminar em `X`; se não terminar, o carregador acrescenta e avisa.
3. Durações precisam ser `≥ 1` e prioridades precisam estar entre 0 e 9.
4. Nome repetido, token desconhecido e dispositivo inexistente são erros fatais, relatados com o
   número da linha e código de saída diferente de zero.

Os parâmetros da linha de comando têm prioridade sobre os da linha `config`:

```bash
./simulador tarefas.txt --politica=prio --quantum=3 --boost=8
```

### 5.2 Saídas

**(a) Gantt textual** — uma coluna por tick, uma linha por processo:

```
GANTT (politica=rr quantum=4)
tick        0    5    10   15   20   25   30
            |    |    |    |    |    |    |
editor      ====.....ooooo===.................
compilador  ....====.....====....====........
daemon      .........====........====.....===
shell       ......====................====...
filho       ...........................====oo

legenda: = executando   . pronto   o bloqueado   (espaço) inexistente ou terminado
```

Acima de 120 ticks, o Gantt é impresso na forma compactada, uma linha por intervalo
(`pid | processo | inicio | fim | estado`), para não estourar a largura do terminal.

**(b) Log de transições**, no formato da §3.

**(c) Estatísticas:**

```
=== POR PROCESSO ===
pid  nome         cpu  espera  bloq  retorno  resposta  despachos
1    editor         8      11     4       23         0          3
2    compilador    15       9     2       26         2          4

=== GLOBAIS ===
ticks simulados .......: 34
utilizacao da CPU .....: 91,2%
processos concluidos ..: 5
espera media ..........: 9,40 ticks
retorno medio .........: 24,60 ticks
resposta media ........:  1,80 ticks
trocas de contexto ....: 17
elevacoes de prioridade: 0
```

### 5.3 Casos de teste

| # | Cenário | Configuração | Critério de aceitação |
|---|---|---|---|
| CT-01 | Round Robin com três processos idênticos | `rr`, `quantum=2`, 3× `C6 X` chegando em 0 | Rodízio estrito P1→P2→P3→P1; tempos de espera iguais entre os três |
| CT-02 | Bloqueio e desbloqueio | `rr`, 2 processos com `D3` | Nenhum processo `BLOQUEADO` é despachado; a CPU só fica ociosa quando todos estão bloqueados |
| CT-03 | Criação de processo | `rr`, 1 processo com `F:filho` | O filho recebe PID maior que o do pai, `ppid` correto, e entra em `PRONTO` no tick do fork |
| CT-04 | Inanição com prioridade estática | `prio`, `boost=0`, 1 processo prio=0 longo + 1 processo prio=9 | O processo de prioridade 9 não executa enquanto o de prioridade 0 não terminar |
| CT-05 | Elevação periódica resolve a inanição | mesma entrada do CT-04, `boost=5` | O processo de prioridade 9 executa; espera no máximo em torno de `9 × boost`; o log registra as elevações |

Cada caso tem seu arquivo em `testes/ct-0N.txt` e a saída esperada em `testes/ct-0N.esperado.txt`,
o que permite conferir o código gerado com um `diff`.

### 5.4 Entrega

```
atividade-03/
├── README.md          # esta especificação
├── src/               # código gerado a partir dela
├── testes/            # ct-01..ct-05 e saídas esperadas
└── saida/             # gantt.txt, transicoes.log, estatisticas.txt
```

A atividade foi feita em equipe de dois componentes, e cada um publica esta especificação em
`atividade-03/README.md` no seu próprio repositório `so-262`. Como o documento é a entrada para a
geração do código por harness (Claude Code / Open Code), tudo o que está aqui vale como regra: os
padrões de configuração, a ordem do laço principal, o formato das saídas e os cinco casos de teste
são o critério de conferência do que for gerado.

