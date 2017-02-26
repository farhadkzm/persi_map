import scrapy
import json
from datetime import datetime


class DetailSpider(scrapy.Spider):
    name = "healthpages.wiki_detail"
    data_path = '/code/doctors/healthpages/healthpages'

    def start_requests(self):
        links = json.load(open("{}/doctors_link.json".format(self.data_path), 'r'))
        for link in links:
            yield scrapy.Request(url=link["link"], callback=self.parse)

    def parse(self, response):
        language = self.extract_language(response)

        if language is not None:
            text = response.body.decode(response.encoding).lower()
            if 'farsi' in text or 'persian' in text:
                for item in self.generate_output('lang', response):
                    yield item
            return
            # else:
            #     first_name = self.extract_firstname(response)
            #
            #     if first_name is not None and len(self.lines.intersection(first_name.lower().split(' '))):
            #         yield self.generate_output('name', response)

    def generate_output(self, type, response):
        items = []
        name = self.extract_firstname(response) + ' ' + self.extract_familyname(response)
        occ = self.extract_occupation(response)
        gender = self.extract_gender(response)
        addresses = self.extract_addresses(response)
        for address in addresses:
            created_date = datetime.utcnow().isoformat('T') + 'Z'
            items.append({
                'type': 'doctor',
                'src': response.url,
                'name': name,
                'detail': {

                    'occupation': occ,
                    'gender': gender,
                },

                'location': address,
                'creation': created_date,
                'updated': created_date,
            })
        return items

    def extract_language(self, response):
        return response.xpath('//dt[text()="Languages Spoken"]').extract_first()

    def extract_firstname(self, response):
        return response.xpath('//*[@itemprop="givenName"]/@content').extract_first()

    def extract_familyname(self, response):
        return response.xpath('//*[@itemprop="familyName"]/@content').extract_first()

    def extract_occupation(self, response):
        return response.xpath('//*[@itemprop="jobTitle"]/a/text()').extract_first()

    def extract_gender(self, response):
        return response.xpath('//*[@itemprop="gender"]/text()').extract_first()

    def extract_addresses(self, response):
        addresses = []
        for item in response.xpath('//div[@class="groupitem"]'):
            address_line = ""
            for address in item.xpath('.//*[@itemprop="address"]//span/descendant-or-self::*/text()'):
                address_line += address.extract() + " "

            latitude = float(
                item.xpath('.//span[@itemprop="geo"]//meta[@itemprop="latitude"]/@content').extract_first(), )
            longitude = float(
                item.xpath('.//span[@itemprop="geo"]//meta[@itemprop="longitude"]/@content').extract_first(), )
            addresses.append({
                'phone': item.xpath('.//*[@itemprop="telephone"]/@content').extract_first(),
                'address': address_line.strip(),
                'geo_set': {
                    "lat": latitude,
                    "lon": longitude
                },
                'clinic_name': item.xpath('.//span[@itemprop="name"]//a/text()').extract_first()
            })

        return addresses
