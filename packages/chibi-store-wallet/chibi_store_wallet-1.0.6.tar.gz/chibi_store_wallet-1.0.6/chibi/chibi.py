import requests
import re

def chibi(code: str, phone: str) -> dict:
    code = re.sub(r"https://gift\.truemoney\.com/campaign/\?v=", "", code)

    url = f"https://gift.truemoney.com/campaign/vouchers/{code}/redeem"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36 Edg/84.0.522.52",
        "Content-Type": "application/json"
    }
    payload = {"mobile": phone}

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            status_code = data.get("status", {}).get("code", "")
            if status_code == "SUCCESS":
                amount = data["data"]["voucher"]["amount_baht"]
                name_owner = data["data"]["owner_profile"]["full_name"]
                link = f"https://gift.truemoney.com/campaign/?v={code}"
                return {
                    "ok": 1001,
                    "message": f"ได้รับเงินจากซองอั่งเปาแล้วจำนวน {amount}",
                    "amount": amount,
                    "name_owner": name_owner,
                    "code": link
                }
            else:
                return {
                    "ok": -1,
                    "message": "เกิดข้อผิดพลาดที่ไม่รู้จัก"
                }

        else:
            return _handle_error(response)

    except Exception as e:
        return {
            "ok": -1,
            "message": f"เกิดข้อผิดพลาด: {str(e)}"
        }

def _handle_error(response):
    try:
        data = response.json()
        code = data.get("status", {}).get("code", "")
    except:
        code = ""

    error_map = {
        "CANNOT_GET_OWN_VOUCHER": (1002, "รับซองตัวเองไม่ได้"),
        "BAD_PARAM": (1003, "เบอร์โทรศัพท์ผู้รับเงินไม่ถูกต้อง"),
        "VOUCHER_OUT_OF_STOCK": (1004, "มีคนรับซองอั่งเปาไปแล้ว"),
        "VOUCHER_NOT_FOUND": (1005, "ไม่พบซองนี้ในระบบ หรือ URL ผิด"),
        "TARGET_USER_NOT_FOUND": (1006, "ไม่พบเบอร์นี้ในระบบ"),
        "VOUCHER_EXPIRED": (1007, "ซองวอเลทนี้หมดอายุแล้ว"),
        "INTERNAL_ERROR": (1008, "ไม่พบซองอั่งเปาในระบบ")
    }

    if code in error_map:
        err_code, err_msg = error_map[code]
    else:
        err_code, err_msg = (-1, "เกิดข้อผิดพลาดที่ไม่รู้จัก")

    return {
        "errorData": err_code,
        "mes_err": err_msg
    }
