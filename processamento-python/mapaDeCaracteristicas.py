import numpy as np
from PIL import Image

alpha = 1/16 #ativacao
kernel_r = np.array([[2,1,2], [1,4,1], [2,1,2]]) 
kernel_g = np.array([[1,2,1], [2,4,2], [1,2,1]])
kernel_b = np.array([[2,2,2], [1,4,1], [2,2,2]])

def convolucao_3x3(canal: np.ndarray, kernel: np.ndarray):
    altura, largura = canal.shape

    altura_saida = altura - 2 #nao trata as bordas, entao, tira 2 de cada dimensao
    largura_saida = largura - 2
    canal_convolucionado = np.zeros((altura_saida, largura_saida), dtype=np.int64)

    for x in range(altura_saida):
        for y in range(largura_saida):
            bloco = canal[x:x+3, y:y+3]
            soma = np.sum(bloco*kernel)
            canal_convolucionado[x,y] = int(soma)

    return canal_convolucionado

def ativacaoLeakyRelu(canal_convolucionado: np.ndarray, alpha: float):
    canal_ativacao = canal_convolucionado.astype(float)
    valores_neg = canal_ativacao < 0.0

    canal_ativacao[valores_neg] = canal_ativacao[valores_neg] * alpha

    canal_ativacao_truncado = np.trunc(canal_ativacao).astype(np.int64)

    return canal_ativacao_truncado

def avgPooling(canal: np.ndarray):
    altura, largura = canal.shape

    altura_saida = altura // 2 #diminui as dimensoes pela metade. pega so a parte inteira
    largura_saida = largura // 2
    canal_pooling = np.zeros((altura_saida, largura_saida), dtype=np.int64)

    for x in range(altura_saida):
        for y in range(largura_saida):
            bloco = canal[2*x:2*x+2, 2*y:2*y+2]
            canal_pooling[x,y] = int(np.round(np.mean(bloco)))
    
    return canal_pooling

def salvarMapaASM(mapa_r: np.ndarray, mapa_g: np.ndarray, mapa_b: np.ndarray, nome_arquivo):
    mapa_r = np.clip(mapa_r, 0, 255)
    mapa_g = np.clip(mapa_g, 0, 255)
    mapa_b = np.clip(mapa_b, 0, 255)

    with open(nome_arquivo, "w") as f:
        f.write(".data\n\n")
        
        def escrever_label(label, arr):
            flat = arr.flatten().tolist()
            f.write(f"{label}: .byte ")
            
            # escreve grupos de 16 por linha
            grupos = [flat[i:i+16] for i in range(0, len(flat), 16)]
            for idx, g in enumerate(grupos):
                linha = ", ".join(str(int(v)) for v in g)
                if idx == 0:
                    f.write(linha + "\n")
                else:
                    f.write("    .byte " + linha + "\n")
            f.write("\n")

        escrever_label("mapa_carac_R", mapa_r)
        escrever_label("mapa_carac_G", mapa_g)
        escrever_label("mapa_carac_B", mapa_b)
    print(f"Arquivo ASM salvo em: {nome_arquivo} (formato .byte)")

def gerarMapaTuplas(mapa_r: np.ndarray, mapa_g: np.ndarray, mapa_b: np.ndarray):
    altura, largura = mapa_r.shape
    lista_tuplas = []

    for x in range(altura):
        for y in range(largura):
            tupla_rgb = (int(mapa_r[x, y]), int(mapa_g[x, y]), int(mapa_b[x, y]))
            lista_tuplas.append(tupla_rgb)

    return lista_tuplas

def salvarMapaTuplasASM(mapa_tuplas, nome_arquivo):
    with open(nome_arquivo, "w") as f:
        f.write(".data\n\n")
        f.write("mapa_carac_rgb:\n")

        for (r, g, b) in mapa_tuplas:
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            f.write(f"    .byte {r}, {g}, {b}\n")

    print(f"Arquivo ASM com tuplas salvo em: {nome_arquivo}")

def main():
    #carrega imagem
    nome_imagem = "11.jpeg" #nome da imagem
    saida_mapa = "mapa_caracteristicas_python_G11.asm"

    try:
        imagem = Image.open(nome_imagem)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_imagem}' não foi encontrado.")
        exit()

    array = np.array(imagem)
    
    tamanho = array.shape
    print(f"o tamanho eh {tamanho}")

    canal_r = array[:, :, 0]
    canal_g = array[:, :, 1]
    canal_b = array[:, :, 2]

    #convolucao 3x3
    conv_r = convolucao_3x3(canal_r, kernel_r)
    conv_g = convolucao_3x3(canal_g, kernel_g)
    conv_b = convolucao_3x3(canal_b, kernel_b)

    #ativação LeakyReLU
    ativ_r = ativacaoLeakyRelu(conv_r, alpha)
    ativ_g = ativacaoLeakyRelu(conv_g, alpha)
    ativ_b = ativacaoLeakyRelu(conv_b, alpha)

    #avgPooling 2x2
    pool_r = avgPooling(ativ_r)
    pool_g = avgPooling(ativ_g)
    pool_b = avgPooling(ativ_b)

    #gerar mapa com tuplas
    mapa_tuplas = gerarMapaTuplas(pool_r, pool_g, pool_b)
    salvarMapaTuplasASM(mapa_tuplas, "mapa_caracteristicas_tuplas.asm")


    #salvar saida para assembly
    salvarMapaASM(pool_r, pool_g, pool_b, nome_arquivo=saida_mapa)

    print("Processamento concluído.")

if __name__ == "__main__":
    main()