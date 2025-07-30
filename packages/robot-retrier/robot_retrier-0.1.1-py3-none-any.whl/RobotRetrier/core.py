import threading
import ast
import logging
from robot.libraries.BuiltIn import BuiltIn
from datetime import datetime
import re


class SimpleRetryCore:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self):
        self.builtin = BuiltIn()
        self.failed_keyword = None
        self.current_test = None
        self.current_suite = None
        self.continue_event = threading.Event()
        self.retry_success = False
        self.abort_suite = False
        self.gui_controller = None
        self.skip_test = False
        self.skip_keyword = False
        self.keyword_stack = []
        # Define muted keywords in normal readable format, and normalize them to lowercase
        raw_mutes = {
            "Run Keyword And Ignore Error",
            "Run Keyword And Expect Error",
            "Run Keyword And Return Status",
            "Run Keyword And Warn On Failure",
            "Wait Until Keyword Succeeds",
            "Run Keyword If",
            "Run Keywords",
            "Run Keyword Unless",
            "Continue For Loop If",
            "Exit For Loop If",
        }
        self.muting_keywords = {kw.strip().lower() for kw in raw_mutes}

        logging.basicConfig(
            filename="retry_debug.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def start_suite(self, data, result):
        self.current_suite = data.name
        logging.info(f"Suite started: {self.current_suite}")

    def start_test(self, data, result):
        self.current_test = data.name
        logging.info(f"Test started: {self.current_test}")

    def _normalize_keyword_name(self, raw_name):
        # Robot keywords always separate name/args with 2+ spaces
        return raw_name.strip().split("  ")[0].strip().lower()

    def end_keyword(self, data, result):
        # ✅ Normalize current keyword name
        normalized_name = self._normalize_keyword_name(data.name)

        if result.status == 'FAIL':
            # ✅ Check for muted wrapper BEFORE popping
            muted_parent = next((kw for kw in self.keyword_stack if kw in self.muting_keywords), None)
            if muted_parent:
                logging.info(f"[Muted Context] Failure in '{data.name}' suppressed (inside '{muted_parent}')")

                if self.gui_controller:
                    self.gui_controller.update_status(
                        f"⚠️ Skipped retry for '{data.name}' (inside '{muted_parent}')",
                        "gray"
                    )
                    self.gui_controller._update_failure_display(
                        text=f"'{data.name}' failed, but retry skipped because it was inside muted wrapper: '{muted_parent}'",
                        prefix="[Muted]",
                        status="pending"
                    )

                # ✅ Make test continue by marking the keyword as passed
                result.status = 'PASS'
                result.message = f"[Muted] Failure in '{data.name}' suppressed due to wrapper: '{muted_parent}'"

                # ✅ Now pop the stack
                if self.keyword_stack:
                    popped = self.keyword_stack.pop()
                    print(f"[END-MUTED] keyword={data.name} -> popped={popped} -> stack={self.keyword_stack}")

                return

        # ✅ If not muted — continue with retry GUI as usual
        if normalized_name in self.keyword_stack:
            popped = self.keyword_stack.pop()
            print(f"[END] keyword={data.name} -> popped={popped} -> stack={self.keyword_stack}")

        if self.abort_suite:
            result.status = 'FAIL'
            result.message = 'Suite aborted by user'
            logging.warning("Suite aborted by user.")
            return

        if self.skip_test:
            result.status = 'FAIL'
            result.message = 'Test skipped by user'
            self.skip_test = False
            logging.info("Test skipped by user.")
            return

        if result.status == 'FAIL':
            self.failed_keyword = data
            if self.gui_controller:
                self.gui_controller.show_failure(
                    suite=self.current_suite,
                    test=self.current_test,
                    keyword=data.name,
                    message=result.message or "(No failure message)",
                    args=data.args
                )

                self.continue_event.clear()
                self.continue_event.wait()

                if self.skip_keyword:
                    result.status = 'PASS'
                    result.message = '[DEBUGGER OVERRIDE] Keyword was skipped by user.'
                    try:
                        BuiltIn().log(f"[Debugger] Skipped keyword: {data.name}", "WARN")
                        BuiltIn().set_tags("debugger-skipped")
                    except Exception as e:
                        logging.warning(f"Failed to log/set tag for skipped keyword: {e}")
                    self.skip_keyword = False
                    self.failed_keyword = None
                    return

                if self.retry_success:
                    result.status = 'PASS'
                    result.message = '[RETRIED SUCCESSFULLY] Keyword passed after GUI retry.'
                    try:
                        BuiltIn().log(f"[Debugger] Retried keyword succeeded: {data.name}", "INFO")
                        BuiltIn().set_tags("debugger-retried")
                    except Exception as e:
                        logging.warning(f"Failed to log/set tag for retried keyword: {e}")
                    self.retry_success = False
                    self.failed_keyword = None
                    return

    def start_keyword(self, data, result):
        base_name = self._normalize_keyword_name(data.name)
        self.keyword_stack.append(base_name)
        print(f"[START] keyword={data.name} -> normalized={base_name} -> stack={self.keyword_stack}")

    def _handle_failure(self, data, result):
        if self.gui_controller:
            self.gui_controller.show_failure(
                suite=self.current_suite,
                test=self.current_test,
                keyword=data.name,
                message=result.message or "(No failure message)",
                args=data.args
            )

            self.continue_event.clear()
            self.continue_event.wait()

            # Handle skip keyword
            if self.skip_keyword:
                result.status = 'PASS'
                result.message = '[DEBUGGER OVERRIDE] Keyword was skipped by user.'
                try:
                    BuiltIn().log(f"[Debugger] Skipped keyword: {data.name}", "WARN")
                    BuiltIn().set_tags("debugger-skipped")
                except Exception as e:
                    logging.warning(f"Failed to log/set tag for skipped keyword: {e}")
                self.skip_keyword = False
                return

            # Handle retry success
            if self.retry_success:
                result.status = 'PASS'
                result.message = '[RETRIED SUCCESSFULLY] Keyword passed after GUI retry.'
                try:
                    BuiltIn().log(f"[Debugger] Retried keyword succeeded: {data.name}", "INFO")
                    BuiltIn().set_tags("debugger-retried")
                except Exception as e:
                    logging.warning(f"Failed to log/set tag for retried keyword: {e}")
                self.retry_success = False
                return

    def retry_keyword(self, kw_name, args):
        try:
            result = self.builtin.run_keyword_and_ignore_error(kw_name, *args)
            logging.info(f"Retry result for {kw_name}: {result}")
            return result
        except Exception as e:
            logging.exception("Exception during retry:")
            return ('FAIL', str(e))

    def parse_arg(self, val):
        if not isinstance(val, str):
            return val

        val = val.strip()
        if not val:
            return val

        lowered = val.lower()
        if lowered in ('none', 'null'):
            return None
        if lowered == 'true':
            return True
        if lowered == 'false':
            return False

        try:
            return ast.literal_eval(val)
        except:
            return val
