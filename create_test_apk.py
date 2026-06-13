"""
Builds a minimal-but-valid test APK (test_malicious.apk) with:
  - AndroidManifest.xml (hand-encoded binary AXML) declaring:
      package = com.sbi.update.security
      application label = "SBI Bank Update"
      permissions: READ_SMS, RECEIVE_SMS, SEND_SMS, BIND_ACCESSIBILITY_SERVICE,
                    SYSTEM_ALERT_WINDOW, REQUEST_INSTALL_PACKAGES, RECEIVE_BOOT_COMPLETED
  - classes.dex (hand-built minimal DEX) whose string pool contains
      "http://malicious-update.top/api/steal"

This is for local testing of the /analyze pipeline only.
"""

import hashlib
import struct
import zipfile
import zlib

U16 = lambda v: struct.pack("<H", v)
U32 = lambda v: struct.pack("<I", v)
U8 = lambda v: struct.pack("<B", v)


# ---------------------------------------------------------------------------
# AXML (binary AndroidManifest.xml) builder
# ---------------------------------------------------------------------------

RES_STRING_POOL_TYPE = 0x0001
RES_XML_TYPE = 0x0003
RES_XML_START_NAMESPACE_TYPE = 0x0100
RES_XML_END_NAMESPACE_TYPE = 0x0101
RES_XML_START_ELEMENT_TYPE = 0x0102
RES_XML_END_ELEMENT_TYPE = 0x0103
RES_XML_RESOURCE_MAP_TYPE = 0x0180

TYPE_STRING = 0x03

ANDROID_NS = "http://schemas.android.com/apk/res/android"

ATTR_NAME_RESID = 0x01010003   # android:name
ATTR_LABEL_RESID = 0x01010001  # android:label

PERMISSIONS = [
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.SEND_SMS",
    "android.permission.BIND_ACCESSIBILITY_SERVICE",
    "android.permission.SYSTEM_ALERT_WINDOW",
    "android.permission.REQUEST_INSTALL_PACKAGES",
    "android.permission.RECEIVE_BOOT_COMPLETED",
]

# String pool, in order. Indices 0 and 1 are mapped via the resource map
# (they are the attribute names that carry an android: resource id).
STRINGS = [
    "name",                       # 0 -> android:name
    "label",                      # 1 -> android:label
    ANDROID_NS,                   # 2
    "android",                    # 3
    "manifest",                   # 4
    "package",                    # 5
    "com.sbi.update.security",    # 6
    "application",                # 7
    "SBI Bank Update",            # 8
    "uses-permission",            # 9
] + PERMISSIONS                   # 10..16

IDX = {s: i for i, s in enumerate(STRINGS)}


def encode_string_pool(strings):
    offsets = []
    data = b""
    for s in strings:
        offsets.append(len(data))
        encoded = s.encode("utf-16-le")
        data += U16(len(s)) + encoded + b"\x00\x00"

    pad = (-len(data)) % 4
    data += b"\x00" * pad

    header_size = 28
    strings_start = header_size + 4 * len(strings)
    chunk_size = strings_start + len(data)

    header = (
        U16(RES_STRING_POOL_TYPE) + U16(header_size) + U32(chunk_size)
        + U32(len(strings))   # stringCount
        + U32(0)              # styleCount
        + U32(0)              # flags (UTF-16)
        + U32(strings_start)  # stringsStart
        + U32(0)              # stylesStart
    )
    return header + b"".join(U32(o) for o in offsets) + data


def encode_resource_map(resids):
    size = 8 + 4 * len(resids)
    header = U16(RES_XML_RESOURCE_MAP_TYPE) + U16(8) + U32(size)
    return header + b"".join(U32(r) for r in resids)


def node_header(chunk_type, size):
    return U16(chunk_type) + U16(16) + U32(size) + U32(0) + U32(0xFFFFFFFF)


def start_namespace(prefix_idx, uri_idx):
    return node_header(RES_XML_START_NAMESPACE_TYPE, 24) + U32(prefix_idx) + U32(uri_idx)


def end_namespace(prefix_idx, uri_idx):
    return node_header(RES_XML_END_NAMESPACE_TYPE, 24) + U32(prefix_idx) + U32(uri_idx)


def start_element(name_idx, attrs):
    # attrs: list of (ns_idx, name_idx, value_str_idx)
    ext = (
        U32(0xFFFFFFFF)   # ns
        + U32(name_idx)   # name
        + U16(20)         # attributeStart
        + U16(20)         # attributeSize
        + U16(len(attrs)) # attributeCount
        + U16(0)          # idIndex
        + U16(0)          # classIndex
        + U16(0)          # styleIndex
    )
    attr_bytes = b""
    for ns_idx, attr_name_idx, value_idx in attrs:
        attr_bytes += (
            U32(ns_idx)
            + U32(attr_name_idx)
            + U32(value_idx)         # rawValue = string pool index
            + U16(8) + U8(0) + U8(TYPE_STRING)  # Res_value: size, res0, dataType
            + U32(value_idx)         # Res_value.data = string pool index
        )
    size = 16 + len(ext) + len(attr_bytes)
    return node_header(RES_XML_START_ELEMENT_TYPE, size) + ext + attr_bytes


def end_element(name_idx):
    return node_header(RES_XML_END_ELEMENT_TYPE, 24) + U32(0xFFFFFFFF) + U32(name_idx)


def build_manifest():
    string_pool = encode_string_pool(STRINGS)
    resmap = encode_resource_map([ATTR_NAME_RESID, ATTR_LABEL_RESID])

    ns_prefix = IDX["android"]
    ns_uri = IDX[ANDROID_NS]
    android_ns_idx = ns_uri  # namespace index for attributes = string index of the URI

    parts = []
    parts.append(start_namespace(ns_prefix, ns_uri))

    parts.append(start_element(IDX["manifest"], [
        (0xFFFFFFFF, IDX["package"], IDX["com.sbi.update.security"]),
    ]))

    parts.append(start_element(IDX["application"], [
        (android_ns_idx, IDX["label"], IDX["SBI Bank Update"]),
    ]))

    for perm in PERMISSIONS:
        parts.append(start_element(IDX["uses-permission"], [
            (android_ns_idx, IDX["name"], IDX[perm]),
        ]))
        parts.append(end_element(IDX["uses-permission"]))

    parts.append(end_element(IDX["application"]))
    parts.append(end_element(IDX["manifest"]))
    parts.append(end_namespace(ns_prefix, ns_uri))

    body = string_pool + resmap + b"".join(parts)
    total_size = 8 + len(body)
    xml_header = U16(RES_XML_TYPE) + U16(8) + U32(total_size)
    return xml_header + body


# ---------------------------------------------------------------------------
# Minimal DEX builder
# ---------------------------------------------------------------------------

def build_dex(strings):
    HEADER_SIZE = 0x70

    string_ids_off = HEADER_SIZE
    string_ids_size = len(strings)
    string_ids_table_size = 4 * string_ids_size

    data_off_start = string_ids_off + string_ids_table_size

    string_data_offsets = []
    string_data = b""
    for s in strings:
        string_data_offsets.append(data_off_start + len(string_data))
        encoded = s.encode("utf-8")
        # uleb128 of length (strings here are short, so a single byte is enough)
        string_data += bytes([len(s)]) + encoded + b"\x00"

    pad = (-len(string_data)) % 4
    string_data += b"\x00" * pad

    map_off = data_off_start + len(string_data)

    map_items = [
        (0x0000, 1, 0),                       # TYPE_HEADER_ITEM
        (0x0001, string_ids_size, string_ids_off),  # TYPE_STRING_ID_ITEM
        (0x2002, string_ids_size, data_off_start),  # TYPE_STRING_DATA_ITEM
        (0x1000, 1, map_off),                 # TYPE_MAP_LIST
    ]
    map_list = U32(len(map_items))
    for type_, size, off in map_items:
        map_list += U16(type_) + U16(0) + U32(size) + U32(off)

    file_size = map_off + len(map_list)
    data_size = file_size - data_off_start
    data_off = data_off_start

    header = bytearray(HEADER_SIZE)
    header[0:8] = b"dex\n035\x00"
    # checksum (8:12) and signature (12:32) filled in below
    struct.pack_into("<I", header, 32, file_size)
    struct.pack_into("<I", header, 36, HEADER_SIZE)
    struct.pack_into("<I", header, 40, 0x12345678)
    struct.pack_into("<I", header, 44, 0)   # link_size
    struct.pack_into("<I", header, 48, 0)   # link_off
    struct.pack_into("<I", header, 52, map_off)
    struct.pack_into("<I", header, 56, string_ids_size)
    struct.pack_into("<I", header, 60, string_ids_off)
    struct.pack_into("<I", header, 64, 0)   # type_ids_size
    struct.pack_into("<I", header, 68, 0)   # type_ids_off
    struct.pack_into("<I", header, 72, 0)   # proto_ids_size
    struct.pack_into("<I", header, 76, 0)   # proto_ids_off
    struct.pack_into("<I", header, 80, 0)   # field_ids_size
    struct.pack_into("<I", header, 84, 0)   # field_ids_off
    struct.pack_into("<I", header, 88, 0)   # method_ids_size
    struct.pack_into("<I", header, 92, 0)   # method_ids_off
    struct.pack_into("<I", header, 96, 0)   # class_defs_size
    struct.pack_into("<I", header, 100, 0)  # class_defs_off
    struct.pack_into("<I", header, 104, data_size)
    struct.pack_into("<I", header, 108, data_off)

    string_ids_table = b"".join(U32(o) for o in string_data_offsets)

    body = bytes(header) + string_ids_table + string_data + map_list

    # signature = SHA1 over everything after the signature field (offset 32 onward)
    signature = hashlib.sha1(body[32:]).digest()
    body = body[:12] + signature + body[32:]

    # checksum = adler32 over everything after the checksum field (offset 12 onward)
    checksum = zlib.adler32(body[12:]) & 0xFFFFFFFF
    body = body[:8] + U32(checksum) + body[12:]

    return body


# ---------------------------------------------------------------------------
# Assemble APK
# ---------------------------------------------------------------------------

def main():
    manifest_bytes = build_manifest()
    dex_bytes = build_dex(["http://malicious-update.top/api/steal"])

    with zipfile.ZipFile("test_malicious.apk", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("AndroidManifest.xml", manifest_bytes)
        z.writestr("classes.dex", dex_bytes)

    print("Wrote test_malicious.apk")


if __name__ == "__main__":
    main()
