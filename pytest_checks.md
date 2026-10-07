pytest -q

=============================================================== ERRORS ===============================================================
________________________________________________ ERROR collecting test_admin_route.py ________________________________________________
venv\Lib\site-packages\urllib3\connection.py:204: in _new_conn
    sock = connection.create_connection(
venv\Lib\site-packages\urllib3\util\connection.py:85: in create_connection
    raise err
venv\Lib\site-packages\urllib3\util\connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\urllib3\connectionpool.py:788: in urlopen
    response = self._make_request(
venv\Lib\site-packages\urllib3\connectionpool.py:493: in _make_request
    conn.request(
venv\Lib\site-packages\urllib3\connection.py:500: in request
    self.endheaders()
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1331: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1091: in _send_output
    self.send(msg)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1035: in send
    self.connect()
venv\Lib\site-packages\urllib3\connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
venv\Lib\site-packages\urllib3\connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\requests\adapters.py:696: in send
    resp = conn.urlopen(
venv\Lib\site-packages\urllib3\connectionpool.py:842: in urlopen
    retries = retries.increment(
venv\Lib\site-packages\urllib3\util\retry.py:543: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))

During handling of the above exception, another exception occurred:
test_admin_route.py:5: in <module>
    login = requests.post(
venv\Lib\site-packages\requests\api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:784: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\adapters.py:729: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))
_________________________________________________ ERROR collecting test_auth_api.py __________________________________________________
venv\Lib\site-packages\urllib3\connection.py:204: in _new_conn
    sock = connection.create_connection(
venv\Lib\site-packages\urllib3\util\connection.py:85: in create_connection
    raise err
venv\Lib\site-packages\urllib3\util\connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\urllib3\connectionpool.py:788: in urlopen
    response = self._make_request(
venv\Lib\site-packages\urllib3\connectionpool.py:493: in _make_request
    conn.request(
venv\Lib\site-packages\urllib3\connection.py:500: in request
    self.endheaders()
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1331: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1091: in _send_output
    self.send(msg)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1035: in send
    self.connect()
venv\Lib\site-packages\urllib3\connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
venv\Lib\site-packages\urllib3\connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\requests\adapters.py:696: in send
    resp = conn.urlopen(
venv\Lib\site-packages\urllib3\connectionpool.py:842: in urlopen
    retries = retries.increment(
venv\Lib\site-packages\urllib3\util\retry.py:543: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/register (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))

During handling of the above exception, another exception occurred:
test_auth_api.py:11: in <module>
    response = requests.post(
venv\Lib\site-packages\requests\api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:784: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\adapters.py:729: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/register (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] Noconnection could be made because the target machine actively refused it"))
______________________________________________ ERROR collecting test_auth_dependency.py ______________________________________________
ImportError while importing test module 'C:\Users\akhil\ai-workspace-v2\backend\test_auth_dependency.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
..\..\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
test_auth_dependency.py:2: in <module>
    from app.core.auth import get_current_user_payload
E   ImportError: cannot import name 'get_current_user_payload' from 'app.core.auth' (C:\Users\akhil\ai-workspace-v2\backend\app\core\auth.py)
______________________________________________ ERROR collecting test_change_password.py ______________________________________________
venv\Lib\site-packages\urllib3\connection.py:204: in _new_conn
    sock = connection.create_connection(
venv\Lib\site-packages\urllib3\util\connection.py:85: in create_connection
    raise err
venv\Lib\site-packages\urllib3\util\connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\urllib3\connectionpool.py:788: in urlopen
    response = self._make_request(
venv\Lib\site-packages\urllib3\connectionpool.py:493: in _make_request
    conn.request(
venv\Lib\site-packages\urllib3\connection.py:500: in request
    self.endheaders()
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1331: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1091: in _send_output
    self.send(msg)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1035: in send
    self.connect()
venv\Lib\site-packages\urllib3\connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
venv\Lib\site-packages\urllib3\connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\requests\adapters.py:696: in send
    resp = conn.urlopen(
venv\Lib\site-packages\urllib3\connectionpool.py:842: in urlopen
    retries = retries.increment(
venv\Lib\site-packages\urllib3\util\retry.py:543: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))

During handling of the above exception, another exception occurred:
test_change_password.py:5: in <module>
    login = requests.post(
venv\Lib\site-packages\requests\api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:784: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\adapters.py:729: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))
______________________________________________ ERROR collecting test_create_session.py _______________________________________________
test_create_session.py:15: in <module>
    session, token = service.create_session(
E   TypeError: SessionService.create_session() missing 1 required positional argument: 'refresh_token'
________________________________________________ ERROR collecting test_get_profile.py ________________________________________________
venv\Lib\site-packages\urllib3\connection.py:204: in _new_conn
    sock = connection.create_connection(
venv\Lib\site-packages\urllib3\util\connection.py:85: in create_connection
    raise err
venv\Lib\site-packages\urllib3\util\connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\urllib3\connectionpool.py:788: in urlopen
    response = self._make_request(
venv\Lib\site-packages\urllib3\connectionpool.py:493: in _make_request
    conn.request(
venv\Lib\site-packages\urllib3\connection.py:500: in request
    self.endheaders()
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1331: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1091: in _send_output
    self.send(msg)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1035: in send
    self.connect()
venv\Lib\site-packages\urllib3\connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
venv\Lib\site-packages\urllib3\connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\requests\adapters.py:696: in send
    resp = conn.urlopen(
venv\Lib\site-packages\urllib3\connectionpool.py:842: in urlopen
    retries = retries.increment(
venv\Lib\site-packages\urllib3\util\retry.py:543: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))

During handling of the above exception, another exception occurred:
test_get_profile.py:5: in <module>
    login = requests.post(
venv\Lib\site-packages\requests\api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:784: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\adapters.py:729: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))
____________________________________________ ERROR collecting test_login_new_password.py _____________________________________________
venv\Lib\site-packages\urllib3\connection.py:204: in _new_conn
    sock = connection.create_connection(
venv\Lib\site-packages\urllib3\util\connection.py:85: in create_connection
    raise err
venv\Lib\site-packages\urllib3\util\connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\urllib3\connectionpool.py:788: in urlopen
    response = self._make_request(
venv\Lib\site-packages\urllib3\connectionpool.py:493: in _make_request
    conn.request(
venv\Lib\site-packages\urllib3\connection.py:500: in request
    self.endheaders()
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1331: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1091: in _send_output
    self.send(msg)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1035: in send
    self.connect()
venv\Lib\site-packages\urllib3\connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
venv\Lib\site-packages\urllib3\connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\requests\adapters.py:696: in send
    resp = conn.urlopen(
venv\Lib\site-packages\urllib3\connectionpool.py:842: in urlopen
    retries = retries.increment(
venv\Lib\site-packages\urllib3\util\retry.py:543: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))

During handling of the above exception, another exception occurred:
test_login_new_password.py:5: in <module>
    response = requests.post(
venv\Lib\site-packages\requests\api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:784: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\adapters.py:729: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))
__________________________________________________ ERROR collecting test_logout.py ___________________________________________________
test_logout.py:23: in <module>
    session = service.create_session(
E   TypeError: SessionService.create_session() missing 1 required positional argument: 'ip_address'
____________________________________________ ERROR collecting test_membership_relation.py ____________________________________________
test_membership_relation.py:5: in <module>
    print("Workspace -> members :", Workspace.members.property.back_populates)
                                    ^^^^^^^^^^^^^^^^^
E   AttributeError: type object 'Workspace' has no attribute 'members'
____________________________________________ ERROR collecting test_membership_service.py _____________________________________________
ImportError while importing test module 'C:\Users\akhil\ai-workspace-v2\backend\test_membership_service.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
..\..\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
test_membership_service.py:1: in <module>
    from app.services.workspace_member_service import MembershipService
E   ImportError: cannot import name 'MembershipService' from 'app.services.workspace_member_service' (C:\Users\akhil\ai-workspace-v2\backend\app\services\workspace_member_service.py)
_______________________________________________ ERROR collecting test_old_password.py ________________________________________________
venv\Lib\site-packages\urllib3\connection.py:204: in _new_conn
    sock = connection.create_connection(
venv\Lib\site-packages\urllib3\util\connection.py:85: in create_connection
    raise err
venv\Lib\site-packages\urllib3\util\connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\urllib3\connectionpool.py:788: in urlopen
    response = self._make_request(
venv\Lib\site-packages\urllib3\connectionpool.py:493: in _make_request
    conn.request(
venv\Lib\site-packages\urllib3\connection.py:500: in request
    self.endheaders()
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1331: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1091: in _send_output
    self.send(msg)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1035: in send
    self.connect()
venv\Lib\site-packages\urllib3\connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
venv\Lib\site-packages\urllib3\connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\requests\adapters.py:696: in send
    resp = conn.urlopen(
venv\Lib\site-packages\urllib3\connectionpool.py:842: in urlopen
    retries = retries.increment(
venv\Lib\site-packages\urllib3\util\retry.py:543: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))

During handling of the above exception, another exception occurred:
test_old_password.py:5: in <module>
    response = requests.post(
venv\Lib\site-packages\requests\api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:784: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\adapters.py:729: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))
______________________________________________ ERROR collecting test_project_create.py _______________________________________________
test_project_create.py:9: in <module>
    payload = ProjectCreate(
E   pydantic_core._pydantic_core.ValidationError: 1 validation error for ProjectCreate
E   title
E     Field required [type=missing, input_value={'name': 'Stock Predictor...': 'LSTM + RNN project'}, input_type=dict]
E       For further information visit https://errors.pydantic.dev/2.13/v/missing
___________________________________________ ERROR collecting test_project_relationship.py ____________________________________________
test_project_relationship.py:12: in <module>
    print(Project.creator.property.back_populates)
          ^^^^^^^^^^^^^^^
E   AttributeError: type object 'Project' has no attribute 'creator'
---------------------------------------------------------- Captured stdout -----------------------------------------------------------
User relationships:
owner
Workspace relationships:
workspace
Project relationships:
_______________________________________________ ERROR collecting test_protected_api.py _______________________________________________
venv\Lib\site-packages\urllib3\connection.py:204: in _new_conn
    sock = connection.create_connection(
venv\Lib\site-packages\urllib3\util\connection.py:85: in create_connection
    raise err
venv\Lib\site-packages\urllib3\util\connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\urllib3\connectionpool.py:788: in urlopen
    response = self._make_request(
venv\Lib\site-packages\urllib3\connectionpool.py:493: in _make_request
    conn.request(
venv\Lib\site-packages\urllib3\connection.py:500: in request
    self.endheaders()
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1331: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1091: in _send_output
    self.send(msg)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1035: in send
    self.connect()
venv\Lib\site-packages\urllib3\connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
venv\Lib\site-packages\urllib3\connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\requests\adapters.py:696: in send
    resp = conn.urlopen(
venv\Lib\site-packages\urllib3\connectionpool.py:842: in urlopen
    retries = retries.increment(
venv\Lib\site-packages\urllib3\util\retry.py:543: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))

During handling of the above exception, another exception occurred:
test_protected_api.py:6: in <module>
    login = requests.post(
venv\Lib\site-packages\requests\api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:784: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\adapters.py:729: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))
_________________________________________________ ERROR collecting test_rotation.py __________________________________________________
test_rotation.py:10: in <module>
    session, token = service.create_session(
E   TypeError: SessionService.create_session() missing 1 required positional argument: 'refresh_token'
_______________________________________________ ERROR collecting test_session_model.py _______________________________________________
ImportError while importing test module 'C:\Users\akhil\ai-workspace-v2\backend\test_session_model.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
..\..\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
test_session_model.py:1: in <module>
    from app.models.session import Session
E   ImportError: cannot import name 'Session' from 'app.models.session' (C:\Users\akhil\ai-workspace-v2\backend\app\models\session.py)
______________________________________________ ERROR collecting test_update_profile.py _______________________________________________
venv\Lib\site-packages\urllib3\connection.py:204: in _new_conn
    sock = connection.create_connection(
venv\Lib\site-packages\urllib3\util\connection.py:85: in create_connection
    raise err
venv\Lib\site-packages\urllib3\util\connection.py:73: in create_connection
    sock.connect(sa)
E   ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\urllib3\connectionpool.py:788: in urlopen
    response = self._make_request(
venv\Lib\site-packages\urllib3\connectionpool.py:493: in _make_request
    conn.request(
venv\Lib\site-packages\urllib3\connection.py:500: in request
    self.endheaders()
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1331: in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1091: in _send_output
    self.send(msg)
..\..\AppData\Local\Programs\Python\Python312\Lib\http\client.py:1035: in send
    self.connect()
venv\Lib\site-packages\urllib3\connection.py:331: in connect
    self.sock = self._new_conn()
                ^^^^^^^^^^^^^^^^
venv\Lib\site-packages\urllib3\connection.py:219: in _new_conn
    raise NewConnectionError(
E   urllib3.exceptions.NewConnectionError: HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it

The above exception was the direct cause of the following exception:
venv\Lib\site-packages\requests\adapters.py:696: in send
    resp = conn.urlopen(
venv\Lib\site-packages\urllib3\connectionpool.py:842: in urlopen
    retries = retries.increment(
venv\Lib\site-packages\urllib3\util\retry.py:543: in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))

During handling of the above exception, another exception occurred:
test_update_profile.py:5: in <module>
    login = requests.post(
venv\Lib\site-packages\requests\api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\sessions.py:784: in send
    r = adapter.send(request, **kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\requests\adapters.py:729: in send
    raise ConnectionError(e, request=request)
E   requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=8000): Failed to establish a new connection: [WinError 10061] No connection could be made because the target machine actively refused it"))
_____________________________________________ ERROR collecting test_workspace_lookup.py ______________________________________________
venv\Lib\site-packages\sqlalchemy\engine\base.py:1969: in _exec_single_context
    self.dialect.do_execute(
venv\Lib\site-packages\sqlalchemy\engine\default.py:952: in do_execute
    cursor.execute(statement, parameters)
E   psycopg2.errors.InvalidTextRepresentation: invalid input syntax for type uuid: "REPLACE_WITH_WORKSPACE_UUID"
E   LINE 3: WHERE workspaces.id = 'REPLACE_WITH_WORKSPACE_UUID'::UUID 
E                                 ^

The above exception was the direct cause of the following exception:
test_workspace_lookup.py:8: in <module>
    workspace = repo.get_by_id(
app\repositories\workspace_repository.py:22: in get_by_id
    .first()
     ^^^^^^^
venv\Lib\site-packages\sqlalchemy\orm\query.py:2766: in first
    return self.limit(1)._iter().first()  # type: ignore
           ^^^^^^^^^^^^^^^^^^^^^
venv\Lib\site-packages\sqlalchemy\orm\query.py:2864: in _iter
    result: Union[ScalarResult[_T], Result[_T]] = self.session.execute(
venv\Lib\site-packages\sqlalchemy\orm\session.py:2373: in execute
    return self._execute_internal(
venv\Lib\site-packages\sqlalchemy\orm\session.py:2271: in _execute_internal
    result: Result[Any] = compile_state_cls.orm_execute_statement(
venv\Lib\site-packages\sqlalchemy\orm\context.py:306: in orm_execute_statement
    result = conn.execute(
venv\Lib\site-packages\sqlalchemy\engine\base.py:1421: in execute
    return meth(
venv\Lib\site-packages\sqlalchemy\sql\elements.py:526: in _execute_on_connection
    return connection._execute_clauseelement(
venv\Lib\site-packages\sqlalchemy\engine\base.py:1643: in _execute_clauseelement
    ret = self._execute_context(
venv\Lib\site-packages\sqlalchemy\engine\base.py:1848: in _execute_context
    return self._exec_single_context(
venv\Lib\site-packages\sqlalchemy\engine\base.py:1988: in _exec_single_context
    self._handle_dbapi_exception(
venv\Lib\site-packages\sqlalchemy\engine\base.py:2365: in _handle_dbapi_exception
    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
venv\Lib\site-packages\sqlalchemy\engine\base.py:1969: in _exec_single_context
    self.dialect.do_execute(
venv\Lib\site-packages\sqlalchemy\engine\default.py:952: in do_execute
    cursor.execute(statement, parameters)
E   sqlalchemy.exc.DataError: (psycopg2.errors.InvalidTextRepresentation) invalid input syntax for type uuid: "REPLACE_WITH_WORKSPACE_UUID"
E   LINE 3: WHERE workspaces.id = 'REPLACE_WITH_WORKSPACE_UUID'::UUID 
E                                 ^
E   
E   [SQL: SELECT workspaces.id AS workspaces_id, workspaces.owner_id AS workspaces_owner_id, workspaces.name AS workspaces_name, workspaces.description AS workspaces_description, workspaces.color AS workspaces_color, workspaces.icon AS workspaces_icon, workspaces.is_archived AS workspaces_is_archived, workspaces.created_at AS workspaces_created_at, workspaces.updated_at AS workspaces_updated_at 
E   FROM workspaces 
E   WHERE workspaces.id = %(id_1)s::UUID 
E    LIMIT %(param_1)s]
E   [parameters: {'id_1': 'REPLACE_WITH_WORKSPACE_UUID', 'param_1': 1}]
E   (Background on this error at: https://sqlalche.me/e/20/9h9h)
_____________________________________ ERROR collecting test_workspace_membership_relationship.py _____________________________________
test_workspace_membership_relationship.py:6: in <module>
    print("Workspace members ->", Workspace.members.property.back_populates)
                                  ^^^^^^^^^^^^^^^^^
E   AttributeError: type object 'Workspace' has no attribute 'members'
---------------------------------------------------------- Captured stdout -----------------------------------------------------------
User memberships -> user
______________________________________________ ERROR collecting tests/test_security.py _______________________________________________
import file mismatch:
imported module 'test_security' has this __file__ attribute:
  C:\Users\akhil\ai-workspace-v2\backend\test_security.py
which is not the same as the test file we want to collect:
  C:\Users\akhil\ai-workspace-v2\backend\tests\test_security.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
___________________________________________ ERROR collecting tests/test_user_repository.py ___________________________________________
import file mismatch:
imported module 'test_user_repository' has this __file__ attribute:
  C:\Users\akhil\ai-workspace-v2\backend\test_user_repository.py
which is not the same as the test file we want to collect:
  C:\Users\akhil\ai-workspace-v2\backend\tests\test_user_repository.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
========================================================== warnings summary ==========================================================
venv\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\akhil\ai-workspace-v2\backend\venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====================================================== short test summary info =======================================================
ERROR test_admin_route.py - requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceededwith url: /auth/login (...
ERROR test_auth_api.py - requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/registe...
ERROR test_auth_dependency.py
ERROR test_change_password.py - requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (...
ERROR test_create_session.py - TypeError: SessionService.create_session() missing 1 required positional argument: 'refresh_token'
ERROR test_get_profile.py - requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceededwith url: /auth/login (...
ERROR test_login_new_password.py - requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (...
ERROR test_logout.py - TypeError: SessionService.create_session() missing 1 required positional argument: 'ip_address'
ERROR test_membership_relation.py - AttributeError: type object 'Workspace' has no attribute 'members'
ERROR test_membership_service.py
ERROR test_old_password.py - requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (...
ERROR test_project_create.py - pydantic_core._pydantic_core.ValidationError: 1 validation error for ProjectCreate
ERROR test_project_relationship.py - AttributeError: type object 'Project' has no attribute 'creator'
ERROR test_protected_api.py - requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (...
ERROR test_rotation.py - TypeError: SessionService.create_session() missing 1 required positional argument: 'refresh_token'
ERROR test_session_model.py
ERROR test_update_profile.py - requests.exceptions.ConnectionError: HTTPConnectionPool(host='127.0.0.1', port=8000): Max retries exceeded with url: /auth/login (...
ERROR test_workspace_lookup.py - sqlalchemy.exc.DataError: (psycopg2.errors.InvalidTextRepresentation) invalid input syntax for type uuid: "REPLACE_WITH_WORKSPACE_...
ERROR test_workspace_membership_relationship.py - AttributeError: type object 'Workspace' has no attribute 'members'
ERROR tests/test_security.py
ERROR tests/test_user_repository.py
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Interrupted: 21 errors during collection !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
1 warning, 21 errors in 26.41s