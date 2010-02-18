from Docblock import Docblock

class PHPDocblock(Docblock):
    """
    PHP Docblock generator
    """
    
    opt = {
        'line_ending': '\n',
        
        'prefix':  '/**',
        'infix':   ' * ',
        'suffix':  ' */',
        'command': '@',
        
        # docblock formatting definitions for other languages besides PHP...
        # keep these around for laters.
#         'prefix':  '/*!',
#         'infix':   ' * ',
#         'suffix':  ' */',
#         
#         'prefix':  '///',
#         'infix':   '///',
#         'suffix':  '///',
#         
#         'prefix':  '//!',
#         'infix':   '//!',
#         'suffix':  '//!',
#         
#         'command': '\\',
        
        'signatures': {
            'function': {
                'pattern': '^(?P<whitespace>\s*)(?:(?:(?P<abstract>abstract)|(?P<final>final)|(?P<static>static)|(?P<access>private|public|protected))\s+)*function\s*&?(?P<name>[-a-zA-Z0-9_]+)\s*\((?P<params>.*)\)\s*(?:{.*}?|;)?\s*$',
                'template':
                    """
                    %name% function.
                    
                    %access%
                    %abstract%
                    %static%
                    %final%
                    %params%
                    @return void
                    """,
                'callbacks': {
                    'access':   'accessCallback',
                    'abstract': 'keywordCallback',
                    'final':    'keywordCallback',
                    'static':   'keywordCallback',
                    'params':   'paramsCallback',
                }
            },
            
            'class': {
                'pattern': '^(?P<whitespace>\s*)(?:(?:(?:(?P<abstract>abstract)|(?P<final>final)|(?P<static>static))\s+)*)class\s+(?P<name>[-a-zA-Z0-9_]+)(?:\s+extends\s+(?P<extends>[-a-zA-Z0-9_]+))?(?:\s+implements\s+(?P<implements>[-a-zA-Z0-9_,\s]+))?',
                'template':
                    """
                    %name% class.
                    
                    %abstract%
                    %static%
                    %final%
                    %extends%
                    %implements%
                    """,
                'callbacks': {
                    'name':       'classNameCallback',
                    'abstract':   'keywordCallback',
                    'final':      'keywordCallback',
                    'static':     'keywordCallback',
                    'extends':    'extendsCallback',
                    'implements': 'implementsCallback',
                }
            },
            
            'interface': {
                'pattern': '^(?P<whitespace>\s*)interface\s+(?P<name>[-a-zA-Z0-9_]+)(?:\s+extends\s+(?P<extends>[-a-zA-Z0-9_]+))?',
                'template':
                     """
                     %name% interface.
                     
                     %extends%
                     """,
                'callbacks': {
                    'extends': 'extendsCallback',
                }
            },
            
            'member_variable': {
                'pattern': '(?P<whitespace>\s*)(?:(?:(?P<abstract>abstract)|(?P<static>static)|(?P<final>final)|(?P<access>private|public|protected))\s+)*(?:var\s+)?\$(?P<name>[-a-zA-Z0-9_]+)(?:\s*=\s*(?P<value>[^;]+);)?',
                'template':
                    """
                    %name%
                    
                    %value%
                    %access%
                    %abstract%
                    %static%
                    %final%
                    """,
                'callbacks': {
                    'abstract': 'keywordCallback',
                    'static':   'keywordCallback',
                    'final':    'keywordCallback',
                    'access':   'accessCallback',
                    'value':    'varValueCallback',
                }
            },
        }
    }
    
    def accessCallback(self, s):
        if not s:
            s = self.guessAccess()
        return "%saccess %s" % (self.opt['command'], s)
    
    def guessAccess(self, name = None):
        if not name:
            if not 'name' in self.matches:
                return "public"
            else:
                name = self.matches['name']
        
        if name.startswith('__'):
            # magic, not private...
            return "public"
        elif name.startswith('_T'):
            return "protected"
        elif name.startswith('_'):
            return "private"
        else:
            return "public"
    
    def classNameCallback(self, s):
        name = []
        for key in ('abstract', 'static', 'final'):
            if key in self.matches and self.matches[key]:
                name.append(key)
        
        if len(name):
            name[0] = name[0].capitalize()
        
        name.append(s)
        
        return " ".join(name)
    
    def extendsCallback(self, s):
        if not s: return
            
        s = s.strip()
        if s != "":
            return "%sextends %s" % (self.opt['command'], s)
    
    def implementsCallback(self, s):
        if not s: return
        
        ret = []
        for i in s.split(','):
            ret.append("%simplements %s" % (self.opt['command'], i.strip()))
        
        return self.opt['line_ending'].join(ret)
    
    def varValueCallback(self, s):
        if s: s = s.strip()
        
        if s:
            ret = "(default value: %s)%s%s" % (s, self.opt['line_ending'], self.opt['line_ending'])
        else:
            ret = ""
        
        return "%s%svar %s" % (ret, self.opt['command'], self.guessType(s))
    
    def guessType(self, s):
        """Guess the type of this variable or param based on the default value."""
        
        if not s:
            return 'mixed'
        elif '"' in s or "'" in s:
            return 'string'
        # elif s.find('"') > -1 or s.find("'") > -1:
        elif 'array(' in s:
        # elif s.find('array(') > -1:
            return 'array'
        elif 'true' in s or 'false' in s:
        # elif s.find('true') > -1 or s.find('false') > -1:
            return 'bool'
        elif s.isdigit():
            return 'int'
        elif self.is_float(s):
            return 'float'
        else:
            return 'mixed'


