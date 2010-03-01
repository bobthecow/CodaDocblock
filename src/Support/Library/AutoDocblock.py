from Docblock import Docblock
from PHPDocblock import PHPDocblock
#from PyDocblock import PyDocblock

class AutoDocblock(Docblock):
    """
    Automatic language detection Docblock generator.
    
    Way beta.
    """
    
    classes = (PHPDocblock,)
    
    def doc(self, text):
        
        for c in self.classes:
           d = c()
           d.setLineEnding(self.opt['line_ending'])
           docblock = d.doc(text)
           
           if docblock: return docblock
           
        return None