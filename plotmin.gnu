#load './default.plt'
load './parula.pal'
#set palette model RGB rgbformulae 7,5,15
#set palette model XYZ rgbformulae 7,5,15

#set palette rgb 7,5,15 #"traditional pm3d\n(black-blue-red-yellow)"; splot g(x)

#set palette rgb 3,11,6 #"green-red-violet"; splot g(x)

#set palette rgb 23,28,3 #"ocean (green-blue-white)\ntry also other permutations"; splot g(x)

#set palette rgb 21,22,23 #"hot (black-red-yellow-white)"; splot g(x)

#set palette rgb 30,31,32 #"color printable on gray\n(black-blue-violet-yellow-white)"; splot g(x)
#set palette rgb 33,13,10 #"rainbow (blue-green-yellow-red)"; splot g(x)
#set palette rgb 34,35,36 #"AFM hot (black-red-yellow-white)"; splot g(x)
#set palette model HSV #
#set palette rgb 3,2,2 #"HSV model\n(red-yellow-green-cyan-blue-magenta-red)"; splot g(x)
#set pal gray #"gray palette"; splot g(x)

#set grid lc rgbcolor "#BBBBBB"

set term png size 3200, 2400 font "arial,28"

set autoscale z

unset key
unset xlabel
unset ylabel
unset xtics
unset ytics
unset title

set colorbox vertical user origin 0.9,0.05 size 0.04, 0.9
#unset cblabel
#unset cbrange
if ( globmin != 0.0 ) set cbrange[globmin:globmax]
#unset cbtics
if ( globmin != 0.0 ) set cbtics add(sprintf("%2.1f",globmin) globmin)
if ( globmax != 0.0 ) set cbtics add(sprintf("%2.1f",globmax) globmax)
#unset cbdtics
#unset cbmtics
set cblabel 'Signal power'

#set border 0
set lmargin 0
set rmargin at screen 0.875
set tmargin 0
set bmargin 0

set output outname.".png"
set datafile nofpe_trap

plot outname.".bin" binary array=@matorg rotation=-90d format='%float' with image
