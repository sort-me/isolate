#include <stdio.h>
#include <unistd.h>

const int EXCEPTED_PROCESSES_LIMIT = 50;

int main() {
    for (int i = 0; i < EXCEPTED_PROCESSES_LIMIT; i++) {
        switch (fork()) {
            case 0:
                for (;;) {
                    pause();
                }
            case -1:
                fprintf(stderr, "Failed to fork at process %d\n", i);
                if (i == (EXCEPTED_PROCESSES_LIMIT - 1)) {
                    return 0;
                } else {
                    return 1;
                }
        }
    }
    return 1;
}