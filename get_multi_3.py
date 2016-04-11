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
        print 'Data for tag ', tag
        print running_label_dict[tag]
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



# Data for tag  Color
# {u'Pink': 7, u'Blue': 9, u'Multi': 4, u'Brown': 16, u'Purple': 3, u'Maroon': 12, u'Grey': 1, u'Yellow': 5, u'NavyBlue': 6, u'Black': 2, u'Beige': 8, u'Orange': 10, u'Green': 14, u'OffWhite': 11, u'White': 15, u'Red': 13}
# {u'Pink': 3846, u'Blue': 8061, u'Multi': 6218, u'Brown': 1142, u'Purple': 1359, u'Maroon': 1067, u'Grey': 2636, u'Yellow': 1933, u'NavyBlue': 2568, u'Black': 10250, u'Beige': 1251, u'Orange': 1577, u'Green': 2836, u'OffWhite': 1641, u'White': 4327, u'Red': 2820}
# (u'Black', 10250)
# (u'Blue', 8061)
# (u'Multi', 6218)
# (u'White', 4327)
# (u'Pink', 3846)
# (u'Green', 2836)
# (u'Red', 2820)
# (u'Grey', 2636)
# (u'NavyBlue', 2568)
# (u'Yellow', 1933)
# (u'OffWhite', 1641)
# (u'Orange', 1577)
# (u'Purple', 1359)
# (u'Beige', 1251)
# (u'Brown', 1142)
# (u'Maroon', 1067)
# Data for tag  Fabric
# {'polyester': 2, 'wool': 19, 'crepe': 8, 'chiffon': 10, 'leather': 20, 'blended': 13, 'denim': 18, 'viscose': 7, 'fleece': 14, 'acrylic': 17, 'linen': 9, 'satin': 15, 'modal': 12, 'rayon': 4, 'net': 6, 'nylon': 16, 'knit': 11, 'georgette': 3, 'jersey': 5, 'cotton': 1}
# {'polyester': 13582, 'wool': 654, 'crepe': 2506, 'chiffon': 561, 'leather': 125, 'blended': 1861, 'denim': 421, 'viscose': 3869, 'fleece': 298, 'acrylic': 731, 'linen': 311, 'satin': 206, 'modal': 255, 'rayon': 1488, 'net': 359, 'nylon': 444, 'knit': 265, 'georgette': 2972, 'jersey': 207, 'cotton': 22417}
# ('cotton', 22417)
# ('polyester', 13582)
# ('viscose', 3869)
# ('georgette', 2972)
# ('crepe', 2506)
# ('blended', 1861)
# ('rayon', 1488)
# ('acrylic', 731)
# ('wool', 654)
# ('chiffon', 561)
# ('nylon', 444)
# ('denim', 421)
# ('net', 359)
# ('linen', 311)
# ('fleece', 298)
# ('knit', 265)
# ('modal', 255)
# ('jersey', 207)
# ('satin', 206)
# ('leather', 125)
# Data for tag  Style
# {u'Graphic': 8, u'Checked': 6, u'Solid': 4, u'Washed': 7, u'Embroidered': 3, u'Printed': 1, u'Striped': 5, u'Embellished': 2}
# {u'Graphic': 502, u'Checked': 624, u'Solid': 24262, u'Washed': 546, u'Embroidered': 2849, u'Printed': 21687, u'Striped': 1648, u'Embellished': 1414}
# (u'Solid', 24262)
# (u'Printed', 21687)
# (u'Embroidered', 2849)
# (u'Striped', 1648)
# (u'Embellished', 1414)
# (u'Checked', 624)
# (u'Washed', 546)
# (u'Graphic', 502)
