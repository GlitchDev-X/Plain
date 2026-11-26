import re
import sys
import time
import ctypes
import urllib.request
import webbrowser
import tkinter as tk
from tkinter import simpledialog

variabili = {}

def chiedi_input_popup(domanda):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    risposta = simpledialog.askstring("Plain", domanda, parent=root)
    root.destroy()
    return risposta if risposta is not None else ""
def valuta_valore(val):
    val = val.strip()
    if val == "nothing":
        return None
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("“") and val.endswith("”")):
        return val[1:-1]
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return variabili.get(val, None)

def controlla_link(url_raw):
    url = str(valuta_valore(url_raw)).strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception:
        return False
def esegui_change(istruzione):
    istruzione = re.sub(r'\bthe\b', '', istruzione).strip()
    match_to = re.match(r'^change\s+(\w+)\s+to\s+(.+)$', istruzione)
    if match_to:
        nome, val = match_to.groups()
        valore_vero = valuta_valore(val)
        if valore_vero is None and val.strip() == "nothing":
            variabili.pop(nome, None)
        else:
            variabili[nome] = valore_vero
        return True
    match_by = re.match(r'^change\s+(\w+)\s+by\s+([+-]?\d+(?:.\d+)?)$', istruzione)
    if match_by:
        nome, delta = match_by.groups()
        if nome in variabili and isinstance(variabili[nome], (int, float)):
            variabili[nome] += float(delta) if '.' in delta else int(delta)
            return True
        return False
    return False
def valuta_singola_condizione(cond):
    cond = re.sub(r'\bthe\b', '', cond).strip()
    if cond.startswith("check link "):
        return controlla_link(cond[11:].strip())
    match_azione = re.match(r'^(\w+)\s+change\s+(by|to)\s+(.+)$', cond)
    if match_azione:
        nome, tipo, resto = match_azione.groups()
        return esegui_change(f"change {nome} {tipo} {resto}")
    match_is = re.match(r'^(\w+)\s+is\s+(.+)$', cond)
    if match_is:
        nome, val_atteso = match_is.groups()
        return variabili.get(nome, None) == valuta_valore(val_atteso)
    return False

def valuta_condizione_completa(testo_cond):
    parti_or = re.split(r'\bor\b', testo_cond)
    for blocco_or in parti_or:
        parti_and = re.split(r'\band\b', blocco_or)
        if all(valuta_singola_condizione(p) for p in parti_and):
            return True
    return False

def trova_fine_blocco(righe, indice_inizio):
    profondita = 1
    i = indice_inizio
    while i < len(righe):
        r = righe[i]
        if (r.startswith("if ") and r.endswith(" then")) or (r.startswith("repeat ") and r.endswith(" times")):
            profondita += 1
        elif r == "end":
            profondita -= 1
            if profondita == 0:
                return i
        i += 1
    return len(righe)
def esegui_plain(codice):
    righe = [r.strip() for r in codice.split('\n') if r.strip()]
    i = 0
    while i < len(righe):
        riga = righe[i]
        if riga.startswith("change "):
            esegui_change(riga)
            i += 1
        elif riga.startswith("say;"):
            contenuto = str(valuta_valore(riga[4:].strip()))
            for k, v in variabili.items():
                contenuto = contenuto.replace("{" + k + "}", str(v))
            ctypes.windll.user32.MessageBoxW(0, contenuto, "Plain", 0x40)
            i += 1
        elif riga.startswith("open link "):
            url = str(valuta_valore(riga[10:].strip())).strip()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            webbrowser.open(url)
            i += 1
        elif riga.startswith("ask;"):
            match_ask = re.match(r'^ask;\s*(.+?)\s+to\s+(\w+)$', riga)
            if match_ask:
                domanda_raw, var_nome = match_ask.groups()
                risposta = chiedi_input_popup(str(valuta_valore(domanda_raw)))
                variabili[var_nome] = valuta_valore(risposta) if risposta.isdigit() else risposta
            i += 1
        elif riga.startswith("wait "):
            time.sleep(float(valuta_valore(riga[5:].strip())))
            i += 1
        elif riga.startswith("repeat ") and riga.endswith(" times"):
            volte = int(valuta_valore(riga[7:-6].strip()))
            fine = trova_fine_blocco(righe, i + 1)
            blocco = "\n".join(righe[i + 1:fine])
            for x in range(volte):
                esegui_plain(blocco)
            i = fine + 1
        elif riga.startswith("if ") and riga.endswith(" then"):
            fine = trova_fine_blocco(righe, i + 1)
            rami, cond_corrente, blocco_corrente = [], riga[3:-5].strip(), []
            j = i + 1
            while j < fine:
                r = righe[j]
                if r.startswith("else if ") and r.endswith(" then"):
                    rami.append((cond_corrente, blocco_corrente))
                    cond_corrente, blocco_corrente = r[8:-5].strip(), []
                elif r == "else":
                    rami.append((cond_corrente, blocco_corrente))
                    cond_corrente, blocco_corrente = "TRUE", []
                else:
                    blocco_corrente.append(r)
                j += 1
            rami.append((cond_corrente, blocco_corrente))
            for cond, istruzioni in rami:
                if cond == "TRUE" or valuta_condizione_completa(cond):
                    esegui_plain("\n".join(istruzioni))
                    break
            i = fine + 1
        else:
            ctypes.windll.user32.MessageBoxW(0, f"Riga non riconosciuta: {riga}", "Errore Plain", 0x10)
            i += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        ctypes.windll.user32.MessageBoxW(0, "Trascina un file .pln su esegui_plain.bat!", "Plain", 0x40)
    else:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            esegui_plain(f.read())