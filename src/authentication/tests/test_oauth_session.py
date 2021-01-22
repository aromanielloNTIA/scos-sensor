import base64
import json
import secrets
from datetime import datetime

import jwt
import oauthlib
import pytest
import requests_mock
from django.test.testcases import SimpleTestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, RequestsClient

from authentication.auth import oauth_session_authentication_enabled
from authentication.models import User
from authentication.tests.test_jwt_auth import (
    BAD_PRIVATE_KEY,
    BAD_PUBLIC_KEY_FILE,
    PRIVATE_KEY,
    TEST_JWT_PUBLIC_KEY_FILE,
    get_token_payload,
    one_day,
    one_min,
)
from sensor import V1
from sensor.settings import CLIENT_ID, FQDN, OAUTH_AUTHORIZATION_URL, OAUTH_TOKEN_URL

pytestmark = pytest.mark.skipif(
    not oauth_session_authentication_enabled,
    reason="OAuth JWT authentication is not enabled!",
)


@pytest.mark.django_db
def test_oauth_login_view(settings):
    client = APIClient()
    response = client.get(reverse("oauth-login"))
    assert response.wsgi_request.session["oauth_state"]
    oauth_callback_path = reverse("oauth-callback")
    state = response.wsgi_request.session["oauth_state"]
    url_redirect = f"{OAUTH_AUTHORIZATION_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri=https://{FQDN}{oauth_callback_path}&state={state}"
    SimpleTestCase().assertRedirects(
        response, url_redirect, fetch_redirect_response=False
    )


@pytest.mark.django_db
def test_oauth_login_callback():
    test_state = "test_state"
    test_token = "test_access_token"
    client = APIClient()
    session = client.session
    session["oauth_state"] = test_state
    session.save()
    response = None
    with requests_mock.Mocker() as m:
        m.post(OAUTH_TOKEN_URL, json={"access_token": test_token})
        oauth_callback_url = reverse("oauth-callback")
        response = client.get(f"{oauth_callback_url}?code=test_code&state={test_state}")
    assert response.wsgi_request.session["oauth_token"]["access_token"] == test_token
    SimpleTestCase().assertRedirects(
        response, reverse("api-root", kwargs=V1), fetch_redirect_response=False
    )


@pytest.mark.django_db
def test_oauth_login_callback_bad_state():
    test_state = "test_state"
    test_token = "test_access_token"
    client = APIClient()
    session = client.session
    session["oauth_state"] = test_state
    session.save()
    with requests_mock.Mocker() as m:
        m.post(OAUTH_TOKEN_URL, json={"access_token": test_token})
        oauth_callback_url = reverse("oauth-callback")
        with pytest.raises(oauthlib.oauth2.rfc6749.errors.MismatchingStateError):
            client.get(f"{oauth_callback_url}?code=test_code&state=some_state")


################ From test_jwt_auth.py ##############################


def get_oauth_authorized_client(token, live_server):
    def auth_callback(request, context):
        if f"{request.scheme}://{request.hostname}{request.path}".startswith(
            OAUTH_AUTHORIZATION_URL
        ):
            query_start_index = request.path_url.find("?")
            query = request.path_url[query_start_index + 1 :]
            if "response_type=code" in query:
                if f"client_id={CLIENT_ID}" in query:
                    for query_param in query.split("&"):
                        if query_param.startswith("state="):
                            equals_index = query_param.find("=")
                            state = query_param[equals_index + 1 :]
                            _oauth_callback_url = reverse("oauth-callback")
                            context.headers = {
                                "Location": f"{live_server.url}{_oauth_callback_url}?code=test_code&state={state}"
                            }
        return ""

    with requests_mock.Mocker(real_http=True) as m:
        _oauth_callback_url = reverse("oauth-callback")
        m.post(OAUTH_TOKEN_URL, json={"access_token": token})
        url_redirect = (
            OAUTH_AUTHORIZATION_URL + "?response_type=code&client_id=" + CLIENT_ID
        )
        m.get(url_redirect, status_code=307, text=auth_callback)
        client = RequestsClient()
        login_path = reverse("oauth-login")
        url = f"{live_server.url}{login_path}"
        response = client.get(url, allow_redirects=False)  # sensor login
        assert response.is_redirect == True
        assert response.is_permanent_redirect == False
        response = client.get(  # authserver login
            response.headers["Location"], allow_redirects=False
        )
        assert response.is_redirect == True
        assert response.is_permanent_redirect == False
        assert reverse("oauth-callback") in response.headers["Location"]
        response = client.get(  # sensor callback
            response.headers["Location"], allow_redirects=False
        )
        assert response.is_redirect == True
        assert response.is_permanent_redirect == False
        location = response.headers["Location"]
        assert reverse("api-root", kwargs=V1) in location

        for item in m.request_history:
            if OAUTH_TOKEN_URL in item.url:
                assert "grant_type=authorization_code&code=test_code" in item.text
        return client


def perform_oauth_test(token, live_server, test_url):
    client = get_oauth_authorized_client(token, live_server)
    response = client.get(test_url)
    return response


@pytest.mark.django_db
def test_no_token_unauthorized(live_server):
    client = RequestsClient()
    response = client.get(f"{live_server.url}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_token_no_roles_unauthorized(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token_payload = get_token_payload(authorities=[])
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    response = perform_oauth_test(utf8_bytes, live_server, f"{live_server.url}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_token_role_manager_accepted(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token_payload = get_token_payload()
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    response = perform_oauth_test(utf8_bytes, live_server, f"{live_server.url}")
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token_payload = get_token_payload()
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    client = get_oauth_authorized_client(utf8_bytes, live_server)
    response = client.get(f"{live_server.url}")
    assert response.status_code == 200
    logout_url = reverse("oauth-logout")
    response = client.get(f"{live_server.url}{logout_url}")
    response.raise_for_status()
    response = client.get(f"{live_server.url}")
    assert response.status_code == 403


def test_bad_token_forbidden(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token = (
        secrets.token_urlsafe(28)
        + "."
        + secrets.token_urlsafe(679)
        + "."
        + secrets.token_urlsafe(525)
    )
    response = perform_oauth_test(token, live_server, f"{live_server.url}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_token_expired_1_day_forbidden(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    current_datetime = datetime.now()
    token_payload = get_token_payload(exp=(current_datetime - one_day).timestamp())
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    response = perform_oauth_test(utf8_bytes, live_server, f"{live_server.url}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_bad_private_key_forbidden(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token_payload = get_token_payload()
    encoded = jwt.encode(token_payload, str(BAD_PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    response = perform_oauth_test(utf8_bytes, live_server, f"{live_server.url}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_bad_public_key_forbidden(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = BAD_PUBLIC_KEY_FILE
    token_payload = get_token_payload()
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    response = perform_oauth_test(utf8_bytes, live_server, f"{live_server.url}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_token_expired_1_min_forbidden(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    current_datetime = datetime.now()
    token_payload = get_token_payload(exp=(current_datetime - one_min).timestamp())
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    response = perform_oauth_test(utf8_bytes, live_server, f"{live_server.url}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_token_expires_in_1_min_accepted(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    current_datetime = datetime.now()
    token_payload = get_token_payload(exp=(current_datetime + one_min).timestamp())
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    response = perform_oauth_test(utf8_bytes, live_server, f"{live_server.url}")
    assert response.status_code == 200


@pytest.mark.django_db
def test_token_role_user_forbidden(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token_payload = get_token_payload(authorities=["ROLE_USER"])
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    response = perform_oauth_test(utf8_bytes, live_server, f"{live_server.url}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_token_role_user_required_role_accepted(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    settings.REQUIRED_ROLE = "ROLE_USER"
    token_payload = get_token_payload(authorities=["ROLE_USER"])
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    response = perform_oauth_test(utf8_bytes, live_server, f"{live_server.url}")
    assert response.status_code == 200


@pytest.mark.django_db
def test_token_mulitple_roles_accepted(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token_payload = get_token_payload(
        authorities=["ROLE_MANAGER", "ROLE_USER", "ROLE_ITS"]
    )
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    response = perform_oauth_test(utf8_bytes, live_server, f"{live_server.url}")
    assert response.status_code == 200


@pytest.mark.django_db
def test_token_multiple_roles_forbidden(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token_payload = get_token_payload(
        authorities=["ROLE_SENSOR", "ROLE_USER", "ROLE_ITS"]
    )
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    response = perform_oauth_test(utf8_bytes, live_server, f"{live_server.url}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_urls_unauthorized(settings, live_server, user):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token_payload = get_token_payload(authorities=["ROLE_USER"])
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    client = get_oauth_authorized_client(utf8_bytes, live_server)

    capabilities = reverse("capabilities", kwargs=V1)
    response = client.get(f"{live_server.url}{capabilities}")
    assert response.status_code == 403

    schedule_list = reverse("schedule-list", kwargs=V1)
    response = client.get(f"{live_server.url}{schedule_list}")
    assert response.status_code == 403

    status = reverse("status", kwargs=V1)
    response = client.get(f"{live_server.url}{status}")
    assert response.status_code == 403

    task_root = reverse("task-root", kwargs=V1)
    response = client.get(f"{live_server.url}{task_root}")
    assert response.status_code == 403

    task_results_overview = reverse("task-results-overview", kwargs=V1)
    response = client.get(f"{live_server.url}{task_results_overview}")
    assert response.status_code == 403

    upcoming_tasks = reverse("upcoming-tasks", kwargs=V1)
    response = client.get(f"{live_server.url}{upcoming_tasks}")
    assert response.status_code == 403

    user_list = reverse("user-list", kwargs=V1)
    response = client.get(f"{live_server.url}{user_list}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_urls_authorized(settings, live_server, admin_user):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token_payload = get_token_payload(authorities=["ROLE_MANAGER"])
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    client = get_oauth_authorized_client(utf8_bytes, live_server)

    capabilities = reverse("capabilities", kwargs=V1)
    response = client.get(f"{live_server.url}{capabilities}")
    assert response.status_code == 200

    schedule_list = reverse("schedule-list", kwargs=V1)
    response = client.get(f"{live_server.url}{schedule_list}")
    assert response.status_code == 200

    status = reverse("status", kwargs=V1)
    response = client.get(f"{live_server.url}{status}")
    assert response.status_code == 200

    task_root = reverse("task-root", kwargs=V1)
    response = client.get(f"{live_server.url}{task_root}")
    assert response.status_code == 200

    task_results_overview = reverse("task-results-overview", kwargs=V1)
    response = client.get(f"{live_server.url}{task_results_overview}")
    assert response.status_code == 200

    upcoming_tasks = reverse("upcoming-tasks", kwargs=V1)
    response = client.get(f"{live_server.url}{upcoming_tasks}")
    assert response.status_code == 200

    user_list = reverse("user-list", kwargs=V1)
    response = client.get(f"{live_server.url}{user_list}")
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_cannot_view_user_detail(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    sensor01_token_payload = get_token_payload(authorities=["ROLE_MANAGER"])
    encoded = jwt.encode(sensor01_token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    client_user1 = get_oauth_authorized_client(utf8_bytes, live_server)
    response = client_user1.get(f"{live_server.url}")
    assert response.status_code == 200

    sensor02_token_payload = get_token_payload(authorities=["ROLE_USER"])
    sensor02_token_payload["user_name"] = "sensor02"
    encoded = jwt.encode(sensor02_token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    client_user2 = get_oauth_authorized_client(utf8_bytes, live_server)

    sensor01_user = User.objects.get(username=sensor01_token_payload["user_name"])
    kws = {"pk": sensor01_user.pk}
    kws.update(V1)
    user_detail = reverse("user-detail", kwargs=kws)
    response = client_user2.get(f"{live_server.url}{user_detail}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_view_user_detail_role_change(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    sensor01_token_payload = get_token_payload(authorities=["ROLE_MANAGER"])
    encoded = jwt.encode(sensor01_token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    client = get_oauth_authorized_client(utf8_bytes, live_server)
    response = client.get(f"{live_server.url}")
    assert response.status_code == 200

    token_payload = get_token_payload(authorities=["ROLE_USER"])
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    client_new_token = get_oauth_authorized_client(utf8_bytes, live_server)

    sensor01_user = User.objects.get(username=sensor01_token_payload["user_name"])
    kws = {"pk": sensor01_user.pk}
    kws.update(V1)
    user_detail = reverse("user-detail", kwargs=kws)
    response = client_new_token.get(f"{live_server.url}{user_detail}")
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_view_user_detail(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token_payload = get_token_payload(authorities=["ROLE_MANAGER"])
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    client = get_oauth_authorized_client(utf8_bytes, live_server)
    response = client.get(f"{live_server.url}")
    assert response.status_code == 200

    sensor01_user = User.objects.get(username=token_payload["user_name"])
    kws = {"pk": sensor01_user.pk}
    kws.update(V1)
    user_detail = reverse("user-detail", kwargs=kws)
    response = client.get(f"{live_server.url}{user_detail}")
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_can_view_other_user_detail(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    sensor01_token_payload = get_token_payload(authorities=["ROLE_MANAGER"])
    encoded = jwt.encode(sensor01_token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    client_user1 = get_oauth_authorized_client(utf8_bytes, live_server)
    response = client_user1.get(f"{live_server.url}")
    assert response.status_code == 200

    sensor02_token_payload = get_token_payload(authorities=["ROLE_MANAGER"])
    sensor02_token_payload["user_name"] = "sensor02"
    encoded = jwt.encode(sensor02_token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    client_user2 = get_oauth_authorized_client(utf8_bytes, live_server)

    sensor01_user = User.objects.get(username=sensor01_token_payload["user_name"])
    kws = {"pk": sensor01_user.pk}
    kws.update(V1)
    user_detail = reverse("user-detail", kwargs=kws)
    response = client_user2.get(f"{live_server.url}{user_detail}")
    assert response.status_code == 200


@pytest.mark.django_db
def test_token_hidden(settings, live_server):
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token_payload = get_token_payload(authorities=["ROLE_MANAGER"])
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    client = get_oauth_authorized_client(utf8_bytes, live_server)
    response = client.get(f"{live_server.url}")
    assert response.status_code == 200

    sensor01_user = User.objects.get(username=token_payload["user_name"])
    kws = {"pk": sensor01_user.pk}
    kws.update(V1)
    user_detail = reverse("user-detail", kwargs=kws)
    response = client.get(f"{live_server.url}{user_detail}")
    assert response.status_code == 200
    assert (
        response.json()["auth_token"]
        == "rest_framework.authentication.TokenAuthentication is not enabled"
    )


@pytest.mark.django_db
def test_change_token_role_bad_signature(settings, live_server):
    """Make sure token modified after it was signed is rejected"""
    settings.PATH_TO_JWT_PUBLIC_KEY = TEST_JWT_PUBLIC_KEY_FILE
    token_payload = get_token_payload(authorities=["ROLE_USER"])
    encoded = jwt.encode(token_payload, str(PRIVATE_KEY), algorithm="RS256")
    utf8_bytes = encoded.decode("utf-8")
    first_period = utf8_bytes.find(".")
    second_period = utf8_bytes.find(".", first_period + 1)
    payload = utf8_bytes[first_period + 1 : second_period]
    payload_bytes = payload.encode("utf-8")
    # must be multiple of 4 for b64decode
    for i in range(len(payload_bytes) % 4):
        payload_bytes = payload_bytes + b"="
    decoded = base64.b64decode(payload_bytes)
    payload_str = decoded.decode("utf-8")
    payload_data = json.loads(payload_str)
    payload_data["user_name"] = "sensor013"
    payload_data["authorities"] = ["ROLE_MANAGER"]
    payload_data["userDetails"]["authorities"] = [{"authority": "ROLE_MANAGER"}]
    payload_str = json.dumps(payload_data)
    encoded = base64.b64encode(payload_str.encode("utf-8"))
    modified_payload = encoded.decode("utf-8")
    # remove padding
    if modified_payload.endswith("="):
        last_padded_index = len(modified_payload) - 1
        for i in range(len(modified_payload) - 1, -1, -1):
            if modified_payload[i] != "=":
                last_padded_index = i
                break
        modified_payload = modified_payload[: last_padded_index + 1]
    modified_token = (
        utf8_bytes[:first_period]
        + "."
        + modified_payload
        + "."
        + utf8_bytes[second_period + 1 :]
    )
    client = get_oauth_authorized_client(modified_token, live_server)
    response = client.get(f"{live_server.url}")
    assert response.status_code == 403