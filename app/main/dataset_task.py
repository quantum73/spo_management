import math
import socket
import struct
import time
from dataclasses import dataclass
from enum import Enum

import numpy as np

from .. import get_logger

logger = get_logger(__name__)


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
        logger.info(">>> [CLIENT SOCKET CONNECT TO {}]".format(self.__addr))
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
        logger.info(">>> [SEND SOME INTEGER VALUE]: {}".format(val))
        self.__sock.send(struct.pack('i', val))

    def __del__(self) -> None:
        self.__sock.close()
        logger.info(">>> [CLIENT SOCKET CLOSED]")


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
        logger.info(">>> [PATH SIZE]: {}".format(path_size))
        # Получаем путь до выборки
        dataset_path = self.__cam_client.get_data(path_size)
        dataset_path = dataset_path.decode("utf-8")
        logger.info(">>> [DATASET PATH]: {}".format(dataset_path))

        # Строим траекторию
        H0 = int(self.get_H_start() - self.get_interest_point()[2])
        R_start = math.sqrt(math.pow(self.get_D_start(), 2) + math.pow(H0, 2))
        step = self.get_velocity() / self.get_fps()
        step_count = math.ceil(math.fabs(self.get_D_start() - self.get_D_stop()) / step)

        rx = self.get_interest_point()[0] * 100
        ry = self.get_interest_point()[1] * 100
        rz = self.get_interest_point()[2] * 100

        # Отправляем число сэмплов
        full_samples_count = self.get_samples_num() * step_count
        logger.info(">>> [FULL SAMPLES COUNT]: {}".format(full_samples_count))
        self.__cam_client.set_value(full_samples_count)

        # Отправляем данные по построенной траектории
        for i in range(self.get_samples_num()):
            alpha = self.get_alpha()
            x0 = self.get_interest_point()[0] - R_start * math.sin(self.rad(alpha))
            y0 = self.get_interest_point()[1] + R_start * math.cos(self.rad(alpha))

            # вектор движения
            vec = np.asarray([self.get_interest_point()[0] - x0, self.get_interest_point()[1] - y0, -H0])
            vec = self.normalize(vec)
            vec[:] = [v * step for v in vec]
            for j in range(step_count):
                logger.info(">>> [STEP]: {}_{}".format(i, j))
                xc = (x0 + vec[0] * j) * 100
                yc = (y0 + vec[1] * j) * 100
                zc = (self.get_H_start() + vec[2] * j) * 100

                coords = (55.034645, 38.821565, 200, 0, 0, 0)
                # coords = (xc, yc, zc, rx, ry, rz)
                self.__cam_client.set_pose(coords)

        # Проверяем ответный сигнал
        logger.info(">>> [SEND WAITING COMMAND]")
        self.__cam_client.send_waiting_command()

        logger.info(">>> [WAITING ANSWER]")
        try:
            answer = self.__cam_client.get_data()
        except socket.timeout as timeout_err:
            logger.info(">>> [TIMEOUT ERROR]: {}".format(timeout_err))
            response.content = timeout_err.__class__.__name__
        except socket.error as other_err:
            logger.info(">>> [OTHER ERROR]: {}".format(other_err))
            response.content = other_err.__class__.__name__
        else:
            logger.info(">>> [ANSWER]: {}".format(answer))
            if answer == self.__ok_code:
                response.status = TaskStatus.OK.value
                response.content = dataset_path

        return response


if __name__ == '__main__':
    json_data = {
        'scene': 'oka',
        'title': 'Test sample',
        'sample_count': 10,
        'trajectory_type': 'glissade',
        'd_start': 12,
        'd_finish': 500,
        'h_start': 150,
        'h_finish': 1000,
        'start_x_target': 38,
        'start_y_target': 55,
        'start_z_target': 10,
        'finish_x_target': 38,
        'finish_y_target': 55,
        'finish_z_target': 10,
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
        logger.info(res)
    except socket.error as socket_err:
        logger.info(">>> [SOCKET ERROR]: {}".format(socket_err))
