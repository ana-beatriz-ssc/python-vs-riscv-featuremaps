
.include "imagem_dados.asm"

.data
# --- CONFIGURAÇÃO DA IMAGEM ---
WIDTH:      .word 176     
HEIGHT:     .word 120    

# --- KERNELS---
KERNEL_R:   .word 2, 1, 2, 1, 4, 1, 2, 1, 2
KERNEL_G:   .word 1, 2, 1, 2, 4, 2, 1, 2, 1
KERNEL_B:   .word 2, 2, 2, 1, 4, 1, 2, 2, 2

# --- BUFFERS DE SAÍDA ---
MAPA_R:      .space 8000
MAPA_G:      .space 8000
MAPA_B:      .space 8000

# Buffer Temporário
BUFFER_TEMP: .space 100000 

# --- FORMATAÇÃO ---
str_header:  .string ".data\n"
str_label_R: .string "\nmapa_carac_R:\n    .byte "
str_label_G: .string "\n\nmapa_carac_G:\n    .byte "
str_label_B: .string "\n\nmapa_carac_B:\n    .byte "
str_comma:   .string ", "

.text
.globl main
.eqv SYS_PRINT_INT 1
.eqv SYS_PRINT_STR 4
.eqv SYS_EXIT 10

main:
    li a7, SYS_PRINT_STR
    la a0, str_header
    ecall

    # --- CANAL R ---
    la a0, imagem_R
    la a1, MAPA_R
    la a2, KERNEL_R
    jal ra, processar_canal_completo

    li a7, SYS_PRINT_STR
    la a0, str_label_R
    ecall
    la a0, MAPA_R
    jal ra, imprimir_mapa_formatado

    # --- CANAL G ---
    la a0, imagem_G
    la a1, MAPA_G
    la a2, KERNEL_G
    jal ra, processar_canal_completo

    li a7, SYS_PRINT_STR
    la a0, str_label_G
    ecall
    la a0, MAPA_G
    jal ra, imprimir_mapa_formatado

    # --- CANAL B ---
    la a0, imagem_B
    la a1, MAPA_B
    la a2, KERNEL_B
    jal ra, processar_canal_completo

    li a7, SYS_PRINT_STR
    la a0, str_label_B
    ecall
    la a0, MAPA_B
    jal ra, imprimir_mapa_formatado

    li a7, SYS_EXIT
    ecall

processar_canal_completo:
    addi sp, sp, -16
    sw ra, 0(sp)
    sw s0, 4(sp)
    sw s1, 8(sp)
    sw s2, 12(sp)

    mv s0, a0
    mv s1, a1
    mv s2, a2

    # --- CONVOLUÇÃO ---
    mv a0, s0
    la a1, BUFFER_TEMP
    mv a2, s2
    lw a3, WIDTH
    lw a4, HEIGHT
    jal ra, convolucao_3x3

    # --- LEAKYRELU ---
    la a0, BUFFER_TEMP
    lw t0, WIDTH
    addi t0, t0, -2
    lw t1, HEIGHT
    addi t1, t1, -2
    mul a1, t0, t1
    jal ra, ativacao_leaky_relu

    # --- AVG POOLING ---
    la a0, BUFFER_TEMP
    mv a1, s1
    lw t0, WIDTH
    addi a2, t0, -2
    lw t1, HEIGHT
    addi a3, t1, -2
    jal ra, avg_pooling_byte

    lw s2, 12(sp)
    lw s1, 8(sp)
    lw s0, 4(sp)
    lw ra, 0(sp)
    addi sp, sp, 16
    ret

convolucao_3x3:
    addi t0, a4, -2     
    addi t1, a3, -2     
    li t2, 0            
L_cy:
    bge t2, t0, fim_conv
    li t3, 0            
L_cx:
    bge t3, t1, next_cy
    
    li t4, 0            
    li t5, 0            
L_ky:
    li t6, 3
    bge t5, t6, store_c
    li a5, 0            
L_kx:
    li t6, 3
    bge a5, t6, next_ky

    add s3, t2, t5
    mul s3, s3, a3
    add s4, t3, a5
    add s3, s3, s4
    add s3, s3, a0
    lbu s5, 0(s3)

    mul s3, t5, t6
    add s3, s3, a5
    slli s3, s3, 2
    add s3, s3, a2
    lw s6, 0(s3)

    mul s5, s5, s6
    add t4, t4, s5

    addi a5, a5, 1
    j L_kx

next_ky:
    addi t5, t5, 1
    j L_ky

store_c:
    mul s3, t2, t1
    add s3, s3, t3
    slli s3, s3, 2
    add s3, s3, a1
    sw t4, 0(s3)

    addi t3, t3, 1
    j L_cx

next_cy:
    addi t2, t2, 1
    j L_cy

fim_conv:
    ret

ativacao_leaky_relu:
    li t0, 0
    li t4, 16
L_relu:
    bge t0, a1, fim_relu
    slli t2, t0, 2    
    add t2, t2, a0
    lw t3, 0(t2)

    bge t3, zero, prox_relu
    div t3, t3, t4     

    sw t3, 0(t2)
prox_relu:
    addi t0, t0, 1
    j L_relu
fim_relu:
    ret

avg_pooling_byte:
    srli t0, a3, 1      
    srli t1, a2, 1      
    li t2, 0
L_py:
    bge t2, t0, fim_pool
    li t3, 0
L_px:
    bge t3, t1, next_py

    slli s3, t2, 1
    slli s4, t3, 1

    mul s5, s3, a2
    add s5, s5, s4
    slli s5, s5, 2
    add s5, s5, a0

    lw s6, 0(s5)
    lw s7, 4(s5)
    slli s8, a2, 2
    add s8, s5, s8
    lw s9, 0(s8)
    lw s10, 4(s8)

    add s11, s6, s7
    add s11, s11, s9
    add s11, s11, s10   
    
    srai t4, s11, 2     
    andi t5, s11, 3     

    li t6, 2            
    blt t5, t6, pool_write_q  
    bgt t5, t6, pool_inc      

    andi a4, t4, 1      
    beqz a4, pool_write_q 
    addi t4, t4, 1      
    j pool_write_q

pool_inc:
    addi t4, t4, 1

pool_write_q:
    mv s11, t4          

    blt s11, zero, clamp0
    li a5, 255          
    ble s11, a5, store_b
    li s11, 255
    j store_b
clamp0:
    li s11, 0

store_b:
    mul s5, t2, t1
    add s5, s5, t3
    add s5, s5, a1
    sb s11, 0(s5)

    addi t3, t3, 1
    j L_px

next_py:
    addi t2, t2, 1
    j L_py

fim_pool:
    ret

imprimir_mapa_formatado:
    lw t0, WIDTH
    addi a1, t0, -2
    srli a1, a1, 1
    lw t1, HEIGHT
    addi a2, t1, -2
    srli a2, a2, 1

    mul t0, a1, a2
    li t1, 0
    mv t2, a0

L_print:
    bge t1, t0, fim_print
    lbu a0, 0(t2)
    li a7, SYS_PRINT_INT
    ecall

    addi t3, t0, -1
    beq t1, t3, no_comma
    li a7, SYS_PRINT_STR
    la a0, str_comma
    ecall
no_comma:
    addi t1, t1, 1
    addi t2, t2, 1
    j L_print

fim_print:
    ret
