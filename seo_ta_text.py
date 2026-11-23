# -*- coding: utf-8 -*-
"""23.11.2026 SEO: eigener Fließtext + FAQ für tagesaktuell.html (aufgerufen aus tagesaktuell_seite.render). Keine Tageszahlen im Text, damit nichts veraltet."""
import html
e = html.escape
FAQ = [
 ("Was sind tagesaktuelle Arbeitsblätter zu Nachrichten?",
  "Es sind Arbeitsblätter, die ein aktuelles Ereignis aus den Nachrichten für den Unterricht aufbereiten: ein kurzer Lesetext, Aufgaben zum Verstehen und Diskutieren, eine Kartenaufgabe und ein Lösungsblatt für Lehrkräfte. Sie erscheinen jeden Tag neu und lassen sich ohne Vorbereitung einsetzen."),
 ("Sind die Nachrichten-Arbeitsblätter wirklich kostenlos?",
  "Ja. Alle Blätter auf dieser Seite sind kostenlos als PDF abrufbar, ohne Anmeldung. Du kannst sie für deinen eigenen Unterricht ausdrucken und kopieren."),
 ("Für welche Klassenstufen sind die Blätter gedacht?",
  "Jedes Thema gibt es in zwei Fassungen: für Klasse 5–6 mit einfacherer Sprache und kürzerem Text sowie für Klasse 7–10 mit anspruchsvolleren Aufgaben. Beide Fassungen gibt es farbig und in Schwarz-Weiß."),
 ("Woher stammen die Informationen und Bilder?",
  "Die Texte beruhen auf mindestens zwei unabhängigen Meldungen; die Quellen stehen im Lösungsblatt. Die Fotos sind frei lizenzierte Bilder von Wikimedia Commons, der Nachweis steht am Blatt."),
 ("Wie setze ich die Blätter im Unterricht ein?",
  "Gut geeignet sind der Morgenkreis, eine Vertretungsstunde, die Einstiegsphase im Politik-, Erdkunde- oder Deutschunterricht oder eine Hausaufgabe. Bei ernsten Themen stehen Hinweise zum behutsamen Umgang im Lösungsblatt."),
]


def block():
    t = ("<h2 id=\"einsatz\">Tagesaktuelle Arbeitsblätter zu Nachrichten im Unterricht</h2>"
         "<p>Aktuelle Nachrichten holen die Welt ins Klassenzimmer. Schülerinnen und Schüler erleben, dass Politik, Wissenschaft, Umwelt und Wirtschaft nicht nur im Schulbuch stattfinden, sondern jeden Tag. "
         "Das Problem für Lehrkräfte ist der Aufwand: Ein gutes Nachrichtenthema zu finden, den Text altersgerecht zu kürzen, Aufgaben zu schreiben und eine Lösung zu erstellen, kostet schnell eine Stunde. "
         "Genau diese Arbeit nehmen dir die tagesaktuellen Arbeitsblätter auf dieser Seite ab.</p>"
         "<h3>Was auf jedem Blatt steht</h3>"
         "<p>Jedes Blatt beginnt mit einem verständlichen Lesetext zum Ereignis des Tages. Darauf folgen Aufgaben, die vom reinen Verstehen („Was ist passiert?“) über das Einordnen („Warum ist das wichtig?“) bis zum Diskutieren und Begründen führen. "
         "Fast immer gehört eine Kartenaufgabe dazu, damit die Klasse lernt, wo ein Ereignis stattfindet. Für dich gibt es ein eigenes Lösungsblatt mit den erwarteten Antworten und den Quellen, auf die sich der Text stützt.</p>"
         "<h3>Zwei Klassenstufen, zwei Fassungen</h3>"
         "<p>Alle Themen erscheinen in einer Fassung für Klasse 5–6 und in einer Fassung für Klasse 7–10. Die jüngere Stufe arbeitet mit kürzeren Sätzen und konkreten Beispielen, die ältere verlangt Begründungen, Vergleiche und eigene Stellungnahmen. "
         "Wer Tinte sparen möchte, nimmt die Schwarz-Weiß-Fassung; sie ist inhaltlich identisch und kopiert sich sauber.</p>"
         "<h3>Einsatz im Fachunterricht</h3>"
         "<p>Die Themen kommen aus Politik, Geographie, Umwelt, Wirtschaft und Gesellschaft und passen deshalb zu Politik und Sozialkunde, Erdkunde, Deutsch, Ethik und dem Sachunterricht der höheren Klassen. "
         "Das tägliche Nachrichtenblatt eignet sich als fester Einstieg am Wochenanfang, als Vertretungsmaterial, das ohne Vorbereitung funktioniert, oder als Übung zur Medienkompetenz: Woher weiß ich, ob eine Meldung stimmt? "
         "Mehr zu festen Unterrichtsthemen findest du bei den <a href=\"lehrplan-themen.html\">Lehrplan-Themen</a>, weitere kostenlose Blätter unter <a href=\"kostenlos.html\">kostenloses Unterrichtsmaterial</a>.</p>"
         "<h2 id=\"faq\">Häufige Fragen zu den News-Arbeitsblättern</h2>"
         + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQ))
    return t


def faq_ld():
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
