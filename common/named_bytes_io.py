#=========================================================================================================
#This class serves for the alternative scenario described in alternative_main.py
#in which we only have available a stream of bytes and not a file to read from phsyical storage
#This is a common scenario when working with Blob Triggered Azure functions or when working with streams of data from APIs:
#They will only provide you with a stream of bytes and not a file to read from physical storage. These streams does not have a name attribute,
#so calls to the Whisper API will fail.
#To solve this, I created this NamedBytesIO class to be able to instantiate an object with a "name" attribute and of course, the stream of bytes:
#Similar to what you would get from a file stream, but without the need of a file to read from physical storage.
#=========================================================================================================



import io


#A class with the same interface as BytesIO but with an additional "name" attribute
class NamedBytesIO(io.BytesIO):
    def __init__(self, data=None, name=None):
        super().__init__(data if data is not None else b'')
        self.name = name

    #This method is used to create a NamedBytesIO object from a file stream and set the name attribute as required for exmaple by the Whisper API
    @classmethod
    def from_file_stream(cls, file_stream, new_name):
        # Return a new instance of NamedBytesIO with this data and the new name
        return cls(file_stream, new_name)
