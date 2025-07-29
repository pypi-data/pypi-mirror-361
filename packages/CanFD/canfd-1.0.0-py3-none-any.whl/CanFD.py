import queue
import threading
import serial.tools.list_ports


class TxMsg:
    def __init__(self):
        self.extend = 0
        self.remote = 0
        self.fd = 0
        self.brs = 0
        self.id = 0
        self.dlc = 0
        self.data = bytearray(64)


class RxMsg:
    def __init__(self):
        self.extend = 0
        self.remote = 0
        self.fd = 0
        self.brs = 0
        self.id = 0
        self.dlc = 0
        self.data = bytearray(64)
        self.timestamp_us = 0


class CanFD:
    MODE_NORMAL = 0
    MODE_LOOPBACK = 1
    MODE_SILENT = 2
    MODE_SILENT_LOOPBACK = 3

    STAND_ISO = 0
    STAND_BOSCH = 1

    RETRANS_DISABLE = 0
    RETRANS_ENABLE = 1

    TERMINAL_DISABLE = 0
    TERMINAL_ENABLE = 1

    __serial = serial.Serial()
    __rx_thread = threading.Thread()
    __rx_queue = queue.Queue()

    __err_code = 0
    __err_rx_count = 0
    __err_tx_count = 0

    def __init__(self):
        self.__err_code = 0
        self.__err_rx_count = 0
        self.__err_tx_count = 0

    def scan(self):
        # scan port
        ports_list = []
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            if "CANDO" in hwid:
                start = hwid.find("SER=")
                end = hwid.find("CANDO")
                ports_list.append(hwid[start + 4 : end])
        return ports_list

    def open(self, dev, mode, stand, retrans, terminal, can_timing, data_timing):
        # scan port
        port_name = ""
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            if dev in hwid:
                port_name = port
        if port_name == "":
            return -1  # not found

        # open port
        try:
            self.__serial = serial.Serial(port_name, 5000000)
        except Exception as e:
            return -2  # open error

        # start can-fd
        data = bytearray()
        data += b"\xf0"
        data += (mode << 4 | stand << 3 | retrans << 2 | terminal).to_bytes()
        data += can_timing[0].to_bytes(2, "little")[0].to_bytes()
        data += can_timing[0].to_bytes(2, "little")[1].to_bytes()
        data += can_timing[1].to_bytes()
        data += can_timing[2].to_bytes()
        data += can_timing[3].to_bytes()
        data += data_timing[0].to_bytes(2, "little")[0].to_bytes()
        data += data_timing[0].to_bytes(2, "little")[1].to_bytes()
        data += data_timing[1].to_bytes()
        data += data_timing[2].to_bytes()
        data += data_timing[3].to_bytes()
        data += b"\xaa"
        self.__serial.write(data)
        self.__serial.flush()

        self.__rx_thread = threading.Thread(target=self.__rx_loop)
        self.__rx_thread.start()
        return 0

    def close(self):
        if self.__serial.is_open:
            try:
                data = bytearray()
                data += b"\x81"
                data += b"\xcc"
                data += b"\xaa"
                self.__serial.write(data)
                self.__serial.flush()
                self.__serial.close()
                self.__rx_thread.join()
            except Exception as e:
                return

    def write(self, tx_msg):
        if not self.__serial.is_open:
            return -1  # open error

        data = bytearray()
        data += b"\x82"
        flag = tx_msg.extend << 31 | tx_msg.remote << 30 | tx_msg.id
        data += flag.to_bytes(4, "little")[0].to_bytes()
        data += flag.to_bytes(4, "little")[1].to_bytes()
        data += flag.to_bytes(4, "little")[2].to_bytes()
        data += flag.to_bytes(4, "little")[3].to_bytes()
        data += b"\x00"
        data += b"\x00"
        data += (tx_msg.fd << 1 | tx_msg.brs).to_bytes()
        data += tx_msg.dlc.to_bytes()
        data += tx_msg.data[0 : self.dlc_2_len(tx_msg.dlc)]
        data += b"\xaa"
        self.__serial.write(data)
        return 0

    def flush(self):
        if not self.__serial.is_open:
            return -1  # open error
        self.__serial.flush()

    def in_waiting(self):
        return self.__rx_queue.qsize()

    def read(self):
        return self.__rx_queue.get_nowait()

    def status(self):
        return self.__err_code, self.__err_rx_count, self.__err_tx_count

    @staticmethod
    def dlc_2_len(dlc):
        DLC_TO_LEN_TABLE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]
        return DLC_TO_LEN_TABLE[dlc]

    def __rx_loop(self):
        rx_pack = bytearray()
        rx_pack.clear()

        while self.__serial.is_open:
            try:
                data = self.__serial.read_until(b"\xaa")
                rx_pack += data
                self.__parse_pack(rx_pack)
            except Exception as e:
                self.__serial.close()

    def __parse_pack(self, data):
        size = len(data)
        match data[0]:
            case 0x02:  # REG_CAN_MSG
                if size < 10:
                    return False
                data_size = self.dlc_2_len(data[8])
                pack_size = 10 + data_size
                if size < pack_size:
                    return False
                elif size > pack_size:
                    data.clear()
                    return False

                rx_msg = RxMsg()
                flag = int.from_bytes(data[1 : 1 + 4], "little")
                if flag & (1 << 31):
                    rx_msg.extend = 1
                else:
                    rx_msg.extend = 0
                if flag & (1 << 30):
                    rx_msg.remote = 1
                else:
                    rx_msg.remote = 0
                rx_msg.id = flag & 0x1FFFFFFF
                flag = int.from_bytes(data[5 : 5 + 2], "little")
                rx_msg.timestamp_us = flag
                if data[7] & (1 << 1):
                    rx_msg.fd = 1
                else:
                    rx_msg.fd = 0
                if data[7] & (1 << 0):
                    rx_msg.brs = 1
                else:
                    rx_msg.brs = 0
                rx_msg.dlc = data[8]
                rx_msg.data[0 : self.dlc_2_len(rx_msg.dlc)] = data[
                    9 : 9 + self.dlc_2_len(rx_msg.dlc)
                ]
                self.__rx_queue.put(rx_msg)

                data.clear()
                return True

            case 0x03:  # REG_STATUS
                if size < 5:
                    return False
                elif size > 5:
                    data.clear()
                    return False

                self.__err_code = data[1]
                self.__err_rx_count = data[2]
                self.__err_tx_count = data[3]

                data.clear()
                return True

            case _:
                data.clear()
                return False
