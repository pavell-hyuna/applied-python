import socket
import argparse

class TaskQueueServer:

    def __init__(self, ip, port, path, timeout):
        self._ip = ip
        self._port = port
        self._path = path
        self._timeout = timeout
        self._queues = {}
        self._last_id = 1

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
            conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            conn.bind((self._ip, self._port))
            conn.listen()

            while True:
                current_connection, addr = conn.accept()
                received = current_connection.recv(10000)
                data = received.decode('utf-8').split(' ')

                if data:
                    if data[0] == 'ADD':
                        queue_name, length, str_data = (data[1], data[2], data[3])
                        queue_id = self._last_id
                        queue = {
                            'length': length,
                            'data': str_data,
                            'id': queue_id,
                            'confirmed': False
                        }
                        self._last_id += 1
                        if queue_name not in self._queues:
                            self._queues[queue_name] = {
                                'last_queue': 0,
                                'jobs': []
                            }
                        self._queues[queue_name]['jobs'].append(queue)
                        current_connection.send(b'%d' % queue_id)
                    elif data[0] == 'GET':
                        queue_name = data[1]
                        if queue_name not in self._queues:
                            return b'NONE'
                        queue = self._queues[queue_name]['jobs'][self._queues[queue_name]['last_queue']]
                        current_connection.send(('%s %s %s' % (queue['id'], queue['length'], queue['data']))
                                                .encode('utf-8'))
                        self._queues[queue_name]['last_queue'] += 1
                    elif data[0] == 'ACK':
                        queue_name, queue_id = data[1], int(data[2])
                        if queue_name in self._queues:
                            for key, item in enumerate(self._queues[queue_name]['jobs']):
                                if item['id'] == queue_id:
                                   if not item['confirmed']:
                                       self._queues[queue_name]['jobs'][key]['confirmed'] = True
                                       current_connection.send('YES'.encode('utf-8'))
                                   else:
                                       current_connection.send('NO'.encode('utf-8'))
                        else:
                            current_connection.send('NO'.encode('utf-8'))
                    elif data[0] == 'IN':
                        queue_name, queue_id = data[1], int(data[2])
                        in_queue = 'NO'
                        if queue_name in self._queues:
                            for item in self._queues[queue_name]['jobs']:
                                if item['id'] == queue_id:
                                    if not item['confirmed']:
                                        in_queue = 'YES'
                            current_connection.send(in_queue.encode('utf-8'))
                        else:
                            current_connection.send('NO'.encode('utf-8'))
                    elif data[0] == 'SAVE':
                        current_connection.send('OK'.encode('utf-8'))
                    else:
                        current_connection.send('ERROR'.encode('utf-8'))


def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=5555,
        help='Server port')
    parser.add_argument(
        '-i',
        action="store",
        dest="ip",
        type=str,
        default='127.0.0.1',
        help='Server ip adress')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./',
        help='Server checkpoints dir')
    parser.add_argument(
        '-t',
        action="store",
        dest="timeout",
        type=int,
        default=300,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
