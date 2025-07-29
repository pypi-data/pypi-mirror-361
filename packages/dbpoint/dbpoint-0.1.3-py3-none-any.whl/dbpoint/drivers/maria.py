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
        return 'MARIA'
    
    
    def connect(self, profile: dict) -> int:
        
        if self.conn is not None: # kui ühendus on olemas, siis ei võta ühendust
            return 0
        
        try:
            import mariadb # https://github.com/sqlanywhere/sqlanydb/blob/master/sqlanydb.py
        except ImportError:
            raise Exception(f"Driver package not installed. Do pip install mariadb")
            #raise unified.DataDriverNotInstalled('tee: pip install mariadb')
        
        conn_dict = self.profile_to_dict(profile)
        self.conn = mariadb.connect(**conn_dict)
        self.conn.autocommit = False # mysql/mariadb iseärasus (default on true)
        #print('now MariaDB is connected')
        if profile.get('version', 10) < 10: # vaikeversioonina eeldame uuemat, nt 8. aga kuni mysql ver 5-ni oli varjestaja kaldkriips (mitte ülakoma)
            self.apostrophe_escape = '\\'
        #self.error = mariadb.Error
        return 1
    
    def profile_to_dict(self, profile: dict) -> dict:
        
        conn_args = {}
        
        conn_args['user'] = profile.get('username', 'xxxxx')
        conn_args['password'] = profile.get('password', 'xxxxx')
        conn_args['database'] = profile.get('database', 'xxxxx')
        conn_args['host'] = profile.get('host', 'localhost')
        conn_args['port'] = profile.get('port', 3306)
        
        return conn_args
        