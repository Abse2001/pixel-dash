/* First instruction of the GP ROM's UART0 peripheral-boot payload.
 * The ROM has already configured the UART and internal SRAM. */
.syntax unified
.cpu cortex-a8
.arm
.section .text
.global _start
.type _start, %function
_start:
    cpsid   if
    ldr     r0, =0x44e10040         @ CONTROL_STATUS, before any pad writes
    ldr     r5, [r0]
    ldr     r4, =0x44e09000         @ UART0
    mov     r0, #3
    strb    r0, [r4, #0x0c]        @ operational register bank, 8N1
    adr     r6, banner
1:  ldrb    r0, [r6], #1
    cmp     r0, #0
    beq     print_status
    bl      putc
    b       1b

print_status:
    mov     r6, #8
2:  mov     r0, r5, lsr #28
    cmp     r0, #10
    addlo   r0, r0, #'0'
    addhs   r0, r0, #('A' - 10)
    bl      putc
    lsl     r5, r5, #4
    subs    r6, r6, #1
    bne     2b
    mov     r0, #13
    bl      putc
    mov     r0, #10
    bl      putc
halt:
    b       halt

putc:
    ldrb    r1, [r4, #0x14]        @ line status register
    tst     r1, #0x20              @ transmit holding register empty
    beq     putc
    strb    r0, [r4]               @ transmit holding register
    bx      lr
.balign 4
banner:
    .asciz "Pixel Dash SRAM CONTROL_STATUS=0x"
.ltorg
