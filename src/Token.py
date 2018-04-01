class Token(object):
    """
    A simple Token object for describing a tagged portion of the text
    """

    def __init__(self, text, init_index, end_index, tag):
        """
        Args:
            text (string): The text contained in the segment
            init_index (int): The index in which the token starts
            end_index (int): The index in which the token ends
            tag (string): The tag to be applied to the token
        """

        if len(text) != end_index - init_index + 1:
            raise Exception("Token text does not fit the boundaries")

        self._text = text
        self._init_index = init_index
        self._end_index = end_index
        self.tag = tag
    
    def enclosing(self, i):
        """
        Returns a bool indicating if 'i' is in the token boundaries
        
        Args:
            i (int): The value that will be searched inside the token boundaries
        
        Returns:
            bool: True if inside the token boundaries, false otherwise
        """
        if self._init_index <= i <= self._end_index:
            return True
        return False