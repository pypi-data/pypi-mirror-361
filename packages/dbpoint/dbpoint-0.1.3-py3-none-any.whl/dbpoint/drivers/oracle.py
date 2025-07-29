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
        'SyntaxError': Exception #  unified.DataDriverSyntaxException
        , 'UndefinedTable' : Exception # unified.DataDriverUndefinedTable
        }
    
    
    def me(self) -> str:
        return 'ORA'
    
    
    def connect(self, profile: dict) -> int:
        
        if self.conn is not None: # kui ühendus on olemas, siis ei võta ühendust
            return 0
        
        try:
            import oracledb
        except:
            raise Exception(f"Driver package not installed. Do pip install oracledb")
            #raise unified.DataDriverNotInstalled('tee: pip install oracledb')
        
        conn_args = self.profile_to_dict(profile)
        if profile.get('mode', 'thin') == 'thick':
            import platform, os
            oracle_instantclient_subdir = 'instantclient_11_2' # näib, et see võib olla ka suvaline uuem?!
            # On Linux and related platforms, enable Thick mode by calling init_oracle_client() without passing a lib_dir parameter.
            # oracledb.init_oracle_client() # samaväärne lib_dir=None, järgmine kood tegeleb (tervikluse mõttes) kõigega
            oracle_instanclient_dir = None  # default suitable for Linux
            print(platform.system())
            print(platform.machine())
            if platform.system() == "Darwin" and platform.machine() == "x86_64":   # macOS
                oracle_instanclient_dir = "/".join([os.environ.get('HOME'), 'Downloads', oracle_instantclient_subdir]) # mac home ja Downloads (testimata loomulikult, ideena lihtsalt)
            elif platform.system() == "Windows":
                oracle_instanclient_dir = "C:\\" + "\\".join(['oracle', oracle_instantclient_subdir])
            print(oracle_instantclient_subdir)
            if not os.path.exists(oracle_instantclient_subdir):
                print(f"kausta {oracle_instanclient_dir} ei ole olemas")
                raise unified.DataDriverNotInstalledAdditional(f"Paksu Oracle jaoks pole InstanceClient asukohas {oracle_instanclient_dir}, midagi on vaja muuta")
            oracledb.init_oracle_client(lib_dir=oracle_instanclient_dir) # paksu kliendi jaoks vaja initsialiseerida

        self.conn = oracledb.connect(**conn_args) # nimelised argumendid ehk kwargs on dict ja viidata vaja kahe tärniga
        #self.error = oracledb.Error
        return 1
    
    def profile_to_dict(self, profile: dict) -> dict:
        
        conn_args = {}
        conn_args['user'] = profile.get('username', 'xxxxx')
        conn_args['password'] = profile.get('password', 'xxxxx')
        # aga vb anda host port ja service eraldi?
        #conn_args['dsn'] = profile.get('host', 'localhost') + "/" + profile.get('database', 'xxxxx') # nt 192.168.0.54/xe  
        conn_args['port'] = profile.get('port', 1521)
        conn_args['host'] = profile.get('host', 'localhost')
        conn_args['service_name'] = profile.get('database', 'xe')
        conn_args['tcp_connect_timeout'] = 8 # default on 20 sek
        return conn_args
    
'''
https://python-oracledb.readthedocs.io/en/latest/api_manual/module.html

oracledb.connect(dsn=None, pool=None, conn_class=None, params=None, user=None, proxy_user=None, password=None, newpassword=None, wallet_password=None
, access_token=None, host=None, port=1521, protocol='tcp', https_proxy=None, https_proxy_port=0
, service_name=None, sid=None, server_type=None, cclass=None, purity=oracledb.PURITY_DEFAULT, expire_time=0, retry_count=0, retry_delay=1
, tcp_connect_timeout=20.0, ssl_server_dn_match=True, ssl_server_cert_dn=None, wallet_location=None, events=False, externalauth=False
, mode=oracledb.AUTH_MODE_DEFAULT, disable_oob=False, stmtcachesize=oracledb.defaults.stmtcachesize, edition=None, tag=None, matchanytag=False
, config_dir=oracledb.defaults.config_dir, appcontext=[], shardingkey=[], supershardingkey=[], debug_jdwp=None, connection_id_prefix=None
, ssl_context=None, sdu=8192, pool_boundary=None, use_tcp_fast_open=False, ssl_version=None, handle=0)

'''