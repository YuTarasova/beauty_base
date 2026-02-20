from fastapi import APIRouter, HTTPException, Form, Query, Depends, Body
from db.database import DataManager
from api.utils import (create_access_token, require_client_role, require_admin,
                       require_cosmetologist, require_head,require_acc, PaginatedResponse,
                       password_hash)

data_manager = DataManager()
router = APIRouter()
ph_min = 10000000000
ph_max = 99999999999
salon_id_max = 300
smallint_max = 65535

#           Client
@router.post("/cli/register")  # add auto-login
async def register_client(first_name: str = Form(), last_name: str = Form(None),
                          phone: int = Form(ge=ph_min, le=ph_max),
                          password: str = Form(min_length=6, max_length=32)):
    query = """
    INSERT INTO client (first_name, last_name, phone, password_hash)
    VALUES (%s, %s, %s, %s);"""
    try:
        pass_hash = password_hash(password)
        data_manager.exec(query, (first_name, last_name,
                                  phone, pass_hash))
        return {"detail": "Регистрация прошла успешно."}
    except Exception:
        raise HTTPException(status_code=400,
                            detail="Не удалось зарегистрировать пользователя.")


@router.post("/cli/login")
async def login_client(phone: int = Form(ge=ph_min, le=ph_max),
                       password: str = Form(min_length=6, max_length=32)):
    query = """
    SELECT id, phone, password_hash FROM client
    WHERE phone = %s;"""
    try:
        pass_hash = password_hash(password)
        client = data_manager.get_single(query, (phone,))
        query = ""
        if client is None:
            query = "Отсутствует пользователь с данным номером."
            raise Exception
        if client["password_hash"] == pass_hash:
            access_token = create_access_token(client["id"], "client")
            return {"token": "bearer " + access_token}
        query = "Неверный пароль."
        raise Exception
    except Exception:
        raise HTTPException(status_code=401, detail=query if query else "Не удалось авторизовать пользователя.")


@router.get("/cli/city")
async def get_city(page: int = Query(ge=0)):
    try:
        data = data_manager.get_page("*", "city ORDER BY city_name", page=page)
        page_num = data_manager.get_last_page("city")
        return PaginatedResponse(items=data, last=page_num)
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось получить список городов.")


@router.get("/cli/salon")
async def get_salon(city_id: int = Query(ge=0, le=salon_id_max)):
    query = """
    SELECT id, address FROM salon WHERE city_id = %s ORDER BY address;"""
    try:
        salon = data_manager.get_all(query, (city_id,))
        return {"items": salon}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить список салонов.")


# route 1
@router.get("/cli/staff")
async def get_client_staff(salon_id: int = Query(ge=0, le=salon_id_max)):
    query = """
    SELECT id, first_name, last_name FROM staff
    WHERE salon_id = %s AND id > 1000 ORDER BY last_name, first_name;"""
    try:
        staff = data_manager.get_all(query, (salon_id,))
        return {"items": staff}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить сведения о персонале.")


@router.get("/typebystaff")
async def get_typebystaff(staff_id: int = Query(gt=1000, le=smallint_max)):
    query = """
    SELECT id, name, price, TIME_FORMAT(duration, '%H ч, %i мин') as dur FROM proc_type
    JOIN staff_type ON id = type_id
    WHERE staff_id = %s ORDER BY name;"""
    try:
        proc_type = data_manager.get_all(query, (staff_id,))
        return {"items": proc_type}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить сведения об этом сотруднике.")


# route 2
@router.get("/cli/type")
async def get_client_type(salon_id: int = Query(ge=0, le=salon_id_max)):
    query = """
    SELECT DISTINCT proc_type.id, name,
    price, TIME_FORMAT(duration, '%H ч, %i мин') as dur FROM proc_type
    JOIN staff_type ON proc_type.id = type_id
    JOIN staff ON staff.id = staff_id
    WHERE salon_id = %s ORDER BY name, dur;
    """
    try:
        proc_type = data_manager.get_all(query, (salon_id,))
        return {"items": proc_type}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить сведения об услугах данного салона.")


@router.get("/cli/staffbytype")
async def get_client_staffbytype(salon_id: int = Query(ge=0, le=salon_id_max),
                                   type_id: int = Query(ge=0, le=smallint_max)):
    query = """
    SELECT id, first_name, last_name FROM staff
    JOIN staff_type ON staff_id = id
    AND type_id = %s AND salon_id = %s ORDER BY last_name, first_name;"""
    try:
        staff = data_manager.get_all(query, (type_id, salon_id))
        return {"items": staff}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить сведения о персонале данного салона.")

# continuation
@router.get("/cli/day")
async def get_client_day(staff_id: int = Query(gt=1000, le=smallint_max), tz: str = Query(min_length=5,max_length=6)):
    try:
        day = data_manager.get_day(staff_id, tz)
        return {"items": day}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить рабочие дни данного сотрудника.")


@router.get("/time")
async def get_client_time(staff_id: int = Query(gt=1000, le=smallint_max), day: str = Query(),
                          type_id: int = Query(ge=0, le=smallint_max)):
    query = "CALL get_time_intervals(%s, %s, %s);"
    try:
        proced_time = data_manager.get_all(query, (staff_id, type_id, day))
        return {"items": proced_time}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить свободное время для записи.")


@router.post("/cli/reserve")
async def client_reserve(staff_id: int = Body(gt=1000, le=smallint_max), res_date: str = Body(), res_st: str = Body(),
                         type_id: int = Body(ge=0, le=smallint_max), user=Depends(require_client_role)):
    query = "CALL make_rsv(%s, %s, %s, %s, %s);"
    try:
        data_manager.exec(query, (staff_id, type_id, user.id, res_date,res_st))
        return {"detail": "Запись успешно создана."}
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось сделать запись.")


@router.get("/cli/reservation")
async def get_client_reservation(user=Depends(require_client_role)):
    query = """
    SELECT res_date, TIME_FORMAT(res_st, '%H:%i') as beg, proc_type.name,
    price, staff.first_name, staff.last_name, address
    FROM reservation
    JOIN staff ON staff_id = staff.id
    JOIN salon ON salon_id = salon.id
    JOIN proc_type ON type_id = proc_type.id
    WHERE client_id = %s AND status = 'active'
    ORDER BY res_date, beg;
    """
    try:
        reservation = data_manager.get_all(query, (user.id,))
        return {"items": reservation}
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось получить список активных записей.")


#               STAFF
@router.post("/stf/login")
async def login_staff(staff_id: int = Form(), password: str = Form(min_length=6, max_length=32)):
    query = """
    SELECT password_hash, salon_id, tz FROM staff 
    JOIN salon ON salon_id = salon.id 
    JOIN city ON city_id = city.id WHERE staff.id = %s;"""
    msg = ""
    try:
        pass_hash = password_hash(password)
        staff = data_manager.get_single(query, (staff_id,))
        if staff is None:
            msg = "Неверный ID."
        elif staff["password_hash"] != pass_hash:
            msg = "Неверный пароль."
        else:
            access_token = create_access_token(staff_id, "staff", tz=staff["tz"], salon_id=staff["salon_id"])
            return {"token": "bearer " + access_token}
        raise Exception
    except Exception:
        raise HTTPException(status_code=401,
                            detail=msg if msg else "Не удалось авторизовать пользователя.")


@router.get("/stf/day")
async def get_staff_day(user=Depends(require_cosmetologist)):
    try:
        day = data_manager.get_day(user.id, user.tz, start=0)
        return {"items": day}
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось получить рабочие дни.")


@router.get("/stf/reservation")
async def get_staff_reservation(day: str = Query(),
                                user=Depends(require_cosmetologist)):
    query = """
    SELECT TIME_FORMAT(res_st, '%H:%i') as beg, name FROM reservation
    JOIN proc_type ON type_id = proc_type.id
    WHERE staff_id = %s AND res_date = %s
    ORDER BY beg;
    """
    try:
        reservation = data_manager.get_all(query, (user.id, day))
        return {"items": reservation}
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось получить список записей.")


#               ADMIN
@router.get("/adm/day")
async def get_admin_day(user=Depends(require_admin)):
    query = """
    SELECT distinct sch_date FROM schedule
    JOIN staff ON staff.id = staff_id WHERE salon_id = %s 
    AND DATEDIFF(sch_date, CONVERT_TZ(NOW(), @@GLOBAL.time_zone, %s)) BETWEEN 0 AND 14
    ORDER BY sch_date;"""
    try:
        day = data_manager.get_all(query, (user.salon_id, user.tz))
        return {"items": day}
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось получить рабочие дни.")


@router.get("/adm/reservation")
async def get_admin_reservation(day: str = Query(),
                                user=Depends(require_admin)):
    query = """
    SELECT reservation.id, TIME_FORMAT(res_st, '%H:%i') as beg, staff_id, client_id, staff.first_name as sfn, staff.last_name as sln,
    client.first_name as cfn, client.last_name as cln, client.phone, status FROM reservation JOIN staff
    ON staff_id = staff.id JOIN client ON client_id = client.id
    WHERE res_date = %s ORDER BY beg;"""
    try:
        reservation = data_manager.get_all(query, (day,))
        return {"items": reservation}
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось получить список записей.")


@router.post("/adm/status")
async def update_status(status: str = Body(), res_id: int = Body(ge=0,le=4294967295),
                        user=Depends(require_admin)):
    query = """
    UPDATE reservation SET status = %s WHERE id = %s;"""
    try:
        data_manager.exec(query, (status, res_id))
        return {"detail": "Статус был изменён."}
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось изменить статус.")


# route 1
@router.get("/adm/staff")
async def get_admin_staff(user=Depends(require_admin)):
    query = """
    SELECT id, first_name, last_name FROM staff
    WHERE salon_id = %s AND id > 1000 ORDER BY last_name, first_name;"""
    try:
        staff = data_manager.get_all(query, (user.salon_id,))
        return {"items": staff}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить сведения о персонале.")


# route 2
@router.get("/adm/type")
async def get_admin_type(user=Depends(require_admin)):
    query = """
    SELECT DISTINCT proc_type.id, name,
    price, TIME_FORMAT(duration, '%H ч, %i мин') as dur FROM proc_type
    JOIN staff_type ON proc_type.id = type_id
    JOIN staff ON staff.id = staff_id
    WHERE salon_id = %s ORDER BY name, dur;
    """
    try:
        proc_type = data_manager.get_all(query, (user.salon_id,))
        return {"items": proc_type}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить сведения об услугах данного салона.")


@router.get("/adm/staffbytype")
async def get_admin_staffbytype(type_id: int = Query(ge=0, le=smallint_max),user=Depends(require_admin)):
    query = """
    SELECT id, first_name, last_name FROM staff
    JOIN staff_type ON staff_id = id
    AND type_id = %s AND salon_id = %s ORDER BY last_name, first_name;"""
    try:
        staff = data_manager.get_all(query, (type_id, user.salon_id))
        return {"items": staff}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить сведения о персонале данного салона.")


@router.get("/adm/dayofstaff")
async def get_admin_dayofstaff(staff_id: int = Query(gt=1000, le=smallint_max), user=Depends(require_admin)):
    try:
        day = data_manager.get_day(staff_id, user.tz, start=0)
        return {"items": day}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить рабочие дни данного сотрудника.")


@router.post("/adm/reserve")
async def admin_reserve(staff_id: int = Body(gt=1000, le=smallint_max),
                        phone: int = Body(ge=ph_min, le=ph_max),
                        res_date: str = Body(), res_st: str = Body(),
                        type_id: int = Body(ge=0, le=smallint_max), user=Depends(require_admin)):
    query = "SELECT id FROM client WHERE phone = %s;"
    try:
        data = data_manager.get_single(query, (phone,))
        if data is not None:
            query = "CALL make_rsv(%s, %s, %s, %s, %s);"
            data_manager.exec(query, (staff_id, type_id, data["id"], res_date,res_st))
            return {"detail": "Запись успешно создана."}
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось сделать запись.")


#               HEAD
@router.post("/head/register")
async def head_register(staff_id: int = Form(gt=0, le=smallint_max), first_name: str = Form(),
                        last_name: str = Form(), fathers_name: str = Form(None),
                        phone: int = Form(ge=ph_min, le=ph_max),
                        password: str = Form(min_length=6, max_length=32),
                        user=Depends(require_head)):
    query = """
    INSERT INTO staff VALUES (%s,%s,%s,%s,%s,%s,%s);"""
    try:
        pass_hash = password_hash(password)
        data_manager.exec(query, (staff_id, user.salon_id, first_name, last_name,
                                  fathers_name, phone, pass_hash))
        return {"detail": "Сотрудник внесён."}
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось сделать внести сотрудника.")


@router.get("/head/staff")
async def get_head_staff(user=Depends(require_head)):
    query = """
    SELECT id, first_name, last_name, fathers_name FROM staff
    WHERE salon_id = %s AND id > 1000
    ORDER BY last_name,first_name;"""
    try:
        staff = data_manager.get_all(query, (user.salon_id,))
        return {"items": staff}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить сведения о персонале.")

@router.get("/head/type")
async def get_head_type(staff_id: int = Query(gt=1000, le=smallint_max),
                        page: int = Query(ge=0), user=Depends(require_head)):
    try:
        data = data_manager.get_missing_type(staff_id, page=page)
        page_num = data_manager.get_mt_lp(staff_id)
        return PaginatedResponse(items=data, last=page_num)
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось получить сведения о существующих услугах.")


@router.get("/head/stafftype")
async def get_head_stafftype(staff_id: int = Query(gt=1000, le=smallint_max), user=Depends(require_head)):
    query = """
    SELECT id, name, staff_lvl FROM proc_type
    JOIN staff_type ON type_id = id
    WHERE staff_id = %s 
    ORDER BY name;"""
    try:
        proc_type = data_manager.get_all(query, (staff_id,))
        return {"items": proc_type}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить сведения о квалификации.")


@router.post("/head/type")
async def add_type(staff_id: int = Body(gt=1000, le=smallint_max), type_id: int = Body(ge=0, le=smallint_max),
                   user=Depends(require_head)):
    query = "INSERT INTO staff_type VALUES (%s,%s);"
    try:
        data_manager.exec(query, (staff_id, type_id))
        return {"detail": "Квалификация добавлена."}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось добавить квалификацию.")


@router.delete("/head/type")
async def delete_type(staff_id: int = Body(gt=1000, le=smallint_max), type_id: int = Body(ge=0, le=smallint_max),
                      user=Depends(require_head)):
    query = "DELETE FROM staff_type WHERE staff_id = %s AND type_id = %s;"
    try:
        data_manager.exec(query, (staff_id, type_id))
        return {"detail": "Квалификация удалена."}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось удалить квалификацию.")


@router.get("/head/day")
async def get_head_day(staff_id: int = Query(gt=1000, le=smallint_max), start: int = Query(1, ge=0),
                       dur: int = Query(14, ge=1), user=Depends(require_head)):
    try:
        day = data_manager.get_day(staff_id, user.tz, start=start, end=start+dur-1)
        return {"items": day}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить расписание.")


@router.post("/head/day")
async def add_day(staff_id: int = Body(gt=1000, le=smallint_max), sch_date: str = Body(),sch_st: str = Body(),
                  sch_end: str = Body(), user=Depends(require_head)):
    query = "INSERT INTO schedule VALUES (%s,%s,%s,%s);"
    try:
        data_manager.exec(query, (staff_id, sch_date,sch_st, sch_end))
        return {"detail": "День добавлен."}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось добавить день.")


@router.delete("/head/day")
async def delete_day(staff_id: int = Body(gt=1000, le=smallint_max), date: str = Body(),
                     user=Depends(require_head)):
    query = """
    START TRANSACTION;
    UPDATE reservation SET status = 'cancelled' WHERE staff_id = %(id)s
    AND res_date = %(day)s AND status = 'active';
    DELETE FROM schedule WHERE staff_id = %(id)s
    AND sch_date = %(day)s;
    COMMIT;
    """
    try:
        data_manager.exec(query, {'id': staff_id, 'day': date})
        return {"detail": "День удалён."}
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось удалить день.")


@router.get("/head/reservation")
async def get_head_reservation(res_start: str = Query(), res_end: str = Query(),
                               page: int = Query(ge=0), user=Depends(require_head)):
    col = """reservation.id,staff_id,staff.first_name as sfn,staff.last_name as sln,client.phone,
    res_date, TIME_FORMAT(res_st, '%H:%i') as beg,proc_type.name,type_id,status"""
    tab = f"""reservation JOIN staff ON staff_id = staff.id
    JOIN client ON client_id = client.id JOIN proc_type ON type_id = proc_type.id
    WHERE salon_id = {user.salon_id} AND status <> 'active' 
    AND status <> 'completed' AND res_date BETWEEN '{res_start}' AND '{res_end}'
    ORDER BY res_date, beg"""
    try:
        data = data_manager.get_page(col, tab, page=page)
        tab = f"""reservation JOIN staff ON staff_id = staff.id
    WHERE salon_id = {user.salon_id} AND status <> 'active' 
    AND status <> 'completed' AND res_date BETWEEN '{res_start}' AND '{res_end}'
    """
        page_num = data_manager.get_last_page(tab)
        return PaginatedResponse(items=data, last=page_num)
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить список записей.")

#               ACCOUNTANT
@router.get("/acc/hour")
async def get_acc_hour(sch_start: str = Query(), sch_end: str = Query(),
                              page: int = Query(ge=0), user=Depends(require_acc)):
    col = "staff_id, SUM(HOUR(SUBTIME(sch_end, sch_st))) as hour, SUM(MINUTE(SUBTIME(sch_end, sch_st))) as min"
    tab = f"""schedule
    WHERE sch_date BETWEEN '{sch_start}' AND '{sch_end}'
    GROUP BY staff_id ORDER BY staff_id"""
    try:
        data = data_manager.get_page(col, tab, page=page)
        tab = f"""schedule
    WHERE sch_date BETWEEN '{sch_start}' AND '{sch_end}'"""
        page_num = data_manager.get_last_page(tab, col="DISTINCT staff_id")
        return PaginatedResponse(items=data, last=page_num)
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить отработанные часы.")

@router.get("/acc/income")
async def get_acc_income(start: str = Query(), end: str = Query(),
                               page: int = Query(ge=0), user=Depends(require_acc)):
    col = "staff_id, SUM(price) as income"
    tab = f"""reservation JOIN proc_type ON type_id = proc_type.id
    WHERE status = 'completed' AND res_date BETWEEN '{start}' AND '{end}'
    GROUP BY staff_id ORDER BY staff_id"""
    try:
        data = data_manager.get_page(col, tab, page=page)
        tab = f"""reservation
    WHERE status = 'completed' AND res_date BETWEEN '{start}' AND '{end}'
    """
        page_num = data_manager.get_last_page(tab,col="DISTINCT staff_id")
        return PaginatedResponse(items=data, last=page_num)
    except Exception:
        raise HTTPException(status_code=404, detail="Не удалось получить выручку.")






