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


# Used to print some sample data
def JabongPageDataSample():
    data=JabongPageData.select(JabongPageData.id, JabongPageData.productTitle, JabongPageData.requestURL, JabongPageData.desc1).limit(5)
    for row in data:
        d = json.loads(row.desc1)
        print d['Color']
        # print row.id, row.requestURL, row.productTitle, row.desc1

# Prints color stats for JabongPageData (count of each color in descending order)
def printColorStats():
    color_dict = {}
    data=JabongPageData.select(JabongPageData.id, JabongPageData.productTitle, JabongPageData.requestURL, JabongPageData.desc1)
    for row in data:
        d = json.loads(row.desc1)
        key = d.get('Color','ColorFieldAbsent')
        color_dict[key] = color_dict.get(key, 0)+1
    sorted_color_dict = sorted(color_dict.items(), key=operator.itemgetter(1), reverse=True)
    for key in sorted_color_dict:
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
                tmpname = row.image_1280.replace("/", "_")
                fname = DIRNAME+tmpname
                if os.path.isfile(fname):
                    result+='dataset/'+tmpname+' '+str(key)+str(color)+'\n'
                    count+=1
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
