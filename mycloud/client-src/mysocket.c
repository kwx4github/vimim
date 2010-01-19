/* tcpsend function for both WinSock and Linux */

#ifdef WIN32
# include <winsock2.h>
#else
# include <sys/types.h>          /* See NOTES */
# include <sys/socket.h>
# include <arpa/inet.h>
# include <unistd.h>
#endif

#include <stdio.h>
#include <string.h>

int tcpsend(char *ret, const char *src, const char *host, unsigned short port)
{
#ifdef WIN32
    /* init winsock */
    WSADATA       wsd;
    if (WSAStartup(MAKEWORD(2,2), &wsd) != 0) {
        printf("Failed to load Winsock library!\n");
        goto error0;
    }
#endif

    /* limit the data length */
    int lensrc = strlen(src);
    if (lensrc >= BUFSIZ)
        goto error1;
    /* create the socket */
#ifdef WIN32
    SOCKET s = socket(AF_INET, SOCK_STREAM, 0);
#else
    int s = socket(PF_INET, SOCK_STREAM, 0);
#endif
    if (s < 0) 
        goto error1;
    /* assign the address */
    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof serv_addr);
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr(host);
    serv_addr.sin_port = htons(port);

    if (connect(s, (struct sockaddr *)&serv_addr, sizeof serv_addr) < 0)
        goto error2;

    if (src[lensrc-1] == '\n') {
        lensrc--;
    }
    if (send(s, src, lensrc, 0) != lensrc)
        goto error2;
    send(s, "\n", 1, 0);
    ret[0] = '\0';
    for (;;) {
        char buf[BUFSIZ];
        size_t sz = recv(s, buf, sizeof buf - 1, 0);
        if (sz <= 0)
            goto error2;
        buf[sz] = '\0';
        strcat(ret, buf);
        if (buf[sz-1] == '\n')
            break;
    }
#ifdef WIN32
    closesocket(s);
#else
    close(s);
#endif
    return 0;

error2:
#ifdef WIN32
    closesocket(s);
#else
    close(s);
#endif
error1:
#ifdef WIN32
    WSACleanup();
error0:
#endif
    ret[0] = '\0';
    return 0;
}

