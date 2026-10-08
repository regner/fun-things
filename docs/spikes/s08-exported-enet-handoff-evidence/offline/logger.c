
#include <stdarg.h>
#include <stdio.h>
#include <unistd.h>
static void log_record(const char *format, ...) {
    va_list args;
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
}
int main(void) {
    log_record("S08 {\"ok\":true,\"padding\":\"");
    for (int i=0; i<22000; ++i) log_record("x");
    log_record("\"}\n");
    log_record("S03 {\"event\":\"ready\"}\n");
    usleep(700000);
    log_record("S03 {\"event\":\"result\",\"ok\":false}\n");
    return 1;
}
