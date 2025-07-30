import json
import sys
from threading import Lock

from je_web_runner.utils.exception.exception_tags import cant_generate_json_report
from je_web_runner.utils.exception.exceptions import WebRunnerGenerateJsonReportException
from je_web_runner.utils.logging.loggin_instance import web_runner_logger
from je_web_runner.utils.test_record.test_record_class import test_record_instance


def generate_json():
    """
    :return: success test dict and failure test dict
    """
    web_runner_logger.info("generate_json")
    if len(test_record_instance.test_record_list) == 0 and len(test_record_instance.error_record_list) == 0:
        raise WebRunnerGenerateJsonReportException(cant_generate_json_report)
    else:
        success_dict = dict()
        failure_dict = dict()
        failure_count: int = 1
        failure_test_str: str = "Failure_Test"
        success_count: int = 1
        success_test_str: str = "Success_Test"
        for record_data in test_record_instance.test_record_list:
            if record_data.get("program_exception", "None") == "None":
                success_dict.update(
                    {
                        success_test_str + str(success_count): {
                            "function_name": str(record_data.get("function_name")),
                            "param": str(record_data.get("local_param")),
                            "time": str(record_data.get("time")),
                            "exception": str(record_data.get("program_exception")),
                        }
                    }
                )
                success_count = success_count + 1
            else:
                failure_dict.update(
                    {
                        failure_test_str + str(failure_count): {
                            "function_name": str(record_data.get("function_name")),
                            "param": str(record_data.get("local_param")),
                            "time": str(record_data.get("time")),
                            "exception": str(record_data.get("program_exception")),
                        }
                    }
                )
                failure_count = failure_count + 1
    return success_dict, failure_dict


def generate_json_report(json_file_name: str = "default_name"):
    """
    :param json_file_name: save json file's name
    """
    web_runner_logger.info(f"generate_json_report, json_file_name: {json_file_name}")
    lock = Lock()
    success_dict, failure_dict = generate_json()
    try:
        lock.acquire()
        with open(json_file_name + "_success.json", "w+") as file_to_write:
            json.dump(dict(success_dict), file_to_write, indent=4)
    except Exception as error:
        web_runner_logger.error(f"generate_json_report, json_file_name: {json_file_name}, failed: {repr(error)}")
    finally:
        lock.release()
    try:
        lock.acquire()
        with open(json_file_name + "_failure.json", "w+") as file_to_write:
            json.dump(dict(failure_dict), file_to_write, indent=4)
    except Exception as error:
        web_runner_logger.error(f"generate_json_report, json_file_name: {json_file_name}, failed: {repr(error)}")
    finally:
        lock.release()
