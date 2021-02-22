class Dyn(object):
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, Dyn):
            return False
        if (self.A() != other.A()).any() or (self.b() != other.b()).any():
            return False
        return True
