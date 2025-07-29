from loguru import logger
from typing import Callable, Any
from types import ModuleType
from pydantic_yaml import parse_yaml_raw_as  #, to_yaml_str
from collections import namedtuple
from datetime import datetime

from .moduleops import prepare_module_fn
from .textops import yaml_string_to_dict
from .profile_sql import ProfileSqlCollection, ProfileSql
from .dataset import Dataset, Datarow
from .datacolumn import DataColumn
from .datacommand import DataCommand


class Hub():
    """
    Single access point for all database action. 
    New way is to init with two strings (yaml strings): list of profiles, and name-to-module mapping dict
    """
    def __init__(self, list_of_profiles: str = "", known_drivers: str = ""):
        """
        Init by YAML string that conforms to ProfileSQL structure
        """
        self.module_cache: dict[str, ModuleType] = {} # private, use fn 
        self.profile_collection: ProfileSqlCollection | None = None
        self.known_drivers: dict[str, dict] | None = None
        self.init_sql_drivers_for_app(known_drivers)
        if not self.known_drivers:
            logger.error("No database drivers known!")
            raise Exception("No database drivers known")
        self.init_sql_profiles_for_app(list_of_profiles)
        if not self.profile_collection:
            logger.error("No database profiles!")
            raise Exception("No database profiles")
        
        # increasing
        self.run_count = 0
        self.run_count_after_last_disconnect = 0

        # data about LAST command (in whatever channel)
        self.last_command: DataCommand = DataCommand()

        #self.last_profile: str = '' # profile to where last command was directed
        #self.last_sql: str = '' # last SQL commant in whatever channel/profile/connection
        #self.last_sql_with_error: str = ''
        #self.last_run = None
        #self.columns_definition: list[dict] = []
        #self.query_column_description: DataColumn | None = None
        #self.last_command_data: dict[str, DataColumn] | None = {}

    def cache_get(self, module_short_name: str) -> ModuleType | None:
        return self.module_cache.get(module_short_name, None)
    
    def cache_set(self, module_short_name: str, the_module: ModuleType) -> None:
        self.module_cache[module_short_name] = the_module

    def cacher(self, module_short_name: str, the_module: ModuleType | None) -> ModuleType | None:
        """
        One fn to manipulate both cache ops
        """
        if the_module: # if module is given then caller wants to set it
            self.cache_set(module_short_name, the_module)
            return the_module
        else:
            return self.cache_get(module_short_name)
    
    def mapper_for_driver_module(self, module_short_name: str) -> dict | None:
        """
        Knowledge how to find python package and module for some short alias
        Knowledge bases on self.know_driver dict
        Returns dict: "package" and "module" (and maybe "relative" = main package -- ??)
        """
        if not module_short_name:
            return None
        library_info: dict | None = (self.known_drivers or {}).get(module_short_name, None)
        if not library_info:
            logger.error(f"Module info for {module_short_name} not found")
        #else:
        #    logger.debug(f"Module for {module_short_name} is {library_info}") # package and module
        return library_info # currently our input (known drivers) are same dict structure that is needed

    def init_sql_drivers_for_app(self, known_drivers: str | dict):
        """
        Input is YAML formated text with names to point to package and module where allowed DataDrivers reside
        If app needs just one connecction then don't give more/unneeded drivers.
        NB! dict type support is deprecated
        """
        if isinstance(known_drivers, str):
            self.known_drivers = yaml_string_to_dict(known_drivers)
        else:
            self.known_drivers = known_drivers
    
    def init_sql_profiles_for_app(self, list_of_profiles: str | list[dict]):
        """
        Giving app database connection configuration profiles.
        """
        try:
            self.profile_collection = parse_yaml_raw_as(ProfileSqlCollection, list_of_profiles)
            for profile in self.profile_collection:
                profile.password = self.substitute_env(profile.password)
        except Exception as e1:
            logger.error(f"Unable to parse config data from yaml-string, string is not correct YAML ProfileSql, {e1}")
            raise e1 # FATAL

    def substitute_env(self, text: str) -> str:
        #return [replace_dict(profile) for profile in list_of_profiles]
        import os
        if text is None:
            return None
        if text.startswith("%") and text.endswith("%"):
            env_key = text[1:-1]
            #logger.error(f"{env_key}")
            substed = os.getenv(env_key, "")
        else:
            substed = text
        #logger.debug(f"orig {text} and replaced {substed}")
        return substed

    def validate_all_profiles(self, stop_on_first_error: bool = False) -> bool:
        result: bool = True
        profile: ProfileSql # for for
        for profile in self.profile_collection:
            sub_result: bool = self.validate_profile(profile)
            if not sub_result:
                logger.warning(f"Profile {profile.name} is not technically usalble (invalid driver)")
            else:
                logger.debug(f"Profile {profile.name} is technically usable (valid driver)")
            result = sub_result and result
            if not result and stop_on_first_error:
                return False
        return result

    def validate_profile_by_name(self, profile_name: str) -> bool:
        return self.validate_profile(self.get_profile(profile_name))
    
    def validate_profile(self, profile: ProfileSql | None) -> bool:
        """
        Connection profile preliminary validation -- is driver alias known
        """
        if profile is None:
            return False
        if self.known_drivers.get(profile.driver):
            return True
        else:
            return False

    def get_profile(self, profile_name) -> ProfileSql | None:
        return self.profile_collection.find_by_name(profile_name)

    def get_last_error_command(self):
        return self.last_command.command_with_error if self.last_command else None

    def get_last_command(self):
        return self.last_command.command if self.last_command else None
    
    def create_driver(self, driver_alias: str) -> ModuleType | None:
        """
        Result is driver object (corresponding to corrent DBMS) without actual connection
        Called only by get_driver()
        """
        logger.debug(f"Loading module for driver {driver_alias}")
        the_module: ModuleType = prepare_module_fn(driver_alias, self.cacher, self.mapper_for_driver_module)
        if the_module is None:
            logger.error(f"Preparation result is None")
            return None
        try:
            driver_module = the_module #.DataDriver() # class with such fixed name
            return driver_module
        except Exception as e1:
            logger.error(f"Problem with driver, {e1}")
            return None

    def get_driver(self, profile_name: str | None) -> ModuleType | None:
        """
        Returns object capable to make actions (don't need to be connected)
        """
        if profile_name is None:
            logger.error("Missing profile name for driver")
            return None
        profile: ProfileSql = self.get_profile(profile_name)
        if profile is None:
            return None
        if profile.driver_module is None: # if driver object/module not found yet
            new_driver_module = self.create_driver(profile.driver)
            if not new_driver_module:
                logger.error(f"Couldn't init driver '{profile.driver}'")
                return None
            if not hasattr(new_driver_module, "connect"): # or not hasattr(new_driver_module, "class_mapper"):
                logger.error(f"Wrong spec driver '{profile.driver}'")
                return None
            profile.driver_module = new_driver_module
        return profile.driver_module

    def prepare_flags(self, flags: dict = None):
        # style: text, number, both # FIXME teha Enum
        defaults = { 
            'on_success_commit' : True
            , 'new_transaction': False
            , 'on_error_rollback' : True
            , 'on_error_disconnect' : False
            , 'verbose' : False
            , 'style' : 'number' # both on liiga ohtlik, kuna meil metasüsteem ja mitmes kohas on iteratsioon üle veergude
            }
        flags = flags or {}
        control = {**defaults, **flags}
        if control['style'] == 'text':
            control['style'] = 'name'
        if control['style'] not in ('name', 'number', 'both', 'dataset'):
            control['style'] = 'number'
        return control

    def find_connection(self, profile_name: str, reconnect: bool = False):
        #logger.info(f"find connection {profile_name} with {reconnect}")
        profile = self.get_profile(profile_name)
        driver_module: ModuleType = self.get_driver(profile_name)
        if driver_module is None:
            logger.error(f"No real driver for profile '{profile_name}'")
            return None
        if not profile.connection_object or reconnect:
            profile.connection_object = driver_module.connect(profile)
        return profile.connection_object # shortcut
    
    def get_executed_cursor(self, profile_name: str, sql: str, control: dict = None, counter: int = 1) -> None | Any: # Any = cursor from any DBMS package (which may by dynamic)
        """
        Internal function!
        Return new Executed Cursor (or None), so connection issues are mostly solved.
        "Empty command error" should be checked ealier
        """
        if counter < 0: # avoid infinite recursion
            logger.error(f"Loop limit full")
            return None
        
        connection = self.find_connection(profile_name)
        if connection is None:
            logger.error(f"Couldn't find connection {profile_name}")
            return None
        try:
            cursor = connection.cursor() # normal guess that connection object will give error if connection is lost, but no...
            if control['new_transaction']:
                self.try_and_log(connection.commit, logger.warning, "Failed to start transaction before command, ignoring")
            cursor.execute(sql) # ... error about lost connection becomes visible only after execution of cursor
            # logger.debug(f"cursor executed succesfully, {cursor}")
        except Exception as e1:
            #  (b'Connection was terminated', -308),  (b'Not connected to a database', -101)
            logger.error(e1) # MariaDB annab siia str(e1) lihtsalt stringi "Server has gone away"
            logger.error(e1.args) # Kuidagi peaks kinni püüdma vea staatuskoodi. ASA annab -101 või -308, MariaDB annab tuple, kus esimene/ainuke element on string
            if (len(e1.args) > 1 and isinstance(e1.args[1], int) and e1.args[1] in (-101, -308)) or str(e1) == "Server has gone away":
                logger.error("Caught connection error")
                connection = self.find_connection(profile_name, reconnect=True)
                if connection is None:
                    logger.error(f"Unable to reconnect {profile_name}")
                    return None
                logger.info(f"Reconnected!")
                try:
                    control['on_error_rollback'] = False
                    control['on_error_disconnect'] = False
                    cursor = self.get_executed_cursor(profile_name, sql, control, counter - 1)
                except Exception as e2:
                    logger.error(e2)
                    cursor = None
            else: # all other errors (SQL syntax, priviledges etc)
                logger.error("Other error")
                self.last_command.command_with_error = sql
                if control['on_error_rollback']:
                    self.try_and_log(connection.rollback, logger.warning, "Failed to roll back after error, ignoring")
                if control['on_error_disconnect']:
                    self.try_and_log(connection.disconnect, logger.warning, "Failed to disconnect after error, ignoring")
                logger.error(f"Database command error, {e1}")
                return None #raise e1
        # if cursor was meant for only execution of command without result set, we can commit (if wanted) and close, but let these things are inside run()
        return cursor
    
    def fn_stream(self, profile_name: str):
        def dummy(sql):
            return None
        def streamer(sql):
            logger.info(f"streamer is here with SQL: {sql}")
            control: dict = self.prepare_flags({})
            cursor = None
            try:
                cursor = self.get_executed_cursor(profile_name, sql, control)
            except Exception as e1:
                logger.error(f"problem with cursor")
                return None
            
            if cursor is None:
                logger.error(f"lets take dummy")
                return None
            
            #cursor.execute(sql)
            if not self.analyze_column_meta(cursor.description, profile_name):
                logger.error(f"problem with analyze meta")
                cursor.close()
                return None
            while True:
                try:
                    row = cursor.fetchone()
                except Exception as e1:
                    logger.error(e1)
                    break
                if row is None:
                    break
                else:
                    yield row
            cursor.close()
            logger.info("streamer ends")
        return streamer

    def run(self, profile_name: str, sql: str, do_return: bool = True, **kwargs) -> None | bool | Any: # Any = data as wanted by control['style']
        """
        Runs SQL and returns (if asked) something (just universal list, or our Dataset)
        - new_transaction = False -- do we need to start with commit()
        - on_error_rollback = True
        - on_error_disconnect = False
        - on_success_commit = True
        - verbose = False
        - style = 'number' (vs 'name', 'both', 'dataset')
        """
        if sql is None or len(sql.strip()) < 1:
            logger.warning(f"Empty SQL command")
            return None
            #raise Exception("Empty command")
        self.last_command.command = sql
        self.last_command.profile_name = profile_name
        
        control: dict = self.prepare_flags(kwargs) # how to behave/act during execution of one command
        cursor = self.get_executed_cursor(profile_name, sql, control)
        if cursor is None:
            return None # as result_set (not relevant does user want us to return something or not)
#
        # data management
        result_set: list | Dataset | None = None
        #with self.conn.cursor() as cursor: // cannot use this approach, Sybase ASA cursor __enter__() has some bug (AttributeError) in sqlanydb 1.0.14
        logger.trace(f"SQL executed, {sql}")
        if do_return or do_return is None:
            fetch_switch: dict = { # maps result set access style name to function with executed cursor as argument
                'number' : self.stuctured_fetch_index
                , 'name': self.stuctured_fetch_label
                , 'both': self.stuctured_fetch_both
                , 'dataset': self.structured_fetch_dataset
            }
            result_set = (fetch_switch[control['style']])(cursor, profile_name) # if control['style'] == 'number': result_set = self.stuctured_fetch_index(cur)

        self.usage_increment()
        self.try_and_log(cursor.close, logger.warning, "Failed to close cursor, in confusion, ignoring") # close cursor anyway
        if control['on_success_commit']:
            connection = self.find_connection(profile_name)
            self.try_and_log(connection.commit, logger.error, "Failed to end transaction after success, ignoring")
        
        if (do_return or do_return is None) and result_set:
            return result_set
        else:
            return True

    def try_and_log(self, try_action: Callable, problem_logging_action: Callable, logging_message_prefix: str) -> bool:
        """
        Perform simple (database connection) action (function without params) and if failed log it using logging function (logger.error or logger.warning).
        try_action shoold be like commit, rollback, disconnect (from their owner object)
        Just to shorten run() code there are different flags (do commit before, after etc)
        """
        try:
            try_action()
        except Exception as e1:
            problem_logging_action(f"{logging_message_prefix}, {e1}")
            return False
        return True

    def reconnect(self, profile_name, wake_up_select: str | None = None):
        """
        Reconnect (eg. after sudden disconnect) for use by outsiders.
        Tries to disconnect first, ignores disconnection failure.
        Keep in mind -- we have automatic connection (command "run") and dev dont need to worry about connect, so try to avoid reconnect as well.
        We force here new connect by running simple SQL command, but it may not work for all DBMS-s ("SELECT 1") 
        """
        try:
            self.disconnect(profile_name)
        except Exception as e1:
            logger.warning(f"disconnect failed, ignoring, probably disconnected, {e1}")
        try:
            wake_up_command = wake_up_select if wake_up_select else "SELECT 1"
            self.run(profile_name, wake_up_command) # first run for non-connected, tries to connect
        except Exception as e1:
            logger.warning(f"wakeup SQL, {wake_up_command}")
            logger.error(f"still no connection (or incompatible wake-up SQL), {e1}")
            return False
        return True

    def stuctured_fetch_index(self, cursor, profile_name: str) -> list[tuple] | None:
        """
        The simpliest variant from cursor to list, list item (row) is number-indexed (tuple)
        """
        try:
            return cursor.fetchall()
        except Exception as e1:
            return None
    
    def stuctured_fetch_label(self, cursor, profile_name: str) -> list:
        """
        Labeled variant from cursor to list, list item (row) is string-labeled (access: rs[0].colname)
        """
        # cur.description: tuple[str, DBAPITypeCode, int | None, int | None, int | None, int | None, bool | None]
        if not self.analyze_column_meta(cursor.description, profile_name):
            logger.error("During analyze of columns the emptyness happenes")
            return None
        columns_named_spaced = self.extract_name_string(' ')
        if columns_named_spaced is None:
            logger.error(f"No metadata present")
            raise Exception('no metadata grabbed')
        record_type = namedtuple('NamedTupleRecord', columns_named_spaced, rename=True)
        try:
            return list(map(record_type._make, cursor.fetchall()))
        except Exception as e1:
            return None

    def stuctured_fetch_both(self, cursor, profile_name: str) -> list[dict]:
        """
        Duplicated variant from cursor to list, list item (row) is bot string-labeled and int-labeled (dict) 
        """
        # cur.description: tuple[str, DBAPITypeCode, int | None, int | None, int | None, int | None, bool | None]
        if not self.analyze_column_meta(cursor.description, profile_name):
            logger.error("During analyze of columns the emptyness happenes")
            return None
        columns_named_spaced = self.extract_name_string(' ')
        record_type = namedtuple('DictRecord', columns_named_spaced, rename=True)
        result_set = []
        row: tuple
        for row in cursor.fetchall():
            # row on numbrilise indeksiga (list): row[0], row[1] jne
            new_row : dict = {}
            for pos, cell in enumerate(row): # kordame datat
                new_row[record_type._fields[pos]] = cell # str key
                new_row[pos] = cell # int key
            result_set.append(new_row) # list[dict[int|str, any]]
        return result_set

    def structured_fetch_dataset(self, cursor, profile_name: str) -> Dataset:
        """
        Our custom class/structure
        """
        rowset = cursor.fetchall()
        full_data: Dataset = Dataset()
        if rowset:
            for row in rowset:
                datarow = Datarow()
                for col in row:
                    datarow.add_cell(col)
                full_data.append(datarow)
        return full_data

    def usage_increment(self):
        self.last_command.last_run_datetime = datetime.now()
        self.run_count = self.run_count + 1 # õnnestunud käsk suurendab käskude arvu
        self.run_count_after_last_disconnect = self.run_count_after_last_disconnect + 1


    def copy_to(self, sql : str, profile_name : str, first_row_grab : Callable, side_effects : Callable | None, prepare_row_command : Callable, save_command : Callable, info_step: int = 1000):
        """
        
        """
        # FIXME , REVIEW ME
        #permanent_info = {}
        pos = 0
        logger.info(f"copy_to.. {profile_name}")
        logger.info(f"side by (not used): {side_effects.__qualname__}")
        logger.info(f"prep by: {prepare_row_command.__qualname__}, {type(prepare_row_command)}")
        logger.info(f"save by: {save_command.__qualname__}, {type(save_command)}")
        flower = self.fn_stream(profile_name)
        if flower is None:
            logger.error("Flow is None?!")
            return -1
        logger.info(f"flow by: {flower.__qualname__}, {type(flower)}")

        
        
        for pos, row in enumerate(flower(sql), 1):
            if pos == 1:
                logger.info(row)
                permanent_info = self.last_command.query_cols
                logger.info(permanent_info)
                #pass
                #permanent_info : dict = first_row_grab()
                #if permanent_info is None:
                #    logger.error("Problem with GRAB")
                #    return -1
                #logger.debug(f"pos=1 start side effect")
                #side_quest = side_effects() if side_effects is not None else True
                #logger.debug(f"pos=1 end side effect")
            logger.info(row)
            
            command = prepare_row_command(row, permanent_info)
            logger.warning(command)
            if not save_command(command, pos):
                logger.error(f"Problem with SAVE, made {pos}")
                return -pos # if 1st row failes, return -1, if second returns -2
            # if pos % info_step == 0:
            #     mem_free = mem_free_now()
            #     logger.info(f"Pulled up to here {pos} rows, free memory {mem_free:.2f} MB")
            #     if mem_free < 1:
            #         logger.error(f"Out of memory very soon, so lets quit as we can it do now")
            #         return -pos
            
        logger.info(f"copy_to END {pos} rows")
        return pos

    def generate_command_for_create_table(self, target_table: str, create_as_temp: False, cols_def: list | dict = None, map_columns: dict = None) -> str:
        as_temp = ' TEMP' if create_as_temp else ''
        if isinstance(cols_def, list): # list of DataColumn's
            create_columns = ', '.join([column.get_ddl_declaration() for column in cols_def])
        else: # vana dict variant
            if map_columns is None:
                create_columns = ', '.join([col_def['name'] + ' ' + col_def['type'] for col_def in cols_def])
            else:
                create_columns = ', '.join([map_columns[col_def['name']] + ' ' + col_def['type'] for col_def in cols_def if col_def['name'] in map_columns and map_columns[col_def['name']] != ''])
        
        create_table = f"CREATE{as_temp} TABLE {target_table} ({create_columns})"
        print(f"{create_table=}")
        return create_table
        
    # def to_file(self, profile_name: str, query: str, file_path) -> int:
        
    #     driver: AnyDataDriver = self.get_driver(profile_name)
    #     if driver is None:
    #         return -1
    #     try:
    #         number_of_rows = driver.to_file(query, file_path)
    #     except Exception as e0: # FIXME unified.DataControllerException as e0:
    #         print('vigusk juhtus: ' + str(e0))
    #         return -1
    #     return number_of_rows

    def commit(self, profile_name: str):
        profile = self.get_profile(profile_name)
        if profile.connection_object:
            profile.connection_object.commit()

    def rollback(self, profile_name: str):
        profile = self.get_profile(profile_name)
        if profile.connection_object:
            profile.connection_object.rollback()

    def disconnect(self, profile_name: str):
        profile = self.get_profile(profile_name)
        if profile.connection_object:
            profile.connection_object.close()

    def disconnect_all(self):
        for profile in self.profile_collection:
            self.disconnect(profile.name)
            logger.debug(f"{profile.name} disconnected")

    def sql_string_value(self, profile_name: str, value: Any, datacolumn: DataColumn, for_null: str = 'NULL') -> str:
        """
        Knowing value and some info about its general type, return string which will be part of SQL command (eg INSERT) 
        where texts and times are surrounded with apostrophes and empty strings are replaced with nulls for numbers and dates
        and texts are escaped (this one is made using by profile name what is wrong -- taking data from source and saving to target the target rules must be followed)
        """
        if value is None:
            return for_null # NULL (without surronding apostrophes)
        if datacolumn.is_literal_type:
            return str(value) if value > '' else for_null
        if datacolumn.class_name == 'TIME':
            return f"'{value}'" if value > '' else for_null # if value then with surroundings, otherwise NULL without
        driver_module: ModuleType = self.get_driver(profile_name)
        escaped_value = driver_module.escape(value) or value
        f"'{escaped_value}'"
        #escaped = value.replace("'", "''") # ' -> ''
        #return f"'{escaped}'"

    def prepare(self, profile_name, cell_value, data_class, needs_escape):
        if cell_value is None:
            return 'NULL'
        if data_class == 'INT':
            if cell_value == '':
                return 'NULL'
            else:
                return str(cell_value)
        else:
            driver: ModuleType = self.get_driver(profile_name)
            escaped_value = driver.escape(cell_value) or cell_value
            return f"'{escaped_value}'"

    def get_columns_def(self, profile_name) -> list[DataColumn]:
        return self.last_command.query_cols
    
    def get_columns_definition(self, profile_name)-> list[dict]:
        """
        Last connection last SQL
        """
        return self.last_command.query_cols

    def __repr__(self):
        # kõik profiilid ühendusinfoga (parool on varjestatud) ja profiilide metainfoga (millal, palju)
        str_lines = []
        profile: ProfileSql
        for jrk, (name, profile) in enumerate(self.profile_collection.items(), 1):
            str_lines.append(f"{jrk}) {name}")
            safe_profile: ProfileSql = profile.model_copy(deep=True)
            safe_profile.password = "******"
            str_lines.append(str(safe_profile.model_dump_json()))
            str_lines.append("")
        str_lines.append("")
        return "\n".join(str_lines)


    def analyze_column_meta(self, cursor_description: list[tuple] | None, profile_name: str) -> bool:
        """
        This (columns_definition) belongs to ONE profile (channel), but **currently** we interpret is as LAST in any channel
        """
        #self.columns_definition.clear()
        self.last_command.query_cols = []
        if cursor_description is None:
            return False
        
        driver_module: ModuleType = self.get_driver(profile_name)
        mapper = None 
        if hasattr(driver_module, "class_mapper"):
            mapper = driver_module.class_mapper()
        if hasattr(driver_module, "type_mapper"):
            mapper = driver_module.type_mapper

        for column_description in cursor_description:
            dcol = DataColumn(column_description, mapper)
            self.last_command.query_cols.append(dcol)
            #dcol.get_ddl_declaration()
            #col_def = {'name': dcol.get_name(), 'name_original': dcol.get_name(), "class": dcol.class_name, "type": dcol.typename, "needs_escape": not dcol.is_literal_type()}
            #logger.warning(col_def)
            #self.columns_definition.append(col_def)
        return True


        for desc in cursor_description: # https://peps.python.org/pep-0249/#description
            logger.warning(desc) #  ('id', DBAPISet({480, 482, 484, 496, 500, 604}), None, 4, 0, 0, 0)
            if isinstance(desc[1], frozenset):
                logger.error('jah, on frozenset')
                dbapiset_mapper: dict = driver_module.type_mapper()
                dataclass = dbapiset_mapper.get(list(desc[1])[0], 'TEXT')

            else:
                logger.warning(type(desc[1]))
                dataclass = mapper.get(desc[1], desc[1]) # here logic: if not mentioned in mapper then itself (ALT: if not mentioned then TEXT)
            
            if dataclass in ('BIGINT', 'INT', 'NUMERIC', 'BOOLEAN', 'INTEGER', 'DECIMAL', 'FLOAT'):
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
            temp_name = desc[0] # vaja oleks korduvust ja nime olemasolu kontrollida (aga need võivad ka feilida ja las arendaja teeb korda)
            col_def = {'name' : temp_name, 'name_original' : desc[0], "class" : dataclass, "type" : datatype, "needs_escape" : needs_escape}
            logger.warning(col_def)
            self.columns_definition.append(col_def)
        return True

    def extract_name_string(self, separator: str=', ') -> str:
        if not self.get_columns_def('suva'):
            return ''
        return separator.join([col.colname for col in self.last_command.query_cols])
        return separator.join([col['name'] for col in self.columns_definition])
