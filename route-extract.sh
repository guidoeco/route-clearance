#!/bin/sh

TABULA=1.0.3

TABULADIR=..
PATH=${PATH}:${TABULADIR}
TABULAFILE=tabula-${TABULA}-jar-with-dependencies.jar

FILEPATH=$1
FILEDIR=$(dirname $1)

if [ ! "$(ls -A pdf)" ]; then
    STARTSEQ=$(pdfgrep -n 'ROUTE CLEARANCE' download/*.pdf | sed 's/:.*$//' | sort -u | head -1)
    pdfseparate -f ${STARTSEQ} download/*.pdf pdf/pg_%04d.pdf
fi

for FILEPATH in pdf/*.pdf
do
    FILESTUB=$(basename $FILEPATH | sed 's/\.pdf$//')
    if [ ! -f work/${FILESTUB}.png ]; then
        convert ${FILEPATH} -flatten work/${FILESTUB}.png 2> /dev/null
    fi
    N=1
    if [ ! -f ${FILESTUB}_${N}.tsv ]; then
        set -- lattice stream lattice
        for P in $(../rectangles3.py work/${FILESTUB}.png)
        do
            XFLAG=$1
            java -Dfile.encoding=utf-8 -Xms256M -Xmx2048M -jar ${TABULADIR}/${TABULAFILE} --area ${P} --${XFLAG} -f TSV -o ${FILESTUB}_${N}.tsv pdf/${FILESTUB}.pdf
            fromdos ${FILESTUB}_${N}.tsv
            N=$((N+1))
            shift
        done
    fi
    find . -size -4c -exec rm {} \;
done
