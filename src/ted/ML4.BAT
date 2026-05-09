disint
COPY [ | TIME > TIME.TXT
ECHO TEDSTR.MAC wordt nu geassembleerd...
M80 =TEDSTR/M/P > TED.ERR
COPY [ | TIME >> TIME.TXT
TYPE TED.ERR
ECHO GETPUT.MAC wordt nu geassembleerd...
M80 =GETPUT/M/P >> TED.ERR
COPY [ | TIME >> TIME.TXT
TYPE TED.ERR
ECHO SUBTED.MAC wordt nu geassembleerd...
M80 =SUBTED/M/P >> TED.ERR
COPY [ | TIME >> TIME.TXT
TYPE TED.ERR
ECHO MAIN.MAC wordt nu geassembleerd...
M80 =MAIN/M/P >> TED.ERR
COPY [ | TIME >> TIME.TXT
TYPE TED.ERR
ECHO Alles wordt nu gelinkt...
L80 SUBTED,GETPUT,TEDSTR,MAIN,/G
COPY [ | TIME >> TIME.TXT
ECHO Klaar.
enaint
