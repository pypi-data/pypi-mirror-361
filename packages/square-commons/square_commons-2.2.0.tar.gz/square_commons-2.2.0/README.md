# square_commons

## about

helper module containing common functions for all my python modules.

## installation

```shell
pip install square_commons
```

## usage

[reference](./usage)

## env

- python>=3.12.0

## changelog

### v2.2.0

- api_utils
    - add make_request.

### v2.1.0

- config_reader
    - new optional parameter sample_file_path.

### v2.0.0

- api_utils
    - make_request_json_output have separate paramater for data and json.
    - new optional parameter auth.
- email
    - add send_email_using_mailgun

### v1.5.0

- new dependencies: pytest, pytest-mock.
- added pytest test cases.
- add github workflow for auto test on commit.

### v1.4.1

- update default param for same_site to strict in api_utils -> create_cookie.

### v1.4.0

- add api_utils -> create_cookie.

### v1.3.0

- update api_utils -> make_request_json_output to send files as well.

### v1.2.0

- added make_request_json_output in api_utils.

### v1.1.0

- added api_utils with get_api_output_in_standard_format.

### v1.0.0

- initial version with config reading methods.

## Feedback is appreciated. Thank you!
