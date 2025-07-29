
# Getting Started with Cuadra AI

## Introduction

API Documentation

## Install the Package

The package is compatible with Python versions `3.7+`.
Install the package from PyPi using the following pip command:

```bash
pip install cuadra-ai-sdk==1.0.3
```

You can also view the package at:
https://pypi.python.org/pypi/cuadra-ai-sdk/1.0.3

## Initialize the API Client

**_Note:_** Documentation for the client can be found [here.](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/client.md)

The following parameters are configurable for the API Client:

| Parameter | Type | Description |
|  --- | --- | --- |
| environment | `Environment` | The API environment. <br> **Default: `Environment.PRODUCTION`** |
| http_client_instance | `HttpClient` | The Http Client passed from the sdk user for making requests |
| override_http_client_configuration | `bool` | The value which determines to override properties of the passed Http Client from the sdk user |
| http_call_back | `HttpCallBack` | The callback value that is invoked before and after an HTTP call is made to an endpoint |
| timeout | `float` | The value to use for connection timeout. <br> **Default: 30** |
| max_retries | `int` | The number of times to retry an endpoint call if it fails. <br> **Default: 0** |
| backoff_factor | `float` | A backoff factor to apply between attempts after the second try. <br> **Default: 2** |
| retry_statuses | `Array of int` | The http statuses on which retry is to be done. <br> **Default: [408, 413, 429, 500, 502, 503, 504, 521, 522, 524]** |
| retry_methods | `Array of string` | The http methods on which retry is to be done. <br> **Default: ['GET', 'PUT']** |
| logging_configuration | [`LoggingConfiguration`](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/logging-configuration.md) | The SDK logging configuration for API calls |
| authorization_code_auth_credentials | [`AuthorizationCodeAuthCredentials`](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/auth/oauth-2-authorization-code-grant.md) | The credential object for OAuth 2 Authorization Code Grant |

The API client can be initialized as follows:

```python
client = CuadraaiClient(
    authorization_code_auth_credentials=AuthorizationCodeAuthCredentials(
        oauth_client_id='OAuthClientId',
        oauth_client_secret='OAuthClientSecret',
        oauth_redirect_uri='OAuthRedirectUri'
    ),
    environment=Environment.PRODUCTION,
    logging_configuration=LoggingConfiguration(
        log_level=logging.INFO,
        request_logging_config=RequestLoggingConfiguration(
            log_body=True
        ),
        response_logging_config=ResponseLoggingConfiguration(
            log_headers=True
        )
    )
)
```

## Authorization

This API uses the following authentication schemes.

* [`OAuth2 (OAuth 2 Authorization Code Grant)`](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/auth/oauth-2-authorization-code-grant.md)

## List of APIs

* [Chat](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/controllers/chat.md)
* [Models](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/controllers/models.md)
* [Embeds](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/controllers/embeds.md)
* [Usage](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/controllers/usage.md)

## SDK Infrastructure

### Configuration

* [AbstractLogger](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/abstract-logger.md)
* [LoggingConfiguration](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/logging-configuration.md)
* [RequestLoggingConfiguration](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/request-logging-configuration.md)
* [ResponseLoggingConfiguration](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/response-logging-configuration.md)

### HTTP

* [HttpResponse](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/http-response.md)
* [HttpRequest](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/http-request.md)

### Utilities

* [ApiResponse](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/api-response.md)
* [ApiHelper](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/api-helper.md)
* [HttpDateTime](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/http-date-time.md)
* [RFC3339DateTime](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/rfc3339-date-time.md)
* [UnixDateTime](https://www.github.com/cuadra-ai/cuadra-ai-python-sdk/tree/1.0.3/doc/unix-date-time.md)

