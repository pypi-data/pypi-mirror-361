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
        'SyntaxError' : Exception # unified.DataDriverSyntaxException
        , 'UndefinedTable' : Exception # unified.DataDriverUndefinedTable
        }
    
    def me(self) -> str:
        return 'ODBC'
    
    
    def connect(self, profile: dict) -> int:
        
        if self.conn is not None: # kui ühendus on olemas, siis ei võta ühendust
            return 0
        
        try:
            import pyodbc
        except ImportError:
            #raise unified.DataDriverNotInstalled('tee: pip install pyodbc')
            raise Exception(f"Driver package not installed. Do pip install pyodbc")
        
        conn_string = self.profile_to_string(profile) # https://www.connectionstrings.com/
        self.conn = pyodbc.connect(**conn_string)
        #self.error = pyodbc.Error
        return 1
        
    def profile_to_string(self, profile: dict) -> str:
        
        # anname eelistuse valmis tehtud (draiverile sobivale) connect-stringile, kui see on olemas.
        # PS. Connectstring peab vastama pigem ODBC draiverile (kui tootele), sest see suhtleb edasi tootega
        
        if 'conn_string' in profile:
            return profile['conn_string']
        
        
        conn_str = ''
        
        # kui polnud antud tervet, siis proovime juhutarkusega stringi kokku saada (ja see on üsna hiromantia, kuna kõigil tootjatel on omad kiiksud)
        product = profile.get('dialect', 'general')
        if product == 'general':
            if 'driver' in profile: # nn keerukam lähenemine, mis võtab ainult ODBCINST draveri info ja lisame baasi, hosti, pordi ja kasutaja 
                conn_str = f"Driver={{{driver}}};Host={profile['host']};Database={profile['database']};Port={profile['port']};UID={profile['username']};PWD={profile['password']}"
            else: # lühike variant, kus ODBC-s on DSN kirjeldatud ja lisame ainult kasutajanime ja parooli
                conn_str = f"DSN={profile['database']};UID={profile['username']};PWD={profile['password']}"
        if product in ('mssql', 'progress'):
            if profile['password'] == '':
                creds = "Trusted_Connection=yes;Uid=auth_window"
            else:
                creds = f"UID={profile['username']};PWD={profile['password']}"
                
            if 'driver' in profile: # nn keerukam lähenemine, mis võtab ainult ODBCINST draveri info ja lisame baasi, hosti, pordi ja kasutaja 
                conn_str = f"Driver={{{driver}}};Host={conn_conf['host']};Database={conn_conf['database']};Port={conn_conf['port']};{creds}"
            else: # lühike variant, kus ODBC-s on DSN kirjeldatud ja lisame ainult kasutajanime ja parooli
                conn_str = f"DSN={conn_conf['database']};{creds}"
            # võimalus lülitada Progressi fataalsena mõjuv hoiatus välja (parem oleks algandmed korda teha -- SQL ja APL veeru defid pole süngis)      
            # conn_str = conn_str + ';truncateTooLarge=output'
        
        return conn_str
        
