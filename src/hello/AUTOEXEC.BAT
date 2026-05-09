ECHO OFF
ECHO --- assembling HELLO ---
M80 =HELLO/M/P
ECHO --- linking HELLO ---
L80 HELLO,HELLO/N/E
ECHO --- running HELLO ---
HELLO
ECHO --- done ---
DIR HELLO.COM
