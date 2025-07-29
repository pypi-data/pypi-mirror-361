'''

Ühendus läbi confi (dict), kus võimalikud võtmed järgmistes gruppides:
a) väljast juhitavad, mida ei tasuks näppida: driver (miks siia jõuti), class (siinne instants ise pärast)
b) ühenduseteks üldiselt vajaminevad: host, port, engine (ASA jaoks), database, dsn (ODBC DNS), username, password
c) ühenduse ajal muud kasutatavad: appname (PG jaoks)
d) metainfos ja muudes üldistustes erisuste juhtimiseks (sh ODBC korral): dialect (ODBC korral nt mysql, ASA korral nt asa5, asa7)
 - võib olla tähenduses metainfo jaoks oluline versioon (ASA tüüpprobleem) kui ka 
 - teistele tarbijatele dünaamilsite SQL.ide loomiseks vajalik ver (nt vanemates puudub mingi omadus)  

SQL käskude jooksutamine (run) koos võimalusega andmete tagastamiseks (do_return), commitiga järel (do_commit_after) ja meta küsimsiega (mõte alles)
- käskuke jooksutamisel tekkivad vead mäpitakse tootja moduli exceptionitest meie ühtlustatud exceptioniteks (kasutades alamklassis täidetud mäpperit)

'''
from loguru import logger
from datetime import datetime
from collections import namedtuple
# two attempts for getting annotations to work (first failed, second is semantically wrong (MySQL Cursor is not Postgre Cursor)):
#from _typeshed.dbapi import DBAPIConnection, DBAPICursor # too fresh too raw yet (eg. Protocol don't mention rollback())
#from psycopg2.extensions import connection, cursor
# third attempt:
from collections.abc import Sequence, Mapping
from typing import Any, Protocol


# next classes (Cursor and Connection) are only for type Annotations for IDEs
class Cursor(Protocol):
    description: Sequence[Any] | None
    rowcount: int
    arraysize: int

    def close(self) -> None:
        ...

    def execute(self, operation: Any, *args, **kwargs) -> None:
        ...

    def executemany(
            self,
            operation: Any,
            seq_of_parameters: Sequence[Any] | Mapping[Any, Any],
            *args,
            **kwargs
        ) -> None:
        ...

class Connection(Protocol):
    def close(self) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def cursor(self, *args, **kwargs) -> Cursor:
        ...


class DataDriverGeneric():
    
    map_of_exceptions = {} # alluv importigu sql_driver_errors ja lihtnime järgi (tootja-draiveri exc klassi viimane osis) vastavus (vt pg teostust)
    #conn: Connection = None # klassi instantsil on üks ühendus
    created = None
    last_run = None
    closed_ts = None
    run_count = 0 # tegelikult õnnestunud käskude arv
    run_count_after_last_disconnect = 0
    # escape võidakse ära muuta kui on juba olemas konkreetne draiver ja vb ka lausa konkreetne versioon
    # nt ASA on vana kaldkriips, MySQL on kuni ver 5 (incl) kaldkriips, aga uuemad juba starndadi järgi ülakoma
    apostrophe_escape = r"''" 
    # mõelda, kas on vaja
    #error = None ¤ või Exception  # ja konkreetne draiver paneb connect sees siia enda oma (endanimi.Error) ja run eristab seda muudest py üldisematest
    #
    type_mapper = {} 
    columns_definition: list[dict] = []

    class_mapper = {
        'CHAR' : 'VARCHAR'
        , 'NCHAR' : 'VARCHAR'
        , 'NVARCHAR' : 'TEXT'
        , 'VARCHAR' : 'TEXT'
        , 'DATETIME' : 'TIMESTAMP'
        , 'TINYINT': 'SMALLINT'
        , 'BLOB' : 'BYTEA'
        , 'LONG VARCHAR' : 'TEXT'
        , 'LONG BINARY' : 'BYTEA'
    }
    
    def __init__(self):
        self.created = datetime.now()
        self.conn: Connection = None 
    
    def me(self):
        return '' # üldine on nimetu, alluvad suurtähelised (läbivalt suur- või läbivalt väiketähelised) lühendid? PG, MYSQL, MSSQL, ORA, ASA, IQ, ASE, ODBC  
    

    def connect(self, profile: dict) -> int: # usutavasti on alluvatel nati erinevad nõksud/detailid
        ...
    
    
    def stream(self, sql: str):
        cur: Cursor = self.conn.cursor()
        cur.execute(sql)
        if not self.analyze_column_meta(cur.description):
            return
        #self.last_apos, self.last_structure = self.make_for_create(cur.description)
        #self.last_columns = self.make_for_columns(cur.description)
        while True:
            try:
                row = cur.fetchone()
            except Exception as e1:
                logger.error(e1)
                break
            
            if row is None:
                break
            else:
                yield row
        cur.close()

    
    def get_columns_definition(self) -> list[dict]:
        return self.columns_definition
    
    
    
    def get_mapper(self):
        def the_mapper(dataclass: str) -> str:
            dataclass2 = self.class_mapper.get(dataclass.upper(), dataclass.upper())
            #print(f"{dataclass} -> {dataclass2}")
            return dataclass2
        return the_mapper
    
    
    def analyze_column_meta(self, cursor_description: tuple | None) -> bool:
        
        self.columns_definition.clear()
        if cursor_description is None:
            return False
        
        for desc in cursor_description: # https://peps.python.org/pep-0249/#description
            dataclass = self.type_mapper.get(desc[1], 'TEXT')
            
            if dataclass in ('BIGINT', 'INT', 'NUMERIC', 'BOOLEAN'):
                needs_escape = False
            else:
                needs_escape = True
            
            if dataclass not in ('TEXT') and desc[3] > 1 and desc[4] is not None: # and desc[4] != 65535:
                details = []
                details.append(f"{desc[4]}")
                if desc[5] is not None and desc[5] != 65535:
                    details.append(f"{desc[5]}")
                datatype_details = ",".join(details)
                datatype_details = f"({datatype_details})" # sulud ümber
            else:
                datatype_details = ''
            datatype = dataclass + datatype_details
            temp_name = desc[0] # vaja oleks korduvust ja nime olemasolu kontrollida (aga need võivad ka failida ja las arendaja teeb korda)
            col_def = {'name' : temp_name, 'name_original' : desc[0], "class" : dataclass, "type" : datatype, "needs_escape" : needs_escape}
            self.columns_definition.append(col_def)
        return True

    def extract_name_string(self, separator: str=', ') -> str:
        if not self.columns_definition:
            return ''
        return separator.join([col['name'] for col in self.columns_definition])
    
    def run(self, sql: str, do_return: bool = True, **kwargs):
        # , do_commit_after: bool = True, on_error_rollback = True, do_grab_meta = False
        
        if sql is None or len(sql.strip()) < 1:
            raise Exception("Empty command")
            #raise unified.DataDriverEmptyCommand('Empty command') # kas tühi SQL on fataalne või edasi mindav, otsustagu väljakutsuja
        
        # olulised muutuvad argumendid ja nende vaikeväärtused
        defaults = { 
            'on_success_commit' : True
            , 'new_transaction': False
            , 'on_error_rollback' : True
            , 'on_error_disconnect' : False
            , 'verbose' : False
            , 'style' : 'number' # both on liiga ohtlik, kuna meil metasüsteem ja mitmes kohas on iteratsioon üle veergude
            }
        control = {**defaults, **kwargs}
        
        # alternatiiv:
        kwargs.setdefault('verbose', False)
        
        # 
        extra_on_success_commit = control['on_success_commit']
        extra_on_error_rollback = control['on_error_rollback']
        extra_on_error_disconnect = control['on_error_disconnect']
        extra_new_transaction = control['new_transaction']

        #' extra_verbose = control['verbose']
        # ja selle alternatiiv:
        extra_verbose = kwargs.get('verbose', False)
        extra_return_style = control['style'] # text, number, both
        if extra_return_style == 'text':
            extra_return_style = 'name'
        if extra_return_style not in ('name', 'number', 'both'):
            extra_return_style = 'number'
        
        if extra_new_transaction:
            self.conn.commit()
        
        result_set = []
        try:
            #with self.conn.cursor() as cur: // see tuli ära jätta, sest asa cursori __enter__ evib mingit viga (AttributeError)
            cur: Cursor = self.conn.cursor()
            cur.execute(sql)
            #logger.debug("execution instructed")

            if do_return:
                # cur.description: tuple[str, DBAPITypeCode, int | None, int | None, int | None, int | None, bool | None]
                if not self.analyze_column_meta(cur.description):
                    logger.debug("during analyze emptyness happenes")
                    return []
                
                if extra_return_style == 'number':
                    #logger.debug("numbered columns instructed")
                    result_set = cur.fetchall()

                if extra_return_style == 'name':
                    #logger.debug("named columns instructed")
                    columns_named_spaced = self.extract_name_string(' ')
                    if columns_named_spaced is None:
                        raise Exception('no metadata grabbed')
                    record_type = namedtuple('NamedTupleRecord', columns_named_spaced, rename=True)
                    result_set = list(map(record_type._make, cur.fetchall()))

                if extra_return_style == 'both':
                    #logger.debug("dualistic columns instructed")
                    columns_named_spaced = self.extract_name_string(' ')
                    record_type = namedtuple('DictRecord', columns_named_spaced, rename=True)
                    result_set = []
                    row: tuple
                    for row in cur.fetchall():
                        # row on numbrilise indeksiga (list): row[0], row[1] jne
                        new_row : dict = {}
                        for pos, cell in enumerate(row): # kordame datat
                            new_row[record_type._fields[pos]] = cell # str key
                            new_row[pos] = cell # int key
                        result_set.append(new_row) # list[dict[int|str, any]]

        except Exception as ex:
            #print('hakkame töötlema ja peitma ja muud tegema, mis pole päris hea vea lokaliseerimiseks, aga hea lõpptarbijale')
            if extra_on_error_rollback:
                self.conn.rollback()
                logger.debug("rollback happenes")
            if extra_on_error_disconnect:
                self.disconnect()
                logger.debug("disconnect happenes")
            raise ex
        finally:      
            cur.close() # see juhtub isegi raise ex korral except osas
        
        self.last_run = datetime.now()
        self.run_count = self.run_count + 1 # õnnestunud käsk suurendab käskude arvu
        self.run_count_after_last_disconnect = self.run_count_after_last_disconnect + 1
        
        #logger.debug(f"commands executed is now {self.run_count} (and {self.run_count_after_last_disconnect} after last connect)")

        if extra_on_success_commit:
            #logger.debug("commit happenes")
            self.conn.commit()
        
        if do_return:
            #logger.debug("return data happenes")
            return result_set
        else:
            #logger.debug("just return happenes")
            return []
    
    def escape(self, cell_value, data_class, needs_escape):
        ''' 
        Postgre jaoks kirjutame üle niikuinii, sest saame kasutada märkhaaval asendamise asemel nn 3nda märgiga ümbritsemist (mis aitab säilitada json ja xml sisusid, peamiselt json)
        Teistel ei tarvitse olla boolean tüüpi, aga sellest ei lähe midagi siin katki. 
        Pigem läheb katki, kui on boolean ja see antakse stringina teisiti (ega tõlgita py bool-iks) -- sii ssee fn üle kirjutada 
        ''' 
        if cell_value is None:
            return 'NULL'
        if data_class == 'BOOLEAN' or isinstance(cell_value, bool):
            return 'TRUE' if cell_value == 't' else 'FALSE' 
        if needs_escape:
            # vs liht-asendamise meetod
            return (str(cell_value)).replace("'", self.apostrophe_escape)
        else:
            return f"{cell_value}"   
        
    
    def disconnect(self):
        try:
            self.conn.close()
        except:
            ...
        finally:
            self.conn = None
            self.closed_ts = datetime.now()
            self.run_count_after_last_disconnect = 0

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
    
    def __repr__(self) -> str:
        # profiiliga seotud metainfo
        info = []
        info.append(self.me())
        info.append(f"inited at {self.created:%F %T.%f}") # ISO formatted date, Time, fractions (6 kohta)
        if(self.conn is not None):
            info.append('connected,')
            if self.last_run is None:
                info.append("no runs")
            else:
                info.append(f"last run at {self.last_run:%F %T.%f}")
        else:
            if(self.closed_ts is not None): # kui pole ühendust veel olnud, siis pole ka sulgemise aega
                info.append(f"disconnected at {self.closed_ts:%F %T.%f}")
        info.append(f"run count is {self.run_count} ({self.run_count_after_last_disconnect})")
        return " ".join(info)

