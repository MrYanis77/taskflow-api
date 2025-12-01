def log_kpi(request, reponse):
    method = request.method
    endpoint = request.path
    status = reponse.status_code
    duration = reponse.get('X-Process-Time', '0.000s')
    with open('logs/kip.log','a') as f:
        f.write(f"{method} {endpoint} {status} {duration}\n")