import socket
import struct
import sys
import os

OP_RRQ = 1
OP_WRQ = 2
OP_DATA = 3
OP_ACK = 4
OP_ERROR = 5

DEFAULT_PORT = 69
DATA_SIZE = 512
MAX_PACKET_SIZE = DATA_SIZE + 4


def tftp_client(host, command, filename, port=DEFAULT_PORT):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(5.0)
        server_address = (host, port)

        print(f"TFTP 서버 {host}:{port} 에 연결 시도 중...")

    except socket.gaierror:
        print(f"오류: 호스트 '{host}'의 주소를 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"소켓 초기화 중 오류 발생: {e}")
        return

    if command.lower() == 'get':
        print(f"파일 '{filename}' 다운로드 요청 (octet 모드)...")
        download_file(client_socket, server_address, filename)

    elif command.lower() == 'put':
        print(f"파일 '{filename}' 업로드 요청 기능은 아직 구현되지 않았습니다.")

    else:
        print(f"오류: 알 수 없는 명령 '{command}'. 'get' 또는 'put'을 사용하세요.")

    client_socket.close()
    print("TFTP 클라이언트 종료.")


def download_file(client_socket, server_address, filename):
    mode = 'octet'
    packet = struct.pack('!h', OP_RRQ) + \
             filename.encode('ascii') + b'\x00' + \
             mode.encode('ascii') + b'\x00'

    try:
        client_socket.sendto(packet, server_address)
        response, new_server_address = client_socket.recvfrom(MAX_PACKET_SIZE)
        server_address = new_server_address

    except socket.timeout:
        print("오류: 서버로부터 초기 응답이 없습니다 (타임아웃).")
        return
    except Exception as e:
        print(f"통신 오류 발생: {e}")
        return

    block_num = 1
    total_bytes = 0

    try:
        with open(filename, 'wb') as f:
            while True:
                opcode, current_block = struct.unpack('!hh', response[:4])
                data = response[4:]

                if opcode == OP_ERROR:
                    error_code = current_block
                    error_msg = data.decode('ascii', errors='ignore').split('\x00')[0]
                    print(f"\n[SERVER ERROR] 코드: {error_code}, 메시지: {error_msg}")
                    if 'File not found' in error_msg:
                        print("다운로드 실패: 요청하신 파일을 서버에서 찾을 수 없습니다.")
                    return

                elif opcode == OP_DATA:
                    if current_block == block_num:
                        f.write(data)
                        total_bytes += len(data)

                        ack_packet = struct.pack('!hh', OP_ACK, block_num)
                        client_socket.sendto(ack_packet, server_address)

                        print(f"\r수신 중... 블록: {block_num}, 크기: {total_bytes} bytes", end="")

                        if len(data) < DATA_SIZE:
                            print(f"\n다운로드 완료: 총 {total_bytes} bytes 수신.")
                            break

                        block_num += 1

                        response, _ = client_socket.recvfrom(MAX_PACKET_SIZE)

                    else:
                        print(f"\n경고: 블록 번호 불일치. 예상: {block_num}, 수신: {current_block}")
                        pass
                else:
                    print(f"\n예상치 못한 Opcode 수신: {opcode}")
                    return

    except socket.timeout:
        print("\n오류: 서버로부터 다음 DATA 패킷을 받지 못했습니다 (타임아웃).")
    except IOError:
        print(f"\n오류: 파일을 로컬에 저장하는 데 실패했습니다: {filename}")
    except Exception as e:
        print(f"\n알 수 없는 오류 발생: {e}")


def main():
    if len(sys.argv) < 4:
        print("사용법: mytftp host [-p port] [get|put] filename")
        print("예시: $ mytftp 203.250.133.88 get tftp.conf")
        print("예시: $ mytftp genie.pcu.ac.kr –p 9988 put tftp.txt")
        return

    host = sys.argv[1]
    port = DEFAULT_PORT
    command = None
    filename = None

    try:
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '-p':
                port = int(sys.argv[i + 1])
                i += 2
            elif command is None:
                command = sys.argv[i]
                i += 1
            elif filename is None:
                filename = sys.argv[i]
                i += 1
            else:
                i += 1
    except (ValueError, IndexError):
        print("오류: 포트(-p) 옵션의 값이 올바르지 않거나 누락되었습니다.")
        return

    if command is None or filename is None:
        print("오류: 명령(get/put)과 파일 이름이 지정되지 않았습니다.")
        return

    tftp_client(host, command, filename, port)


if __name__ == "__main__":
    main()