/*
 *	Process Isolator -- Test Suite
 *
 *	(c) 2024 Sort Me <guys@sort-me.org>
 */

#include <unistd.h>

int main(int argc, char **argv) {
    // Fork forever
    while (true) {
        fork();
    }
}