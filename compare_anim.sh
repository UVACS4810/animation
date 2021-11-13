# Usage: oneDiff refrence.png student.png diffimgname.png
# Result: diffimgname.png
function oneDiff {
    compare -fuzz 2% "$1" "$2" ae.png
    if [ ! -e ae.png ]; then return 1; fi
    composite "$1" "$2" -compose difference diff.png
    convert diff.png -level 0%,8% diff2.png
    convert +append "$2" "$1" ae.png diff.png diff2.png "$3"
    rm ae.png diff.png diff2.png
}

# Usage: extractFrames animated.png basename
# Result: basename-000.png through end of animation
function extractFrames {
    ffmpeg -i "$1" "$2"-%03d.png
    for f in "$2"-???.png
    do
        num=${f##*-}; num=${num%.png}
        nf=$(printf %03d $((10#$num-1)))
        mv $f ${f%-*}-$nf.png
    done
}

# Usage: makeDiffAnimation path/to/reference.png dir/of/yours/
# Result: ./diff-basename-000.png through end of animation
function makeDiffAnimation {
    base=.
    if [ "$#" -gt 1 ]; then base="$2"; fi
    name=$(basename "$1" .png)
    
    extractFrames "$1" tmp
    for f in tmp-???.png
    do
        oneDiff $f "$base/$name-${f##*-}" "diff-$name-${f##*-}"
    done
    rm tmp-???.png
}

makeDiffAnimation "$@"