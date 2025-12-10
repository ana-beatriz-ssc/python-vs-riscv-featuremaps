from PIL import Image
import numpy as np

# Digite o nome da imagem aqui
nome_imagem = "11.jpeg"

try:
    imagem = Image.open(nome_imagem)
except FileNotFoundError:
    print(f"Erro: O arquivo '{nome_imagem}' não foi encontrado.")
    exit()

imagem = imagem.convert("RGB")
array = np.array(imagem)
canal_r = array[:, :, 0]
canal_g = array[:, :, 1]
canal_b = array[:, :, 2]

output_file = "imagem_dados.asm"

def escrever_buffer_asm(arquivo, label, dados_array):
    arquivo.write(f"{label}:\n")
    dados_flat = dados_array.flatten()
    elementos_por_linha = 16 
    for i in range(0, len(dados_flat), elementos_por_linha):
        chunk = dados_flat[i:i + elementos_por_linha]
        valores_str = ", ".join(map(str, chunk))
        arquivo.write(f"    .byte {valores_str}\n")
    
    arquivo.write("\n")

# Gera o arquivo .asm
with open(output_file, "w") as f:
    f.write(".data\n\n")
    
    print("Escrevendo buffer imagem_R...")
    escrever_buffer_asm(f, "imagem_R", canal_r)
    
    print("Escrevendo buffer imagem_G...")
    escrever_buffer_asm(f, "imagem_G", canal_g)
    
    print("Escrevendo buffer imagem_B...")
    escrever_buffer_asm(f, "imagem_B", canal_b)

print(f"\nSucesso! O arquivo '{output_file}' foi gerado com os 3 buffers.")
print(f"Dimensões da imagem: {imagem.width} x {imagem.height} pixels.")