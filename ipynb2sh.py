#!/usr/bin/env python3
import os
import sys
import json
import datetime
import textwrap
from pathlib import Path


def ipynb2sh(filename):
    postfix = 'exit 0\n'
    paragraph = '\n\n'
    prefix_str = '''
        #!/bin/bash

        BASENAME="$(basename ${0%.sh})"

        DIR_LOG="${HOME}/tmp/logs-${PRODUCT_NAME}-${BASENAME}"
        if [ ! -d ${DIR_LOG} ];then
          mkdir -p ${DIR_LOG}
        fi

        FILE_LOG="${DIR_LOG}/$(date +%Y-%m-%d)-${PRODUCT_NAME}-${BASENAME}.log" &&\\
        echo ${FILE_LOG}
        
        if [ "$(basename ${0})" != "bash" ];then 
          exec &> ${FILE_LOG}
          set -vx
        fi
    '''

    prefix = textwrap.dedent(prefix_str).strip()

    with open(f'{filename}.ipynb') as f:
        data = json.load(f)
    
    language = data.get('metadata').get('kernelspec').get('language')

    if language != 'bash':
        print(f'ERROR: {filename}.ipynb kernelspec language is not bash')

    cells = data['cells']
    sources = [cell['source'] 
            for cell in cells 
            if cell['cell_type'] == 'code']

    with open(f'{filename}.sh', 'w') as f:
        f.writelines(prefix)
        f.write(paragraph)
        for source in sources:
            f.writelines(source)
            f.write(paragraph)
        f.write(postfix)
    os.chmod(f'{filename}.sh', 0o755)


if __name__ == "__main__":

    convert_path = Path('.')
    if len(sys.argv) == 2:
        convert_path = Path(sys.argv[1])

    ipynbs = list(convert_path.glob("*.ipynb"))
    for ipynb in ipynbs:
        filename, ext = os.path.splitext(ipynb)
        ipynb2sh(filename)

    sys.exit(0)
