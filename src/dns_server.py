import uasyncio as asyncio
import usocket as socket
import gc

class DNSServer:
    """
    A minimal DNS server for Captive Portal usage.
    It resolves ALL DNS queries to the specified local IP address (DNS Hijacking).
    """
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self._running = False
        self._task = None

    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._run())
            print(f"DNSServer: Started (Redirecting to {self.ip_address})")

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
        print("DNSServer: Stopped")

    async def _run(self):
        # Create UDP socket bound to port 53
        udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udps.setblocking(False)
        
        try:
            udps.bind(('0.0.0.0', 53))
        except Exception as e:
            print(f"DNSServer: Failed to bind port 53: {e}")
            return

        while self._running:
            try:
                # Use polling for UDP in MicroPython asyncio
                # (create_datagram_endpoint is not fully standard in all ports)
                data, addr = None, None
                try:
                    data, addr = udps.recvfrom(1024)
                except OSError:
                    # No data available
                    pass

                if data and addr:
                    response = self._make_response(data)
                    udps.sendto(response, addr)
                
                await asyncio.sleep_ms(100) # Yield
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"DNSServer: Error handling request: {e}")
                await asyncio.sleep(1)

        udps.close()

    def _make_response(self, request):
        """
        Constructs a simple DNS A-record response pointing to self.ip_address
        """
        try:
            # Extract Transaction ID (first 2 bytes)
            tid = request[0:2]
            
            # Flags: Standard query response, No error
            # 0x8180: Response (1), Opcode Query (0000), AA(0), TC(0), RD(1), RA(1), Z(0), RCODE(0)
            flags = b'\x81\x80'
            
            # Questions count (copy from request, usually 1)
            qdcount = request[4:6]
            
            # Answer count (1)
            ancount = b'\x00\x01'
            
            # NS and AR counts (0)
            nscount = b'\x00\x00'
            arcount = b'\x00\x00'
            
            # The Question Section (copy directly from request)
            # Find the end of the domain name string (null byte)
            # Header is 12 bytes. Question starts at index 12.
            # Domain name format: [len]label[len]label...[0]
            # Then Type (2 bytes) and Class (2 bytes)
            
            # Simplification: Just copy the body of the request as the question section
            # assuming the request is well-formed.
            # We need to find where the question ends to append answer.
            
            packet = tid + flags + qdcount + ancount + nscount + arcount
            
            # Provide the pointer to the domain name in the question section (0xc00c)
            # 0xc0 = 11000000 (compression pointer), 0x0c = 12 (offset to start of header body)
            # This says "The answer is for the name at offset 12"
            dns_answer_name_ptr = b'\xc0\x0c'
            
            # Type A (Host Address) = 1
            dns_answer_type = b'\x00\x01'
            
            # Class IN (Internet) = 1
            dns_answer_class = b'\x00\x01'
            
            # TTL (Time to Live) - 60 seconds
            dns_answer_ttl = b'\x00\x00\x00\x3c'
            
            # Data Length (IPv4 = 4 bytes)
            dns_answer_len = b'\x00\x04'
            
            # IP Address converted to bytes
            ip_parts = [int(x) for x in self.ip_address.split('.')]
            dns_answer_data = bytes(ip_parts)
            
            # Reconstruct the response: Header + Question(from req) + Answer
            # We need the original question block.
            # Header is 12 bytes.
            payload = request[12:]
            
            return packet + payload + dns_answer_name_ptr + dns_answer_type + dns_answer_class + dns_answer_ttl + dns_answer_len + dns_answer_data
            
        except Exception as e:
            print(f"DNSServer: Error constructing response: {e}")
            return b''
