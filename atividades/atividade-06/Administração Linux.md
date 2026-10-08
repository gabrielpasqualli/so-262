

Este exercício prático aborda o gerenciamento de arquivos e diretórios em ambiente Linux, cobrindo navegação, manipulação de arquivos, cópia, movimentação e automação por meio de Shell Script no sistema de arquivos 1, 2\.

### Cenário do Exercício

Você é o administrador de sistemas de uma empresa e precisa organizar a estrutura de pastas do **"Projeto\_A"**, gerar arquivos de relatório e log, organizar os arquivos entre diretórios e desenvolver um script em Shell Script para automatizar a cópia de segurança (backup) 2, 3\.

### Etapa 1: Navegação e Inspeção do Ambiente

Antes de criar qualquer pasta, é essencial identificar em qual ponto da árvore do sistema de arquivos você está localizado 1, 4\.

1. Verifique o seu diretório atual de trabalho usando o comando pwd 4\.  
2. Navegue para o seu diretório pessoal (*home*) com o comando cd \~ 5, 6\.  
3. Liste todo o conteúdo do seu diretório em formato detalhado, incluindo arquivos ocultos, utilizando ls \-la 7-9.

pwd  
cd \~  
ls \-la

* **Conceito:** O comando pwd exibe o caminho absoluto do diretório ativo no terminal 4\. O caractere \~ é um atalho direto para a pasta pessoal do usuário (/home/usuario) 6\. O comando ls \-la exibe permissões, proprietário, tamanho e arquivos ocultos (iniciados com .) 8-10.

### Etapa 2: Criação da Estrutura de Diretórios

Crie a estrutura do **"Projeto\_A"** e seus subdiretórios usando caminhos relativos 11-13.

1. Crie o diretório principal chamado Projeto\_A 12, 14\.  
2. Entre no diretório Projeto\_A 5, 13\.  
3. Crie três subdiretórios simultaneamente: documentos, logs e scripts 12, 15\.

mkdir Projeto\_A  
cd Projeto\_A  
mkdir documentos logs scripts  
ls \-l

* **Conceito:** O comando mkdir cria novos diretórios 12, 14\. É possível passar múltiplos nomes como argumento para criar vários diretórios de uma vez 15\. O comando cd com caminho relativo permite navegar a partir do diretório atual sem precisar digitar o caminho completo desde a raiz / 5, 11, 13\.

### Etapa 3: Criação e Edição de Arquivos de Texto

Nesta etapa, você criará arquivos de texto e inserirá conteúdo neles 8, 16, 17\.

1. Crie um arquivo vazio chamado relatorio\_inicial.txt dentro da pasta documentos usando o comando touch 8, 16\.  
2. Grave uma linha de texto dentro de um novo arquivo sistema.log na pasta logs usando echo com o redirecionador \> 17\.  
3. Visualize o conteúdo do arquivo gravado usando o comando cat 18, 19\.

touch documentos/relatorio\_inicial.txt  
echo "Log de inicialização do sistema \- Projeto A" \> logs/sistema.log  
cat logs/sistema.log

* **Conceito:** O touch altera a data de modificação ou cria um arquivo vazio 8, 16\. O operador \> redireciona a saída do comando echo diretamente para um arquivo de texto 17\. O comando cat imprime o conteúdo do arquivo no terminal 18, 19\.

### Etapa 4: Cópia e Movimentação de Arquivos

Gerencie os arquivos copiando e movendo-os entre as pastas criadas 20-23.

1. Faça uma cópia do arquivo relatorio\_inicial.txt na pasta logs com o nome relatorio\_backup.txt usando cp 20, 23\.  
2. Mova o arquivo sistema.log do diretório logs para o diretório documentos usando mv 21, 22\.  
3. Confirme a alteração listando o conteúdo dos dois diretórios 7, 24\.

cp documentos/relatorio\_inicial.txt logs/relatorio\_backup.txt  
mv logs/sistema.log documentos/  
ls \-l documentos  
ls \-l logs

* **Conceito:** O comando cp duplica o arquivo, mantendo o original intacto 20, 23\. O comando mv transfere o arquivo para o destino (ou o renomeia), removendo-o da localização de origem 21, 22\.

### Etapa 5: Criação e Execução de um Script Shell

Desenvolva um script na pasta scripts para automatizar a cópia de segurança dos documentos 2, 3, 25, 26\.

1. Entre no diretório scripts 5\.  
2. Crie o arquivo fazer\_backup.sh com um editor de texto (nano ou vim) 16, 27, 28\.  
3. Escreva o seguinte código dentro do script:

\#\!/bin/bash  
\# Script de automação de backup do Projeto\_A

echo "Iniciando o processo de backup..."  
mkdir \-p \~/Projeto\_A/backup\_geral  
cp \-r \~/Projeto\_A/documentos/\* \~/Projeto\_A/backup\_geral/  
echo "Backup concluído com sucesso em: \$(date)"

1. Adicione permissão de execução ao script com chmod \+x 29-31.  
2. Execute o script no diretório atual utilizando ./fazer\_backup.sh 25, 31, 32\.

cd \~/Projeto\_A/scripts  
chmod \+x fazer\_backup.sh  
./fazer\_backup.sh

* **Conceito:** A primeira linha \#\!/bin/bash (chamada *shebang*) define qual interpretador executará as instruções do arquivo 26, 33\. Por padrão, arquivos recém-criados não possuem permissão de execução; o comando chmod \+x adiciona essa permissão 29, 31, 34\. O caractere ./ sinaliza ao shell que o executável está localizado no diretório corrente 25, 32\.

### Etapa 6: Verificação do Backup

Confirme se o script executou a tarefa corretamente 14, 32\.  
cd \~/Projeto\_A/backup\_geral  
ls \-l

* **Resultado Esperado:** O diretório backup\_geral deve conter as cópias de todos os arquivos do diretório documentos, validando a automação desenvolvida 20, 32\.

💡 Deseja expandir este exercício adicionando tarefas de compactação do backup com tar.gz ou agendamento de execução automática com o cron?  

Displaying Administração Linux.md.
