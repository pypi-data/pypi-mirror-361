import sys
from threading import Lock

from je_web_runner.utils.exception.exception_tags import html_generate_no_data_tag
from je_web_runner.utils.exception.exceptions import WebRunnerHTMLException
from je_web_runner.utils.logging.loggin_instance import web_runner_logger
from je_web_runner.utils.test_record.test_record_class import test_record_instance

_lock = Lock()

_html_string = \
    r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <title>AutoControl Report</title>

    <style>

        body{{
            font-size: 100%;
        }}

        h1{{
            font-size: 2em;
        }}

        .main_table {{
            margin: 0 auto;
            border-collapse: collapse;
            width: 75%;
            font-size: 1.5em;
        }}

        .event_table_head {{
            border: 3px solid #262626;
            background-color: aqua;
            font-family: "Times New Roman", sans-serif;
            text-align: center;
        }}

        .failure_table_head {{
            border: 3px solid #262626;
            background-color: #f84c5f;
            font-family: "Times New Roman", sans-serif;
            text-align: center;
        }}

        .table_data_field_title {{
            border: 3px solid #262626;
            padding: 0;
            margin: 0;
            background-color: #dedede;
            font-family: "Times New Roman", sans-serif;
            text-align: center;
            width: 25%;
        }}

        .table_data_field_text {{
            border: 3px solid #262626;
            padding: 0;
            margin: 0;
            background-color: #dedede;
            font-family: "Times New Roman", sans-serif;
            text-align: left;
            width: 75%;
        }}

        .text {{
            text-align: center;
            font-family: "Times New Roman", sans-serif;
        }}
    </style>
</head>
<body>
<h1 class="text">
    Test Report
</h1>
{event_table}
</body>
</html>
""".strip()

_event_table = \
    r"""
    <table class="main_table">
        <thead>
        <tr>
            <th colspan="2" class="{table_head_class}">Test Report</th>
        </tr>
        </thead>
        <tbody>
        <tr>
            <td class="table_data_field_title">function_name</td>
            <td class="table_data_field_text">{function_name}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">param</td>
            <td class="table_data_field_text">{param}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">time</td>
            <td class="table_data_field_text">{time}</td>
        </tr>
        <tr>
            <td class="table_data_field_title">exception</td>
            <td class="table_data_field_text">{exception}</td>
        </tr>
        </tbody>
    </table>
    <br>
    """.strip()


def make_html_table(event_str: str, record_data: dict, table_head: str) -> str:
    """
    use to add record to html
    :param event_str: what event trigger
    :param record_data: what date need to recode
    :param table_head: table head text
    :return: whole current str
    """
    event_str = "".join(
        [
            event_str,
            _event_table.format(
                table_head_class=table_head,
                function_name=str(record_data.get("function_name")),
                param=str(record_data.get("local_param")),
                time=str(record_data.get("time")),
                exception=str(record_data.get("program_exception")),
            )
        ]
    )
    return event_str


def generate_html() -> str:
    """
    :return: html_string
    """
    web_runner_logger.info("generate_html")
    if len(test_record_instance.test_record_list) == 0:
        raise WebRunnerHTMLException(html_generate_no_data_tag)
    else:
        event_str = ""
        for record_data in test_record_instance.test_record_list:
            # because data on record_data all is str
            if record_data.get("program_exception") == "None":
                event_str = make_html_table(event_str, record_data, "event_table_head")
            else:
                event_str = make_html_table(event_str, record_data, "failure_table_head")
        new_html_string = _html_string.format(event_table=event_str)
    return new_html_string


def generate_html_report(html_name: str = "default_name"):
    """
    this function will create and save html report on current folder
    :param html_name: save html file name
    """
    web_runner_logger.info(f"generate_html_report, html_name: {html_name}")
    new_html_string = generate_html()
    try:
        _lock.acquire()
        with open(html_name + ".html", "w+") as file_to_write:
            file_to_write.write(
                new_html_string
            )
    except Exception as error:
        print(repr(error), file=sys.stderr)
    finally:
        _lock.release()
