#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["voyageai", "numpy", "rich"]
# ///
# this_file: voyemb.py

import voyageai
import base64
import numpy as np
import struct
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# Set wider console for full-width display
console = Console(width=200)


def int_list_to_binary_visual(int_list, bits_per_int=8):
    """
    Convert a list of integers to a visual binary string where 0 = '.'
    and 1 = '#'
    """
    binary_str = ""
    for num in int_list:
        # Convert to binary with specified bit width, remove '0b' prefix
        binary_repr = format(num, f"0{bits_per_int}b")
        # Replace 0 with '.' and 1 with '#'
        visual_binary = binary_repr.replace("0", ".").replace("1", "#")
        binary_str += visual_binary
    return binary_str


def int_list_to_base64(int_list):
    """
    Convert a list of integers to URL-safe Base64 representation.
    Extracts the first bit of the first 8 bytes, packs them into an appended
    byte to achieve exactly 44 Base64 characters (33 bytes = 264 bits).
    """
    # Extract the first bit of each of the first 8 bytes
    first_bits = []
    for i in range(min(8, len(int_list))):
        # Get the most significant bit (first bit) of each byte
        first_bit = (int_list[i] >> 7) & 1
        first_bits.append(first_bit)

    # Pad with zeros if we have less than 8 bytes
    while len(first_bits) < 8:
        first_bits.append(0)

    # Pack the 8 first bits into a single byte
    packed_byte = 0
    for i, bit in enumerate(first_bits):
        packed_byte |= bit << (7 - i)

    # Append the packed byte to the original embedding
    enhanced_data = int_list + [packed_byte]

    # Convert to bytes and encode
    byte_data = bytes(enhanced_data)
    # Encode to URL-safe Base64 and decode to string
    base64_result = base64.urlsafe_b64encode(byte_data).decode("ascii")
    # Remove padding for cleaner URLs (should be exactly 44 chars now)
    base64_result = base64_result.rstrip("=")
    return base64_result


def simhash_bits(int_list, planes=64):
    """SimHash: Project onto random hyperplanes, store sign bits"""
    rng = np.random.default_rng(42)
    rand_vectors = rng.normal(size=(planes, len(int_list)))
    # Convert bytes→{-1,1}
    vec = np.array(int_list, dtype=float)
    vec = (vec - 128) / 128  # roughly centre
    dots = rand_vectors @ vec
    bits = (dots > 0).astype(int)
    return bits


def simhash_slug(int_list, planes=64):
    """64-bit SimHash → 11-char URL slug"""
    bits = simhash_bits(int_list, planes)
    # Pack into 8-byte integer
    h = 0
    for b in bits:
        h = (h << 1) | int(b)
    slug = base64.urlsafe_b64encode(struct.pack(">Q", h)).decode().rstrip("=")
    return slug


def gray_coded_hex(int_list):
    """Gray-coded nibble stream → hex string"""
    # Gray code lookup for 4-bit values (0-15)
    gray_codes = [0, 1, 3, 2, 6, 7, 5, 4, 12, 13, 15, 14, 10, 11, 9, 8]

    hex_result = ""
    for byte_val in int_list:
        # Split byte into two nibbles
        high_nibble = (byte_val >> 4) & 0xF
        low_nibble = byte_val & 0xF
        # Convert to Gray code and format as hex
        gray_high = gray_codes[high_nibble]
        gray_low = gray_codes[low_nibble]
        hex_result += f"{gray_high:x}{gray_low:x}"
    return hex_result


def top_k_indices(int_list, k=8):
    """Top-k index signature: indices of highest magnitude values"""
    # Get indices sorted by magnitude (descending)
    indices = np.argsort(np.array(int_list))[-k:]
    indices = sorted(indices.tolist())  # Convert to list then sort ascending
    # Format as dash-separated hex
    return "-".join(f"{idx:02x}" for idx in indices)


def run_length_encode_binary(int_list):
    """Run-length encode the .# binary pattern"""
    binary_str = int_list_to_binary_visual(int_list, bits_per_int=8)

    if not binary_str:
        return ""

    result = ""
    current_char = binary_str[0]
    count = 1

    for char in binary_str[1:]:
        if char == current_char:
            count += 1
        else:
            result += f"{count}{current_char}"
            current_char = char
            count = 1

    result += f"{count}{current_char}"  # Add the last run
    return result


def emoji_quaternions(int_list):
    """Map 2-bit pairs to emoji quaternions"""
    emojis = ["⚪", "🟡", "🟠", "🔴"]  # 00, 01, 10, 11

    result = ""
    for byte_val in int_list:
        # Extract 4 pairs of 2 bits from each byte
        for shift in [6, 4, 2, 0]:
            two_bits = (byte_val >> shift) & 0b11
            result += emojis[two_bits]
    return result


def z_order_hash(int_list):
    """Simplified Z-order (Morton code) encoding"""
    # Quantize each byte to 2 bits (0-3), then interleave
    quantized = [(b >> 6) & 0b11 for b in int_list]  # Take top 2 bits

    # Simple bit interleaving for first 16 bytes (32 bits total)
    result = 0
    for i, val in enumerate(quantized[:16]):
        # Interleave the 2 bits
        for bit_pos in range(2):
            bit = (val >> bit_pos) & 1
            result |= bit << (i * 2 + bit_pos)

    # Convert to Base64
    packed = struct.pack(">I", result)
    return base64.urlsafe_b64encode(packed).decode().rstrip("=")


# q64: Positional-alphabet codec for prefix-search-friendly encoding
ALPHABETS = [
    "ABCDEFGHIJKLMNOP",  # pos ≡ 0 (mod 4)
    "QRSTUVWXYZabcdef",  # pos ≡ 1
    "ghijklmnopqrstuv",  # pos ≡ 2
    "wxyz0123456789-_",  # pos ≡ 3
]

# Pre-compute reverse lookup tables for O(1) decode
REV_LOOKUP = {}
for idx, pos_set in enumerate(ALPHABETS):
    for c in pos_set:
        REV_LOOKUP[c] = (idx, pos_set.index(c))


def q64_encode(byte_seq):
    """
    Encode bytes into q64 positional alphabet.
    Each 8-bit byte → 2 chars. Result length = 2⋅len(byte_seq).
    Eliminates "abc matches everywhere" substring pollution.
    """
    if isinstance(byte_seq, list):
        byte_seq = bytes(byte_seq)

    out = []
    pos = 0
    for byte in byte_seq:
        hi, lo = byte >> 4, byte & 0xF  # two 4-bit nibbles
        for nibble in (hi, lo):
            alphabet = ALPHABETS[pos & 3]  # pos mod 4
            out.append(alphabet[nibble])
            pos += 1
    return "".join(out)


def q64_decode(s):
    """
    Inverse of q64_encode. Raises ValueError on malformed input.
    """
    if len(s) & 1:
        raise ValueError("q64 length must be even (2 chars per byte).")

    nibbles = []
    for pos, ch in enumerate(s):
        try:
            expected_alpha, val = REV_LOOKUP[ch]
        except KeyError:
            raise ValueError(f"Invalid q64 character {ch!r}") from None
        if expected_alpha != (pos & 3):
            raise ValueError(f"Character {ch!r} illegal at position {pos}")
        nibbles.append(val)

    # Stitch nibbles back into bytes
    it = iter(nibbles)
    return bytes((hi << 4) | lo for hi, lo in zip(it, it))


def simhash_q64(int_list, planes=64):
    """64-bit SimHash → 16-char q64 position-safe slug"""
    bits = simhash_bits(int_list, planes)

    # Pack bits into bytes (8 bits per byte)
    byte_data = []
    for i in range(0, len(bits), 8):
        byte_val = 0
        for j in range(8):
            if i + j < len(bits):
                byte_val |= int(bits[i + j]) << (7 - j)
        byte_data.append(byte_val)

    # Encode using q64
    return q64_encode(bytes(byte_data))


def top_k_q64(int_list, k=8):
    """Top-k indices → q64 position-safe encoding"""
    # Get indices sorted by magnitude (descending)
    indices = np.argsort(np.array(int_list))[-k:]
    indices = sorted(indices.tolist())  # Convert to list then sort ascending

    # Convert indices to bytes and encode with q64
    return q64_encode(bytes(indices))


def z_order_q64(int_list):
    """Z-order (Morton code) → q64 position-safe encoding"""
    # Quantize each byte to 2 bits (0-3), then interleave
    quantized = [(b >> 6) & 0b11 for b in int_list]  # Take top 2 bits

    # Simple bit interleaving for first 16 bytes (32 bits total)
    result = 0
    for i, val in enumerate(quantized[:16]):
        # Interleave the 2 bits
        for bit_pos in range(2):
            bit = (val >> bit_pos) & 1
            result |= bit << (i * 2 + bit_pos)

    # Convert to bytes and encode with q64
    packed = struct.pack(">I", result)
    return q64_encode(packed)


def eq64_encode(byte_seq):
    """
    Encode bytes into Eq64 format with dots every 8 characters.
    Each 8-bit byte → 2 chars. Dots inserted every 8 chars for readability.
    """
    # Get the base q64 encoding
    base_encoded = q64_encode(byte_seq)

    # Insert dots every 8 characters
    result = []
    for i, char in enumerate(base_encoded):
        if i > 0 and i % 8 == 0:
            result.append(".")
        result.append(char)

    return "".join(result)


def eq64_decode(s):
    """
    Decode Eq64 format by removing dots and using standard q64 decode.
    """
    # Remove all dots
    clean_s = s.replace(".", "")
    # Use standard q64 decode
    return q64_decode(clean_s)


vo = voyageai.Client()

examples = [
    (
        "FontLab 8 is an integrated font editor for Mac and Windows that "
        "helps you create fonts from start to finish, from a simple design "
        "to a complex project, and brings a spark of magic into type design."
    ),
    (
        "FontLab 8 is a Mac and Windows font editor that helps you create "
        "fonts of any complexity, from start to finish."
    ),
    (
        "FontLab 8 to zintegrowany edytor fontów dla Mac i Windows, który "
        "pomaga tworzyć fonty od początku do końca, od prostego projektu po "
        "złożone przedsięwzięcie, i wnosi iskrę magii w projektowanie krojów "
        "pisma."
    ),
    ("Warsaw is the capital of Poland."),
]

# Generate voyage-3-large vectors, which by default are 1024-dimensional
# floating-point numbers
embd1 = vo.embed(
    examples,
    model="voyage-3.5-lite",
    input_type="document",
    truncation=True,
    output_dimension=256,
    output_dtype="ubinary",
).embeddings

console.print("\n[bold blue]🔬 Q64 FAMILY ENCODING DEMONSTRATIONS[/bold blue]")
console.rule("[blue]Position-Safe Encoding Analysis[/blue]")

# Create main results table for q64 methods only with full width
results_table = Table(
    "Text",
    "Eq64 (Full Embedding)",
    "Shq64 (SimHash)",
    "T8q64 (Top-8)",
    "Zoq64 (Z-order)",
    title="🧬 Q64 Family Encoding Results",
    show_header=True,
    header_style="bold magenta",
    expand=True,  # Expand to full width
    min_width=180,  # Minimum width to ensure no truncation
)

for i, embedding in enumerate(embd1):
    # Convert embedding to list for processing
    emb_list = list(embedding)  # type: ignore

    # Calculate all q64 encodings
    eq64 = eq64_encode(emb_list)  # Full embedding with dots
    shq64 = simhash_q64(emb_list)  # SimHash
    t8q64 = top_k_q64(emb_list)  # Top-8
    zoq64 = z_order_q64(emb_list)  # Z-order

    results_table.add_row(
        f"[cyan]Text {i + 1}[/cyan]",
        f"[green]{eq64}[/green]",
        f"[yellow]{shq64}[/yellow]",
        f"[magenta]{t8q64}[/magenta]",
        f"[blue]{zoq64}[/blue]",
    )

console.print(results_table)

console.print("\n[bold green]🎯 LOCALITY PRESERVATION ANALYSIS[/bold green]")
console.rule("[green]Similar texts should have similar codes![/green]")

# Locality comparison table focusing on first two texts with full width
locality_table = Table(
    "Method",
    "Text 1",
    "Text 2",
    "Similarity Notes",
    title="🔍 Q64 Family Locality Preservation",
    show_header=True,
    header_style="bold red",
    expand=True,  # Expand to full width
    min_width=180,  # Minimum width to ensure no truncation
)

emb1_list = list(embd1[0])  # type: ignore
emb2_list = list(embd1[1])  # type: ignore

# Q64 family methods
locality_table.add_row(
    "[green]Eq64[/green]",
    f"[green]{eq64_encode(emb1_list)}[/green]",
    f"[green]{eq64_encode(emb2_list)}[/green]",
    "Full precision preservation",
)
locality_table.add_row(
    "[yellow]Shq64[/yellow]",
    f"[yellow]{simhash_q64(emb1_list)}[/yellow]",
    f"[yellow]{simhash_q64(emb2_list)}[/yellow]",
    "Semantic similarity hashing",
)
locality_table.add_row(
    "[magenta]T8q64[/magenta]",
    f"[magenta]{top_k_q64(emb1_list)}[/magenta]",
    f"[magenta]{top_k_q64(emb2_list)}[/magenta]",
    "Top feature preservation",
)
locality_table.add_row(
    "[blue]Zoq64[/blue]",
    f"[blue]{z_order_q64(emb1_list)}[/blue]",
    f"[blue]{z_order_q64(emb2_list)}[/blue]",
    "Spatial locality encoding",
)

console.print(locality_table)

console.print("\n[bold purple]🔄 ROUND-TRIP VERIFICATION[/bold purple]")
console.rule("[purple]Data Integrity Check[/purple]")

# Round-trip verification table
verification_table = Table(
    "Text",
    "Original Length",
    "Eq64 Length",
    "Status",
    "Details",
    title="✅ Q64 Round-Trip Verification Results",
    show_header=True,
    header_style="bold purple",
)

for i, embedding in enumerate(embd1[:2]):  # Test first 2
    emb_list = list(embedding)  # type: ignore
    encoded = eq64_encode(emb_list)
    decoded = list(eq64_decode(encoded))
    match = decoded == emb_list

    verification_table.add_row(
        f"[cyan]Text {i + 1}[/cyan]",
        f"{len(emb_list)}",
        f"{len(encoded)}",
        "[green]✅ PASS[/green]" if match else "[red]❌ FAIL[/red]",
        "Perfect round-trip" if match else "Data corruption detected",
    )

console.print(verification_table)

console.print("\n[bold white]📋 Q64 METHOD COMPARISON[/bold white]")
console.rule("[white]Method Overview[/white]")

# Summary comparison table for q64 methods only
summary_table = Table(
    "Method",
    "Length",
    "Best For",
    "Key Advantage",
    "Performance",
    title="🏆 Q64 Family Method Comparison",
    show_header=True,
    header_style="bold white",
)

methods_data = [
    (
        "Eq64",
        "64",
        "Full precision",
        "Complete data preservation",
        "🟡 Medium",
    ),
    (
        "Shq64",
        "16",
        "Similarity search",
        "Semantic locality hashing",
        "🟢 High",
    ),
    (
        "T8q64",
        "16",
        "Feature analysis",
        "Top feature preservation",
        "🟢 High",
    ),
    (
        "Zoq64",
        "8",
        "Spatial queries",
        "Morton code locality",
        "🟢 High",
    ),
]

for method, length, best_for, advantage, performance in methods_data:
    summary_table.add_row(
        f"[yellow]{method}[/yellow]",
        f"[cyan]{length}[/cyan]",
        f"[green]{best_for}[/green]",
        f"[magenta]{advantage}[/magenta]",
        performance,
    )

console.print(summary_table)

rprint("\n[bold blue]🎨 Q64 Family Key Insights:[/bold blue]")
rprint(
    "• [green]Position-safe encoding[/green] eliminates substring "
    "pollution in search systems"
)
rprint(
    "• [green]Eq64 dot notation[/green] provides visual structure "
    "every 8 characters for readability"
)
rprint(
    "• [yellow]Hierarchical structure[/yellow] follows UPPER→lower→mixed→digit pattern"
)
rprint(
    "• [red]Locality preservation[/red] enables efficient similarity search operations"
)
rprint(
    "• [purple]Round-trip verification[/purple] ensures perfect data "
    "integrity with dot handling"
)
rprint(
    "• [magenta]Variable compression[/magenta] from 8 to 71 characters "
    "based on use case"
)
