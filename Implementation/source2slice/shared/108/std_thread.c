#ifdef _WIN32
  /* windows.h needs to be the top-most header usually */
# include <windows.h>
#endif
#include "std_testcase.h"
#ifdef _WIN32
# include <process.h>
#else
# include <pthread.h>
#endif
#include "std_thread.h"

struct _stdThread {
#ifdef _WIN32
    uintptr_t handle;
#else
    pthread_t handle;
#endif
    stdThreadRoutine start;
    void *args;
};

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _WIN32
static unsigned __stdcall internal_start(void *args)
#else
static void *internal_start(void *args)
#endif
{
    stdThread thread = (stdThread)args;

    thread->start(thread->args);

#ifdef _WIN32
    _endthreadex(0);
    /* dead code, but return to avoid warnings */
    return 0;
#else
    pthread_exit(NULL);
    /* dead code, but return to avoid warnings */
    return NULL;
#endif
}

int stdThreadCreate(stdThreadRoutine start, void *args, stdThread *thread)
{
#ifdef _WIN32
    uintptr_t handle;
#else
    pthread_t handle;
#endif
    stdThread my_thread;

    *thread = NULL;

    my_thread = (stdThread)malloc(sizeof(*my_thread));
    if (my_thread == NULL) {
        return 0;
    }

    my_thread->start = start;
    my_thread->args = args;

#ifdef _WIN32
    handle = _beginthreadex(NULL, 0, internal_start, my_thread, 0, NULL);
    if (handle == 0) {
        free(my_thread);
        return 0;
    }
#else
    if (0 != pthread_create(&handle, NULL, internal_start, my_thread)) {
        free(my_thread);
        return 0;
    }
#endif

    /* clearly, you cannot access _stdThread.handle from within the thread
     * itself, because initialization of this field is not synchronized w.r.t.
     * multiple threads
     */
    my_thread->handle = handle;

    *thread = my_thread;

    return 1;
}

int stdThreadJoin(stdThread thread)
{
#ifdef _WIN32
    DWORD value;

    value = WaitForSingleObject((HANDLE)thread->handle, INFINITE);
    if (value != WAIT_OBJECT_0) return 0;
#else
    void *dummy;
    if (0 != pthread_join(thread->handle, &dummy)) return 0;
#endif

    return 1;
}

int stdThreadDestroy(stdThread thread)
{
#ifdef _WIN32
    CloseHandle((HANDLE)thread->handle);
#else
#endif
    free(thread);

    return 1;
}

#ifdef __cplusplus
} /* end extern "C" */
#endif

struct _stdThreadLock {
#ifdef _WIN32
    CRITICAL_SECTION CriticalSection;
#else
    pthread_mutex_t mutex;
#endif
};

#ifdef __cplusplus
extern "C" {
#endif

int stdThreadLockCreate(stdThreadLock *lock)
{
    stdThreadLock my_lock = NULL;

    *lock = NULL;

    my_lock = (stdThreadLock)malloc(sizeof(*my_lock));
    if (my_lock == NULL) return 0;

#ifdef _WIN32
    __try {
        InitializeCriticalSection(&my_lock->CriticalSection);
    } __except (GetExceptionCode() == STATUS_NO_MEMORY) {
        free(my_lock);
        return 0;
    }
#else
    if (0 != pthread_mutex_init(&my_lock->mutex, NULL)) {
        free(lock);
        return 0;
    }
#endif

    *lock = my_lock;

    return 1;
}

void stdThreadLockAcquire(stdThreadLock lock)
{
    /* pthread_mutex's and CRITICAL_SECTIONS differ
     *
     * CRITICAL_SECTION's are recursive, meaning a thread can acquire a
     * CRITICAL_SECTION multiple times, so long as it then releases it
     * the same number of times.
     *
     * pthread_mutex's seem to be undefined with regards to recursion,
     * meaning that acquiring the same mutex twice leads to undefined
     * behavior (it could deadlock, crash, act recursively, who knows)
     *
     * Therefore, we will define multiple acquisitions of a lock in a
     * single thread as "undefined" behavior, thereby allowing us to
     * ignore the platform compatibility issues here.
     */

#ifdef _WIN32
    /* may throw an exception in Windows 2000 but documentation says to let
     * it terminate the process (i.e., don't handle it)
     */
    EnterCriticalSection(&lock->CriticalSection);
#else
    pthread_mutex_lock(&lock->mutex);
#endif
}

void stdThreadLockRelease(stdThreadLock lock)
{
    /* see comments in stdThreadLockAcquire with regards to lock
     * recursion */

#ifdef _WIN32
    LeaveCriticalSection(&lock->CriticalSection);
#else
    pthread_mutex_unlock(&lock->mutex);
#endif
}

void stdThreadLockDestroy(stdThreadLock lock)\
{
#ifdef _WIN32
    DeleteCriticalSection(&lock->CriticalSection);
#else
    pthread_mutex_destroy(&lock->mutex);
#endif
    free(lock);
}

#ifdef __cplusplus
} /* end extern "C" */
#endif
