from lib.database import Database
from lib.exec import exec
import psutil
import time
import GPUtil
from lib.decorators import set_interval
import settings

def run():
    db = Database()
    _time = int(time.time())

    cpu_usage = psutil.cpu_percent()
    disk_space = psutil.disk_usage('/var/lib/docker')
    disk_space_root = psutil.disk_usage('/')
    disk_usage = psutil.disk_io_counters(perdisk=False)
    network_usage = psutil.net_io_counters(pernic=True)
    networksum = 0

    def get_average(items):
        items = [item.current for item in items]
        return sum(items) / len(items)

    def get_CPUTemps():
        testCPUTemp = psutil.sensors_temperatures()
        if 'coretemp' in testCPUTemp:
            testCPUTemp = get_average(testCPUTemp['coretemp'])
            return testCPUTemp
        if 'k10temp' in testCPUTemp:
            testCPUTemp = (testCPUTemp.get('k10temp')[0][1])
            return testCPUTemp
        testCPUTemp = open("/sys/class/thermal/thermal_zone0/temp", 'r').readlines()
        if testCPUTemp:
            testCPUTemp = float(testCPUTemp[0]) / 1000
            return testCPUTemp
        return 0

    hardware_records = []

    hardware_records.append({
        "component": "ram",
        "hw_id": None,
        "utilisation": psutil.virtual_memory().percent,
        "temperature": None,
        "power_consumption": None,
    })

    hardware_records.append({
        "component": "disk_space",
        "hw_id": None,
        "utilisation": disk_space.percent,
        "temperature": None,
        "power_consumption": None,
    })

        hardware_records.append({
        "component": "disk_space_root",
        "hw_id": None,
        "utilisation": disk_space.percent,
        "temperature": None,
        "power_consumption": None,
    })

    # Add other hardware records in a similar way

    for item in network_usage:
        networksum = networksum + network_usage[item].bytes_recv + network_usage[item].bytes_sent

    hardware_records.append({
        "component": "network",
        "hw_id": None,
        "utilisation": networksum,
        "temperature": None,
        "power_consumption": None,
    })

    hardware_records.append({
        "component": "cpu",
        "hw_id": None,
        "utilisation": psutil.cpu_percent(),
        "temperature": None,
        "power_consumption": None,
    })

    for gpu in GPUtil.getGPUs():
        gpu_power_consumption = float(exec("gpu_power", {"gpu_id": gpu.id}))
        hardware_records.append({
            "component": "gpu",
            "hw_id": gpu.id,
            "utilisation": gpu.load * 100,
            "temperature": gpu.temperature,
            "power_consumption": gpu_power_consumption,  # Use the obtained power consumption value
        })


    # Insert data in batches
    db.insert_batch_hardware(hardware_records, _time)

if __name__ == "__main__":
    run()
