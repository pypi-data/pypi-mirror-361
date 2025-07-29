import os
import json
import tempfile
import requests
import posixpath
import contextlib

from typing import Optional, Any

from .entities import run
from .error.value_error import HaiqvValueError
from .utils.files import guess_mime_type
from .utils.log_config import setup_logger

__logger = None
__session = requests.Session()
__timeout = 3

# Notebook
def get_notebook_info(client_ip: str) -> Any:
    try:
        notebook_info = __session.get(f'{os.environ.get("_HAIQV_PLAT_URL")}/platform/resource/get-notebook-info?ip={client_ip}', timeout=__timeout)

        if notebook_info.status_code == 200:
            return notebook_info.json()
        else:
            __log_write('warning', f'notebook info fetch failed - client_ip: {client_ip} -> {notebook_info.text}')
            return HaiqvValueError(notebook_info.text)
    except Exception as e:
        __log_write('warning', f'notebook info fetch exception - client_ip: {client_ip}')
        return None


# Run
def create_run(exp_name: str, run_name: str, namespace: str, notebook_id: int, notebook_name: str, owner: str, owner_name: str) -> Any:
    data = {
        'exp_name': exp_name,
        'run_name': run_name,
        'namespace': namespace,
        'notebook_id': notebook_id,
        'notebook_name': notebook_name,
        'owner': owner,
        'owner_name': owner_name,
    }

    try:
        run_info = __session.post(f'{os.environ.get("_HAIQV_BASE_URL")}/experiment/run',
                                 data=json.dumps(data),
                                 headers={'Content-Type': 'application/json'},
                                 timeout=__timeout)

        if run_info.status_code == 200:
            __log_write('info', f'create_run ok - exp_name: {exp_name}, run_name: {run_name}')
            return run.Run(id=run_info.json()['run_id'], name=run_name)
        else:
            __log_write('warning', f'create_run failed - exp_name: {exp_name}, run_name: {run_name} -> {run_info.text}')
            return HaiqvValueError(run_info.text)
    except Exception as e:
        __log_write('warning', f'create_run exception - exp_name: {exp_name}, run_name: {run_name}')
        return None


def update_run(
        run_id: str,
        status: Optional[str] = None,
        is_end: Optional[bool] = False,
) -> Any:
    try:
        res = __session.post(f'{os.environ.get("_HAIQV_BASE_URL")}/experiment/run/update?run_id={run_id}&status={status}&is_end={is_end}', timeout=__timeout)

        if res.status_code == 200:
            __log_write('info', f'update_run ok - status: {status}, is_end: {is_end}')
        else:
            __log_write('warning', f'update_run failed - status: {status}, is_end: {is_end} -> {res.text}')
            return HaiqvValueError(res.text)
    except Exception as e:
        __log_write('warning', f'update_run exception - status: {status}, is_end: {is_end}')
        return None


# Parameter
def log_param(run_id: str, key: str, value: Any) -> Any:
    data = [
        {
            key: str(value)
        }
    ]
    try:
        res = __session.post(f'{os.environ.get("_HAIQV_BASE_URL")}/experiment/logging/batch-params?run_id={run_id}',
                            data=json.dumps(data),
                            headers={'Content-Type': 'application/json'},
                            timeout=__timeout)
        if res.status_code == 200:
            __log_write('info', f'log_param ok - key: {key}, value: {value}')
        else:
            __log_write('warning', f'log_param failed - key: {key}, value: {value} -> {res.text}')
            return HaiqvValueError(res.text)
    except Exception as e:
        __log_write('warning', f'log_param exception - key: {key}, value: {value}')
        return None


def log_params(run_id: str, data: Any) -> Any:
    try:
        res = __session.post(f'{os.environ.get("_HAIQV_BASE_URL")}/experiment/logging/batch-params?run_id={run_id}',
                            data=json.dumps(data),
                            headers={'Content-Type': 'application/json'},
                            timeout=__timeout)
        if res.status_code == 200:
            __log_write('info', f'log_params ok - data: {data}')
        else:
            __log_write('warning', f'log_params failed - data: {data} -> {res.text}')
            return HaiqvValueError(res.text)
    except Exception as e:
        __log_write('warning', f'log_params exception - data: {data}')
        return None


# Metric
def log_metric(run_id: str, key: str, value: float, step: int) -> Any:
    data = [
        {
            'key': key,
            'value': str(value),
            'step': step
        }
    ]
    try:
        res = __session.post(f'{os.environ.get("_HAIQV_BASE_URL")}/experiment/logging/batch-metrics?run_id={run_id}',
                            data=json.dumps(data),
                            headers={'Content-Type': 'application/json'},
                            timeout=__timeout)
        if res.status_code == 200:
            __log_write('info', f'log_metric ok - key: {key}, value: {value}, step={step}')
        else:
            __log_write('warning', f'log_metric failed - key: {key}, value: {value}, step={step} -> {res.text}')
            return HaiqvValueError(res.text)
    except Exception as e:
        __log_write('warning', f'log_metric exception - key: {key}, value: {value}, step={step}')
        return None


def log_metrics(run_id: str, data: Any) -> Any:
    try:
        res = __session.post(f'{os.environ.get("_HAIQV_BASE_URL")}/experiment/logging/batch-metrics?run_id={run_id}',
                            data=json.dumps(data),
                            headers={'Content-Type': 'application/json'},
                            timeout=__timeout)
        if res.status_code == 200:
            __log_write('info', f'log_metrics ok - data: {data}')
        else:
            __log_write('warning', f'log_metrics failed - data: {data} -> {res.text}')
            return HaiqvValueError(res.text)
    except Exception as e:
        __log_write('warning', f'log_metrics exception - data: {data}')
        return None


# Artifact
def log_artifact(run_id: str, local_file: str, artifact_path: str) -> Any:
    try:
        filename = os.path.basename(local_file)
        mime = guess_mime_type(filename)
        with open(local_file, 'rb') as f:
            res = __session.post(
                f'{os.environ.get("_HAIQV_BASE_URL")}/experiment/logging/artifacts?run_id={run_id}&artifact_path={artifact_path}',
                files={'local_file': (filename, f, mime)},
                timeout=__timeout
            )
            if res.status_code == 200:
                __log_write('info', f'log_artifact ok - local_file: {local_file}, artifact_path: {artifact_path}')
            else:
                __log_write('warning', f'log_artifact failed - local_file: {local_file}, artifact_path: {artifact_path} -> {res.text}')
                return HaiqvValueError(res.text)
    except Exception as e:
        __log_write('warning', f'log_artifact exception - local_file: {local_file}, artifact_path: {artifact_path}')
        return None


# Requirements
def log_requirements(run_id: str, text: str, requirement_file: str) -> Any:
    try:
        with _log_artifact_helper(run_id, requirement_file) as tmp_path:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(text)
    except Exception as e:
        __log_write('warning', 'log_requirements exception')
        return None


# metadata
def log_dataset_metadata(run_id: str, name: str, path: str, desc: str = None) -> Any:
    try:
        res = __session.post(f'{os.environ.get("_HAIQV_BASE_URL")}/experiment/logging/metadata-dataset?run_id={run_id}&name={name}&path={path}&description={desc}',
                            headers={'Content-Type': 'application/json'},
                            timeout=__timeout)
        if res.status_code == 200:
            __log_write('info', f'log_dataset_metadata ok - name: {name}, path: {path}, desc: {desc}')
        else:
            __log_write('warning', f'log_dataset_metadata failed - name: {name}, path: {path}, desc: {desc} -> {res.text}')
            return HaiqvValueError(res.text)
    except Exception as e:
        __log_write('warning', f'log_dataset_metadata exception - name: {name}, path: {path}, desc: {desc}')
        return None


def log_model_metadata(run_id: str, name: str, path: str, step: int, volume_name: str, volume_path: str, metric: Optional[dict] = None) -> Any:
    try:
        res = __session.post(f'{os.environ.get("_HAIQV_BASE_URL")}/experiment/logging/metadata-model?run_id={run_id}&name={name}&path={path}&step={step}&volume_name={volume_name}&volume_path={volume_path}',
                            data=json.dumps(metric),
                            headers={'Content-Type': 'application/json'},
                            timeout=__timeout)
        if res.status_code == 200:
            __log_write('info', f'log_model_metadata ok - name: {name}, path: {path}, step: {step}, metric: {metric}, volume_name: {volume_name}, volume_path: {volume_path}')
        else:
            __log_write('warning', f'log_model_metadata failed - name: {name}, path: {path}, step: {step}, metric: {metric}, volume_name: {volume_name}, volume_path: {volume_path} -> {res.text}')
            return HaiqvValueError(res.text)
    except Exception as e:
        __log_write('warning', f'log_model_metadata exception - name: {name}, path: {path}, step: {step}, metric: {metric}, volume_name: {volume_name}, volume_path: {volume_path}')
        return None


def keepalive(run_id: str) -> Optional[HaiqvValueError]:
    try:
        res = __session.post(f'{os.environ.get("_HAIQV_BASE_URL")}/experiment/run/heartbeat?run_id={run_id}',
                            headers={'Content-Type': 'application/json'},
                            timeout=__timeout)
        if res.status_code != 200:
            __log_write('warning', f'keepalive failed -> {res.text}')
            return HaiqvValueError(res.text)
    except Exception as e:
        __log_write('warning', 'keepalive failed')
        return None


@contextlib.contextmanager
def _log_artifact_helper(run_id, artifact_file):
    norm_path = posixpath.normpath(artifact_file)
    filename = posixpath.basename(norm_path)
    artifact_dir = posixpath.dirname(norm_path)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = os.path.join(tmp_dir, filename)
        yield tmp_path
        log_artifact(run_id, tmp_path, artifact_dir)


def create_logger(level: str):
    global __logger
    if __logger is None:
        __logger = setup_logger('client', level)


def __log_write(level: str, message: Any):
    if __logger:
        if level == 'info':
            __logger.info(message)
        elif level == 'error':
            __logger.error(message)
        elif level == 'warning' or level == 'debug':
            __logger.warning(message)
        else:
            return