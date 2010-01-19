#ifdef WIN32
# include <wininet.h>
#else
/* do_geturl not supported in linux */
#endif

#include <stdio.h>
#include <string.h>
#include "mycloud.h"
#include "cdecode.h"
#include "cencode.h"

char buffer1[8192];
char buffer2[8192];

char *do_geturl(const char *url)
{
    char *geturl = buffer2;

#ifndef WIN32
    if (strcmp(url, "__isvalid") == 0) {
        strcpy(geturl, "False");
        return geturl;
    }
#else
    if (strcmp(url, "__isvalid") == 0) {
        strcpy(geturl, "True");
        return geturl;
    }
    HINTERNET hInet = InternetOpen(NULL,INTERNET_OPEN_TYPE_PRECONFIG,NULL,NULL,0);
    if (hInet == NULL)
        goto myerror0;

    HINTERNET hUrl = InternetOpenUrl(hInet,url,NULL,0,0,0);
    if (hUrl == NULL)
        goto myerror1;
    geturl[0] = '\0';
    for (;;) {
        char buf[BUFSIZ];
        DWORD len;
        BOOL ret = InternetReadFile(hUrl, buf, sizeof buf - 1, &len);
        if (ret == FALSE)
            goto myerror2;
        if (len == 0)
            break;
        buf[len] = '\0';
        strcat(geturl, buf);
    }

    InternetCloseHandle(hUrl);
    InternetCloseHandle(hInet);
    return geturl;

myerror2:
    InternetCloseHandle(hUrl);
myerror1:
    InternetCloseHandle(hInet);
myerror0:
#endif
    geturl[0] = '\0';
    return geturl;
}

/* unquote the %xx url quote */
char *do_unquote(const char *src)
{
    char *unquote = buffer1;
    size_t i;
    const char *p = src;
    for (i = 0; p[0] != '\0'; i++) {
        if (p[0] == '%') {
            unsigned int x = 0x20;
            int ret = sscanf(p+1, "%02X", &x);
            if (ret != 1) {
                unquote[i] = '%';
                p ++;
            } else {
                unquote[i] = x & 0xff;
                p += 3;
            }
        } else {
            unquote[i] = *p;
            p ++;
        }
    }
    unquote[i] = '\0';
    return unquote;
}

int base64_encode(char *to, const char *from)
{
    base64_encodestate state;

    base64_init_encodestate(&state);
    to[0] = '\0';
    int codelength1 = base64_encode_block(from, strlen(from), to, &state);
    int codelength2 = base64_encode_blockend(to+codelength1, &state);
    to[codelength1+codelength2] = '\0';

    return codelength1+codelength2;
}

int base64_decode(char *to, const char *from)
{
    base64_decodestate state;

    base64_init_decodestate(&state);
    to[0] = '\0';

    int plainlength = base64_decode_block(from, strlen(from), to, &state);

    return plainlength;
}

char *do_getlocal(const char *keyb)
{
    char *getlocal = buffer1;
    char *temp = buffer2;
    char host[16];
    strcpy(temp, keyb);
    char *space = strstr(temp, " ");

    if (space == NULL) {
        strcpy(host, "127.0.0.1");
        space = temp;
    } else {
        space[0] = '\0';
        strncpy(host, keyb, 16);
        host[15] = '\0';
        space++;
    }

    base64_encode(getlocal, space);
    tcpsend(temp, getlocal, host, 10007);
    base64_decode(getlocal, temp);

    return getlocal;
}

char *do_test(const char *dummy)
{
    static char result[8];
    static int i = 0;
    i++;
    sprintf(result, "%d", i);
    return result;
}

