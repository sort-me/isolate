/*
 *	Process Isolator -- Test Suite
 *
 *	(c) 2024 Sort Me <guys@sort-me.org>
 */

#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {
    // Allocate 32MB of memory
    char *mem = (char *)malloc(32 * 1024 * 1024);

    // Fill it with zeros
    for (int i = 0; i < 32 * 1024 * 1024; i++) {
        mem[i] = 0;
    }

    printf("Memory allocated and filled\n");
}