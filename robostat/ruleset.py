class Ruleset:

    # voi palauttaa mitä tahansa, mikä kuvaa suorituksen pisteitä (luku, dict, olio, ...)
    # robostat ei tee mitään oletuksia sen suhteen millainen score on
    def create_score(self):
        raise NotImplementedError

    # muutaa bytes objektin scoreksi
    def decode(self, data):
        raise NotImplementedError

    # muuttaa scoren bytes objectkiksi
    def encode(self, score):
        raise NotImplementedError

    # tarkistaa _kaikki_ 
    def validate(self, *scores):
        pass

class ValidationError(Exception): pass
class CodecError(Exception): pass

class _CategoryScore:

    # laita __slots__ ja __cats__

    def __init__(self, data=None):
        if data is None:
            for k,v in self.__cats__:
                setattr(self, k, v.default)
        else:
            self.decode(data)

    # TODO muuta toi data streamiks (io.BytesIO)
    def decode(self, data):
        pos = 0
        for k,v in self.__cats__:
            val, l = v.decode(data[pos:])
            setattr(self, k, val)
            pos += l
        
        if pos != len(data):
            raise CodecError("read %d bytes of %d" % (pos, len(data)))

    def encode(self, dest):
        for k,v in self.__cats__:
            v.encode(dest, getattr(self, k))

    def validate(self):
        for k,v in self.__cats__:
            v.validate(getattr(self, k))

# cats_sorted: list(nimi, cat)
def cat_score(name, cats_sorted, bases=[]):
    class Ret(_CategoryScore, *bases):
        __slots__ = [k for k,v in cats_sorted]
        __cats__ = cats_sorted

    Ret.__name__ = name
    return Ret

class CategoryRuleset(Ruleset):

    def __init__(self, score_type):
        self.score_type = score_type

    def create_score(self):
        return self.score_type()

    def decode(self, data):
        return self.score_type(data)

    def encode(self, score):
        ret = bytearray()
        score.encode(ret)
        return ret

    def validate(self, score):
        score.validate()

class IntCategory:

    def __init__(self, default=0, length=2, signed=False):
        self.default = default
        self._length = length
        self._signed = signed

    def decode(self, data):
        return int.from_bytes(data[:self._length], byteorder="big", signed=self._signed),\
                self._length

    def encode(self, dest, value):
        dest.extend(value.to_bytes(self._length, byteorder="big", signed=self._signed))

    def validate(self, value):
        if value<0 and not self._signed:
            raise ValidationError("Expected unsigned integer")
        if value.bit_length() > 8*self._length:
            raise ValidationError("Value %d overflows %d bytes" % (value, self._length))

class ListCategory:

    def __init__(self, cat):
        self._cat = cat

    @property
    def default(self):
        return []

    def decode(self, data):
        ret = self.default
        pos = 1
        num = int(data[0])

        for _ in range(num):
            val, l = self._cat.decode(data[pos:])
            ret.append(val)
            pos += l

        return ret

    def encode(self, dest, value):
        dest.append(len(value))
        for v in value:
            self._cat.encode(dest, v)

    def validate(self, value):
        if len(value) > 0xff:
            raise ValidationError("List length overflow: %d" % len(value))
        for v in value:
            self._cat.validate(v)

# ottaa [team, ranking] listoja ja antaa [team, max_ranking] listan
def max_ranking(*rankings):
    max_ranks = {}

    for ranking in rankings:
        for t,r in ranking:
            if not t in max_ranks or max_ranks[t] < r:
                max_ranks[t] = r

    return max_ranks
