disint
M80 %1=%1/p/m > ted.err
type ted.err
M80 %2=%2/p/m >> ted.err
type ted.err
M80 %3=%3/p/m >> ted.err
type ted.err
L80 SUBTED,GETPUT,TEDSTR,MAIN,/G
enaint
