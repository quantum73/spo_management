import math
import socket
import struct
import time
from dataclasses import dataclass
from enum import Enum

import numpy as np
from pyproj import Transformer


class TaskStatus(Enum):
    OK = "OK"
    BAD = "BAD"


@dataclass
class TaskResponse:
    content: str = "Unexpected error"
    status: TaskStatus = TaskStatus.BAD.value


class TCPCamClient:
    def __init__(self, ip: str = "127.0.0.1", port: int = 4545, timeout: float = 0.3) -> None:
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__addr = (ip, port)
        self.__timeout = timeout
        self.__waiting_cmd = "WAITING"

    def connect(self) -> None:
        print(f">>> [CLIENT SOCKET CONNECT TO {self.__addr}]")
        self.__sock.connect(self.__addr)

    def get_data(self, bytes_size: int = 1024) -> bytes:
        return self.__sock.recv(bytes_size)

    def set_pose(self, coords_data: tuple[float, ...]) -> None:
        coords_to_bytes = struct.pack('dddfff', *coords_data)
        self.__sock.send(coords_to_bytes)
        time.sleep(self.__timeout)

    def send_waiting_command(self) -> None:
        cmd_to_bytes = bytes(self.__waiting_cmd, 'utf-8')
        cmd_length = len(cmd_to_bytes)
        self.__sock.send(struct.pack("%ds" % cmd_length, cmd_to_bytes))

    def set_value(self, val: int) -> None:
        print(">>> [SEND SOME INTEGER VALUE]: {}".format(val))
        self.__sock.send(struct.pack('i', val))

    def __del__(self) -> None:
        self.__sock.close()
        print(">>> [CLIENT SOCKET CLOSED]")


class CreateDatasetTask:
    def __init__(self, ip: str, port: int, params: dict):
        self.__ok_code = b"END"
        self.__ip = ip
        self.__port = port
        self.__cam_client = TCPCamClient(ip=ip, port=port)
        self.__cam_client.connect()

        self.__samples_num = params.get("sample_count")
        self.__type_trajectory = params.get("trajectory_type")
        self.__D_start = params.get("d_start")
        self.__D_stop = params.get("d_finish")
        self.__H_start = params.get("h_start")
        self.__H_stop = params.get("h_finish")
        self.__velocity = params.get("velocity")
        self.__fps = params.get("frequency")

        if self.__type_trajectory == "glissade":
            interest_point = (
                params.get("finish_x_target"), params.get("finish_y_target"), params.get("finish_z_target"),
            )
        else:
            interest_point = (params.get("x_target"), params.get("y_target"), params.get("z_target"))
        self.__interest_point = interest_point
        self.__alpha = params.get("alpha", 20)

        self.__new_interest_point = (
            params.get("start_x_target"), params.get("start_y_target"), params.get("start_z_target"),
            params.get("finish_x_target"), params.get("finish_y_target"), params.get("finish_z_target"),
        )

    def get_samples_num(self) -> int:
        return self.__samples_num

    def get_type_trajectory(self) -> str:
        return self.__type_trajectory

    def get_D_start(self) -> float:
        return self.__D_start

    def get_D_stop(self) -> float:
        return self.__D_stop

    def get_H_start(self) -> float:
        return self.__H_start

    def get_H_stop(self) -> float:
        return self.__H_stop

    def get_velocity(self) -> float:
        return self.__velocity

    def get_interest_point(self) -> tuple[float, float, float]:
        return self.__interest_point

    def get_fps(self) -> int:
        return self.__fps

    def get_alpha(self) -> float:
        return self.__alpha

    def length(self, v) -> float:
        return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

    def normalize(self, v) -> list[float, float, float]:
        l = self.length(v)
        return [v[0] / l, v[1] / l, v[2] / l]

    def rad(self, deg) -> float:
        return deg * math.pi / 180

    def run(self) -> TaskResponse:
        response = TaskResponse()
        # Получаем размер пути
        path_size = self.__cam_client.get_data(4)
        path_size = int.from_bytes(path_size, signed=True, byteorder="little")
        print(">>> [PATH SIZE]: ", path_size)
        # Получаем путь до выборки
        dataset_path = self.__cam_client.get_data(path_size)
        dataset_path = dataset_path.decode("utf-8")
        print(">>> [DATASET PATH]: ", dataset_path)

        # Строим траекторию
        H0 = int(self.get_H_start() - self.get_interest_point()[2])
        R_start = math.sqrt(math.pow(self.get_D_start(), 2) + math.pow(H0, 2))
        step = self.get_velocity() / self.get_fps()
        step_count = math.ceil(math.fabs(self.get_D_start() - self.get_D_stop()) / step)

        rx = self.get_interest_point()[0] * 100
        ry = self.get_interest_point()[1] * 100
        rz = self.get_interest_point()[2] * 100

        # Отправляем число сэмплов
        samples_count = self.get_samples_num()
        print(f">>> [FULL SAMPLES COUNT]: {samples_count}")
        self.__cam_client.set_value(samples_count)

        # инициализация трансформера координат
        trfmer_geo2utm = Transformer.from_crs("EPSG:4326", "EPSG:32637")
        trfmer_utm2geo = Transformer.from_crs("EPSG:32637", "EPSG:4326")
        # utm координаты точки финиша
        x_f, y_f = trfmer_geo2utm.transform(self.__new_interest_point[3], self.__new_interest_point[4])
        z_f = self.__new_interest_point[5]
        xv_f = np.array((x_f, y_f, z_f))

        x_s, y_s = trfmer_geo2utm.transform(self.__new_interest_point[0], self.__new_interest_point[1])
        z_s = self.__new_interest_point[2]
        xv_s = np.array((x_s, y_s, z_s))

        # Отправляем данные по построенной траектории
        for i in range(samples_count):
            print(f">>> [Step {i + 1}]")
            alpha = i / samples_count
            xv_cur = xv_s * (1 - alpha) + xv_f * alpha
            lat, lon = trfmer_utm2geo.transform(xv_cur[0], xv_cur[1])

            print(f">>> [LAT, LON, Z]: {lat} {lon} {xv_cur[2]}")
            coords = (lat, lon, xv_cur[2], 0, 0, 0)
            self.__cam_client.set_pose(coords)

        # Проверяем ответный сигнал
        print(">>> [SEND WAITING COMMAND]")
        self.__cam_client.send_waiting_command()

        print(">>> [WAITING ANSWER]")
        try:
            answer = self.__cam_client.get_data()
        except socket.timeout as timeout_err:
            print(">>> [TIMEOUT ERROR]: ", timeout_err)
            response.content = socket_err.__class__.__name__
        except socket.error as other_err:
            print(">>> [OTHER ERROR]: ", other_err)
            response.content = socket_err.__class__.__name__
        else:
            print(">>> [ANSWER]: ", answer)
            if answer == self.__ok_code:
                response.status = TaskStatus.OK.value
                response.content = dataset_path

        return response


if __name__ == '__main__':
    json_data = {
        'scene': 'oka',
        'title': 'Test sample',
        'sample_count': 100,
        'trajectory_type': 'glissade',
        'd_start': 12,
        'd_finish': 500,
        'h_start': 150,
        'h_finish': 1000,
        'start_x_target': 55.037095,
        'start_y_target': 38.819087,
        'start_z_target': 0,
        'finish_x_target': 55.034686,
        'finish_y_target': 38.821543,
        'finish_z_target': 100,
        'h_min': None,
        'h_max': None,
        'r_x': None,
        'r_y': None,
        'r_z': 10.0,
        'x_target': None,
        'y_target': None,
        'z_target': None,
        'frequency': 25,
        'velocity': 100,
        'submit': True,
        'from_json': '',
        'sensor_name': 'GOES TV',
        'sensor_type': 'TV',
        'resolution_x': 234,
        'resolution_y': 67,
        'size_x': 345,
        'size_y': 346,
        'field_view': 26,
        'host': '10.24.50.4',
        'port': 4545,
        'clear_sensor': False,
    }
    try:
        runner = CreateDatasetTask(ip=json_data.get('host'), port=json_data.get('port'), params=json_data)
        res = runner.run()
        print(res)
    except socket.error as socket_err:
        print(">>> [SOCKET ERROR]: ", socket_err)
