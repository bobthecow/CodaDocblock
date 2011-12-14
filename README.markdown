Manipulate Coda
===============

A text manipulation plug-in suite for Panic's [Coda][1].

Manipulate Coda is a series of text-manipulation plug-ins for [Panic's Coda][1].
They're built using the [Coda Plugin Skeleton][2], an open source framework for
writing Cocoa plug-ins for Coda using Python. They are inspired by Ian Beck's
amazing [TEA for Coda][3] plugin.

Because Manipulate Coda is a Cocoa (native) Coda plug-in, it's crazy fast. For
example, the "Move Lines" commands are instant for any file that's not hampered
by Coda's (sometimes slothlike) syntax highlighting. It doesn't bat an eye at
moving or duplicating 10k lines of code.

Because Manipulate Coda is written in Python, it can leverage the strengths of
all sorts of interesting Python libraries. Manipulate Markup can change text
from Textile or Markdown or reStructuredText to HTML and back. It's pretty hot.

   [1]: http://panic.com/coda/
   [2]: http://github.com/bobthecow/coda-plugin
   [3]: http://onecrayon.com/tea/coda/
