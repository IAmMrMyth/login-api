from kavenegar import KavenegarAPI

API_TOKEN = ""
TEMPLATE_NAME = "verify"
TYPE = "sms"


def send_otp(
    phone_number, otp, api_token=API_TOKEN, template_name=TEMPLATE_NAME, type=TYPE
):
    try:
        api = KavenegarAPI(api_token)

        params = {
            "receptor": phone_number,
            "template": template_name,
            "token": otp,
            "type": type,
        }
        response = api.verify_lookup(params)
        status = response.get("status", False)
        if status == 5:
            return True

    except Exception as e:
        return None
