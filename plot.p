set terminal png enhanced font 'Georgia,12' size 640,400
set output "%(name)s.png"
set grid y
set xlabel "Clients"
set ylabel "Messages per second, per client"
set decimal locale
set format y "%%'g"
set xrange [1:%(clients)s]
plot %(lines)s
