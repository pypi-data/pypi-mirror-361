'''
Konkreetse DB Lib 2.0 draiveri wrapper-klass, mis omab tarkust, 
a) kuidas ühendusprofiili andmetest teha ühenduseks vajalik struktuur ja ühendust võtta
b) kuidas RDBM draiveri spetsiifilised vead teisendada meie universaalseteks vigadeks 
    (selleks, et kasutaja ei peaks mooduleid importima ega urgitsema teostaja detaildies) 
'''

#from dbpoint.datadriver import DataDriverGeneric # ülemklass (fn-id run, disconnect)
#from datadriver import DataDriverGeneric # ülemklass (fn-id run, disconnect)


#class DataDriver(DataDriverGeneric):
class DataDriver():
    map_of_exceptions = {
        'SyntaxError':  Exception # unified.DataDriverSyntaxException
        , 'UndefinedTable' : Exception # unified.DataDriverUndefinedTable
        , 'InvalidSchemaName' : Exception # unified.DataDriverInvalidSchemaName
        }
    
    type_mapper = {
        20 : 'BIGINT'
        , 1184 : 'TIMESTAMPTZ'
        , 23 : 'INT'
        , 3802 : 'JSONB' #(jsonb tehakse pythoni json stringiks, kus on ülakomad jutumärkide asemel ja ei saa tagasi kirjutada) 
        , 16 : 'BOOLEAN'
        , 1043 : 'TEXT' # varchar tasub niikuinii pikemaks teha, lisaks on tüütu saada universaalselt kätte pikkust 
        , 25 :'TEXT'
        , 1700 : 'NUMERIC'
    }
    
    def __init__(self):
        #self.created = datetime.now()
        self.conn = None 
    
    def me(self) -> str:
        return 'PG'
    
    def commit(self):
        if self.conn:
            self.conn.commit()
    

    def connect(self, profile: dict) -> int:
        print(profile)
        if self.conn is not None: # kui ühendus on olemas, siis ei võta ühendust
            return 0
        
        try:
            import psycopg2
        except:
            # raise -1
            #raise unified.DataDriverNotInstalled('tee: pip install psycopg2')
            raise Exception(f"Driver package not installed. Do pip install psycopg2")
        
        # receive everything in the postgres string representation
        #psycopg2.extensions.string_types.clear() # SEE POLE HEA MÕTE! JSONB tüübiga on suur jama, ja vb on ka date/time omadega
        bad_keys = [199, 114, 3802, 3807, 16, 1114, 1184, 1083, 1266, 1082, 704, 1186]
        for bad_key in bad_keys:
            if bad_key in psycopg2.extensions.string_types: # teisel sama draiveriga ühendusel
                del psycopg2.extensions.string_types[bad_key]
        #for k in psycopg2.extensions.string_types.keys():
        #    print(f"{k} = {psycopg2.extensions.string_types[k]}")
        
        conn_url = self.profile_to_url(profile)
        self.conn: psycopg2.extensions.connection = psycopg2.connect(conn_url) # on error return -1?
        #self.error = psycopg2.Error
        return 1
    
    def profile_to_url(self, profile: dict) -> str:
        params = [] # küsimärgi-tagune (omavahel eraldatud ampersandiga)
        #if 'appname' in profile:
        #    params.append(f"application_name={profile['appname']}")
        
        if profile.get('extra'):
            for key, value in profile['extra'].items(): # FIXME -- make it more secure!!!
                params.append(f"{key}={value}")
        
        parts = [] # maksimaalselt 2 osa
        parts.append(f"postgresql://{profile['username']}:{profile['password']}@{profile['host']}:{profile['port']}/{profile['database']}")
        if(params):
            parts.append('&'.join(params))
        
        connection_url = '?'.join(parts)
        if profile.get('debug', False):
            print(connection_url) # ohtlik!
        return connection_url

    def escape(self, cell_value, data_class, needs_escape):
        '''
        Postgres jaoks üle kirjutatud funktsioon, et saaks topelt-dollar ümbritsemise meetodiga lahendada paljud murekohad
        Ja juhusk, kui algväärtuses on topelt-dollar sees, siis proovime midagi muud 
        (paha on ainult see, et praegune algoritm proovib kõik läbi selmet esimese mitteleidumise korral rõõmustada ja katkestada) 
        '''
        if cell_value is None:
            return 'NULL'
        if data_class == 'BOOLEAN':
            return 'TRUE' if cell_value == 't' else 'FALSE' 
        if needs_escape:
            # uue märgistuse abil ümbritsemise meetod (võtame kandidaatidest esimese, mida ei leidu väärtuses)
            surround = [surround_candidate for surround_candidate in ['$xx$', '$xiyaz$', '$sUvaLinE$'] if surround_candidate not in str(cell_value)] [0]
            return f"{surround}{cell_value}{surround}"
            # vs liht-asendamise meetod
            # return (str(cell)).replace("'", self.apostrophe_escape)
        else:
            return f"{cell_value}"

    def from_file(self, file_path: str, **kwargs) -> int:
        import os
        if not os.path.file_exists(file_path):
            raise Exception # fixme, parem valida 
        
        
        #curTrg = self.getCursor(idx2, True) # kui ühendus on aegunud, siis loob uue ühenduse
        #curTrg.copy_expert(trgSql, file_handler, size=self.bufferSize)
        #file_handler.close()
        #curTrg.close()
        #self.doCommit(idx2, True) # self.conns[idx2]['conn'].commit()
        
        
        
    def to_file(self, query: str, file_path: str, **kwargs) -> int:
        
        universal = False
        
        # kaks lahendusteed: universaalne (teeme päringu ja kirjutame faili tehes ise kõik varjestused) ja postgre pakutav copy_expert
        if universal:
            try:
                file_handler = open(file_path, 'w')    # avada lugemiseks ('w' kirjutab üle, kui fail olemas) 
            except Exception as e1:
                # siia logimine?
                number_of_rows = -1 # ??? raise ju parem?!
                ...
                raise e1
            
            rs = self.run(query, True) # this loads the entire table into memory - which will crash your machine for a big table!
            number_of_rows = 0
            for row in rs:
                file_handler.write("\t".join([str(cell) for cell in row]) + "\n")
                number_of_rows += 1
            
            file_handler.close()
            
        else:
            number_of_rows = self.to_file_postgres(query, file_path)
        
        return number_of_rows
        
    def to_file_postgres(self, query: str, file_path: str, **kwargs) -> int:
        buffer_size = 2**14 # 16384 (vaikimisi on 8192)
        control = """WITH (FORMAT 'csv', DELIMITER E'\t', NULL '(NULL)', QUOTE '\"', ESCAPE '\\', ENCODING 'utf8')"""

        try:
            file_handler = open(file_path, 'w')    # avada lugemiseks ('w' kirjutab üle, kui fail olemas) 
        except Exception as e1:
            ...
            raise e1
        
        cur = self.conn.cursor()
        copy_to_expression = f"COPY ({query}\n) TO STDOUT {control}"
        try:
            cur.copy_expert(copy_to_expression, file_handler, size=buffer_size)
            number_of_rows = cur.rowcount
            self.conn.commit()
        except Exception as e1:
            print(e1)
            self.conn.rollback()
            number_of_rows = -1
        finally:
            cur.close()
            
        file_handler.close()
        # väike mure: kuidas me teame, mitu kirjet kirjutati
        return number_of_rows
        
        
        
        