TimSav G-Code Output for Inkscape
===========================================

This is an Inkscape extension that allows you to save your Inkscape drawings as
G-Code files suitable for needle cutting with the [ERC TimSav](https://www.thingiverse.com/thing:3951161).

Disclaimer
===========================================
I am not responsible for any damanage or harm that may have caused by this extension, do so at your own risk

* Modified by: [Brian Ho](http://github.com/kawateihikaru)
* Original Author: [Marty McGuire](http://github.com/martymcguire)

Credits
=======

* Brian Ho modified this extension to generate compatable g-code for TimSav (Robotini GRBL)  
* Marty McGuire pulled this all together into an Inkscape extension.
* [Inkscape](http://www.inkscape.org/) is an awesome open source vector graphics app.
* [Scribbles](https://github.com/makerbot/Makerbot/tree/master/Unicorn/Scribbles%20Scripts) is the original DXF-to-Unicorn Python script.
* [The Egg-Bot Driver for Inkscape](http://code.google.com/p/eggbotcode/) provided inspiration and good examples for working with Inkscape's extensions API.

Install
=======

Copy the contents of `src/` to your Inkscape `extensions/` folder.

Typical locations include:

* OS X - `/Applications/Inkscape.app/Contents/Resources/extensions`
* Linux - `/usr/share/inkscape/extensions`
* Windows - `C:\Program Files\Inkscape\share\extensions`

Usage
=====

* Create a document with the size of your foamboard (eg. 20x30)
* IMPORTANT! make sure your document unit is in px (Known issue, will try to fix)
* Create some objects and convert all to paths:
	* Select all text objects.
	* Choose **Path | Object to Path**.
* Save as G-Code:
	* **File | Save a Copy**.
	* Select **TimSav G-Code (\*.gcode)**.
	* Save your file.

TODOs
=====
* Fix units in document
* Rename `*PolyLine` stuff to `*Path` to be less misleading.
* Formalize "home" to be a reasonable place to change pages/pens.
* Parameterize smoothness for curve approximation.
* Use native curve G-Codes instead of converting to paths?
* Include example templates?
