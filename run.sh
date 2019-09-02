#!/bin/bash

IFS=$'\012'

for FILE in $(ls download/*Sectional\ Appendix*.pdf | sed 's/^download\///')
do
    echo "${FILE}	$(echo ${FILE} | sed 's/ Sectional Appendix .* 2019.pdf//; s/[,)(]//g; s/ /-/g')"
done | jq -Rsc 'split("\n")[0:-1] | map([split("\t")][] | {(.[1]): (.[0])})' > section-list.json

TABULA=1.0.3

if [ ! -f tabula-${TABULA}-jar-with-dependencies.jar ]; then
    echo downloading tabula-${TABULA}-jar-with-dependencies.jar
    wget https://github.com/tabulapdf/tabula-java/releases/download/v${TABULA}/tabula-${TABULA}-jar-with-dependencies.jar
fi

TABULAFILE=tabula-${TABULA}-jar-with-dependencies.jar

for i in report output
do
    if [ ! -d ${i} ]; then
        mkdir -p ${i}
    fi
done

for i in $(jq -c '.[]' section-list.json)
do
    ROUTE=$(echo ${i} | jq -r 'keys[]')
    for j in download pdf work
    do
        if [ ! -d ${ROUTE}/${j} ]; then
            mkdir -p ${ROUTE}/${j}
        fi
    done

    FILE=$(echo ${i} | jq -r 'values[]')
    if [ ! -f "${ROUTE}/download/${FILE}" ]; then
        ln "download/${FILE}" "${ROUTE}/download/${FILE}"
    fi

    (cd ${ROUTE}; ../route-extract.sh ${ROUTE})
done

sed -i 's/^""\t\t\t/""\t-\t-\t/' London-North-Western-South/pg_0544_3.tsv

./generate-report2.py

for i in $(jq -c '.[]' section-list.json)
do
    ROUTE=$(echo ${i} | jq -r 'keys[]')
    echo ${ROUTE}
    cat report/${ROUTE}_????.tsv > output/${ROUTE}.tsv
done
