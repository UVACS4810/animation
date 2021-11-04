#!/bin/zsh
shopt -s nullglob
for file in test/test_files/*.txt
do
    make run file=$file
    filename="$(basename "${file%.*}")"
    make comp file=$filename.png
    rm $filename.png
     
done
shopt -u nullglob
