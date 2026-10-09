"""Shared-deadline cleanup for only the S08 runner's owned children and resources."""
import signal
import subprocess
import time

GRACE_SECONDS = 2.0
INTERRUPT_SECONDS = 2.0
TERMINATE_SECONDS = 2.0
RECEIPT_RESERVE_SECONDS = 0.25


def cleanup(children, streams, proxy, proxy_log, set_deadline, now=None):
    """Attempt every handle and close independently; report observed failures honestly."""
    if now is None:
        now = time.monotonic
    errors, actions = [], []
    reaped = [False]*len(children)
    cleanup_deadline = set_deadline-RECEIPT_RESERVE_SECONDS

    def error(target, operation, exception):
        """Retain exact cleanup diagnostics without preventing later cleanup."""
        errors.append({'target':target, 'operation':operation, 'error':repr(exception)})

    def wait_all(stage, deadline):
        """Use one remaining allowance, including zero, for this entire stage."""
        for index, child in enumerate(children):
            if reaped[index]:
                continue
            timeout = max(0.0, deadline-now())
            actions.append({'child':index, 'operation':stage, 'timeout':timeout, 'at':now()})
            try:
                child.wait(timeout=timeout)
                reaped[index] = child.returncode is not None
            except subprocess.TimeoutExpired as exception:
                if stage == 'reap':
                    error(index, stage, exception)
            except Exception as exception:
                error(index, stage, exception)

    def signal_all(stage):
        """Signal only unreaped owned Popen handles and continue after each error."""
        for index, child in enumerate(children):
            if reaped[index]:
                continue
            try:
                if child.poll() is not None:
                    reaped[index] = True
                    continue
                actions.append({'child':index, 'operation':stage, 'at':now()})
                if stage == 'interrupt':
                    child.send_signal(signal.SIGINT)
                elif stage == 'terminate':
                    child.terminate()
                else:
                    child.kill()
            except Exception as exception:
                error(index, stage, exception)

    # Normal exit is always attempted first. Escalation/waits are shared, not per-child budgets.
    wait_all('grace', min(now()+GRACE_SECONDS, cleanup_deadline))
    for stage, seconds in [('interrupt', INTERRUPT_SECONDS), ('terminate', TERMINATE_SECONDS)]:
        signal_all(stage)
        wait_all(stage+'_wait', min(now()+seconds, cleanup_deadline))
    signal_all('kill')
    wait_all('reap', cleanup_deadline)
    for index, child in enumerate(children):
        if not reaped[index]:
            try:
                reaped[index] = child.poll() is not None
            except Exception as exception:
                error(index, 'final_poll', exception)
        if not reaped[index]:
            error(index, 'unreaped', RuntimeError('owned child remains unreaped at deadline'))

    closed = []
    for index, stream in enumerate(streams):
        try:
            stream.close()
            closed.append(bool(stream.closed))
        except Exception as exception:
            closed.append(False)
            error('stream:'+str(index), 'close', exception)
    proxy_closed = proxy is None
    if proxy is not None:
        try:
            proxy.socket.close()
            proxy_closed = True
        except Exception as exception:
            error('proxy', 'close', exception)
    proxy_log_closed = proxy_log is None
    if proxy_log is not None:
        try:
            proxy_log.close()
            proxy_log_closed = bool(proxy_log.closed)
        except Exception as exception:
            error('proxy_log', 'close', exception)
    return {'errors':errors, 'actions':actions, 'children_reaped':reaped,
            'all_children_reaped':all(reaped), 'streams_closed':all(closed),
            'proxy_closed':proxy_closed, 'proxy_log_closed':proxy_log_closed,
            'set_deadline':set_deadline, 'cleanup_ended':now()}
