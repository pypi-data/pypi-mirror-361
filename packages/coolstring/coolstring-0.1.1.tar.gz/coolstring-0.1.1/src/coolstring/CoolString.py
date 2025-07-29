import warnings
import re
import random

warnings.simplefilter("always", UserWarning)
warnings.simplefilter("always", UnicodeWarning)
    
class CoolString:
    """
    This class implements a CoolString object that is a string with additional features. It tries to implement as
    many magic methods as possible.

    :param val: The value of the CoolString object.
    :type val: str or any object that can be converted to a string.
    :param creator: An optional CoolString object that is used to copy the attributes of the creator object. It is used
        to create new CoolString objects with the same attributes as the creator object so settings get derived from the creator.
    :type creator: :class:`CoolString`, optional

    """
    
    @staticmethod
    def convertval(val):
        """
        Converts the given value to a string representation.

        Throws a warning if the string representation is the
        identity representation of an object or class.

        :param val: The value to convert.
        :type val: any object that can be converted to a string.
        :return: The string representation of the value.
        :rtype: str
        :meta private:
        """
        if (re.fullmatch(r"<.*object at 0x[0-9a-fA-F]+>", str(val)) or re.fullmatch(r"<class '.*'>", str(val))) is not None:
            warnings.warn(f"{type(val).__name__} __str__ uses obj identity representation format",
            UserWarning
            )
        return str(val)

    @staticmethod
    def classifyfloat(val):
        """
        Classifies the given value as a float and determines if it is positive or negative.

        :param val: The value to classify.
        :type val: any object that can be converted to a float.
        :return: A tuple containing the float value and a boolean indicating if it is positive.
        :rtype: tuple(float, bool)
        :raises ValueError: If the value cannot be converted to a float.
        :meta private:
        """
        val2 = 0.0
        positive = False if str(val)[0] == "-" else True
        try:
            val2 = float(val)
        except ValueError:
            raise ValueError("Given variable not convertable to numeric")
        return (val2, positive)

    @staticmethod
    def classifyint(val):
        """
        Classifies the given value as an integer and determines if it is positive or negative.

        :param val: The value to classify.
        :type val: any object that can be converted to an integer.
        :return: A tuple containing the integer value and a boolean indicating if it is positive.
        :rtype: tuple(int, bool)
        :raises ValueError: If the value cannot be converted to an integer.
        :meta private:
        """
        val2 = 0
        positive = False if str(val)[0] == "-" else True
        try:
            val2 = int(val)
        except ValueError:
            try:
                val2 = int(float(val))
            except ValueError:
                raise ValueError("Given variable not convertable to numeric")
        return (val2, positive)
        
    @staticmethod
    def matchlengths(val1, val2):
        """
        Matches the lengths of two strings by padding the shorter one with spaces.

        :param val1: String to match with val2.
        :type val1: str
        :param val2: String to match with val1.
        :type val2: str
        :return: A tuple containing the two strings with matched lengths.
        :rtype: tuple(str, str)
        :meta private:
        """
        max_len = max(len(val1), len(val2))
        val1 = val1.ljust(max_len)
        val2 = val2.ljust(max_len)
        print(val1 + ".")
        print(val2 + ".")
        return (val1, val2)
        
    @staticmethod
    def bitshift(val, shift, direction):
        """
        Performs a bitwise shift on the given string value.

        This method encodes the string to bytes, converts it to an integer,
        shifts the bits, and then decodes it back to a string.

        :param val: The string value to shift.
        :type val: str
        :param shift: The number of bits to shift.
        :type shift: int
        :param direction: The direction of the shift, either "l" for left or "r" for right.
        :type direction: str
        :return: The new string value after the bitwise shift.
        :rtype: str
        :raises ValueError: If the direction is neither "l" nor "r".
        :meta private:
        """
        byte_data = val.encode('utf-8')
        bitval = int.from_bytes(byte_data, 'big')
        if direction == "l":
            bitval <<= shift
        elif direction == "r":
            bitval >>= shift
        else:
            raise ValueError("Direction is neither 'l' nor 'r'!")
        new_len = max((bitval.bit_length() + 7) // 8, 1)
        new_bytes = bitval.to_bytes(new_len, 'big')
        try:
            new_val = new_bytes.decode('utf-8')
        except UnicodeDecodeError:
            warnings.warn("Unable to decode bytes", UnicodeWarning)
            new_val = f"<binary:{new_bytes.hex()}>"
        return new_val

    def _decode(self, val):
        """
        Decodes the given value.

        :param val: The value to decode.
        :type val: str
        :return: The decoded value.
        :rtype: str
        :meta private:
        """
        return "".join(chr((ord(c) - 5) % 256) for c in val)

    def getcompval(self, val):
        """
        Gets the comparison value of the given value based on the configured comparison mode.

        :param val: The value to get the comparison value for.
        :type val: str
        :return: The comparison value.
        :rtype: int or str
        :raises ValueError: If the comparison mode is invalid.
        :meta private:
        """
        match self.compmode:
            case "length":
                return len(val)
            case "content":
                return val
            case "unicodesum":
                return sum(ord(a) for a in val)
            case "unicodemax":
                return max(ord(a) for a in val)
            case _:
                raise ValueError("Invalid compmode")
                
    def _createnew(self, val):
        """
        Creates a new CoolString object with the given value and the same attributes as the creator.

        :param val: The value for the new CoolString object.
        :type val: str or any object that can be converted to a string.
        :return: A new CoolString object with the given value and the same attributes as the creator.
        :rtype: :class:`CoolString`
        :meta private:
        """
        return CoolString(val, creator=self)

    def _verbose(self, *args, **kwargs):
        """
        Passes the given arguments to the print function if verbose mode is enabled.

        :param args: args
        :type args: tuple
        :param kwargs: kwargs
        :type kwargs: dict
        :meta private:
        """
        if self.verbose:
            print(*args, **kwargs)

    def configure(self, **kwargs):
        """
        Configures the CoolString object with the given keyword arguments.

        Valid keyword arguments include:

        - `shiftmode`: The shift mode, either "stringshift" or "bitshift".
        - `compmode`: The comparison mode, can be "length", "content", "unicodesum", or "unicodemax".
        - `verbose`: A boolean indicating whether to enable verbose mode.

        :param kwargs: Keyword arguments to configure the CoolString object.
        :type kwargs: dict
        :raises ValueError: If a given keyword argument is invalid.
        :meta public:
        """
        if "shiftmode" in kwargs.keys():
            self._verbose("Configuring CoolString with shiftmode:", kwargs["shiftmode"])
            if kwargs["shiftmode"] not in ["stringshift", "bitshift"]:
                raise ValueError("Invalid shiftmode")
            self.shiftmode = kwargs["shiftmode"]
        if "compmode" in kwargs.keys():
            self._verbose("Configuring CoolString with compmode:", kwargs["compmode"])
            if kwargs["compmode"] not in ["length", "content", "unicodesum", "unicodemax"]:
                raise ValueError("Invalid compmode")
            self.compmode = kwargs["compmode"]
        if "verbose" in kwargs.keys():
            self._verbose("Configuring CoolString with verbose mode:", kwargs["verbose"])
            if not isinstance(kwargs["verbose"], bool):
                raise ValueError("Verbose must be a boolean")
            self.verbose = kwargs["verbose"]
            
    def __init__(self, val, creator=None):
        """
        Initializes a CoolString object with the given value and an optional creator object.

        :param val: The value of the CoolString object.
        :type val: str or any object that can be converted to a string.
        :param creator: An optional CoolString object that is used to copy the attributes of the creator object.
        :type creator: :class:`CoolString`, optional
        """
        self.verbose = False
        if isinstance(creator, CoolString):
            self._verbose("Initializing CoolString with value:", val, "and copying attributes from creator")
            self.__dict__ = creator.__dict__.copy()
        else:
            self._verbose("Initializing CoolString with value:", val, "and default attributes:\n  (stringshift, content, verbose=False)")
            self.shiftmode = "stringshift"
            self.compmode = "content"
        self.val = self.convertval(val)
    
    def __str__(self):
        """
        Returns the string representation of the CoolString object.

        :return: The string representation of the CoolString object.
        :rtype: str
        :meta public:
        """
        self._verbose("Converting CoolString value to string")
        return self.val
    
    def __repr__(self):
        """
        Returns a string representation of the CoolString object for debugging purposes.

        :return: A meta styled string representation of the CoolString object.
        :rtype: str
        :meta public:
        """
        self._verbose("Creating string representation of CoolString object")
        return f"CoolString({self.val!r})"

    def __int__(self):
        """
        Converts the CoolString value to an integer.

        :return: The integer representation of the CoolString value.
        :rtype: int
        :raises ValueError: If the value cannot be converted to an integer.
        :meta public:
        """
        self._verbose("Converting CoolString value to int if possible")
        try:
            return int(self.val)
        except ValueError as e:
            try:
                return int(float(self.val))
            except (TypeError, ValueError) as e:
                raise ValueError("Value not convertible to int")
        except TypeError as e:
            raise ValueError("Value not convertible to int")

    def __float__(self):
        """
        Converts the CoolString value to a float.

        :return: The float representation of the CoolString value.
        :rtype: float
        :raises ValueError: If the value cannot be converted to a float.
        :meta public:
        """
        self._verbose("Converting CoolString value to float if possible")
        try:
            return float(self.val)
        except ValueError as e:
            raise ValueError("Value not convertible to float")

    def __add__(self, other):
        """
        Adds the given value to the CoolString value.

        :param other: The value to add to the CoolString value.
        :type other: str or any object that can be converted to a string.
        :return: A new CoolString object with the concatenated value.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Performing addition operation on CoolString value")
        otr = self.convertval(other)
        return self._createnew(self.val + otr)
    
    def __sub__(self, other):
        """
        Removes the given value from the CoolString value.

        :param other: The value to remove from the CoolString value.
        :type other: str or any object that can be converted to a string.
        :return: A new CoolString object with the value after removal.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value is not a substring of the CoolString value.
        :raises ValueError: If the given value cannot be converted to a string.
        :meta public:
        """
        otr = self.convertval(other)
        if otr not in self.val:
            raise ValueError("Given variable not part of CoolString")
        self._verbose("Removing", otr, "from CoolString value")
        return self._createnew(self.val.replace(otr, ""))
    
    def __mul__(self, other):
        """
        Multiplies the CoolString value by the given value.

        :param other: The value to multiply the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: A new CoolString object with the multiplied value.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        :meta public:
        """

        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        self._verbose("Multiplying CoolString value by", other)
        if not pos:
            val2 = self.val[::-1]
        else:
            val2 = self.val
        return self._createnew(val2 * abs(otr2))
    
    def __truediv__(self, other):
        """
        Divides the CoolString value by the given value.

        This method splits the CoolString value into parts of equal length based on length divided by the given value.
        If the other value is negative, the CoolString value is reversed before truncation and then reversed back.
        The remaining part is added as the last element in the list.

        :param other: The value to divide the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: A list of new CoolString objects with the truncated values.
        :rtype: list(:class:`CoolString`)
        :raises ValueError: If the given value cannot be converted to a numeric.
        :raises ValueError: If the CoolString value cannot be divided into the given number of parts.
        :meta public:
        """

        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        self._verbose("Dividing CoolString value by", other)
        if not pos:
            val2 = self.val[::-1]
        else:
            val2 = self.val
        idx = 0
        ret = []
        div = len(val2)//abs(otr2)
        if len(val2) < abs(otr2):
            raise ValueError("Cannot divide CoolString in more parts than its length")
        while idx <= len(val2)-div:
            ret.append(self._createnew(val2[idx:idx+div][::-1] if not pos else val2[idx:idx+div]))
            idx += div
        ret.append(self._createnew(val2[idx:][::-1] if not pos else val2[idx:]))
        return ret
    
    def __floordiv__(self, other):
        """
        The same as __truediv__ for the floor division operator.

        Only difference is that it does not return the remaining part as a new CoolString object.

        :param other: The value to divide the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: A new CoolString object with the truncated value.
        :rtype: list(:class:`CoolString`)
        :raises ValueError: If the given value cannot be converted to a numeric.
        :raises ValueError: If the CoolString value cannot be divided into the given number of parts.
        :meta public:
        """
        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        self._verbose("Floor dividing CoolString value by", other)
        if not pos:
            val2 = self.val[::-1]
        else:
            val2 = self.val
        idx = 0
        ret = []
        div = len(val2) // abs(otr2)
        if len(val2) < abs(otr2):
            raise ValueError("Cannot divide CoolString in more parts than its length")
        while idx <= len(val2) - div:
            ret.append(self._createnew(val2[idx:idx + div][::-1] if not pos else val2[idx:idx + div]))
            idx += div
        return ret
    
    def __mod__(self, other):
        """
        Modulo operator for CoolString.

        This method splits the CoolString value into parts of equal length based on length modulo the given value
        and returns the remaining part as a new CoolString object.

        :param other: The value to divide the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: A new CoolString object with the remaining value after division.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        :raises ValueError: If the CoolString value cannot be divided into the given number of parts.
        :meta public:
        """

        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        self._verbose("Performing modulo operation on CoolString value by", other)
        if not pos:
            val2 = self.val[::-1]
        else:
            val2 = self.val
        idx = 0
        ret = []
        div = len(val2) // abs(otr2)
        if len(val2) < abs(otr2):
            raise ValueError("Cannot divide CoolString in more parts than its length")
        while idx <= len(val2) - div:
            idx += div
        return self._createnew((val2[idx:][::-1] if not pos else val2[idx:]) if len(val2) % abs(otr2) != 0 else "")
    
    def __pow__(self, other):
        """
        Power operator for CoolString.

        This method repeats the CoolString value length power given value times.
        If the other value is negative, it truncates the CoolString value to a fraction of its length.
        The behavior is the same as the default power operator, but applied on string and its length.

        :param other: The value to raise the CoolString value to the power of.
        :type other: int or str or any object that can be converted to an integer.
        :return: A new CoolString object with the value raised to the power of the given value.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        :meta public:
        """

        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        self._verbose("Performing power operation on CoolString value to the power of", other)
        val2 = len(self.val)
        if not pos:
            valx = 1
            for i in range(0, abs(otr2)):
                valx = valx/val2
                print(valx)
            return self._createnew(self.val[0:int(len(self.val)*valx)])
        else:
            ret = CoolString(self.val)
            if otr2 == 0:
                ret = CoolString(self.val[0:1])
            else:
                origlen = len(ret)
                for i in range(0, otr2):
                    ret = ret * origlen
            return ret
        
    def __len__(self):
        """
        Returns the length of the CoolString value.

        :return: The length of the CoolString value.
        :rtype: int
        :meta public:
        """
        self._verbose("Getting length of CoolString value")
        return len(self.val)

    def __rshift__(self, other):
        """
        Right shift operator for CoolString.

        Depending on the shift mode, it either removes characters from the end of the string
        or performs a bitwise right shift on the string's byte representation.

        :param other: The value to shift the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: A new CoolString object with the shifted value.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        :meta public:
        """
        self._verbose("Performing right shift operation in", self.shiftmode, "mode")
        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        if not pos:
            return self.__lshift__(abs(otr2))
        if self.shiftmode == "stringshift":
            if otr2 > len(self.val):
                return self._createnew("")
            return self._createnew(self.val[0:-otr2])
        elif self.shiftmode == "bitshift":
            return self._createnew(self.bitshift(self.val, otr2, "r"))
    
    def __lshift__(self, other):
        """
        Left shift operator for CoolString.

        Depending on the shift mode, it either adds spaces to the end of the string
        or performs a bitwise left shift on the string's byte representation.

        :param other: The value to shift the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: A new CoolString object with the shifted value.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        :meta public:
        """
        self._verbose("Performing left shift operation in", self.shiftmode, "mode")
        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        if not pos:
            return self.__rshift__(abs(otr2))
        if self.shiftmode == "stringshift":
            return self._createnew(self.val + ' '*otr2)
        elif self.shiftmode == "bitshift":
            return self._createnew(self.bitshift(self.val, otr2, "l"))
            


    def __and__(self, other):
        """
        Bitwise AND operator for CoolString.

        :param other: The value to perform the bitwise AND operation with.
        :type other: str or any object that can be converted to a string.
        :return: A new CoolString object with the result of the bitwise AND operation.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Performing bitwise AND operation")
        otr = self.convertval(other)
        val2, otr2 = self.matchlengths(self.val, otr)
        return self._createnew("".join(chr(ord(a) & ord(b)) for a, b in zip(val2, otr2)))

    def __or__(self, other):
        """
        Bitwise OR operator for CoolString.

        :param other: The value to perform the bitwise OR operation with.
        :type other: str or any object that can be converted to a string.
        :return: A new CoolString object with the result of the bitwise OR operation.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Performing bitwise OR operation")
        otr = self.convertval(other)
        val2, otr2 = self.matchlengths(self.val, otr)
        return self._createnew("".join(chr(ord(a) | ord(b)) for a, b in zip(val2, otr2)))

    def __xor__(self, other):
        """
        Bitwise XOR operator for CoolString.

        :param other: The value to perform the bitwise XOR operation with.
        :type other: str or any object that can be converted to a string.
        :return: A new CoolString object with the result of the bitwise XOR operation.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Performing bitwise XOR operation")
        otr = self.convertval(other)
        val2, otr2 = self.matchlengths(self.val, otr)
        return self._createnew("".join(chr(ord(a) ^ ord(b)) for a, b in zip(val2, otr2)))


    # Comparasion operators
    
    def __lt__(self, other):
        """
        Less than operator for CoolString. Functionality depends on the comparison mode.

        :param other: The value to compare the CoolString value with.
        :type other: str or any object that can be converted to a string.
        :return: True if the CoolString value is less than the other value, False otherwise.
        :rtype: bool
        :raises ValueError: If the comparison mode is invalid.
        :meta public:
        """
        self._verbose("Performing less than operation using", self.compmode, "comparasion")
        otr = self.convertval(other)
        return self.getcompval(self.val) < self.getcompval(otr)
    
    def __gt__(self, other):
        """
        Greater than operator for CoolString. Functionality depends on the comparison mode.

        :param other: The value to compare the CoolString value with.
        :type other: str or any object that can be converted to a string.
        :return: True if the CoolString value is greater than the other value, False otherwise.
        :rtype: bool
        :raises ValueError: If the comparison mode is invalid.
        :meta public:
        """
        self._verbose("Performing greater than operation using", self.compmode, "comparasion")
        otr = self.convertval(other)
        return self.getcompval(self.val) > self.getcompval(otr)
    
    def __le__(self, other):
        """
        Less than or equal to operator for CoolString. Functionality depends on the comparison mode.

        :param other: The value to compare the CoolString value with.
        :type other: str or any object that can be converted to a string.
        :return: True if the CoolString value is less than or equal to the other value, False otherwise.
        :rtype: bool
        :raises ValueError: If the comparison mode is invalid.
        :meta public:
        """
        self._verbose("Performing less than or equal operation using", self.compmode, "comparasion")
        otr = self.convertval(other)
        return self.getcompval(self.val) <= self.getcompval(otr)
    
    def __ge__(self, other):
        """
        Greater than or equal to operator for CoolString. Functionality depends on the comparison mode.

        :param other: The value to compare the CoolString value with.
        :type other: str or any object that can be converted to a string.
        :return: True if the CoolString value is greater than or equal to the other value, False otherwise.
        :rtype: bool
        :raises ValueError: If the comparison mode is invalid.
        :meta public:
        """
        self._verbose("Performing greater than or equal operation using", self.compmode, "comparasion")
        otr = self.convertval(other)
        return self.getcompval(self.val) >= self.getcompval(otr)
    
    def __eq__(self, other):
        """
        Equality operator for CoolString. Functionality depends on the comparison mode.

        :param other: The value to compare the CoolString value with.
        :type other: str or any object that can be converted to a string.
        :return: True if the CoolString value is equal to the other value, False otherwise.
        :rtype: bool
        :raises ValueError: If the comparison mode is invalid.
        :meta public:
        """
        self._verbose("Performing equal operation using", self.compmode, "comparasion")
        otr = self.convertval(other)
        return self.getcompval(self.val) == self.getcompval(otr)
    
    def __ne__(self, other):
        """
        Not equal operator for CoolString. Functionality depends on the comparison mode.

        :param other: The value to compare the CoolString value with.
        :type other: str or any object that can be converted to a string.
        :return: True if the CoolString value is not equal to the other value, False otherwise.
        :rtype: bool
        :raises ValueError: If the comparison mode is invalid.
        :meta public:
        """
        self._verbose("Performing not equal operation using", self.compmode, "comparasion")
        otr = self.convertval(other)
        return self.getcompval(self.val) != self.getcompval(otr)
        
    # Assignment operators
    
    def __iadd__(self, other):
        """
        In-place addition operator for CoolString.

        :param other: The value to add to the CoolString value.
        :type other: str or any object that can be converted to a string.
        :return: The CoolString object itself after addition.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Performing in-place addition operation")
        otr = self.convertval(other)
        self.val = self.val + otr
        return self
    
    def __isub__(self, other):
        """
        In-place subtraction operator for CoolString.

        :param other: The value to remove from the CoolString value.
        :type other: str or any object that can be converted to a string.
        :return: The CoolString object itself after removal.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value is not a substring of the CoolString value.
        :meta public:
        """
        self._verbose("Performing in-place subtraction operation")
        otr = self.convertval(other)
        if otr not in self.val:
            raise ValueError("Given variable not part of CoolString")
        self.val = self.val.replace(otr, "")
        return self
    
    def __imul__(self, other):
        """
        In-place multiplication operator for CoolString.

        :param other: The value to multiply the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: The CoolString object itself after multiplication.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        :meta public:
        """
        self._verbose("Performing in-place multiplication operation")
        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        if not pos:
            self.val = self.val[::-1]
        self.val = self.val * abs(otr2)
        return self
    
    def __itruediv__(self, other):
        """
        In-place division operator for CoolString.

        This method truncates the CoolString value to a fraction of its length based on the given value.
        This length is determined by the length of the CoolString divided by the given value.
        If the other value is negative, the CoolString value is reversed before truncation and then reversed back.

        :param other: The value to divide the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: The CoolString object itself after division.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        :meta public:
        """
        self._verbose("Performing in-place division operation")
        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        if not pos:
            self.val = self.val[::-1]
        self.val = self.val[0:len(self.val)//abs(otr2)]
        if not pos:
            self.val = self.val[::-1]
        return self
            
    def __ifloordiv__(self, other):
        """
        In-place floor division operator for CoolString.

        This method is similar to __idiv__.

        :param other: The value to divide the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: The CoolString object itself after floor division.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        """
        self._verbose("Performing in-place floor division operation")
        return self.__itruediv__(other)
    
    def __imod__(self, other):
        """
        In-place modulo operator for CoolString.

        This method truncates the CoolString value to a fraction of its length based on the given value.
        The length is determined by the length of the CoolString modulo the given value.
        If the other value is negative, the CoolString value is reversed before truncation and then reversed back.

        :param other: The value to divide the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: The CoolString object itself after modulo operation.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        :meta public:
        """
        self._verbose("Performing in-place modulo operation")
        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        if not pos:
            self.val = self.val[::-1]
        self.val = self.val[0:len(self.val)%abs(otr2)]
        if not pos:
            self.val = self.val[::-1]
        return self
        
    def __ipow__(self, other):
        """
        In-place power operator for CoolString.

        This method repeats the CoolString value length power given value times.
        If the other value is negative, it truncates the CoolString value to a fraction of its length.
        The behavior is the same as the default power operator, but applied on string and its length.

        :param other: The value to raise the CoolString value to the power of.
        :type other: int or str or any object that can be converted to an integer.
        :return: The CoolString object itself after raising to the power.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        :meta public:
        """
        self._verbose("Performing in-place power operation")
        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        val2 = len(self.val)
        if not pos:
            valx = 1
            for i in range(0, abs(otr2)):
                valx = valx/val2
                print(valx)
            self.val = self.val[0:int(len(self.val)*valx)]
        else:
            if otr2 == 0:
                self.val = self.val[0:1]
            else:
                origlen = len(self.val)
                for i in range(0, otr2):
                    self.val = self.val * origlen
        return self
                    
    def __irshift__(self, other):
        """
        In-place right shift operator for CoolString.

        Depending on the shift mode, it either removes characters from the end of the string
        or performs a bitwise right shift on the string's byte representation.

        :param other: The value to shift the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: The CoolString object itself after right shifting.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        :meta public:
        """
        self._verbose("Performing in-place right shift operation in", self.shiftmode, "mode")
        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        if not pos:
            return self.__ilshift__(abs(otr2))
        if self.shiftmode == "stringshift":
            if otr2 > len(self.val):
                self.val = ""
            self.val = self.val[0:-otr2]
        elif self.shiftmode == "bitshift":
            self.val = self.bitshift(self.val, otr2, "r")
        return self
    
    def __ilshift__(self, other):
        """
        In-place left shift operator for CoolString.

        Depending on the shift mode, it either adds spaces to the end of the string
        or performs a bitwise left shift on the string's byte representation.

        :param other: The value to shift the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: The CoolString object itself after left shifting.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        :meta public:
        """
        self._verbose("Performing in-place left shift operation in", self.shiftmode, "mode")
        otr = self.convertval(other)
        otr2, pos = self.classifyint(otr)
        if not pos:
            return self.__irshift__(abs(otr2))
        if self.shiftmode == "stringshift":
            self.val = self.val + ' '*otr2
        elif self.shiftmode == "bitshift":
            self.val = self.bitshift(self.val, otr2, "l")
        return self
    
    def __iand__(self, other):
        """
        In-place bitwise AND operator for CoolString.

        :param other: The value to perform the bitwise AND operation with.
        :type other: str or any object that can be converted to a string.
        :return: The CoolString object itself after the bitwise AND operation.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Performing in-place bitwise AND operation")
        otr = self.convertval(other)
        val2, otr2 = self.matchlengths(self.val, otr)
        self.val = "".join(chr(ord(a) & ord(b)) for a, b in zip(val2, otr2))
        return self
        
    def __ior__(self, other):
        """
        In-place bitwise OR operator for CoolString.

        :param other: The value to perform the bitwise OR operation with.
        :type other: str or any object that can be converted to a string.
        :return: The CoolString object itself after the bitwise OR operation.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Performing in-place bitwise OR operation")
        otr = self.convertval(other)
        val2, otr2 = self.matchlengths(self.val, otr)
        self.val = "".join(chr(ord(a) | ord(b)) for a, b in zip(val2, otr2))
        return self
    
    def __ixor__(self, other):
        """
        In-place bitwise XOR operator for CoolString.

        :param other: The value to perform the bitwise XOR operation with.
        :type other: str or any object that can be converted to a string.
        :return: The CoolString object itself after the bitwise XOR operation.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Performing in-place bitwise XOR operation")
        otr = self.convertval(other)
        val2, otr2 = self.matchlengths(self.val, otr)
        self.val = "".join(chr(ord(a) ^ ord(b)) for a, b in zip(val2, otr2))
        return self
      
    # Unary operators
    
    def __neg__(self):
        """
        Negation operator for CoolString.

        This method converts the CoolString value to lowercase.

        :return: A new CoolString object with the value in lowercase.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Converting CoolString to lowercase")
        return CoolString(self.val.lower())
    
    def __pos__(self):
        """
        Positive operator for CoolString.

        This method converts the CoolString value to uppercase.

        :return: A new CoolString object with the value in uppercase.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Converting CoolString to uppercase")
        return CoolString(self.val.upper())
    
    def __invert__(self):
        """
        Inversion operator for CoolString.

        This method swaps the case of all characters in the CoolString value.

        :return: A new CoolString object with the value with swapped case.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Swapping case of CoolString")
        return CoolString(self.val.swapcase())

    def __trunc__(self):
        """
        Truncates the CoolString value to an integer.

        :return: The integer representation of the CoolString value.
        :rtype: int
        :raises ValueError: If the value cannot be converted to an integer.
        :meta public:
        """
        self._verbose("Calculating truncated (int) value of CoolString")
        return int(self)

    def __ceil__(self):
        """
        Ceil operator for CoolString.

        This method rounds the CoolString value up to the nearest integer.

        :return: The integer representation of the CoolString value rounded up.
        :rtype: int
        :raises ValueError: If the value cannot be converted to an integer.
        :meta public:
        """
        self._verbose("Calculating ceil value of CoolString")
        val2, pos = self.classifyint(self.val)
        if not pos:
            return int(self)
        else:
            return int(self) + 1 if self.val[-1] != '0' else int(self)

    def __floor__(self):
        """
        Floor operator for CoolString.

        This method rounds the CoolString value down to the nearest integer.

        :return: The integer representation of the CoolString value rounded down.
        :rtype: int
        :raises ValueError: If the value cannot be converted to an integer.
        :meta public:
        """
        self._verbose("Calculating floor value of CoolString")
        val2, pos = self.classifyint(self.val)
        if not pos:
            return int(self) - 1 if self.val[-1] != '0' else int(self)
        else:
            return int(self)

    def __round__(self, ndigits=2):
        """
        Rounds the CoolString value to a specified number of digits.

        This method prefers mathematical rounding to string length rounding if possible.
        If the value cannot be converted to a float, it rounds based on the length of the string.
        if string length `round(length/base) * base` is less than or equal to the length of the string,
        it truncates the string to that length, otherwise it pads the string with spaces.

        :param ndigits: The number of digits to round to. If negative, it rounds to the nearest base of 10.
        :type ndigits: int or str or any object that can be converted to an integer.
        :return: A new CoolString object with the rounded value.
        :rtype: :class:`CoolString`
        :raises ValueError: If the given value cannot be converted to a numeric.
        :meta public:
        """
        ndig = self.convertval(ndigits)
        ndig2, pos = self.classifyint(ndig)
        try:
            valf, pos2 = self.classifyfloat(self.val)
            self._verbose("Mathematical rounding with value:", valf, "and ndigits:", ndig2)
            return self._createnew(f"{round(valf, ndig2)}")
        except ValueError:
            self._verbose("Rounding based on string length `round(length/base) * base` with ndigits:", ndig2)
            n = 10 ** abs(ndig2) if ndig2 < 0 else ndig2
            rlen = round(len(self.val) / n) * n
            if rlen <= len(self.val):
                return self._createnew(self.val[:rlen])

            else:
                return self._createnew(self.val.ljust(rlen))


    def __abs__(self):
        """
        Absolute value operator for CoolString.

        This method returns a new CoolString object with all words starting with '-' having their case swapped.

        :return: A new CoolString object with swapped case for words starting with '-'.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Swapping case of all words starting with '-'")
        words = self.val.split(" ")
        for i, word in enumerate(words):
            if word and word[0] == "-":
                words[i] = word[1:].swapcase()
        return self._createnew(" ".join(words))

    def __divmod__(self, other):
        """
        Divmod operator for CoolString.

        This method returns a tuple containing the result of true division and modulo operation on the CoolString value.

        :param other: The value to divide the CoolString value by.
        :type other: int or str or any object that can be converted to an integer.
        :return: A tuple containing the result of true division and modulo operation.
        :rtype: tuple(list(:class:`CoolString`), :class:`CoolString`)
        :raises ValueError: If the given value cannot be converted to a numeric.
        :meta public:
        """
        self._verbose("Performing divmod operation on CoolString")
        return self.__floordiv__(other), self.__mod__(other)

    def __unicode__(self):
        """
        Returns the CoolString value as a Unicode string.

        :return: A Unicode string representation of the CoolString value.
        :rtype: str
        :meta public:
        """
        self._verbose("Converting CoolString to Unicode string")
        return self.val.encode('utf-8')

    def __format__(self, format_spec):
        """
        Formats the CoolString value according to the given format specification.
        This method supports various format specifications such as:

        - "d": Decimal representation of character codes
        - "b": Binary representation of character codes
        - "o": Octal representation of character codes
        - "x": Hexadecimal representation of character codes
        - "X": Uppercase hexadecimal representation of character codes
        - ",": Comma-separated format every 3 characters
        - "_": Underscore-separated format every 3 characters
        - "%": Appends a percentage sign to the end of the string
        - "g": General format, removing non-alphanumeric characters and
          replacing multiple whitespaces with a single space
        - "G": General format, removing non-alphanumeric characters and
          multiple whitespaces with a single space, then converting to uppercase
        - "u": Converts the CoolString value to uppercase
        - "l": Converts the CoolString value to lowercase
        - "s": Swaps the case of the CoolString value
        - "i": Reverses the CoolString value
        - Any other format specifier is passed to the default format function.

        :param format_spec: The format specification string.
        :type format_spec: str
        :return: A formatted string representation of the CoolString value.
        :rtype: str
        :raises ValueError: If the format specification is invalid.
        :meta public:
        """
        self._verbose("Formatting CoolString with format_spec:", format_spec)
        match format_spec:
            case "d":
                chars = [ord(c) for c in self.val]
                return " ".join(str(c) for c in chars)
            case "b":
                chars = [ord(c) for c in self.val]
                return " ".join(format(c, '08b') for c in chars)
            case "o":
                chars = [ord(c) for c in self.val]
                return " ".join(format(c, 'o') for c in chars)
            case "x":
                chars = [ord(c) for c in self.val]
                return " ".join(format(c, 'x') for c in chars)
            case "X":
                chars = [ord(c) for c in self.val]
                return " ".join(format(c, 'X') for c in chars)
            case ",":
                return ",".join([self.val[i:i+3] for i in range(0, len(self.val), 3)])
            case "_":
                return "_".join([self.val[i:i+3] for i in range(0, len(self.val), 3)])
            case "%":
                return self.val + "%"
            case "g":
                newval = re.sub(r"\s+", ' ', self.val)
                return re.sub(r"[^a-zA-Z0-9 ]", "", newval).strip()
            case "G":
                newval = re.sub(r"\s+", ' ', self.val)
                return re.sub(r"[^a-zA-Z0-9 ]", "", newval).strip().upper()
            case "u":
                return self.val.upper()
            case "l":
                return self.val.lower()
            case "s":
                return self.val.swapcase()
            case "i":
                return self.val[::-1]
            case _:
                return format(self.val, format_spec)

    def __hash__(self):
        """
        Returns a hash of the CoolString object.
        This method hashes the CoolString value and its attributes by xoring the hash of the value
        and the hash of the attributes.

        :return: A hash value of the CoolString object.
        :rtype: int
        :meta public:
        """
        self._verbose("Hashing object by xoring hash of the value and hash of the attributes")
        valhash = hash(self.val)
        attrs = tuple(sorted(self.__dict__.items()))
        attrshash = hash(attrs)
        return valhash ^ attrshash

    def __bool__(self):
        """
        Returns True if the CoolString value is not empty, False otherwise.

        :return: True if the CoolString value is not empty, False otherwise.
        :rtype: bool
        :meta public:
        """
        self._verbose("Checking if CoolString is empty")
        return bool(self.val)

    def __contains__(self, item):
        """
        Checks if the given item is in the CoolString value.

        :param item: The item to check for in the CoolString value.
        :type item: str or any object that can be converted to a string.
        :return: True if the item is in the CoolString value, False otherwise.
        :rtype: bool
        :meta public:
        """
        otr = self.convertval(item)
        self._verbose("Checking if item is in CoolString")
        return otr in self.val

    def __delattr__(self, name):
        """
        Deletes an attribute from the CoolString object.

        This method prevents deletion of critical attributes such as 'shiftmode', 'compmode', 'verbose', and 'val'.

        :param name: The name of the attribute to delete.
        :type name: str
        :raises AttributeError: If the attribute is critical and cannot be deleted.
        :meta public:
        """
        if name in ("shiftmode", "compmode", "verbose", "val"):
            raise AttributeError("Deleting critical attributes is prohibited")
        self._verbose(f"Deleting attribute {name} from CoolString")
        super().__delattr__(name)

    def __iter__(self):
        """
        Creates an iterator for the CoolString value.

        :return: An iterator for the CoolString value.
        :rtype: iterator
        :meta public:
        """
        self._verbose("Creating an iterator for CoolString")
        return iter(self.val)

    def __call__(self, *args, **kwargs):
        """
        Calls the CoolString object as a function.

        This method returns some cool string.

        :param args: args
        :type args: tuple
        :param kwargs: kwargs
        :type kwargs: dict
        :return: A random cool string.
        :rtype: str
        :meta public:
        """
        self._verbose("Called CoolString as a function, because you are cool!")
        x = ['Ymnx%nx%sty%ozxy%f%xywnsl333%ny,x%HTTQ%?.',
             'Ymj%Fsx|jw%yt%ymj%Lwjfy%Vzjxynts%333%tk%Qnkj1%ymj%Zsn{jwxj%fsi%J{jw~ymnsl%333%nx%333%Ktwy~2y|t3',
             'Xufhj1%ymj%knsfq%kwtsynjw3']
        return self._decode(x[random.randint(0, len(x) - 1)])

    def __getitem__(self, idx):
        """
        Gets a portion of the CoolString value based on the given index or slice.

        :param idx: The index or slice to get from the CoolString value.
        :type idx: int or slice
        :return: A new CoolString object with the value at the given index or slice.
        :rtype: :class:`CoolString`
        :raises IndexError: If the index is out of range.
        :raises TypeError: If the index is not an integer or a slice.
        :meta public:
        """
        if isinstance(idx, slice):
            self._verbose(f"Getting slice {idx} from CoolString")
            return self._createnew(self.val[idx])
        elif isinstance(idx, int):
            if idx < 0:
                idx += len(self.val)
            if idx < 0 or idx >= len(self.val):
                raise IndexError("Index out of range")
            self._verbose(f"Getting item at index {idx} from CoolString")
            return self._createnew(self.val[idx])
        else:
            raise TypeError("Index must be an integer or a slice")

    def __reversed__(self):
        """
        Reverses the CoolString value.

        This method works similar to the ~-operator.

        :return: A new CoolString object with the value reversed.
        :rtype: :class:`CoolString`
        :meta public:
        """
        self._verbose("Reversing CoolString")
        return self._createnew(self.val[::-1])

