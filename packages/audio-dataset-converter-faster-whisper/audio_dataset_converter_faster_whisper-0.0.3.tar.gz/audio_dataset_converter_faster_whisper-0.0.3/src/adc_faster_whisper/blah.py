from datetime import timedelta

td = timedelta(seconds=3.567)
print(td)
mm, ss = divmod(td.seconds, 60)
hh, mm = divmod(mm, 60)
s = "%d:%02d:%02d" % (hh, mm, ss)
if td.microseconds:
    s = s + ",%03d" % (td.microseconds // 1000)
print(s)
