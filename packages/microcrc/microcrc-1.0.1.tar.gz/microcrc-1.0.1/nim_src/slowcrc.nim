# mymodule.nim - file name should match the module name you're going to import from python
# https://github.com/yglukhov/nimpy/tree/master
# Compile on Windows:
# nim c --app:lib --out:mymodule.pyd --threads:on --tlsEmulation:off --passL:-static mymodule
# Compile on everything else:
# nim c --app:lib --out:mymodule.so --threads:on mymodule

import strutils
import nimpy

type CRC32* = uint32
const initCRC32* = CRC32(0xFFFFFFFF)

proc createCRCTable(): array[256, CRC32] =
  for i in 0..255:
    var rem = CRC32(i)
    for j in 0..7:
      if (rem and 1) > 0: rem = (rem shr 1) xor CRC32(0xedb88320)
      else: rem = rem shr 1
    result[i] = rem

# Table created at runtime
var crc32table = createCRCTable()

proc crc32(s: string): CRC32 {.exportpy.} =
  result = initCRC32
  for c in s:
    result = (result shr 8) xor crc32table[(result and 0xff) xor uint32(ord(c))]
  result = not result

# String conversion proc $, automatically called by echo
proc `$`(c: CRC32): string = int64(c).toHex(8)

# assert crc32("The quick brown fox jumps over the lazy dog") == 0x414FA339