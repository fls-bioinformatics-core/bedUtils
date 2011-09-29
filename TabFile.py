class TabFile:
    """Class to get data from a tab-delimited file

    Loads data from the specified file into a data structure than can
    then be queried on a per line and per item basis.

    Data lines are represented by TabDataLine objects.

    Example usage:

        data = TabFile(myfile)     # load initial data

        print '%s' % len(data)     # report number of lines of data

        print '%s' % data.header() # report header (i.e. column names)

        for line in data:
            ...                    # loop over lines of data

        myline = data[0]           # fetch first line of data
    """
    def __init__(self,filen,column_names=None,skip_first_line=False,
                 first_line_is_header=False):
        """Create a new TabFile object

        Arguments:
          filen: name of tab-delimited file to load
          column_names: (optional) list of column names to assign to
              columns in the file
          skip_first_line: (optional) if True then ignore the first
              line of the input file
          first_line_is_header: (optional) if True then takes column
              names from the first line of the file (over-riding
              'column_names' argument if specified.
        """
        # Initialise
        self.__filen = filen
        self.__ncols = 0
        # Set up column names
        self.__header = []
        if column_names is not None:
            self.setHeader(column_names)
        # Read in data
        self.__data = []
        self.load(skip_first_line=skip_first_line,
                  first_line_is_header=first_line_is_header)

    def load(self,skip_first_line=False,first_line_is_header=False):
        """Load data into the object from file

        *** Should not be called externally ***

        Lines starting with '#' are ignored (unless the first_line_is_header
        is set and the first line starts with '#').

        If a header is set then lines with fewer data items than header
        items raise an IndexError exception.

        Arguments:
          skip_first_line: (optional) if True then ignore the first
              line of the input file
          first_line_is_header: (optional) if True then take column
              names from the first line of the file
        """
        line_no = 0
        fp = open(self.__filen,'rU')
        for line in fp:
            line_no += 1
            if skip_first_line:
                # Skip first line
                skip_first_line = False
                continue
            elif first_line_is_header:
                # Set up header from first line
                self.setHeader(line.strip().strip('#').split('\t'))
                first_line_is_header = False
                continue
            if line.lstrip().startswith('#'):
                # Skip commented line
                continue
            # Store data
            data_line = TabDataLine(line,column_names=self.header(),lineno=line_no)
            if self.__ncols > 0 and len(data_line) < self.__ncols:
                # Inconsistent lines are an error
                logging.error("L%d: fewer data items in line than expected" % line_no)
                raise IndexError, "Not enough data items in line"
            self.__data.append(data_line)
        fp.close()

    def setHeader(self,column_names):
        """Set the names for columns of data

        *** Should not be called externally ***

        Arguments:
          column_names: a tuple or list with names for each column in order.
        """
        if len(self.__header) > 0:
            logging.warning("Overriding existing headers")
            self.__header = []
        for name in column_names:
            self.__header.append(name)
        self.__ncols = len(self.__header)

    def header(self):
        """Return list of column names

        If no column names were set then this will be an empty list.
        """
        return self.__header

    def lookup(self,key,value):
        """Return lines where the key matches the specified value
        """
        result = []
        for line in self.__data:
            if line[key] == value:
                result.append(line)
        return result

    def indexByLineNumber(self,n):
        """Return index of a data line given the file line number

        Given the line number n for a line in the original file,
        returns the index required to access the data for that
        line in the TabFile object.

        If no matching line is found then raises an IndexError.
        """
        for idx in range(len(self.__data)):
            if self.__data[idx].lineno() == n:
                return idx
        raise IndexError,"No line number %d" % n

    def insert(self,i):
        """Create and insert a new data line at a specified index
 
        Creates a new (empty) TabDataLine and inserts it into the
        list of lines at the specified index position 'i' (nb NOT
        a line number).

        Returns the new TabDataLine which can then be populated
        by the calling subprogram.
        """
        data_line = TabDataLine(column_names=self.header())
        self.__data.insert(i,data_line)
        return data_line

    def write(self,filen):
        """Write the TabFile data to an output file
        """
        fp = open(filen,'w')
        for data in self.__data:
            fp.write("%s\n" % data)
        fp.close()

    def __getitem__(self,key):
        return self.__data[key]

    def __delitem__(self,key):
        del(self.__data[key])

    def __len__(self):
        return len(self.__data)

class TabDataLine:
    """Class to store a line of data from a tab-delimited file

    Values can be accessed by integer index or by column names (if
    set), e.g.

        line = TabDataLine("1\t2\t3",('first','second','third'))

    allows the 2nd column of data to accessed either via line[1] or
    line['second'].

    Values can also be changed, e.g.

        line['second'] = new_value

    Subsets of data can be created using the 'subset' method.

    Line numbers can also be set by the creating subprogram, and
    queried via the 'lineno' method.
    """
    def __init__(self,line=None,column_names=None,lineno=None):
        """Create a new TabFileLine object

        Arguments:
          line: (optional) Tab-delimited line with data values
          column_names: (optional) tuple or list of column names
            to assign to each value.
          lineno: (optional) Line number
        """
        # Data
        self.data = []
        if line is not None:
            self.data = line.strip().split('\t')
        # Column names
        self.names = []
        if column_names:
            for name in column_names:
                self.names.append(name)
        while len(self.data) < len(column_names):
            self.data.append('')
        # Line number
        self.__lineno = lineno

    def __getitem__(self,key):
        try:
            return self.data[int(key)]
        except ValueError:
            # See if key is a column name
            try:
                i = self.names.index(key)
            except ValueError:
                # Not a column name
                raise KeyError, "column '%s' not found" % key
            # Return the data
            return self.data[i]

    def __setitem__(self,key,value):
        try:
            self.data[int(key)] = value
        except ValueError:
            # Assume key is a column name
            try:
                i = self.names.index(key)
            except ValueError:
                # Not a column name
                raise KeyError, "column '%s' not found" % key
            # Assign the data
            self.data[i] = value

    def __len__(self):
        return len(self.data)

    def append(self,*values):
        """Append values to the data line

        Should only be used when creating new data lines.
        """
        for value in values:
            self.data.append(value)

    def subset(self,*keys):
        """Return a subset of data items

        This method creates a new TabFileLine instance with a
        subset of data specified by the 'keys' argument, e.g.

            new_line = line.subset(2,1)

        returns an instance with only the 2nd and 3rd data values
        in reverse order.
        
        Arguments:
          keys: one or more keys specifying columns to include in
            the subset. Keys can be column indices, column names,
            or a mixture, and the same column can be referenced
            multiple times.
        """
        # Set column names for subset
        subset_column_names = []
        for key in keys:
            name = None
            try:
                name = self.names[key]
            except TypeError:
                # key is not an integer
                if key in self.names:
                    name = key
            if not name:
                # No matching column for key
                raise KeyError, "key '%s' not found" % key
            subset_column_names.append(name)
        # Construct subset
        subset = TabDataLine(column_names=subset_column_names)
        for key in keys:
            subset.append(self[key])
        return subset

    def lineno(self):
        """Return the line number associated with the line

        NB The line number is set by the class or function which
        created the TabDataLine object, it is not guaranteed by
        the TabDataLine class itself.
        """
        return self.__lineno

    def __repr__(self):
        return '\t'.join(self.data)
