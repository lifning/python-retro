#include <stdio.h>
#include <stdarg.h>
#include "libretro.h"

typedef void (*wrapped_retro_log_print_t)(enum retro_log_level level, const char* msg);

static wrapped_retro_log_print_t g_wrapped_log_cb;

void retro_log_snprintf(enum retro_log_level level, const char* fmt, ...)
{
    char msg[4096];

    va_list args;
    va_start(args, fmt);
    vsnprintf(msg, sizeof(msg), fmt, args);
    va_end(args);

    g_wrapped_log_cb(level, msg);
}

void handle_env_get_log_interface(
    struct retro_log_callback *retro_cb,
    wrapped_retro_log_print_t wrapped_cb)
{
    g_wrapped_log_cb = wrapped_cb;
    retro_cb->log = retro_log_snprintf;
}
