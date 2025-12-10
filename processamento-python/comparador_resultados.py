import re
import os

def ler_valores_asm(nome_arquivo):
    if not os.path.exists(nome_arquivo):
        return None
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        texto = f.read()
    return [int(n) for n in re.findall(r"-?\d+", texto)]


def comparar_arquivos(arq_ref, arq_teste):
    ref = ler_valores_asm(arq_ref)
    tst = ler_valores_asm(arq_teste)

    if ref is None or tst is None:
        return {"ok": False, "msg": "arquivo inexistente"}

    tam_min = min(len(ref), len(tst))
    erros = []

    for i in range(tam_min):
        if ref[i] != tst[i]:
            erros.append((i, ref[i], tst[i]))

    return {
        "ok": len(erros) == 0 and len(ref) == len(tst),
        "tamanhos_iguais": len(ref) == len(tst),
        "total_erros": len(erros),
        "erros": erros[:5]
    }


def main():
    pares = [
        ("mapa_caracteristicas_tuplas.asm",
         "mapa_caracteristicas_tuplas_assembly.asm",
         "TUPLAS RGB"),

        ("mapa_caracteristicas_python_G11.asm",
         "mapa_caracteristicas_assembly_G11.asm",
         "CANAIS SEPARADOS")
    ]

    for ref, tst, titulo in pares:
        resultado = comparar_arquivos(ref, tst)

        print(f"\n=== {titulo} ===")
        if resultado["ok"]:
            print("Arquivos idênticos.")
        else:
            if resultado["total_erros"] == 0:
                print("Valores iguais, mas tamanhos diferentes.")
            else:
                print(f"Diferenças encontradas: {resultado['total_erros']}")
                for i, v1, v2 in resultado["erros"]:
                    print(f"índice {i}: ref={v1}, asm={v2}")


if __name__ == "__main__":
    main()
