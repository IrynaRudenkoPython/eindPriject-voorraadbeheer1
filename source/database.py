import sqlite3


class Database:
    def __init__(self, db_name):
        self.db_name = db_name

    def __str__(self, code):
        artikel = self.artikels_code(code)
        return (f'artikel: {artikel[1]}\n'
               f'code: {artikel[0]}\n'
               f'aankoopprijs: {artikel[2]}\n'
               f'voorraad: {artikel[3]}\n'
               f'minimumvoorraad: {artikel[4]}\n'
               f'maximumvoorraad: {artikel[5]}')

    def create_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def all_artikels(self):
        with self.create_connection() as conn:
            curs = conn.cursor()
            return curs.execute('SELECT * FROM artikels').fetchall()

    def artikels_code(self, code):
        with self.create_connection() as conn:
            curs = conn.cursor()
            return curs.execute('SELECT * FROM artikels WHERE code = ?', (code,)).fetchone()

    def artikelToevoegen(self, code, naam, aankoopprijs, voorraad, minimum_aantal_in_voorraad,
                         maximum_aantal_in_voorraad):
        with self.create_connection() as conn:
            artikel = self.artikels_code(code)
            if artikel is None:
                conn.execute(
                    'INSERT INTO artikels (code, naam, aankoopprijs, voorraad, minimum_aantal_in_voorraad, maximum_aantal_in_voorraad) VALUES (?, ?, ?, ?, ?, ?)',
                    (code, naam, aankoopprijs, voorraad, minimum_aantal_in_voorraad, maximum_aantal_in_voorraad))
            else:
                conn.execute(
                    'UPDATE artikels SET naam = ?, aankoopprijs = ?, voorraad = ?, minimum_aantal_in_voorraad = ?, maximum_aantal_in_voorraad = ?  WHERE code = ?',
                    (naam, aankoopprijs, voorraad, minimum_aantal_in_voorraad, maximum_aantal_in_voorraad, code))
            conn.commit()

    #of voorraad minder dan minimum_aantal
    def tekort(self, code):
        artikel = self.artikels_code(code)
        tekort = artikel['voorraad'] - artikel['minimum_aantal_in_voorraad']
        return tekort if tekort < 0 else 0

    def aankoop(self, code, aantal):
        with self.create_connection() as conn:
            artikel = self.artikels_code(code)
            aantal = artikel[3] + int(aantal)
            conn.execute('UPDATE artikels SET voorraad = ?  WHERE code = ?', (aantal, code))
            conn.commit()

    def verkoop(self, code, aantal):
        with self.create_connection() as conn:
            artikel = self.artikels_code(code)
            kol = artikel['voorraad'] - aantal
            if kol >= 0:
                conn.execute('UPDATE artikels SET voorraad = ?  WHERE code = ?', (kol, code))
                conn.commit()
            else:
                # assert aantal >= 0, f'niet voldoende voorraad van artikel {code} ({abs(aantal)} stuks te kort)'
                return abs(kol)

    def waarde(self):
        totale_sum = 0
        rows = self.all_artikels()
        for row in rows:
            totale_sum += row['aankoopprijs'] * row['voorraad']
        return totale_sum

    def aanvullen(self):
        printlijst = []
        rows = self.all_artikels()
        for row in rows:
            tekort = self.tekort(row['code'])
            if tekort != 0:
                el = self.__str__(row[0]) + f'\n--> {row["maximum_aantal_in_voorraad"] - row["voorraad"]} stuks bijbestellen'
                printlijst.append(el)
        if len(printlijst) > 0:
            return ('\n========================\n'.join(printlijst))

    def print_artikelen(self):
        printlijst = []
        rows = self.all_artikels()
        for row in rows:
            el = self.__str__(row[0])
            printlijst.append(el)
        if len(printlijst) > 0:
            return ('\n========================\n'.join(printlijst))

