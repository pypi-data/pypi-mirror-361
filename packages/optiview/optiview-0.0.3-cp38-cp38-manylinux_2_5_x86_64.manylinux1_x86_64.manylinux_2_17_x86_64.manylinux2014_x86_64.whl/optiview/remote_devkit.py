# Copyright (c) 2025 SiMa.ai
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os
import re
import logging
import os
import posixpath
from scp import SCPClient
from shlex import quote
import socket
from optiview.remotefs import _load_remote_config, RemoteFS, create_ssh_client

def is_remote_devkit_configured():
    """
    Determines if the remote devkit is configured as a remote (non-local) system.

    Criteria:
    - `_load_remote_config()` must succeed (i.e., cfg.json exists and contains expected fields).
    - The IP must not be 127.0.0.1, or if it is, then rootPassword must be present.

    Returns:
        bool: True if the remote devkit is considered remotely configured, False otherwise.
    """
    try:
        creds = _load_remote_config()
        ip = creds.get("host")
        password = creds.get("password")

        return ip != "127.0.0.1"

    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        return False

def get_remote_devkit_ip():
    """
    Returns the IP address of the remote devkit from config.

    Returns:
        str: IP address as a string (e.g., '192.168.2.10')
    
    Raises:
        FileNotFoundError, ValueError, json.JSONDecodeError if config is invalid
    """
    creds = _load_remote_config()
    ip = creds.get("host")
    if not ip:
        raise ValueError("Missing 'host' in remote devkit config")
    return ip

def is_remote_devkit_connected(host=None, port=22, timeout=2):
    """
    Lightweight check to see if the remote devkit is reachable over TCP.

    Args:
        host (str): Remote hostname or IP.
        port (int): Port to test (default is 22 for SSH).
        timeout (int): Connection timeout in seconds.

    Returns:
        bool: True if the host is reachable, False otherwise.
    """
    if host is None:
        creds = _load_remote_config()
        host = creds["host"]

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False

def check_remote_process_status(app_name):
    try:
        ssh = create_ssh_client()
        try:
            pattern = f"/data/simaai/applications/{app_name}/bin/gst_app"
            cmd = f"ps -ef | grep {quote(pattern)} | grep -v grep"

            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode().strip()

            pids = []
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    pids.append(parts[1])

            return {
                "is_running": len(pids) > 0,
                "matching_pids": pids,
                "log_path": f"/tmp/{app_name}.log"
            }
        finally:
            ssh.close()
    except Exception as e:
        return {
            "is_running": False,
            "error": str(e),
            "matching_pids": [],
            "log_path": f"/tmp/{app_name}.log"
        }


def get_remote_metrics(app_name):
    ssh = create_ssh_client()

    def run(cmd):
        stdin, stdout, stderr = ssh.exec_command(cmd)
        return stdout.read().decode()

    # CPU load
    cpu_raw = run("top -bn1 | grep 'Cpu(s)'")
    cpu_match = re.search(r"(\d+\.\d+)\s+us", cpu_raw)
    cpu_percent_total = float(cpu_match.group(1)) if cpu_match else None

    # Memory
    mem_raw = run("free -b")
    mem_match = re.findall(r"Mem:\s+(\d+)\s+(\d+)\s+(\d+)", mem_raw)
    memory_usage = {}
    if mem_match:
        total, used, _ = map(int, mem_match[0])
        memory_usage = {
            "total": total,
            "used": used,
            "percent": round((used / total) * 100, 1) if total else 0
        }

    # MLA memory
    mla_allocated_bytes = None
    try:
        mla_raw = run("cat /dev/simaai-mem")
        match = re.search(r"Total allocated size: (0x[0-9a-fA-F]+)", mla_raw)
        if match:
            mla_allocated_bytes = int(match.group(1), 16)
    except:
        pass

    # Disk
    disk_raw = run("df -B1 /data | tail -1")
    disk_parts = disk_raw.split()
    disk_usage = {}
    if len(disk_parts) >= 5:
        disk_usage = {
            "mount": "/data",
            "total": int(disk_parts[1]),
            "used": int(disk_parts[2]),
            "free": int(disk_parts[3]),
            "percent": int(disk_parts[4].rstrip('%'))
        }

    # Temperature (if available)
    avg_temp = None
    try:
        temp_raw = run("cat /sys/kernel/temperature_profile")
        temps = [int(m.group(1)) for m in re.finditer(r"Temperature.*is (\d+) C", temp_raw)]
        if temps:
            avg_temp = sum(temps) / len(temps)
    except:
        pass

    ssh.close()
    return {
        "cpu_load": cpu_percent_total,
        "memory": memory_usage,
        "mla_allocated_bytes": mla_allocated_bytes,
        "disk": disk_usage,
        "pipeline_status": check_remote_process_status(app_name),
        "temperature_celsius_avg": avg_temp,
        "REMOTE": True
    }

def delete_remote_file(remote_path):
    """
    Deletes a file from the remote device using RemoteFS (SFTP).

    Args:
        remote_path (str): Absolute path to the file on the remote system.

    Returns:
        dict: {"status": "deleted"} or {"error": "..."}
    """
    try:
        with RemoteFS() as rfs:
            if not rfs.exists(remote_path):
                return {"error": f"File not found: {remote_path}"}

            rfs.sftp.remove(remote_path)
            logging.info(f"🗑️ Deleted remote file: {remote_path}")
            return {"status": "deleted"}

    except Exception as e:
        logging.error(f"Failed to delete remote file {remote_path}: {e}")
        return {"error": str(e)}

def handle_remote_mpk_upload(mpk_path, approot):
    """
    Handles uploading and installing an .mpk file on a remote devkit via SSH.

    Args:
        mpk_path (str): Path to the local .mpk file
        approot (str): Root path (e.g., /home/dev/mpk_apps) where RPM installs

    Yields:
        str: Status messages for streaming to the frontend.
    """
    remote_temp_dir = f"/tmp/mpk_upload_{os.path.basename(mpk_path).replace('.', '_')}"

    ssh = create_ssh_client()

    # Step 1: Create temp dir on remote
    yield f"📁 Creating temp dir on the remote devkit: {remote_temp_dir}\n"
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {remote_temp_dir}")
    if stderr.read():
        raise RuntimeError("Failed to create temp dir on remote.")

    # Step 2: Copy .mpk file to remote
    yield "📤 Uploading .mpk file to the remote devkit...\n"
    with SCPClient(ssh.get_transport()) as scp:
        remote_mpk_path = posixpath.join(remote_temp_dir, os.path.basename(mpk_path))
        scp.put(mpk_path, remote_mpk_path)

    # Step 3: Unzip the .mpk
    yield "📦 Extracting .mpk file on the remote devkit...\n"
    unzip_cmd = f"unzip -o {remote_mpk_path} -d {remote_temp_dir}"
    stdin, stdout, stderr = ssh.exec_command(unzip_cmd)
    unzip_err = stderr.read().decode()
    if "cannot find or open" in unzip_err.lower():
        raise RuntimeError("Failed to unzip .mpk on remote.")

    # Step 4: Check for manifest and rpm
    print('step 4...')
    yield "🔍 Locating manifest and installer.rpm...\n"
    find_cmd = f"find {remote_temp_dir} -name manifest.json -o -name installer.rpm"
    stdin, stdout, stderr = ssh.exec_command(find_cmd)
    found_files = stdout.read().decode().splitlines()

    manifest_path = next((f for f in found_files if f.endswith("manifest.json")), None)
    rpm_path = next((f for f in found_files if f.endswith("installer.rpm")), None)

    if not manifest_path or not rpm_path:
        raise RuntimeError(f"Missing manifest.json or installer.rpm in .mpk (searched under {remote_temp_dir})")

    # Step 5: Run rpm -qpl to find install path
    yield f"📂 Running rpm query... {rpm_path}\n"
    rpm_query = f"rpm -qpl {rpm_path}"
    stdin, stdout, stderr = ssh.exec_command(rpm_query)
    rpm_files = stdout.read().decode().splitlines()

    # Step: identify app subdir directly under approot
    candidate_dirs = [line.strip() for line in rpm_files if line.startswith(approot)]
    app_dirs = set()

    # Match full app directories like /data/simaai/applications/<app-name>/bin or /lib/etc/share
    pattern = re.compile(rf"^{re.escape(approot)}/([^/]+)/")
    for path in candidate_dirs:
        match = pattern.search(path)
        if match:
            app_name = match.group(1)
            app_dirs.add(f"{approot}/{app_name}")

    # If nothing matched, fallback to the deepest common directory below approot
    if not app_dirs:
        parent_dirs = [os.path.dirname(p) for p in candidate_dirs]
        common_root = os.path.commonprefix(parent_dirs)
        app_dirs = [common_root.rstrip("/")]

    if not app_dirs:
        raise RuntimeError(f"❌ Could not identify install path from RPM.\nRPM contents:\n" + "\n".join(rpm_files))

    pipeline_dir = sorted(app_dirs, key=lambda p: -p.count("/"))[0]

    # Step 6: Install the RPM
    yield f"📥 Installing RPM to: {pipeline_dir} on the remote devkit\n"
    rpm_install = f"rpm -U --replacepkgs {rpm_path}"
    stdin, stdout, stderr = ssh.exec_command(rpm_install)
    err = stderr.read().decode()
    if "error" in err.lower():
        raise RuntimeError(f"RPM installation failed: {err}")

    # Step 7: Copy manifest.json to pipeline directory
    yield "📄 Copying manifest.json on the remote devkit\n"
    remote_manifest_target = posixpath.join(pipeline_dir, 'manifest.json')
    copy_cmd = f"cp {manifest_path} {remote_manifest_target}"
    stdin, stdout, stderr = ssh.exec_command(copy_cmd)
    if stdout.channel.recv_exit_status() != 0:
        raise RuntimeError(f"Failed to copy manifest.json to {remote_manifest_target}")

    yield "🎉 Remote install complete!\n"
    ssh.close()


def run_remote_gst_pipeline(app_name, gst_command, env_vars):
    """
    Executes a GStreamer pipeline remotely via SSH using provided environment.

    Args:
        app_name (str): Name of the application for logging/debugging.
        gst_command (str): GStreamer pipeline launch command.
        env_vars (dict): Environment variables to export remotely.

    Returns:
        (bool, str): (True, None) if success; (False, error_message) if failed.
    """
    try:
        ssh = create_ssh_client()
        try:
            # Quote each env var value
            exports = " ".join(f'{k}={quote(v)}' for k, v in env_vars.items())

            # Quote the full command (pipeline + exports) into a bash -c string
            full_inner_cmd = f"{exports} {gst_command}".strip()
            remote_cmd = f"nohup bash -c {quote(full_inner_cmd)} > /tmp/{app_name}.log 2>&1 &"

            logging.info(f"🚀 Starting remote app '{app_name}' with command: {remote_cmd}")
            stdin, stdout, stderr = ssh.exec_command(remote_cmd)

            err = stderr.read().decode().strip()
            if err:
                return False, err

            return True, None
        finally:
            ssh.close()
    except Exception as e:
        return False, f"SSH error: {str(e)}"
    
def stop_remote_process(app_name):
    """
    Stops a remote GStreamer process by name.

    Args:
        app_name (str): The app name used to identify the process (e.g., YoloV7).

    Returns:
        dict: {
            "stopped_pids": list of PIDs terminated,
            "error": optional error message if failure occurs
        }
    """
    try:
        ssh = create_ssh_client()
        try:
            # Build pattern based on the known path structure
            pattern = f"/data/simaai/applications/{app_name}/bin/gst_app"
            find_cmd = f"ps -ef | grep {quote(pattern)} | grep -v grep"

            stdin, stdout, stderr = ssh.exec_command(find_cmd)
            output = stdout.read().decode().strip()

            pids_to_kill = []
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    pid = parts[1]
                    pids_to_kill.append(pid)

            if not pids_to_kill:
                return {"stopped_pids": [], "message": "No matching processes found."}

            kill_cmd = f"kill {' '.join(pids_to_kill)}"
            ssh.exec_command(kill_cmd)

            return {"stopped_pids": pids_to_kill}
        finally:
            ssh.close()

    except Exception as e:
        return {"stopped_pids": [], "error": str(e)}
    
def run_remote_gst_inspect(plugin, env_vars):
    """
    Executes gst-inspect-1.0 for a given plugin on the remote devkit via SSH.

    Args:
        plugin (str): GStreamer plugin name.
        env_vars (dict): Environment variables for the remote environment.

    Returns:
        (int, str): Tuple of (exit_code, combined stdout/stderr output)
    """
    try:
        ssh = create_ssh_client()
        try:
            exports = " ".join(f"{k}='{v}'" for k, v in env_vars.items())
            cmd = f"{exports} gst-inspect-1.0 {plugin}"
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)

            output = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()
            return exit_code, output.strip()
        finally:
            ssh.close()
    except Exception as e:
        return -1, f"[Remote error] {str(e)}"
