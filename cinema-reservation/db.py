# Autores: Javier Rocafull Cabello y Jaime Rodriguez Martin-Palomino
from cassandra.cluster import Cluster, NoHostAvailable
from cassandra.query import SimpleStatement
import uuid


NODES = ['127.0.0.1', '127.0.0.2', '127.0.0.3']
KEYSPACE = "cinema_reservations"


def get_cluster(contact_points=None):
    if contact_points is None:
        contact_points = NODES
    return Cluster(contact_points, port=9042)


def get_session(cluster=None, contact_points=None):
    if cluster is None:
        cluster = get_cluster(contact_points)
    try:
        session = cluster.connect()
        return session
    except NoHostAvailable as e:
        print(f"Error: Could not connect to Cassandra. {e}")
        raise


def init_schema(session):
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
        WITH replication = {{
            'class': 'SimpleStrategy',
            'replication_factor': 2
        }}
    """)
    session.set_keyspace(KEYSPACE)

    session.execute("""
        CREATE TABLE IF NOT EXISTS screenings (
            movie_name text,
            show_time timestamp,
            screen_number int,
            total_seats int,
            screening_id UUID,
            PRIMARY KEY ((movie_name), show_time, screen_number)
        )
    """)

    session.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            movie_name text,
            show_time timestamp,
            screen_number int,
            seat_number int,
            customer_name text,
            status text,
            reservation_id UUID,
            created_at timestamp,
            PRIMARY KEY ((movie_name, show_time), screen_number, seat_number)
        )
    """)

    session.execute("""
        CREATE INDEX IF NOT EXISTS idx_customer
        ON reservations (customer_name)
    """)

    session.execute("""
        CREATE INDEX IF NOT EXISTS idx_status
        ON reservations (status)
    """)

    print("Schema initialized successfully.")


def seed_screenings(session):
    session.set_keyspace(KEYSPACE)
    movies = [
        ("Inception", "2026-06-15 18:00:00", 1, 50),
        ("Inception", "2026-06-15 21:00:00", 1, 50),
        ("Interstellar", "2026-06-15 18:00:00", 2, 40),
        ("Interstellar", "2026-06-15 21:00:00", 2, 40),
        ("The Matrix", "2026-06-15 19:00:00", 3, 30),
        ("Dune", "2026-06-16 18:00:00", 1, 50),
        ("Dune", "2026-06-16 21:00:00", 2, 40),
    ]
    for movie, show_time, screen, seats in movies:
        session.execute("""
            INSERT INTO screenings (movie_name, show_time, screen_number, total_seats, screening_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (movie, show_time, screen, seats, uuid.uuid4()))
    print("Sample screenings inserted.")
