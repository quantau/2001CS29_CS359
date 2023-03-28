import scapy.all as scapy
import socket

x = 0

def get_ip_address(hostname):
    return socket.gethostbyname(hostname)


def tcp_3_way_handshake_start(ip_address, interface):
    filter = "tcp and host " + ip_address
    capture = scapy.sniff(iface=interface, store=True, filter=filter, count=3)
    print(capture.summary())
    filename = "TCP_3_Way_Handshake_Start_2001CS29.pcap"
    scapy.wrpcap(filename, capture, append=False)


def process_tcp_handshake_close(packet):
    global x
    if(packet[scapy.TCP].flags==0x011 or x<3):
        x-=1
        if(x==0):
            return True
        return False

def tcp_handshake_close(ip_address, interface):
    filter = "tcp and host " + ip_address
    capture=scapy.sniff(iface=interface, store=True, filter=filter, stop_filter=process_tcp_handshake_close)
    print(capture.summary())
    filename="TCP_Handshake_Close_2001CS29.pcap"
    scapy.wrpcap(filename, capture, append=False)

def process_dns_request_response(packet):
    global x
    filename="DNS_Request_Response_2001CS29.pcap"
    if(x<2 and packet.haslayer(scapy.DNSQR) and packet[scapy.DNSQR].qtype==1 and ("codeforces" in str(packet[scapy.DNSQR].qname))): 
        print(packet)
        scapy.wrpcap(filename, packet, append=True)
        x=x+1

def dns_request_response(interface):
    filter = "port 53"
    scapy.sniff(iface=interface, store=False, filter=filter, count=20, prn=process_dns_request_response)    

def ping_request_response(ip_address, interface):
    filter = "icmp and host " + ip_address
    capture = scapy.sniff(
        iface=interface,
        store=True,
        filter=filter,
        count=2,
    )
    print(capture.summary())
    filename = "PING_Request_Response_2001CS29.pcap"
    scapy.wrpcap(filename, capture, append=False)


def process_arp(packet):
    global x
    filename = "ARP_2001CS29.pcap"
    if x == 0 and packet.haslayer(scapy.ARP) and packet[scapy.ARP].op == 1:
        print(packet)
        scapy.wrpcap(filename, packet, append=True)
        x = 1
    if x == 1 and packet.haslayer(scapy.ARP) and packet[scapy.ARP].op == 2:
        print(packet)
        scapy.wrpcap(filename, packet, append=True)
        x = 2
    if x == 2:
        return True
    return False


def arp(interface):
    filter = "arp"
    scapy.sniff(iface=interface, store=False, filter=filter, stop_filter=process_arp)

def process_ftp_connection_start(packet):
    print(packet)
    filename = "FTP_Connection_Start_2001CS29.pcap"
    scapy.wrpcap(filename, packet, append=True)


def ftp_connection_start(interface):
    filter = "port 21"
    scapy.sniff(
        iface=interface,
        store=False,
        filter=filter,
        count=9,
        prn=process_ftp_connection_start,
    )


def process_ftp_connection_close(packet):
    global x
    if packet[scapy.TCP].flags.F:
        print(packet)
        filename = "FTP_Connection_Close_2001CS29.pcap"
        scapy.wrpcap(filename, packet, append=True)
        x -= 1


def ftp_connection_close(interface):
    global x
    filter = "port 21"
    while x:
        scapy.sniff(
            iface=interface,
            store=False,
            filter=filter,
            count=1,
            prn=process_ftp_connection_close,
        )



def main():
    hostname = "codeforces.com"
    interface = "Wi-Fi"
    ip_address = get_ip_address(hostname)
    print(ip_address)
    global x
    # tcp_3_way_handshake_start(ip_address, interface)
    x=3
    tcp_handshake_close(ip_address, interface)
    # arp()
    # dns_request_response(interface)
    # ping_request_response(ip_address, interface)
    interface = "\\Device\\NPF_Loopback"
    # ftp_connection_start(interface)
    x = 1
    # ftp_connection_close(interface)

if __name__ == "__main__":
    main()
