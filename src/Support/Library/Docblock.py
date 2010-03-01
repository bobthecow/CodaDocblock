'''Docblock generator class'''

import re

# These imports are actually done inside the Docblock class to fix a circular reference.
#from AutoDocblock import AutoDocblock
#from PHPDocblock import PHPDocblock
#from PyDocblock import PyDocblock
#from JSDocblock import JSDocblock


class Docblock(object):
    """
    Generic Docblock generator class
    """
    
    opt = {
        'line_ending': '\n',
    }
    
    @staticmethod
    def get(ext):
        """
        Get a Docblock instance for the requested file extension.
        
        Using extensions is ghetto, but it's the best we can do until Panic gives us access to the
        currently selected syntax mode.
        
        Hmmm... Mebbe I'll poke around and see if I can figure that out from the context somehow.
        """
        
        from AutoDocblock import AutoDocblock
        from PHPDocblock import PHPDocblock
        # from PyDocblock import PyDocblock
        # from JSDocblock import JSDocblock
        
        if ext: ext = ext.lower()
        
        if ext in ('php', 'phtml', 'php3', 'php4', 'php5', 'ph3', 'ph4', 'ph5', 'phps', 'module', 'inc', 'install',):
            return PHPDocblock()
#         elif ext in ('python', 'py',):
#             return PyDocblock()
#         elif ext in ('javascript', 'js',):
#             return JSDocblock()
#         elif ext in ('smarty', 'tpl',):
#             return SmartyDocblock()
        else:
            # at this point we'll try just about anything...
            return AutoDocblock()
    
    def setLineEnding(self, line_ending):
        self.opt['line_ending'] = line_ending
    
    def doc(self, sig):
        """
        Document a class, function or variable signature.
        """
        
        # store this away for later, can be used by formatter functions to guess values, etc.
        self.signature = sig
        
        # we'll keep a dict of the most recent matches, can be used as a lookaround of sorts
        # (i.e. the access callback can look at self.matches[name] to see if the name starts
        # with the "_" character.
        self.matches = {}
        
        docblock   = ''
        whitespace = ''
        
        for k, s in self.opt['signatures'].items():
            result = re.match(s['pattern'], sig)
            
            if not result:
                continue
            
            # we have a match, let's document!
            
            # remove whitespace at the front of the template, since it's
            # not actually necessary for the docblock...
            docblock = re.sub('\n[ \t]*', '\n', s['template'].strip())
            
            for name, match in result.groupdict().items():
                self.matches[name] = match
            
            for name, match in result.groupdict().items():
                if name == 'whitespace':
                    whitespace = match
                    continue
                
                if name in s['callbacks'].keys():
                    match = self[s['callbacks'][name]](match)
                
                if not match:
                    continue
                
                docblock = docblock.replace("%" + (name) + "%", match)
            
            # remove all the leftovers
            docblock = re.sub('%[a-zA-Z]+%\n?', '', docblock).strip()
            
            # return pretty docblock
            return self.formatDocblock(docblock, whitespace)
    
    def formatDocblock(self, docblock, whitespace):
        # clean up white space and line endings
        lines = []
        if self.opt['prefix']:
            lines.append(self.opt['prefix'])
        lines += [self.opt['infix'] + s for s in docblock.split('\n')]
        # lines.extend(map(lambda s: self.opt['infix'] + s, docblock.split('\n')))
        if self.opt['suffix']:
            lines.append(self.opt['suffix'])
        
        return self.opt['line_ending'].join([whitespace + s for s in lines]) + self.opt['line_ending']
        # return self.opt['line_ending'].join(map(lambda s: whitespace + s, lines))
    
    def is_float(self, s):
        try:
            float(s)
            return True
        except:
            return False
    
    def keywordCallback(self, s):
        """
        Generic Docblock keyword callback.
        """
        if not s: return
        
        s = s.strip()
        if s != "":
            return "%s%s" % (self.opt['command'], s)
    
    def paramsCallback(self, s):
        """
        Callback for formatting individual @param documentation lines.
        """
        
        if not s: return
        
        ret = []
        
        for p in s.split(','):
            chunks = p.split('=')
            
            param_name = chunks[0].strip()
            
            if not param_name: return
            
            param_type = 'mixed'
            default = None
            
            if len(chunks) > 1:
                default = chunks[1].strip()
                param_type = self.guessType(default)
            
            if default is not None:
                ret.append("%sparam %s %s (default: %s)" % (self.opt['command'], param_type, param_name, default))
            else:
                ret.append("%sparam %s %s" % (self.opt['command'], param_type, param_name))
        
        return self.opt['line_ending'].join(ret)
    
    def __getitem__(self, item):
        return self.__getattribute__(item)
    
    def __setitem__(self, item, value):
        return self.__setattr__(item, value)
