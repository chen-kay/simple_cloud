import wmi
import win32con # noqa
import platform
import socket

c = wmi.WMI()

# 系统信息
print('操作系统名称' + platform.platform()[:-(len(platform.version()) + 1)])
print('操作系统版本号' + platform.version())
print('操作系统的位数' + platform.architecture()[0])
hostname = socket.getfqdn(socket.gethostname())
ip = socket.gethostbyname(hostname)
print('ip:' + ip)


# CPU信息
def get_CPU():
    cpumsg = []
    for cpu in c.Win32_Processor():
        tmpmsg = {}
        tmpmsg['Name'] = cpu.Name
        cpumsg.append(tmpmsg)

    print(cpumsg)


# 内存信息
def get_PhysicalMemory():

    memorys = []
    for mem in c.Win32_PhysicalMemory():
        tmpmsg = {}
        tmpmsg['Tag'] = mem.Tag
        tmpmsg['ConfiguredClockSpeed'] = str(mem.ConfiguredClockSpeed) + 'MHz'
        memorys.append(tmpmsg)

    print(memorys)


# 显卡信息
def get_video():
    videos = []
    for v in c.Win32_VideoController():
        tmpmsg = {}
        tmpmsg['Caption'] = v.Caption
        tmpmsg['AdapterRAM'] = str(abs(v.AdapterRAM) / (1024**3)) + 'G'
        videos.append(tmpmsg)

    print(videos)


# 网卡mac地址
def get_MacAddress():
    macs = []
    for n in c.Win32_NetworkAdapter():
        mactmp = n.MACAddress
        if mactmp and len(mactmp.strip()) > 5:
            tmpmsg = {}
            tmpmsg['ProductName'] = n.ProductName
            tmpmsg['NetConnectionID'] = n.NetConnectionID
            tmpmsg['MACAddress'] = n.MACAddress
            macs.append(tmpmsg)
    print(macs)


def main():
    get_CPU()
    get_PhysicalMemory()
    get_video()
    get_MacAddress()


if __name__ == '__main__':
    main()
