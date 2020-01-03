import sys
import re


class Simplify():

    def __init__(self, sentences):

        self.verb_suffixes = ['n', 'd', 'b', 'me', 'te', 'vad']

        #(parsed lemma = ma infinitv without ma)
        self.irregular_verbs = {'rääki':'räägi', 'taht': 'taha', 'pida':'pea', 'luge': 'loe', 'and':'anna', 'seis':'seisa', 'mine':'lähe', 'lask':'lase', 
        'õppi': 'õpi', 'saat':'saada', 'välti': 'väldi', 'panti': 'pandi', 'kart': 'karda', 'ehti':'ehi', 'sead':'sea', 'ladu':'lao', 'sidu':'seo', 
        'sada': 'saja', 'küündi':'küüni', 'kõndi': 'kõnni', 'murd':'murra', 'pildu':'pillu', 'vilku':'vilgu', 'märki':'märgi', 'saagi':'sae', 'nülgi':'nüli',
        'marssi':'marsi', 'jooks':'jookse', 'jät':'jäta', 'mat':'mata', 'mõsk':'mõse', 'näge':'näe', 'tege':'tee', 'veda': 'vea'}

        self.relpron = {'kes':('. Tema','. Nad'), 'kelle':('. Tema', '. Nende'), 'keda':('. Teda', '. Neid'), 
        'kellesse': ('. Temasse', '. Nendesse'), 'kelles':('. Temas', '. Nendes'), 'kellest': ('. Temast', '. Neist'),
        'kellele':('. Talle', '. Neile'), 'kellel':('. Tal', 'Neil'), 'kellelt': ('. Temalt', '. Nendelt'), 
        'kelleks': ('. Temaks', '. Nendeks'), 'kelleni': ('. Temani', '. Nendeni'), 'kellena':('. Temana', '. Nendena'), 
        'kelleta':('. Ilma tematata', '. Ilma nendeta'), 'kellega': ('. Temaga', '. Nendega'),

        'mis': ('. See', '. Need'), 'mille': ('. Selle', '. Nende'), 'mida': ('. Seda', '. Neid'), 'millesse':('. Sellesse', '. Nendesse'), 
        'milles': ('. Selles', '. Nendes'), 'millest': ('. Sellest', '. Nendest'), 'millele': ('. Sellele', '. Nendele'),
        'millel':('. Sellel', '. Nendel'), 'millelt': ('. Sellelt', '. Nendelt'), 'milleks': ('. Selleks', '. Nendeks'),
        'milleni':('. Selleni', '. Nendeni'), 'millena':('. Sellena', '. Nendena'), 'milleta':('. Ilma selleta', '. Ilma nendeta'),
        'millega': ('. Sellega', '. Nendega'),

        'kus': ('. Seal', '. Seal')}

        

    def get_information(self, parsed_sentence_dic):
        '''
        Returns index of root of sentence and the word which is the root.'''
        root = None
        n = None
        for word, parsing in parsed_sentence_dic.items():
            dep_info = parsing.split(' ')[-1]
            n = dep_info.split('->')[0].strip('#') #(starts with 1 - not compatible with python indexing!)
            dependency = int(dep_info.split('->')[1])
            if dependency == 0:
                root = word
        return n, root


 
    def transformation(self, sent, n, head):

        def get_n_head(word, parsed_sentence_dic):
            '''
            Returns index of word and index of its head.
            '''
            info = parsed_sentence_dic[word]
            dependency = info.split(' ')[-1]
            n = dependency.split('->')[0].strip('#')
            head = dependency.split('->')[1]
            return n, head

        def get_subj(sent):
            '''
            Returns all subjects of sentence.
            '''
            subjects = []
            for word in sent:
                if '@SUBJ' in sent[word].split(" "):
                    subjects.append(word) 
            return subjects


        def get_verbs(sent):
            '''
            Returns all verbs of sentence.
            '''
            verbs = []
            for word in sent:
                if 'main' in sent[word].split(" "): 
                    verbs.append(word) 
            return verbs

        def get_root(sent):
        '''
        Returns root of sentence.
        '''
        for word in sent:
            if sent[word].split(" ")[-1] == 0:
                return word

#---------------------------------------------------------------------------------------------------------------------------------------------------------
        
        def conditional(new_sent_list, orig_sent_dic):
            ''' Replaces conditional verb forms in sentence by indicatives.
            Input: Sentence as list and dict with parsed information
            Output: Same sentence as list with conditional verbs replaced by according indicatives.
            '''

            #TO-DO: negative verb forms

            subj = None
            subject = None

            new_sent = []
            for word in new_sent_list:
                if word in orig_sent_dic:
                    if len(orig_sent_dic[word].split(' ')) >= 5:
                        if orig_sent_dic[word].split(' ')[4] == 'cond':
                            conj_index = get_n_head(word, orig_sent_dic)[0]
                            ksi_index = word.rfind('ksi')
                            if ksi_index > -1:
                                #long conditional form: remove ksi
                                if word[-4:] == 'ksid':
                                    subjects = get_subj(orig_sent_dic)
                                    for s in subjects:
                                        s_head = get_n_head(s, orig_sent_dic)[1]
                                        if s_head == conj_index:
                                            subject = subj

                                    if subject: 
                                        #choose subject that refers to verb
                                        pers = orig_sent_dic[subject].split(" ")[4] + orig_sent_dic[subject].split(" ")[5]
                                        if pers == 'ps3pl' or 'pl' in sent[subject].split(" "):
                                            word = word[:ksi_index]+'vad'
                                        else:
                                            word = word[:ksi_index]+'d'
                                else:
                                    word = word[:ksi_index]+word[ksi_index+3:]

                            #short conditional form: find out number and person of subject
                            else:
                                lemma = orig_sent_dic[word].split(' ')[0].strip('"')

                                #handling irregular verbs
                                if lemma in self.irregular_verbs:
                                    lemma = self.irregular_verbs[lemma]
                                

                                #find the subject that refers to the predicate
                                subj = get_subj(sent)
                                verb_index = get_n_head(word, orig_sent_dic)[0]

                                for s in subj:
                                    subj_head = get_n_head(s, orig_sent_dic)[1]
                                    if subj_head == verb_index:
                                        subject = s
                                        break

                                #generate verb form according to subject's person and number
                                if subject: 
                                    pers = orig_sent_dic[subject].split(' ')[4] + orig_sent_dic[subject].split(' ')[5]
                                    if pers == 'ps1sg':
                                        word = lemma + self.verb_suffixes[0]
                                    elif pers == 'ps2sg':
                                        word = lemma + self.verb_suffixes[1]
                                    elif pers == 'ps3sg' or 'sg' in sent[subject].split(" ") or 'sg' in pers:
                                        word = lemma + self.verb_suffixes[2]
                                    elif pers == 'ps1pl':
                                        word = lemma + self.verb_suffixes[3]
                                    elif pers == 'ps2pl':
                                        word = lemma + self.verb_suffixes[4]
                                    elif pers == 'ps3pl' or 'pl' in sent[subject].split(" ") or 'pl' in pers:
                                        word = lemma + self.verb_suffixes[5] 

                #correct uniquely irregular verb forms of 'to be'
                if word == 'oleb' or word == 'olevad':
                    word = 'on'

                new_sent.append(word)

            return new_sent

#--------------------------------------------------------------------------------------------------------------------------------------------------
        
        def relative_clause(sent):
            '''Turns relative subordinate clause into main clause starting with demonstrative pronoun.
            Input: Sentence with parsed information as dictionary.
            '''

            main_sent = True
            new_sent = []
            liste = []

            subj = get_subj(sent)
            verbs = get_verbs(sent)

            subject = None
            predicate = None
            demonstrative_index = None

            for word in sent:
                if main_sent == True:
                    word = word.strip(' ')        

                    #append word to sentence if not a relative pronoun
                    if word not in self.relpron:
                        if word != subject and word != predicate:
                            new_sent.append(word)    

                    #substitute relative pronouns by corresponding demonstrative pronoun
                    if word in self.relpron:
                        if 'pl' in sent[word].split(" "):
                            new_sent.append(self.relpron[word][1])
                            demonstrative_index = new_sent.index(self.relpron[word][1])
                        else:
                            new_sent.append(self.relpron[word][0])
                            demonstrative_index = new_sent.index(self.relpron[word][0])



            #make this a function if needed for other subordinate clauses
            if demonstrative_index: 
                subj_index = None
                adj_head = None

                for word in new_sent[demonstrative_index:]:
                    if word in subj:
                        subject = word
                        subj_index = get_n_head(subject, sent)[0]
                    if word in verbs:
                        predicate = word
                    if word in sent:
                        #in case that there's an adjective referring to the subject
                        if '@AN' in sent[word].split(' '):
                            adj = word
                            adj_head = get_n_head(adj, sent)[1]

                if subject in new_sent:            
                    new_sent.remove(subject)
                if predicate in new_sent:
                    new_sent.remove(predicate)

                if subj_index and adj_head:
                    if subj_index == adj_head:
                        if adj in new_sent:
                            new_sent.remove(adj)
                            new_sent.insert(demonstrative_index+1, adj)
                            new_sent.insert(demonstrative_index+2, subject)
                            new_sent.insert(demonstrative_index+3, predicate)
                
                else:
                    new_sent.insert(demonstrative_index+1, subject)
                    new_sent.insert(demonstrative_index+2, predicate)

            return new_sent

#----------------------------------------------------------------------------------------------------------------------------------------------------------
        
     
        def split_and(sent_list, orig_sent_dic):
            '''Splits sentence on 'and' if there is a subject and a conjugated verb before and after the conjunction.
            Input: Sentence as list and dict with parsed information
            Output: Multiple shorter sentences as list.
            '''
            new_sent_list = sent_list[:] #copy sent_list without reference

            index = None
            subj_after = False
            conjugated_verb_after = False
            subj_before = False
            conjugated_verb_before = False

            for word in new_sent_list:

                if word == 'ja' or word == 'ning':
                    index = new_sent_list.index(word)
                    new_sent_list[index] = '.'
                    if len(new_sent_list) > index+1:
                        new_sent_list[index+1] = new_sent_list[index+1].capitalize()

            subj = None
            conjugated_verb = None

            if index:
                subjects = get_subj(orig_sent_dic)
                verbs = get_verbs(orig_sent_dic)
                

                for word in sent_list[index:]:
                    if word in subjects:
                        subj_after = True
                    if word in verbs:
                        conjugated_verb_after = True

                for word in sent_list[:index]:
                    if word in subjects:
                        subj_before = True
                    if word in verbs:
                        conjugated_verb_before = True


            if subj_before and conjugated_verb_before and subj_after and conjugated_verb_after: 
                return new_sent_list
            else:
                return sent_list

            return new_sent_list
         
#----------------------------------------------------------------------------------------------------------------
       
        #main part of transformation: execute the single simplification steps
        rel = relative_clause(sent)
        rel_cond = conditional(rel, sent)
        rel_cond_and = split_and(rel_cond, sent)
        return rel_cond_and



    def simplify(self, sent, n, head):#, ant, comp=False, conf=False):        
        """
        Call the simplification process for all sentences in the document.
        """


        simplified_sent_list = self.transformation(sent, n, head)

        simplified_sent = ''
        simplified_sent_list = self.transformation(sent, n, head)

        for word in simplified_sent_list:
            if word:
                simplified_sent += word + ' '
        if simplified_sent:
            #last simplifying step: split sentences on 'aga' and 'ent'
            simplified_sent = simplified_sent.replace(', aga', '. Aga')
            simplified_sent = simplified_sent.replace(', ent', '. Ent')
            simplified_sent = simplified_sent.replace(', kuid', '. Kuid')


            #remove unnecessary punctuation
            simplified_sent = simplified_sent.replace(' .', '.')
            simplified_sent = simplified_sent.replace(' ?', '?')
            simplified_sent = simplified_sent.replace(' ,', ',')
            simplified_sent = simplified_sent.replace(' !', '!') 
            simplified_sent = simplified_sent.replace(' :', ':')
            simplified_sent = simplified_sent.replace(',.', '.')
            simplified_sent = simplified_sent.replace('( ', '(')
            simplified_sent = simplified_sent.replace(' )', ')')
            #remove superfluous white spaces
            simplified_sent = re.sub('\s+', ' ', simplified_sent) 

            return simplified_sent





        
#--------------------------------------------------------------------------------------------------------------------------------------------------------
def main():
    #sentences = [{'Paari': '"paar" L0 N card sg gen l cap @P> #1->3', 'nädala': '"nädal" L0 S com sg gen @<Q #2->1', 'eest': '"eest" L0 K post <gen> @ADVL #3->7', ',': '"," Z Com CLBC CLB CLB #36->36', '22.': '"22." L0 N ord sg ad <?> digit @AN> #5->6', 'novembril': '"november" Ll S com sg ad @ADVL #6->3', 'saatis': '"saat" Lis V main indic impf ps3 sg ps af <FinV> <NGP-P> <All> <PhVerb> <liiku> <0> @FMV #7->0', 'uudisteagentuur': '"uudiste_agentuur" L0 S com sg nom @SUBJ #8->7', 'AFP': '"AFP" L0 Y nominal cap @ADVL #9->7', 'üle': '"üle" L0 K pre <gen> @ADVL #29->33', 'kogu': '"kogu" L0 A pos @AN> #11->12', 'riigi': '"riik" L0 S com sg gen @NN> @OBJ #12->13', '24': '"24" L0 N card sg tr <?> digit @ADVL #13->7', 'tunniks': '"tund" Lks S com sg tr @<Q #14->13', 'laiali': '"laiali" L0 D @Vpart #15->15', 'fotoajakirjanikud': '"foto_aja_kirjanik" Ld S com pl nom @OBJ @ADVL #16->7', 'et': '"et" L0 J sub @J #18->19', 'jäädvustada': '"jäädvusta" Lda V main inf <NGP-P> <0> @IMV #19->7', 'brutaalsust': '"brutaal=sus" Lt S com sg part @OBJ #20->19', 'mida': '"mis" Lda P inter rel sg part @OBJ #22->24', 'endas': '"ise" Ls P refl sg in @ADVL #23->24', 'kätkeb': '"kätke" Lb V main indic pres ps3 sg ps af <FinV> <NGP-P> <In> <0> @FMV #24->20', 'ööpäev': '"öö_päev" L0 S com sg nom @SUBJ #25->24', 'Mehhikos': '"Mehhiko" Ls S prop sg in cap @ADVL #26->24','kus': '"kus" L0 D @ADVL #28->33', '250000': '"250000" L0 N card <?> digit @NN> @ADVL #30->33', 'inimese': '"inimene" L0 S com sg gen @<P #31->29', 'on': '"ole" L0 V aux indic pres ps3 sg ps af <FinV> <Intr> @FCV #32->33', 'mõrvatud': '"mõrva" Ltud V main partic past imps @IMV #33->26', 'alates': '"alates" L0 K pre <el> @ADVL #34->33', 'sellest': '"see" Lst P dem sg el @<P #35->34', 'kui': '"kui" L0 J sub @J #37->39', 'valitsus': '"valitsus" L0 S com sg nom @SUBJ #38->39', 'andis': '"and" Lis V main indic impf ps3 sg ps af <FinV> <NGP-P> <All> <Tr> @FMV #39->33', '2006': '"2006" L0 N card sg nom <?> digit @OBJ @ADVL #40->39', '.': '"." Z Fst CLB #48->48', 'aastal': '"aasta" Ll S com sg ad @ADVL #42->45', 'sõjaväele': '"sõja_vägi" Lle S com sg all @ADVL #43->45', 'korralduse': '"korraldus" L0 S com sg gen @OBJ #44->45', 'alustada': '"alusta" Lda V main inf <Part> <El> <Kom> @IMV #45->33', 'võitlust': '"võitlus" Lt S com sg part @OBJ #46->45', 'narkokartellidega': '"narko_kartell" Ldega S com pl kom @ADVL #47->45'}, {'Iga': '"iga" L0 P det sg nom cap @NN> #1->2', 'asi': '"asi" L0 S com sg nom @NN> @SUBJ @ADVL #2->4', 'Ciudad': '"Ciudad+" S prop cap @NN> @ADVL #3->5', 'Juárezis': '"Juárezis" L0 S prop sg nom cap @SUBJ #4->5', 'on': '"ole" L0 V main indic pres ps3 sg ps af <FinV> <Intr> <0> @FMV #5->0', 'äärmuslik': '"äärmuslik" L0 A pos sg nom @PRD #6->5', ':': '":" Z Col CLBC #7->7', 'põuane': '"põuane" L0 A pos sg nom @PRD #10->5', 'kliima': '"kliima" L0 S com sg gen @OBJ @NN> #11->11', ',': '"," Z Com #19->19', 'USA-Mehhiko': '"USA-Mehhiko" L0 S prop sg gen cap @NN> #13->11', 'piiri': '"piir" L0 S com sg gen @P> #14->11', 'ääres': '"ääres" L0 K post <gen> @ADVL #15->5', 'valitsevad': '"valitsev" Ld A pos pl nom @AN> #16->18', 'teravad': '"terav" Ld A pos pl nom @AN> #17->18', 'kontrastid': '"kontrast" Ld S com pl nom @OBJ @SUBJ #18->5', 'vägivald': '"vägi_vald" L0 S com sg nom @<NN @PRD @SUBJ #20->18', '.': '"." Z Fst CLB #21->21'}, {'Kunagi': '"kunagi" L0 D cap @ADVL #1->2', 'nimetati': '"nimeta" Lti V main indic impf imps af <FinV> <NGP-P> <Tr> <0> @FMV #2->0', 'seda': '"see" Lda P dem sg part @NN> #3->4', 'kohta': '"koht" L0 S com sg part @OBJ #4->2', 'maailma': '"maa_ilm" L0 S com sg gen @NN> #5->6', 'mõrvapealinnaks': '"mõrva_pea_linn" Lks S com sg tr @ADVL #6->2', ',': '"," Z Com CLB CLB CLB #7->7', 'kuid': '"kuid" L0 J crd @J #8->18', 'nüüdseks': '"nüüdne" Lks A pos sg tr @ADVL #9->18', 'on': '"ole" L0 V aux indic pres ps3 pl ps af <FinV> <Intr> @FCV #10->18', 'teised': '"teine" Ld P dem pl nom @NN> #11->12', 'linnad': '"linn" Ld S com pl nom @SUBJ #12->18', 'oma': '"oma" L0 P pos sg gen @NN> #13->14', 'verisuselt': '"veri=sus" Llt S com sg abl @ADVL #14->18', 'Ciudad': '"Ciudad+" S prop cap @NN> @ADVL #15->18', 'mööda': '"mööda" L0 D @Vpart #17->18', 'läinud': '"mine" Lnud V main partic past ps <Intr> <PhVerb> <mööda> <0> @IMV #18->2', '.': '"." Z Fst CLB #19->19'}, {'36-aastasele': '"36_aastane" Lle A pos sg all @AN> #1->2', 'fotoajakirjanikule': '"foto_aja_kirjanik" Lle S com sg all @ADVL #2->5', 'Hérika': '"Hérika" L0 S prop sg nom cap @NN> #3->4', 'Martínezile': '"Martínezile" L0 S prop sg nom cap @SUBJ #4->5', 'on': '"ole" L0 V aux indic pres ps3 pl ps af <FinV> <Intr> @FCV #27->30', 'see': '"see" L0 P dem sg nom @NN> #6->7', 'kodu': '"kodu" L0 S com sg nom "ko" partic @PRD #7->5', '.': '"." Z Fst CLB #35->35', '': '""" Z Quo CLB CLC #32->32', 'Minu': '"mina" L0 P pers ps1 sg gen cap CLB @NN> #10->11', 'pildid': '"pilt" Ld S com pl nom @SUBJ #11->12', 'jutustavad': '"jutusta" Lvad V main indic pres ps3 pl ps af <FinV> <NGP-P> @FMV #12->33', 'lugusid': '"lugu" Lsid S com pl part @OBJ #13->12', 'emadest': '"ema" Ldest S com pl el @ADVL #14->12', ',': '"," Z Com CLBC #31->31', 'kes': '"kes" L0 P inter rel pl nom @OBJ #26->30', 'kaotanud': '"kaota" Lnud V main partic past ps <NGP-P> <In> @IMV #18->14', 'tütre': '"tütar" L0 S com sg gen @OBJ #19->18', 'massimõrvade': '"massi_mõrv" Lde S com pl gen @NN> #21->22', 'ohvritest': '"ohver" Ltest S com pl el @ADVL #22->18', 'kogukondadest': '"kogukond" Ldest S com pl el @ADVL #24->18', 'vägivalla': '"vägi_vald" L0 S com sg gen @P> #28->29', 'tõttu': '"tõttu" L0 K post <gen> @ADVL #29->30', 'hüljatud': '"hülga" Ltud V main partic past imps @IMV #30->24', 'lausub': '"lausu" Lb V main indic pres ps3 sg ps af <FinV> <NGP-P> CLB @FMV #33->0', 'naine': '"naine" L0 S com sg nom @SUBJ #34->33'}, {'Selles': '"see" Ls P dem sg in cap @NN> #1->2', 'linnas': '"linn" Ls S com sg in @ADVL #2->5', 'võib': '"või" Lb V mod indic pres ps3 sg ps af <FinV> @FCV #3->5', 'surm': '"surm" L0 S com sg nom @SUBJ @OBJ #4->5', 'tabada': '"taba" Lda V main inf <NGP-P> <0> @IMV #5->0', 'igaühte': '"iga_üks" L0 P det sg part @SUBJ @OBJ #6->5', 'igal': '"iga" Ll P det sg ad @NN> #7->8', 'hetkel': '"hetk" Ll S com sg ad @ADVL #8->5', ':': '":" Z Col CLBC CLB #9->9', 'kartellisõja': '"kartelli_sõda" L0 S com sg gen @P> #10->13', 'või': '"või" L0 J crd @J #11->12', 'narkoäri': '"narko_äri" L0 S com sg gen @P> #12->10', 'vastu': '"vastu" L0 K post <gen> @ADVL #13->14', 'suunatud': '"suuna=tud" L0 A pos partic <tud> "suuna" partic @AN> #14->15', 'operatsioonide': '"operatsioon" Lde S com pl gen @P> #15->16', 'eest': '"eest" L0 K post <gen> @ADVL #16->19', 'pole': '"ole" L0 V aux indic pres ps neg <FinV> <Intr> @FCV #17->19', 'keegi': '"keegi" L0 P indef sg nom @OBJ #18->19', 'kaitstud': '"kaits" Ltud V main partic past imps <Part> @IMV #19->5', '.': '"." Z Fst CLB #20->20'}, {'Vahel': '"vahel" L0 D cap @ADVL #1->2', 'on': '"ole" L0 V main indic pres ps3 pl ps af <FinV> <Intr> <0> @FMV #2->0', 'süütud': '"süütu" Ld A pos pl nom @AN> #3->4', 'tsiviilisikud': '"tsiviil_isik" Ld S com pl nom @SUBJ #4->2', 'keset': '"keset" L0 K pre <part> @ADVL #5->2', 'tulevahetust': '"tule_vahetus" Lt S com sg part @<P #6->5', '.': '"." Z Fst CLB #7->7'}, {'12': '"12" L0 N card <?> digit @ADVL #1->3', 'aasta': '"aasta" L0 S com sg gen @<Q #2->1', 'eest': '"eest" L0 K post <gen> @ADVL #3->4', 'kolis': '"koli" Ls V main indic impf ps3 sg ps af <FinV> <0> @FMV #4->0', 'Julio': '"Julio" L0 S prop sg nom cap @NN> #5->6', 'Cesar': '"Cesar" L0 S prop sg nom cap @NN> #6->7', 'Aguilar': '"Aguilar" L0 S prop sg nom cap @NN> #7->8', 'Põhja-Mehhiko': '"Põhja-Mehhiko" L0 S prop sg gen cap @NN> @OBJ #8->4', 'tööstuslinna': '"tööstus_linn" L0 S com sg adit @NN> @ADVL #9->4', 'Monterreysse': '"Monterrey" Lsse S prop sg ill cap @ADVL #10->4', 'ning': '"ning" L0 J crd CLBC CLB CLB CLBC @J #11->13', 'nüüd': '"nüüd" L0 D @ADVL #12->13', 'jäädvustab': '"jäädvusta" Lb V main indic pres ps3 sg ps af <FinV> <NGP-P> @FMV #13->4', '41-aastane': '"41_aastane" L0 A pos sg nom @AN> #14->15', 'mees': '"mees" L0 S com sg nom @SUBJ #15->13', 'sealset': '"sealne" Lt A pos sg part @AN> #16->17', 'vägivalda': '"vägi_vald" L0 S com sg part @OBJ #17->13', '.': '"." Z Fst CLB #18->18'}]
    #sentences = [{'See': '"see" L0 P dem sg nom cap @SUBJ #1->2', 'on': '"ole" L0 V main indic pres ps3 sg ps af <FinV> <Intr> <0> @FMV #2->0', 'tüdruk': '"tüdruk" L0 S com sg nom @PRD #3->2', ',': '"," Z Com CLB CLB #4->4', 'keda': '"kes" Lda P inter rel sg part @OBJ #5->7', 'ma': '"mina" L0 P pers ps1 sg nom @SUBJ #6->7', 'armastan': '"armasta" Ln V main indic pres ps1 sg ps af <FinV> <Part-P> <InfP> <0> @FMV #7->3', '.': '"." Z Fst CLB #8->8'}, {'See': '"see" L0 P dem sg nom cap @SUBJ #1->2', 'on': '"ole" L0 V main indic pres ps3 sg ps af <FinV> <Intr> <0> @FMV #2->0', 'poiss': '"poiss" L0 S com sg nom @PRD #3->2', ',': '"," Z Com CLB CLB #4->4', 'keda': '"kes" Lda P inter rel sg part @OBJ #5->7', 'ma': '"mina" L0 P pers ps1 sg nom @SUBJ #6->7', 'armastan': '"armasta" Ln V main indic pres ps1 sg ps af <FinV> <Part-P> <InfP> <0> @FMV #7->3', '.': '"." Z Fst CLB #8->8'}]
    #sentences = [{'See': '"see" L0 P dem sg nom cap @SUBJ #1->2', 'on': '"ole" L0 V main indic pres ps3 sg ps af <FinV> <Intr> @FMV #10->7', 'tüdruk': '"tüdruk" L0 S com sg nom @PRD #3->2', ',': '"," Z Com CLB CLB #12->12', 'keda': '"kes" Lda P inter rel sg part @OBJ #13->15', 'ma': '"mina" L0 P pers ps1 sg nom @SUBJ #14->15', 'armastan': '"armasta" Ln V main indic pres ps1 sg ps af <FinV> <Part-P> <InfP> <0> @FMV #15->11', 'ja': '"ja" L0 J crd CLB CLB CLBC @J #8->10', 'see': '"see" L0 P dem sg nom @SUBJ #9->10', 'poiss': '"poiss" L0 S com sg nom @PRD #11->10', '.': '"." Z Fst CLB #16->16'}]
    #sentences = [{'See': '"see" L0 P dem sg nom cap @SUBJ #1->2', 'on': '"ole" L0 V main indic pres ps3 sg ps af <FinV> <Intr> @FMV #10->7', 'tüdruk': '"tüdruk" L0 S com sg nom @PRD #3->2', ',': '"," Z Com CLB CLB #12->12', 'keda': '"kes" Lda P inter rel sg part @OBJ #13->15', 'ma': '"mina" L0 P pers ps1 sg nom @SUBJ #14->15', 'armastan': '"armasta" Ln V main indic pres ps1 sg ps af <FinV> <Part-P> <InfP> <0> @FMV #15->11', 'ja': '"ja" L0 J crd CLB CLB CLBC @J #8->10', 'see': '"see" L0 P dem sg nom @SUBJ #9->10', 'poiss': '"poiss" L0 S com sg nom @PRD #11->10', '.': '"." Z Fst CLB #16->16'}, {'See': '"see" L0 P dem sg nom cap @SUBJ #1->2', 'on': '"ole" L0 V main indic pres ps3 sg ps af <FinV> <Intr> <0> @FMV #2->0', 'koht': '"koht" L0 S com sg nom @PRD #3->2', ',': '"," Z Com CLB CLB #4->4', 'kus': '"kus" L0 D @ADVL #5->7', 'ma': '"mina" L0 P pers ps1 sg nom @SUBJ #6->7', 'elan': '"ela" Ln V main indic pres ps1 sg ps af <FinV> <Intr> <In> <Ad> <0> @FMV #7->3', '.': '"." Z Fst CLB #8->8'}, {'See': '"see" L0 P dem sg nom cap @SUBJ #1->2', 'on': '"ole" L0 V main indic pres ps3 sg ps af <FinV> <Intr> <0> @FMV #2->0', 'tüdruk': '"tüdruk" L0 S com sg nom @PRD #3->2', ',': '"," Z Com CLB CLB #4->4', 'kellega': '"kes" Lga P inter rel sg kom @ADVL #5->8', 'ma': '"mina" L0 P pers ps1 sg nom @SUBJ #6->8', 'ballile': '"ball" Lle S com sg all @ADVL #7->8', 'lähen': '"mine" Ln V main indic pres ps1 sg ps af <FinV> <Intr> <0> @FMV #8->3', '.': '"." Z Fst CLB #9->9'}, {'Nad': '"tema" Ld P pers ps3 pl nom cap @SUBJ #1->2', 'on': '"ole" L0 V main indic pres ps3 pl ps af <FinV> <Intr> <0> @FMV #2->0', 'inimesed': '"inimene" Ld S com pl nom @PRD #3->2', ',': '"," Z Com CLB CLB #4->4', 'kellega': '"kes" Lga P inter rel pl kom @ADVL #5->8', 'ma': '"mina" L0 P pers ps1 sg nom @SUBJ #6->8', 'ballile': '"ball" Lle S com sg all @ADVL #7->8', 'lähen': '"mine" Ln V main indic pres ps1 sg ps af <FinV> <Intr> <0> @FMV #8->3', '.': '"." Z Fst CLB #9->9'}]
    #sentences = [{'See': '"see" L0 P dem sg nom cap @SUBJ #1->2', 'on': '"ole" L0 V main indic pres ps3 sg ps af <FinV> <Intr> <0> @FMV #2->0', 'tüdruk': '"tüdruk" L0 S com sg nom @PRD #3->2', ',': '"," Z Com CLB CLB #12->12', 'keda': '"kes" Lda P inter rel sg part @OBJ #5->7', 'armastan': '"armasta" Ln V main indic pres ps1 sg ps af <FinV> <Part-P> <InfP> <0> @FMV #7->3', 'ma': '"mina" L0 P pers ps1 sg nom @SUBJ #6->7','ja': '"ja" L0 J crd CLB CLB CLBC @J #8->10', 'see': '"see" L0 P dem sg nom @SUBJ #9->10', 'on          ': '"ole" L0 V main indic pres ps3 sg ps af <FinV> <Intr> @FMV #10->7', 'poiss': '"poiss" L0 S com sg nom @PRD #11->10', 'keda ': '"kes" Lda P inter rel sg part @OBJ #13->15', 'armastan          ': '"armasta" Ln V main indic pres ps1 sg ps af <FinV> <Part-P> <InfP> <0> @FMV #15->11', 'ma          ': '"mina" L0 P pers ps1 sg nom @SUBJ #14->15','.': '"." Z Fst CLB #16->16'}, {'See': '"see" L0 P dem sg nom cap @SUBJ #1->2', 'on': '"ole" L0 V main indic pres ps3 sg ps af <FinV> <Intr> <0> @FMV #2->0', 'koht': '"koht" L0 S com sg nom @PRD #3->2', ',': '"," Z Com CLB CLB #4->4', 'kus': '"kus" L0 D @ADVL #5->7', 'ma': '"mina" L0 P pers ps1 sg nom @SUBJ #6->7', 'elan': '"ela" Ln V main indic pres ps1 sg ps af <FinV> <Intr> <In> <Ad> <0> @FMV #7->3', '.': '"." Z Fst CLB #8->8'}, {'See': '"see" L0 P dem sg nom cap @SUBJ #1->2', 'on': '"ole" L0 V main indic pres ps3 sg ps af <FinV> <Intr> <0> @FMV #2->0', 'tüdruk': '"tüdruk" L0 S com sg nom @PRD #3->2', ',': '"," Z Com CLB CLB #4->4', 'kellega': '"kes" Lga P inter rel sg kom @ADVL #5->8', 'ma': '"mina" L0 P pers ps1 sg nom @SUBJ #6->8', 'ballile': '"ball" Lle S com sg all @ADVL #7->8', 'lähen': '"mine" Ln V main indic pres ps1 sg ps af <FinV> <Intr> <0> @FMV #8->3', '.': '"." Z Fst CLB #9->9'}, {'Nad': '"tema" Ld P pers ps3 pl nom cap @SUBJ #1->2', 'on': '"ole" L0 V main indic pres ps3 pl ps af <FinV> <Intr> <0> @FMV #2->0', 'inimesed': '"inimene" Ld S com pl nom @PRD #3->2', ',': '"," Z Com CLB CLB #4->4', 'kellega': '"kes" Lga P inter rel pl kom @ADVL #5->8', 'ma': '"mina" L0 P pers ps1 sg nom @SUBJ #6->8', 'ballile': '"ball" Lle S com sg all @ADVL #7->8', 'lähen': '"mine" Ln V main indic pres ps1 sg ps af <FinV> <Intr> <0> @FMV #8->3', '.': '"." Z Fst CLB #9->9'}]
    sentences = [{'See': '"see" L0 P dem sg nom cap @SUBJ #1->2', 'oleks': '"ole" L0 V main cond pres ps3 sg ps af <FinV> <Intr> <0> @FMV #2->0', 'asi': '"asi" L0 S com sg nom @PRD #3->2', ',': '"," Z Com CLB CLB #4->4', 'mida': '"mis" Lda P inter rel sg part @OBJ #5->7', 'ma': '"mina" L0 P pers ps1 sg nom @SUBJ #6->7', 'armastan': '"armasta" Ln V main indic pres ps1 sg ps af <FinV> <Part-P> <InfP> <0> @FMV #7->3', '.': '"." Z Fst CLB #8->8'}, {'Mida': '"mis" Lda P inter rel sg part cap @OBJ #1->3', 'sa': '"sina" L0 P pers ps2 sg nom @SUBJ #2->3', 'armastad': '"armasta" Ld V main indic pres ps2 sg ps af <FinV> <Part-P> <InfP> <0> @FMV #3->0', '?': '"?" Z Int CLB #4->4'}, {'Ma': '"mina" L0 P pers ps1 sg nom cap @SUBJ #1->2', 'küsisin': '"küsi" Lsin V main indic impf ps1 sg ps af <FinV> <NGP-P> <Abl> <0> @FMV #2->0', 'temalt': '"tema" Llt P pers ps3 sg abl @ADVL #3->2', ',': '"," Z Com CLB CLB #4->4', 'mida': '"mis" Lda P inter rel sg part @OBJ #5->7', 'ta': '"tema" L0 P pers ps3 sg nom @SUBJ #6->7', 'armastab': '"armata" Lb V main indic pres ps3 sg ps af <FinV> <0> @FMV #7->3', '.': '"." Z Fst CLB #8->8'}, {'Ta': '"tema" L0 P pers ps3 sg nom cap @SUBJ #1->2', 'vastas': '"vasta" Ls V main indic impf ps3 sg ps af <FinV> <NGP-P> <All> <0> @FMV #2->0', ':': '":" Z Col CLBC CLB #3->3', '': '""" Z Quo CLBC CLB CLO #4->4', 'Ma': '"mina" L0 P pers ps1 sg nom cap CLB @SUBJ #5->6', 'armastan': '"armata" Ln V main indic pres ps1 sg ps af <FinV> @FMV #6->2', 'sind': '"sina" Ld P pers ps2 sg part @OBJ #7->6', '.': '"." Z Fst CLB #8->8', '          ': '""" Z Quo CLB CLC #9->9'}]
    simp_obj = Simplify(sentences)
    for sent in sentences:
        n = simp_obj.get_information(sent)[0]
        head = simp_obj.get_information(sent)[1]
        x = simp_obj.simplify(sent, n, head)
        print(x)

if __name__ == '__main__':
    main()
