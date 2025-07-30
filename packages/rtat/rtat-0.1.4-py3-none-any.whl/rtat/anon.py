import pymysql
import sys


def get_apid(cursor, pid):
    query = "SELECT APID FROM Analysis.Matching WHERE PID=%s"
    cursor.execute(query, (pid,))
    result = cursor.fetchone()
    return result[0] if result else None


def insert_apid(cursor, pid):
    query = "INSERT INTO Analysis.Matching (PID) VALUES (%s)"
    cursor.execute(query, (pid,))
    return cursor.lastrowid

def get_plan_name(cursor, pid, plan):
    query = "SELECT APlan FROM Analysis.Matching_Plans WHERE OPID=%s AND OPlan=%s"
    cursor.execute(query, (pid, plan))
    result = cursor.fetchone()
    return result[0] if result else None


def get_last_plan_name(cursor, pid):
    query = "SELECT APlan FROM Analysis.Matching_Plans WHERE OPID=%s ORDER BY APlan DESC LIMIT 1"
    cursor.execute(query, (pid,))
    result = cursor.fetchone()
    return result[0] if result else None


def insert_plan(cursor, pid, apid, plan, aplan_name):
    query = "INSERT INTO Analysis.Matching_Plans (OPID, APID, OPlan, APlan) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (pid, apid, plan, aplan_name))

def a2o(cursor, apid, aplan=None):
    if not aplan:
       query = "SELECT PID FROM Analysis.Matching WHERE APID=%s"
       cursor.execute(query, (apid))
       result = cursor.fetchone()
       return result if result else None
    else:
       query="SELECT OPID, OPlan FROM Analysis.Matching_Plans WHERE APID='%s' AND APlan LIKE %s"
       cursor.execute(query, (apid,aplan))
       result = cursor.fetchone()
       return result if result else None


def o2a(cursor, pid, plan=None):
    print(" pid ",pid)
    print(" plan ",plan)
    if not plan:
       query = "SELECT APID FROM Analysis.Matching WHERE PID=%s"
       cursor.execute(query, (pid))
       result = cursor.fetchone()
       return result if result else None
    else:
       query="SELECT APID, APlan FROM Analysis.Matching_Plans WHERE OPID=%s AND OPlan LIKE %s"
       cursor.execute(query, (pid,plan))
       result = cursor.fetchone()
       return result if result else None

def getAnonymized (db, pid, plan=None):

    cursor = db.cursor()

    apid = get_apid(cursor, pid)
    if not apid:
        insert_apid(cursor, pid)
        db.commit()
        apid = get_apid(cursor, pid)

    if plan:
        aplan_name = get_plan_name(cursor, pid, plan)

        if not aplan_name:
            last_plan_name = get_last_plan_name(cursor, pid)
            if last_plan_name:
                p_number = int(last_plan_name[-3:]) + 1
                aplan_name = f"plan{p_number:03d}"
            else:
                aplan_name = "plan001"

            insert_plan(cursor, pid, apid, plan, aplan_name)
            db.commit()

        return apid+"-"+aplan_name

    else:
        return apid
