from park import Park
import csv

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        rows = []

        with open(self.file_path, 'r', encoding='utf-8-sig', newline='') as file:
            reader = csv.DictReader(file)

            for row in reader:
                cleaned_row = self.clean(row)
                park = Park(cleaned_row)
                rows.append(park)

        return rows

    def clean(self, row):
        cleaned = {}

        for key, value in row.items():
            if value is None:
                value = ''

            value = value.strip()

            if value.startswith('http://'):
                value = value.replace('http://', 'https://', 1)
            
            cleaned[key] = value
        
        if cleaned['지역'] == '':
            address = cleaned['공원주소']
        
            for word in address.split():
                if word.endswith('구'):
                    cleaned['지역'] = word
                    break

        cleaned['area'] = self.to_number(cleaned['면적'])

        lat = cleaned['Y좌표(WGS84)']
        lng = cleaned['X좌표(WGS84)']

        if lat == '':
            lat = None
        else:
            lat = float(lat)
        
        if lng == '':
            lng = None
        else:
            lng = float(lng)

        data = {
            'id': cleaned['연번'],
            'name': cleaned['공원명'],
            'district': cleaned['지역'],
            'address': cleaned['공원주소'],
            'area_text': cleaned['면적'],
            'area': cleaned['area'],
            'open_date': cleaned['개원일'],
            'open_date_value': self.to_date_value(cleaned['개원일']),
            'department': cleaned['관리부서'],
            'phone': cleaned['전화번호'],
            'summary': cleaned['공원개요'],
            'facilities': cleaned['주요시설'],
            'plants': cleaned['주요식물'],
            'guide_map': cleaned['안내도'],
            'directions': cleaned['오시는길'],
            'notes': cleaned['이용시참고사항'],
            'image': cleaned['이미지'],
            'lat': lat,
            'lng': lng,
            'link': cleaned['바로가기']
        }

        return data

    def to_number(self, text):
        text = text.replace(',', '').strip()

        if text.startswith('총'):
            text = text[1:].strip()

        number =''

        for char in text:
            if char.isdigit() or char == '.':
                number += char
            else:
                break
        if number == '':
            return None
        
        return float(number)

    def to_date_value(self, text):
        text = text.strip().replace(' ', '.')

        if text == '':
            return None
        
        date = []

        for part in text.split('.'):
            if part != '':
                date.append(int(part))

        return date

if __name__ == '__main__':
    loader = DataLoader('parks.csv')
    parks = loader.load()

    print('전체 공원 수:', len(parks))
    print('첫 번째 공원:', parks[0].name)
    print('위치:', parks[0].get_location())