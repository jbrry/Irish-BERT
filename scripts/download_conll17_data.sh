#!/usr/bin/env bash

# download handle for CoNLL 2017 data for Irish
UD_CC="https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-1989/Irish-annotated-conll17.tar?sequence=23&isAllowed=y"
ARCHIVE="ud_2017_data.tgz"

DATASET_DIR="data/ga/conll17"
mkdir -p $DATASET_DIR

echo $'\n'"Downloading data from CoNLL 2017..."$'\n'
curl ${UD_CC} -o ${ARCHIVE}
tar -xf ${ARCHIVE} -C ${DATASET_DIR}
mv ${ARCHIVE} $DATASET_DIR

# download handle for UDPipe v2.5 Irish model
UDPIPE_ga="https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/irish-idt-ud-2.5-191206.udpipe?sequence=39&isAllowed=y"
UDPIPE_MODEL_DIR=udpipe_models
mkdir -p ${UDPIPE_MODEL_DIR}

echo $'\n'"Downloading UDPipe model for ga..."$'\n'
curl ${UDPIPE_ga} -o ga.udpipe
mv ga.udpipe ${UDPIPE_MODEL_DIR}

# convert files to raw text
data=$(find "$DATASET_DIR/Irish" -type f -name "*.xz" )
echo $'\n'"found the following files:"$'\n'
echo "$data"

# downloaded files are in x-zip format
for compressed in ${data}; do
  echo "processing: ${compressed}"
	
  # decompress file
  unxz ${compressed}
	
  base="$(basename -- ${compressed})"
  # remove file-extension
  filestring="$(echo $base | cut -f1 -d ".")"
  conllu_file=${DATASET_DIR}/Irish/${filestring}.conllu
  
  # convert conllu to text
  perl scripts/conllu_to_text.pl --language=ga_idt < ${conllu_file}  > ${DATASET_DIR}/${filestring}.txt
	
  # use udpipe model to tokenize/segment the raw text:
  #udpipe --tokenize --output horizontal ${UDPIPE_MODEL_DIR}/ga.udpipe ${DATASET_DIR}/${filestring}.txt > ${DATASET_DIR}/${filestring}_tokenised.txt

done
