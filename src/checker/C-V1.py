import re

import vera
from utils import is_source_file, is_header_file, get_lines

ALLOWED_TYPES = [
    "sfBlack",
    "sfBlendAdd",
    "sfBlendAlpha",
    "sfBlendMultiply",
    "sfBlendNone",
    "sfBlue",
    "sfCircleShape",
    "sfClock",
    "sfColor",
    "sfContext",
    "sfConvexShape",
    "sfCyan",
    "sfFloatRect",
    "sfFont",
    "sfGreen",
    "sfImage",
    "sfIntRect",
    "sfJoystick",
    "sfKeyboard",
    "sfListener",
    "sfMagenta",
    "sfMicroseconds",
    "sfMilliseconds",
    "sfMouse",
    "sfMusic",
    "sfMutex",
    "sfRectangleShape",
    "sfRed",
    "sfRenderTexture",
    "sfRenderWindow",
    "sfSeconds",
    "sfSensor",
    "sfShader",
    "sfShape",
    "sfSleep",
    "sfSound",
    "sfSoundBuffer",
    "sfSoundBufferRecorder",
    "sfSoundRecorder",
    "sfSoundStream",
    "sfSprite",
    "sfText",
    "sfTexture",
    "sfThread",
    "sfTime",
    "sfTouch",
    "sfTransform",
    "sfTransformable",
    "sfTransparent",
    "sfVertexArray",
    "sfVideoMode",
    "sfView",
    "sfWhite",
    "sfWindow",
    "sfYellow",
    "sfBool",
    "sfFtp",
    "sfFtpDirectoryResponse",
    "sfFtpListingResponse",
    "sfFtpResponse",
    "sfGlslIvec2",
    "sfGlslVec2",
    "sfGlslVec3",
    "sfHttp",
    "sfHttpRequest",
    "sfHttpResponse",
    "sfInputStream",
    "sfInputStreamGetSizeFunc",
    "sfInputStreamReadFunc",
    "sfInputStreamSeekFunc",
    "sfInputStreamTellFunc",
    "sfInt16",
    "sfInt32",
    "sfInt64",
    "sfInt8",
    "sfPacket",
    "sfShapeGetPointCallback",
    "sfSocketSelector",
    "sfSoundBuffer",
    "sfSoundBufferRecorder",
    "sfSoundRecorder",
    "sfSoundRecorderProcessCallback",
    "sfSoundRecorderStartCallback",
    "sfSoundRecorderStopCallback",
    "sfSoundStream",
    "sfSoundStreamChunk",
    "sfSoundStreamGetDataCallback",
    "sfSoundStreamSeekCallback",
    "sfTcpListener",
    "sfTcpSocket",
    "sfUdpSocket",
    "sfUint16",
    "sfUint32",
    "sfUint64",
    "sfUint8",
    "sfVector2f",
    "sfVector2u",
    "sfVector2i",
    "sfVector3f",
    "sfVector3u",
    "sfVector3i",
    "sfWindowHandle",
    "userData",
    "FILE",
    "DIR",
    "Elf_Byte",
    "Elf32_Sym",
    "Elf32_Off",
    "Elf32_Addr",
    "Elf32_Section",
    "Elf32_Versym",
    "Elf32_Half",
    "Elf32_Sword",
    "Elf32_Word",
    "Elf32_Sxword",
    "Elf32_Xword",
    "Elf32_Ehdr",
    "Elf32_Phdr",
    "Elf32_Shdr",
    "Elf32_Rel",
    "Elf32_Rela",
    "Elf32_Dyn",
    "Elf32_Nhdr",
    "Elf64_Sym",
    "Elf64_Off",
    "Elf64_Addr",
    "Elf64_Section",
    "Elf64_Versym",
    "Elf64_Half",
    "Elf64_Sword",
    "Elf64_Word",
    "Elf64_Sxword",
    "Elf64_Xword",
    "Elf64_Ehdr",
    "Elf64_Phdr",
    "Elf64_Shdr",
    "Elf64_Rel",
    "Elf64_Rela",
    "Elf64_Dyn",
    "Elf64_Nhdr",
    "_Bool",
    "WINDOW"
]


def check_function_return_type():
    for file in vera.getSourceFileNames():
        if not is_source_file(file) and not is_header_file(file):
            continue
        s = ""
        for line in get_lines(file):
            s += line
            s += "\n"
        p = re.compile(r"^[\t ]*(?P<modifiers>(?:(?:inline|static|unsigned|signed|short|long|volatile|struct)[\t ]+)*)"
                       r"(?!else|typedef|return)(?P<type>\w+)\**[\t ]+\**[\t ]*\**[\t ]*(?P<name>\w+)(?P<spaces>[\t ]*)"
                       r"\((?P<parameters>[\t ]*"
                       r"(?:(void|(\w+\**[\t ]+\**[\t ]*\**\w+[\t ]*(,[\t \n]*)?))+|)[\t ]*)\)[\t ]*"
                       r"(?P<endline>;\n|\n?{*\n){1}", re.MULTILINE)
        for search in p.finditer(s):
            line_start = s.count('\n', 0, search.start()) + 1
            if search.group('type') and not re.match("^[a-z][a-z0-9_]*$", search.group('type')) \
                    and search.group('type') not in ALLOWED_TYPES:
                vera.report(vera.Token(" ", 0, line_start, "V1", file), "MINOR:C-V1")


check_function_return_type()
