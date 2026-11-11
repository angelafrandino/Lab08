from database.distributore_DAO import DistributoreDAO
from database.prezzo_DAO import PrezzoDAO

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
        distributori = DistributoreDAO.get_distributori()
        prezzo_medio = []

        for d in distributori:
            tutti_prezzi = PrezzoDAO.get_prezzi(d.id)

            prezzi_mese = [p.prezzo_litro for p in tutti_prezzi if p.data.month == mese]

            if prezzi_mese:
                media = sum(prezzi_mese) / len(prezzi_mese)
            else:
                media = 0.0

            prezzo_medio.append((d.nome, media))

        return prezzo_medio


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
        # TODO
        if giorno > 7:
            if self.__costo_ottimo == -1 or self.__costo_ottimo > costo_corrente:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
            return

        for d_id in prezzi_settimana.keys():
            prezzo_litro = prezzi_settimana[d_id][giorno - 1]
            costo_carburante = prezzo_litro * 100

            costo_spostamento = 0
            if ultimo_distributore is not None and d_id != ultimo_distributore:
                costo_spostamento = 5

            nuovo_costo = costo_corrente + costo_spostamento + costo_carburante

            if self.__costo_ottimo == -1 or nuovo_costo < self.__costo_ottimo:  #va al giorno dopo solo se il costo parziale
                sequenza_parziale.append(d_id)                                  # non ha superato il miglior costo totale noto

                self.__ricorsione(
                    sequenza_parziale=sequenza_parziale,
                    giorno=giorno + 1,
                    ultimo_distributore=d_id,
                    costo_corrente=nuovo_costo,
                    prezzi_settimana=prezzi_settimana
                )

                sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_settimana = {}

        for d in self._distributori:
            tutti_prezzi = PrezzoDAO.get_prezzi(d.id)

            prezzi_filtrati = [
                p for p in tutti_prezzi
                if p.data.month == mese and 1 <= p.data.day <= 7
            ]

            prezzi_settimana[d.id] = [p.prezzo_litro for p in prezzi_filtrati]

        return prezzi_settimana