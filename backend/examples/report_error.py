import requests

API_TOKEN = "your-project-api-token"
BASE_URL = "http://localhost:5000/api/v1"


def report_error(exception_type, message, stack_trace=None,
                 severity="error", environment="unknown", context=None):
    resp = requests.post(
        f"{BASE_URL}/errors",
        headers={"X-API-Token": API_TOKEN},
        json={
            "exception_type": exception_type,
            "message": message,
            "stack_trace": stack_trace,
            "severity": severity,
            "environment": environment,
            "context": context,
        },
    )
    return resp.json()


if __name__ == "__main__":
    result = report_error(
        exception_type="ValueError",
        message="invalid input data",
        stack_trace=(
            "Traceback (most recent call last):\n"
            '  File "/app/services/user.py", line 42, in create_user\n'
            "    validate_email(email)\n"
            '  File "/app/utils/validators.py", line 15, in validate_email\n'
            '    raise ValueError("invalid input data")'
        ),
        severity="error",
        environment="production",
        context={
            "user_id": "12345",
            "request_path": "/api/users",
            "method": "POST",
        },
    )
    print(result)
