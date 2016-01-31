# pywikipedia-fi

*Pywikipedia scripts used on the Finnish Wikipedia.*

Pywikipedia-fi on kokoelma Pywikibotiin perustuvia työkaluja, joita käytetään suomenkielisessä Wikipediassa. Kokoelma sisältää seuraavat skriptit:
* `birthcat.py` – Henkilöartikkelien lisääminen syntymä- ja kuolinvuosiluokkiin. `birthcat -auto` lisää ilman vahvistusta luokat sellaisiin artikkeleihin, joiden tiedot voidaan vahvistaa en-, de- ja es-wikeistä.
* `sciname.py` – Ohjausten lisääminen tieteellisistä nimistä eliöartikkeleihin.

Hankkeen sivusto: https://github.com/silvonen/pywikipedia-fi

## Ohjeita käyttäjille

Näin saat pywikipedia-fi-työkalut käyttöön:

1. Lataa ja ota käyttöön Pywikibotin tuorein versio [ohjeen](https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation/fi) mukaan. Muista lisätä pywikibot-hakemisto PYTHONPATH-ympäristömuuttujaan.
2. Lataa pywikipedia-fi:n tuorein versio: `git clone https://github.com/silvonen/pywikipedia-fi.git pywikipedia-fi`
3. Varmista, että botillasi on [bottikäytännön](http://fi.wikipedia.org/wiki/Wikipedia:Botit) mukaiset luvat suomenkielisessä Wikipediassa.
4. Aja! Kunkin skriptin käyttöohjeen voi tulostaa komennolla `skripti -help`.

Esimerkkejä:

    # Lisätään suomalaiset matemaatikot syntymä- ja kuolinvuosiluokkiin
    birthcat.py -catr:"Suomalaiset matemaatikot"

    # Lisätään kastemadon tieteellinen nimi
    sciname.py "Kastemato"

## Ohjeita kehittäjille

Vaikka pywikipedia-fi on tarkoitettu suomenkielistä Wikipediaa varten, jotkin työkalumme saattavat päätyä osaksi yleisempään käyttöön. Siksi kannattaa noudattaa seuraavia periaatteita:

* Yritä toteuttaa skriptit niin, että ne voidaan helposti laajentaa muissa wikeissä käytettäviksi.
* Nimeä luokat, metodit ja muuttujat englanniksi ja käytä englantia myös koodin kommenteissa.
* Tulosta vain skriptin käyttäjälle näkyvät tekstit englanniksi.
* Kirjoita muokkausyhteenvedot ja muut suomenkielisessä Wikipediassa näkyvät tekstit suomeksi, mutta toteuta ne aina Pywikibotin `translate()`-metodilla.
