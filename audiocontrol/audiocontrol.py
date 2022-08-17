import pulsectl
"""
Commands:
listsources
    returns: index:'name','description'|index:'name','description'|...
listsinks
    returns: index:'name','description'|index:'name','description'|...
getdefaultsource
getdefaultsink
getvolume           sink/source, id
setvolume           sink/source, id, volume
incvolume           sink/source, id, value
decvolume           sink/source, id, value
getmute             sink/source, id
setmute             sink/source, id, 1/0
togglemute          sink/source, id

"""