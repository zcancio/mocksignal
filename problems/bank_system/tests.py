"""
Testing suite for the Bank System simulation.
============================================================
This suite uses unittest to validate the functionality of the bank system
simulation.

Author: Eric Zheng
Date: Jan 2026
"""
import unittest
import threading
import sys
import os
# Uncomment the following line to import solution implementation for testing
# from simulation_solution import InMemoryDatabase
from solution import Simulation

class TestLevel1(unittest.TestCase):
    def test_create_account(self):
        simulation = Simulation()
        self.assertEqual(simulation.create_account(1, "acc1"), True)
        self.assertEqual(simulation.create_account(2, "acc1"), False)
        self.assertEqual(simulation.create_account(3, "acc2"), True)

    def test_deposit(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        self.assertEqual(simulation.deposit(2, "acc1", 500), 500)
        self.assertEqual(simulation.deposit(3, "acc1", 300), 800)
        self.assertEqual(simulation.deposit(4, "non_existent", 100), None)

    def test_transfer(self):
        simulation = Simulation()
        self.assertEqual(simulation.create_account(1, "acc1"), True)
        self.assertEqual(simulation.create_account(2, "acc2"), True)
        self.assertEqual(simulation.deposit(3, "acc1", 1000), 1000)
        self.assertEqual(simulation.transfer(4, "acc1", "acc2", 300), 700)
        # Insufficient funds
        self.assertEqual(simulation.transfer(5, "acc1", "acc2", 800), None)
        # Non-existent account
        self.assertEqual(simulation.transfer(6, "acc1", "non_existent", 100), None)
        # Transfer to self
        self.assertEqual(simulation.transfer(7, "acc1", "acc1", 100), None)

    def test_1(self):
        simulation = Simulation()
        self.assertEqual(simulation.create_account(1, "account1"), True)
        self.assertEqual(simulation.create_account(2, "account1"), False)
        self.assertEqual(simulation.create_account(3, "account2"), True)
        self.assertEqual(simulation.deposit(4, "non_existent", 100), None)
        self.assertEqual(simulation.deposit(5, "account1", 2700), 2700)
        self.assertEqual(simulation.transfer(6, "account1", "account2", 2701), None)
        self.assertEqual(simulation.transfer(7, "account1", "account2", 200), 2500)

    def test_2(self):
        simulation = Simulation()
        self.assertEqual(simulation.create_account(1, "A"), True)
        self.assertEqual(simulation.create_account(2, "B"), True)
        self.assertEqual(simulation.deposit(3, "A", 500), 500)
        self.assertEqual(simulation.transfer(4, "A", "B", 300), 200)
        self.assertEqual(simulation.deposit(5, "B", 200), 500)
        self.assertEqual(simulation.transfer(6, "B", "A", 600), None)
        self.assertEqual(simulation.transfer(7, "B", "A", 400), 100)

    def test_3(self):
        simulation = Simulation()
        self.assertEqual(simulation.create_account(1, "X"), True)
        self.assertEqual(simulation.deposit(2, "X", 1000), 1000)
        self.assertEqual(simulation.create_account(3, "Y"), True)
        self.assertEqual(simulation.transfer(4, "X", "Y", 500), 500)
        self.assertEqual(simulation.transfer(5, "Y", "X", 600), None)
        self.assertEqual(simulation.deposit(6, "Y", 300), 800)
        self.assertEqual(simulation.transfer(7, "Y", "X", 400), 400)

class TestLevel2(unittest.TestCase):
    def test_top_spenders_empty(self):
        simulation = Simulation()
        top_0 = simulation.top_spenders(1, 0)
        self.assertEqual(top_0, [])
        top_5 = simulation.top_spenders(2, 5)
        self.assertEqual(top_5, [])

    def test_top_spenders_single_account_less_than_n(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        simulation.create_account(3, "acc2")
        simulation.transfer(4, "acc1", "acc2", 500)
        top_1 = simulation.top_spenders(5, 1)
        self.assertEqual(top_1, ["acc1(500)"])

    def test_top_spenders_tie(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.create_account(2, "acc2")
        simulation.create_account(3, "acc3")
        simulation.deposit(4, "acc1", 1000)
        simulation.deposit(5, "acc2", 1500)
        simulation.deposit(6, "acc3", 1200)
        simulation.transfer(8, "acc2", "acc3", 500)  # acc2 outgoing: 500
        simulation.transfer(7, "acc1", "acc2", 500)  # acc1 outgoing: 500
        simulation.transfer(9, "acc3", "acc1", 300)  # acc3 outgoing: 300
        top_2 = simulation.top_spenders(10, 3)
        self.assertEqual(top_2, ["acc1(500)", "acc2(500)", "acc3(300)"])

class TestLevel3(unittest.TestCase):
    def test_pay_no_account_id(self):
        simulation = Simulation()
        self.assertEqual(simulation.pay(1, "non_existent", 100), None)
        self.assertEqual(simulation.get_payment_status(2, "non_existent", "payment1"), None)

    def test_pay_insufficient_funds(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 100)
        self.assertEqual(simulation.pay(3, "acc1", 200), None)

    def test_pay_top_spenders(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        payment_id1 = simulation.pay(3, "acc1", 500)
        self.assertEqual(payment_id1, "payment1")
        payment_id2 = simulation.pay(4, "acc1", 300)
        self.assertEqual(payment_id2, "payment2")
        simulation.create_account(5, "acc2")
        simulation.deposit(6, "acc2", 800)
        simulation.transfer(7, "acc2", "acc1", 200)
        top_1 = simulation.top_spenders(8, 2)
        self.assertEqual(top_1, ["acc1(800)", "acc2(200)"])

    def test_payment_status_non_existent_account(self):
        simulation = Simulation()
        self.assertEqual(simulation.get_payment_status(1, "non_existent", "payment1"), None)

    def test_payment_status_non_existent_payment(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        self.assertEqual(simulation.get_payment_status(2, "acc1", "payment1"), None)

    def test_payment_status_inconsistent_accountid_and_paymentid(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        payment_id = simulation.pay(3, "acc1", 500)
        self.assertEqual(payment_id, "payment1")
        # Create a different account
        simulation.create_account(4, "acc2")
        # Querying payment status with wrong account_id
        self.assertEqual(simulation.get_payment_status(4, "acc2", payment_id), None)

    def test_pay_cashback_and_status(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        payment_id = simulation.pay(3, "acc1", 500)
        self.assertEqual(payment_id, "payment1")
        # Before cashback time
        status_in_progress = simulation.get_payment_status(4, "acc1",
                                                           payment_id)
        self.assertEqual(status_in_progress, "IN_PROGRESS")
        status_before_cashback = simulation.get_payment_status(26*3600,
                                                               "acc1",
                                                               payment_id)
        # After cashback time (Exactly 24 hours after the payment)
        status_after_cashback = simulation.get_payment_status(24 * 60 * 60 * 1000 + 3,
                                                              "acc1",
                                                              payment_id)
        self.assertEqual(status_after_cashback, "CASHBACK_RECEIVED")
        # Check balance after cashback
        final_balance = simulation.deposit(28 * 60 * 60 * 1000,
                                            "acc1",
                                            0)  # deposit 0 to get current balance
        self.assertEqual(final_balance, 1000 - 500 + 10)  # 2% of 500 is 10

class TestLevel4(unittest.TestCase):
    def test_account_id_1_not_exist(self):
        simulation = Simulation()
        simulation.create_account(1, "acc2")
        self.assertEqual(simulation.merge_accounts(2, "acc1", "acc2"), False)

    def test_account_id_2_not_exist(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        self.assertEqual(simulation.merge_accounts(2, "acc1", "acc2"), False)

    def test_merge_cashback(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        payment_id = simulation.pay(3, "acc1", 500)
        self.assertIsNot(payment_id, None)
        simulation.create_account(4, "acc2")
        simulation.merge_accounts(5, "acc2", "acc1")
        status_acc2 = simulation.get_payment_status(6, "acc2", payment_id)
        self.assertEqual(status_acc2, "IN_PROGRESS")
        status_after_cashback = simulation.get_payment_status(24 * 60 * 60 * 1000 + 3,
                                                              "acc2",
                                                                payment_id)
        self.assertEqual(status_after_cashback, "CASHBACK_RECEIVED")
        self.assertEqual(simulation.deposit(24 * 60 * 60 * 1000 + 5, "acc2", 0), 510)

    def test_merge_top_spender(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        simulation.pay(3, "acc1", 500)
        simulation.create_account(4, "acc2")
        simulation.deposit(5, "acc2", 2000)
        simulation.pay(6, "acc2", 800)
        simulation.merge_accounts(7, "acc1", "acc2")
        top_1 = simulation.top_spenders(8, 1)
        self.assertEqual(top_1, ["acc1(1300)"])  # acc1 now has acc2's outgoing too

    def test_cashback(self):
        simulation = Simulation()
        simulation.create_account(1, "acc1")
        simulation.deposit(2, "acc1", 1000)
        simulation.pay(3, "acc1", 300)
        self.assertEqual(simulation.get_balance(4, "acc1", 3), 700)
        self.assertEqual(simulation.get_balance(24 * 60 * 60 * 1000 + 5,
                                      "acc1",
                                      24 * 60 * 60 * 1000 + 2), 700)
        self.assertEqual(simulation.get_balance(24 * 60 * 60 * 1000 + 5,
                                      "acc1",
                                      24 * 60 * 60 * 1000 + 3), 706)


class TestLevel5(unittest.TestCase):
    """Level 5 — concurrency: every public method must be thread-safe."""

    def test_concurrent_deposits_to_same_account(self):
        """100 threads, each depositing $10 to the same account.
        Final balance must be exactly $1000, not $990 or $1010."""
        sim = Simulation()
        sim.create_account(0, "acct1")

        def worker(i):
            sim.deposit(i, "acct1", 10)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        final = sim.get_balance(1000, "acct1", 1000)
        self.assertEqual(final, 1000)

    def test_concurrent_deposits_different_accounts(self):
        """100 threads each create and deposit to a unique account."""
        sim = Simulation()

        def worker(i):
            aid = f"acct{i}"
            sim.create_account(i, aid)
            sim.deposit(i, aid, 50)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Every account should have exactly 50
        for i in range(100):
            self.assertEqual(sim.get_balance(1000, f"acct{i}", 1000), 50)

    def test_total_money_conserved(self):
        """Transfers between two accounts must conserve total money.
        Even with races, total = initial_a + initial_b at the end."""
        sim = Simulation()
        sim.create_account(0, "a")
        sim.create_account(0, "b")
        sim.deposit(0, "a", 10000)
        sim.deposit(0, "b", 10000)

        def transfer_a_to_b(i):
            sim.transfer(i, "a", "b", 1)

        def transfer_b_to_a(i):
            sim.transfer(i, "b", "a", 1)

        threads = []
        for i in range(200):
            threads.append(threading.Thread(target=transfer_a_to_b, args=(i,)))
            threads.append(threading.Thread(target=transfer_b_to_a, args=(i,)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        bal_a = sim.get_balance(1000, "a", 1000)
        bal_b = sim.get_balance(1000, "b", 1000)
        self.assertEqual(bal_a + bal_b, 20000,
                         f"money not conserved: a={bal_a}, b={bal_b}")

    def test_concurrent_deposits_and_reads(self):
        """Readers and writers concurrent. No crashes, final state correct."""
        sim = Simulation()
        sim.create_account(0, "acct1")
        sim.deposit(0, "acct1", 1000)

        def depositor(i):
            for _ in range(10):
                sim.deposit(i, "acct1", 1)

        def reader(i):
            for _ in range(10):
                sim.get_balance(i, "acct1", i)

        threads = []
        for i in range(20):
            threads.append(threading.Thread(target=depositor, args=(i,)))
        for i in range(20):
            threads.append(threading.Thread(target=reader, args=(i,)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 20 depositors * 10 deposits = 200 added on top of 1000
        final = sim.get_balance(1000, "acct1", 1000)
        self.assertEqual(final, 1200)


if __name__ == "__main__":
    unittest.main()
