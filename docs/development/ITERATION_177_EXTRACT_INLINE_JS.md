# I177 – JavaScript aus dem Maskeneditor auslagern

**Ziel:** Die Bearbeitung des Maskeneditors vereinfachen, ohne sein sichtbares oder technisches Verhalten zu verändern.

## Änderung
Der bisher rund 86.100 Zeichen lange JavaScript-Quelltext steht jetzt unverändert in `src/provoware_db/mask_builder/interaction_script.js`. `browser_shell.py` lädt ihn beim Import aus derselben Modulablage und setzt die **ursprünglichen** `<script>`-Grenzen samt allen Zeilenumbrüchen wieder zusammen.

- Das JavaScript wird weiterhin direkt in der HTML-Antwort eingebettet. Es entstehen **keine zusätzlichen HTTP-Endpunkte** und keine Abhängigkeiten von externen Servern.
- HTML, CSS, WSGI-Server, Datenmodell und produktive Speicherung bleiben unverändert.
- Der SHA-1-Wert im Git-Blob-Format des ursprünglichen kompletten Inline-Skriptblocks ist `20fd1f9b5080c4cf53b738b3109697d6bfd28851`. Der neue Regressionstest berechnet ihn erneut aus dem gerenderten Scriptblock.
- Die bisherigen Maskeneditor-Regressionstests und der Ausgangstest I176 müssen weiterhin bestehen.

## Grenzen
Die separate `.js`-Datei muss beim Start **im selben Ordner wie `browser_shell.py`** liegen. Der bisherige Source-Start wird dadurch klarer und einfacher wartbar. Ein späteres installierbares Distributionspaket muss die Datei ausdrücklich mitliefern; ohne diesen Nachweis keine portable Paketfreigabe.

Die Datei wird **nicht** über einen zusätzlichen HTTP-Pfad ausgeliefert. Der Editor bleibt auf GET für `/` beschränkt. Änderungen an HTML-/CSS-Ausgabe oder Browser-Darstellung benötigen eine neue, gesondert geprüfte Iteration.

## Einfache Erklärung
Das große JavaScript-Programm liegt jetzt in einer eigenen Datei. Beim Aufruf des Editors wird es genauso wie bisher in die Seite eingesetzt. Dadurch können Entwickler den Programmteil leichter bearbeiten, ohne dass die Bedienoberfläche verändert werden soll.
