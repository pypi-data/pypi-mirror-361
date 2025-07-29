import os
import re
import shutil
import cv2

def to_low_quality_img(input_image_path, output_dir):
    original_image = cv2.imread(input_image_path)
    filename = os.path.split(input_image_path)[-1].rsplit('.', 1)[0]
    sourcepath = os.path.split(input_image_path)[0]
    sourcef = os.path.join(os.path.split(input_image_path)[0], f'{filename}.xml')
    with open(sourcef, encoding='utf8') as f:
        scode = f.read()
    jpeg_quality = 20
    while jpeg_quality<100:
        tfilename = f'lowq_{jpeg_quality}_{filename}.jpg'
        output_image_path = os.path.join(output_dir, tfilename)
        txmlfilename = f'lowq_{jpeg_quality}_{filename}.xml'
        sxmlf = os.path.join(sourcepath, txmlfilename)
        txmlf = os.path.join(output_dir, txmlfilename)
        tcode = scode
        tcode = re.sub(r'<filename>([^<>]*?)</filename>', lambda k:f'<filename>{tfilename}</filename>', tcode)
        tcode = re.sub(r'<path>([^<>]*?)</path>', lambda k:f'<path>{tfilename}</path>', tcode)
        with open(txmlf, 'w', encoding='utf8') as f:
            f.write(tcode)
        cv2.imwrite(output_image_path, original_image, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
        jpeg_quality += 20

def fix_width_height(sxmlf, sf):
    sfile_np = cv2.imread(sf)
    height, width, _ = sfile_np.shape
    with open(sxmlf, encoding='utf8') as f:
        scode = f.read()
    scode = re.sub(r'<width>([^<>]*?)</width>', lambda k:f'<width>{width}</width>', scode)
    scode = re.sub(r'<height>([^<>]*?)</height>', lambda k:f'<height>{height}</height>', scode)
    with open(sxmlf, 'w', encoding='utf8') as f:
        f.write(scode)

sr = './src_data'
tr = './data'
os.makedirs(tr, exist_ok=True)
cindex = 0
for i in os.listdir(sr):
    sf = os.path.join(sr, i)
    if i.endswith('.jpg') or i.endswith('.jpeg') or i.endswith('.png') or i.endswith('.gif'):
        cindex += 1
        print(cindex, i)
        if i.startswith('9136e'):
            break
        sxmlf = os.path.join(sr, i.rsplit('.', 1)[0]+'.xml')
        txmlf = os.path.join(tr, i.rsplit('.', 1)[0]+'.xml')
        fix_width_height(sxmlf, sf)
        tf = os.path.join(tr, i)
        shutil.copy(sxmlf, txmlf)
        shutil.copy(sf, tf)
        if os.path.exists(sxmlf):
            to_low_quality_img(sf, tr)