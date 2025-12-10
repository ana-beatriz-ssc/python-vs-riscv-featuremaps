import re
import os

def ler_dados_assembly(nome_arquivo):
    """
    Lê o arquivo de saída do RARS e extrai os arrays de bytes.
    Espera encontrar os rótulos 'mapa_carac_R:', 'mapa_carac_G:' e 'mapa_carac_B:'.
    """
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{nome_arquivo}' não encontrado na pasta: {os.getcwd()}")
        return None, None, None

    # Função auxiliar para extrair números entre dois marcadores ou até o fim
    def extrair_numeros(texto, inicio_marcador, fim_marcador=None):
        try:
            if inicio_marcador not in texto:
                print(f"Aviso: Marcador '{inicio_marcador}' não encontrado no arquivo.")
                return []

            start_idx = texto.index(inicio_marcador) + len(inicio_marcador)
            
            if fim_marcador and fim_marcador in texto:
                end_idx = texto.index(fim_marcador, start_idx)
                bloco = texto[start_idx:end_idx]
            else:
                bloco = texto[start_idx:]
            
            # Encontra todos os números inteiros no bloco
            # A regex r'-?\d+' captura números positivos e negativos (embora pixel seja positivo)
            lista_numeros = [int(n) for n in re.findall(r'-?\d+', bloco)]
            return lista_numeros
        except Exception as e:
            print(f"Erro ao extrair dados de {inicio_marcador}: {e}")
            return []

    # Extração baseada nos labels que usamos no código Assembly
    print("Extraindo Canal R...")
    dados_r = extrair_numeros(conteudo, "mapa_carac_R:", "mapa_carac_G:")
    
    print("Extraindo Canal G...")
    dados_g = extrair_numeros(conteudo, "mapa_carac_G:", "mapa_carac_B:")
    
    print("Extraindo Canal B...")
    dados_b = extrair_numeros(conteudo, "mapa_carac_B:")

    return dados_r, dados_g, dados_b

def salvar_formato_g11(dados_r, dados_g, dados_b, nome_saida):
    """
    Salva no formato do arquivo 'mapa_caracteristicas_python_G11.asm'.
    Formato: Label seguido de .byte com 16 valores por linha.
    """
    if not dados_r:
        print("Aviso: Sem dados para salvar no arquivo G11.")
        return

    try:
        with open(nome_saida, 'w', encoding='utf-8') as f:
            f.write(".data\n\n")

            def escrever_canal(label, dados):
                f.write(f"{label}: .byte ")
                for i, val in enumerate(dados):
                    # Escreve o valor
                    f.write(str(val))
                    
                    # Lógica para vírgulas e quebras de linha
                    if i == len(dados) - 1:
                        # Último elemento: sem vírgula, com quebra
                        f.write("\n")
                    elif (i + 1) % 16 == 0:
                        # Fim de linha (múltiplo de 16): sem vírgula, quebra e nova diretiva
                        f.write("\n    .byte ")
                    else:
                        # Elemento normal: vírgula e espaço
                        f.write(", ")
                f.write("\n")

            escrever_canal("mapa_carac_R", dados_r)
            escrever_canal("mapa_carac_G", dados_g)
            escrever_canal("mapa_carac_B", dados_b)
        print(f"[SUCESSO] Arquivo '{nome_saida}' gerado.")
    except Exception as e:
        print(f"Erro ao salvar arquivo G11: {e}")

def salvar_formato_tuplas(dados_r, dados_g, dados_b, nome_saida):
    """
    Salva no formato do arquivo 'mapa_caracteristicas_tuplas_assembly.asm'.
    Formato: '    .byte R, G, B' (um pixel por linha).
    """
    if not dados_r:
        return

    # Verifica o menor tamanho para evitar erro de índice
    tamanho = min(len(dados_r), len(dados_g), len(dados_b))
    if tamanho == 0:
        print("Erro: Um dos canais está vazio.")
        return

    try:
        with open(nome_saida, 'w', encoding='utf-8') as f:
            f.write(".data\n\n")
            f.write("mapa_carac_rgb:\n")
            
            for i in range(tamanho):
                r = dados_r[i]
                g = dados_g[i]
                b = dados_b[i]
                f.write(f"    .byte {r}, {g}, {b}\n")

        print(f"[SUCESSO] Arquivo '{nome_saida}' gerado.")
    except Exception as e:
        print(f"Erro ao salvar arquivo Tuplas: {e}")

def main():
    # Nome do arquivo que você copiou do RARS
    arquivo_entrada = "processamento_assembly.asm"
    
    # Nomes dos arquivos finais
    saida_g11 = "mapa_caracteristicas_assembly_G11.asm"
    saida_tuplas = "mapa_caracteristicas_tuplas_assembly.asm"

    print(f"--- Iniciando processamento de '{arquivo_entrada}' ---")
    r, g, b = ler_dados_assembly(arquivo_entrada)

    if r and g and b:
        print(f"\nDados extraídos com sucesso!")
        print(f"Pixels Canal R: {len(r)}")
        print(f"Pixels Canal G: {len(g)}")
        print(f"Pixels Canal B: {len(b)}")
        
        # Gera os arquivos
        salvar_formato_g11(r, g, b, saida_g11)
        salvar_formato_tuplas(r, g, b, saida_tuplas)
        
        print("\nProcesso finalizado.")
    else:
        print("\nFALHA: Não foi possível extrair os dados corretamente.")
        print("Verifique se você copiou a saída do RARS para 'processamento_assembly.asm'")
        print("O arquivo deve começar com '.data' e conter 'mapa_carac_R:', etc.")

if __name__ == "__main__":
    main()