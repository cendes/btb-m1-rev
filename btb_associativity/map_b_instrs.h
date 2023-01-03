#define MAP_B_INSTRS "dsb  sy            \n" \
"add  x10, x10, 12  \n" \
"add  x10, x10, 4   \n" \
"add  x10, x10, 4   \n" \
"ldr x11, [x3]      \n" \
"add x10, x10, x11  \n" \
"ldr x12, [x3, #8]  \n" \
"dc  civac, x3      \n" \
"add x3,  x3, x12   \n" \
"dsb  sy            \n" \
"br   x10           \n" \
