import logging
import time
import os, pathlib, shutil
import dill
import yaml
import hashlib, json, random

class timer:
    """ utility for calculate time duration
    """
    def __init__(self):
        """ init and tik() the timer """
        self._start = None
        self._stop  = None
        self.tik()

    def tik(self):
        self._start = time.time()
        return self._start

    def tok(self):
        self._stop  = time.time()
        return self._stop

    def taketime(seconds=None):
        """ static function for calc the time """
        if seconds:
            seconds  = seconds % (24 * 3600) 
            hour     = seconds // 3600
            seconds %= 3600
            minutes  = seconds // 60
            seconds %= 60
            return "%02d:%02d:%02d" % (hour, minutes, seconds) 
        else:
            return 'no given time (seconds)'


    def reset(self):
        """ reset start & stop timer to None, then tik() the timer """
        self._start = None
        self._stop  = None
        self.tik()

    def time(self, seconds=None):
        """ in-house function for calc timer """
        if seconds == None:
            seconds = self._stop - self._start if self._start and self._stop else None
 
        return timer.taketime(seconds)



class configure:
    def load(filename):
        """ load yaml file to configure """
        with open(filename, 'r') as f:
            conf = yaml.full_load(f)
        return conf


    def save(content, filename):
        """ write data to yaml file configure """
        data.make_path(filename)
        with open(filename, 'w') as f:
            yaml.dump(content, f, allow_unicode=True)



class data:
    def path_split(path:str) -> (str, str):
        """ split folder_path out of file_name
        """
        try:
            path   = path.strip()
            tokens = path.split('/')
            folder = '.' if len(tokens) == 1 else '/'.join(tokens[:-1])
            fname  = tokens[-1]
            return folder, fname

        except Exception as e:
            raise e


    def path_type(path:str) -> str:
        """ check type [file, folder, None] of a given path
        """
        try:
            thing = pathlib.Path(path)
            if thing.exists():
                if   thing.is_dir():  return 'folder'
                elif thing.is_file(): return 'file'
                else:                return None
            else:
                return None

        except Exception as e:
            raise e


    def exist(path, pathtype:str='any') -> bool:
        """ check if given path exist """
        try:
            thing   = pathlib.Path(path)

            if   pathtype == 'any':    return thing.exists()
            elif pathtype == 'folder': return thing.is_dir()
            elif pathtype == 'file':   return thing.is_file()
            else: raise TypeError('pathtype should be ["any", "file" or "folder"]')

        except TypeError as e:
            raise e

        except Exception as e:
            raise e
            

    def make_path(path, pathtype='file') -> bool:
        """ make folder in the path, return True if success, else False """
        # setup folder path
        #if pathtype == 'file':
        #    tokens = path.split('/')
        #    folder = '/'.join(tokens[:-1])
        #    fname  = tokens[-1]
        #else:
        #    folder = path

        # setup folder path
        if pathtype == 'file':
            _folder, _ = data.path_split(path)
        else:
            _folder    = path[:-1] if path.endswith('/') else path
        # create folder
        try: 
            #if len(folder) > 0: pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
            if len(_folder) and _folder != '.': pathlib.Path(_folder).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f'error: {str(e)}')
            return False
        return True


    def ls(path:str, fmt:str='list'):
        try:
            result = {'folder': [], 'file': []}
            for obj in os.scandir(path):
                o_type = 'folder' if obj.is_dir() else 'file'
                result[o_type].append(obj.name)

            if fmt == 'list':
                out  = []
                out += [f'{item}/' for item in result['folder']]
                out += result['file']
                return out

            elif fmt == 'dict':
                return result

            else:
                raise Exception('something error')

        except Exception as e:
            raise e


    def rm(path:str):
        try:
            file_type = data.path_type(path)
            if   file_type == 'file':
                os.remove(path)
                return True
            elif file_type == 'folder':
                shutil.rmtree(path)
                return True
            else:
                raise FileNotFoundError(f'path "{path}" not found')


        except FileNotFoundError as e:
            print(str(e))
            return False

        except Exception as e:
            print(f'> rm() error - {str(e)}')
            return False


    def save_object(obj, filename, verbose:bool=True):
        """ save any data to dill object file """
        data.make_path(filename)
        with open(filename, 'wb') as f:
            dill.dump(obj, f)
            if verbose: print(f'> saving data to "{filename}"')


    def load_object(filename, verbose:bool=True):
        """ load content in a file to dill data object """
        if verbose: print(f'> loading data from "{filename}"')
        with open(filename, 'rb') as f:
            data = dill.load(f)
        return data


    def save(lines, filename, verbose:bool=True):
        """ save text in lines to a file """
        data.make_path(filename)
        lines = [lines] if type(lines) == str else lines
        with open(filename, 'w') as f:
            for line in lines:
                f.write(line+'\n')
            if verbose: print(f'> saving content to "{filename}"')


    def load(filename, loadtype='original', verbose:bool=True):
        """ load text content in a file """
        if verbose: print(f'> loading "{loadtype}" content from "{filename}"')
        with open(filename, 'r') as f:
            if loadtype == 'original': lines = [line[:-1]    for line in f.readlines()]
            else:                      lines = [line.strip() for line in f.readlines()]
        return lines


    def load_file_list(f_list, n_char:int=0, verbose:bool=True):
        """ load content from a file list, each content line > n_char """
        content = []
        n_fail  = 0
        for f in f_list:
            try:
                content += [v for v in data.load(f, loadtype='strip', verbose=verbose) if len(v) > n_char]
            except Exception as e:
                n_fail  += 1
        if verbose: print(f'>>> load content from {len(f_list)} file(s) .. failed {n_fail} file(s)')
        return content


    def category_mapper(f_list, n_char:int=0, verbose:bool=True):
        """ grouping a line of token list as a category
            return those categories and mapper
        """
        lines    = data.load_file_list(f_list, n_char, verbose=verbose)
        category = {line.split(',')[0].strip(): [token.strip() for token in line.split(',')] for line in lines}
        mapper   = {l: k for k, L in category.items() for l in L}
        return category, mapper
            
            

class hasher:
    def hash(obj, n:int=None) -> str:
        """ if obj type is dictionary, convert to string before hashing
            n is number of digit
        """
        try:
            s_obj   = json.dumps(obj).encode() if type(obj) == dict else obj.encode()
            hashval = hashlib.md5(s_obj).hexdigest()
            return hashval[:n]

        except AttributeError as e:
            print(f'> hasher.hash() error, obj type should be string or dict - {str(e)}')
            raise e

        except TypeError as e:
            print(f'> hasher.hash() error, n type should be int or None - {str(e)}')
            raise e

        except Exception as e:
            print(f'> hasher.hash() error - {str(e)}')
            raise e


    def random_hash(prefix:str='', n:int=None) -> (str, str):
        """ randomly generate a key and its hash
        """
        try:
            seed = f'{random.randint(0, 99):02}'
            key  = f'{prefix}{seed}'
            return key, hasher.hash(key, n)

        except TypeError as e:
            print(f'> hasher.random_hash() error, prefix type should be string, n type should be int or None - {str(e)}')
            raise e

        except Exception as e:
            print('> hasher.random_hash() error - {str(e)}')
            raise e





class log:
    import logging.handlers

    """ static class for creating logger instance """
    DEBUG   =10
    INFO    =20
    WARNING =30
    ERROR   =40
    CRITICAL=50

    def info(logger, message=''):
        """ print information of the given handler """
        print(f'--- {message} logger "{logger.name}" info ---')
        print(f'logger: {logger}')
        print(f'handlers: {len(logger.handlers)}')
        for hand in logger.handlers:
            print(f'  {hand}')
        print()


    def GetHandler(filename=None, when=None, level=logging.DEBUG, formatter='minimal'):
        """ formatter will be in f-string format
            formatter: [nothing, minimal, basic, full, custom]
            o nothing: only message
            o minimal: time, message
            o basic:   level, name, message (exclude time)
            o full:    level, time, name, message
            o custom:  any format, but in f-string format only

            when: preset is [daily, weekly] or logging format e.g., W0
        """
        if   formatter == None: formatter = 'minimal'
        if   formatter == 'nothing':      formatter = '{message}'
        elif formatter == 'minimal':      formatter = '{asctime} || {message}'
        elif formatter == 'basic':        formatter = '{asctime} || {name} || {message}'
        elif formatter == 'full':         formatter = '{levelname:<8} || {asctime} || {name} || {message}'

        fmt = logging.Formatter(formatter, style='{')
        if filename:
            # make sure the folder is exist
            data.make_path(filename)
            # create log_handler
            w = 'midnight' if when == 'daily' else 'W0' if when=='weekly' else when
            if w is not None:
                handler = logging.handlers.TimedRotatingFileHandler(filename, when=w, encoding='utf8')
            else:
                handler = logging.FileHandler(filename, encoding='utf8')
            
        else:
            handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(fmt)
        return handler



    def GetLogger(name='muuusiiik', filename=None, when=None, level=logging.DEBUG, formatter='minimal'):
        """ generate Logger """
        # manage logger
        if not name: name = __name__
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        # manage handler
        handler = log.GetHandler(filename=filename, when=when, level=level, formatter=formatter) 
        logger.addHandler(handler)
        return logger
