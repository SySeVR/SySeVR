#ifndef _STD_THREAD_H
#define _STD_THREAD_H

typedef struct _stdThread *stdThread;
typedef struct _stdThreadLock *stdThreadLock;

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*stdThreadRoutine)(void *args);

/* All of these return positive ('true') on success, zero ('false') on failure */
int stdThreadCreate(stdThreadRoutine start, void *args, stdThread *thread);
int stdThreadJoin(stdThread thread);
int stdThreadDestroy(stdThread thread);

int stdThreadLockCreate(stdThreadLock *lock);
void stdThreadLockAcquire(stdThreadLock lock);
void stdThreadLockRelease(stdThreadLock lock);
void stdThreadLockDestroy(stdThreadLock lock);

#ifdef __cplusplus
};
#endif

#endif
