# Autores: Javier Rocafull Cabello y Jaime Rodriguez Martin-Palomino
import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_cluster, get_session, init_schema, seed_screenings
from reservation import ReservationSystem


def print_menu():
    print("\n===== CINEMA RESERVATION SYSTEM =====")
    print("1. View available screenings")
    print("2. Make a reservation")
    print("3. View my reservations")
    print("4. View all reservations")
    print("5. Update a reservation")
    print("6. Cancel a reservation")
    print("7. Cancel multiple reservations")
    print("8. Initialize / reset database")
    print("9. Help")
    print("0. Exit")
    print("========================================")


def main():
    cluster = None
    try:
        cluster = get_cluster()
        session = get_session(cluster)
    except Exception as e:
        print(f"Could not connect to Cassandra. Make sure the nodes are running.\n{e}")
        input("Press Enter to exit...")
        return

    rs = ReservationSystem(session)

    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            rs.list_screenings()

        elif choice == "2":
            movie = input("Movie name: ").strip()
            time_str = input("Show time (YYYY-MM-DD HH:MM:SS): ").strip()
            seat = int(input("Seat number: ").strip())
            customer = input("Your name: ").strip()
            ok, msg = rs.make_reservation(movie, time_str, seat, customer)
            print(f"  {msg}")

        elif choice == "3":
            name = input("Your name: ").strip()
            rs.view_reservations(customer_name=name)

        elif choice == "4":
            rs.view_all_reservations_with_customer()

        elif choice == "5":
            rid = uuid.UUID(input("Reservation ID to update: ").strip())
            seat_input = input("New seat (leave empty to keep): ").strip()
            new_seat = int(seat_input) if seat_input else None
            ok, msg = rs.update_reservation(rid, new_seat_number=new_seat)
            print(f"  {msg}")

        elif choice == "6":
            rid = uuid.UUID(input("Reservation ID to cancel: ").strip())
            ok, msg = rs.cancel_reservation(rid)
            print(f"  {msg}")

        elif choice == "7":
            ids_str = input("IDs separated by commas: ").strip()
            ids = [uuid.UUID(x.strip()) for x in ids_str.split(",")]
            results = rs.cancel_multiple(ids)
            for rid, ok, msg in results:
                print(f"  {rid}: {msg}")

        elif choice == "8":
            confirm = input("This will delete all data. Continue? (y/n): ").strip().lower()
            if confirm == "y":
                init_schema(session)
                seed_screenings(session)

        elif choice == "9":
            print("\nHELP:")
            print("  - Make sure the 3 Cassandra nodes are running with Docker")
            print("  - Use 'start_nodes.bat' to start the nodes")
            print("  - Wait about 60s for the cluster to initialize")
            print("  - All operations use LWT for consistency")

        elif choice == "0":
            print("Exiting...")
            break

        else:
            print("Invalid option")

    if cluster:
        cluster.shutdown()


if __name__ == "__main__":
    main()
