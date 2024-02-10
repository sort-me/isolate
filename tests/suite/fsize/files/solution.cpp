/*
 *	Process Isolator -- Test Suite
 *
 *	(c) 2024 Sort Me <guys@sort-me.org>
 */

#include <cstdio>

const int allowedFileSize = 256 * 1024; // 256KB

int main() {
    setbuf(stdout, NULL);

    // exact file size, should be allowed
    FILE *file = fopen("file1.txt", "w");
    for (int i = 0; i < allowedFileSize; i++) {
        fputc('a', file);
    }
    fclose(file);

    // exact file size again, should be allowed
    FILE *file2 = fopen("file2.txt", "w");
    for (int i = 0; i < allowedFileSize; i++) {
        fputc('a', file2);
    }
    fclose(file2);

    fprintf(stdout, "OK\n");

    // file size is too big, should be denied
    FILE *file3 = fopen("file3.txt", "w");
    setbuf(file3, NULL);

    for (int i = 0; i < allowedFileSize; i++) {
        fputc('a', file3);
    }

    fputc('a', file3); // should panic here

    fprintf(stdout, ", but this should not be printed\n");

    fclose(file3); // or here

    return 0;
}