# Gen3Save  
Una libreria Python per leggere i file di salvataggio dei giochi Pokémon di **terza generazione** (Game Boy Advance).

## Come utilizzarlo

### Da riga di comando:
```bash
python pokemondata/Gen3Save.py salvataggio.sav
```

### All’interno di uno script Python:
```python
from pokemondata import Gen3Save

data = Gen3Save('salvataggio.sav')
```

Sostituisci `salvataggio.sav` con un file di salvataggio di Pokémon Rubino, Zaffiro, Smeraldo, Rosso Fuoco o Verde Foglia.  
Puoi ottenere questi file:

- Usando un emulatore come **VisualBoy Advance**, oppure  
- Trasferendo il salvataggio direttamente da una cartuccia GBA al PC.  
  Una guida dettagliata è disponibile qui:  
  👉 https://www.drashsmith.com/post/copying-save-files-from-gameboy-advance-games-to-a-pc/

---

## Documentazione

Questa libreria include due classi principali:  
- `Gen3Save`: per leggere il file di salvataggio  
- `Gen3Pokemon`: per accedere ai dati dei singoli Pokémon  

⚠️ **Le classi sono a sola lettura**: non è previsto modificare o salvare i dati tramite questa libreria.

### `Gen3Save`
Una volta caricato un file `.sav`, puoi accedere ai seguenti attributi:

- `team`: una lista dei Pokémon presenti nella **squadra del giocatore**
- `boxes`: una lista di **tutti i Pokémon depositati nei box del PC**

### `Gen3Pokemon`
Ogni Pokémon ha diverse proprietà utili:

- `name`: nome o soprannome del Pokémon (stringa)
- `trainer`: oggetto con ID e nome dell’allenatore originale
- `level`: livello del Pokémon (intero)
- `species`: oggetto con ID e nome della specie
- `nature`: natura del Pokémon (stringa, es. "Docile", "Vivace", ecc.)
- `moves`: lista di mosse conosciute, ognuna con nome, ID e PP
- `exp`: punti esperienza (intero)
- `ivs`: statistiche individuali (IV) parzialmente implementate
- `data`: i dati interni del Pokémon, decriptati (utili per strumenti come **A-Save**)

---

## Ringraziamenti

Questa libreria è stata resa possibile grazie alle ricerche dettagliate pubblicate su Bulbapedia:

- 📘 [Struttura dei file di salvataggio in Gen III](https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_in_Generation_III)  
- 📘 [Struttura dati dei Pokémon in Gen III](https://bulbapedia.bulbagarden.net/wiki/Pokémon_data_structure_in_Generation_III)  
- 📘 [Sottostrutture dei dati dei Pokémon in Gen III](https://bulbapedia.bulbagarden.net/wiki/Pokémon_data_substructures_in_Generation_III)  
- 📘 [Codifica dei caratteri in Gen III](https://bulbapedia.bulbagarden.net/wiki/Character_encoding_in_Generation_III)

Grazie a chi ha fatto il reverse engineering e condiviso queste informazioni.

---

## Perché la Terza Generazione?

- È **facile ottenere i salvataggi** da una cartuccia GBA
- Da qui in poi, il formato dei dati diventa molto più interessante e ricco
- I Pokémon catturati in Gen III possono essere **trasferiti fino a Gen VII**
- Perché, diciamolo, **la Gen IV è sopravvalutata** 😄
