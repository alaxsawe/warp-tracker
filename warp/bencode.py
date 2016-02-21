"""Nov 25 16:07 MSK 2015
warp-tracker - bencode.py

Bencode elems map:
  <int>:<string>                : string
  i<int>e                       : int
  l<elem>...e                   : list
  d<key_elem><val_elem>...e     : dict

"""

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def decode(ben_string):
    """ Returns decoded data """
    return _decode(ben_string)[0]


def _decode(ben_string, start_from=0):
    """ Bencode decode function """
    position = start_from
    char = chr(ben_string[position])

    if char in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0'):
        string_len_text = char
        position += 1
        follow_char = chr(ben_string[position])
        while follow_char != ':':
            string_len_text = '{}{}'.format(string_len_text, follow_char)
            position += 1
            follow_char = chr(ben_string[position])
        position += 1
        string_start = position
        string_finish = string_start + int(string_len_text)
        return (ben_string[string_start:string_finish]), string_finish

    elif char == 'i':
        position += 1
        follow_char = chr(ben_string[position])
        int_text = ''
        while follow_char != 'e':
            int_text = '{}{}'.format(int_text, follow_char)
            position += 1
            follow_char = chr(ben_string[position])
        return int(int_text), position + 1

    elif char == 'l':
        position += 1
        follow_char = chr(ben_string[position])
        res_list = []
        while follow_char != 'e':
            item, position = _decode(ben_string, start_from=position)
            res_list.append(item)
            follow_char = chr(ben_string[position])
        return res_list, position + 1

    elif char == 'd':
        position += 1
        follow_char = chr(ben_string[position])
        res_dict = {}
        while follow_char != 'e':
            key, position = _decode(ben_string, start_from=position)
            value, position = _decode(ben_string, start_from=position)
            res_dict.update({key: value})
            follow_char = chr(ben_string[position])
        return res_dict, position + 1


def encode(struct):
    """ Returns encoded data """
    return _encode(struct)


def _encode(struct):
    """ Encoding structure to bencoded bytestring """
    if isinstance(struct, dict):
        res = b''
        for key, value in sorted(struct.items(), key=lambda x: x[0]):
            res = b'%b%b%b' % (res, _encode(key), _encode(value))
        return b'd%be' % res

    elif isinstance(struct, list):
        return b'l%be' % b''.join([_encode(n) for n in struct])

    elif isinstance(struct, bytes):
        return b'%d:%b' % (len(struct), struct)

    elif isinstance(struct, int):
        return b'i%de' % struct


if __name__ == '__main__':
    assert decode(b'0:') == b''
    assert decode(b'5:Hello') == b'Hello'
    assert decode(b'12:Hello World!') == b'Hello World!'
    assert decode(b'i42e') == 42
    assert decode(b'i-1e') == -1
    assert decode(b'l5:helloe') == [b'hello']
    assert decode(b'l5:hello5:worlde') == [b'hello', b'world']
    assert decode(b'd5:hello5:world2:hil5:hello5:worldee') == {b'hello': b'world', b'hi': [b'hello', b'world']}
    assert decode(b'd5:hello5:world2:hil5:hello5:worlde3:hi2l5:hello5:worldee') == {b'hello': b'world', b'hi2': [b'hello', b'world'], b'hi': [b'hello', b'world']}

    assert encode(b'') == b'0:'
    assert encode(b'Hello') == b'5:Hello'
    assert encode(42) == b'i42e'
    assert encode(-1) == b'i-1e'
    assert encode([b'hello']) == b'l5:helloe'
    assert encode([b'hello', b'world']) == b'l5:hello5:worlde'
    assert encode({b'hello': b'world', b'hi': [b'hello', b'world']}) == b'd5:hello5:world2:hil5:hello5:worldee'
    assert encode({b'hello': b'world', b'hi2': [b'hello', b'world'], b'hi': [b'hello', b'world']}) == b'd5:hello5:world2:hil5:hello5:worlde3:hi2l5:hello5:worldee'
