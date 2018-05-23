#!/bin/sh
yui-compressor main.css >  main.min.css
cat normalize.min.css main.min.css > minified.css
rm -f main.min.css
