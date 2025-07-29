import importlib
import multiprocessing


def start_server():
    """使用反射调用 eagle_eye_scraper.scheduler_visual.visual_application.start_visual_server"""
    module = importlib.import_module("eagle_eye_scraper.scheduler_visual.visual_application")
    start_func = getattr(module, "run_app")
    start_func()


def start_visual_scheduler():
    server_process = multiprocessing.Process(target=start_server)
    server_process.daemon = True
    server_process.start()
