import ibm_db


class Converter(object):
    @classmethod
    def __get_dictionary_conversions__(cls):
        converter = {
            'int': cls.__to_int__,
            'float': cls.__to_float__,
            'real': cls.__to_float__,
            'decimal': cls.__to_float__,
            'string': cls.__do_nothing__,
            'date': cls.__do_nothing__,
            'datetime': cls.__do_nothing__,
            'time': cls.__do_nothing__,
            'timestamp': cls.__do_nothing__,
            'clob': cls.__do_nothing__,
        }

        return converter

    @classmethod
    def has_type(cls, typename):
        return typename in cls.__get_dictionary_conversions__()

    @classmethod
    def get_converter(cls, typename):
        return cls.__get_dictionary_conversions__()[typename]

    @staticmethod
    def __to_float__(val):
        if val is not None:
            return float(str(val).replace(',', '.'))
        return None

    @staticmethod
    def __to_int__(val):
        if val is not None:
            return int(str(val).replace(',', '.'))
        return None

    @staticmethod
    def __do_nothing__(val):
        return val

    @staticmethod
    def get_types(stmt):
        detected_types = dict()
        for i in range(ibm_db.num_fields(stmt)):
            detected_types[ibm_db.field_name(stmt, i)] = ibm_db.field_type(stmt, i)

        return detected_types


class TupleIterator(object):
    """
    Classe para iterar sobre as respostas de um banco de dados DB2.
    """
    fetch_method = ibm_db.fetch_tuple

    def __init__(self, stmt, *, convert_type=True):
        """

        :param stmt: Consulta a ser iterada sobre
        :param convert_type: Opcional - use True caso queira que o iterador retorna o dado no tipo armazenado
        originalmente no banco de dados. O padrão é True
        """
        self.uninitialized = True
        self.stmt = stmt
        self.next_item = None
        self.convert_type = convert_type

        self.detected_types = Converter.get_types(self.stmt)

    def __iter__(self):
        if self.uninitialized:
            self.uninitialized = False
            self.next_item = self.fetch_method(self.stmt)

        return self

    def __next__(self):
        if self.next_item is not False:
            if self.uninitialized:
                self.next_item = self.fetch_method(self.stmt)
                self.uninitialized = False

            to_return = self.next_item
            if to_return is False:
                raise StopIteration

            to_return_new = dict()
            return_tuple = False
            if isinstance(to_return, tuple):
                return_tuple = True
            if not return_tuple:
                iterable = to_return.items()
            else:
                iterable = zip(self.detected_types.keys(), to_return)

            if self.convert_type:
                for k, v in iterable:
                    to_return_new[k] = Converter.get_converter(self.detected_types[k])(v)
            else:
                to_return_new = dict(iterable)

            self.next_item = self.fetch_method(self.stmt)

            if return_tuple:
                return tuple(to_return_new.values())
            return to_return_new
        else:
            raise StopIteration


class DictIterator(TupleIterator):
    fetch_method = ibm_db.fetch_assoc
