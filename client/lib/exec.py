import subprocess

commands = {
    "gpu_power": "nvidia-smi -i {gpu_id} --format=csv,noheader,nounits --query-gpu=power.draw",
    "syslog": 'cat /var/log/syslog | grep -iE "error|warning"'
}

def exec(key, globals_dict=None):
    cmd = commands[key]

    if globals_dict is not None:
        cmd = cmd.format(**globals_dict)

    result = subprocess.run(cmd.split(" "), stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8').strip()
    return output
