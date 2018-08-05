dc18-schedule-qr-code.png: dc18-schedule-qr-code.json
	gzip -9 < $^ | qr --optimize=0 > $@
	optipng -o7 $@
	advpng -z4 $@
