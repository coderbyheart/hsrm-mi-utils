#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
"""Script zum automatischen setzen des Druckers abhängig vom Raum
in dem man sich einloggt.

Funktioniert nur mit dem Benamungsschema am Fachbereich Medieninformatik
der Hochschule RheinMain.

@autor Markus Tacker <m@tacker.org>"""

import socket
import re
import sys
import cups
import subprocess

# Bevorzugter Drucker-Typ: schwarz oder color
pref = 'schwarz'

debug = False

def sortPrinters(p1, p2):
    if pref in p1 and pref not in p2:
        return -1
    if (pref in p1 and pref in p2) or (pref not in p1 and pref not in p2):
        return 0
    if pref not in p1 and pref in p2:
        return 1
    
def setPrinter():
    hostname = socket.gethostname()
    hnmatch = re.match('^pc([0-9]+)-[0-9]+$', hostname)
    if hnmatch is None:
        if debug:
            sys.stderr.write("Hostname %s konnte nicht erkannt werden.\n" % hostname)
        sys.exit(1)
    raumnr = int(hnmatch.groups()[0])
    
    con = cups.Connection()
    # Finde passende Drucker zum Raum
    allprinters = con.getPrinters()
    pre = re.compile('^printer%02d(-[0-9]+)*_(schwarz|color)$' % raumnr)
    printers = []
    if debug:
        sys.stdout.write("Gefundene Drucker (%d):\n" % len(allprinters))
    for printerClass in allprinters:
        if debug:
            sys.stdout.write("    %s\n" % allprinters[printerClass]['printer-info'])
        pmatch = pre.match(allprinters[printerClass]['printer-info'])
        if pmatch == None:
            continue
        printers.append({'name': printerClass, 'info': allprinters[printerClass]['printer-info']})

    if len(printers) < 1:
        if debug:
            sys.stderr.write("Keine passenden Drucker zum Raum %s gefunden.\n" % hostname)
        sys.exit(2)    
    
    printers.sort(sortPrinters, lambda printer: printer['info'])
    if debug:
        sys.stdout.write("Setze Drucker auf %s.\n" % printers[0]['name'])
    retcode = subprocess.call(['/usr/bin/env', 'lpoptions', '-d', printers[0]['name']])
    if retcode != 0:
        if debug:
            sys.stderr.write("Konnte Drucker nicht auf %s setzen.\n" % printers[0]['name'])
        sys.exit(2)
    
    if debug:
        sys.stdout.write("Default Printer auf %s gesetzt.\n" % printers[0]['name'])
        
def showHelp():
    "Zeigt die Hilfe an"
    sys.stdout.write("\n")
    sys.stdout.write("Script zum automatischen setzen des Druckers abhängig vom Raum\nin dem man sich einloggt. Funktioniert nur mit dem Benamungsschema\nam Fachbereich Medieninformatik  der Hochschule RheinMain.\n\nAutor: Markus Tacker <m@tacker.org>\n")
    sys.stdout.write("\n")
    sys.stdout.write("Verwendung: %s [Switch]\n" % sys.argv[0])
    sys.stdout.write("\n")
    sys.stdout.write("Der Aufruf ohne Switch versucht den Drucker still und heimlich zu setzen.\n")
    sys.stdout.write("\n")
    sys.stdout.write("Switch:\n")
    sys.stdout.write("    --help, -h:\n")
    sys.stdout.write("        Zeigt diese Hilfe an.\n")
    sys.stdout.write("    --debug, -d:\n")
    sys.stdout.write("        Debug-Informationen beim Setzen des Druckers ausgeben.\n")
    sys.stdout.write("\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-h', '--help'): 
            showHelp()
        if sys.argv[1] in ('-d', '--debug'):
            debug = True
            setPrinter()
    else:
        setPrinter()

