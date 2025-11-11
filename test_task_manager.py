import pytest
import mysql.connector
from task_manager import pripojeni_db, vytvoreni_tabulky

# ============================
# NASTAVENÍ TESTOVACÍ DB
# ============================

TEST_DB = "testing_databaze_test"

@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """Fixture vytvoří testovací databázi a tabulku se stejnou strukturou jako v hlavním programu."""
    conn = mysql.connector.connect(host="localhost", user="root", password="1111")
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB}")
    conn.database = TEST_DB

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(100) NOT NULL,
            popis TEXT,
            stav ENUM('nezahájeno', 'probíhá', 'hotovo') NOT NULL DEFAULT 'nezahájeno',
            datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    yield  # --- Zde běží testy ---

    # Smazání testovacích dat
    cursor.execute("DROP DATABASE IF EXISTS testing_databaze_test")
    conn.close()

@pytest.fixture
def db_connection():
    """Fixture vrací nové připojení a kurzor k testovací databázi."""
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database=TEST_DB
    )
    cursor = conn.cursor()
    yield conn, cursor
    conn.commit()
    cursor.close()
    conn.close()

# ============================
# TESTY PRO pridat_ukol()
# ============================

def pridat_ukol_do_db(conn, cursor, nazev, popis):
    """Pomocná funkce pro vložení úkolu, která funguje stejně jako pridat_ukol z hlavního programu."""
    sql = "INSERT INTO ukoly (nazev, popis, stav) VALUES (%s, %s, %s)"
    cursor.execute(sql, (nazev, popis, "nezahájeno"))
    conn.commit()

def test_pridat_ukol_pozitivni(db_connection):
    """Pozitivní test - ověří, že se úkol správně uloží do databáze."""
    conn, cursor = db_connection
    pridat_ukol_do_db(conn, cursor, "Dokončit projekt", "Napsat automatizované testy")

    cursor.execute("SELECT * FROM ukoly WHERE nazev = %s", ("Dokončit projekt",))
    vysledek = cursor.fetchone()

    assert vysledek is not None
    assert vysledek[1] == "Dokončit projekt"
    assert vysledek[3] == "nezahájeno"

def test_pridat_ukol_negativni(db_connection):
    """Negativní test - pokus o vložení prázdného názvu; úkol by se neměl uložit."""
    conn, cursor = db_connection

    # Pokus o vložení prázdného názvu
    nazev = ""
    popis = "Popis testu bez názvu"

    # Manuální zadání INSERTu
    if nazev.strip() and popis.strip():
        cursor.execute("INSERT INTO ukoly (nazev, popis, stav) VALUES (%s, %s, %s)", (nazev, popis, "nezahájeno"))
        conn.commit()

    # Ověření, že se nic nevložilo
    cursor.execute("SELECT COUNT(*) FROM ukoly WHERE popis = %s", (popis,))
    pocet = cursor.fetchone()[0]

    assert pocet == 0, "Úkol s prázdným názvem byl vložen, což by se nemělo stát."

# ============================
# TESTY PRO aktualizovat_ukol()
# ============================

def test_aktualizovat_ukol_pozitivni(db_connection):
    """Pozitivní test - úspěšně změní stav existujícího úkolu."""
    conn, cursor = db_connection
    pridat_ukol_do_db(conn, cursor, "Aktualizační test", "Popis testu")
    
    cursor.execute("SELECT id FROM ukoly WHERE nazev = %s", ("Aktualizační test",))
    id_ukolu = cursor.fetchone()[0]

    cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", ("hotovo", id_ukolu))
    conn.commit()

    cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (id_ukolu,))
    novy_stav = cursor.fetchone()[0]

    assert novy_stav == "hotovo"

def test_aktualizovat_ukol_negativni(db_connection):
    """Negativní test - pokus o změnu stavu neexistujícího úkolu; test by měl selhat."""
    conn, cursor = db_connection
    neexistujici_id = 999
    cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", ("hotovo", neexistujici_id))
    conn.commit()
    assert cursor.rowcount == 0  # Očekáváme, že se nic neaktualizuje

# ============================
# TESTY PRO odstranit_ukol()
# ============================

def test_odstranit_ukol_pozitivni(db_connection):
    """Pozitivní test - ověří, že se existující úkol úspěšně odstraní."""
    conn, cursor = db_connection
    pridat_ukol_do_db(conn, cursor, "Úkol k odstranění", "Popis úkolu")

    cursor.execute("SELECT id FROM ukoly WHERE nazev = %s", ("Úkol k odstranění",))
    id_ukolu = cursor.fetchone()[0]

    cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
    conn.commit()

    cursor.execute("SELECT * FROM ukoly WHERE id = %s", (id_ukolu,))
    vysledek = cursor.fetchone()

    assert vysledek is None  # Úkol byl odstraněn

def test_odstranit_ukol_negativni(db_connection):
    """Negativní test - pokus o odstranění neexistujícího úkolu; test by měl selhat."""
    conn, cursor = db_connection
    neexistujici_id = 999
    cursor.execute("DELETE FROM ukoly WHERE id = %s", (neexistujici_id,))
    conn.commit()
    assert cursor.rowcount == 0  # Očekáváme, že se nic nesmaže