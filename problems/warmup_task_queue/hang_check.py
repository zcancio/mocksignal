"""
Hang check — runs in ~3 seconds, dumps thread stacks, exits.

This is a deliberate deadlock to confirm:
1. faulthandler works on your machine
2. You can read the dump and identify the stuck line

Expected output: a dump showing two threads, both paused inside the
transfer function. That's the lock-ordering deadlock signature.

If you can read the dump and identify the bug in under 30 seconds,
your hang-debugging muscle is warm.
"""
import faulthandler
import threading
import time

faulthandler.dump_traceback_later(2, exit=True)


class Account:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.lock = threading.Lock()


def transfer(source, target, amount):
    with source.lock:
        time.sleep(0.05)
        with target.lock:
            source.balance -= amount
            target.balance += amount


if __name__ == "__main__":
    alice = Account("alice", 1000)
    bob = Account("bob", 1000)

    def t1():
        transfer(alice, bob, 1)

    def t2():
        transfer(bob, alice, 1)

    th1 = threading.Thread(target=t1, name="AliceToBob")
    th2 = threading.Thread(target=t2, name="BobToAlice")
    th1.start()
    th2.start()
    th1.join()
    th2.join()
