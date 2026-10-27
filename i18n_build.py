# -*- coding: utf-8 -*-
"""27.10.: Sprachversionen /en/ /es/ /fr/ /it/ fuer snice-unterricht.eu (wird von build.py aufgerufen).
EN/ES (+ FR-Einzelstuecke) = Live-Produkte im TpT-Store "snice" (_tpt_live.json, Skripte/_homepage_tpt_pull.py),
FR/IT = eduki-Welten fr/it (_eduki_welten.json, Skripte/_homepage_eduki_welt_pull.py).
Je Sprache nur Material in DIESER Sprache; die anderen Sprachen stehen unter "Other languages".
hreflang-Cluster (gleichwertige Seiten) + x-default (EN), Sitemap je Sprache mit xhtml:link,
Sprachumschalter auf jeder Seite, automatische Sprachwahl NUR auf der deutschen Startseite (JS, keine Bots)."""
import os, re, json, html, datetime, collections, glob

B = None            # build-Modul (in prepare() gesetzt)
SITE = "https://snice-unterricht.eu"
TPT_STORE = "https://www.teacherspayteachers.com/store/snice"
LANGS = ["de", "en", "es", "fr", "it"]
FOREIGN = ["en", "es", "fr", "it"]
LANG_NAME = {"de": "Deutsch", "en": "English", "es": "Español", "fr": "Français", "it": "Italiano"}
OG_LOCALE = {"de": "de_DE", "en": "en_US", "es": "es_LA", "fr": "fr_FR", "it": "it_IT"}
GRID_FIRST = 48
ITEMS = {}          # lang -> [item]
PAGES = {}          # lang -> {cluster_key: slug}  (nur tatsaechlich gebaute Seiten)
DE_CLUSTER = {}     # DE-Slug -> cluster_key
SITEMAP_URLS = {}   # lang -> [(url, cluster_key|None)]
STATS = {}

# ------------------------------------------------------------------ Texte (von Hand geschrieben, Gegenpruefung per LLM)
T = {
 "en": {
  "free": "Free resources", "free_nav": "Free", "free_title": "Free Reading Comprehension Resources – No Prep",
  "free_desc": "Free printable resources from my TpT store: no-prep reading comprehension with answer keys. The list updates automatically.",
  "free_intro": "These resources are currently free in my TpT store. The list updates automatically every day.",
  "home_title": "No-Prep Reading Comprehension & Math Centers | Snice",
  "home_desc": "{n}+ printable, no-prep resources with answer keys: reading comprehension passages, escape-style reading trails, and math centers for grades {g}. Available in my TpT store.",
  "eyebrow": "By a teacher, for teachers",
  "h1a": "Classroom-ready.", "h1b": "In five minutes.",
  "hero_sub": "{n}+ no-prep printables with answer keys – reading comprehension passages, escape-style reading trails, and hands-on math centers for grades {g}.",
  "search_ph": "Search: Thanksgiving, volcano, Rome…", "search_label": "Search resources",
  "btn_store": "Visit my TpT store", "btn_all": "Browse all resources",
  "trust": ["<b>{n}+</b> resources", "<b>Answer keys</b> included", "<b>No prep</b> – print &amp; go", "<b>Grades {g}</b>"],
  "trust_trails": "<b>{n}+</b> reading trails",
  "tiles": [("No prep", "Printable PDF – print and go. Every resource comes with an answer key, so it works for sub plans, centers and early finishers."),
            ("Built for real classrooms", "Clear, simple language, step-by-step tasks and self-checking elements help every student work independently."),
            ("Standards in mind", "Listings name the matching CCSS reading and language standards, so planning stays quick.")],
  "all": "All resources", "new": "New", "new_long": "New resources", "fall": "Thanksgiving & Fall", "winter": "Christmas & Winter",
  "trails": "Reading Trails", "rw": "Math Role Plays", "ws": "Reading Comprehension Worksheets", "bundle": "Bundles", "ws_nav": "Worksheets",
  "other": "Other languages", "store": "TpT store", "about_link": "About",
  "fam_blurb": {
    "trails": "Escape-style reading scavenger hunts: students read a station, follow the clue to the next place, collect letters, and crack the secret word. Dead ends let them check their own work.",
    "rw": "Hands-on math centers: the class plays a real-life scene and practices math along the way – with answer keys.",
    "ws": "Informational text as a cloze passage with word bank, a QR-code listening task with free audio, and a word search – 5 pages with answer keys.",
    "bundle": "Several resources on one topic in one download – at a lower price than buying them one by one."},
  "season_blurb": {
    "fall": "Pumpkins, apples, harvest, and Thanksgiving – reading and math resources for the fall months.",
    "winter": "Gingerbread, snow, winter sports, Christmas, and the New Year – resources for the cold season."},
  "n_items": "{n} resources", "n_item": "1 resource", "see_all": "See all {n} →", "more": "Show more", "loading": "Loading …",
  "noresults": "No resources found – try a different search term or filter.",
  "by_subject": "By subject", "by_subject_lead": "All resources on one topic area – filterable by grade.",
  "by_grade": "By grade", "by_grade_lead": "Pick a grade level to see matching resources.",
  "grade": "Grade", "grades": "Grades", "grade_n": "Grade {n}", "all_chip": "All",
  "subject": "Subject", "pages": "Pages", "format": "Format", "type": "Resource type", "answer_key": "Answer key", "included": "Included",
  "price": "Price", "free": "FREE",
  "btn_buy": "View on TpT", "btn_buy_eduki": "View on eduki", "related": "Similar resources", "overview": "Related pages",
  "click_note": "Each card opens the resource page; the button there takes you to TpT.",
  "faq_h": "Frequently asked questions",
  "faq": [("Where can I buy the resources?", "All resources on this page are sold in my Teachers Pay Teachers store “Snice”. Every resource page has a button that takes you straight to the product on TpT."),
          ("Which grades are they for?", "Most resources are written for grades 1–10. The exact grade range is shown on each resource page and in the TpT listing."),
          ("Are answer keys included?", "Yes. The reading passages, reading trails and math centers come with answer keys, so they also work as sub plans or independent work."),
          ("What format are the files?", "Printable PDF files – no prep needed: print and go."),
          ("Do you have resources in other languages?", "Yes: Spanish resources are on the Spanish page, and French and Italian worksheets, as well as German materials, can be found under “Other languages”.")],
  "about_h": "By a teacher, for teachers",
  "about_p": "I'm a teacher from Germany and I create classroom resources for my own students first. Every resource is checked before it goes live – so you spend less time preparing and more time teaching.",
  "other_title": "Resources in other languages", "other_h1": "Other languages",
  "other_intro": "This page only shows resources in English. Here you'll find my materials in Spanish, French, Italian and German.",
  "other_desc": "Snice resources in other languages: Spanish reading passages and reading trails, French and Italian worksheets and German teaching materials.",
  "lang_blurb": {"es": "Spanish reading passages, cloze worksheets and reading trails – available on TpT.",
                 "fr": "French cloze worksheets with listening task and word search – available on eduki.",
                 "it": "Italian cloze worksheets with listening task and word search – available on eduki.",
                 "de": "More than {n} German teaching materials with answer keys – available on eduki.",
                 "en": "English reading passages, reading trails and math centers – available on TpT."},
  "to_lang": "Go to the {l} page →", "de_home": "Go to the German homepage →",
  "all_title": "All Resources – Reading Comprehension, Reading Trails & Math Centers",
  "all_desc": "Search all {n} Snice resources by topic, subject and grade: reading comprehension worksheets, reading trails, math role plays and bundles with answer keys.",
  "all_intro": "Search for a topic or filter by subject and grade. Each resource page links straight to the product in my TpT store.",
  "new_title": "New Resources", "new_desc": "The newest Snice resources: reading trails, math centers and reading comprehension worksheets – newest first.",
  "new_intro": "My newest resources appear here first. The list updates automatically.",
  "season_title": {"fall": "Thanksgiving & Fall Resources", "winter": "Christmas & Winter Resources"},
  "season_desc": {"fall": "No-prep fall resources: Thanksgiving, pumpkins, apples and harvest – reading comprehension, reading trails and math centers with answer keys.",
                  "winter": "No-prep winter resources: Christmas, gingerbread, snow, winter sports and New Year – reading comprehension, reading trails and math centers with answer keys."},
  "fam_title": {"trails": "Reading Trails – Escape-Style Reading Scavenger Hunts", "rw": "Math Role Plays – Hands-On Math Centers",
                "ws": "Reading Comprehension Worksheets with Cloze, Listening & Word Search", "bundle": "Bundles – Save with Resource Sets"},
  "subj_title": "{s} Resources", "subj_desc": "{n} no-prep {s} resources with answer keys: reading comprehension, reading trails, and more – filter by grade.",
  "grade_title": "Grade {g} Resources", "grade_desc": "{n} no-prep resources for grade {g} with answer keys: reading comprehension passages, reading trails, and math centers.",
  "crumb_home": "Home", "nav_label": "Main navigation", "lang_label": "Language",
  "foot_tag": "Resources that make teaching easier.",
  "foot_sold": "All resources on this page are sold in my <a href=\"{store}\" rel=\"noopener\">Teachers Pay Teachers store</a>.",
  "legal": "Legal notice (German)", "privacy": "Privacy policy (German)",
  "home": "Home", "skip": "Skip to content",
  "ws_suffix": "", "story_in": "",
  "meta_ws": "Reading comprehension worksheet", "meta_trail": "Reading trail", "meta_rw": "Math role play", "meta_bundle": "Bundle", "meta_other": "Resource",
 },
 "es": {
  "free": "Recursos gratis", "free_nav": "Gratis", "free_title": "Recursos gratis en español",
  "free_desc": "Recursos gratis de mi tienda de TpT, sin preparación y con solucionario. La lista se actualiza automáticamente.",
  "free_intro": "Estos recursos son gratis en este momento en mi tienda de TpT. La lista se actualiza cada día.",
  "home_title": "Lecturas en español y búsquedas del tesoro, sin preparación | Snice",
  "home_desc": "Más de {n} recursos imprimibles en español con solucionario: fichas de comprensión lectora y búsquedas del tesoro de lectura para los grados {g}. Disponibles en mi tienda de TpT.",
  "eyebrow": "De un docente para docentes",
  "h1a": "Listo para la clase.", "h1b": "En cinco minutos.",
  "hero_sub": "Más de {n} recursos imprimibles en español, sin preparación y con solucionario: fichas de comprensión lectora y búsquedas del tesoro de lectura al estilo escape room.",
  "search_ph": "Buscar: otoño, volcán, Roma …", "search_label": "Buscar recursos",
  "btn_store": "Ir a mi tienda en TpT", "btn_all": "Ver todos los recursos",
  "trust": ["<b>{n}+</b> recursos", "<b>Solucionario</b> incluido", "<b>Sin preparación</b>: imprimir y usar", "<b>Grados {g}</b>"],
  "trust_trails": "<b>{n}+</b> búsquedas del tesoro",
  "tiles": [("Sin preparación", "PDF para imprimir y usar de inmediato. Cada recurso incluye el solucionario: ideal para suplencias, estaciones o trabajo autónomo."),
            ("Pensado para el aula", "Lenguaje claro y sencillo, tareas paso a paso y elementos de autocorrección para que cada estudiante trabaje con autonomía."),
            ("Todo en español", "Los textos y las tareas para el alumno están en español neutro, adecuados para clases de español, programas bilingües y ELE.")],
  "all": "Todos los recursos", "new": "Novedades", "new_long": "Recursos nuevos", "fall": "Otoño", "winter": "Navidad e invierno",
  "trails": "Búsquedas del tesoro", "rw": "Juegos de rol de matemáticas", "ws": "Fichas de lectura", "bundle": "Paquetes",
  "other": "Otros idiomas", "store": "Tienda TpT", "about_link": "Sobre mí",
  "fam_blurb": {
    "trails": "Búsquedas del tesoro de lectura al estilo escape room: el alumnado lee una estación, sigue la pista hasta el siguiente lugar, reúne letras y descifra la palabra secreta. Los callejones sin salida permiten la autocorrección.",
    "rw": "Estaciones de matemáticas: la clase representa una escena de la vida real y practica matemáticas, con solucionario.",
    "ws": "Texto informativo en español con huecos y banco de palabras, comprensión auditiva con código QR (audio gratuito) y sopa de letras: 5 páginas con solucionario.",
    "bundle": "Varios recursos sobre un tema en una sola descarga, a un precio menor que por separado."},
  "season_blurb": {
    "fall": "Calabazas, cosecha, hojas de otoño y fiestas de temporada: recursos de lectura para los meses de otoño.",
    "winter": "Pan de jengibre, nieve, deportes de invierno, Navidad y Año Nuevo: recursos para la temporada fría."},
  "n_items": "{n} recursos", "n_item": "1 recurso", "see_all": "Ver los {n} →", "more": "Mostrar más", "loading": "Cargando …",
  "noresults": "No se encontraron recursos. Prueba con otra palabra o con otro filtro.",
  "by_subject": "Por materia", "by_subject_lead": "Todos los recursos de un área en una sola página, filtrables por grado.",
  "by_grade": "Por grado", "by_grade_lead": "Elige un grado para ver los recursos adecuados.",
  "grade": "Grado", "grades": "Grados", "grade_n": "Grado {n}", "all_chip": "Todos",
  "subject": "Materia", "pages": "Páginas", "format": "Formato", "type": "Tipo de recurso", "answer_key": "Solucionario", "included": "Incluido",
  "price": "Precio", "free": "GRATIS",
  "btn_buy": "Ver en TpT", "btn_buy_eduki": "Ver en eduki", "related": "Recursos similares", "overview": "Páginas relacionadas",
  "click_note": "Cada tarjeta abre la página del recurso; desde allí el botón lleva a TpT.",
  "faq_h": "Preguntas frecuentes",
  "faq": [("¿Dónde puedo comprar los recursos?", "Todos los recursos de esta página se venden en mi tienda “Snice” de Teachers Pay Teachers (TpT). Cada página de recurso tiene un botón que lleva directamente al producto."),
          ("¿Para qué grados son?", "El grado exacto aparece en cada página de recurso y en la ficha de TpT. Las fichas de lectura en español están pensadas sobre todo para los grados 7–12."),
          ("¿Incluyen solucionario?", "Sí. Las fichas de lectura y las búsquedas del tesoro incluyen solucionario, así que también sirven para suplencias o trabajo autónomo."),
          ("¿En qué formato están?", "Archivos PDF para imprimir, sin preparación: imprimir y usar."),
          ("¿Hay recursos en otros idiomas?", "Sí: en la sección “Otros idiomas” encontrarás mis recursos en inglés, francés, italiano y alemán.")],
  "about_h": "De un docente para docentes",
  "about_p": "Soy docente en Alemania y creo los recursos primero para mis propios estudiantes. Cada recurso se revisa antes de publicarse, para que prepares menos y enseñes más.",
  "other_title": "Recursos en otros idiomas", "other_h1": "Otros idiomas",
  "other_intro": "Esta página solo muestra recursos en español. Aquí encontrarás mis materiales en inglés, francés, italiano y alemán.",
  "other_desc": "Recursos de Snice en otros idiomas: lecturas y búsquedas del tesoro en inglés, fichas en francés e italiano y materiales en alemán.",
  "lang_blurb": {"en": "Lecturas, búsquedas del tesoro y estaciones de matemáticas en inglés, disponibles en TpT.",
                 "fr": "Fichas en francés con texto con huecos, comprensión auditiva y sopa de letras, disponibles en eduki.",
                 "it": "Fichas en italiano con texto con huecos, comprensión auditiva y sopa de letras, disponibles en eduki.",
                 "de": "Más de {n} materiales en alemán con solucionario, disponibles en eduki.",
                 "es": ""},
  "to_lang": "Ir a la página en {l} →", "de_home": "Ir a la página en alemán →",
  "all_title": "Todos los recursos en español: fichas de lectura y búsquedas del tesoro",
  "all_desc": "Busca entre los {n} recursos de Snice en español por tema, materia y grado: fichas de comprensión lectora, búsquedas del tesoro y paquetes con solucionario.",
  "all_intro": "Busca un tema o filtra por materia y grado. Cada página de recurso lleva directamente al producto en mi tienda de TpT.",
  "new_title": "Recursos nuevos en español", "new_desc": "Los recursos más nuevos de Snice en español: búsquedas del tesoro y fichas de lectura, los más recientes primero.",
  "new_intro": "Aquí aparecen primero mis recursos más nuevos. La lista se actualiza automáticamente.",
  "season_title": {"fall": "Recursos de otoño en español", "winter": "Recursos de Navidad e invierno en español"},
  "season_desc": {"fall": "Recursos de otoño en español, sin preparación: calabazas, cosecha y fiestas de temporada, con solucionario.",
                  "winter": "Recursos de invierno en español, sin preparación: Navidad, pan de jengibre, nieve y Año Nuevo, con solucionario."},
  "fam_title": {"trails": "Búsquedas del tesoro de lectura en español (estilo escape room)", "rw": "Juegos de rol de matemáticas",
                "ws": "Fichas de lectura en español: texto con huecos, comprensión auditiva y sopa de letras", "bundle": "Paquetes de recursos en español"},
  "subj_title": "Recursos de {s} en español", "subj_desc": "{n} recursos de {s} en español, sin preparación y con solucionario: fichas de lectura, búsquedas del tesoro y más, filtrables por grado.",
  "grade_title": "Recursos en español para el grado {g}", "grade_desc": "{n} recursos en español para el grado {g}, sin preparación y con solucionario.",
  "crumb_home": "Inicio", "nav_label": "Navegación principal", "lang_label": "Idioma",
  "foot_tag": "Recursos que facilitan la enseñanza.",
  "foot_sold": "Todos los recursos de esta página se venden en mi <a href=\"{store}\" rel=\"noopener\">tienda de Teachers Pay Teachers</a>.",
  "legal": "Aviso legal (en alemán)", "privacy": "Privacidad (en alemán)",
  "home": "Inicio", "skip": "Saltar al contenido",
  "meta_ws": "Ficha de lectura", "meta_trail": "Búsqueda del tesoro", "meta_rw": "Juego de rol de matemáticas", "meta_bundle": "Paquete", "meta_other": "Recurso",
 },
 "fr": {
  "free": "Ressources gratuites", "free_nav": "Gratuit", "free_title": "Fiches gratuites en français",
  "free_desc": "Fiches gratuites en français, prêtes à imprimer et avec corrigé. La liste se met à jour automatiquement.",
  "free_intro": "Ces fiches sont actuellement gratuites dans ma boutique. La liste se met à jour chaque jour.",
  "home_title": "Fiches de lecture en français, prêtes à imprimer | Snice",
  "home_desc": "Plus de {n} fiches en français avec corrigé : texte à trous avec banque de mots, compréhension orale par QR code et mots mêlés. Disponibles sur eduki.",
  "eyebrow": "D'un enseignant pour les enseignants",
  "h1a": "Prêt pour la classe.", "h1b": "En cinq minutes.",
  "hero_sub": "Plus de {n} fiches en français, prêtes à imprimer et avec corrigé : texte documentaire à trous, compréhension orale par QR code et mots mêlés.",
  "search_ph": "Chercher : automne, volcan, Rome …", "search_label": "Chercher une ressource",
  "btn_store": "Voir ma boutique sur eduki", "btn_all": "Toutes les ressources",
  "trust": ["<b>{n}+</b> fiches", "<b>Corrigé</b> inclus", "<b>Sans préparation</b> : imprimer et c'est parti", "<b>{g}</b>"],
  "trust_trails": "",
  "tiles": [("Sans préparation", "PDF à imprimer, utilisable tout de suite. Chaque fiche contient son corrigé : idéal pour l'autonomie, les ateliers ou un remplacement."),
            ("Pensé pour la classe", "Un langage clair, des consignes pas à pas et des éléments d'autocorrection pour que chaque élève avance seul."),
            ("Écouter et lire", "Le texte est enregistré : un QR code donne accès à l'audio en français (MP3 gratuit, sans inscription).")],
  "all": "Toutes les ressources", "new": "Nouveautés", "new_long": "Nouvelles ressources", "fall": "Automne", "winter": "Noël et hiver",
  "trails": "Rallyes-lecture", "rw": "Jeux de rôle en maths", "ws": "Fiches de lecture", "bundle": "Lots",
  "other": "Autres langues", "store": "Boutique eduki", "about_link": "À propos",
  "fam_blurb": {
    "trails": "Rallyes-lecture façon escape game : les élèves lisent une étape, suivent l'indice jusqu'au lieu suivant et trouvent le mot secret.",
    "rw": "Ateliers de maths : la classe joue une scène de la vie quotidienne et calcule en chemin.",
    "ws": "Texte documentaire à trous avec banque de mots, compréhension orale par QR code (audio gratuit) et mots mêlés, avec corrigé.",
    "bundle": "Plusieurs ressources sur un même thème en un seul téléchargement."},
  "season_blurb": {
    "fall": "Citrouilles, récoltes, feuilles et fêtes d'automne : des fiches pour les mois d'automne.",
    "winter": "Noël, neige, sports d'hiver et Nouvel An : des fiches pour la saison froide."},
  "n_items": "{n} ressources", "n_item": "1 ressource", "see_all": "Voir les {n} →", "more": "Afficher plus", "loading": "Chargement …",
  "noresults": "Aucune ressource trouvée – essaie un autre mot ou un autre filtre.",
  "by_subject": "Par thème", "by_subject_lead": "Toutes les fiches d'un domaine sur une seule page.",
  "by_grade": "Par niveau", "by_grade_lead": "Choisis un niveau pour voir les fiches adaptées.",
  "grade": "Niveau", "grades": "Niveaux", "grade_n": "{n}", "all_chip": "Tous",
  "subject": "Thème", "pages": "Pages", "format": "Format", "type": "Type de ressource", "answer_key": "Corrigé", "included": "Inclus",
  "price": "Prix", "free": "GRATUIT",
  "btn_buy": "Voir sur TpT", "btn_buy_eduki": "Voir sur eduki", "related": "Ressources similaires", "overview": "Pages associées",
  "click_note": "Chaque carte ouvre la page de la ressource ; le bouton mène ensuite à la boutique.",
  "faq_h": "Questions fréquentes",
  "faq": [("Où acheter les fiches ?", "Les fiches en français sont vendues dans ma boutique « Snice » sur eduki. Chaque page de ressource contient un bouton qui mène directement au produit."),
          ("Pour quel niveau ?", "Le niveau indiqué sur eduki figure sur chaque page de ressource. Le texte est écrit dans un langage clair et simple."),
          ("Le corrigé est-il inclus ?", "Oui, chaque fiche contient son corrigé."),
          ("Sous quel format ?", "Des fichiers PDF à imprimer, sans préparation."),
          ("Existe-t-il des ressources dans d'autres langues ?", "Oui : sous « Autres langues », tu trouveras mes ressources en anglais, en espagnol, en italien et en allemand.")],
  "about_h": "D'un enseignant pour les enseignants",
  "about_p": "Je suis enseignant en Allemagne et je crée mes ressources d'abord pour mes propres élèves. Chaque fiche est vérifiée avant sa publication, pour que tu passes moins de temps à préparer et plus de temps à enseigner.",
  "other_title": "Ressources dans d'autres langues", "other_h1": "Autres langues",
  "other_intro": "Cette page ne montre que des ressources en français. Tu trouveras ici mes ressources en anglais, en espagnol, en italien et en allemand.",
  "other_desc": "Ressources Snice dans d'autres langues : lectures et rallyes-lecture en anglais et en espagnol, fiches en italien et matériel en allemand.",
  "lang_blurb": {"en": "Lectures, rallyes-lecture et ateliers de maths en anglais, disponibles sur TpT.",
                 "es": "Lectures et rallyes-lecture en espagnol, disponibles sur TpT.",
                 "it": "Fiches en italien avec texte à trous, compréhension orale et mots mêlés, disponibles sur eduki.",
                 "de": "Plus de {n} ressources en allemand avec corrigé, disponibles sur eduki.",
                 "fr": ""},
  "to_lang": "Aller à la page en {l} →", "de_home": "Aller à la page en allemand →",
  "all_title": "Toutes les fiches en français : lecture, écoute et mots mêlés",
  "all_desc": "Cherche parmi les {n} fiches Snice en français par thème et par niveau : texte à trous, compréhension orale et mots mêlés, avec corrigé.",
  "all_intro": "Cherche un thème ou filtre par domaine et par niveau. Chaque page de ressource mène directement au produit.",
  "new_title": "Nouvelles fiches en français", "new_desc": "Les fiches Snice les plus récentes en français, les plus récentes d'abord.",
  "new_intro": "Mes nouvelles fiches apparaissent ici en premier. La liste se met à jour automatiquement.",
  "season_title": {"fall": "Fiches d'automne en français", "winter": "Fiches de Noël et d'hiver en français"},
  "season_desc": {"fall": "Fiches d'automne en français, prêtes à imprimer : citrouille, récoltes et fêtes d'automne, avec corrigé.",
                  "winter": "Fiches de Noël et d'hiver en français, prêtes à imprimer : Noël, neige et Nouvel An, avec corrigé."},
  "fam_title": {"trails": "Rallyes-lecture en français", "rw": "Jeux de rôle en maths",
                "ws": "Fiches de lecture : texte à trous, compréhension orale et mots mêlés", "bundle": "Lots de ressources"},
  "subj_title": "Fiches « {s} » en français", "subj_desc": "{n} fiches en français sur le thème « {s} », prêtes à imprimer et avec corrigé.",
  "grade_title": "Fiches en français – {g}", "grade_desc": "{n} fiches en français pour le niveau {g}, prêtes à imprimer et avec corrigé.",
  "crumb_home": "Accueil", "nav_label": "Navigation principale", "lang_label": "Langue",
  "foot_tag": "Des ressources qui facilitent l'enseignement.",
  "foot_sold": "Les fiches en français sont vendues dans ma <a href=\"{store}\" rel=\"noopener\">boutique sur eduki</a>.",
  "legal": "Mentions légales (en allemand)", "privacy": "Confidentialité (en allemand)",
  "home": "Accueil", "skip": "Aller au contenu",
  "meta_ws": "Fiche de lecture", "meta_trail": "Rallye-lecture", "meta_rw": "Jeu de rôle en maths", "meta_bundle": "Lot", "meta_other": "Ressource",
 },
 "it": {
  "free": "Materiali gratuiti", "free_nav": "Gratis", "free_title": "Schede gratuite in italiano",
  "free_desc": "Schede gratuite in italiano, pronte da stampare e con soluzioni. L'elenco si aggiorna automaticamente.",
  "free_intro": "Queste schede sono attualmente gratuite nel mio negozio. L'elenco si aggiorna ogni giorno.",
  "home_title": "Schede di lettura in italiano, pronte da stampare | Snice",
  "home_desc": "Oltre {n} schede in italiano con soluzioni: testo con spazi vuoti e banca delle parole, comprensione all'ascolto con codice QR e crucipuzzle. Disponibili su eduki.",
  "eyebrow": "Da un insegnante per gli insegnanti",
  "h1a": "Pronto per la classe.", "h1b": "In cinque minuti.",
  "hero_sub": "Oltre {n} schede in italiano, pronte da stampare e con soluzioni: testo informativo con spazi vuoti, comprensione all'ascolto con codice QR e crucipuzzle.",
  "search_ph": "Cerca: autunno, vulcano, Roma …", "search_label": "Cerca materiali",
  "btn_store": "Vai al mio negozio su eduki", "btn_all": "Tutti i materiali",
  "trust": ["<b>{n}+</b> schede", "<b>Soluzioni</b> incluse", "<b>Senza preparazione</b>: stampa e usa", "<b>{g}</b>"],
  "trust_trails": "",
  "tiles": [("Senza preparazione", "PDF da stampare e usare subito. Ogni scheda contiene le soluzioni: ideale per il lavoro autonomo o una supplenza."),
            ("Pensato per la classe", "Linguaggio chiaro e semplice, consegne passo dopo passo ed elementi di autocorrezione."),
            ("Leggere e ascoltare", "Il testo è registrato: un codice QR porta all'audio in italiano (MP3 gratuito, senza registrazione).")],
  "all": "Tutti i materiali", "new": "Novità", "new_long": "Nuovi materiali", "fall": "Autunno", "winter": "Natale e inverno",
  "trails": "Cacce al tesoro di lettura", "rw": "Giochi di ruolo di matematica", "ws": "Schede di lettura", "bundle": "Pacchetti",
  "other": "Altre lingue", "store": "Negozio eduki", "about_link": "Chi sono",
  "fam_blurb": {
    "trails": "Cacce al tesoro di lettura in stile escape room: gli alunni leggono una tappa, seguono l'indizio fino al luogo successivo e scoprono la parola segreta.",
    "rw": "Laboratori di matematica: la classe recita una scena di vita quotidiana e calcola strada facendo.",
    "ws": "Testo informativo con spazi vuoti e banca delle parole, comprensione all'ascolto con codice QR (audio gratuito) e crucipuzzle, con soluzioni.",
    "bundle": "Più materiali sullo stesso tema in un unico download."},
  "season_blurb": {
    "fall": "Zucche, vendemmia, foglie e feste d'autunno: schede per i mesi autunnali.",
    "winter": "Natale, neve, sport invernali e Capodanno: schede per la stagione fredda."},
  "n_items": "{n} materiali", "n_item": "1 materiale", "see_all": "Vedi tutti i {n} →", "more": "Mostra altri", "loading": "Caricamento …",
  "noresults": "Nessun materiale trovato: prova con un'altra parola o un altro filtro.",
  "by_subject": "Per tema", "by_subject_lead": "Tutte le schede di un'area in un'unica pagina.",
  "by_grade": "Per classe", "by_grade_lead": "Scegli una classe per vedere le schede adatte.",
  "grade": "Classe", "grades": "Classi", "grade_n": "{n}", "all_chip": "Tutti",
  "subject": "Tema", "pages": "Pagine", "format": "Formato", "type": "Tipo di materiale", "answer_key": "Soluzioni", "included": "Incluse",
  "price": "Prezzo", "free": "GRATIS",
  "btn_buy": "Vedi su TpT", "btn_buy_eduki": "Vedi su eduki", "related": "Materiali simili", "overview": "Pagine correlate",
  "click_note": "Ogni scheda apre la pagina del materiale; da lì il pulsante porta al negozio.",
  "faq_h": "Domande frequenti",
  "faq": [("Dove posso acquistare le schede?", "Le schede in italiano sono in vendita nel mio negozio “Snice” su eduki. Ogni pagina del materiale ha un pulsante che porta direttamente al prodotto."),
          ("Per quale classe?", "La classe indicata su eduki è riportata in ogni pagina del materiale. Il testo è scritto in un linguaggio chiaro e semplice."),
          ("Le soluzioni sono incluse?", "Sì, ogni scheda contiene le soluzioni."),
          ("In che formato?", "File PDF da stampare, senza preparazione."),
          ("Ci sono materiali in altre lingue?", "Sì: in “Altre lingue” trovi i miei materiali in inglese, spagnolo, francese e tedesco.")],
  "about_h": "Da un insegnante per gli insegnanti",
  "about_p": "Sono un insegnante in Germania e creo i materiali prima di tutto per i miei alunni. Ogni scheda viene controllata prima della pubblicazione, così prepari meno e insegni di più.",
  "other_title": "Materiali in altre lingue", "other_h1": "Altre lingue",
  "other_intro": "Questa pagina mostra solo materiali in italiano. Qui trovi i miei materiali in inglese, spagnolo, francese e tedesco.",
  "other_desc": "Materiali Snice in altre lingue: letture e cacce al tesoro in inglese e spagnolo, schede in francese e materiali in tedesco.",
  "lang_blurb": {"en": "Letture, cacce al tesoro di lettura e laboratori di matematica in inglese, disponibili su TpT.",
                 "es": "Letture e cacce al tesoro di lettura in spagnolo, disponibili su TpT.",
                 "fr": "Schede in francese con testo con spazi vuoti, ascolto e crucipuzzle, disponibili su eduki.",
                 "de": "Oltre {n} materiali in tedesco con soluzioni, disponibili su eduki.",
                 "it": ""},
  "to_lang": "Vai alla pagina in {l} →", "de_home": "Vai alla pagina in tedesco →",
  "all_title": "Tutte le schede in italiano: lettura, ascolto e crucipuzzle",
  "all_desc": "Cerca tra le {n} schede Snice in italiano per tema e classe: testo con spazi vuoti, comprensione all'ascolto e crucipuzzle, con soluzioni.",
  "all_intro": "Cerca un tema o filtra per area e classe. Ogni pagina del materiale porta direttamente al prodotto.",
  "new_title": "Nuove schede in italiano", "new_desc": "Le schede Snice più recenti in italiano, dalle più nuove.",
  "new_intro": "Qui compaiono per prime le mie schede più recenti. L'elenco si aggiorna automaticamente.",
  "season_title": {"fall": "Schede d'autunno in italiano", "winter": "Schede di Natale e d'inverno in italiano"},
  "season_desc": {"fall": "Schede d'autunno in italiano, pronte da stampare: zucca, vendemmia e feste d'autunno, con soluzioni.",
                  "winter": "Schede di Natale e d'inverno in italiano, pronte da stampare: Natale, neve e Capodanno, con soluzioni."},
  "fam_title": {"trails": "Cacce al tesoro di lettura", "rw": "Giochi di ruolo di matematica",
                "ws": "Schede di lettura: testo con spazi vuoti, ascolto e crucipuzzle", "bundle": "Pacchetti di materiali"},
  "subj_title": "Schede «{s}» in italiano", "subj_desc": "{n} schede in italiano sul tema «{s}», pronte da stampare e con soluzioni.",
  "grade_title": "Schede in italiano – {g}", "grade_desc": "{n} schede in italiano per la {g}, pronte da stampare e con soluzioni.",
  "crumb_home": "Home", "nav_label": "Navigazione principale", "lang_label": "Lingua",
  "foot_tag": "Materiali che rendono l'insegnamento più facile.",
  "foot_sold": "Le schede in italiano sono in vendita nel mio <a href=\"{store}\" rel=\"noopener\">negozio su eduki</a>.",
  "legal": "Note legali (in tedesco)", "privacy": "Privacy (in tedesco)",
  "home": "Home", "skip": "Vai al contenuto",
  "meta_ws": "Scheda di lettura", "meta_trail": "Caccia al tesoro di lettura", "meta_rw": "Gioco di ruolo di matematica", "meta_bundle": "Pacchetto", "meta_other": "Materiale",
 },
}
DE_T = {"other": "Andere Sprachen", "other_long": "Material in anderen Sprachen",
        "other_title": "Unterrichtsmaterial in anderen Sprachen: Englisch, Spanisch, Französisch, Italienisch",
        "other_desc": "Snice-Materialien in anderen Sprachen: englische und spanische Lesetexte und Lesespuren auf TpT, französische und italienische Arbeitsblätter auf eduki.",
        "other_intro": "Auf den deutschen Seiten stehen nur deutschsprachige Materialien. Hier findest du meine Materialien in Englisch, Spanisch, Französisch und Italienisch – jede Sprache hat eine eigene Seite.",
        "lang_blurb": {"en": "Englische Lesetexte, Lesespuren (Reading Trails) und Rechenwelten – erhältlich auf Teachers Pay Teachers.",
                       "es": "Spanische Lesetexte, Arbeitsblätter und Lesespuren (Búsquedas del tesoro) – erhältlich auf Teachers Pay Teachers.",
                       "fr": "Französische Arbeitsblätter mit Lückentext, Hörverstehen und Suchsel – erhältlich auf eduki.",
                       "it": "Italienische Arbeitsblätter mit Lückentext, Hörverstehen und Suchsel – erhältlich auf eduki."},
        "to_lang": "Zur Seite auf {l} →", "n_items": "{n} Materialien",
        "en_eduki": "Englische Arbeitsblätter für den Englischunterricht in Deutschland gibt es außerdem auf eduki: <a href=\"english-worksheets.html\">English Worksheets</a>."}

CATS = ["geo", "animals", "science", "history", "holidays", "music", "arts", "sports", "tech", "math", "language", "general"]
CAT_NAME = {
 "en": {"geo": "Geography", "animals": "Animals & Nature", "science": "Science & Health", "history": "History & Society",
        "holidays": "Holidays & Traditions", "music": "Music", "arts": "Art & Culture", "sports": "Sports", "tech": "Technology",
        "math": "Math", "language": "Language & Grammar", "general": "General Knowledge"},
 "es": {"geo": "Geografía", "animals": "Animales y naturaleza", "science": "Ciencias y salud", "history": "Historia y sociedad",
        "holidays": "Fiestas y tradiciones", "music": "Música", "arts": "Arte y cultura", "sports": "Deportes", "tech": "Tecnología",
        "math": "Matemáticas", "language": "Lengua", "general": "Cultura general"},
 "fr": {"geo": "Géographie", "animals": "Animaux et nature", "science": "Sciences et santé", "history": "Histoire et société",
        "holidays": "Fêtes et traditions", "music": "Musique", "arts": "Arts et culture", "sports": "Sport", "tech": "Technologie",
        "math": "Mathématiques", "language": "Langue", "general": "Culture générale"},
 "it": {"geo": "Geografia", "animals": "Animali e natura", "science": "Scienze e salute", "history": "Storia e società",
        "holidays": "Feste e tradizioni", "music": "Musica", "arts": "Arte e cultura", "sports": "Sport", "tech": "Tecnologia",
        "math": "Matematica", "language": "Lingua", "general": "Cultura generale"},
}
# DE-Fachseiten, die einem Themenbereich entsprechen (hreflang-Cluster), nur wenn die DE-Seite existiert
DE_CAT = {"geo": "erdkunde", "history": "geschichte", "music": "musik", "arts": "kunst", "sports": "sport", "math": "mathematik"}

SLUG = {
 "en": {"home": "index", "all": "resources", "new": "new", "fall": "fall-thanksgiving", "winter": "christmas-winter",
        "trails": "reading-trails", "rw": "math-role-plays", "ws": "reading-comprehension-worksheets", "bundle": "bundles",
        "other": "other-languages", "cat": "{c}", "grade": "grade-{g}", "free": "free"},
 "es": {"home": "index", "all": "recursos", "new": "novedades", "fall": "otono", "winter": "navidad-invierno",
        "trails": "busquedas-del-tesoro", "rw": "juegos-de-rol-matematicas", "ws": "fichas-de-lectura", "bundle": "paquetes",
        "other": "otros-idiomas", "cat": "{c}", "grade": "grado-{g}", "free": "gratis"},
 "fr": {"home": "index", "all": "ressources", "new": "nouveautes", "fall": "automne", "winter": "noel-hiver",
        "trails": "rallyes-lecture", "rw": "jeux-de-role-maths", "ws": "fiches-de-lecture", "bundle": "lots",
        "other": "autres-langues", "cat": "{c}", "grade": "niveau-{g}", "free": "gratuit"},
 "it": {"home": "index", "all": "risorse", "new": "novita", "fall": "autunno", "winter": "natale-inverno",
        "trails": "cacce-al-tesoro", "rw": "giochi-di-ruolo-matematica", "ws": "schede-di-lettura", "bundle": "pacchetti",
        "other": "altre-lingue", "cat": "{c}", "grade": "classe-{g}", "free": "gratis"},
}
DE_SLUG = {"home": "", "all": "materialien.html", "new": "neu.html", "fall": "herbst.html", "winter": "advent-winter.html",
           "trails": "lesespurgeschichten.html", "rw": "rechenwelten.html", "ws": "lueckentexte.html",
           "other": "material-in-anderen-sprachen.html", "free": "kostenlos.html"}

# ------------------------------------------------------------------ Klassifikation
KW = {
 "holidays": r"holiday|festival|celebrat|christmas|easter|halloween|thanksgiving|new year|carnival|tradition|hanukkah|kwanzaa|"
             r"fiesta|celebra|navidad|pascua|año nuevo|carnaval|tradici|día de (los )?muertos|reyes magos|"
             r"fête|célébr|noël|pâques|nouvel an|"
             r"festa|natale|pasqua|capodanno|carnevale|tradizion|befana",
 "music": r"music|instrument|song|orchestra|composer|piano|guitar|violin|drum|flute|trumpet|"
          r"música|canción|orquesta|compositor|guitarra|violín|tambor|"
          r"musique|chanson|orchestre|compositeur|violon|"
          r"musica|canzone|compositore|chitarra|violino",
 "sports": r"\bsport|football|soccer|tennis|basketball|baseball|hockey|olympic|athlet|swimming|skiing|"
           r"deporte|fútbol|tenis|baloncesto|olímpic|atleta|natación|"
           r"olympique|athlète|natation|calcio|pallacanestro|olimpic|nuoto",
 "math": r"\bmath|number|geometry|fraction|multiplication|division|measurement|"
         r"matemátic|número|geometría|fracci|multiplicaci|"
         r"mathémat|géométrie|multiplication|"
         r"matematic|numero|geometria|frazion|moltiplicazion",
 "animals": r"animal|species|mammal|\bbirds?\b|\bfish|insect|reptile|amphibian|\bplants?\b|\btrees?\b|flower|forest|"
            r"especie|mamífero|\baves?\b|\bpez\b|peces|insecto|reptil|planta|árbol|\bflor|bosque|"
            r"espèce|mammifère|oiseau|poisson|insecte|plante|arbre|fleur|forêt|"
            r"animale|specie|mammifero|uccell|pesce|insett|rettil|pianta|albero|fiore|foresta",
 "geo": r"\bcity\b|\btown\b|capital|country|district|\briver|mountain|island|\blake\b|region|\bstate of|village|located|municipality|continent|ocean|"
        r"ciudad|capital|\bpaís|\brío\b|montaña|\bisla\b|\blago\b|región|pueblo|situad|municipio|continente|océano|"
        r"\bville|capitale|\bpays\b|fleuve|rivière|montagne|\bîle\b|\blac\b|région|commune|arrondissement|situé|continent|océan|"
        r"città|\bpaese|fiume|montagna|\bisola|regione|\bcomune\b|situat|continente|oceano",
 "science": r"chemi|element|\batoms?\b|energy|planet|\bstars?\b|\bspace\b|\bbody\b|disease|health|\bcells?\b|physic|scien|medic|weather|climate|volcan|earthquake|"
            r"químic|átomo|energía|planeta|estrella|enfermedad|salud|célula|físic|científic|medicina|clima|volcán|terremoto|"
            r"chimi|atome|énergie|planète|étoile|maladie|santé|cellule|scientifique|médec|climat|séisme|"
            r"chimic|atomo|energia|pianeta|stella|malattia|salute|cellula|scienz|medic|clima|vulcano|terremoto",
 "history": r"\bwar\b|century|empire|\bking\b|queen|emperor|ancient|history|revolution|castle|medieval|dynasty|government|law|econom|\bbank|"
            r"guerra|siglo|imperio|\brey\b|reina|emperador|antigu|historia|revoluci|castillo|medieval|dinastía|gobierno|\bley\b|económ|banco|"
            r"guerre|siècle|empire|\broi\b|reine|empereur|antique|histoire|révolution|château|médiév|dynastie|gouvernement|\bloi\b|économ|banque|"
            r"secolo|impero|\bre\b|regina|imperatore|antic|storia|rivoluzion|castello|mediev|dinastia|governo|legge|economi|banca",
 "arts": r"\bart\b|\barts\b|painter|painting|sculpt|museum|architect|\bfilm|literature|\bpoet|writer|novel|theat|"
         r"\barte\b|pintor|pintura|escultur|museo|arquitect|literatura|poeta|escritor|novela|teatro|"
         r"peintre|peinture|musée|architect|littérature|poète|écrivain|roman|théâtre|"
         r"pittore|pittura|scultur|architett|letteratura|scrittore|romanzo",
 "tech": r"technolog|computer|internet|machine|invent|\bcars?\b|\btrains?\b|airplane|aircraft|robot|engine|digital|software|"
         r"tecnolog|computadora|ordenador|máquina|invento|\bcoche|\btren\b|avión|motor|"
         r"ordinateur|machine|voiture|avion|moteur|numérique|"
         r"macchina|invenzion|\bauto\b|treno|aereo|motore|digitale",
 "language": r"grammar|\bnoun|\bverb|adjective|preposition|pronoun|alphabet|"
             r"gramática|sustantivo|\bverbo|adjetivo|preposici|pronombre|"
             r"grammaire|\bverbe|adjectif|préposition|pronom|"
             r"grammatica|sostantivo|aggettivo|preposizion|pronome|alfabeto",
}
KW_RE = {k: re.compile(v, re.I) for k, v in KW.items()}
CAT_PRIO = ["holidays", "music", "sports", "math", "language", "animals", "geo", "science", "history", "arts", "tech"]
SUBJ_MAP = [(r"^music|instrumental", "music"), (r"geograph", "geo"), (r"history|economics|civics|government", "history"),
            (r"biology|environment", "animals"), (r"physical science|chemistry|physics|earth science|astronomy|health|general science|science", "science"),
            (r"physical education", "sports"), (r"art history|visual arts|^arts", "arts"),
            (r"engineering|computer|technology", "tech"), (r"math|geometry|measurement|fraction|multiplication", "math")]

SEASON_KW = {
 "fall": r"\bfall\b|autumn|thanksgiving|harvest|pumpkin|\bturkey\b|\bapples?\b|acorn|squirrel|halloween|"
         r"otoño|acción de gracias|cosecha|calabaza|manzana|ardilla|día de (los )?muertos|"
         r"automne|récolte|citrouille|potiron|châtaigne|écureuil|vendange|"
         r"autunno|vendemmia|zucca|castagn|scoiattolo",
 "winter": r"winter|christmas|gingerbread|\bsnow|\bice\b|icy|sled|\bski|skating|hanukkah|kwanzaa|new year|reindeer|polar bear|advent|"
           r"invierno|navidad|jengibre|nieve|hielo|año nuevo|reyes magos|reno\b|"
           r"hiver|noël|pain d'épices|neige|glace|nouvel an|avent|renne|"
           r"inverno|natale|pan di zenzero|neve|ghiaccio|capodanno|befana|avvento|renna",
}
SEASON_BLOCK = r"ice age|ice hockey sticks|fall of|waterfall|freefall|turkey \(|republic of turkey|iceland|eisstadt"
SEASON_RE = {k: re.compile(v, re.I) for k, v in SEASON_KW.items()}
SEASON_BLOCK_RE = re.compile(SEASON_BLOCK, re.I)
JUNK_RE = re.compile(r"^(couverture|copertina|portada|cover|deckblatt)\b|^(matériel pédagogique|materiale didattico|material didáctico)$", re.I)


def load_block():
    """Marken/Figuren/Politik/Sensibles: dieselben Sperrlisten wie der TpT-Uploader (Skripte/_tpt_batch.py)."""
    src = ""
    try:
        src = open(r"C:\Claude-Arbeitsblätter\Skripte\_tpt_batch.py", encoding="utf-8").read()
    except Exception:
        pass
    import ast
    found = {}
    try:
        for node in ast.parse(src).body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ("BLOCK", "BLOCK_TEASER"):
                arg = node.value.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    found[node.targets[0].id] = re.compile(arg.value, re.I)
    except Exception:
        pass
    pats = [found.get("BLOCK"), found.get("BLOCK_TEASER")]
    extra = re.compile(r"\b(yakari|asterix|obelix|simpson|spongebob|bob esponja|pok[eé]mon|disney|mickey|barbie|lego|minecraft|fortnite|"
                       r"harry potter|peppa|paw patrol|tintin|garfield|snoopy|looney|biene maja|winnie|pooh|superman|batman|marvel|"
                       r"mussolini|hitler|nazi|stalin|election|elecci[oó]n|élection|elezion|partido|parti politique|partito)\b", re.I)
    return pats[0], pats[1], extra


BLOCK_T, BLOCK_D, BLOCK_X = None, None, None


def blocked(title, text):
    for r in (BLOCK_T, BLOCK_X):
        if r is not None and r.search(title):
            return True
    return BLOCK_D is not None and BLOCK_D.search(text or "") is not None


def slugify(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:70].strip("-") or "resource"


def esc(s):
    return html.escape(s or "", quote=True)


def cat_of(topic, text, subjects=()):
    for s in subjects or ():
        for pat, c in SUBJ_MAP:
            if re.search(pat, s, re.I):
                return c
    score = collections.Counter()
    for k, r in KW_RE.items():
        score[k] += 3 * len(r.findall(topic or "")) + len(r.findall(text or ""))
    best = max(score.values()) if score else 0
    if best <= 0:
        return "general"
    return next(k for k in CAT_PRIO if score[k] == best)


def seasons_of(text, heute=None):
    if SEASON_BLOCK_RE.search(text or ""):
        return set()
    res = {k for k, r in SEASON_RE.items() if r.search(text or "")}
    d = heute or datetime.date.today()
    if "fall" in res and not (d.month == 10 or (d.month == 9 and d.day > 20)) and re.search(r"halloween|d[ií]a de (los )?muertos", text or "", re.I):
        res.discard("fall")   # Halloween nur im Oktober (wie DE ab 1.11. ohne Halloween)
    return res


def grade_nums_tpt(g):
    g = (g or "").replace("Kindergarten", "0").replace("PreK", "-1")
    ns = [int(x) for x in re.findall(r"-?\d+", g)]
    if not ns:
        return []
    lo, hi = min(ns), max(ns)
    return [n for n in range(max(lo, 0), min(hi, 12) + 1)] if hi - lo <= 12 else []


def grade_label(lang, nums):
    nums = [n for n in nums if n >= 1]
    if not nums:
        return ""
    a, b = nums[0], nums[-1]
    if lang == "es":
        return f"Grado {a}" if a == b else f"Grados {a}–{b}"
    return f"Grade {a}" if a == b else f"Grades {a}–{b}"


# ------------------------------------------------------------------ Items
def tpt_lang(d):
    """Materialsprache: zuerst Upload-Familie, sonst Titelmuster der Reihen (NICHT nur 'Spanish'/'French' im Titel:
    'French Revolution', 'Spanish flu' usw. sind englische Arbeitsblaetter)."""
    f, n = d.get("fam", ""), d.get("name", "")
    if f.startswith(("es", "lesespur_es")):
        return "es"
    if f == "fr":
        return "fr"
    if f in ("en", "inst_en") or f.startswith("lesespur_en"):
        return "en"
    if re.search(r"^Spanish\b.*(Passages|Comprehension|Scavenger|BUNDLE)|Spanish Reading|\(Ficha\)|Búsqueda del tesoro|Juego de rol", n):
        return "es"
    if re.search(r"Compréhension de lecture|Texte à trous|mots mêlés", n):
        return "fr"
    return "en"


def tpt_fam(d):
    n, f = d.get("name", "").lower(), d.get("fam", "")
    if d.get("bundle") or f == "bundle" or "bundle" in n:
        return "bundle"
    if "role play" in n or "juego de rol" in n or f.startswith("rw"):
        return "rw"
    if f.startswith("lesespur") or "scavenger hunt" in n or "búsqueda del tesoro" in n or "reading trail" in n:
        return "trails"
    if "cloze" in n or "(ficha)" in n or "texte à trous" in n or f in ("en", "es", "fr", "inst_en"):
        return "ws"
    return "other"


def first_quote(desc):
    m = re.search(r'From the text:\s*[“"](.+?)[”"]', desc or "")
    return m.group(1).strip() if m else ""


def story_title(desc):
    m = re.search(r'In\s+[“"](.+?)[,.]?[”"]', desc or "")
    return m.group(1).strip().rstrip(",.") if m else ""


def tpt_desc_html(desc):
    """TpT-Beschreibung (eigener Text) als Absaetze/Listen; Nutzungsbedingungen-Zeile weg."""
    out, ul = "", []
    lines = [x.strip() for x in (desc or "").split("\n") if x.strip()]
    lines = [x for x in lines if not re.match(r"(Terms of use|Thank you|Follow me|Please leave|Reviews?\b)", x, re.I)]
    for x in lines + [""]:
        if re.match(r"^[-•●▪]\s*", x):
            ul.append(re.sub(r"^[-•●▪]\s*", "", x)); continue
        if ul:
            out += "<ul>" + "".join(f"<li>{esc(li)}</li>" for li in ul) + "</ul>"; ul = []
        if x:
            out += f"<p>{esc(x)}</p>"
    return out


def es_ws_desc(topic, d):
    desc = d.get("desc") or ""
    gaps = re.search(r"\((\d+) gaps\)", desc)
    n_gaps = gaps.group(1) if gaps else None
    pages = d.get("pages")
    q = first_quote(desc)
    p = (f"<p>Ficha de lectura en español sobre «{esc(topic)}»: texto informativo con huecos y banco de palabras, "
         f"comprensión auditiva con código QR (audio MP3 gratuito, sin registro) y sopa de letras"
         + (f" ({pages} páginas, con solucionario)." if pages else ", con solucionario.") + "</p>")
    if q:
        p += f"<p>Del texto: «{esc(q)}»</p>"
    if pages == 5:
        p += ("<p><b>Contenido:</b></p><ul>"
              f"<li>Página 1: texto informativo sobre {esc(topic)} como texto con huecos y banco de palabras" + (f" ({n_gaps} huecos)" if n_gaps else "") + "</li>"
              "<li>Página 2: solucionario del texto con huecos</li>"
              "<li>Página 3: comprensión auditiva: escanear el código QR, escuchar la grabación en español, escribir un título, anotar tres datos y resumir lo escuchado en dos oraciones</li>"
              "<li>Página 4: sopa de letras" + (f" con las {n_gaps} palabras clave" if n_gaps else "") + "</li>"
              "<li>Página 5: solucionario de la sopa de letras</li></ul>")
    if "A2" in desc and "B1" in desc:
        p += "<p>Lenguaje claro y sencillo (aprox. nivel MCER A2–B1). Sin preparación: imprimir y usar. En blanco y negro, fácil de fotocopiar.</p>"
    else:
        p += "<p>Sin preparación: imprimir y usar.</p>"
    return p


def es_trail_desc(title_es, d):
    desc = d.get("desc") or ""
    pages = d.get("pages")
    p = ("<p>Búsqueda del tesoro de lectura en español, al estilo escape room en papel"
         + (f": «{esc(title_es)}»." if title_es else ".") + "</p>"
         "<p>El alumnado lee una estación breve en español, encuentra la pista que lleva al siguiente lugar, "
         "reúne una letra en cada estación correcta y ordena las letras para descubrir la palabra secreta. "
         "Los callejones sin salida permiten que cada estudiante compruebe su propio trabajo.</p>")
    facts = []
    if pages:
        facts.append(f"{pages} páginas")
    if re.search(r"answer key", desc, re.I):
        facts.append("con solucionario")
    if re.search(r"teacher (guide|notes|instructions)", desc, re.I):
        facts.append("con guía para el docente")
    if facts:
        p += "<p>" + esc(", ".join(facts)).capitalize() + ". Todo el material para el alumno está en español.</p>"
    return p


def tpt_item(d):
    name = (d.get("name") or "").replace("\ufffd", "–").strip()
    if not name:
        return None
    lang = tpt_lang(d); fam = tpt_fam(d)
    desc = d.get("desc") or d.get("desc_ld") or ""
    topic = re.split(r"\s+[–-]\s+", name)[0].strip() if fam == "ws" else name
    quote = first_quote(desc)
    if blocked(name, (quote or desc[:600])):
        return None
    nums = grade_nums_tpt(d.get("grades"))
    imgs = d.get("images") or []
    img = imgs[0] if imgs else ""
    title = name
    if lang == "es":
        if fam == "ws":
            title = f"{topic} – Ficha de lectura: texto con huecos, comprensión auditiva y sopa de letras"
            dh = es_ws_desc(topic, d)
        elif fam == "trails":
            st = story_title(desc)
            title = f"«{st}» – Búsqueda del tesoro de lectura" if st else name
            dh = es_trail_desc(st, d)
        else:
            dh = tpt_desc_html(desc)
    else:
        dh = tpt_desc_html(desc)
    text_cls = " ".join([quote, desc[:400] if fam != "ws" else ""])
    cat = cat_of(topic, text_cls, d.get("subjects"))
    if fam == "rw":
        cat = "math"
    seas = seasons_of(name + " " + (story_title(desc) if fam == "trails" else ""))
    price = d.get("price")
    try:
        pnum = float(price)
    except Exception:
        pnum = None
    return {"id": "t" + d["id"], "pid": d["id"], "lang": lang, "src": "tpt", "url": d.get("url"), "title": title, "name": name,
            "topic": topic, "fam": fam, "cat": cat, "grades": nums, "glabel": grade_label(lang, nums),
            "gkeys": [str(n) for n in nums if n >= 1], "season": seas, "date": (d.get("release") or "")[:10],
            "pnum": pnum, "cur": d.get("currency") or "USD", "img": img, "desc_html": dh,
            "meta_src": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(dh)))[:400],
            "pages": d.get("pages"), "subjects": d.get("subjects") or [], "answer": bool(re.search(r"answer key", desc, re.I)),
            "slug": slugify(topic if fam == "ws" else title)}


def eduki_item(m, lang):
    title = (m.get("title") or "").strip()
    if not title or JUNK_RE.search(title):
        return None
    desc = (m.get("desc") or "").strip()
    if blocked(title, desc[:600]):
        return None
    topic = re.split(r"\s+[–-]\s+(?:Fiche|Scheda)\b", title)[0].strip()
    cat = cat_of(topic, desc[:400])
    gl = [g for g in (m.get("grades") or []) if g]
    try:
        pnum = 0.0 if m.get("is_free") else float(m.get("price") or 0)
    except Exception:
        pnum = None
    fam = "ws" if re.search(r"fiche|scheda|texte à trous|spazi vuoti", title, re.I) else "other"
    return {"id": "e" + m["id"], "pid": m["id"], "lang": lang, "src": "eduki", "url": f"https://eduki.com/{lang}/{'materiale' if lang == 'it' else 'material'}/{m['id']}/{m.get('slug', '')}", "title": title, "name": title,
            "topic": topic, "fam": fam, "cat": cat, "grades": [], "glabel": ", ".join(gl[:3]),
            "gkeys": [slugify(g) for g in gl], "gnames": {slugify(g): g for g in gl},
            "season": seasons_of(topic), "date": (m.get("created") or "")[:10], "pnum": pnum, "cur": "EUR",
            "img": "", "eduki_cover": m.get("cover", ""), "desc_html": "".join(f"<p>{esc(x.strip())}</p>" for x in desc.split("\n") if x.strip()),
            "meta_src": desc[:400], "pages": None, "subjects": [], "answer": bool(re.search(r"corrig|soluzion", title + " " + desc, re.I)),
            "slug": slugify(topic)}


def load_items():
    global BLOCK_T, BLOCK_D, BLOCK_X
    BLOCK_T, BLOCK_D, BLOCK_X = load_block()
    out = {l: [] for l in FOREIGN}
    tp = os.path.join(B.OUT, "_tpt_live.json")
    if os.path.exists(tp):
        for d in json.load(open(tp, encoding="utf-8")).values():
            if d.get("live") and d.get("name"):
                it = tpt_item(d)
                if it and it["lang"] in out:
                    out[it["lang"]].append(it)
    ep = os.path.join(B.OUT, "_eduki_welten.json")
    if os.path.exists(ep):
        ew = json.load(open(ep, encoding="utf-8"))
        for lang in ("fr", "it"):
            for m in ew.get(lang) or []:
                it = eduki_item(m, lang)
                if it:
                    out[lang].append(it)
    for lang, items in out.items():
        seen, uniq = set(), []
        for it in sorted(items, key=lambda x: (x["date"], x["pid"]), reverse=True):
            k = (it["title"].lower(), it["src"])
            if k in seen:
                continue
            seen.add(k); uniq.append(it)
        for it in uniq:
            sub = "tpt" if it["src"] == "tpt" else lang   # 27.10.: alle Vorschauen lokal (kein Drittanbieter-Cookie)
            img_local = os.path.join(B.OUT, "thumbs-i18n", sub, it["pid"] + ".webp")
            it["img"] = f"thumbs-i18n/{sub}/{it['pid']}.webp" if os.path.exists(img_local) else ""
            it["path"] = f"p/{it['pid']}-{it['slug']}.html"
        out[lang] = uniq
    return out


# ------------------------------------------------------------------ Seiten-Grundgeruest
def lang_root(lang, depth=0):
    return "../" * depth


def site_root(depth):
    return "../" * (depth + 1)


def url_of(lang, slug):
    if lang == "de":
        return f"{SITE}/{slug}" if slug else f"{SITE}/"
    return f"{SITE}/{lang}/" if slug in ("", "index", "index.html") else f"{SITE}/{lang}/{slug}"


def cluster_urls(key):
    """lang -> absolute URL fuer einen Cluster (nur gebaute Seiten)."""
    res = {}
    for l in LANGS:
        if l == "de":
            s = de_slug_for(key)
            if s is not None:
                res["de"] = url_of("de", s)
        else:
            s = PAGES.get(l, {}).get(key)
            if s is not None:
                res[l] = url_of(l, s if s == "index" else s + ".html")
    return res if len(res) > 1 else {}


def de_slug_for(key):
    if key in DE_SLUG:
        return DE_SLUG[key]
    if key.startswith("cat:"):
        c = key[4:]
        if c in DE_CAT and ("fach-" + DE_CAT[c] + ".html") in STATS.get("de_pages", set()):
            return "fach-" + DE_CAT[c] + ".html"
    if key.startswith("grade:"):
        g = key[6:]
        if ("klasse-" + g + ".html") in STATS.get("de_pages", set()):
            return "klasse-" + g + ".html"
    return None


def xdefault(key, cu, fallback):
    """Startseite: x-default = deutsche Wurzel (waehlt die Sprache automatisch), sonst die englische Fassung."""
    if key == "home" and cu.get("de"):
        return cu["de"]
    return cu.get("en") or cu.get("de") or next(iter(cu.values()), fallback)


def hreflang_tags(key, self_lang, self_url):
    cu = cluster_urls(key) if key else {}
    if not cu:
        return f'<link rel="alternate" hreflang="{self_lang}" href="{self_url}">'
    tags = "".join(f'<link rel="alternate" hreflang="{l}" href="{u}">' for l, u in cu.items())
    xd = xdefault(key, cu, self_url)
    return tags + f'<link rel="alternate" hreflang="x-default" href="{xd}">'


SWITCH_JS = ("<script>(function(){var s=document.querySelectorAll('a[hreflang]');for(var i=0;i<s.length;i++)"
             "s[i].addEventListener('click',function(){try{localStorage.setItem('snice_lang',this.getAttribute('hreflang'))}catch(e){}});})();</script>")


def switcher(key, cur_lang, depth_rel):
    """depth_rel: Praefix vom aktuellen Dokument zur Website-Wurzel (z. B. '../')."""
    cu = cluster_urls(key) if key else {}
    a = ""
    for l in LANGS:
        if l != "de" and not ITEMS.get(l):
            continue
        u = cu.get(l) or url_of(l, "" if l == "de" else "index")
        rel = depth_rel + u.replace(SITE + "/", "")
        if rel.endswith("/") or rel == depth_rel:
            rel = rel or "./"
        cls = ' aria-current="true" class="on"' if l == cur_lang else ""
        a += f'<a href="{esc(rel or "./")}" hreflang="{l}" lang="{l}"{cls} title="{LANG_NAME[l]}">{l.upper()}</a>'
    return f'<nav class="langsw" aria-label="Sprache · Language">{a}</nav>'


LANG_CSS = """<style>
.langsw{display:flex;gap:2px;margin-left:12px;padding:3px;border:1px solid var(--line);border-radius:10px;background:var(--surface);flex:0 0 auto}
.langsw a{font-size:12px;font-weight:600;letter-spacing:.04em;padding:4px 7px;border-radius:7px;color:var(--muted);line-height:1.2}
.langsw a:hover{color:var(--text)}.langsw a.on{background:var(--text);color:var(--bg)}
.topnav .links+.langsw{margin-left:14px}
@media(max-width:980px){.langsw{margin-left:auto}.topnav .links{order:3}}
.langgrid{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.langcard{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:24px;box-shadow:var(--shadow)}
.langcard .code{display:inline-block;font-weight:700;font-size:13px;letter-spacing:.06em;padding:3px 9px;border-radius:8px;background:var(--text);color:var(--bg);margin-bottom:10px}
.langcard h3{margin:0 0 6px;font-size:21px}.langcard p{margin:0 0 12px;color:var(--muted)}
.mat-cover.small img{max-width:330px;margin:0 auto}
</style>"""


def head_i18n(lang, title, desc, url, key, depth, extra_ld=(), og_img="", robots="index,follow,max-image-preview:large"):
    root = site_root(depth)   # Praefix zur Website-Wurzel
    t = esc(title); d = esc(re.sub(r"\s+", " ", desc).strip())
    lds = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in extra_ld)
    return f"""<!doctype html>
<html lang="{lang}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{B.HTTPS_JS}
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
{hreflang_tags(key, lang, url)}
<meta name="robots" content="{robots}">
<meta property="og:type" content="website"><meta property="og:title" content="{t}"><meta property="og:description" content="{d}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{esc(og_img or SITE + '/assets/logo.png')}">
<meta property="og:locale" content="{OG_LOCALE[lang]}"><meta property="og:site_name" content="Snice">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#fbfbfd" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme:dark)">
{""}
<link rel="icon" type="image/png" href="{root}assets/logo.png">
<link rel="apple-touch-icon" href="{root}assets/logo.png">
<link rel="stylesheet" href="{root}assets/style.css">
<script>document.documentElement.className+=' js';</script>
{lds}
</head><body>
{topnav_i18n(lang, key, depth)}
"""


def topnav_i18n(lang, key, depth):
    t = T[lang]; pre = lang_root(lang, depth); P = PAGES.get(lang, {})
    links = [(P.get("all"), t["all"]), (P.get("free"), t["free_nav"])]
    for k in ("trails", "rw", "ws", "bundle"):
        if P.get(k):
            links.append((P[k], t.get(k + "_nav", t[k])))
    for s in season_now():
        if P.get(s):
            links.append((P[s], t[s])); break
    if P.get("new"):
        links.append((P["new"], t["new"]))
    links.append((P.get("other"), t["other"]))
    nav = "".join(f'<a href="{pre}{s}.html">{esc(n)}</a>' for s, n in links if s)
    store = TPT_STORE if lang in ("en", "es") else B.SHOP.replace("/de/", f"/{lang}/")
    return (f'<header class="topnav" id="topnav"><a class="brand" href="{pre}./" aria-label="Snice – {esc(t["home"])}">'
            f'<img src="{site_root(depth)}assets/logo-h.png" alt="Snice" width="303" height="97"></a>'
            f'<nav class="links" aria-label="{esc(t["nav_label"])}">{nav}<a href="{store}" rel="noopener">{esc(t["store"])}</a></nav>'
            f'{switcher(key, lang, site_root(depth))}</header>')


def foot_i18n(lang, depth):
    t = T[lang]; pre = lang_root(lang, depth); root = site_root(depth); P = PAGES.get(lang, {})
    store = TPT_STORE if lang in ("en", "es") else B.SHOP.replace("/de/", f"/{lang}/")
    cats = " · ".join(f'<a href="{pre}{P["cat:" + c]}.html">{esc(CAT_NAME[lang][c])}</a>' for c in CATS if P.get("cat:" + c))
    grades = " · ".join(f'<a href="{pre}{s}.html">{esc(n)}</a>' for k, (s, n, _o) in sorted(STATS.get("grade_pages", {}).get(lang, {}).items(), key=lambda kv: kv[1][2]))
    kinds = " · ".join(f'<a href="{pre}{P[k]}.html">{esc(t[k])}</a>' for k in ("all", "free", "trails", "rw", "ws", "bundle", "new", "fall", "winter", "other") if P.get(k))
    langs = " · ".join(f'<a href="{root}{"" if l == "de" else l + "/"}" hreflang="{l}" lang="{l}">{LANG_NAME[l]}</a>' for l in LANGS if l == "de" or ITEMS.get(l))
    return f"""<footer class="site">
<p class="big">Snice</p>
<p>{esc(t["foot_tag"])} {t["foot_sold"].format(store=store)}</p>
<div class="fcols"><div><h4>{esc(t["by_subject"])}</h4><p>{cats}</p></div><div><h4>{esc(t["by_grade"])}</h4><p>{grades}</p></div><div><h4>{esc(t["type"])}</h4><p>{kinds}</p></div></div>
<p>{langs}</p>
<p><a href="{root}impressum.html">{esc(t["legal"])}</a> · <a href="{root}datenschutz.html">{esc(t["privacy"])}</a></p>
</footer>
{B.NAV_SCRIPT}{SWITCH_JS}
</body></html>"""


WRITTEN = set()


def write(lang, slug, content):
    p = os.path.join(B.OUT, lang, slug.replace("/", os.sep) + ("" if slug.endswith((".html", ".json", ".xml")) else ".html"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(content)
    WRITTEN.add(os.path.normcase(p))


def season_now(heute=None):
    m = {"herbst": "fall", "advent-winter": "winter"}
    return [m[s] for s in B.saison_aktuell(heute)]


# ------------------------------------------------------------------ Karten / Grid
def img_of(it, depth):
    if not it.get("img"):
        return ""
    return it["img"] if it["img"].startswith("http") else site_root(depth) + it["img"]


def card(it, lang, depth=0):
    t = esc(it["title"]); pre = lang_root(lang, depth)
    meta = " · ".join(x for x in (CAT_NAME[lang].get(it["cat"], ""), it["glabel"]) if x)
    src = img_of(it, depth)
    img = (f'<div class="card-img"><img loading="lazy" decoding="async" src="{esc(src)}" alt="{t}" width="247" height="350"></div>'
           if src else f'<div class="card-img"><div class="ph">{esc(it["topic"])}</div></div>')
    return (f'<a class="card" href="{pre}{it["path"]}">{img}<div class="card-body"><h3>{t}</h3>'
            f'{f"<p class=card-meta>{esc(meta)}</p>" if meta else ""}</div></a>')


def keys_of(it):
    k = [f"c:{it['cat']}", f"t:{it['fam']}"] + [f"g:{g}" for g in it["gkeys"]] + [f"s:{s}" for s in sorted(it["season"])]
    return " " + " ".join(k) + " "


GRID_JS = """<script>
(function(){
 var g=document.getElementById('grid');if(!g)return;
 var q=document.getElementById('q'),cnt=document.getElementById('cnt'),nores=document.getElementById('nores'),more=document.getElementById('more');
 var SRC=g.getAttribute('data-src'),F=g.getAttribute('data-f')||'',PRE=g.getAttribute('data-pre')||'',ROOT=g.getAttribute('data-root')||'';
 var L=JSON.parse(g.getAttribute('data-l')),PAGE=48,all=null,view=null,shown=g.children.length,chip='',term='',busy=false,js=false;
 var qm=location.search.match(/[?&]q=([^&]+)/);
 if(qm&&q){try{q.value=decodeURIComponent(qm[1].replace(/\\+/g,' '));term=q.value.trim().toLowerCase();}catch(e){}}
 function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
 function card(m){var t=esc(m[0]),src=m[2]?(m[2].indexOf('http')===0?m[2]:ROOT+m[2]):'';
  var img=src?'<div class="card-img"><img loading="lazy" decoding="async" src="'+esc(src)+'" alt="'+t+'" width="247" height="350"></div>'
   :'<div class="card-img"><div class="ph">'+esc(m[5])+'</div></div>';
  return '<a class="card" href="'+esc(PRE+m[1])+'">'+img+'<div class="card-body"><h3>'+t+'</h3>'+(m[3]?'<p class="card-meta">'+esc(m[3])+'</p>':'')+'</div></a>';}
 function ok(m){return (!F||m[4].indexOf(' '+F+' ')>-1)&&(!chip||m[4].indexOf(' '+chip+' ')>-1)&&(!term||m[6].indexOf(term)>-1);}
 function show(reset){js=true;if(reset){g.innerHTML='';shown=0;view=all.filter(ok);}
  var h='',part=view.slice(shown,shown+PAGE);for(var i=0;i<part.length;i++)h+=card(part[i]);
  g.insertAdjacentHTML('beforeend',h);shown+=part.length;
  if(cnt)cnt.textContent=view.length===1?L.one:L.n.replace('{n}',view.length.toLocaleString(document.documentElement.lang));
  if(nores)nores.style.display=view.length?'none':'block';if(more)more.style.display=shown<view.length?'':'none';}
 function load(cb){if(all){cb();return;}if(busy)return;busy=true;if(more)more.textContent=L.loading;
  fetch(SRC).then(function(r){return r.json();}).then(function(d){all=d;busy=false;if(more)more.textContent=L.more;cb();})
  .catch(function(){busy=false;if(more)more.textContent=L.more;});}
 function apply(){load(function(){show(true);});}
 var tm;if(q)q.addEventListener('input',function(e){var v=e.target.value.trim().toLowerCase();clearTimeout(tm);tm=setTimeout(function(){term=v;apply();},200);});
 [].forEach.call(document.querySelectorAll('.chip[data-k]'),function(c){c.addEventListener('click',function(){chip=c.getAttribute('data-k');
  [].forEach.call(document.querySelectorAll('.chip[data-k]'),function(x){x.classList.toggle('on',x===c);});apply();});});
 if(more)more.addEventListener('click',function(){load(function(){show(!js);});});
 if(term)apply();
})();
</script>"""


def search_box(lang, form=False):
    t = T[lang]
    svg = ('<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"></circle>'
           '<path d="M21 21l-4.3-4.3"></path></svg>')
    if form:
        return (f'<form class="searchwrap" action="{PAGES[lang]["all"]}.html" method="get" role="search">{svg}'
                f'<input name="q" type="search" placeholder="{esc(t["search_ph"])}" autocomplete="off" aria-label="{esc(t["search_label"])}"></form>')
    return (f'<div class="searchwrap">{svg}<input id="q" type="search" placeholder="{esc(t["search_ph"])}" '
            f'autocomplete="off" aria-label="{esc(t["search_label"])}"></div>')


def chips(lang, items, kind):
    """kind 'g' = Klassen-Chips, 'c' = Themen-Chips."""
    t = T[lang]; c = collections.Counter()
    for it in items:
        for k in (it["gkeys"] if kind == "g" else [it["cat"]]):
            c[k] += 1
    if len(c) < 2:
        return ""
    if kind == "g":
        names = STATS["gnames"][lang]
        order = sorted(c, key=lambda k: names.get(k, (k, 0))[1])
        label = t["grade"]; disp = lambda k: names.get(k, (k, 0))[0]
    else:
        order = [k for k in CATS if k in c]; label = t["subject"]; disp = lambda k: CAT_NAME[lang][k]
    s = f'<button class="chip on" data-k="" type="button">{esc(t["all_chip"])}</button>'
    s += "".join(f'<button class="chip" data-k="{kind}:{esc(k)}" type="button">{esc(disp(k))}<span class="n">{c[k]}</span></button>' for k in order)
    return f'<div class="row"><span class="flabel">{esc(label)}</span>{s}</div>'


def breadcrumb_ld(crumbs):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}


def itemlist_ld(lang, name, items, limit=30):
    return {"@context": "https://schema.org", "@type": "ItemList", "name": name, "numberOfItems": len(items), "inLanguage": lang,
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": it["title"], "url": f"{SITE}/{lang}/{it['path']}"}
                                for i, it in enumerate(items[:limit])]}


def grid_page(lang, key, slug, title, h1, desc, intro, items, filt="", chip_kinds=("c", "g"), extra_html="", faq=None):
    t = T[lang]; url = url_of(lang, slug + ".html"); n = len(items)
    lds = [breadcrumb_ld([(t["crumb_home"], url_of(lang, "index")), (h1, url)]), itemlist_ld(lang, h1, items)]
    if faq:
        lds.append(faq_ld(faq))
    rows = "".join(chips(lang, items, k) for k in chip_kinds)
    filt_html = f'<div class="filters">{rows}</div>' if rows else ""
    lbl = json.dumps({"n": t["n_items"], "one": t["n_item"], "more": t["more"], "loading": t["loading"]}, ensure_ascii=False)
    more = (f'<p class="btnrow"><button class="btn ghost" id="more" type="button">{esc(t["more"])}</button></p>' if n > GRID_FIRST else "")
    out = head_i18n(lang, f"{title} | Snice", desc, url, key, 0, lds, og_img=items[0]["img"] if items and items[0]["img"].startswith("http") else "")
    out += f"""<main id="main" style="padding:0;max-width:none">
<section class="hero small">
<nav class="crumbs" aria-label="Breadcrumb"><a href="./">{esc(t["crumb_home"])}</a> › <span>{esc(h1)}</span></nav>
<h1>{esc(h1)}</h1>
<p class="sub">{esc(intro)}</p>
{search_box(lang)}
<p class="count"><span id="cnt">{esc(t["n_items"].format(n=f"{n:,}" if lang == "en" else f"{n:,}".replace(",", ".")) if n != 1 else t["n_item"])}</span></p>
</section>
{filt_html}
<div style="max-width:1240px;margin:0 auto;padding:38px 22px 40px">
{extra_html}
<div class="grid" id="grid" data-src="search-index.json" data-f="{esc(filt)}" data-pre="" data-root="../" data-l="{esc(lbl)}">
{"".join(card(it, lang) for it in items[:GRID_FIRST])}
</div>
{more}
<p class="noresults" id="nores">{esc(t["noresults"])}</p>
{faq_html(lang, faq) if faq else ""}
</div>
</main>
{GRID_JS}
""" + foot_i18n(lang, 0)
    write(lang, slug + ".html", out)
    PAGES[lang][key] = slug
    SITEMAP_URLS[lang].append((url, key))
    return n


def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def faq_html(lang, faq):
    return (f'<section class="section faq" style="padding-left:0;padding-right:0"><h2>{esc(T[lang]["faq_h"])}</h2>'
            + "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faq) + "</section>")


# ------------------------------------------------------------------ Seitenplanung (Slugs vor dem Rendern festlegen -> Navigation/Cluster)
def plan(lang):
    items = ITEMS[lang]; P = {"home": "index", "all": SLUG[lang]["all"], "other": SLUG[lang]["other"]}
    if items:
        P["new"] = SLUG[lang]["new"]
    if any(it["pnum"] == 0 for it in items):
        P["free"] = SLUG[lang]["free"]
    for s in ("fall", "winter"):
        if sum(1 for it in items if s in it["season"]) >= 4:
            P[s] = SLUG[lang][s]
    for f in ("trails", "rw", "ws", "bundle"):
        if sum(1 for it in items if it["fam"] == f) >= 3:
            P[f] = SLUG[lang][f]
    cc = collections.Counter(it["cat"] for it in items)
    for c in CATS:
        if cc[c] >= 6:
            P["cat:" + c] = slugify(CAT_NAME[lang][c])
    gc = collections.Counter(g for it in items for g in it["gkeys"])
    gp = {}
    names = {}
    for it in items:
        for i, g in enumerate(it["gkeys"]):
            if it["src"] == "tpt":
                names[g] = (T[lang]["grade_n"].format(n=g), int(g))
            else:
                nm = it["gnames"][g]
                names.setdefault(g, (nm, len(names)))
    STATS.setdefault("gnames", {})[lang] = names
    for g, n in gc.items():
        if n >= 6 and g in names:
            slug = SLUG[lang]["grade"].format(g=g)
            key = f"grade:{g}" if g.isdigit() else f"grade-{lang}:{g}"
            P[key] = slug
            gp[key] = (slug, names[g][0], names[g][1])
    STATS.setdefault("grade_pages", {})[lang] = gp
    PAGES[lang] = P


# ------------------------------------------------------------------ Startseite je Sprache
def hero(lang, items):
    t = T[lang]; n = len(items)
    nr = n // 100 * 100 if n >= 200 else n // 10 * 10
    seas = season_now()
    pool = [it for it in items if it.get("img") and seas and seas[0] in it["season"]]
    pool = sorted(pool, key=lambda x: ({"trails": 0, "rw": 0}.get(x["fam"], 1), -int(re.sub(r"\D", "", x["date"]) or 0)))
    if len(pool) < 5:
        pool += [it for it in items if it.get("img") and it not in pool][:5 - len(pool)]
    imgs = ""
    seen_t = set(); pool = [x for x in pool if not (x["topic"].lower() in seen_t or seen_t.add(x["topic"].lower()))]
    for k, it in enumerate(pool[:5]):
        load = 'fetchpriority="high"' if k == 0 else 'loading="lazy"'
        imgs += (f'<a class="c{k}" href="{it["path"]}"><img src="{esc(img_of(it, 0))}" alt="{esc(it["title"])}" '
                 f'width="247" height="350" {load} decoding="async"></a>')
    g_all = sorted({n_ for it in items for n_ in it["grades"] if n_ >= 1})
    if lang in ("en", "es"):
        g = f"{g_all[0]}–{g_all[-1]}" if g_all else ""
    else:
        g = " / ".join(sorted({it["glabel"] for it in items if it["glabel"]}, key=len)[:1])
    trust = [x.format(n=f"{nr:,}" if lang == "en" else f"{nr:,}".replace(",", "."), g=g) for x in t["trust"] if "{g}" not in x or g]
    ntr = sum(1 for it in items if it["fam"] == "trails")
    if t.get("trust_trails") and ntr >= 20:
        trust.insert(1, t["trust_trails"].format(n=ntr // 10 * 10))
    store = TPT_STORE if lang in ("en", "es") else B.SHOP.replace("/de/", f"/{lang}/")
    STATS.setdefault("grange", {})[lang] = g
    return f"""<section class="hero2{'' if imgs else ' noimg'}">
<div class="h2text">
<p class="eyebrow">{esc(t["eyebrow"])}</p>
<h1>{esc(t["h1a"])}<br><span>{esc(t["h1b"])}</span></h1>
<p class="sub">{esc(t["hero_sub"].format(n=f"{nr:,}" if lang == "en" else f"{nr:,}".replace(",", "."), g=g))}</p>
{search_box(lang, form=True)}
<p class="btnrow"><a class="btn" href="{store}" rel="noopener">{esc(t["btn_store"])}</a><a class="btn ghost" href="{PAGES[lang]["all"]}.html">{esc(t["btn_all"])}</a></p>
<ul class="trust">{"".join(f"<li>{x}</li>" for x in trust)}</ul>
</div>
<div class="collage">{imgs}</div>
</section>
""", nr


def sec(lang, h2, lead, href, items, n_all, k=8, tag=""):
    t = T[lang]
    ms = [it for it in items if it.get("img")][:k] or items[:k]
    more = f'<a class="more" href="{href}.html">{esc(t["see_all"].format(n=n_all))}</a>' if href else ""
    return (f'<section class="section">\n<div class="sec-head"><div>{f"<p class=tag-neu>{esc(tag)}</p>" if tag else ""}<h2>{esc(h2)}</h2>'
            f'<p class="lead">{esc(lead)}</p></div>\n{more}</div>\n<div class="grid grid-home">{"".join(card(it, lang) for it in ms)}</div>\n</section>\n')


def render_home(lang):
    t = T[lang]; items = ITEMS[lang]; P = PAGES[lang]
    hero_html, nr = hero(lang, items)
    body = hero_html
    body += '<section class="section tiles">' + "".join(f'<div class="tile"><h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for a, b in t["tiles"]) + "</section>\n"
    for s in season_now():
        if P.get(s):
            sel = sort_items([it for it in items if s in it["season"]])
            body += sec(lang, t[s], t["season_blurb"][s], P[s], sel, len(sel))
    if P.get("new"):
        body += sec(lang, t["new_long"], t["new_intro"], P["new"], newest(items), len(newest(items)), tag=t["new"])
    if P.get("free"):
        sel = sort_items([it for it in items if it["pnum"] == 0])
        body += sec(lang, t["free"], t["free_intro"], P["free"], sel, len(sel))
    for f in ("trails", "rw", "bundle", "ws"):
        if P.get(f):
            sel = sort_items([it for it in items if it["fam"] == f])
            body += sec(lang, t[f], t["fam_blurb"][f], P[f], sel, len(sel))
    cc = collections.Counter(it["cat"] for it in items)
    tiles = "".join(f'<a class="fach-tile" href="{P["cat:" + c]}.html"><span class="fname">{esc(CAT_NAME[lang][c])}</span>'
                    f'<span class="fn">{esc(t["n_items"].format(n=cc[c]))}</span></a>' for c in CATS if P.get("cat:" + c))
    body += (f'<section class="section"><div class="sec-head"><div><h2>{esc(t["by_subject"])}</h2><p class="lead">{esc(t["by_subject_lead"])}</p></div></div>'
             f'<div class="fachgrid">{tiles}</div></section>\n')
    gp = STATS["grade_pages"][lang]
    if gp:
        gcount = collections.Counter(g for it in items for g in it["gkeys"])
        ch = "".join(f'<a class="chip big" href="{s}.html">{esc(nm)}<span class="n">{gcount[k.split(":", 1)[1]]}</span></a>'
                     for k, (s, nm, o) in sorted(gp.items(), key=lambda kv: kv[1][2]))
        body += (f'<section class="section"><div class="sec-head"><div><h2>{esc(t["by_grade"])}</h2><p class="lead">{esc(t["by_grade_lead"])}</p></div></div>'
                 f'<div class="klassen">{ch}</div></section>\n')
    langs = other_lang_cards(lang, 0, k=0)
    body += (f'<section class="section"><div class="sec-head"><div><h2>{esc(t["other_h1"])}</h2><p class="lead">{esc(t["other_intro"])}</p></div>'
             f'<a class="more" href="{P["other"]}.html">{esc(t["other"])} →</a></div>{langs}</section>\n')
    body += f'<section class="section faq"><h2>{esc(t["faq_h"])}</h2>' + "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in t["faq"]) + "</section>\n"
    body += f'<section class="section about"><h2>{esc(t["about_h"])}</h2><p class="lead">{esc(t["about_p"])}</p></section>\n'
    url = url_of(lang, "index")
    org = {"@context": "https://schema.org", "@type": "Organization", "name": "Snice", "url": url, "logo": SITE + "/assets/logo.png",
           "sameAs": [TPT_STORE, B.SHOP, "https://www.instagram.com/snice.eduki/", "https://www.pinterest.de/sniceeduki/"]}
    site = {"@context": "https://schema.org", "@type": "WebSite", "name": "Snice", "url": url, "inLanguage": lang,
            "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": f"{SITE}/{lang}/{P['all']}.html?q={{search_term_string}}"},
                                "query-input": "required name=search_term_string"}}
    out = head_i18n(lang, t["home_title"], t["home_desc"].format(n=f"{nr:,}" if lang == "en" else f"{nr:,}".replace(",", "."), g=STATS["grange"].get(lang, "")), url, "home", 0,
                    [site, org, faq_ld(t["faq"])])
    out += f'<main id="main" style="padding:0;max-width:none">{body}</main>\n' + foot_i18n(lang, 0)
    write(lang, "index.html", out)
    SITEMAP_URLS[lang].append((url, "home"))


def sort_items(items):
    return sorted(items, key=lambda x: (0 if x.get("img") else 1, {"trails": 0, "rw": 0, "bundle": 1, "ws": 2}.get(x["fam"], 3), -dnum(x)))


def dnum(x):
    return int(re.sub(r"\D", "", x.get("date") or "") or 0)


def newest(items, k=48):
    return sorted(items, key=lambda x: (x["date"], x["pid"]), reverse=True)[:k]


# ------------------------------------------------------------------ "Other languages"
def other_lang_cards(lang, depth, k=4):
    root = site_root(depth); h = ""
    blurbs = T[lang]["lang_blurb"] if lang != "de" else DE_T["lang_blurb"]
    for l in LANGS:
        if l == lang or (l != "de" and not ITEMS.get(l)):
            continue
        if l == "de":
            n = len(B.katalog_de())
            blurb = blurbs.get("de", "").format(n=f"{n // 100 * 100:,}".replace(",", "." if lang != "en" else ","))
            href = root
            cnt = ""
        else:
            n = len(ITEMS[l]); blurb = blurbs.get(l, "")
            href = f"{root}{l}/"
            cnt = (DE_T["n_items"] if lang == "de" else T[lang]["n_items"]).format(n=f"{n:,}".replace(",", "." if lang != "en" else ","))
        to = (DE_T["to_lang"] if lang == "de" else T[lang]["to_lang"]).format(l=LANG_NAME[l])
        sample = ""
        if k and l != "de":
            pick = [it for it in sort_items(ITEMS[l]) if it.get("img")][:k]
            sample = '<div class="grid grid-home" style="margin-top:14px">' + "".join(
                card_abs(it, l, root) for it in pick) + "</div>"
        h += (f'<div class="langcard" lang="{l}"><span class="code">{l.upper()}</span><h3>{LANG_NAME[l]}</h3>'
              f'<p>{esc(blurb)}{(" · " + esc(cnt)) if cnt else ""}</p><a class="more" href="{href}" hreflang="{l}">{esc(to)}</a>{sample}</div>')
    return f'<div class="langgrid">{h}</div>'


def card_abs(it, lang, root):
    """Karte einer anderen Sprache (Link in deren Bereich)."""
    t = esc(it["title"]); src = it["img"] if it["img"].startswith("http") else root + it["img"]
    meta = " · ".join(x for x in (CAT_NAME[lang].get(it["cat"], ""), it["glabel"]) if x)
    return (f'<a class="card" href="{root}{lang}/{it["path"]}" hreflang="{lang}" lang="{lang}"><div class="card-img">'
            f'<img loading="lazy" decoding="async" src="{esc(src)}" alt="{t}" width="247" height="350"></div>'
            f'<div class="card-body"><h3>{t}</h3><p class="card-meta">{esc(meta)}</p></div></a>')


def render_other(lang):
    t = T[lang]; slug = PAGES[lang]["other"]; url = url_of(lang, slug + ".html")
    out = head_i18n(lang, f'{t["other_title"]} | Snice', t["other_desc"], url, "other", 0,
                    [breadcrumb_ld([(t["crumb_home"], url_of(lang, "index")), (t["other_h1"], url)])])
    out += (f'<main id="main"><nav class="crumbs"><a href="./">{esc(t["crumb_home"])}</a> › <span>{esc(t["other_h1"])}</span></nav>'
            f'<h1 style="font-size:clamp(30px,5vw,46px);letter-spacing:-.03em;margin:8px 0 6px">{esc(t["other_h1"])}</h1>'
            f'<p class="lead" style="color:var(--muted);max-width:760px">{esc(t["other_intro"])}</p>'
            f'<div style="margin-top:26px">{other_lang_cards(lang, 0, k=4)}</div></main>') + foot_i18n(lang, 0)
    write(lang, slug + ".html", out)
    SITEMAP_URLS[lang].append((url, "other"))


def render_other_de():
    """DE: material-in-anderen-sprachen.html (im Stil der deutschen Seiten)."""
    slug = "material-in-anderen-sprachen"; url = f"{SITE}/{slug}.html"
    out = B.head(DE_T["other_title"], DE_T["other_desc"], url, "", extra_ld=[B.breadcrumb_ld([("Start", SITE + "/"), (DE_T["other_long"], url)])])
    out += (f'<main><nav class="crumbs"><a href="index.html">Start</a> › <span>{DE_T["other_long"]}</span></nav>'
            f'<h1 style="font-size:clamp(30px,5vw,46px);letter-spacing:-.03em;margin:8px 0 6px">{DE_T["other_long"]}</h1>'
            f'<p class="lead" style="color:var(--muted);max-width:760px">{esc(DE_T["other_intro"])}</p>'
            f'<div style="margin-top:26px">{other_lang_cards("de", -1, k=4)}</div>'
            f'<p style="margin-top:30px;color:var(--muted)">{DE_T["en_eduki"]}</p></main>') + B.foot()
    open(os.path.join(B.OUT, slug + ".html"), "w", encoding="utf-8").write(out)
    B.EXTRA_URLS.append(url)


# ------------------------------------------------------------------ DE: Kostenloses Unterrichtsmaterial (27.10., Nutzer-OK)
FREE_DE_FAQ = [
    ("Sind die Materialien wirklich kostenlos?", "Ja. Auf dieser Seite stehen nur Materialien, die bei der täglichen Aktualisierung auf eduki 0 € kosten. Ändert sich das, verschwindet das Material automatisch von dieser Seite."),
    ("Wie lade ich ein Material herunter?", "Klick auf das Material: Auf der Detailseite führt dich der Button direkt zum Material auf eduki. Dort startest du den Download."),
    ("Sind Lösungen dabei?", "Die meisten Materialien enthalten eine Musterlösung. Was genau enthalten ist, steht in der Beschreibung des jeweiligen Materials."),
    ("Für welche Klassen gibt es kostenloses Material?", "Die Übersicht ist nach Fach gruppiert und innerhalb des Fachs nach Klasse sortiert. Über die Klassen-Filter oben siehst du nur das Material deiner Klassenstufe."),
]
FREE_JS = """<script>(function(){[].forEach.call(document.querySelectorAll('.card'),function(c){c.classList.add('in');});var cs=document.querySelectorAll('.chip[data-kl]');[].forEach.call(cs,function(c){c.addEventListener('click',function(){
var v=c.getAttribute('data-kl');[].forEach.call(cs,function(x){x.classList.toggle('on',x===c);});
[].forEach.call(document.querySelectorAll('.fsec'),function(s){var n=0;[].forEach.call(s.querySelectorAll('.card'),function(k){
var ok=!v||(k.getAttribute('data-kl')||'').indexOf(','+v+',')>-1;k.style.display=ok?'':'none';if(ok)n++;});s.style.display=n?'':'none';});});});})();</script>"""


def free_de_mats():
    return [m for m in B.katalog_de() if B.is_free(m)]


def render_free_de():
    """kostenlos.html: alle aktuell kostenlosen deutschen eduki-Materialien, gruppiert nach Fach, sortiert nach Klasse."""
    mats = free_de_mats()
    if not mats:
        return 0
    slug = "kostenlos"; url = f"{SITE}/{slug}.html"
    by_f = collections.defaultdict(list)
    for m in mats:
        by_f[m.get("fach") or "Fachübergreifend"].append(m)
    kl_c = collections.Counter(n for m in mats for n in B.grade_nums(m.get("grades")))
    chips = ('<div class="filters"><div class="row"><span class="flabel">Klasse</span><button class="chip on" data-kl="" type="button">Alle</button>'
             + "".join(f'<button class="chip" data-kl="{n}" type="button">{n}. Kl.<span class="n">{kl_c[n]}</span></button>' for n in sorted(kl_c))
             + "</div></div>") if len(kl_c) > 1 else ""
    order = sorted(by_f.items(), key=lambda kv: -len(kv[1]))
    nav = " · ".join(f'<a href="#{B.slugify(f)}">{html.escape(f)} ({len(v)})</a>' for f, v in order)
    secs = ""
    for f, ms in order:
        ms = sorted(ms, key=lambda m: ((B.grade_nums(m.get("grades")) or [99])[0], -int(m["id"])))
        secs += (f'<section class="fsec" id="{B.slugify(f)}"><h2 style="font-size:clamp(24px,3vw,32px);letter-spacing:-.02em;margin:40px 0 16px">'
                 f'Kostenloses Material {html.escape(f)}</h2><div class="grid">{"".join(B.cat_card_html(m) for m in ms)}</div></section>')
    lines = collections.Counter(m.get("line") for m in mats)
    extra = [f"{lines[k]} {w}" for k, w in (("lesespur", "Lesespurgeschichten"), ("lueckentext", "Lückentexte mit Hörverstehen"),
                                             ("pt", "Prüfungstrainings"), ("basteln", "Bastelvorlagen"), ("rechenwelt", "Rechenwelten"),
                                             ("lesespaziergang", "Lesespaziergänge")) if lines.get(k)]
    gs = sorted(kl_c)
    if gs:
        intro = (f"{len(mats)} Unterrichtsmaterialien gibt es auf eduki aktuell kostenlos – Arbeitsblätter zum Ausdrucken für "
                 f"Klasse {gs[0]} bis {gs[-1]}" + (f", darunter {', '.join(extra)}" if extra else "") + ". "
                 "Nach Fach gruppiert, innerhalb des Fachs nach Klasse sortiert. Die Liste aktualisiert sich täglich.")
    else:
        intro = f"{len(mats)} Unterrichtsmaterialien gibt es auf eduki aktuell kostenlos. Die Liste aktualisiert sich täglich."
    title = "Kostenloses Unterrichtsmaterial zum Ausdrucken"
    desc = (f"{len(mats)} kostenlose Arbeitsblätter und Unterrichtsmaterialien zum Ausdrucken, nach Fach und Klasse sortiert – "
            "für Grundschule und Sekundarstufe, täglich aktualisiert.")
    lds = [B.breadcrumb_ld([("Start", SITE + "/"), ("Kostenlos", url)]), B.itemlist_ld("Kostenloses Unterrichtsmaterial", mats),
           B.faq_ld_of(FREE_DE_FAQ)]
    out = B.head(title, desc, url, mats[0].get("cover", ""), extra_ld=lds)
    ed = B.editorial_block([("Kostenlose Arbeitsblätter mit Lösungen", [
        "Alle Materialien auf dieser Seite sind fertige PDFs zum Ausdrucken, die du ohne Vorbereitung im Unterricht einsetzen kannst – "
        "für die Grundschule genauso wie für die Sekundarstufe. Weitere Materialien findest du in der <a href=\"materialien.html\">Materialsuche</a>, "
        "bei den <a href=\"lesespurgeschichten.html\">Lesespurgeschichten</a> oder nach Saison, z. B. <a href=\"herbst.html\">Herbst</a> "
        "und <a href=\"advent-winter.html\">Advent &amp; Winter</a>."])], FREE_DE_FAQ)
    out += f"""<section class="hero small">
<nav class="crumbs" aria-label="Navigationspfad"><a href="index.html">Start</a> › <span>Kostenlos</span></nav>
<h1>Kostenloses Unterrichtsmaterial</h1>
<p class="sub">{html.escape(intro)}</p>
<p class="count">{nav}</p>
</section>
{chips}
<main>
{secs}
{ed}
</main>
{FREE_JS}
""" + B.foot()
    open(os.path.join(B.OUT, slug + ".html"), "w", encoding="utf-8").write(out)
    B.EXTRA_URLS.append(url)
    return len(mats)


def free_de_home():
    """Startseiten-Abschnitt (Hook I18N_FREE_HOME in build.render_index)."""
    mats = free_de_mats()
    if not mats:
        return ""
    ms = [m for m in B.sort_mats(mats) if m.get("cover")][:4] or B.sort_mats(mats)[:4]
    return (f'<section class="section">\n<div class="sec-head"><div><h2>Kostenloses Unterrichtsmaterial</h2>'
            f'<p class="lead">{len(mats)} Materialien gibt es auf eduki aktuell kostenlos – nach Fach und Klasse sortiert.</p></div>\n'
            f'<a class="more" href="kostenlos.html">Alle {len(mats)} ansehen →</a></div>\n'
            f'<div class="grid grid-home">{"".join(B.cat_card_html(m) for m in ms)}</div>\n</section>\n')


# ------------------------------------------------------------------ Detailseiten
def price_html(it, lang):
    t = T[lang]
    if it["pnum"] is None:
        return ""
    if it["pnum"] == 0:
        return t["free"]
    if it["cur"] == "USD":
        return f"${it['pnum']:.2f}" if lang == "en" else f"US$ {it['pnum']:.2f}"
    return f"{it['pnum']:.2f} €".replace(".", ",")


def render_detail(lang, it, related):
    t = T[lang]; P = PAGES[lang]; url = f"{SITE}/{lang}/{it['path']}"
    btn = t["btn_buy"] if it["src"] == "tpt" else t["btn_buy_eduki"]
    md = re.sub(r"\s+", " ", it["meta_src"]).strip()
    md = (md[:155].rsplit(" ", 1)[0] + " …") if len(md) > 158 else md
    cat_slug = P.get("cat:" + it["cat"])
    fam_slug = P.get(it["fam"])
    crumbs = [(t["crumb_home"], url_of(lang, "index"))]
    crumb_html = f'<nav class="crumbs"><a href="../">{esc(t["crumb_home"])}</a>'
    if cat_slug:
        crumbs.append((CAT_NAME[lang][it["cat"]], url_of(lang, cat_slug + ".html")))
        crumb_html += f' › <a href="../{cat_slug}.html">{esc(CAT_NAME[lang][it["cat"]])}</a>'
    if fam_slug:
        crumb_html += f' › <a href="../{fam_slug}.html">{esc(t[it["fam"]])}</a>'
    crumbs.append((it["title"], url)); crumb_html += "</nav>"
    img = img_of(it, 1)
    abs_img = it["img"] if it["img"].startswith("http") else (f"{SITE}/{it['img']}" if it["img"] else f"{SITE}/assets/logo.png")
    offer = {"@type": "Offer", "url": it["url"], "availability": "https://schema.org/InStock"}
    if it["pnum"] is not None:
        offer.update({"price": f"{it['pnum']:.2f}", "priceCurrency": it["cur"]})
    prod = {"@context": "https://schema.org", "@type": "Product", "name": it["title"], "description": md, "image": abs_img,
            "url": url, "sku": it["pid"], "brand": {"@type": "Brand", "name": "Snice"}, "inLanguage": lang,
            "category": CAT_NAME[lang][it["cat"]], "offers": offer}
    typ = t.get("meta_" + ("trail" if it["fam"] == "trails" else it["fam"]), t["meta_other"])
    facts = [(t["subject"], CAT_NAME[lang][it["cat"]]), (t["grades"], it["glabel"]), (t["type"], typ)]
    if it.get("pages"):
        facts.append((t["pages"], str(it["pages"])))
    facts.append((t["format"], "PDF"))
    if it.get("answer"):
        facts.append((t["answer_key"], t["included"]))
    facts_html = "".join(f"<div><b>{esc(a)}</b>{esc(b)}</div>" for a, b in facts if b)
    cover = (f'<div class="mat-cover small"><img src="{esc(img)}" alt="{esc(it["title"])}" '
             f'width="{247 if it["src"] == "tpt" else 280}" height="{350 if it["src"] == "tpt" else 396}"></div>') if img else ""
    links = [f'<a href="../{cat_slug}.html">{esc(CAT_NAME[lang][it["cat"]])}</a>'] if cat_slug else []
    for k, (s, nm, o) in sorted(STATS["grade_pages"][lang].items(), key=lambda kv: kv[1][2]):
        if k.split(":", 1)[1] in it["gkeys"]:
            links.append(f'<a href="../{s}.html">{esc(nm)}</a>')
    if fam_slug:
        links.append(f'<a href="../{fam_slug}.html">{esc(t[it["fam"]])}</a>')
    body = f"""{B.MAT_CSS}
<main class="mat" id="main">
{crumb_html}
<div class="mat-top">
{cover}
<div>
<h1>{esc(it["title"])}</h1>
<p class="meta">{esc(" · ".join(x for x in (CAT_NAME[lang][it["cat"]], it["glabel"], typ) if x))}</p>
<div class="buy"><span class="price">{esc(price_html(it, lang))}</span><a class="btn" href="{esc(it["url"])}" rel="noopener">{esc(btn)}</a></div>
<div class="desc">{it["desc_html"]}</div>
<div class="facts">{facts_html}</div>
<p class="meta">{esc(t["overview"])}: {" · ".join(links)}</p>
</div>
</div>
{f'<h2>{esc(t["related"])}</h2><div class="grid">' + "".join(card(r, lang, 1) for r in related) + "</div>" if related else ""}
</main>
"""
    out = head_i18n(lang, f'{it["title"][:70]} | Snice', md or it["title"], url, None, 1, [prod, breadcrumb_ld(crumbs)], og_img=abs_img)
    write(lang, it["path"], out + body + foot_i18n(lang, 1))
    SITEMAP_URLS[lang].append((url, None))


def render_details(lang):
    items = ITEMS[lang]
    by_cat = collections.defaultdict(list)
    for it in items:
        by_cat[(it["cat"], it["fam"])].append(it)
    for it in items:
        cands = [x for x in by_cat[(it["cat"], it["fam"])] if x is not it]
        gs = set(it["gkeys"])
        cands.sort(key=lambda x: (0 if gs & set(x["gkeys"]) else 1, 0 if x.get("img") else 1, -dnum(x)))
        rel = [x for x in cands if x.get("img")][:8] or cands[:8]
        render_detail(lang, it, rel)
    keep = {os.path.normcase(os.path.join(B.OUT, lang, it["path"].replace("/", os.sep))) for it in items}
    for f in glob.glob(os.path.join(B.OUT, lang, "p", "*.html")):
        if os.path.normcase(f) not in keep:
            os.remove(f)


def write_index(lang):
    t = T[lang]
    idx = []
    for it in sort_items(ITEMS[lang]):
        meta = " · ".join(x for x in (CAT_NAME[lang].get(it["cat"], ""), it["glabel"]) if x)
        img = it["img"]
        s = " ".join([it["title"], it["topic"], meta, it["meta_src"][:120]]).lower()
        idx.append([it["title"], it["path"], img, meta, keys_of(it), it["topic"], s])
    write(lang, "search-index.json", json.dumps(idx, ensure_ascii=False, separators=(",", ":")))


# ------------------------------------------------------------------ Sitemaps
def write_sitemaps():
    """Je Sprache <lang>/sitemap.xml mit xhtml:link-Alternates; lastmod = Datum der letzten Inhaltsaenderung
    (Hash der Seite ohne Datums-/Zufallsanteile, Zustand _lastmod_i18n.json)."""
    import hashlib
    files = []
    today = datetime.date.today().isoformat()
    lp = os.path.join(B.OUT, "_lastmod_i18n.json")
    try:
        lm = json.load(open(lp, encoding="utf-8"))
    except Exception:
        lm = {}
    for lang in FOREIGN:
        if not SITEMAP_URLS.get(lang):
            continue
        rows = []
        for u, key in SITEMAP_URLS[lang]:
            rel = u.replace(f"{SITE}/{lang}/", "") or "index.html"
            try:
                h = hashlib.md5(open(os.path.join(B.OUT, lang, rel.replace("/", os.sep)), "rb").read()).hexdigest()[:12]
            except OSError:
                h = ""
            e = lm.get(u)
            if not e or e[0] != h:
                lm[u] = e = [h, today]
            alts = cluster_urls(key) if key else {}
            x = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{a}"/>' for l, a in alts.items())
            if alts:
                x += f'<xhtml:link rel="alternate" hreflang="x-default" href="{xdefault(key, alts, u)}"/>'
            rows.append(f"<url><loc>{u}</loc><lastmod>{e[1]}</lastmod>{x}</url>")
        open(os.path.join(B.OUT, lang, "sitemap.xml"), "w", encoding="utf-8").write(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>")
        files.append(f"{lang}/sitemap.xml")
    json.dump(lm, open(lp, "w", encoding="utf-8"), separators=(",", ":"))
    return files, today


def de_sitemap_alternates(url):
    key = DE_CLUSTER.get(url)
    alts = cluster_urls(key) if key else {}
    if not alts:
        return ""
    return ("".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{a}"/>' for l, a in alts.items())
            + f'<xhtml:link rel="alternate" hreflang="x-default" href="{xdefault(key, alts, url)}"/>')


# ------------------------------------------------------------------ DE-Seiten: Hooks fuer build.py
AUTO_JS = """<script>
(function(){try{
 var ua=navigator.userAgent||'';
 if(navigator.webdriver||/bot|crawl|spider|slurp|lighthouse|headless|google|bing|yandex|baidu|duckduck|facebookexternalhit|preview|pagespeed/i.test(ua))return;
 var L=(navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||'']).map(function(x){return String(x).toLowerCase();});
 var p=L[0]||'',b=p.slice(0,2),A=AVAIL;
 function go(l){if(l&&l!=='de'&&A.indexOf(l)>-1)location.replace('/'+l+'/');}
 var S=null;try{S=localStorage.getItem('snice_lang');}catch(e){}
 if(S){go(S);return;}
 var DACH=['DE','AT','CH','LI','LU'],FRC=['FR','BE','MC'],ITC=['IT','SM','VA'],
     ESC=['ES','MX','AR','CO','CL','PE','VE','EC','GT','CU','BO','DO','HN','PY','SV','NI','CR','PA','UY','PR','GQ'];
 function decide(cc){
  if(DACH.indexOf(cc)>-1){if(b==='fr'||b==='it')return b;return 'de';}
  if(b==='de')return 'de';
  if(b==='fr'||b==='it'||b==='es')return b;
  if(FRC.indexOf(cc)>-1)return 'fr';if(ITC.indexOf(cc)>-1)return 'it';if(ESC.indexOf(cc)>-1)return 'es';
  if(b==='en'||cc)return 'en';
  return 'de';}
 var done=false,t=setTimeout(function(){if(done)return;done=true;
   if(b==='de')return;
   if(b==='fr'||b==='it'||b==='es')return go(b);
   if(b==='en'&&/^en-(us|gb|ca|au|nz|ie|za|in)/.test(p))return go('en');},900);
 fetch('/cdn-cgi/trace',{cache:'no-store'}).then(function(r){return r.text();}).then(function(x){
   if(done)return;done=true;clearTimeout(t);var m=x.match(/\\nloc=([A-Z]{2})/);go(decide(m?m[1]:''));
 }).catch(function(){});
}catch(e){}})();
</script>"""


def de_head_extra(url):
    """Wird von build.head() fuer jede deutsche Seite aufgerufen."""
    key = DE_CLUSTER.get(url)
    tags = ""
    if key:
        cu = cluster_urls(key)
        if cu:
            tags = "".join(f'<link rel="alternate" hreflang="{l}" href="{u}">' for l, u in cu.items())
            tags += f'<link rel="alternate" hreflang="x-default" href="{xdefault(key, cu, url)}">'
    if url == SITE + "/":
        avail = json.dumps([l for l in FOREIGN if ITEMS.get(l)])
        tags += AUTO_JS.replace("AVAIL", avail)
    return tags


def de_switcher(url, root):
    return switcher(DE_CLUSTER.get(url), "de", root)


# ------------------------------------------------------------------ Einstieg
def prepare(build_module):
    """Vor dem Rendern der deutschen Seiten: Daten laden, Seiten planen, DE-Cluster setzen."""
    global B
    B = build_module
    ITEMS.clear(); PAGES.clear(); DE_CLUSTER.clear(); SITEMAP_URLS.clear()
    ITEMS.update(load_items())
    de_k = B.katalog_de()
    fach_c = collections.Counter(m["fach"] for m in de_k if m.get("fach"))
    kl_c = collections.Counter(n for m in de_k for n in B.grade_nums(m.get("grades")))
    de_pages = {B.fach_slug(f) + ".html" for f, n in fach_c.items() if n >= 10} | {f"klasse-{n}.html" for n, c in kl_c.items() if c >= 10}
    STATS["de_pages"] = de_pages
    for lang in FOREIGN:
        SITEMAP_URLS[lang] = []
        if ITEMS[lang]:
            plan(lang)
        else:
            PAGES[lang] = {}
    keys = set(DE_SLUG)
    for lang in FOREIGN:
        keys |= set(PAGES[lang])
    for key in keys:
        s = de_slug_for(key)
        if s is not None and cluster_urls(key):
            DE_CLUSTER[url_of("de", s)] = key
    B.I18N_HEAD = de_head_extra
    B.I18N_SWITCH = de_switcher
    B.I18N_SITEMAP_ALT = de_sitemap_alternates
    B.I18N_FREE_HOME = free_de_home
    return {l: len(v) for l, v in ITEMS.items()}


def render():
    """Nach den deutschen Seiten: alle Sprachseiten + DE-Seite 'Material in anderen Sprachen'. Liefert Sitemap-Dateien."""
    stats = {}
    for lang in FOREIGN:
        items = ITEMS[lang]
        if not items:
            continue
        t = T[lang]; P = PAGES[lang]
        render_home(lang)
        grid_page(lang, "all", P["all"], t["all_title"], t["all"], t["all_desc"].format(n=len(items)), t["all_intro"], sort_items(items))
        if P.get("free"):
            sel = sort_items([it for it in items if it["pnum"] == 0])
            grid_page(lang, "free", P["free"], t["free_title"], t["free"], t["free_desc"], t["free_intro"], sel, chip_kinds=())
        nw = newest(items)
        grid_page(lang, "new", P["new"], t["new_title"], t["new_long"], t["new_desc"], t["new_intro"], nw, chip_kinds=())
        for s in ("fall", "winter"):
            if P.get(s):
                sel = sort_items([it for it in items if s in it["season"]])
                grid_page(lang, s, P[s], t["season_title"][s], t[s], t["season_desc"][s], t["season_blurb"][s], sel, filt=f"s:{s}")
        for f in ("trails", "rw", "ws", "bundle"):
            if P.get(f):
                sel = sort_items([it for it in items if it["fam"] == f])
                grid_page(lang, f, P[f], t["fam_title"][f], t[f], t["fam_blurb"][f], t["fam_blurb"][f], sel, filt=f"t:{f}")
        for c in CATS:
            if P.get("cat:" + c):
                sel = sort_items([it for it in items if it["cat"] == c]); nm = CAT_NAME[lang][c]
                grid_page(lang, "cat:" + c, P["cat:" + c], t["subj_title"].format(s=nm), nm,
                          t["subj_desc"].format(s=nm if lang != "en" else nm, n=len(sel)), t["subj_desc"].format(s=nm, n=len(sel)), sel,
                          filt=f"c:{c}", chip_kinds=("g",))
        for key, (slug, nm, o) in STATS["grade_pages"][lang].items():
            g = key.split(":", 1)[1]
            sel = sort_items([it for it in items if g in it["gkeys"]])
            gl = nm.replace("Grade ", "").replace("Grado ", "") if lang in ("en", "es") else nm
            grid_page(lang, key, slug, t["grade_title"].format(g=gl), nm, t["grade_desc"].format(g=gl, n=len(sel)),
                      t["grade_desc"].format(g=gl, n=len(sel)), sel, filt=f"g:{g}", chip_kinds=("c",))
        render_other(lang)
        render_details(lang)
        write_index(lang)
        for f in glob.glob(os.path.join(B.OUT, lang, "*.html")):   # Hub-Seiten, die es nicht mehr gibt, entfernen
            if os.path.normcase(f) not in WRITTEN:
                os.remove(f)
        stats[lang] = {"items": len(items), "pages": len(SITEMAP_URLS[lang])}
    render_other_de()
    render_free_de()
    files, today = write_sitemaps()
    STATS["render"] = stats
    return files, today
