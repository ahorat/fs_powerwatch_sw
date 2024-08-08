import tkinter as tk
import tkinter.font as tkf

# --- class ---

class FormatLabel(tk.Label):

    def __init__(self, master=None, cnf={}, **kw):

        # default values
        self._format = '{}'  
        self._textvariable = None

        # get new format and remove it from `kw` so later `super().__init__` doesn't use them (it would get error message)
        if 'format' in kw:
            self._format = kw['format']
            del kw['format']
            
        # Check if limits is set and remove it
        if 'limits' in kw:
            if(kw['limits'][0] > 0):
                self._limits = kw['limits']
            del kw['limits'] 
        
        # get `textvariable` to assign own function which set formatted text in Label when variable change value
        if 'textvariable' in kw:
            self._textvariable = kw['textvariable']
            self._textvariable.trace('w', self._update_text)
            del kw['textvariable']

        # run `Label.__init__` without `format` and `textvariable`
        super().__init__(master, cnf={}, **kw)

        # update text after running `Label.__init__`
        if self._textvariable:
            #self._update_text(None, None, None)
            self._update_text(self._textvariable, '', 'w')
        

    def _update_text(self, a, b, c):
        """update text in label when variable change value"""
        value=self._textvariable.get()
        self["text"] = self._format.format(self._textvariable.get())
        
        if hasattr(self, '_limits'):
            if value < self._limits[0]:
                self["background"] = f'#{0:02x}{255:02x}{0:02x}'
            elif value < self._limits[1]:
                g = int(158-158*(value-self._limits[0])/(self._limits[1] - self._limits[0]))
                self["background"] = f'#{255:02x}{g:02x}{0:02x}'
            else:
                self["background"] = f'#{255:02x}{0:02x}{0:02x}'
                
        
