/*
 *	Process Isolator -- Test Suite
 *
 *	(c) 2024 Sort Me <guys@sort-me.org>
 */

#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv) {
    // Allocate 28MB of memory (with limit of 32MB)
    char *mem = (char *)malloc(28 * 1024 * 1024);

    // Fill it with zeros
    for (int i = 0; i < 28 * 1024 * 1024; i++) {
        mem[i] = 0;
    }

    printf("Memory allocated and filled\n");
}