'''
Konkreetse DB Lib 2.0 draiveri wrapper-klass, mis omab tarkust, 
a) kuidas ühendusprofiili andmetest teha ühenduseks vajalik struktuur ja ühendust võtta
b) kuidas RDBM draiveri spetsiifilised vead teisendada meie universaalseteks vigadeks 
    (selleks, et kasutaja ei peaks mooduleid importima ega urgitsema teostaja detaildies) 

Nõuded: paigaldatud on ASA client (seal on dbcapi.dll ja sõltuvused)
https://help.sap.com/docs/SUPPORT_CONTENT/sqlany/3362971128.html
Hüpotees: võib võtta uusima (ver 17), saadaval on ka 16 ja 12.

'''

from dbpoint.datadriver import DataDriverGeneric # ülemklass (fn-id run, disconnect)
#import datacontroller.datacontroller_exceptions as unified
#from dbpoint import logging


class DataDriver(DataDriverGeneric):
    
    map_of_exceptions = {
        'SyntaxError' : Exception #  unified.DataDriverSyntaxException
        , 'UndefinedTable' : Exception #  unified.DataDriverUndefinedTable
        , 'IntegrityError' : Exception # unified.DataDriverSyntaxException # fixme
        , 'ProgrammingError' : Exception # unified.DataDriverSyntaxException # fixme
        , 'OperationalError' : Exception # unified.DataDriverSyntaxException # fixme
        , 'InternalError' : Exception # unified.DataDriverSyntaxException # fixme
        , 'DataError' : Exception # unified.DataDriverSyntaxException # fixme
        , 'DatabaseError' : Exception # unified.DataDriverSyntaxException # fixme // see on üldine viga, eelmiste üldistus 
        }
    
    def me(self) -> str:
        return 'ASA'
    
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
    
    
    
    
    def connect(self, profile: dict) -> int:
        
        if self.conn is not None: # kui ühendus on olemas, siis ei võta ühendust
            return 0
        
        try:
            import sqlanydb # https://github.com/sqlanywhere/sqlanydb/blob/master/sqlanydb.py
        except ImportError:
            raise Exception(f"Driver package not installed. Do pip install sqlanydb (and install client-side drivers)")
            #raise unified.DataDriverNotInstalled('tee: pip install sqlanydb (ja paigalda ASA kliendifailid)')
        
        conn_dict = self.profile_to_dict(profile)
        self.conn = sqlanydb.connect(**conn_dict)
        #print('now ASA is connected')
        self.apostrophe_escape = '\\'
        # vb tõsta ka versiooniklassid profile -> driver/self
        #self.error = sqlanydb.Error
        return 1
        
    def profile_to_dict(self, profile: dict) -> dict:
        
        conn_args = {}
        conn_args['uid'] = profile.get('username', 'xxxxx')
        conn_args['pwd'] = profile.get('password', 'xxxxx')
        conn_args['eng'] = profile.get('engine', 'xxxxx')
        conn_args['dbn'] = profile.get('database', 'xxxxx')
        
        # ja eraldi võti TCP ühenduste spetsiifika jaoks
        port = profile.get('port', 2638)
        host = profile.get('host', 'localhost')
        conn_args['links'] = f"tcpip(host={host};port={port})"
        
        return conn_args
