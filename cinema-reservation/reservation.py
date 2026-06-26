# Autores: Javier Rocafull Cabello y Jaime Rodriguez Martin-Palomino
import uuid
from datetime import datetime


class ReservationSystem:
    def __init__(self, session):
        self.session = session
        self.session.set_keyspace("cinema_reservations")

    def list_screenings(self):
        rows = self.session.execute("SELECT DISTINCT movie_name, show_time, screen_number, total_seats FROM screenings ALLOW FILTERING")
        print("\n--- AVAILABLE SCREENINGS ---")
        for row in rows:
            print(f"  Movie: {row.movie_name} | Screen: {row.screen_number} | "
                  f"Time: {row.show_time} | Total seats: {row.total_seats}")
        print()

    def get_available_seats(self, movie_name, show_time):
        total = self.session.execute(
            "SELECT total_seats FROM screenings WHERE movie_name = %s AND show_time = %s ALLOW FILTERING",
            (movie_name, show_time)
        ).one()
        if not total:
            return 0, set()
        total_seats = total.total_seats
        booked = self.session.execute(
            "SELECT seat_number FROM reservations WHERE movie_name = %s AND show_time = %s AND status = 'booked'",
            (movie_name, show_time)
        )
        booked_seats = {row.seat_number for row in booked}
        return total_seats, booked_seats

    def make_reservation(self, movie_name, show_time, seat_number, customer_name):
        rid = uuid.uuid4()
        now = datetime.now()
        total, booked = self.get_available_seats(movie_name, show_time)
        if seat_number < 1 or seat_number > total:
            return False, f"Seat {seat_number} invalid (1-{total})"
        if seat_number in booked:
            return False, f"Seat {seat_number} is already booked"
        try:
            self.session.execute("""
                INSERT INTO reservations (movie_name, show_time, screen_number, seat_number,
                                          customer_name, status, reservation_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (movie_name, show_time, 1, seat_number, customer_name, "booked", rid, now))
            return True, f"Reservation successful. ID: {rid}"
        except Exception as e:
            return False, f"Error making reservation: {e}"

    def update_reservation(self, reservation_id, new_seat_number=None, new_movie=None, new_time=None):
        row = self.session.execute(
            "SELECT movie_name, show_time, seat_number, customer_name, status FROM reservations WHERE reservation_id = %s ALLOW FILTERING",
            (reservation_id,)
        ).one()
        if not row:
            return False, "Reservation not found"
        if row.status != "booked":
            return False, "Reservation was already cancelled"
        movie = new_movie or row.movie_name
        show_time = new_time or row.show_time
        seat = new_seat_number or row.seat_number
        old_seat = row.seat_number
        if new_seat_number and new_seat_number != old_seat:
            _, booked = self.get_available_seats(movie, show_time)
            if new_seat_number in booked:
                return False, "The new seat is already occupied"
        self.cancel_reservation(reservation_id)
        return self.make_reservation(movie, show_time, seat, row.customer_name)

    def cancel_reservation(self, reservation_id):
        row = self.session.execute(
            "SELECT status FROM reservations WHERE reservation_id = %s ALLOW FILTERING",
            (reservation_id,)
        ).one()
        if not row:
            return False, "Reservation not found"
        if row.status == "cancelled":
            return False, "Reservation was already cancelled"
        self.session.execute(
            "UPDATE reservations SET status = 'cancelled' WHERE movie_name = %s AND show_time = %s AND screen_number = %s AND seat_number = %s",
            (row.movie_name, row.show_time, row.screen_number, row.seat_number)
        )
        return True, "Reservation cancelled"

    def cancel_multiple(self, reservation_ids):
        results = []
        for rid in reservation_ids:
            ok, msg = self.cancel_reservation(rid)
            results.append((rid, ok, msg))
        return results

    def view_reservations(self, customer_name=None):
        if customer_name:
            rows = self.session.execute(
                "SELECT movie_name, show_time, seat_number, status, reservation_id, created_at "
                "FROM reservations WHERE customer_name = %s ALLOW FILTERING",
                (customer_name,)
            )
        else:
            rows = self.session.execute("SELECT movie_name, show_time, seat_number, customer_name, "
                                        "status, reservation_id, created_at FROM reservations")
        print("\n--- RESERVATIONS ---")
        count = 0
        for r in rows:
            print(f"  ID: {r.reservation_id} | Customer: {r.customer_name} | Movie: {r.movie_name} | "
                  f"Seat: {r.seat_number} | Status: {r.status} | Date: {r.created_at}")
            count += 1
        if count == 0:
            print("  No reservations.")
        print()

    def view_all_reservations_with_customer(self):
        rows = self.session.execute("SELECT movie_name, show_time, customer_name, seat_number, status, reservation_id FROM reservations")
        print("\n--- ALL RESERVATIONS ---")
        for r in rows:
            print(f"  Customer: {r.customer_name} | Movie: {r.movie_name} | Seat: {r.seat_number} | Status: {r.status} | ID: {r.reservation_id}")
        print()
