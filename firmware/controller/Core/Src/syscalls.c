/* No heap or stdio devices: diagnostics use fixed buffers and HAL UART explicitly. */
#include <errno.h>
#include <stddef.h>
#include <sys/stat.h>
void *_sbrk(ptrdiff_t increment) {
    (void)increment;
    errno = ENOMEM;
    return (void *)-1;
}
int _close(int fd) {
    (void)fd;
    errno = EBADF;
    return -1;
}
int _fstat(int fd, struct stat *st) {
    (void)fd;
    (void)st;
    errno = EBADF;
    return -1;
}
int _isatty(int fd) {
    (void)fd;
    return 0;
}
int _lseek(int fd, int position, int whence) {
    (void)fd;
    (void)position;
    (void)whence;
    errno = ESPIPE;
    return -1;
}
int _read(int fd, char *data, int length) {
    (void)fd;
    (void)data;
    (void)length;
    errno = EBADF;
    return -1;
}
int _write(int fd, const char *data, int length) {
    (void)fd;
    (void)data;
    (void)length;
    errno = EBADF;
    return -1;
}
