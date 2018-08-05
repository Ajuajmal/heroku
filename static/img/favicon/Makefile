PNG_SIZES=57 72 76 114 120 128 144 152 180 192 196
PNG_FAVICONS=$(patsubst %,favicon-%.png,$(PNG_SIZES))
ICO_SIZES=16 24 32 48 64
ICO_FAVICONS=$(patsubst %,favicon-%.png,$(ICO_SIZES))

.PHONY: all clean

all: favicon.ico $(PNG_FAVICONS)

clean:
	rm -f $(PNG_FAVICONS) $(ICO_FAVICONS) favicon.ico


favicon.ico: $(ICO_FAVICONS)
	icotool -c -o $@ $^

favicon-%.png: favicon.svg
	set -e; \
	size=$$(echo $@ | cut -d- -f 2 | cut -d. -f 1); \
	rsvg-convert -o $@ -w $$size -h $$size $^
	optipng -o7 $@
	advpng -z4 $@
