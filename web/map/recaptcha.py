import requests


def check(recaptcha):
    recaptcha_request_payload = {'secret': '6LfiNhUUAAAAAO7owWIr66Fo8l_pMFASfhYvxZxF',
                                 'response': recaptcha}
    r = requests.post('https://www.google.com/recaptcha/api/siteverify',
                      data=recaptcha_request_payload)
    return r.json().get('success')
