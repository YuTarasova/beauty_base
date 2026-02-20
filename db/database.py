import mysql.connector
import logging
import os
from typing import Tuple
from pathlib import Path
import time
from api.utils import password_hash

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
pagevolume = 30

if env_path.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception as e:
        print(str(e))


class DataConnection:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.port = int(os.getenv("DB_PORT"))
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.dbname = os.getenv("DB_NAME")

    def _get_connection(self):
        return mysql.connector.connect(host=self.host,
                                       port=self.port,
                                       user=self.user,
                                       password=self.password,
                                       database=self.dbname)

    def exec(self, query: str, params: Tuple | dict = None):
        try:
            with self._get_connection() as cnx:
                cnx.autocommit = True
                with cnx.cursor() as cur:
                    cur.execute(query, params)
                    cur.close()
                    cnx.close()
        except mysql.connector.Error as e:
            logger.error(f"Ошибка в базе данных: {e}")
            raise

    def get_single(self, query: str, params: Tuple |dict = None):
        try:
            with self._get_connection() as cnx:
                cnx.autocommit = True
                with cnx.cursor(dictionary=True) as cur:
                    cur.execute(query, params)
                    data = cur.fetchone()
                    cur.close()
                    cnx.close()
                    return data
        except mysql.connector.Error as e:
            logger.error(f"Ошибка в базе данных: {e}")
            raise

    def get_all(self, query: str, params: Tuple | dict = None):
        try:
            with self._get_connection() as cnx:
                cnx.autocommit = True
                with cnx.cursor(dictionary=True) as cur:
                    cur.execute(query, params)
                    data = cur.fetchall()
                    cur.close()
                    cnx.close()
                    return data
        except mysql.connector.Error as e:
            logger.error(f"Ошибка в базе данных: {e}")
            raise

    def get_page(self, column: str, table: str, page: int = 0):
        query = f"SELECT {column} FROM {table} LIMIT %s OFFSET %s;"
        try:
            data = self.get_all(query, (pagevolume, pagevolume*page))
            return data
        except Exception:
            raise

    def get_last_page(self, table: str, col: str = "*"):
        query = f"SELECT COUNT({col}) as cnt FROM {table};"
        try:
            data = self.get_single(query)
            if data is None:
                raise Exception
            return ((data["cnt"]-1)//pagevolume)
        except Exception:
            raise


class DataManager(DataConnection):
    def create_database(self):
        """Создание базы данных если не существует"""
        try:
            cnx = mysql.connector.connect(host=self.host,
                                          port=self.port,
                                          user=self.user,
                                          password=self.password)
            cnx.autocommit = True
            with cnx.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS {self.dbname}")
                cur.close()
            cnx.close()
        except Exception as e:
            logger.error(f"Ошибка при создании базы данных: {e}")
            raise

    def create_table(self):
        create_query = '''
        CREATE TABLE IF NOT EXISTS client (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        first_name VARCHAR(32) NOT NULL,
        last_name VARCHAR(32),
        phone DECIMAL(11) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        PRIMARY KEY (id),
        CONSTRAINT CHK_client CHECK (REGEXP_LIKE(first_name, '^[А-ЯЁ][-а-яёЁА-Я[:space:]]{0,31}$', 'c') AND
        (REGEXP_LIKE(last_name, '^[А-ЯЁ][-а-яёЁА-Я[:space:]]{0,31}$', 'c') OR last_name is NULL) AND
        phone>=10000000000 AND phone<100000000000)
        );
        
        CREATE TABLE IF NOT EXISTS proc_type (
        id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
        name VARCHAR(50) NOT NULL,
        staff_lvl TINYINT UNSIGNED,
        price DECIMAL(7,2) NOT NULL,
        duration TIME NOT NULL,
        PRIMARY KEY (id),
        CONSTRAINT CHK_proc_type CHECK (REGEXP_LIKE(name, '^[А-ЯЁ[:digit:]][-а-яёЁА-Я,/[:space:][:digit:].+]{0,49}$', 'c') AND
        price>=0 AND duration>0 AND HOUR(duration)<20)
        );
        CREATE TABLE IF NOT EXISTS city (
        id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
        city_name VARCHAR(32) NOT NULL,
        tz VARCHAR(6) NOT NULL,
        PRIMARY KEY (id),
        CONSTRAINT CHK_city CHECK (REGEXP_LIKE(city_name, '^[А-ЯЁ][-а-яёЁА-Я[:space:]]{0,31}$', 'c') AND
        REGEXP_LIKE(tz, '^(\\\\+|\\\\-)[[:digit:]]{1,2}:[[:digit:]]{2}$'))
        );
        CREATE TABLE IF NOT EXISTS salon (
        id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
        city_id SMALLINT UNSIGNED NOT NULL,
        address VARCHAR(50) NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (city_id) REFERENCES city(id),
        CONSTRAINT CHK_salon CHECK (REGEXP_LIKE(address, '^[А-ЯЁ[:digit:]][-а-яёЁА-Я,/[:space:][:digit:].+]{0,49}$', 'c'))
        );
        CREATE TABLE IF NOT EXISTS staff (
        id SMALLINT UNSIGNED UNIQUE NOT NULL,
        salon_id SMALLINT UNSIGNED NOT NULL,
        first_name VARCHAR(32) NOT NULL,
        last_name VARCHAR(32) NOT NULL,
        fathers_name VARCHAR(32),
        phone DECIMAL(11) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (salon_id) REFERENCES salon(id),
        CONSTRAINT CHK_staff CHECK (REGEXP_LIKE(first_name, '^[А-ЯЁ][-а-яёЁА-Я[:space:]]{0,31}$', 'c') AND
        REGEXP_LIKE(last_name, '^[А-ЯЁ][-а-яёЁА-Я[:space:]]{0,31}$', 'c') AND
        (REGEXP_LIKE(fathers_name, '^[А-ЯЁ][-а-яёЁА-Я[:space:]]{0,31}$', 'c') OR fathers_name is NULL) AND
        phone>=10000000000 AND phone<100000000000)
        );
        
        CREATE TABLE IF NOT EXISTS reservation (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        staff_id SMALLINT UNSIGNED NOT NULL,
        client_id INT UNSIGNED NOT NULL,
        res_date DATE NOT NULL,
        res_st TIME NOT NULL,
        type_id SMALLINT UNSIGNED NOT NULL,
        status VARCHAR(13) NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (staff_id) REFERENCES staff(id),
        FOREIGN KEY (client_id) REFERENCES client(id),
        FOREIGN KEY (type_id) REFERENCES proc_type(id),
        CONSTRAINT CHK_rsv CHECK (res_st>0 AND
        status IN ('active','absent client','completed',
        'unpaid','absent staff','interrupted','cancelled',
        'other issue'))
        );
        CREATE TABLE IF NOT EXISTS staff_type (
        staff_id SMALLINT UNSIGNED NOT NULL,
        type_id SMALLINT UNSIGNED NOT NULL,
        FOREIGN KEY (staff_id) REFERENCES staff(id),
        FOREIGN KEY (type_id) REFERENCES proc_type(id)
        );
        CREATE TABLE IF NOT EXISTS schedule (
        staff_id SMALLINT UNSIGNED NOT NULL,
        sch_date DATE NOT NULL,
        sch_st TIME NOT NULL,
        sch_end TIME NOT NULL,
        FOREIGN KEY (staff_id) REFERENCES staff(id),
        CONSTRAINT CHK_sch CHECK (sch_st>0 AND sch_end>sch_st AND HOUR(sch_end)<24)
        );

        DELIMITER //
        CREATE PROCEDURE IF NOT EXISTS make_rsv(
          IN st_id SMALLINT, IN ty_id SMALLINT, IN cl_id INT, 
          IN da_te DATE, IN st_rt TIME)
        BEGIN
          DECLARE fin TIME;
          DECLARE x INT;
          DECLARE y INT;
          START TRANSACTION;
            SET fin = ADDTIME(st_rt, (SELECT duration 
              FROM proc_type WHERE id = ty_id FOR SHARE));
            SET x = (SELECT COUNT(*) FROM staff_type
              WHERE staff_id = st_id AND type_id = ty_id FOR SHARE);
            SET y = (WITH a AS (SELECT res_st, type_id FROM reservation 
                WHERE staff_id = st_id AND res_date = da_te
                AND res_st < fin ORDER BY res_st DESC LIMIT 1)
              SELECT COUNT(*) FROM a JOIN proc_type ON type_id = id
              WHERE ADDTIME(res_st, duration) > st_rt FOR SHARE);
            IF (x = 1 AND y = 0) THEN 
              INSERT INTO reservation (staff_id, client_id, res_date, res_st, type_id, status)
                VALUES (st_id, cl_id, da_te, st_rt, ty_id, 'active');
            ELSE 
              ROLLBACK;
              SELECT ("Couldn't make a reservation. Try refreshing available time intervals") 
                AS Warning;
            END IF;
          COMMIT;
        END // 
        CREATE PROCEDURE IF NOT EXISTS get_time_intervals(
          IN st_id SMALLINT, IN ty_id SMALLINT, IN da_te DATE)
        BEGIN
          DECLARE dur TIME;
          SET dur = (SELECT duration FROM proc_type 
            WHERE id = ty_id);
          WITH a AS (
              (SELECT sch_end as fin,  sch_st as beg
              FROM schedule WHERE staff_id = st_id
              AND sch_date = da_te
              ) UNION (
              SELECT res_st as fin, 
              ADDTIME(res_st, duration) as beg
              FROM reservation JOIN proc_type ON type_id = proc_type.id
              WHERE staff_id = st_id AND res_date = da_te
            )), b1 AS (
              SELECT beg, row_number() over(order by beg) as rn 
              FROM a), b2 AS (
              SELECT fin, row_number() over(order by fin) as rn 
              FROM a)
          SELECT TIME_FORMAT(beg, '%H:%i') as avail_st, 
            TIME_FORMAT(TIMEDIFF(fin, dur), '%H:%i') as avail_end
            FROM b1 JOIN b2 ON b1.rn = b2.rn
            WHERE TIMEDIFF(fin,beg) >= dur
            ORDER BY avail_st;
        END // 
        DELIMITER ;
        '''
        self.exec(create_query)
        logger.info("Таблицы созданы.")

    def starting_filling(self):
        query = """
        INSERT INTO client (first_name, last_name, phone, password_hash)
        VALUES (%s, %s, %s, %s);"""
        try:
            with self._get_connection() as cnx:
                cnx.autocommit = True
                with cnx.cursor() as cur:
                    pass_hash = password_hash("Detroit")
                    cur.execute(query, ("Коннор",None,31324831751,pass_hash))
                    print("Клиенты внесены.")
                    query = """
                    INSERT INTO city (city_name, tz) VALUES (%s, %s);"""
                    cur.execute(query, ("Санкт-Петербург", "+03:00"))
                    cur.execute(query, ("Якутск", "+09:00"))
                    cur.execute(query, ("Гонолулу", "-10:00"))
                    cur.execute(query, ("Анадырь", "+12:00"))
                    print("Города внесены.")
                    query = """
                    INSERT INTO salon (city_id, address) VALUES (%s, %s);"""
                    cur.execute(query,(1, "Невский проспект, 1"))
                    cur.execute(query, (1, "Каменноостровский проспект, 17"))
                    cur.execute(query, (2, "203-й микрорайон, 25"))
                    cur.execute(query, (3, "2080 С Кинг ст"))
                    cur.execute(query, (4, "Отке, 14а"))
                    print("Салоны внесены.")
                    query = """
                    INSERT INTO proc_type (name, staff_lvl, price, duration) VALUES (%s, %s, %s, %s);"""
                    cur.execute(query, ("Коррекция бровей", 1, 400.00, "00:40:00"))
                    cur.execute(query, ("Коррекция бровей", 2, 600.00, "00:30:00"))
                    cur.execute(query, ("Маникюр + покрытие гель-лаком", None , 1900.00, "02:00:00"))
                    cur.execute(query, ("Окрашивание в один тон", 1, 1900.00, "02:10:00"))
                    cur.execute(query, ("Окрашивание в один тон", 2, 2250.00, "01:50:00"))
                    cur.execute(query, ("Окрашивание в один тон", 3, 2600.00, "01:30:00"))
                    cur.execute(query, ("Детская стрижка", None, 700.00, "00:45:00"))
                    cur.execute(query, ("Мужская стрижка", None, 1100.00, "01:00:00"))
                    print("Услуги внесены.")
                    query = """
                    INSERT INTO staff VALUES (%s,%s,%s, %s,%s,%s, %s);"""
                    pass_hash = password_hash("I_$pe@%_Engli$#")
                    cur.execute(query, (1,1,"Наталья","Филатова","Петровна",77777777777,pass_hash))
                    pass_hash = password_hash("@Kostopravik")
                    cur.execute(query, (101, 1, "Самира", "Талипова", "Талантбековна", 79999999999, pass_hash))
                    pass_hash = password_hash("@ApparentlyNo")
                    cur.execute(query, (102, 2, "Екатерина", "Апполонина", "Дмитриевна", 11122233344, pass_hash))
                    pass_hash = password_hash("67MFPoppy")
                    cur.execute(query, (103, 3, "Инесса", "Тарасова", "Геннадьевна", 45556667778, pass_hash))
                    pass_hash = password_hash("@KaitryeGift")
                    cur.execute(query, (104, 4, "Екатерина", "Богданова", "Романовна", 88999000111, pass_hash))
                    pass_hash = password_hash("@pelmesshechka")
                    cur.execute(query, (105, 5, "Дарья", "Циплухина", "Игоревна", 78888888888, pass_hash))
                    pass_hash = password_hash("@pomellon")
                    cur.execute(query, (401, 2, "Мелания", "Аристакесян", "Артуровна", 22233344455, pass_hash))
                    pass_hash = password_hash("@oopsbackagain")
                    cur.execute(query, (402, 4, "Ксения", "Ващук", "Олеговна", 56667778889, pass_hash))
                    pass_hash = password_hash("blue_tractor")
                    cur.execute(query, (403, 3, "Нарияна", "Тарасова", "Геннадьевна", 99000111222, pass_hash))
                    pass_hash = password_hash("Wolf_Quest")
                    cur.execute(query, (404, 5, "Ия", "Эверстова", "Исаевна", 20231015011, pass_hash))
                    pass_hash = password_hash("@Angsterdam")
                    cur.execute(query, (1001, 2, "Нияз", "Курмакаев", "Раилевич", 33344455566, pass_hash))
                    pass_hash = password_hash("@Empinado_513")
                    cur.execute(query, (1002, 3, "Максим", "Илющенко", "Денисович", 67778889990, pass_hash))
                    pass_hash = password_hash("@ttrrell")
                    cur.execute(query, (1003, 4, "Артём", "Семёнов", "Алексеевич", 10111222333, pass_hash))
                    pass_hash = password_hash("@GuntherAdds")
                    cur.execute(query, (1004, 5, "Данила", "Астахов", "Евгеньевич", 44455566677, pass_hash))
                    pass_hash = password_hash("@Shishani7")
                    cur.execute(query, (1005, 2, "Абдул-Малик", "Лепиев", "Саламбекович", 78889990001, pass_hash))
                    pass_hash = password_hash("@tahmazidik")
                    cur.execute(query, (1006, 3, "Кирилл", "Тахмазиди", "Иванович", 11222333444, pass_hash))
                    pass_hash = password_hash("@realpavel")
                    cur.execute(query, (1007, 4, "Павел", "Огарышев", "Олегович", 55566677788, pass_hash))
                    pass_hash = password_hash("@Zaweno")
                    cur.execute(query, (1008, 5, "Павел", "Залесов", "Андреевич", 89990001112, pass_hash))
                    pass_hash = password_hash("@ErkhovSasha")
                    cur.execute(query, (1009, 2, "Александр", "Ерхов", "Александрович", 22333444555, pass_hash))
                    pass_hash = password_hash("@cgsg106")
                    cur.execute(query, (1010, 3, "Михаил", "Цуканов", "Дмитриевич", 66677788899, pass_hash))
                    pass_hash = password_hash("@chenrixx")
                    cur.execute(query, (1011, 4, "Никита", "Насибуллин", "Андреевич", 90001112223, pass_hash))
                    pass_hash = password_hash("@saneknaumchik")
                    cur.execute(query, (1012, 5, "Александр", "Наумов", "Павлович", 33444555666, pass_hash))
                    pass_hash = password_hash("@Ivanyyy")
                    cur.execute(query, (1013, 2, "Иван", "Овсюков", "Сергеевич", 77788899900, pass_hash))
                    pass_hash = password_hash("@Ibragim_oskanov")
                    cur.execute(query, (1014, 3, "Ибрагим", "Осканов", "Ахметович", 11112223334, pass_hash))
                    pass_hash = password_hash("@Syperdupertag")
                    cur.execute(query, (1015, 4, "Егор", "Ерофеев", "Юрьевич", 44555666777, pass_hash))
                    pass_hash = password_hash("@VladislavVorobyov02")
                    cur.execute(query, (1016, 5, "Владислав", "Воробьёв", "Валерьевич", 88899900011, pass_hash))
                    print("Сотрудники внесены.")
                    query = """
        INSERT INTO staff_type VALUES (%s,%s);"""
                    cur.execute(query, (1001, 5))
                    cur.execute(query, (1001, 8))
                    cur.execute(query, (1002, 6))
                    cur.execute(query, (1002, 3))
                    cur.execute(query, (1003, 4))
                    cur.execute(query, (1003, 7))
                    cur.execute(query, (1004, 7))
                    cur.execute(query, (1004, 3))
                    cur.execute(query, (1005, 8))
                    cur.execute(query, (1005, 2))
                    cur.execute(query, (1006, 6))
                    cur.execute(query, (1006, 2))
                    cur.execute(query, (1007, 5))
                    cur.execute(query, (1007, 8))
                    cur.execute(query, (1008, 3))
                    cur.execute(query, (1008, 7))
                    cur.execute(query, (1009, 1))
                    cur.execute(query, (1009, 7))
                    cur.execute(query, (1010, 1))
                    cur.execute(query, (1010, 4))
                    cur.execute(query, (1011, 5))
                    cur.execute(query, (1011, 7))
                    cur.execute(query, (1012, 2))
                    cur.execute(query, (1012, 6))
                    cur.execute(query, (1013, 5))
                    cur.execute(query, (1013, 7))
                    cur.execute(query, (1014, 2))
                    cur.execute(query, (1014, 4))
                    cur.execute(query, (1015, 1))
                    cur.execute(query, (1015, 5))
                    cur.execute(query, (1016, 6))
                    cur.execute(query, (1016, 7))
                    print("Сотрудникам сопоставлены типы.")
                    query = """
        INSERT INTO schedule VALUES (%s,%s,%s,%s);"""# salon_id = 2
                    cur.execute(query, (1001,"2026-02-16","10:00:00","22:00:00"))
                    cur.execute(query, (1001,"2026-02-17","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-02-16","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-02-17","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-02-18","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-02-18","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-02-19","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-02-20","10:00:00","22:00:00"))
                    cur.execute(query, (1013,"2026-02-19","10:00:00","22:00:00"))
                    cur.execute(query, (1013,"2026-02-20","10:00:00","22:00:00"))
                    cur.execute(query, (1001,"2026-02-21","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-02-21","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-02-21","10:00:00","22:00:00"))
                    cur.execute(query, (1013,"2026-02-21","10:00:00","22:00:00"))
                    cur.execute(query, (1001,"2026-02-22","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-02-22","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-02-22","10:00:00","22:00:00"))
                    cur.execute(query, (1013,"2026-02-22","10:00:00","22:00:00"))
                    cur.execute(query, (1001,"2026-02-23","10:00:00","22:00:00"))
                    cur.execute(query, (1001,"2026-02-24","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-02-23","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-02-24","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-02-25","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-02-25","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-02-26","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-02-27","10:00:00","22:00:00"))
                    cur.execute(query, (1013,"2026-02-26","10:00:00","22:00:00"))
                    cur.execute(query, (1013,"2026-02-27","10:00:00","22:00:00"))
                    cur.execute(query, (1001,"2026-02-28","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-02-28","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-02-28","10:00:00","22:00:00"))
                    cur.execute(query, (1013,"2026-02-28","10:00:00","22:00:00"))
                    cur.execute(query, (1001,"2026-03-01","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-03-01","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-03-01","10:00:00","22:00:00"))
                    cur.execute(query, (1013,"2026-03-01","10:00:00","22:00:00"))
                    cur.execute(query, (1001,"2026-03-02","10:00:00","22:00:00"))
                    cur.execute(query, (1001,"2026-03-03","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-03-02","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-03-03","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-03-04","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-03-04","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-03-05","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-03-06","10:00:00","22:00:00"))
                    cur.execute(query, (1013,"2026-03-05","10:00:00","22:00:00"))
                    cur.execute(query, (1013,"2026-03-06","10:00:00","22:00:00"))
                    cur.execute(query, (1001,"2026-03-07","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-03-07","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-03-07","10:00:00","22:00:00"))
                    cur.execute(query, (1013,"2026-03-07","10:00:00","22:00:00"))
                    cur.execute(query, (1001,"2026-03-08","10:00:00","22:00:00"))
                    cur.execute(query, (1005,"2026-03-08","10:00:00","22:00:00"))
                    cur.execute(query, (1009,"2026-03-08","10:00:00","22:00:00"))
                    cur.execute(query, (1013,"2026-03-08","10:00:00","22:00:00"))
        # salon_id = 3
                    cur.execute(query, (1002,"2026-02-16","09:00:00","20:00:00"))
                    cur.execute(query, (1002,"2026-02-17","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-02-16","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-02-17","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-02-18","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-02-18","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-02-19","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-02-20","09:00:00","20:00:00"))
                    cur.execute(query, (1014,"2026-02-19","09:00:00","20:00:00"))
                    cur.execute(query, (1014,"2026-02-20","09:00:00","20:00:00"))
                    cur.execute(query, (1002,"2026-02-21","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-02-21","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-02-21","09:00:00","20:00:00"))
                    cur.execute(query, (1014,"2026-02-21","09:00:00","20:00:00"))
                    cur.execute(query, (1002,"2026-02-22","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-02-22","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-02-22","09:00:00","20:00:00"))
                    cur.execute(query, (1014,"2026-02-22","09:00:00","20:00:00"))
                    cur.execute(query, (1002,"2026-02-23","09:00:00","20:00:00"))
                    cur.execute(query, (1002,"2026-02-24","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-02-23","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-02-24","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-02-25","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-02-25","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-02-26","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-02-27","09:00:00","20:00:00"))
                    cur.execute(query, (1014,"2026-02-26","09:00:00","20:00:00"))
                    cur.execute(query, (1014,"2026-02-27","09:00:00","20:00:00"))
                    cur.execute(query, (1002,"2026-02-28","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-02-28","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-02-28","09:00:00","20:00:00"))
                    cur.execute(query, (1014,"2026-02-28","09:00:00","20:00:00"))
                    cur.execute(query, (1002,"2026-03-01","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-03-01","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-03-01","09:00:00","20:00:00"))
                    cur.execute(query, (1014,"2026-03-01","09:00:00","20:00:00"))
                    cur.execute(query, (1002,"2026-03-02","09:00:00","20:00:00"))
                    cur.execute(query, (1002,"2026-03-03","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-03-02","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-03-03","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-03-04","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-03-04","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-03-05","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-03-06","09:00:00","20:00:00"))
                    cur.execute(query, (1014,"2026-03-05","09:00:00","20:00:00"))
                    cur.execute(query, (1014,"2026-03-06","09:00:00","20:00:00"))
                    cur.execute(query, (1002,"2026-03-07","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-03-07","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-03-07","09:00:00","20:00:00"))
                    cur.execute(query, (1014,"2026-03-07","09:00:00","20:00:00"))
                    cur.execute(query, (1002,"2026-03-08","09:00:00","20:00:00"))
                    cur.execute(query, (1006,"2026-03-08","09:00:00","20:00:00"))
                    cur.execute(query, (1010,"2026-03-08","09:00:00","20:00:00"))
                    cur.execute(query, (1014,"2026-03-08","09:00:00","20:00:00"))
        # salon_id = 4
                    cur.execute(query, (1003,"2026-02-16","09:00:00","18:00:00"))
                    cur.execute(query, (1003,"2026-02-17","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-02-16","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-02-17","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-02-18","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-02-18","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-02-19","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-02-20","09:00:00","18:00:00"))
                    cur.execute(query, (1015,"2026-02-19","09:00:00","18:00:00"))
                    cur.execute(query, (1015,"2026-02-20","09:00:00","18:00:00"))
                    cur.execute(query, (1003,"2026-02-21","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-02-21","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-02-21","09:00:00","18:00:00"))
                    cur.execute(query, (1015,"2026-02-21","09:00:00","18:00:00"))
                    cur.execute(query, (1003,"2026-02-22","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-02-22","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-02-22","09:00:00","18:00:00"))
                    cur.execute(query, (1015,"2026-02-22","09:00:00","18:00:00"))
                    cur.execute(query, (1003,"2026-02-23","09:00:00","18:00:00"))
                    cur.execute(query, (1003,"2026-02-24","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-02-23","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-02-24","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-02-25","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-02-25","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-02-26","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-02-27","09:00:00","18:00:00"))
                    cur.execute(query, (1015,"2026-02-26","09:00:00","18:00:00"))
                    cur.execute(query, (1015,"2026-02-27","09:00:00","18:00:00"))
                    cur.execute(query, (1003,"2026-02-28","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-02-28","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-02-28","09:00:00","18:00:00"))
                    cur.execute(query, (1015,"2026-02-28","09:00:00","18:00:00"))
                    cur.execute(query, (1003,"2026-03-01","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-03-01","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-03-01","09:00:00","18:00:00"))
                    cur.execute(query, (1015,"2026-03-01","09:00:00","18:00:00"))
                    cur.execute(query, (1003,"2026-03-02","09:00:00","18:00:00"))
                    cur.execute(query, (1003,"2026-03-03","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-03-02","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-03-03","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-03-04","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-03-04","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-03-05","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-03-06","09:00:00","18:00:00"))
                    cur.execute(query, (1015,"2026-03-05","09:00:00","18:00:00"))
                    cur.execute(query, (1015,"2026-03-06","09:00:00","18:00:00"))
                    cur.execute(query, (1003,"2026-03-07","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-03-07","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-03-07","09:00:00","18:00:00"))
                    cur.execute(query, (1015,"2026-03-07","09:00:00","18:00:00"))
                    cur.execute(query, (1003,"2026-03-08","09:00:00","18:00:00"))
                    cur.execute(query, (1007,"2026-03-08","09:00:00","18:00:00"))
                    cur.execute(query, (1011,"2026-03-08","09:00:00","18:00:00"))
                    cur.execute(query, (1015,"2026-03-08","09:00:00","18:00:00"))
        # salon_id = 5
                    cur.execute(query, (1004,"2026-02-16","10:00:00","19:00:00"))
                    cur.execute(query, (1004,"2026-02-17","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-02-16","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-02-17","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-02-18","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-02-18","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-02-19","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-02-20","10:00:00","19:00:00"))
                    cur.execute(query, (1016,"2026-02-19","10:00:00","19:00:00"))
                    cur.execute(query, (1016,"2026-02-20","10:00:00","19:00:00"))
                    cur.execute(query, (1004,"2026-02-21","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-02-21","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-02-21","10:00:00","19:00:00"))
                    cur.execute(query, (1016,"2026-02-21","10:00:00","19:00:00"))
                    cur.execute(query, (1004,"2026-02-22","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-02-22","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-02-22","10:00:00","19:00:00"))
                    cur.execute(query, (1016,"2026-02-22","10:00:00","19:00:00"))
                    cur.execute(query, (1004,"2026-02-23","10:00:00","19:00:00"))
                    cur.execute(query, (1004,"2026-02-24","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-02-23","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-02-24","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-02-25","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-02-25","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-02-26","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-02-27","10:00:00","19:00:00"))
                    cur.execute(query, (1016,"2026-02-26","10:00:00","19:00:00"))
                    cur.execute(query, (1016,"2026-02-27","10:00:00","19:00:00"))
                    cur.execute(query, (1004,"2026-02-28","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-02-28","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-02-28","10:00:00","19:00:00"))
                    cur.execute(query, (1016,"2026-02-28","10:00:00","19:00:00"))
                    cur.execute(query, (1004,"2026-03-01","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-03-01","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-03-01","10:00:00","19:00:00"))
                    cur.execute(query, (1016,"2026-03-01","10:00:00","19:00:00"))
                    cur.execute(query, (1004,"2026-03-02","10:00:00","19:00:00"))
                    cur.execute(query, (1004,"2026-03-03","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-03-02","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-03-03","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-03-04","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-03-04","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-03-05","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-03-06","10:00:00","19:00:00"))
                    cur.execute(query, (1016,"2026-03-05","10:00:00","19:00:00"))
                    cur.execute(query, (1016,"2026-03-06","10:00:00","19:00:00"))
                    cur.execute(query, (1004,"2026-03-07","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-03-07","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-03-07","10:00:00","19:00:00"))
                    cur.execute(query, (1016,"2026-03-07","10:00:00","19:00:00"))
                    cur.execute(query, (1004,"2026-03-08","10:00:00","19:00:00"))
                    cur.execute(query, (1008,"2026-03-08","10:00:00","19:00:00"))
                    cur.execute(query, (1012,"2026-03-08","10:00:00","19:00:00"))
                    cur.execute(query, (1016,"2026-03-08","10:00:00","19:00:00"))
                    print("Сотрудникам выставлен график.")
                    cur.close()
                cnx.close()
        except Exception as e:
            print(str(e))

    def initialization_db(self):
        """Полная инициализация базы данных"""
        self.create_database()
        print("database has been created.")
        self.create_table()
        print("tables have been established.")
        self.starting_filling()
        print("filling's ready.")

    def get_day(self, staff_id: int, tz:str, start: int = 1, end: int = 14):
        query = """
        SELECT sch_date, TIME_FORMAT(sch_st, '%H:%i') as beg, TIME_FORMAT(sch_end, '%H:%i') as fin FROM schedule WHERE staff_id = %s 
        AND DATEDIFF(sch_date, CONVERT_TZ(NOW(), @@GLOBAL.time_zone, %s)) BETWEEN %s AND %s
        ORDER BY sch_date;"""
        try:
            data = self.get_all(query, (staff_id,tz,start,end))
            return data
        except Exception:
            raise
    
    def get_missing_type(self,staff_id:int,page:int):
        query = """WITH a AS ((SELECT id, name, staff_lvl FROM proc_type
        ORDER BY name) EXCEPT (
        SELECT id, name, staff_lvl FROM proc_type
        JOIN staff_type ON type_id = id
        WHERE staff_id = %s))
        SELECT * FROM a LIMIT %s OFFSET %s;
        """
        try:
            data = self.get_all(query, (staff_id, pagevolume, pagevolume*page))
            return data
        except Exception:
            raise
    
    def get_mt_lp(self,staff_id:int):
        query = """WITH a AS ((SELECT id FROM proc_type) EXCEPT (
        SELECT id FROM proc_type
        JOIN staff_type ON type_id = id
        WHERE staff_id = %s))
        SELECT COUNT(*) as cnt FROM a;
        """
        try:
            data = self.get_single(query,(staff_id,))
            if data is None:
                raise Exception
            return ((data["cnt"]-1)//pagevolume)
        except Exception:
            raise


def initialize_database():
    print("Инициализация базы данных...")
    data_manager = DataManager()
    try:
        data_manager.initialization_db()
        print("База данных успешно инициализирована")
    except Exception as e:
        logger.exception("Ошибка при инициализации базы данных: %s", e)
        # Повторная попытка через 5 секунд (не более 3 попыток)
        retry_left = int(os.getenv("INIT_DB_RETRY_COUNT", "3"))
        if retry_left > 1:
            os.environ["INIT_DB_RETRY_COUNT"] = str(retry_left - 1)
            time.sleep(5)
            initialize_database()
        else:
            raise


# Comment the line below after initialization.
initialize_database()