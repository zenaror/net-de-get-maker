dbuser ?=
dbpass ?=

RGBDS ?=
RGBASM  ?= $(RGBDS)rgbasm
RGBLINK ?= $(RGBDS)rgblink

all: 
	# TODO: way to declare which languages your game supports
	$(RGBASM) main.asm -o main.o -D _LANG_E
	mkdir -p bin
	$(RGBLINK) main.o -o bin/game.bin -n bin/game.sym
	python3 ./fix.py game.bin
	
push:
	python3 ./push.py game.bin "$(dbuser)" "$(dbpass)"
	
andpush: all push
.PHONY: pad-test c-pad c-reaction
pad-test c-pad c-reaction:
	./tools/build-examples.sh $@
