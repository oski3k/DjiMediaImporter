# =============================================================================
#  i18n.py — Internationalization for DJI Media Importer
# =============================================================================

_lang = "en"

LANGUAGES = {
    "en": "English",
    "pl": "Polski",
}

STRINGS = {
    # ── Application ──────────────────────────────────────────────────────────
    "app.name":       {"en": "DJI MEDIA IMPORTER",               "pl": "DJI MEDIA IMPORTER"},
    "app.goodbye":    {"en": "DJI Media Importer — Goodbye!",    "pl": "DJI Media Importer — Do widzenia!"},

    # ── Main Menu ────────────────────────────────────────────────────────────
    "menu.title":        {"en": "MAIN MENU",                        "pl": "MENU GŁÓWNE"},
    "menu.import":       {"en": "Import media from card / drone",   "pl": "Importuj media z karty / drona"},
    "menu.quick":        {"en": "Quick Import",                     "pl": "Szybki import"},
    "menu.history":      {"en": "Import history",                   "pl": "Historia importów"},
    "menu.statistics":   {"en": "Statistics",                       "pl": "Statystyki"},
    "menu.settings":     {"en": "Settings",                         "pl": "Ustawienia"},
    "menu.quit":         {"en": "Quit",                             "pl": "Wyjdź"},

    # ── Navigation hints (reusable) ──────────────────────────────────────────
    "nav.arrows_enter":         {"en": "Use ↑/↓ to navigate | [Enter] to select",
                                 "pl": "Użyj ↑/↓ do nawigacji | [Enter] aby wybrać"},
    "nav.arrows_enter_esc":     {"en": "Use ↑/↓ to navigate | [Enter] to select | [Esc] to cancel",
                                 "pl": "Użyj ↑/↓ do nawigacji | [Enter] aby wybrać | [Esc] anuluj"},
    "nav.arrows_edit_esc":      {"en": "Use ↑/↓ to navigate | [Enter] to edit | [Esc] to go back",
                                 "pl": "Użyj ↑/↓ do nawigacji | [Enter] edytuj | [Esc] wróć"},
    "nav.arrows_enter_details": {"en": "Use ↑/↓ to navigate | [Enter] to view details | [Esc] to go back",
                                 "pl": "Użyj ↑/↓ do nawigacji | [Enter] szczegóły | [Esc] wróć"},
    "nav.arrows_select_esc":    {"en": "Use ↑/↓ to select | [Enter] to confirm | [Esc] to cancel",
                                 "pl": "Użyj ↑/↓ aby wybrać | [Enter] potwierdź | [Esc] anuluj"},
    "nav.esc_q_back":           {"en": "Press [Esc] or [Q] to go back.",
                                 "pl": "Naciśnij [Esc] lub [Q] aby wrócić."},
    "nav.any_key_back":         {"en": "Press any key to go back",
                                 "pl": "Naciśnij dowolny klawisz aby wrócić"},
    "nav.enter_to_menu":        {"en": "Press Enter to return to the main menu...",
                                 "pl": "Naciśnij Enter aby wrócić do menu..."},
    "nav.enter_continue":       {"en": "[Enter] Continue",
                                 "pl": "[Enter] Kontynuuj"},
    "nav.esc_back":             {"en": "[Esc] Back to main menu",
                                 "pl": "[Esc] Wróć do menu"},

    # ── Wait for card ────────────────────────────────────────────────────────
    "wait.title":      {"en": "DEVICE STATUS",                       "pl": "STATUS URZĄDZENIA"},
    "wait.status":     {"en": "Waiting for device connection...",     "pl": "Oczekiwanie na połączenie..."},
    "wait.info":       {"en": "Insert SD card or connect drone via USB.",
                        "pl": "Włóż kartę SD lub podłącz drona przez USB."},
    "wait.scanning":   {"en": "Scanning drives (searching for DCIM)...",
                        "pl": "Skanowanie dysków (szukanie DCIM)..."},

    # ── Source selector ──────────────────────────────────────────────────────
    "source.title":    {"en": "SELECT SOURCE DEVICE",                "pl": "WYBIERZ URZĄDZENIE ŹRÓDŁOWE"},
    "source.multiple": {"en": "⚠  Multiple devices with DCIM detected!",
                        "pl": "⚠  Wykryto wiele urządzeń z DCIM!"},
    "source.unknown":  {"en": "unknown size",                        "pl": "nieznany rozmiar"},
    "source.free":     {"en": "free",                                "pl": "wolne"},

    # ── Card overview (NEW) ──────────────────────────────────────────────────
    "overview.title":      {"en": "CARD OVERVIEW",               "pl": "PRZEGLĄD KARTY"},
    "overview.device":     {"en": "Device:",                     "pl": "Urządzenie:"},
    "overview.capacity":   {"en": "Card capacity:",              "pl": "Pojemność karty:"},
    "overview.used":       {"en": "Used:",                       "pl": "Zajęte:"},
    "overview.free":       {"en": "Free:",                       "pl": "Wolne:"},
    "overview.breakdown":  {"en": "Content breakdown",           "pl": "Podział zawartości"},
    "overview.video":      {"en": "Video:",                      "pl": "Wideo:"},
    "overview.photos":     {"en": "Photos:",                     "pl": "Zdjęcia:"},
    "overview.raw":        {"en": "RAW:",                        "pl": "RAW:"},
    "overview.files":      {"en": "files",                       "pl": "plików"},
    "overview.no_media":   {"en": "No compatible media found.",  "pl": "Nie znaleziono kompatybilnych mediów."},

    # ── File selector ────────────────────────────────────────────────────────
    "files.title":     {"en": "SELECT FILES TO IMPORT",              "pl": "WYBIERZ PLIKI DO IMPORTU"},
    "files.nav1":      {"en": "Use ↑/↓ to navigate | [Space] to toggle | [Enter] to confirm",
                        "pl": "Użyj ↑/↓ nawiguj | [Space] zaznacz | [Enter] potwierdź"},
    "files.nav2":      {"en": "[A] all | [N] none | [V] video | [P] photos | [R] raw | [Esc] cancel",
                        "pl": "[A] wszystko | [N] nic | [V] wideo | [P] zdjęcia | [R] raw | [Esc] anuluj"},
    "files.above":     {"en": "more above",                         "pl": "więcej powyżej"},
    "files.below":     {"en": "more below",                         "pl": "więcej poniżej"},
    "files.selected":  {"en": "Selected:",                          "pl": "Zaznaczono:"},
    "files.files":     {"en": "files",                               "pl": "plików"},
    "files.size":      {"en": "Size:",                               "pl": "Rozmiar:"},

    # ── Confirm import ───────────────────────────────────────────────────────
    "confirm.summary_title": {"en": "MEDIA SUMMARY",                "pl": "PODSUMOWANIE MEDIÓW"},
    "confirm.ready":         {"en": "✔ Device ready for import",     "pl": "✔ Urządzenie gotowe do importu"},
    "confirm.source_path":   {"en": "Source Path:",                  "pl": "Ścieżka źródłowa:"},
    "confirm.video_files":   {"en": "Video files:",                  "pl": "Pliki wideo:"},
    "confirm.photo_files":   {"en": "Photo files:",                  "pl": "Pliki zdjęć:"},
    "confirm.total_files":   {"en": "Total files:",                  "pl": "Łącznie plików:"},
    "confirm.total_size":    {"en": "Total size:",                   "pl": "Łączny rozmiar:"},
    "confirm.free_target":   {"en": "Free on target:",               "pl": "Wolne na dysku:"},
    "confirm.project_name":  {"en": "❓ Project name [default: {name}]: ",
                              "pl": "❓ Nazwa projektu [domyślnie: {name}]: "},
    "confirm.delete_source": {"en": "❓ Delete source files after import?",
                              "pl": "❓ Usunąć pliki źródłowe po imporcie?"},
    "confirm.tags":          {"en": "❓ Tags (comma-separated, optional): ",
                              "pl": "❓ Tagi (oddzielone przecinkami, opcjonalne): "},
    "confirm.notes":         {"en": "❓ Notes (optional): ",
                              "pl": "❓ Notatki (opcjonalne): "},
    "confirm.title":         {"en": "CONFIRM IMPORT",                "pl": "POTWIERDŹ IMPORT"},
    "confirm.folder":        {"en": "Project folder:",               "pl": "Folder projektu:"},
    "confirm.delete":        {"en": "Delete source:",                "pl": "Usuń źródło:"},
    "confirm.yes":           {"en": "Yes",                           "pl": "Tak"},
    "confirm.no":            {"en": "No",                            "pl": "Nie"},
    "confirm.start":         {"en": "[Enter]  Start import (copy files)",
                              "pl": "[Enter]  Rozpocznij import (kopiuj pliki)"},
    "confirm.dry":           {"en": "[D]      Dry run  (simulate, no files copied)",
                              "pl": "[D]      Symulacja (bez kopiowania plików)"},
    "confirm.cancel":        {"en": "[Esc]    Cancel",               "pl": "[Esc]    Anuluj"},

    # ── Folder preview (NEW) ─────────────────────────────────────────────────
    "preview.title":   {"en": "FOLDER PREVIEW",                     "pl": "PODGLĄD STRUKTURY"},
    "preview.total":   {"en": "Total:",                              "pl": "Łącznie:"},

    # ── Progress ─────────────────────────────────────────────────────────────
    "progress.title":      {"en": "COPYING MEDIA",                  "pl": "KOPIOWANIE MEDIÓW"},
    "progress.title_dry":  {"en": "DRY RUN — SIMULATION",           "pl": "SYMULACJA — BEZ KOPIOWANIA"},
    "progress.dest":       {"en": "Destination:",                    "pl": "Cel:"},
    "progress.overall":    {"en": "Overall progress:",               "pl": "Postęp ogólny:"},
    "progress.copying":    {"en": "Copying file:",                   "pl": "Kopiowanie:"},
    "progress.file_size":  {"en": "File size:",                      "pl": "Rozmiar pliku:"},
    "progress.total":      {"en": "Total progress:",                 "pl": "Postęp łączny:"},
    "progress.speed":      {"en": "Transfer speed:",                 "pl": "Prędkość:"},
    "progress.remaining":  {"en": "Remaining:",                      "pl": "Pozostało:"},
    "progress.verifying":  {"en": "Verifying...  ",                  "pl": "Weryfikacja..."},
    "progress.simulating": {"en": "Simulating... ",                  "pl": "Symulacja...  "},
    "progress.skipped":    {"en": "Skipped (Dup)",                   "pl": "Pominięto(Dup)"},

    # ── Settings ─────────────────────────────────────────────────────────────
    "settings.title":         {"en": "SETTINGS",                       "pl": "USTAWIENIA"},
    "settings.edit_hint":     {"en": "Press Enter to edit the selected setting",
                               "pl": "Naciśnij Enter aby edytować ustawienie"},
    "settings.saved":         {"en": "✔ '{label}' saved successfully!",
                               "pl": "✔ '{label}' zapisano pomyślnie!"},
    "settings.save_error":    {"en": "❌ Error writing config.json",
                               "pl": "❌ Błąd zapisu config.json"},
    "settings.new_value":     {"en": "New value (blank to cancel): ",
                               "pl": "Nowa wartość (puste = anuluj): "},
    "settings.invalid_num":   {"en": "Invalid number.",              "pl": "Nieprawidłowa liczba."},
    "settings.current":       {"en": "Current:",                     "pl": "Aktualna:"},

    # Settings: individual fields
    "settings.target_root":       {"en": "Target directory",         "pl": "Folder docelowy"},
    "settings.target_root_desc":  {"en": "Root folder where imports are saved  (e.g. E:\\Dron)",
                                   "pl": "Folder główny do zapisu importów  (np. E:\\Dron)"},
    "settings.project_name":      {"en": "Default project name",     "pl": "Domyślna nazwa projektu"},
    "settings.project_name_desc": {"en": "Suggested name at import prompt  (e.g. DJI, Lot)",
                                   "pl": "Sugerowana nazwa przy imporcie  (np. DJI, Lot)"},
    "settings.delete_source":     {"en": "Delete source by default", "pl": "Domyślnie usuwaj źródło"},
    "settings.delete_source_desc":{"en": "Pre-select 'delete from card' option",
                                   "pl": "Domyślnie zaznacz opcję 'usuń z karty'"},
    "settings.folder_struct":     {"en": "Folder structure",         "pl": "Struktura folderów"},
    "settings.folder_struct_desc":{"en": "How files are organised in the project folder",
                                   "pl": "Jak pliki są organizowane w folderze projektu"},
    "settings.filename_pat":      {"en": "Filename pattern",         "pl": "Wzorzec nazwy pliku"},
    "settings.filename_pat_desc": {"en": "Tokens: {original}  {file_date}  {project_name}",
                                   "pl": "Tokeny: {original}  {file_date}  {project_name}"},
    "settings.buffer":            {"en": "Copy buffer size (MB)",    "pl": "Rozmiar bufora kopiowania (MB)"},
    "settings.buffer_desc":       {"en": "Memory buffer per chunk during copy  (default: 4)",
                                   "pl": "Bufor pamięci na chunk podczas kopiowania  (domyślnie: 4)"},
    "settings.language":          {"en": "Language",                  "pl": "Język"},
    "settings.language_desc":     {"en": "Interface language",        "pl": "Język interfejsu"},
    "settings.theme":             {"en": "Theme",                    "pl": "Motyw"},
    "settings.theme_desc":        {"en": "Color theme for the interface",
                                   "pl": "Motyw kolorystyczny interfejsu"},
    "settings.reset":             {"en": "🔄 Reset all to defaults", "pl": "🔄 Resetuj do domyślnych"},
    "settings.reset_desc":        {"en": "Restore default settings",
                                   "pl": "Przywróć domyślne ustawienia"},
    "settings.reset_confirm":     {"en": "Are you sure? This will reset ALL settings to defaults.",
                                   "pl": "Czy na pewno? Wszystkie ustawienia zostaną zresetowane."},
    "settings.reset_yes":         {"en": "[Y] Yes, reset",           "pl": "[Y] Tak, resetuj"},
    "settings.reset_no":          {"en": "[N] No, cancel",           "pl": "[N] Nie, anuluj"},
    "settings.reset_done":        {"en": "✔ Settings have been reset to defaults!",
                                   "pl": "✔ Ustawienia zostały zresetowane!"},

    # Folder structure choice labels
    "fs.category_and_ext":  {"en": "Category + Extension  (Video/MP4/)",
                             "pl": "Kategoria + Rozszerzenie  (Wideo/MP4/)"},
    "fs.category_only":     {"en": "Category only         (Video/)",
                             "pl": "Tylko kategoria         (Wideo/)"},
    "fs.flat":              {"en": "Flat                  (all in root)",
                             "pl": "Płaska                  (wszystko w głównym)"},
    "fs.by_date":           {"en": "By date               (2026-06-10/Video/MP4/)",
                             "pl": "Wg daty               (2026-06-10/Wideo/MP4/)"},

    # ── History ──────────────────────────────────────────────────────────────
    "history.title":       {"en": "IMPORT HISTORY",                  "pl": "HISTORIA IMPORTÓW"},
    "history.empty":       {"en": "No import history yet.",          "pl": "Brak historii importów."},
    "history.empty_hint":  {"en": "Complete an import to start tracking history here.",
                            "pl": "Wykonaj import aby rozpocząć śledzenie historii."},
    "history.total":       {"en": "Total: {count} imports recorded",
                            "pl": "Łącznie: {count} importów zapisanych"},
    "history.detail_title":{"en": "IMPORT DETAILS",                  "pl": "SZCZEGÓŁY IMPORTU"},
    "history.date":        {"en": "Date:",                           "pl": "Data:"},
    "history.project":     {"en": "Project:",                        "pl": "Projekt:"},
    "history.status":      {"en": "Status:",                         "pl": "Status:"},
    "history.source":      {"en": "Source:",                         "pl": "Źródło:"},
    "history.destination":  {"en": "Destination:",                   "pl": "Cel:"},
    "history.files":       {"en": "Files:",                          "pl": "Pliki:"},
    "history.total_size":  {"en": "Total size:",                     "pl": "Rozmiar:"},
    "history.duration":    {"en": "Duration:",                       "pl": "Czas trwania:"},
    "history.src_deleted": {"en": "Src deleted:",                    "pl": "Źródło usunięte:"},
    "history.tags":        {"en": "Tags:",                           "pl": "Tagi:"},
    "history.notes":       {"en": "Notes:",                          "pl": "Notatki:"},
    "history.dry_run":     {"en": "DRY RUN",                         "pl": "SYMULACJA"},
    "history.completed":   {"en": "COMPLETED",                       "pl": "ZAKOŃCZONY"},
    "history.nav_extra":   {"en": "[T] Filter by tag | [O] Open folder",
                            "pl": "[T] Filtruj po tagu | [O] Otwórz folder"},
    "history.filter_tag":  {"en": "Filter by tag (blank to clear): ",
                            "pl": "Filtruj po tagu (puste = wyczyść): "},
    "history.filtered":    {"en": "Filtered by tag: '{tag}'",
                            "pl": "Filtrowano po tagu: '{tag}'"},
    "history.open_error":  {"en": "Folder not found.",               "pl": "Folder nie istnieje."},

    # ── Statistics (NEW) ─────────────────────────────────────────────────────
    "stats.title":         {"en": "STATISTICS",                      "pl": "STATYSTYKI"},
    "stats.empty":         {"en": "No statistics available yet.",    "pl": "Brak dostępnych statystyk."},
    "stats.empty_hint":    {"en": "Complete some imports to see statistics here.",
                            "pl": "Wykonaj kilka importów aby zobaczyć statystyki."},
    "stats.total_imports": {"en": "Total imports:",                  "pl": "Łączne importy:"},
    "stats.total_files":   {"en": "Total files copied:",             "pl": "Łącznie plików:"},
    "stats.total_data":    {"en": "Total data moved:",               "pl": "Łącznie danych:"},
    "stats.avg_size":      {"en": "Average import size:",            "pl": "Średni rozmiar importu:"},
    "stats.avg_speed":     {"en": "Average speed:",                  "pl": "Średnia prędkość:"},
    "stats.by_month":      {"en": "Imports by month",                "pl": "Importy wg miesiąca"},
    "stats.imports":       {"en": "imports",                         "pl": "importów"},
    "stats.top":           {"en": "Top 3 largest imports",           "pl": "Top 3 największe importy"},

    # ── Quick Import (NEW) ───────────────────────────────────────────────────
    "quick.title":         {"en": "QUICK IMPORT",                    "pl": "SZYBKI IMPORT"},
    "quick.starting":      {"en": "Starting quick import with default settings...",
                            "pl": "Rozpoczynanie szybkiego importu z domyślnymi ustawieniami..."},
    "quick.project":       {"en": "Project:",                        "pl": "Projekt:"},
    "quick.files":         {"en": "Files found:",                    "pl": "Znalezione pliki:"},
    "quick.total_size":    {"en": "Total size:",                     "pl": "Łączny rozmiar:"},
    "quick.delete":        {"en": "Delete source:",                  "pl": "Usuń źródło:"},

    # ── Resume (NEW) ────────────────────────────────────────────────────────
    "resume.title":        {"en": "INCOMPLETE IMPORT DETECTED",      "pl": "WYKRYTO PRZERWANY IMPORT"},
    "resume.interrupted":  {"en": "⚠ Previous import was interrupted!",
                            "pl": "⚠ Poprzedni import został przerwany!"},
    "resume.project":      {"en": "Project:",                        "pl": "Projekt:"},
    "resume.progress":     {"en": "Progress:",                       "pl": "Postęp:"},
    "resume.remaining":    {"en": "Remaining:",                      "pl": "Pozostało:"},
    "resume.copied":       {"en": "files copied",                    "pl": "plików skopiowanych"},
    "resume.resume":       {"en": "[R]  Resume import (skip already copied files)",
                            "pl": "[R]  Wznów import (pomiń już skopiowane pliki)"},
    "resume.fresh":        {"en": "[S]  Start fresh (ignore previous)",
                            "pl": "[S]  Zacznij od nowa (ignoruj poprzedni)"},
    "resume.cancel":       {"en": "[Esc] Back to menu",              "pl": "[Esc] Wróć do menu"},

    # ── Success / Report ────────────────────────────────────────────────────
    "success.title":        {"en": "SUCCESS",                        "pl": "SUKCES"},
    "success.title_dry":    {"en": "DRY RUN COMPLETE",               "pl": "SYMULACJA ZAKOŃCZONA"},
    "success.completed":    {"en": "🎉 IMPORT COMPLETED SUCCESSFULLY!",
                             "pl": "🎉 IMPORT ZAKOŃCZONY POMYŚLNIE!"},
    "success.completed_dry":{"en": "🎉 SIMULATION COMPLETED SUCCESSFULLY!",
                             "pl": "🎉 SYMULACJA ZAKOŃCZONA POMYŚLNIE!"},
    "success.saved_to":     {"en": "Saved to:",                      "pl": "Zapisano w:"},
    "success.copied_files": {"en": "Copied files:",                  "pl": "Skopiowane pliki:"},
    "success.source_files": {"en": "Source files:",                  "pl": "Pliki źródłowe:"},
    "success.deleted_yes":  {"en": "Yes, deleted from device",       "pl": "Tak, usunięte z urządzenia"},
    "success.deleted_no":   {"en": "No, kept on device",             "pl": "Nie, zachowane na urządzeniu"},
    "success.total_size":   {"en": "Total size:",                    "pl": "Łączny rozmiar:"},
    "success.op_time":      {"en": "Operation time:",                "pl": "Czas operacji:"},
    "success.dry_note":     {"en": "⚠ DRY RUN — no files were actually copied!",
                             "pl": "⚠ SYMULACJA — żadne pliki nie zostały skopiowane!"},
    "success.folder_opened":{"en": "📂 Target folder was automatically opened.",
                             "pl": "📂 Folder docelowy został automatycznie otwarty."},

    # ── Errors ───────────────────────────────────────────────────────────────
    "error.cancelled":      {"en": "CANCELLED",                      "pl": "ANULOWANO"},
    "error.no_files_title":  {"en": "NO COMPATIBLE FILES",           "pl": "BRAK KOMPATYBILNYCH PLIKÓW"},
    "error.no_files":        {"en": "❌ No compatible media found to copy.",
                              "pl": "❌ Nie znaleziono kompatybilnych mediów do kopiowania."},
    "error.scanned_path":    {"en": "Scanned path:",                 "pl": "Przeskanowana ścieżka:"},
    "error.ensure_files":    {"en": "Ensure the card contains video files (.mp4, .mov, .mkv)\nor photo files (.jpg, .jpeg, .dng, .raw, .png).",
                              "pl": "Upewnij się, że karta zawiera pliki wideo (.mp4, .mov, .mkv)\nlub pliki zdjęć (.jpg, .jpeg, .dng, .raw, .png)."},
    "error.disk_title":      {"en": "DISK SPACE ERROR",              "pl": "BRAK MIEJSCA NA DYSKU"},
    "error.disk":            {"en": "❌ INSUFFICIENT DISK SPACE!",    "pl": "❌ NIEWYSTARCZAJĄCE MIEJSCE NA DYSKU!"},
    "error.target_root":     {"en": "Target Root:",                  "pl": "Folder docelowy:"},
    "error.required":        {"en": "Required:",                     "pl": "Wymagane:"},
    "error.available":       {"en": "Available:",                    "pl": "Dostępne:"},
    "error.free_space":      {"en": "Please free up space and try again.",
                              "pl": "Zwolnij miejsce i spróbuj ponownie."},
    "error.write_title":     {"en": "WRITE ERROR",                   "pl": "BŁĄD ZAPISU"},
    "error.write":           {"en": "❌ Error creating target directory!",
                              "pl": "❌ Błąd tworzenia folderu docelowego!"},
    "error.path":            {"en": "Path:",                         "pl": "Ścieżka:"},
    "error.error":           {"en": "Error:",                        "pl": "Błąd:"},
    "error.aborted_title":   {"en": "ABORTED",                      "pl": "PRZERWANO"},
    "error.aborted":         {"en": "⚠ IMPORT CANCELLED BY USER!",   "pl": "⚠ IMPORT ANULOWANY PRZEZ UŻYTKOWNIKA!"},
    "error.aborted_hint":    {"en": "Copying process has stopped.\nSome files may not have been copied.",
                              "pl": "Proces kopiowania został zatrzymany.\nNiektóre pliki mogły nie zostać skopiowane."},
    "error.import_title":    {"en": "ERROR",                         "pl": "BŁĄD"},
    "error.import":          {"en": "❌ IMPORT ERROR!",               "pl": "❌ BŁĄD IMPORTU!"},
    "error.import_hint":     {"en": "An error occurred during copy or verification:",
                              "pl": "Wystąpił błąd podczas kopiowania lub weryfikacji:"},
    "error.src_safe":        {"en": "Source files have NOT been deleted.",
                              "pl": "Pliki źródłowe NIE zostały usunięte."},

    # ── Scanning ─────────────────────────────────────────────────────────────
    "scan.title":      {"en": "SCANNING DEVICE",                     "pl": "SKANOWANIE URZĄDZENIA"},
    "scan.detected":   {"en": "✔ Device detected!",                  "pl": "✔ Urządzenie wykryte!"},
    "scan.path":       {"en": "Path:",                               "pl": "Ścieżka:"},
    "scan.analyzing":  {"en": "🔍 Analysing card contents...",       "pl": "🔍 Analizowanie zawartości karty..."},

    # ── Folder category names ────────────────────────────────────────────────
    "folder.video":    {"en": "Video",                               "pl": "Wideo"},
    "folder.photos":   {"en": "Photos",                              "pl": "Zdjecia"},
    "folder.project":  {"en": "Project",                             "pl": "Projekt"},

    # ── General ──────────────────────────────────────────────────────────────
    "general.yes":     {"en": "Yes",                                 "pl": "Tak"},
    "general.no":      {"en": "No",                                  "pl": "Nie"},
    "general.files":   {"en": "files",                               "pl": "plików"},
}


def t(key, **kwargs):
    """Get translated string. Supports {placeholder} formatting via kwargs."""
    entry = STRINGS.get(key)
    if entry is None:
        return key
    text = entry.get(_lang, entry.get("en", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def set_language(lang):
    """Set the active language."""
    global _lang
    if lang in LANGUAGES:
        _lang = lang


def get_language():
    """Return current language code."""
    return _lang


def get_languages():
    """Return dict of available languages: {code: display_name}."""
    return LANGUAGES.copy()
