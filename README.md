# Geração de Mapas de Características em Python e RISC-V
Este repositório contém a implementação do trabalho prático da disciplina Arquitetura de Computadores (2025.2), realizado na Universidade Federal do Piauí (UFPI). O objetivo foi gerar e comparar mapas de características (feature maps) obtidos a partir de uma imagem, utilizando Python e Assembly RISC-V (RARS), garantindo que ambos produzissem resultados idênticos.

# Descrição
O projeto realiza o processamento da imagem fornecida pelo professor, gerando mapas de características separados por canal (R, G, B). Esse processamento ocorre tanto em Python (alto nível) quanto em Assembly RISC-V (baixo nível).

As etapas de processamento foram:
1. Convolução 3×3 com kernels específicos por canal
2. Aplicação da função de ativação LeakyReLU
3. Avg Pooling 2×2 (média dos blocos)
4. Geração de arquivos .asm contendo os valores pós-processamento
5. Comparação pixel a pixel dos resultados Python × Assembly

# Arquivos Principais
## extrai_Imagem.py (Código criado e fornecido pelos monitores da disciplina)
- Lê a imagem 11.jpeg
- Separa os canais R, G e B
- Converte cada canal para buffer linear
- Gera imagem_dados.asm com valores em .byte (16 por linha)

## mapaDeCaracteristicas.py
Contém funções principais para o processamento em Python:

- convolucao_3x3
- ativacaoLeakyRelu
- avgPooling
- salvarMapaASM
- gerarMapaTuplas
- salvarMapaTuplasASM
- main

Gera dois arquivos:
- mapa_caracteristicas_python_G11.asm – formato por canal
- mapa_caracteristicas_tuplas.asm – formato por tupla RGB (facilita a leitura e depuração)

## processamento.asm
Implementação completa da convolução e pooling em Assembly RISC-V:

Etapas executadas:
- Convolução individual para R, G e B
- Aplicação da ativação LeakyReLU (α = 1/16)
- Média 2×2 com arredondamento e clamp (0–255)
- Armazenamento final em MAPA_R, MAPA_G, MAPA_B
- Impressão formatada dos mapas no console

O arquivo usa os dados presentes em imagem_dados.asm.

## extrator_assembly.py
Converte a saída textual do RARS em arquivos estruturados:
- mapa_caracteristicas_assembly_G11.asm – formato por canal
- mapa_caracteristicas_tuplas_assembly.asm – formato RGB por pixel

## comparador_de_arquivos.py
Compara os mapas gerados em Python e Assembly:
- Verifica tamanho, conteúdo e ordem
- Detecta divergências numéricas pixel a pixel
- Permite validar a equivalência das implementações

# Resultados
Após padronização dos arquivos e comparação final:
- Nenhuma discrepância encontrada
- Python e Assembly produziram exatamente os mesmos valores
- Os três canais (R, G, B) coincidem em tamanho e conteúdo
