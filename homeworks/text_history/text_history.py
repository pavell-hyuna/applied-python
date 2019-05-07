def compute_actions(actions):
    result = []
    for key, value in enumerate(actions):
        next_action = actions[key + 1]
        if  isinstance(value, InsertAction) == isinstance(next_action, InsertAction):
            result.append(type(value)(value.pos, value.from_version, next_action.to_version,
                                      value.text + next_action.text))
            del actions[key + 1]
        elif isinstance(value, DeleteAction) and isinstance(next_action, DeleteAction):
            if next_action.pos == value.pos + value.length:
                result.append(type(value)(value.pos, next_action.pos + next_action.length))
                del actions[key + 1]
            else:
                result.append(value)
        else:
            result.append(value)
    return result


class Action:

    def __init__(self, pos, from_version, to_version, text='', length=None):
        self._pos = pos
        self._text = text
        self._length = length
        self._from_version = from_version
        self._to_version = to_version

    @property
    def version(self):
        return self._to_version

    @property
    def from_version(self):
        return self._from_version

    @property
    def to_version(self):
        return self._to_version

    @property
    def text(self):
        return self._text

    @property
    def pos(self):
        return self._pos

    @property
    def length(self):
        return self._length


class InsertAction(Action):

    def apply(self, text):
        return text[:self._pos] + self._text + text[self._pos:]


class ReplaceAction(Action):

    def apply(self, text):
        return text[:self._pos] + self._text + text[self._pos + self._length:]


class DeleteAction(Action):

    def apply(self, text):
        return text[:self._pos] + text[self._pos + self._length:]


class TextHistory:

    def __init__(self):
        self._text = ''
        self._version = 0
        self._history = []

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def validate_position(self, position, length=0):
        if position < 0 or position > len(self._text) or \
                (length != 0 and len(self._text[position:]) < length):
            raise ValueError()

    def get_position_from_defaults(self, position):
        return len(self._text) if position == '' else position

    def insert(self, text, pos=''):
        pos = self.get_position_from_defaults(pos)
        self.validate_position(pos)

        insert_object = InsertAction(pos, self._version, self._version + 1, text)
        self._history.append(insert_object)
        self._text = self._text[:pos] + text + self._text[pos:]
        self._version += 1
        return self._version

    def replace(self, text, pos=''):
        pos = self.get_position_from_defaults(pos)
        self.validate_position(pos)

        replace_object = ReplaceAction(pos, self._version, self._version + 1, text)
        self._history.append(replace_object)

        self._text = self._text[:pos] + text + self._text[pos+1:]
        self._version += 1
        return self._version

    def delete(self, pos, length):
        pos = self.get_position_from_defaults(pos)
        self.validate_position(pos, length)

        delete_object = DeleteAction(pos, self._version, self._version + 1, length=length)
        self._history.append(delete_object)

        self._text = self._text[:pos] + self._text[pos + length:]
        self._version += 1
        return self._version

    def action(self, action):
        if action.version < self._version \
                or action.from_version == action.to_version\
                or action.to_version < action.from_version\
                or action.pos < 0\
                or action.length == 0:
            raise ValueError
        self._text = action.apply(self._text)
        self._version = action.version
        return self._version

    def get_actions(self, from_version=0, to_version=0):
        if from_version > 0 and not to_version:
            to_version = self._version
        if from_version == 0 and to_version == 0:
            return []
        elif to_version > self._version:
            raise ValueError
        elif to_version < from_version:
            raise ValueError
        elif from_version < 0:
            raise ValueError

        actions = list(filter(lambda x: from_version < x.version <= to_version, self._history))
        return actions