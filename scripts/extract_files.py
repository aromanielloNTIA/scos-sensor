from io import StringIO, BytesIO
import sys
import os
import docker
import requests
import tempfile
import tarfile
import json
from pathlib import Path
import subprocess

if len(sys.argv) < 4:
    print("Usage: python extract_data.py <schedule_name> <token> <container>")

schedule = sys.argv[1]
token = sys.argv[2]
container_name = sys.argv[3]
output_dir = os.path.join(str(Path.home()), f"{schedule}_extracted_files")

# get metadata
headers = {'Authorization': f'Token {token}'}
response = requests.get(f"https://127.0.0.1/api/v1/tasks/completed/{schedule}/1/", verify=False, headers=headers)
response.raise_for_status()
response_data = response.json()
data = response_data["data"]

# get data files
os.makedirs(output_dir, exist_ok=True)
client = docker.from_env()
container = client.containers.get(container_name)
command = f"/bin/bash -c find /files -name \"{schedule}*.sigmf-data\""
print(f"command = {command}")
res = subprocess.run([f"docker exec {container_name} /bin/bash -c \"find /files -name {schedule}*.sigmf-data\""], stdout=subprocess.PIPE, encoding="utf-8", shell=True)
print(f"args = {res.args}")
print(f"stdout = {res.stdout}")
if res.returncode != 0:
    raise Exception("Error occurred in docker exec_run")
for line in res.stdout.splitlines():
    print(f"line = {line}")
    src_path = line.strip()
    res2 = subprocess.run([f"docker cp {container_name}:{src_path} {output_dir}"], shell=True)
    print(f"args = {res2.args}")
    name = os.path.splitext(os.path.basename(line))[0]
    out_file_name = os.path.join(output_dir, name + ".tar")
    print(f"copying {src_path} to {out_file_name}")
    recording_id = int(name.split("_")[-1])
    tr_data = data[recording_id-1]
    if tr_data["recording_id"] != recording_id:
        raise Exception("Recording ID doesn't match")
    metadata = tr_data["metadata"]
    with tarfile.open(out_file_name, "w") as tar_file:
        tarinfo = tarfile.TarInfo(name=f"{name}.sigmf-meta")
        binary_metadata = BytesIO(bytearray(json.dumps(metadata, indent=4), encoding="utf-8"))
        binary_metadata.seek(0)
        size = os.path.getsize(os.path.join(output_dir, os.path.basename(line)))
        tarinfo.size = len(binary_metadata.getvalue())
        with open(os.path.join(output_dir, os.path.basename(line)), "rb") as sigmf_data_file:
            data_tar_info = tarfile.TarInfo(name=os.path.basename(line))
            data_tar_info.size = size
            tar_file.addfile(tarinfo=data_tar_info, fileobj=sigmf_data_file)
        tar_file.addfile(tarinfo=tarinfo, fileobj=binary_metadata)
    os.remove(os.path.join(output_dir, os.path.basename(line)))
