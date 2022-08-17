import pandas as pd
import cv2
from urllib.request import urlopen
import numpy as np
from skimage import io
from pyzbar.pyzbar import decode


occs = pd.read_csv('dwca-o_vascular-v1.1934/occurrence.txt', sep='\t', dtype=str, quoting=3, usecols=['id', 'materialSampleID'])
occs['materialSampleID'] = occs['materialSampleID'].str.replace(';', ',')
occs['uuids-count'] = occs['materialSampleID'].str.count(',') + 1

# Number of records with uuids prefixed with purl
occs_prefixed = occs[occs['materialSampleID'].str.startswith('http://purl.org/nhmuio/id', na=False)]
print(len(occs_prefixed))

# Exclude prefixed ?
# occs = occs[~occs['materialSampleID'].str.startswith('http://purl.org/nhmuio/id', na=False)]

media = pd.read_csv('dwca-o_vascular-v1.1934/multimedia.txt', sep='\t', dtype=str, quoting=3, usecols=['id', 'identifier'])
media_pivot = media.value_counts('id').reset_index(name='images-count')

df = pd.merge(media_pivot, occs, on='id', how='outer')

# The correct number of uuids to images in the media table
df.loc[df['uuids-count'] == df['images-count']]
# count: 312679
# https://www.gbif.org/occurrence/1702008704, https://www.gbif.org/occurrence/1701629280

# More images than uuids
df.loc[df['images-count'] > df['uuids-count']]
# count: 20726
# 2012530 = https://www.gbif.org/occurrence/1702559660, 338129 = https://www.gbif.org/occurrence/1702226760

# More uuids than images
df.loc[df['uuids-count'] > df['images-count']]
# count: 107
# 860476 = https://www.gbif.org/occurrence/2867585068, 2124989 = https://www.gbif.org/occurrence/1702063730

# No images or materialSample uuids
df.loc[df['uuids-count'].isna() & df['images-count'].isna()]
# count: 54284
# 157704 = https://www.gbif.org/occurrence/1702008704, 291226 = https://www.gbif.org/occurrence/1701629280

# No images but supposedly has uuids/qr codes?
df.loc[df['uuids-count'].notna() & df['images-count'].isna()]
# count: 133596 yikes, what is going on here??
# 880198 = https://www.gbif.org/occurrence/2867538038, 941426 = https://www.gbif.org/occurrence/3127393143

# No uuids/qr codes but has images
df.loc[df['uuids-count'].isna() & df['images-count'].notna()]
# count: 458070
# 379529 = https://www.gbif.org/occurrence/1702244341, 753094 = https://www.gbif.org/occurrence/1702413191

# Read images in media table and record QR codes
def getQRs(row):
    print(row['identifier'])
    import pdb; pdb.set_trace()
    image = io.imread(row['identifier'])
    barcodes = decode(image)
    return '|'.join([x.data.decode('utf-8')  for x in barcodes])

media['decodedQRs'] = test.apply(getQRs, axis=1)
media.to_pickle('media-with-qrs.pkl')


#test = df.loc[df['uuids-count'] == df['images-count']].reset_index(drop=True)[0:5]
#test['decodedQRs'] = test.apply(getQRs, axis=1)
#test = media[300254:300259]
#test['decodedQRs'] = test.apply(getQRs, axis=1)
#test.groupby('id')['decodedQRs'].apply(lambda x: ','.join(x)).reset_index(drop=True)
# temp = media.loc[media['id'] == 'urn:catalog:O:V:2236056', 'identifier'].item()
# image = io.imread(temp)
# barcodes = decode(image)

import pdb; pdb.set_trace()
# with urlopen(media.iloc[0]['identifier']) as conn:
#     arr = np.asarray(bytearray(conn.read()), dtype=np.uint8)
#     img = cv2.imdecode(arr, -1)
#     value, points, straight_qrcode = detect.detectAndDecode(img)

# detect = cv2.QRCodeDetector()


# Records with more materialSample uuids than images - SQL
# select v.uuid, vm.catalog_number, COUNT(vm.catalog_number)
# FROM digir_musit.V_DC_O_VASCULAR_MEDIA vm
# LEFT JOIN digir_musit.V_DC_O_VASCULAR v ON v.catalognumber = vm.catalog_number
# GROUP BY vm.catalog_number, v.uuid
# HAVING (
#   (LENGTH(v.uuid) - LENGTH(replace(v.uuid, ',', '')) + 1) > COUNT(vm.catalog_number) AND
#   v.uuid NOT LIKE 'http://purl.org/nhmuio/id%'
# );
