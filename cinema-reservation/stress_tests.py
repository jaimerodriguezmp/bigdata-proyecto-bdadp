# Autores: Javier Rocafull Cabello y Jaime Rodriguez Martin-Palomino
import sys
import os
import uuid
import time
import threading
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_cluster, get_session, init_schema, seed_screenings, KEYSPACE
from reservation import ReservationSystem


STRESS_KEYSPACE = "cinema_stress_test"


def reset_seats(session, count=100):
    for i in range(1, count + 1):
        for _ in range(3):
            try:
                session.execute(
                    "INSERT INTO stress_seats (seat_id, status, customer, reservation_id, created_at) VALUES (%s, 'available', null, null, null)",
                    (i,)
                )
                break
            except Exception:
                time.sleep(0.5)


def init_stress_schema(session):
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {STRESS_KEYSPACE}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': 2 }}
    """)
    session.set_keyspace(STRESS_KEYSPACE)

    session.execute("""
        CREATE TABLE IF NOT EXISTS stress_seats (
            seat_id int PRIMARY KEY,
            status text,
            customer text,
            reservation_id UUID,
            created_at timestamp
        )
    """)

    reset_seats(session, 100)
    print("  stress_seats table initialized with 100 seats.")


def stress1_same_request():
    print("\n=== STRESS TEST 1: Same client, same quick request ===")
    time.sleep(1)
    cluster = get_cluster()
    session = get_session(cluster)
    session.set_keyspace(STRESS_KEYSPACE)
    reset_seats(session, 100)

    seat = 1
    successes = 0
    threads = []
    lock = threading.Lock()

    def try_book(t_id):
        nonlocal successes
        try:
            s = get_session(cluster)
            s.set_keyspace(STRESS_KEYSPACE)
            time.sleep(random.uniform(0, 0.1))
            rid = uuid.uuid4()
            now = datetime.now()
            result = s.execute("""
                UPDATE stress_seats SET status = 'booked', customer = 'stress1',
                    reservation_id = %s, created_at = %s
                WHERE seat_id = %s IF status = 'available'
            """, (rid, now, seat))
            if result.one().applied:
                with lock:
                    successes += 1
                print(f"  Thread-{t_id}: SUCCESSFUL reservation seat {seat}")
            else:
                print(f"  Thread-{t_id}: FAILED reservation seat {seat} (already occupied)")
            s.shutdown()
        except Exception as e:
            if "timed out" in str(e):
                print(f"  Thread-{t_id}: FAILED reservation seat {seat} (CAS timed out)")
            else:
                print(f"  Thread-{t_id}: Error: {e}")

    for i in range(20):
        t = threading.Thread(target=try_book, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"  Result: {successes} successful reservations out of 20 attempts (should be 1)")
    cluster.shutdown()


def stress2_random_clients():
    print("\n=== STRESS TEST 2: Random simultaneous clients ===")
    time.sleep(1)
    cluster = get_cluster()
    session = get_session(cluster)
    session.set_keyspace(STRESS_KEYSPACE)
    reset_seats(session, 100)
    cluster.shutdown()

    total_ops = 50
    results = {"success": 0, "fail": 0, "errors": 0}
    lock = threading.Lock()

    def random_client(cid):
        try:
            c = get_cluster()
            s = get_session(c)
            s.set_keyspace(STRESS_KEYSPACE)
            for _ in range(5):
                seat = random.randint(1, 100)
                rid = uuid.uuid4()
                now = datetime.now()
                try:
                    result = s.execute("""
                        UPDATE stress_seats SET status = 'booked', customer = %s,
                            reservation_id = %s, created_at = %s
                        WHERE seat_id = %s IF status = 'available'
                    """, (f"client-{cid}", rid, now, seat))
                    if result.one().applied:
                        with lock:
                            results["success"] += 1
                    else:
                        with lock:
                            results["fail"] += 1
                except Exception:
                    with lock:
                        results["fail"] += 1
                time.sleep(random.uniform(0, 0.1))
            s.shutdown()
            c.shutdown()
        except Exception as e:
            with lock:
                results["errors"] += 1
            print(f"  Error client-{cid}: {e}")

    threads = []
    for i in range(10):
        t = threading.Thread(target=random_client, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"  Result: {results['success']} successful, {results['fail']} failed, {results['errors']} errors")


def stress3_occupy_all():
    print("\n=== STRESS TEST 3: Immediate occupation of ALL seats by 2 clients ===")
    time.sleep(1)
    cluster = get_cluster()
    session = get_session(cluster)
    session.set_keyspace(STRESS_KEYSPACE)
    reset_seats(session, 100)
    cluster.shutdown()

    client1_seats = []
    client2_seats = []
    lock = threading.Lock()

    def client_worker(name, seat_list):
        try:
            c = get_cluster()
            s = get_session(c)
            s.set_keyspace(STRESS_KEYSPACE)
            for seat in range(1, 101):
                rid = uuid.uuid4()
                now = datetime.now()
                try:
                    result = s.execute("""
                        UPDATE stress_seats SET status = 'booked', customer = %s,
                            reservation_id = %s, created_at = %s
                        WHERE seat_id = %s IF status = 'available'
                    """, (name, rid, now, seat))
                    if result.one().applied:
                        with lock:
                            seat_list.append(seat)
                except Exception:
                    pass
                time.sleep(random.uniform(0, 0.02))
            s.shutdown()
            c.shutdown()
        except Exception as e:
            print(f"  Error {name}: {e}")

    t1 = threading.Thread(target=client_worker, args=("Client-1", client1_seats))
    t2 = threading.Thread(target=client_worker, args=("Client-2", client2_seats))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    total1 = len(client1_seats)
    total2 = len(client2_seats)
    print(f"  Client-1 got: {total1} seats")
    print(f"  Client-2 got: {total2} seats")
    print(f"  Total booked: {total1 + total2} (should be 100, no overlap)")
    overlap = set(client1_seats) & set(client2_seats)
    if overlap:
        print(f"  ERROR: Overlap in seats: {overlap}")
    else:
        print("  OK: No seat overlap")


def stress4_cancel_and_occupy():
    print("\n=== STRESS TEST 4: Constant cancellations and occupation ===")
    time.sleep(1)
    cluster = get_cluster()
    session = get_session(cluster)
    session.set_keyspace(STRESS_KEYSPACE)
    reset_seats(session, 100)
    cluster.shutdown()

    stop_event = threading.Event()
    lock = threading.Lock()
    booked_seats = set()

    def occupier(name):
        try:
            c = get_cluster()
            s = get_session(c)
            s.set_keyspace(STRESS_KEYSPACE)
            while not stop_event.is_set():
                seat = random.randint(1, 100)
                rid = uuid.uuid4()
                now = datetime.now()
                try:
                    result = s.execute("""
                        UPDATE stress_seats SET status = 'booked', customer = %s,
                            reservation_id = %s, created_at = %s
                        WHERE seat_id = %s IF status = 'available'
                    """, (name, rid, now, seat))
                    if result.one().applied:
                        with lock:
                            booked_seats.add(seat)
                except Exception:
                    pass
                time.sleep(0.03)
            s.shutdown()
            c.shutdown()
        except:
            pass

    def canceller():
        try:
            c = get_cluster()
            s = get_session(c)
            s.set_keyspace(STRESS_KEYSPACE)
            while not stop_event.is_set():
                with lock:
                    if booked_seats:
                        seat = random.choice(list(booked_seats))
                    else:
                        seat = None
                if seat is not None:
                    try:
                        result = s.execute("""
                            UPDATE stress_seats SET status = 'available', customer = null,
                                reservation_id = null, created_at = null
                            WHERE seat_id = %s IF status = 'booked'
                        """, (seat,))
                        if result.one().applied:
                            with lock:
                                booked_seats.discard(seat)
                    except:
                        pass
                time.sleep(0.05)
            s.shutdown()
            c.shutdown()
        except:
            pass

    threads = []
    for i in range(3):
        t = threading.Thread(target=occupier, args=(f"Occupier-{i}",))
        threads.append(t)
        t.start()

    for i in range(2):
        t = threading.Thread(target=canceller)
        threads.append(t)
        t.start()

    time.sleep(10)
    stop_event.set()
    for t in threads:
        t.join()

    print(f"  Finished 10 seconds of concurrent operations")
    print(f"  Currently booked seats: {len(booked_seats)}")


def stress5_mass_cancel():
    print("\n=== STRESS TEST 5: Mass cancellation of many reservations ===")
    time.sleep(1)
    cluster = get_cluster()
    session = get_session(cluster)
    session.set_keyspace(STRESS_KEYSPACE)
    for i in range(1, 1001):
        for _ in range(3):
            try:
                session.execute(
                    "INSERT INTO stress_seats (seat_id, status, customer, reservation_id, created_at) "
                    "VALUES (%s, 'booked', 'mass_client', %s, %s)",
                    (i, uuid.uuid4(), datetime.now())
                )
                break
            except Exception:
                time.sleep(0.5)
    cluster.shutdown()

    print("  1000 seats booked. Cancelling in parallel...")
    lock = threading.Lock()
    cancelled = 0
    errors = 0

    def cancel_worker(start, end):
        nonlocal cancelled, errors
        try:
            c = get_cluster()
            s = get_session(c)
            s.set_keyspace(STRESS_KEYSPACE)
            for seat in range(start, end + 1):
                for retry in range(5):
                    try:
                        result = s.execute("""
                            UPDATE stress_seats SET status = 'available', customer = null,
                                reservation_id = null, created_at = null
                            WHERE seat_id = %s IF status = 'booked'
                        """, (seat,))
                        if result.one().applied:
                            with lock:
                                cancelled += 1
                        break
                    except Exception:
                        time.sleep(0.1)
                else:
                    with lock:
                        errors += 1
                time.sleep(0.01)
            s.shutdown()
            c.shutdown()
        except Exception as e:
            with lock:
                errors += 1
            print(f"  Error in range {start}-{end}: {e}")

    threads = []
    batch_size = 200
    for i in range(0, 1000, batch_size):
        t = threading.Thread(target=cancel_worker, args=(i + 1, min(i + batch_size, 1000)))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"  Cancelled: {cancelled} / 1000 | Errors: {errors}")


def main():
    print("===== STRESS TESTS =====")
    print("Connecting to Cassandra...")
    cluster = None
    for attempt in range(5):
        try:
            cluster = get_cluster()
            session = get_session(cluster)
            init_stress_schema(session)
            cluster.shutdown()
            cluster = None
            break
        except Exception as e:
            if cluster:
                try:
                    cluster.shutdown()
                except:
                    pass
                cluster = None
            if attempt < 4:
                print(f"  Retrying connection ({attempt + 1}/5)...")
                time.sleep(3)
            else:
                print(f"Connection error: {e}")
                input("Press Enter to exit...")
                return

    while True:
        print("\n--- SELECT A STRESS TEST ---")
        print("1. Stress Test 1: Same quick request")
        print("2. Stress Test 2: Random simultaneous clients")
        print("3. Stress Test 3: Total occupation by 2 clients")
        print("4. Stress Test 4: Constant cancellations and occupation")
        print("5. Stress Test 5: Mass cancellation")
        print("0. Exit")
        choice = input("Option: ").strip()

        if choice == "1":
            stress1_same_request()
        elif choice == "2":
            stress2_random_clients()
        elif choice == "3":
            stress3_occupy_all()
        elif choice == "4":
            stress4_cancel_and_occupy()
        elif choice == "5":
            stress5_mass_cancel()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
