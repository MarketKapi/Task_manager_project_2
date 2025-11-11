import mysql.connector

# ==============================
#  NASTAVENÍ PŘIPOJENÍ
# ==============================

HOST = "localhost"
USER = "root"
PASSWORD = "1111"       
DATABASE = "testing_databaze"  

# ==============================
#  FUNKCE: PŘIPOJENÍ K DATABÁZI
# ==============================

def pripojeni_db():
    """
    Funkce vytvoří připojení k MySQL serveru, vytvoří databázi (pokud neexistuje)
    a vrací připojení a kurzor.
    """
    # Připojení k MySQL serveru
    try:
        conn = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
        )

        # Vytvoření kurzoru
        cursor = conn.cursor()

        # Vytvoření databáze
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")

        # Přepnutí na vytvořenou databázi
        conn.database = DATABASE
        return conn, cursor

    except mysql.connector.Error as err:
        print(f"Chyba při připojování: {err}")
        return None, None
    
# ==============================
#  FUNKCE: VYTVOŘENÍ TABULKY
# ==============================

def vytvoreni_tabulky():
    """
    Funkce vytvoří tabulku 'ukoly' (pokud neexistuje)
    a ověří existenci tabulky v databázi.
    """
    # Připojení k databázi
    conn, cursor = pripojeni_db()
    if not conn or not cursor:
        print("Nelze se připojit k databázi.")
        return
    
    try:
        # Vytvoření tabulky 'ukoly'
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(100) NOT NULL,
                popis TEXT,
                stav ENUM('nezahájeno', 'probíhá', 'hotovo') NOT NULL DEFAULT 'nezahájeno',
                datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Ověření existence tabulky
        cursor.execute("SHOW TABLES LIKE 'ukoly'")
        result = cursor.fetchone()
        if result:
            print("Tabulka 'ukoly' byla vytvořena nebo již existuje v databázi.")
        else:
            print("Tabulka 'ukoly' nenalezena v databázi.")
    
    except mysql.connector.Error as err:
        print(f"Chyba při vytváření tabulky: {err}")
    
    finally:
        cursor.close()
        conn.close()

# ==============================
#  FUNKCE: ZOBRAZENÍ HLAVNÍ NABÍDKY
# ==============================

def hlavni_menu():
    """
    Funkce zobrazí hlavní nabídku a nechá uživatele zvolit z nabízených možností.
    Pokud uživatel zvolí neplatnou možnost, program ho upozorní a nechá vybrat znovu.
    """
    while True:
        print("\nSprávce úkolů - Hlavní menu")
        print("1. Přidat nový úkol")
        print("2. Zobrazit všechny úkoly")
        print("3. Aktualizovat úkol")
        print("4. Odstranit úkol")
        print("5. Konec programu")

        volba = input("Vyberte možnost (1-5): ").strip()

        if volba == "1":
            pridat_ukol()
        elif volba == "2":
            zobrazit_ukoly()
        elif volba == "3":
            aktualizovat_ukol()
        elif volba == "4":
            odstranit_ukol()
        elif volba == "5":
            print("Konec programu.")
            break
        else:
            print("Neplatná volba. Zadejte číslo mezi 1 a 5.")  

# ==============================
#  FUNKCE: PŘIDAT NOVÝ ÚKOL
# ==============================

def pridat_ukol():
    """
    Funkce přidá nový úkol do databáze. 
    Uživatel zadává jeho název a popis, které nesmí být prázdné.
    Výchozí stav úkolu je 'Nezahájeno'.
    Pro návrat do hlavního menu může uživatel zadat '0'.
    """
    print("\n=== Přidání nového úkolu ===")
    print("Pokud nechcete pokračovat, zadejte '0' pro návrat do hlavního menu.")

    while True:
        nazev = input("\nZadejte název úkolu: ").strip()
        if nazev == "0":
            print("Návrat do hlavního menu.")
            return
        if not nazev:
            print("Název úkolu nesmí být prázdný. Zkuste to, prosím, znovu.")
            continue

        popis = input("Zadejte popis úkolu: ").strip()
        if popis == "0":
            print("Návrat do hlavního menu.")
            return
        if not popis:
            print("Popis úkolu nesmí být prázdný. Zkuste to, prosím, znovu.")
            continue

        # Připojení k databázi
        conn, cursor = pripojeni_db()
        if not conn or not cursor:
            print("Nelze se připojit k databázi.")
            return

        try:
            sql = "INSERT INTO ukoly (nazev, popis, stav) VALUES (%s, %s, %s)"
            values = (nazev, popis, "nezahájeno")
            cursor.execute(sql, values)
            conn.commit()
            print(f"Úkol '{nazev}' byl úspěšně přidán do databáze.")

        except mysql.connector.Error as err:
            print(f"Chyba při vkládání úkolu: {err}")
        
        finally:
            cursor.close()
            conn.close() 

        break 

# ==============================
#  FUNKCE: ZOBRAZIT ÚKOLY
# ============================== 

def zobrazit_ukoly():
    """
    Funkce zobrazí seznam všech úkolů ve stavech "nezahájeno" nebo "probíhá".
    V případě žádného uloženého úkolu se zobrazí informační zpráva.
    Pro návrat do hlavního menu po zobrazení seznamu může uživatel stisknout Enter.
    """
    print("\n=== Seznam uložených úkolů ===")

    # Připojení k databázi
    conn, cursor = pripojeni_db()
    if not conn or not cursor:
        print("Nelze se připojit k databázi.")
        return

    try:
        # Výběr pouze úkolů se stavem 'nezahájeno' nebo 'probíhá'
        sql = """
            SELECT id, nazev, popis, stav 
            FROM ukoly 
            WHERE stav IN ('nezahájeno', 'probíhá')
            ORDER BY id ASC
            """
        cursor.execute(sql)
        ukoly = cursor.fetchall()

        if not ukoly:
            print("\nNemáte žádný uložený úkol.")
        else:
            print(f"{'ID':<5} {'Název':<25} {'Popis':<40} {'Stav':<15}")
            print("-" * 85)
            for id_, nazev, popis, stav in ukoly:
                # Zkrácení dlouhého popisu
                if len(popis) > 35:
                    popis = popis[:32] + "..."
                print(f"{id_:<5} {nazev:<25} {popis:<40} {stav:<15}")

        input("\nStiskněte Enter pro návrat do hlavního menu.")

    except mysql.connector.Error as err:
        print(f"Chyba při načítání úkolů: {err}")
    
    finally:
        cursor.close()
        conn.close()

# ==============================
#  FUNKCE: AKTUALIZOVAT ÚKOL
# ==============================

def aktualizovat_ukol():
    """
    Funkce umožňuje změnu stavu úkolu. 
    Uživateli zobrazí seznam úkolů a nechá ho vybrat nový stav:
    "probíhá" nebo "hotovo".
    Pro návrat do hlavního menu může uživatel zadat '0'.
    """
    print("\n=== Aktualizace úkolu ===")

    # Připojení k databázi
    conn, cursor = pripojeni_db()
    if not conn or not cursor:
        print("Nelze se připojit k databázi.")
        return
    
    try:
        # Výběr všech úkolů
        cursor.execute("SELECT id, nazev, stav FROM ukoly ORDER BY id ASC")
        ukoly = cursor.fetchall()

        if not ukoly:
            print("Žádné uložené úkoly - nic k aktualizaci.")
            return

        # Výpis úkolů
        print(f"{'ID':<5} {'Název':<30} {'Stav':<15}")
        print("-" * 50)
        for id_, nazev, stav in ukoly:
            print(f"{id_:<5} {nazev:<30} {stav:<15}")

        # Výběr úkolu k aktualizaci
        print("\nZadejte ID úkolu, který chcete aktualizovat, nebo '0' pro návrat do hlavního menu.")

        while True:
            try:
                id_ukolu = int(input("ID úkolu: ").strip())
                if id_ukolu == 0:
                    print("Návrat do hlavního menu.")
                    return
                
                cursor.execute("SELECT id FROM ukoly WHERE id = %s", (id_ukolu,))
                existujici_id = cursor.fetchone()
                if existujici_id:
                    break
                else:
                    print("Úkol s tímto ID neexistuje. Zkuste to, prosím, znovu nebo zadejte '0' pro návrat")
            except ValueError:
                print("Zadejte platné číselné ID nebo 0 pro návrat.")

        # Výběr nového stavu
        while True:
            print("\nVyberte nový stav:")
            print("1. probíhá")
            print("2. hotovo")
            print("0. návrat do hlavního menu")
            volba = input("Zadejte číslo možnosti: ").strip()

            if volba == "0":
                print("Návrat do hlavního menu.")
                return
            if volba == "1":
                novy_stav = "probíhá"
                break
            elif volba == "2":
                novy_stav = "hotovo"
                break
            else:
                print("Neplatná volba. Zadejte 1, 2 nebo 0.")

        # Aktualizace v databázi
        cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, id_ukolu))
        conn.commit()
        print(f"Stav úkolu (ID: {id_ukolu}) byl změněn na '{novy_stav}'.")

    except mysql.connector.Error as err:
        print(f"Chyba při aktualizaci úkolu: {err}")
    
    finally:
        cursor.close()
        conn.close()

# ==============================
#  FUNKCE: ODSTRANIT ÚKOL
# ==============================

def odstranit_ukol():
    """
    Funkce odstraní úkol z databáze podle jeho ID.
    Uživatel vybere příslušné ID po zobrazení seznamu úkolů.
    Pokud zadané ID neexistuje, funkce uživatele nechá vybrat znovu.
    Pro návrat do hlavního menu může uživatel zadat '0'.
    """
    # Připojení k databázi
    conn, cursor = pripojeni_db()
    if not conn or not cursor:
        print("Nelze se připojit k databázi.")
        return

    try:
        # Výběr všech úkolů
        cursor.execute("SELECT id, nazev, popis, stav FROM ukoly ORDER BY id ASC")
        ukoly = cursor.fetchall()

        if not ukoly:
            print("V databázi nejsou žádné úkoly k odstranění.")
            return

        # Výpis úkolů
        print("\n=== Seznam úkolů ===")
        print(f"{'ID':<5} {'Název':<25} {'Popis':<40} {'Stav':<15}")
        print("-" * 85)
        for id_, nazev, popis, stav in ukoly:
            if len(popis) > 35:
                popis = popis[:32] + "..."
            print(f"{id_:<5} {nazev:<25} {popis:<40} {stav:<15}")

        print("\nZadejte ID úkolu, který chcete odstranit nebo zadejte '0' pro návrat do hlavního menu. ")

        # Výběr ID k odstranění
        while True:
            try:
                id_ukolu = int(input("ID úkolu: ").strip())
                if id_ukolu == 0:
                    print("Návrat do hlavního menu.")
                    return
                
                cursor.execute("SELECT id, nazev FROM ukoly WHERE id = %s", (id_ukolu,))
                existujici_id = cursor.fetchone()
                if existujici_id:
                    nazev_ukolu = existujici_id[1]
                    break
                else:
                    print("Úkol s tímto ID neexistuje. Zkuste to, prosím, znovu nebo zadejte '0' pro návrat do hlavního menu.")
            except ValueError:
                print("Zadejte platné číselné ID nebo '0' pro návrat.")

        # Potvrzení odstranění
        potvrzeni = input(f"Opravdu chcete odstranit úkol '{nazev_ukolu}'? (a/n): ").strip().lower()
        if potvrzeni == "a":
            cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
            conn.commit()
            print(f"Úkol '{nazev_ukolu}' byl trvale odstraněn z databáze.")
        else:
            print("Odstranění bylo zrušeno.")

    except mysql.connector.Error as err:
        print(f"Chyba při mazání úkolu: {err}")
    finally:
        cursor.close()
        conn.close()

# ==============================
#  SPUŠTĚNÍ PROGRAMU
# ==============================

if __name__ == "__main__":
    vytvoreni_tabulky()
    hlavni_menu()