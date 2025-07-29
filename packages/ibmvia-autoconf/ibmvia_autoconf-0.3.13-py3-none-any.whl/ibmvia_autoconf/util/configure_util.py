#!/bin/python
"""
@copyright: IBM
"""
import os, kubernetes, logging, sys, yaml, pyivia, datetime, subprocess, shutil, time, json
from . import constants as const
from .data_util import Map, FileLoader, CustomLoader, KUBE_CLIENT, KUBE_CLIENT_SLEEP
from kubernetes.stream import stream

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
_logger = logging.getLogger(__name__)

def config_base_dir():
    if const.CONFIG_BASE_DIR in os.environ.keys():
        return os.environ.get(const.CONFIG_BASE_DIR)
    elif const.LEGACY_CONFIG_BASE_DIR in os.environ.keys():
        _logger.warn("DEPRECIATED  The {} environment variable is depreciated, use the \"IVIA\" prefix'd " 
                     "properties instead".format(const.LEGACY_CONFIG_BASE_DIR))
        return os.environ.get(const.LEGACY_CONFIG_BASE_DIR)
    return os.path.expanduser("~") #Default is home directory


def config_yaml(config_file=None):
    if config_file:
        _logger.info("Reading file from provided path {}".format(config_file))
        return Map(yaml.load(open(config_file, 'r'), Loader=CustomLoader))
    cfg_file_var = const.CONFIG_YAML
    if const.LEGACY_CONFIG_YAML_ENV_VAR in os.environ.keys():
        cfg_file_var = const.LEGACY_CONFIG_YAML_ENV_VAR
        _logger.warn("DEPRECIATED  The {} environment variable is depreciated, use the \"IVIA\" prefix'd "
                     "properties instead".format(const.LEGACY_CONFIG_YAML_ENV_VAR))
    if cfg_file_var in os.environ.keys():
        cfg_file = os.environ.get(cfg_file_var)
        if not cfg_file.startswith("/"):
            cfg_file = config_base_dir() + '/' + cfg_file
        _logger.info("Reading file from env var {} = {}".format(cfg_file_var, cfg_file))
        return Map(yaml.load(open(cfg_file, 'r'), Loader=CustomLoader))
    elif config_base_dir() and cfg_file_var in os.listdir(config_base_dir()):
        base_dir = config_base_dir()
        _logger.info("Reading config file from {} env var: {}/config.yaml".format(
            const.CONFIG_BASE_DIR, base_dir))
        return Map(yaml.load(open(
            os.path.join(base_dir, cfg_file_var), 'r'), Loader=CustomLoader))
    else:
        raise RuntimeError("Failed to find a YAML configuration file, help!")


def read_files(base):
    contents = []
    if base.startswith("/"):
        contents = FileLoader("").read_files(base.lstrip("/"))
    else:
        contents = FileLoader(config_base_dir()).read_files(base)
    return contents


def read_file(fp):
    contents = None
    if fp.startswith("/"):
        contents = FileLoader("").read_file(fp.lstrip('/'))
    else:
        contents = FileLoader(config_base_dir()).read_file(fp)
    return contents


def mgmt_base_url(cfg=None):
    if cfg == None:
        cfg = config_yaml()
    if const.LEGACY_MGMT_URL_ENV_VAR in os.environ.keys():
        _logger.warn("DEPRECIATED  The {} environment variable is depreciated, use the \"IVIA\" prefix'd "
                     "properties instead".format(const.LEGACY_MGMT_URL_ENV_VAR))
        return os.environ.get(const.LEGACY_MGMT_URL_ENV_VAR, cfg.mgmt_base_url)
    else:
        return os.environ.get(const.MGMT_URL_ENV_VAR, cfg.mgmt_base_url)


def ext_user_creds(cfg=None):
    user = None; secret = None
    if const.MGMT_EXT_USER_ENV_VAR in os.environ.keys():
        user = os.environ.get(const.MGMT_EXT_USER_ENV_VAR)
    if const.MGMT_EXT_PWD_ENV_VAR in os.environ.keys():
        secret = os.environ.get(const.MGMT_EXT_PWD_ENV_VAR)
    if cfg and not user:
        user = cfg.get('mgmt_ext_user', None)
    if cfg and not secret:
        secret = cfg.get('mgmt_ext_pwd', None)
    if not secret: # Only require secret for API key
        old_user, old_pwd = creds(cfg) # Fall back to existing creds
        if not user:
            user = old_user
        if not secret:
            secret = old_pwd
    return (user, secret)


def creds(cfg=None):
    user = None
    secret = None
    if const.MGMT_USER_ENV_VAR in os.environ.keys():
        user = os.environ.get(const.MGMT_USER_ENV_VAR)
    elif const.LEGACY_MGMT_USER_ENV_VAR in os.environ.keys():
        _logger.warn("DEPRECIATED  The {} environment variable is depreciated, use the \"IVIA\" prefix'd "
                     "properties instead".format(const.LEGACY_MGMT_USER_ENV_VAR))
        user = os.environ.get(const.LEGACY_MGMT_USER_ENV_VAR)
    if const.MGMT_PWD_ENV_VAR in os.environ.keys():
        secret = os.environ.get(const.MGMT_PWD_ENV_VAR)
    elif const.LEGACY_MGMT_PWD_ENV_VAR in os.environ.keys():
        _logger.warn("DEPRECIATED  The {} environment variable is depreciated, use the \"IVIA\" prefix'd "
                     "properties instead".format(const.LEGACY_MGMT_PWD_ENV_VAR))
        secret = os.environ.get(const.LEGACY_MGMT_PWD_ENV_VAR)
    if user == None or secret == None:
        if cfg == None:
            cfg = config_yaml()
        if user == None:
            user = cfg.get('mgmt_user', None) # SSO requires username is null
        if secret == None:
            secret = cfg.get('mgmt_pwd', "admin")
    return (user, secret)


def old_creds(cfg=None):
    user = None
    secret = None
    if const.MGMT_OLD_PASSWORD_ENV_VAR in os.environ.keys():
        user = os.environ.get(const.MGMT_USER_ENV_VAR)
    elif const.LEGACY_MGMT_OLD_PASSWORD_ENV_VAR in os.environ.keys():
        user = os.environ.get(const.LEGACY_MGMT_USER_ENV_VAR)
    if const.MGMT_OLD_PASSWORD_ENV_VAR in os.environ.keys():
        secret = os.environ.get(const.MGMT_OLD_PASSWORD_ENV_VAR)
    elif const.LEGACY_MGMT_OLD_PASSWORD_ENV_VAR in os.environ.keys():
        _logger.warn("DEPRECIATED  The {} environment variable is depreciated, use the \"IVIA\" prefix'd "
                     "properties instead".format(const.LEGACY_MGMT_PWD_ENV_VAR))
        secret = os.environ.get(const.LEGACY_MGMT_OLD_PASSWORD_ENV_VAR)
    if user == None and cfg != None:
        user = cfg.get('mgmt_user', "admin")
    if secret == None and cfg != None:
        secret = cfg.get('mgmt_old_pwd', None)
    return (user, secret)


def _kube_reload_container(namespace, container):
    if not KUBE_CLIENT:
        _logger.error("Unable to restart deployment as kube client is null")
        return
    exec_commands = ['isam_cli', '-c', 'reload', 'all']
    response = stream(KUBE_CLIENT.CoreV1Api().connect_get_namespaced_pod_exec,
            container,
            namespace,
            command=exec_commands,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False)
    if 'The command completed successfully' in response:
        _logger.info(container + " container reloaded successfully")
    else:
        _logger.error(container + " container failed to reload")


def _kube_rollout_restart(namespace, deployment):
    if not KUBE_CLIENT:
        _logger.error("Unable to restart deployment as kube client is null")
        return
    #Get a list of the current pods
    pods = [ pod.metadata.name for pod in 
                KUBE_CLIENT.CoreV1Api().list_namespaced_pod(namespace, label_selector="app=" + deployment).items ]
    _logger.debug("Found {} pods for deployment {}\n{}".format(len(pods), deployment, pods))

    #Request a restart from the controller
    body = {'spec': {
                'template':{ 'metadata': { 'annotations': { 
                        'kubectl.kubernetes.io/restartedAt': str(datetime.datetime.utcnow().isoformat("T") + "Z") 
                } } }
        } }
    try:
        KUBE_CLIENT.AppsV1Api().patch_namespaced_deployment(deployment, namespace, body, pretty='true')
    except kubernetes.client.rest.ApiException as e:
        _logger.error("Exception when calling AppsV1Api->patch_namespaced_deployment: %s" % e)
        sys.exit(1)

    #Now request for the pods to be deleted; when this throws the pods are gone
    for pod in pods:
        count = 1
        while count < 10:
            try:
                KUBE_CLIENT.CoreV1Api().delete_namespaced_pod(name=pod, namespace=namespace)
            except kubernetes.client.rest.ApiException as e:
                if json.loads(e.body).get('code', -1) == 404:
                    break
            time.sleep(count * 10)
            count += 1
        if count == 10:
            _logger.error("Failed to delete pod {} for deployment {}".format(pod, deployment))
            sys.exit(1)


def _kube_wait_for_deployment(namespace, deployment):
    #Finally wait for the new pod list to be ready
    watcher = kubernetes.watch.Watch()
    for event in watcher.stream(func=KUBE_CLIENT.CoreV1Api().list_namespaced_pod,
                                namespace=namespace,
                                label_selector="app=" + deployment,
                                timeout_seconds=30):
        if event['object'].status.phase == "Running":
            watcher.stop()
            _logger.info("{} deployment is running".format(deployment))
            return
        elif event['type'] == "DELETED":
            watcher.stop()
            _logger.error("{} deployment was deleted while waiting to be restarted".format(deployment))
    _logger.error("{} deployment did not return to a running state".format(deployment))
    sys.exit(1) #Pod did not get marked as running :(

def _compose_restart_service(service, config):
    if shutil.which("docker-compose") == None:
        _logger.error("docker-compose not found on $PATH")
        sys.exit(1)
    composeYaml = None
    if const.DOCKER_COMPOSE_CONFIG in os.environ.keys():
        composeYaml = os.environ.get(const.DOCKER_COMPOSE_CONFIG)
    elif const.LEGACY_DOCKER_COMPOSE_CONFIG in os.environ.keys():
        _logger.warn("DEPRECIATED  The {} environment variable is depreciated, use the \"IVIA\" prefix'd "
                     "properties instead".format(const.LEGACY_DOCKER_COMPOSE_CONFIG))
        composeYaml = os.environ.get(const.DOCKER_COMPOSE_CONFIG)
    elif config.container.docker_compose_yaml is not None:
        composeYaml = config.container.docker_compose_yaml
    else:
        _logger.error("Unable to find docker-compose YAML configuration")
        sys.exit(1)
    if not composeYaml.startswith('/'):
        composeYaml = config_base_dir() + '/' + composeYaml
    ps = subprocess.run(['docker-compose', '-f' , composeYaml, 'restart', service])
    if ps.returncode != 0:
        _logger.error("Error restarting docker-compose container:\nstdout: {}\nstderr: {}".format(ps.stdout, ps.stderr))
        sys.exit(1)

def _docker_restart_container(container, config):
    if shutil.which("docker") == None:
        _logger.error("docker  not found on $PATH")
        sys.exit(1)
    ps = subprocess.run(['docker', 'restart', container])
    if ps.returncode != 0:
        _logger.error("Error restarting docker container:\nstdout: {}\nstderr{}".format(ps.stdout, ps.stderr))
        sys.exit(1)


def deploy_pending_changes(factory=None, isvaConfig=None, restartContainers=True):
    if not isvaConfig:
        isvaConfig = config_yaml()
    if not factory:
        factory = pyivia.Factory(mgmt_base_url(isvaConfig), *creds(isvaConfig))

    factory.get_system_settings().configuration.deploy_pending_changes()
    if factory.is_docker() == True:
        published = False
        for i in range(5):
            try:
                response = factory.get_system_settings().docker.publish()
                if response.success == True:
                    published = True
                    break
            except Exception as e:
                _logger.exception(e)
            _logger.warn(f"Failed to publish, retrying in 3 seconds (attempt {i + 1}/5)")
            time.sleep(3) # TODO config option?
        if published == True and restartContainers == True and isvaConfig.container != None:
            if isvaConfig.container.k8s_deployments is not None:
                namespace = isvaConfig.container.k8s_deployments.namespace
                #Are we restarting the containers or rolling out a restart to the deployment descriptor
                if isvaConfig.container.k8s_deployments.deployments is not None:
                    for deployment in isvaConfig.container.k8s_deployments.deployments:
                        _kube_rollout_restart(namespace, deployment)
                    for deployment in isvaConfig.container.k8s_deployments.deployments:
                        _kube_wait_for_deployment(namespace, deployment)

                elif isvaConfig.container.k8s_deployments.pods is not None:
                    for pod in isvaConfig.container.pods:
                        _kube_reload_container(namespace, pod)

            elif isvaConfig.container.compose_services:
                for service in isvaConfig.container.compose_services:
                    _compose_restart_service(service, isvaConfig)

            elif isvaConfig.container.containers is not None:
                for container in isvaConfig.container.containers:
                    _docker_restart_container(container, isvaConfig)

            else:
                _logger.error("Unable to perform container restart, this may lead to errors")
            _logger.info("Idle for {}s to allow orchestration to recover and Verify Identity Access "
                        "components to initialize.".format(KUBE_CLIENT_SLEEP))
            time.sleep(KUBE_CLIENT_SLEEP)
        else:
            _logger.debug("Not asked to restart containers")
