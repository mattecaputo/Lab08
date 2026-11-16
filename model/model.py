from database.distributore_DAO import DistributoreDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """

        risultato = []
        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            prezzi_mese = [p.prezzo_litro for p in prezzi if p.data.month == mese]

            if len(prezzi_mese) > 0:
                media = sum(prezzi_mese) / len(prezzi_mese)
                risultato.append((distributore.nome, round(media, 3)))
            else:
                risultato.append((distributore.nome, 0.0))

        return risultato

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """

        # Se abbiamo pianificato tutti e 7 i giorni, controlliamo se il costo è il migliore trovato finora
        if len(sequenza_parziale) == 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente  # IMPORTANTE: fare una copia della lista, altrimenti le modifiche successive tramite pop() sovrascriveranno anche la sequenza ottima salvata.
                self.__sequenza_ottima = list(sequenza_parziale)
                return

        # Se il costo parziale ha già superato il costo ottimo attuale,
        # è inutile continuare a esplorare questo ramo.
        if self.__costo_ottimo != -1 and costo_corrente >= self.__costo_ottimo:
            return


        for distributore in self._distributori:
            id_dist = distributore.id

            # L'indice della lista dei prezzi è giorno - 1 (perché il giorno parte da 1, ma gli indici da 0)
            prezzo_litro = prezzi_settimana[id_dist][giorno - 1]

            # Calcolo del costo per questa specifica giornata: 100 litri * prezzo
            costo_giornaliero = float(prezzo_litro) * 100

            # Aggiungiamo il costo fisso di 5€ se cambiamo distributore
            if ultimo_distributore is not None and ultimo_distributore != id_dist:
                costo_giornaliero += 5

            # Applichiamo la scelta temporanea (Compute Partial)
            sequenza_parziale.append(id_dist)

            # Scendiamo di livello nella ricorsione per il giorno successivo
            self.__ricorsione(sequenza_parziale,
                              giorno + 1,
                              id_dist,
                              costo_corrente + costo_giornaliero,
                              prezzi_settimana)

            # Finito di esplorare le conseguenze della scelta di 'id_dist',
            # rimuoviamo l'ultimo elemento per permettere al ciclo for di provare l'altro distributore.
            sequenza_parziale.pop()


    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_settimana = {}
        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            # Filtriamo i primi 7 giorni del mese scelto e ordiniamo cronologicamente
            prezzi_filtrati = [p for p in prezzi if p.data.month == mese and 1 <= p.data.day <= 7]
            prezzi_filtrati.sort(key=lambda p: p.data)

            prezzi_settimana[distributore.id] = [p.prezzo_litro for p in prezzi_filtrati]

        return prezzi_settimana
