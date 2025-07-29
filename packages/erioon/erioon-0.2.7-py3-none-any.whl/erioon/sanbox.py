# Copyright 2025-present Erioon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Visit www.erioon.com/dev-docs for more information about the python SDK


import tempfile
import time
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes import watch
from kubernetes.stream import stream

class Sandbox:
    def __init__(self, cluster_info, namespace, sa_name, kubeconfig, sandbox_id, cluster):
        """
        Initialize a Sandbox instance for executing code within a Kubernetes pod.

        Args:
            cluster_info (dict): Information about the Kubernetes cluster (e.g., FQDN).
            namespace (str): Kubernetes namespace where the sandbox pod operates.
            sa_name (str): ServiceAccount name used for generating access tokens.
            kubeconfig (str): Raw kubeconfig YAML string used to authenticate.
            sandbox_id (str): Name of the pod that serves as the sandbox environment.
            cluster (str): Indicates the type of access, e.g., 'viewAccess' for read-only.

        Attributes:
            user_kubeconfig_path (str): Path to a temporary kubeconfig file with service account credentials.
        """
        self.cluster_info = cluster_info
        self.namespace = namespace
        self.sa_name = sa_name
        self.kubeconfig = kubeconfig
        self.sandbox_id = sandbox_id
        self.cluster = cluster
        self.user_kubeconfig_path = self._generate_user_kubeconfig(cluster_info, kubeconfig, sa_name, namespace)
        
    def _is_read_only(self):
        """
        Determine if the current sandbox has read-only access.

        Returns:
            bool: True if the cluster is marked as 'viewAccess', otherwise False.
        """
        return self.cluster == "viewAccess"
    
    def _read_only_response(self):
        """
        Return a standardized error message for read-only access attempts.

        Returns:
            str: Access denied error message.
        """
        return "[Erioon Error - Sandbox access denied] This user is not allowed to perform any operations in the selected sandbox."

    def _generate_user_kubeconfig(self, cluster_info, kubeconfig, sa_name, namespace):
        """
        Generate a user-specific kubeconfig using a service account token.

        Steps:
        - Load the admin kubeconfig.
        - Request a token for the provided service account.
        - Construct a minimal kubeconfig using the token and certificate data.

        Args:
            cluster_info (dict): Contains cluster endpoint information (e.g., FQDN).
            kubeconfig (str): Raw kubeconfig YAML string used to request token.
            sa_name (str): ServiceAccount to use for token request.
            namespace (str): Namespace in which the SA exists.

        Returns:
            str: Path to the generated user kubeconfig file.
        """
        if self._is_read_only():
            return self._read_only_response()
        
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp_kubeconfig:
            tmp_kubeconfig.write(kubeconfig)
            kubeconfig_path = tmp_kubeconfig.name
            config.load_kube_config(config_file=kubeconfig_path)

        v1 = client.CoreV1Api()
        token_request = {
            "apiVersion": "authentication.k8s.io/v1",
            "kind": "TokenRequest",
            "spec": {"audiences": [], "expirationSeconds": 3600},
        }

        token_resp = v1.create_namespaced_service_account_token(sa_name, namespace, body=token_request)
        token = token_resp.status.token

        kubeconfig_dict = yaml.safe_load(kubeconfig)
        ca_crt = kubeconfig_dict["clusters"][0]["cluster"]["certificate-authority-data"]

        new_config = {
            "apiVersion": "v1",
            "kind": "Config",
            "clusters": [
                {
                    "name": "user-cluster",
                    "cluster": {
                        "server": f"https://{cluster_info['fqdn']}:443",
                        "certificate-authority-data": ca_crt,
                    },
                }
            ],
            "users": [
                {
                    "name": sa_name,
                    "user": {
                        "token": token
                    }
                }
            ],
            "contexts": [
                {
                    "name": f"{sa_name}-context",
                    "context": {
                        "cluster": "user-cluster",
                        "user": sa_name,
                        "namespace": namespace,
                    },
                }
            ],
            "current-context": f"{sa_name}-context",
        }

        with tempfile.NamedTemporaryFile("w", delete=False) as tmp_user_config:
            yaml.dump(new_config, tmp_user_config)
            return tmp_user_config.name

    def runCode(self, code, packages=None):
        """
        Launch a Kubernetes pod (if not already running), install optional packages, and execute Python code.

        Workflow:
        - Checks if a sandbox pod already exists and is running.
        - If not, it deletes any stale pod and starts a new pod with a Python container.
        - Installs additional packages via shell (if provided).
        - Runs the given Python code inside the pod using `python -c`.

        Args:
            code (str): Python code to execute inside the sandbox pod.
            packages (str, optional): Shell command string to install additional packages (e.g., "pip install numpy").

        Returns:
            str: Output (stdout and stderr) from executing the Python code.

        Raises:
            ApiException: If interactions with the Kubernetes API fail.
        """
        if self._is_read_only():
            return self._read_only_response()

        config.load_kube_config(config_file=self.user_kubeconfig_path)
        v1 = client.CoreV1Api()

        pod_exists = False
        pod_running = False

        try:
            pod = v1.read_namespaced_pod(name=self.sandbox_id, namespace=self.namespace)
            pod_exists = True
            if pod.status.phase == "Running":
                pod_running = True
        except ApiException as e:
            if e.status != 404:
                raise

        if not pod_exists or not pod_running:
            # Cleanup old pod if needed
            if pod_exists:
                v1.delete_namespaced_pod(name=self.sandbox_id, namespace=self.namespace)
                while True:
                    try:
                        v1.read_namespaced_pod(name=self.sandbox_id, namespace=self.namespace)
                        time.sleep(1)
                    except ApiException as e:
                        if e.status == 404:
                            break

            # Create new pod
            pod_manifest = client.V1Pod(
                metadata=client.V1ObjectMeta(name=self.sandbox_id),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="python",
                            image="python:3.10-slim",
                            command=["sh", "-c", "sleep infinity"],
                        )
                    ],
                    restart_policy="Never",
                ),
            )

            v1.create_namespaced_pod(namespace=self.namespace, body=pod_manifest)
            print(f"Erioon Sandbox '{self.sandbox_id}' is preparing...")

            # Wait for pod to be running and ready
            while True:
                pod_status = v1.read_namespaced_pod_status(self.sandbox_id, self.namespace)
                if pod_status.status.phase == "Running":
                    conditions = pod_status.status.conditions or []
                    if any(cond.type == "Ready" and cond.status == "True" for cond in conditions):
                        break
                time.sleep(1)
        else:
            print(f"Erioon Sandbox '{self.sandbox_id}' is running...")
            print(f"__________________________________________________\n")

        # Install additional packages if specified
        if packages:
            print(f"Installing user packages: {packages}")
            install_command = ["sh", "-c", packages]
            stream(
                v1.connect_get_namespaced_pod_exec,
                self.sandbox_id,
                self.namespace,
                container="python",
                command=install_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
            )

        # Execute the provided Python code
        exec_command = ["python", "-c", code]
        resp = stream(
            v1.connect_get_namespaced_pod_exec,
            self.sandbox_id,
            self.namespace,
            container="python",
            command=exec_command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
        )
        return resp
