# event_logger.py
from datetime import datetime

def log_suite_start(gui, data):
    timestamp = datetime.now().strftime("%H:%M:%S")
    doc = data.doc.strip().replace("\n", " ") if data.doc else "(No documentation)"
    text = (
        f"[{timestamp}] 📂 SUITE STARTED\n"
        f"  Name     : {data.name}\n"
        f"  Documentation: {doc}\n"
        f"{'-' * 60}\n"
    )
    _write(gui, text, "header")

def log_suite_end(gui, data, result):
    timestamp = datetime.now().strftime("%H:%M:%S")
    message = result.message.strip() if result.message else "(Empty)"
    text = (
        f"[{timestamp}] 📁 SUITE ENDED\n"
        f"  Name     : {data.name}\n"
        f"  Status   : {result.status}\n"
        f"  Message  : {message}\n"
        f"{'-' * 60}\n"
    )
    tag = "pass" if result.status.upper() == "PASS" else "fail"
    _write(gui, text, tag)

def log_test_start(gui, data):
    timestamp = datetime.now().strftime("%H:%M:%S")
    tags = ", ".join(data.tags or [])
    doc = data.doc.strip().replace("\n", " ") if data.doc else "(No documentation)"
    args = []
    try:
        args = [f"{k}={v}" for k, v in zip(data.args, data.arguments)]
    except:
        pass
    args_str = ", ".join(args) if args else "(No arguments)"

    text = (
        f"[{timestamp}] 🧪 TEST STARTED\n"
        f"  Name       : {data.name}\n"
        f"  Tags       : {tags}\n"
        f"  Documentation: {doc}\n"
        f"  Arguments  : {args_str}\n"
        f"{'-' * 60}\n"
    )
    _write(gui, text, "header")

def log_test_end(gui, data, result):
    timestamp = datetime.now().strftime("%H:%M:%S")
    message = result.message.strip() if result.message else "(Empty)"
    text = (
        f"[{timestamp}] ✅ TEST ENDED\n"
        f"  Name     : {data.name}\n"
        f"  Status   : {result.status}\n"
        f"  Message  : {message}\n"
        f"{'-' * 60}\n"
    )
    tag = "pass" if result.status.upper() == "PASS" else "fail"
    _write(gui, text, tag)

def _write(gui, text, tag):
    gui.failure_text.config(state="normal")
    gui.failure_text.insert("end", text, tag)
    gui.failure_text.config(state="disabled")
    gui.failure_text.see("end")
