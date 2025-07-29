import socket


def check_port(host, port) -> tuple[bool, str]:
    """
    检查指定主机的指定端口是否开放。
    :param host: 主机名或IP地址。
    :param port: 端口号。
    :return: 一个元组，第一个元素为True表示开放，False表示不开放，第二个元素为错误信息或None。
    """
    try:
        # 创建一个 TCP 套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置超时时间
        sock.settimeout(2)
        # 尝试连接到指定的主机和端口
        result = sock.connect_ex((host, port))
        if result == 0:
            return True, None
        else:
            return False, "端口不开放或网络不通"

    except socket.gaierror as e:
        return False, e
    except socket.error as e:
        return False, e
    finally:
        # 关闭套接字
        sock.close()


def get_local_ip(isIpv6: bool = False):
    """
    获取本机 IP 地址
    return: str
        本机 IP  地址
    """
    try:
        # 创建一个UDP套接字
        sock = socket.socket(socket.AF_INET6 if isIpv6 else socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到一个公共的IP地址和端口，
        # 这不会发送任何数据，但是会为套接字分配一个本地地址
        sock.connect(("2001:4860:4860::8888" if isIpv6 else "8.8.8.8", 80))
        # 获取分配给套接字的本地IP地址
        local_ip = sock.getsockname()[0]
    finally:
        # 关闭套接字
        sock.close()
    return local_ip
