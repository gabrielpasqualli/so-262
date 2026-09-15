Exercício 1: Escalonamento circular
Configurar o escalonamento circular (sem prioridade): janela Gerência do Processador /
Opções
 Criar dois processos com a mesma prioridade (um CPU-bound e outro I/O-bound)
Na janela Console Sosim / Processos / Selecionar observe o tempo de processador de cada
processo durante três minutos e as mudanças de estado. Após esse período anote o tempo de
processador de cada processo. Analise a distribuição do uso da UCP.
Pergunta: O que acontece se o tempo de time slice (quantum) aumentar ou diminuir?

Resolução: 
Se há um aumento do quantum, O sistema perde interatividade (tempo de resposta piora) e o dispositivo de E/S pode ficar ocioso por mais tempo enquanto o processo I/O-bound aguarda a CPU para disparar a próxima leitura/escrita.
Se o quantum diminuir, Aumento de overhead (desperdício de CPU com o escalador) e redução do throughput global se o quantum for excessivamente pequeno.

Exercício 2: Escalonamento circular com prioridades
 Configurar o escalonamento por prioridades: janela Gerência do Processador / Opções
 Criar um processo CPU-bound com prioridade 3 e um I/O-bound com prioridade 4.
Na janela Console Sosim / Processos / Selecionar observe o tempo de processador de cada
processo durante três minutos e as mudanças de estado. Após esse período anote o tempo de
processador de cada processo. Analise a distribuição do uso da UCP comparativamente ao
Exercício 1.
Pergunta: O que acontece se o tempo de espera do processo I/O-bouns aumentar ou diminuir?

Resolução: 
Se o Tempo de Espera de E/S aumentar, O uso da CPU pelo CPU-bound atinge quase 100% durante esses intervalos. No entanto, o tempo total de conclusão do processo I/O-bound aumenta consideravelmente devido à lentidão do dispositivo.
Se o Tempo de Espera de E/S diminuir, O processo I/O-bound usa a CPU por pouquíssimo tempo (apenas para processar o dado e disparar a próxima E/S) e já volta a se bloquear. O CPU-bound roda em "micro-rajadas", avançando muito lentamente.

Exercício 3: Escalonamento circular com prioridades
 Configurar o escalonamento por prioridades: janela Gerência do Processador / Opções
 Criar um processo CPU-bound com prioridade 4 e um I/O-bound com prioridade 3.
Analise a situação.
Pergunta: Quais devem ser os critérios para determinar as prioridades de processos?

Resolução:
1. Perfil do Processo (E/S-bound vs. CPU-bound): Processos I/O-bound devem ter maior prioridade que processos CPU-bound.
2. Tipo de Processo e Criticidade: Processos de Sistema / Kernel: Prioridade máxima; Processos Interativos / Tempo Real: Prioridade alta (O usuário percebe imediatamente qualquer atraso); Processos em Segundo Plano (Batch): Prioridade baixa (Podem ser executados quando a CPU estiver ociosa.)
3. Critérios Estáticos vs. Dinâmicos:
  Prioridade Estática: Definida na criação do processo (pelo usuário ou pelo SO) e mantida inalterada até o fim.
  Prioridade Dinâmica: O SO ajusta a prioridade em tempo de execução para garantir justiça: Aumentar a prioridade de processos que estão há muito tempo esperando na fila de prontos (evita starvation), e reduziz a prioridade de processos que consomem todo o quantum de CPU continuamente sem ceder o processador.
   
Exercício 4: Escalonamento circular com prioridades (prioridade dinâmica – mecanismo
adaptivo)
 Configurar o escalonamento por prioridades: janela Gerência do Processador / Opções
 Criar dois processos com a mesma prioridade (um CPU-bound e outro I/O-bound)
Observe o escalonamento dos processos. Compare a situação desse escalonamento com o
apresentado no Exercício 2.
Pergunta: Qual a vantagem desse escalonamento em processos I/O-bound de perfis diferentes?

Resolução:
1. Desbloqueio e Retorno Imediato à Fila
2. Liberação Voluntária da CPU (Maximização da Eficiência)
3. Prevenção Natural de Inanição (Starvation)
