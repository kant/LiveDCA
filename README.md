# LiveDCA
Python Midi Remote Script that implements DCA processing in Ableton Live

The masters and slaves parameters are defined by the name of the tracks, command-line style.

In Live version 9.2 and under, the changes are updated by the native update_display() method called every 100ms or so. It can therefore be uneven

From Live version 9.5+ the new Live.Base.Timer method is used and thus DCA changes are much smoother.



Installation
------------
* Checkout the master branch
* Rename LiveDCA-master to LiveDCA
* Move the folder to /Applications/Live xxxx/Contents/App-Resources/MIDI Remote Scripts
* In Live preferences / Midi click a drop down list under Control Surface and select LiveDCA




Syntax
------
Names of tracks are used to define the parameters : a track can be master of only one DCA group and can be slave of as many as you want.
Names are divided by slashes. The part before the first / is the key : the name of the DCA which the track is master of and the parts after are the names of the DCAs that command the track.
For example if a track is named "Piano / Key /All" , it is master of the DCA named Piano, and slave of the DCA "Key" and "All". If a track is named "Key/..." any changes made on that track is passed on "Piano".

Note that the spaces at the beginning and the end are irrelevant.

Also note that the changes are relative. They are for the moment linear and not yet exponantial, therefore the relative levels may not be always accurate...


Options
-------
For each DCA and each track you can choose which parameter you want to link. After the key part in the track name, you can specify options after - to set up parameters and link direction.

* -v means volume is linked
* -p means panning is linked
* -m means mute is linked
* -a means arm is linked
* -S means solo is linked



* -s means sends are linked
* -sA to -sL means individual send A to L is linked



* --v means volume is excluded (not linked) 
* --p means panning is excluded
* and so on



* -iv means volume is linked and inverted : a positive change of the master will result as a negative change in the slave
* same thing for -ip, -im, -ia, -iS, -is, -isA to -isL


I've included aliases : -l or -L mean -p  and -r or -R mean -ip


For example if you want to link volumes, mute and inverted panning but not sends, nor arm or solo, the slaves should be named as followed : "track_name/master_key -ip --s --a --S"


@master syntax
--------------

If you want to link few parameters there is an alternate syntax : 

after the initial slash if you type @master_name, then the track is slave of the DCA master but no parameter is linked until you have manually added them.

For example if you want only the volume of a track to be controlled by the master, you can name the slave track "Slave_name /@master_key -v"
