from peewee import *
import os.path
import json
import operator

########################### CREATE INDEX ############################
# Run CREATE INDEX requestURL_idx ON jabongpagedata ("requestURL"); #
#####################################################################

DIRNAME="/home/peeyush/deep-fashion/data/jabongImages/"
db = PostgresqlDatabase('fashion', user='fashion', password='fashion', host='localhost')
db.connect()

color_list = ['Black','Blue','Multi','White','Pink','Green','Red','Grey','NavyBlue','Yellow','OffWhite','Orange','Purple','Beige','Brown','Maroon']
fabric_list = ['cotton', 'polyester', 'georgette', 'blended', 'viscose', 'crepe', 'rayon', 'acrylic', 'chiffon', 'denim', 'net', 'wool', 'fleece', 'linen', 'knit', 'acrylic', 'jersey', 'modal', 'satin', 'nylon', 'leather']
style_list = ['Solid', 'Printed', 'Embroidered', 'Striped', 'Embellished', 'Checked', 'Graphic', 'Washed']

tags_list = ['Color', 'Fabric', 'Style']

running_index = {}
running_label_dict = {}
running_label_dict_count = {}
for tag in tags_list:
    running_index[tag] = 0
    running_label_dict[tag] = {}
    running_label_dict_count[tag] = {}

class JabongPageData(Model):
    id = PrimaryKeyField(primary_key=True)
    brand          = CharField()
    productTitle   = CharField()
    desc1          = CharField()
    desc2          = CharField()
    requestURL     = CharField(index=True)

    class Meta:
        database=db

class JabongData(Model):
    id = PrimaryKeyField(primary_key=True)
    product_link = CharField()
    image_320 = CharField()
    image_500      = CharField()
    image_768      = CharField()
    image_1024     = CharField()
    image_1280     = CharField()
    brand          = CharField()
    name           = CharField()
    previous_price = CharField()
    standard_price = CharField()
    discount       = CharField()
    requestURL     = CharField()
    category       = CharField()

    class Meta:
        database=db


def printClassStats():
    for tag in tags_list:
        print running_label_dict_count[tag]
        sorted_running_label_dict_count = sorted(running_label_dict_count[tag].items(), key=operator.itemgetter(1), reverse=True)
        for key in sorted_running_label_dict_count:
            print key

def get_color(product_url):
    data=JabongPageData.select(JabongPageData.id, JabongPageData.productTitle, JabongPageData.requestURL, JabongPageData.desc1).where(JabongPageData.requestURL==product_url)
    if len(data)>0:
        row = data[0]
        d = json.loads(row.desc1)
        color = d.get('Color','ColorFieldAbsent')
        return color.replace(" ","")
    else:
        return 'ColorFieldAbsent'


def get_fabric(product_url):
    data=JabongPageData.select(JabongPageData.id, JabongPageData.productTitle, JabongPageData.requestURL, JabongPageData.desc1).where(JabongPageData.requestURL==product_url)
    if len(data)>0:
        row = data[0]
        d = json.loads(row.desc1)
        fabric = d.get('Fabric','FabricFieldAbsent')
        for f in fabric_list:
            if f.lower() in fabric.lower():
                return f.lower()
    else:
        return 'FabricFieldAbsent'


def get_style(product_url):
    data=JabongPageData.select(JabongPageData.id, JabongPageData.productTitle, JabongPageData.requestURL, JabongPageData.desc1).where(JabongPageData.requestURL==product_url)
    if len(data)>0:
        row = data[0]
        d = json.loads(row.desc1)
        style = d.get('Style','StyleFieldAbsent')
        style = style.replace(" ","")
        return style
    else:
        return 'StyleFieldAbsent'


labels={
1:'tops-tees-shirts',            
2:'women-sweatshirts',     
3:'leggings-jeggings' ,        
4:'capris-shorts-skirts',      
5:'tunics',                   
6:'sweaters',                
7:'trousers-jeans' ,           
8:'dresses-jumpsuits-dresses', 
9:'winter-jackets'
}
filename='net'

try:
    os.remove(filename)
    os.remove(filename+'1')
    os.remove('train.txt')
    os.remove('test.txt')
except OSError:
    pass

def get_label(text, tag):
    label = running_label_dict[tag].get(text, -1)
    if label == -1:
        running_label_dict[tag][text] = running_index[tag]+1
        running_index[tag]+=1
    running_label_dict_count[tag][text]=running_label_dict_count[tag].get(text,0)+1
    return str(running_label_dict[tag][text])

def gen_data():
    for key, val in labels.iteritems():
        print key, val
        complete_data = JabongData.select(JabongData.id, JabongData.product_link, JabongData.image_1280, JabongData.name, JabongData.category).where(JabongData.category==val)
        result=""
        count=0; missing_count=0
        for row in complete_data:
            if row.product_link and row.image_1280:
                product_url='http://www.jabong.com'+row.product_link
                color = get_color(product_url)
                fabric = get_fabric(product_url)
                style = get_style(product_url)
                tmpname = row.image_1280.replace("/", "_")
                fname = DIRNAME+tmpname
                if os.path.isfile(fname) and color in color_list and fabric in fabric_list and style in style_list:
                    result+='dataset/'+tmpname+' '+str(key)+' '+get_label(color, 'Color')+' '+get_label(fabric, 'Fabric')+' '+get_label(style, 'Style')+'\n'
                    count+=1
                else:
                    missing_count+=1
            else:
                missing_count+=1
        print 'Count is ', count
        print 'Missing Count is ', missing_count
        with open(filename,'a+') as f:
            f.write(result)

    # Shuffle the file and do an 80-20 split
    os.system('cat '+filename+' | shuf > '+filename+'1')
    os.system("gawk 'BEGIN {srand()} {f = FILENAME (rand() <= 0.8 ? \".80\" : \".20\"); print > f}' "+filename+'1')
    os.system('mv '+filename+'1.80 train.txt')
    os.system('mv '+filename+'1.20 test.txt')


if __name__ == '__main__':
    gen_data()
    printClassStats()
