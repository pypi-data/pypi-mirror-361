'''
Konkreetse DB Lib 2.0 draiveri wrapper-klass, mis omab tarkust, 
a) kuidas ühendusprofiili andmetest teha ühenduseks vajalik struktuur ja ühendust võtta
b) kuidas RDBM draiveri spetsiifilised vead teisendada meie universaalseteks vigadeks 
    (selleks, et kasutaja ei peaks mooduleid importima ega urgitsema teostaja detaildies) 
'''

from dbpoint.datadriver import DataDriverGeneric # ülemklass (fn-id run, disconnect)
#import datacontroller.datacontroller_exceptions as unified
from dbpoint import logging

class DataDriver(DataDriverGeneric):
    
    map_of_exceptions = {
        'SyntaxError' : Exception #  unified.DataDriverSyntaxException
        , 'UndefinedTable' : Exception # unified.DataDriverUndefinedTable
        }
    
    def me(self) -> str:
        return 'MSSQL'
    
    
    def connect(self, profile: dict) -> int:
        
        if self.conn is not None: # kui ühendus on olemas, siis ei võta ühendust
            return 0
        
        try:
            import pymssql # NB! pidav olema ühilduv kuni python 3.8 (seega kasutamisel olla ettevaatlik, vajadusel läbi ODBC)
        except ImportError:
            #raise unified.DataDriverNotInstalled('tee: pip install pymssql')
            raise Exception(f"Driver package not installed. Do pip install pymssql")
        
        conn_dict = self.profile_to_dict(profile)
        self.conn = pymssql.connect(**conn_dict)
        #self.error = pymssql.Error
        return 1
        
    def profile_to_dict(self, profile: dict) -> dict:
        
        conn_args = {}
        
        conn_args['database'] = profile.get('database', 'xxxxx').strip("/") # kaldkriipsude eemaldamise vajadus tulenes vist ühest teisest sisendist ja nüüd üle?
        
        # MS SQL host on host+port
        host = profile.get('host', 'localhost')
        port = profile.get('port', 1433)
        conn_args['host'] = f"{host}:{port}" # koos pordiga!
        
        # Trusted_Connection=yes jaoks anname ilma kasutajanimeta-paroolita (ei toimi linuxis)
        # trusted connection tähendab, et baasi kasutajaks on windowsi kasutaja
        if profile.get('password', '') != '': # ja lepime endaga kokku, et kui konfis pole parooli antud, siis ongi soov trusted connection järele
            conn_args['user'] = profile.get('username', 'xxxxx')
            conn_args['password'] = profile.get('password', 'xxxxx')
        
        return conn_args
        
