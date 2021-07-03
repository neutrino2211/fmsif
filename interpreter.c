#include <stdio.h>
#include <malloc.h>
// #define LEN(code) sizeof(code)/sizeof(int)

int BYTECODE_size();
int* BYTECODE_exporter();

void slice(int* c, int* in, int start, int end){
    // int* r = malloc((end-start)*sizeof(int));

    for(int i=start; i<end; i++){
        printf("%i, %i\n", i-start, c[i]);
        in[i-start] = c[i];
    }
}

size_t LEN(int arr[]){
    return sizeof(arr)/sizeof(int);
}

unsigned misc_len(void** l){
    unsigned i = 0;
    for(i;l[i]!=0;i++);
    return i;
}

void main(int argc, char* argv){
    // printf("Starting....\n");
    int* code = BYTECODE_exporter();

    int magic_bytes[4] = {code[0], code[1], code[2], code[3]}, 
        major_ver = code[4], 
        minor_ver = code[5], 
        patch_ver = code[6], 
        other_ver = code[7], 
        func_pointer = code[8], 
        code_info_pointer = code[9],
        mem_start = code[8+code_info_pointer],
        mem_size = code[8+1+code_info_pointer],
        code_start = code[8+2+code_info_pointer],
        exe_start = code[code_start];
        int code_size = BYTECODE_size();
        int exe_size = code_size-exe_start;
    // printf("DONE\n");
    // printf("CODE SSIZE: %d\n", exe_size);
    printf(
        "FILE INFO\nversion: %d.%d.%d.%d\nfunction section: 0x%x\nprogram section: 0x%x\nmemory section: 0x%x\nmemory size: 0x%x\ncode section: 0x%x\n"
        ,major_ver, minor_ver, patch_ver, other_ver, func_pointer
        ,code_info_pointer, mem_start, mem_size, code_start, "\n");


    // printf("%s\n",);
    // printf("CODE SSIZE: %d\n", exe_size);
    int exe[exe_size];
    printf("CODE SSIZE: %d, %i, %i\n", code[code_start], code_info_pointer, code_start);
    printf("\nExecuting...\n\n");
    slice(code, exe ,exe_start, exe_size-1);
    printf("CODE SIZE: %d\n", sizeof(exe)/4);

}