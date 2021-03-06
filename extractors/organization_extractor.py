from typing import Any, Dict, List

from transformers import Pipeline, pipeline

from extractors.extracting_tasks import NERExtractingTask


class OrganizationExtractor(NERExtractingTask):
    model = 'xlm-roberta-large-finetuned-conll03-german'
    tokenizer = 'xlm-roberta-large-finetuned-conll03-german'

    def _extract(self):
        ner_pipeline: Pipeline = pipeline('ner', model=self.model, tokenizer=self.tokenizer, grouped_entities=True)
        extracted: List[Dict[str, Any]] = []

        for line_index, line in self.lines.items():
            entities = ner_pipeline(line)

            delete: List[int] = []

            for index in range(len(entities)):
                if entities[index]['score'] < 0.9:
                    delete.append(index)

            for index in sorted(delete, reverse=True):
                del entities[index]

            if any(entity.get('entity_group') == 'ORG' for entity in entities):
                for entity in entities:
                    if entity['entity_group'] == 'ORG':
                        extracted.append({
                            'type': 'organization',
                            'match': entity['word'],
                            'index': line_index
                        })

        print(f'Organizations: {extracted}')

        return extracted


if __name__ == '__main__':
    oe = OrganizationExtractor(
        {1: '08621 - 9 88 30 88', 2: 'Fernwartung', 3: 'Toggle navigation', 4: 'IT-Support', 5: 'Datenrettung',
         6: 'Datensicherung und Wiederherstellung', 7: 'Monitoring', 8: 'Software & Updates',
         9: 'Upgrade und Austausch', 10: 'Wartungsverträge', 11: 'IT-Beratung', 12: 'Beschaffung', 13: 'Projektplanung',
         14: 'Schulungen', 15: 'Linux- und Microsoftprojekte', 16: 'Virtualisierung', 17: 'Server- und Clientsysteme',
         18: 'Beurteilung von IT-Installationen', 19: 'IT-Sicherheit', 20: 'Clustersysteme', 21: 'Firewall und IDS',
         22: 'Penetrationstests', 23: 'Cloudbasierter Spam- und Virenfilter', 24: 'Schutz vor Web-Angriffen',
         25: 'DSGVO konforme E-Mail Verschlüsselung', 26: 'Standortvernetzung', 27: 'Verschlüsselung',
         28: 'Virenschutz', 29: 'Kommunikation', 30: '3CX Telefonanlagen', 31: 'DECT-Installationen',
         32: 'Groupware-Server', 33: 'Unternehmen', 34: 'Das Unternehmen', 35: 'Vision 2025', 36: 'Ihr Nutzen',
         37: 'Umweltschutz', 38: 'Downloads und Marketingmaterial', 39: 'Referenzen', 41: 'Kontakt', 42: 'News',
         43: 'Blog', 45: 'Home', 46: '&nbsp / &nbsp', 47: 'Unternehmen', 48: '&nbsp / &nbsp',
         50: 'Angaben gemäß § 5 TMG:', 51: 'cubewerk GmbH', 52: 'Herzog-Otto-Straße 32', 53: '83308 Trostberg',
         54: 'Vertreten durch:', 55: 'Stefan Bauer', 56: 'Kontakt:', 57: 'Telefon: 08621-9883088',
         58: 'E-Mail: support@cubewerk.de', 59: 'Registereintrag:', 60: 'Eintragung im', 61: 'Handelsregister.',
         62: 'Registergericht:Traunstein', 63: 'Registernummer: HRB22195',
         64: 'Umsatzsteuer-Identifikationsnummer gemäß §27 a Umsatzsteuergesetz:', 65: 'DE285171480',
         66: 'Angaben zur Berufshaftpflichtversicherung:', 67: 'Name und Sitz des', 68: 'Versicherers:',
         69: 'exali GmbH', 70: 'Franz-Kobinger-Str. 9', 71: '86157 Augsburg',
         72: 'Geltungsraum der Versicherung: Deutschland', 74: 'Abs. 2 RStV:', 75: 'Stefan Bauer',
         76: 'Herzog-Otto-Straße 32', 77: '83308 Trostberg', 79: 'Verbraucherschlichtungsstelle teilzunehmen.',
         82: 'nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als',
         83: 'Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu',
         84: 'überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit', 85: 'hinweisen.',
         86: 'Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach',
         88: 'erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden',
         91: 'Unser Angebot enthält Links zu externen Webseiten Dritter, auf',
         94: 'Anbieter oder Betreiber der Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der',
         96: 'waren zum Zeitpunkt der Verlinkung nicht erkennbar.',
         98: 'Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen.', 99: 'Urheberrecht',
         101: 'unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede',
         102: 'Art der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen',
         103: 'Zustimmung des jeweiligen Autors bzw. Erstellers. Downloads und Kopien dieser Seite sind nur für',
         107: 'Dritter als solche gekennzeichnet. Sollten Sie trotzdem auf eine Urheberrechtsverletzung aufmerksam',
         108: 'werden, bitten wir um einen entsprechenden Hinweis. Bei Bekanntwerden von Rechtsverletzungen',
         112: 'cubewerk GmbH', 113: 'Herzog-Otto-Straße 32', 114: '83308 Trostberg', 115: 'Vertreten durch:',
         116: 'Stefan Bauer', 117: 'Telefon: 08621-9883088', 118: 'E-Mail: anfragen@cubewerk.de',
         119: 'Registereintrag:', 120: 'Eintragung im', 121: 'Handelsregister.', 122: 'Registergericht:Traunstein',
         123: 'Registernummer: HRB22195', 124: 'Umsatzsteuer-Identifikationsnummer gemäß §27 a Umsatzsteuergesetz:',
         125: 'DE285171480', 126: 'Erfassung allgemeiner Informationen',
         127: 'Beim Zugriff auf unsere Homepage werden in der Regel allgemeine Informationen über unsere Nutzer erfasst. Diese sind',
         128: 'Ihr Webbrowser', 129: 'das verwendete Betriebssystem',
         130: 'Ihr Internetanbieter sowie weitere Daten die zur Kommunikation auf Netzwerkebene nötig sind.',
         132: 'Für die Anforderung von Testzugängen, erfassen wir im Rahmen der vorvertraglichen Auftragserfüllung, Name, Firmenname, Adressen und E-Mail-Adresse für die Abwicklung der Anfrage.',
         133: 'SSL-Verschlüsselung',
         134: 'Zur Absicherung und zum Schutz Ihrer Daten, verwenden wir aktuelle – und dem Standard entsprechende – Technik zur Datenverschlüsselung (z.B. SSL) für die HTTPS-Kommunikation.',
         139: 'Die Verarbeitung erfolgt auf Grundlage des § 15 (3) TMG sowie Art. 6 (1) lit. f DSGVO aus dem berechtigten Interesse an den oben genannten Zwecken.',
         140: 'Die auf diese Weise von Ihnen erhobenen Daten werden durch technische Vorkehrungen pseudonymisiert. Eine Zuordnung der Daten zu Ihrer Person ist daher nicht mehr möglich. Die Daten werden nicht gemeinsam mit sonstigen personenbezogenen Daten von Ihnen gespeichert.',
         141: 'Sie haben das Recht aus Gründen, die sich aus Ihrer besonderen Situation ergeben, jederzeit gegen diese auf Art. 6 (1) f DSGVO beruhende Verarbeitung Sie betreffender personenbezogener Daten zu widersprechen.',
         144: 'Chrome Browser:', 146: 'Internet Explorer:', 148: 'Mozilla Firefox:', 150: 'Safari:',
         152: 'Löschung bzw. Sperrung Ihrer Daten',
         153: 'Wir vermeiden zu jeder Zeit die unnötige Datenerhebung und Erfassung und haushalten sparsam. Die für die Verarbeitung nötige Datenspeicherung erfolgt lediglich solange, wie diese für die Erfüllung der hier genannten Zwecke nötig ist oder wie es die gesetzliche Speicherfrist durch den Gesetzgeber vorschreibt. Ist der Zweck nicht mehr gegeben bzw. die etwaige Frist abgelaufen, werden diese Daten regelmäßig überprüft und nach den gesetzlichen Vorgaben gelöscht bzw. der Zugriff darauf gesperrt.',
         157: 'Integrierte / eingebettete Youtubevideos',
         159: 'Ihr Recht auf Auskunft, Berichtigung, Sperre, Löschung und Widerspruch',
         160: 'Es besteht jederzeit für Sie die Möglichkeit, eine Auskunft über die bei uns gespeicherten personenbezogenen Nutzerdaten zu erhalten. Ebenso können Sie eine Berichtigung, Sperrung oder Löschung der von Ihnen personenbezogenen Daten verlangen. Davon abgesehen ist die nötige Datenspeicherung zur Erfüllung unserer Geschäfte mit Ihnen. Hierzu wenden Sie sich bitte an die oben genannten Kontaktdaten.',
         161: 'Damit wir eine gewünschte Sperrung dauerhaft aufrechterhalten können, halten wir – auch zur Kontrolle – eine Datei vor, die die Sperrungen verzeichinet. Auch eine Löschung der Daten ist möglich, wenn denn keine gesetzlichen Archivierungspflichten bestehen. Auf Wunsch sperren wir Ihre Daten, falls eine solche Verpflichtung existiert. Auch können Sie für die Zukunft einen Widerruf Ihrer Einwilligung durch entsprechende Meldung an uns vornehmen.',
         162: 'Zusätzlich besteht für Sie ein Beschwerderecht bei einer Aufsichtsbehörde.',
         166: 'Schreiben Sie uns bitte eine E-Mail oder wenden sich an die oben genannten Kontaktdaten.',
         167: 'Version: 20.08.2019 – cubewerk GmbH / Stefan Bauer', 169: '© 2018 cubewerk GmbH',
         171: 'Weitere Informationen.'})

    print(oe.extract())
