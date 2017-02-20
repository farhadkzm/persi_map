import requests


def check_recaptcha(payload):
    recaptcha_request_payload = {'secret': '6LfiNhUUAAAAAO7owWIr66Fo8l_pMFASfhYvxZxF',
                                 'response': payload.get('recaptcha')}
    r = requests.post('https://www.google.com/recaptcha/api/siteverify',
                      data=recaptcha_request_payload)
    return r.json().get('success')
