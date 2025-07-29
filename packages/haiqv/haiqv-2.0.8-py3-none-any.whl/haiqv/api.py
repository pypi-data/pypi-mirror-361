import os
import pkg_resources
from importlib_metadata import distributions
import __main__
import signal

from typing import Any, Dict, Optional
from datetime import datetime

from .binding.args_bind import ArgBind
from .binding.yaml_bind import YamlBind
from .entities.run import Run
from .store import ClientStore, RunStore, NotebookStore, LogStore
from .utils import get_ip
from .job.background_task import BackGroundTask
from .job.keepalive_task import KeepAliveTask
from . import client
from .error.value_error import HaiqvValueError
from .utils.log_config import setup_logger


__HAIQV_UPLOAD_INTERVAL = 2
__HAIQV_STD_LOG_FILE = 'output_'
__active_run = None
__logger = None


class ActiveRun(Run):

    def __init__(self, run=None):
        if run is not None:
            Run.__init__(self, run.info)

    def __enter__(self):
        return self

    def __del__(self):
        finalize()

    def __exit__(self, exc_type, exc_val, exc_tb):
        status = 'Finished' if exc_type is None else 'Failed'
        finalize(status)


def signal_handler(signum, frame):
    if signum == signal.SIGINT:
        finalize("Killed")
        exit(1)

    if signum == signal.SIGTERM:
        finalize("Finished")
        exit(0)


def _get_current_active_run() -> Optional[Run]:
    if RunStore.id() is None:
        return None
    return RunStore()


def set_client_ip(client_ip: str):
    ClientStore(client_ip)


def get_client_ip():
    if ClientStore.ip() is not None:
        return ClientStore.ip()
    else:
        return get_ip()


def get_run_name() -> str:
    # assert RunStore.status() and RunStore.id() is not None, 'has not active runs, please run init() command first'
    if RunStore.id() is None:
        __log_write('warning', 'get_run_name - has not active runs')
        return ''
    return RunStore().name


def set_log_level(log_level: str):
    LogStore(log_level)


def init(
        experiment_name: str,
        run_name: Optional[str] = None,
        auto_track_args: Optional[bool] = False,
        enable_output_upload: Optional[bool] = False
) -> ActiveRun:
    assert experiment_name, 'init requires experiment name'

    client_ip = ClientStore.ip()
    if client_ip is None:
        client_ip = get_ip()
    assert client_ip, 'has not valid IP. You can specify IP address using set_client_ip() command before init()'

    notebook_info = client.get_notebook_info(client_ip)
    if notebook_info is None or isinstance(notebook_info, HaiqvValueError):
        return ActiveRun(None)

    notebook_name = notebook_info.get('name', '')
    __log_write('info', f'notebook name: {notebook_name}')
    NotebookStore(notebook_info)

    if RunStore.status():
        RunStore.flush()

    if run_name:
        run_name_final = f"{run_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    else:
        run_name_final = f"run-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    run_info = client.create_run(
        exp_name=experiment_name,
        run_name=run_name_final,
        namespace=NotebookStore.namespace(),
        notebook_id=NotebookStore.id(),
        notebook_name=NotebookStore.name(),
        owner=NotebookStore.owner(),
        owner_name=NotebookStore.owner_name()
    )
    if run_info is None or isinstance(run_info, HaiqvValueError):
        return ActiveRun(None)

    if not RunStore.status():
        RunStore(run_info)

    client.update_run(
        run_id=run_info.id,
        status='Running'
    )

    running_file = getattr(__main__, '__file__', None)
    if running_file and os.path.getsize(running_file) > 0:
        log_artifact(running_file, "code")

    # dists = [str(d).replace(" ", "==") for d in pkg_resources.working_set]
    dists = [f"{dist.metadata['Name']}=={dist.version}" for dist in distributions()]
    client.log_requirements(run_info.id, '\n'.join(dists), "requirements.txt")

    if auto_track_args:
        ArgBind.patch_argparse(log_params)
        YamlBind.patch_load(log_params)

    if enable_output_upload:
        bg = BackGroundTask()
        std_log_filename = f'{__HAIQV_STD_LOG_FILE}_{run_name_final}.log'
        bg.set_std_log_config(std_log_filename, __HAIQV_UPLOAD_INTERVAL, log_artifact)
        bg.start_std_log()

    run = ActiveRun()

    global __active_run
    __active_run = run

    ka = KeepAliveTask()
    ka.set_fn(keepalive)
    ka.start(run_info.interval)

    # signal
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    return run


def finalize(status: str = "Finished") -> None:
    bg = BackGroundTask()
    if bg is not None:
        bg.end_std_log()
    ka = KeepAliveTask()
    if ka is not None:
        ka.stop()
    if RunStore.status():
        active_run = _get_current_active_run()
        if active_run is not None:
            l_level = 'info'
            if status == 'Killed':
                l_level = 'warning'
            __log_write(l_level, f'finalize run name: {active_run.name}, status: {status}')
            client.update_run(
                run_id=active_run.id,
                status=status,
                is_end=True,
            )
        RunStore.flush()


def log_param(key: str, value: Any) -> None:
    active_run = _get_current_active_run()
    if active_run is not None:
        run_id = active_run.id
        client.log_param(run_id=run_id, key=key, value=value)
    else:
        __log_write('warning', 'log_param - has not active run')


def log_params(params: Dict[str, Any]) -> None:
    active_run = _get_current_active_run()
    if active_run is not None:
        run_id = active_run.id
        data = [{key: str(value)} for key, value in params.items()]
        client.log_params(run_id=run_id, data=data)
    else:
        __log_write('warning', 'log_params - has not active run')


def log_metric(key: str, value: float, step: int) -> None:
    active_run = _get_current_active_run()
    if active_run is not None:
        run_id = active_run.id
        client.log_metric(run_id=run_id, key=key, value=value, step=step)
    else:
        __log_write('warning', 'log_metric - has not active run')


def log_metrics(metrics: Dict[str, float], step: int) -> None:
    active_run = _get_current_active_run()
    if active_run is not None:
        run_id = active_run.id
        data = [{'key': key, 'value': str(value), 'step': step} for key, value in metrics.items()]
        client.log_metrics(run_id=run_id, data=data)
    else:
        __log_write('warning', 'log_metrics - has not active run')



def log_artifact(local_file: str, artifact_path: Optional[str] = None) -> None:
    active_run = _get_current_active_run()
    if active_run is not None:
        run_id = active_run.id
        client.log_artifact(run_id=run_id, local_file=local_file, artifact_path=f'{artifact_path}')
    else:
        __log_write('warning', 'log_artifact - has not active run')


def log_dataset_metadata(name: str, path: str, desc: str = None):
    active_run = _get_current_active_run()
    if active_run is not None:
        run_id = active_run.id
        client.log_dataset_metadata(
            run_id=run_id,
            name=name,
            path=path,
            desc=desc
        )
    else:
        __log_write('warning', 'log_dataset_metadata - has not active run')


def log_model_metadata(name: str, path: str, step: int, metric: Optional[dict] = None):
    active_run = _get_current_active_run()
    if active_run is not None:
        run_id = active_run.id
        volume_name, volume_path = NotebookStore.get_volume_info(path)
        client.log_model_metadata(
            run_id=run_id,
            name=name,
            path=path,
            step=step,
            volume_name=volume_name,
            volume_path=volume_path,
            metric=metric
        )
    else:
        __log_write('warning', 'log_model_metadata - has not active run')


def __log_write(level: str, message: Any):
    global __logger
    if __logger is None:
        __logger = setup_logger('api', LogStore.level())
    client.create_logger(LogStore.level())

    if __logger:
        if level == 'info':
            __logger.info(message)
        elif level == 'error':
            __logger.error(message)
        elif level == 'warning' or level == 'debug':
            __logger.warning(message)
        else:
            return


def keepalive() -> None:
    active_run = _get_current_active_run()
    if active_run is not None:
        run_id = active_run.id
        client.keepalive(run_id=run_id)
