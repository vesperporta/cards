"""
Copyright 2020 (c) GlibGlob Ltd.
Author: Laurence
Email: vesper.porta@protonmail.com

Models for Tarot information storage.
"""


class StatType:
    """Generic store for a type of data with a simple value associated."""
    _name = ''
    search = ''
    description = ''
    ratio = 0

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value or ''
        if not value:
            return
        if type(value) is list:
            value = ''.join(value)
        self.search = value.replace(' ', '').lower()

    def __init__(self, name=None, description='', ratio=1.0):
        self.name = name
        self.description = description
        self.ratio = ratio

    def __str__(self):
        return '<StatType "{}", ratio: {}>'.format(self.name, self.ratio)


class StatGroup:
    """Defining group of stats, defaults: Stat, discipline, skill."""
    _name = ''
    search = ''
    description = ''
    stats = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value or ''
        if not value:
            return
        self.search = value.replace(' ', '').lower()

    def find(self, related, auto_create=True):
        """
        Find the statistic of a relational name:
        Passing in another statistic a found statistic from this known list
        will be returned with no match to object equality other than name id.
        For a none found statistic object in this list but a statistic is passed
        as a relational object a new statistic will be aded to the group as a
        separately managed object.
        Equality of string identifiers will be returned as normal.

        :param related: Stat | StatType | str
        :param auto_create: bool, to automatically create a statistic.
        :return: Stat or None
        """
        found = None
        names = [stat.search for stat in self.stats]
        if hasattr(related, 'name'):
            value_name = related.name.replace(' ', '').lower()
            if value_name in names:
                found = self.stats[names.index(value_name)]
        elif hasattr(related, 'type'):
            value_type = related.type.name.replace(' ', '').lower()
            if value_type in names:
                found = self.stats[names.index(value_type)]
        else:
            value = related.replace(' ', '').lower()
            names = [stat.search for stat in self.stats]
            if value in names:
                found = self.stats[names.index(value)]
        if not found and auto_create:
            found = Stat(name=related, group=self)
            if hasattr(related, 'type'):
                found.type = related.type
            if hasattr(related, 'group'):
                found.unknown['group'] = related.group
            self.stats.append(found)
        return found

    def find_of_type(self, name):
        """
        Find the statistics which are bound by a type.

        :param name: str identifier for type name.
        :return: list
        """
        return [a for a in self.stats if a.type.name == name]

    def update(self):
        """Update statistics associated with this group."""
        for s in self.stats:
            s.update()

    def __init__(self, name=None, description='', stats=None):
        self.name = name
        self.description = description
        self.stats = stats or []

    def __str__(self):
        lst = ['{}: {}'.format(s.name, s.total) for s in self.stats]
        return '<StatGroup "{}", stats={}>'.format(
            self.name,
            str(lst[:20]) if len(lst) < 20 else str(lst[:20])[:-1] + ', ...]'
        )


class Stat:
    """Basic stat option."""
    type = None
    _name = ''
    search = ''
    description = ''
    group = None
    unknown = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value or ''
        if not value:
            return
        self.search = value.replace(' ', '').lower()

    def __init__(self, name=None, group=None):
        self.name = name
        self.group = group
        if self.group and self._name not in [g.name for g in self.group.stats]:
            self.group.stats.append(self)
        self.unknown = {}

    def __str__(self):
        return '<Stat name: "{}", group: "{}">'.format(
            self.name, self.group.name if self.group else 'None')
