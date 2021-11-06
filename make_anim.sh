#!/bin/zsh
TEST_FILE=$1
if [ ! -f "$TEST_FILE"]; then
    echo "$TEST_FILE does not exist."
fi
echo -n "Whate Frame Rate do you want?: "
read FRAME
make run file=$TEST_FILE
filename="$(basename "${TEST_FILE%.*}")"
# make directory
if [ ! -d "test/created_files/$filename"]; then
    echo "making directory"
    mkdir test/created_files/$filename
fi
mkdir test/created_files/$filename
mv $filename* test/created_files/$filename
ffmpeg -r $FRAME -i test/created_files/$filename/$filename-%03d.png -f apng -plays 0 test/created_files/$filename.png
rm test/created_files/$filename/$filename-*
rmdir test/created_files/$filename