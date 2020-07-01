from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from pymongo import MongoClient


client = MongoClient('localhost',port=27017)

db = client['senado']

# Nombre de la colección que quieres crear

col_semblanzas = db['semblanzas']
col_personal = db['personal']
col_comisiones = db['comisiones']
col_intervenciones = db['intervenciones']
col_votaciones = db['votaciones']
col_asistencias = db['asistencias']


class Senado(CrawlSpider):
    name = 'perfiles_senadores'
    custom_settings = {
    'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36'
    }

    allowed_domains = ['senado.gob.mx']
    start_urls = ['https://www.senado.gob.mx/64/senadoras']
    # Seguro puedes agregar a ambos como start_urls... pero lo hice separado just cause
    # start_urls = ['https://www.senado.gob.mx/64/senadores']
    # start_urls = ['https://www.senado.gob.mx/64/senador/1069']
    download_delay = 1

    rules = (
        # Recuerda que lo estás poniendo solo para los de Morena, despues debes ajustar el XPath para que agarre de todos
        Rule(
            LinkExtractor(
                allow=r'/senador/',
                restrict_xpaths=['//div[@class="container-fluid bg-content main"]//div[@class="col-sm-4"]//h3/strong'] # Evita obtener URLs repetidas reduciendo el espectro de busqueda de las URLs a solamente un contenedor especifico dentro de un XPATH
        ), follow=True, callback='parse_senador'),
        Rule(
            LinkExtractor(
                allow=r'/iniciativas',
                restrict_xpaths=['//div[@class="panel-footer"]/div[2]'] # Evita obtener URLs repetidas reduciendo el espectro de busqueda de las URLs a solamente un contenedor especifico dentro de un XPATH
        ), follow=True, callback='parse_iniciativas'),
        Rule(
            LinkExtractor(
                allow=r'/asistencias/',
                restrict_xpaths=['//div[@class="panel-footer"]/div[1]'] # Evita obtener URLs repetidas reduciendo el espectro de busqueda de las URLs a solamente un contenedor especifico dentro de un XPATH
        ), follow=True, callback='parse_asistencias'),
        Rule(
            LinkExtractor(
                allow=r'/votaciones/',
                restrict_xpaths=['//div[@class="panel-footer"]/div[1]'] # Evita obtener URLs repetidas reduciendo el espectro de busqueda de las URLs a solamente un contenedor especifico dentro de un XPATH
        ), follow=True, callback='parse_votaciones'),
        Rule(
            LinkExtractor(
                allow=r'/intervenciones/',
                restrict_xpaths=['//div[@class="text-center"]/a[2]'] # Evita obtener URLs repetidas reduciendo el espectro de busqueda de las URLs a solamente un contenedor especifico dentro de un XPATH
        ), follow=True, callback='parse_intervenciones'),
    )

    def parse_senador(self, response):
        sel = Selector(response)
        clave_senador = response.url.split('/')[-1]

        # Obtengamos los datos particulares del senador
        partido = sel.xpath('string(//table[@class="table table-condensed"]//strong)').get()
        estado = sel.xpath('//div[@class="col-sm-9"][1]//div[@class="col-sm-12"][1]/img/following-sibling::text()[1]').get()
        eleccion = sel.xpath('//div[@class="col-sm-9"][1]//div[@class="col-sm-12"][1]/br[1]/following-sibling::text()[1]').get()
        col_personal.insert_one({
                'clave_senador':clave_senador,
                'partido':partido,
                'estado': estado,
                'eleccion': eleccion
        })

        # Ahora populamos la colección de semblanzas
        semblanzas = sel.xpath('//div[@id="semblanzaCurricular"]//p')
        for semblanza in semblanzas:
            trayectoria = semblanza.xpath('./strong/text()').get()
            detalle_trayectoria = semblanza.xpath('./following-sibling::ul[1]//text()').extract()
            col_semblanzas.insert_one({
                'clave_senador':clave_senador,
                'trayectoria':trayectoria,
                'detalle_trayectoria': detalle_trayectoria
            })

        # Ahora populamos la colección de comisiones
        comisiones = sel.xpath('//div[@class="col-sm-9"][1]//div[@class="col-sm-12"][last()]//p')
        for comision in comisiones:
            cargo_comision = comision.xpath('./strong/text()').get()
            comisiones = comision.xpath('./following-sibling::ul[1]//text()').extract()
            col_comisiones.insert_one({
                'clave_senador':clave_senador,
                'cargo_comision':cargo_comision,
                'comisiones': comisiones
            })

    def parse_intervenciones(self,response):
        sel = Selector(response)
        clave_senador = response.url.split('/')[-1]
        tot_intervenciones = sel.xpath('count(//div[@class="panel panel-default"]/div[@class="panel-body"])').get()
        col_intervenciones.insert_one({
            'clave_senador':clave_senador,
            'tot_intervenciones': tot_intervenciones
        })

    def parse_votaciones(self,response):
        sel = Selector(response)
        clave_senador = response.url.split('/')[-1]
        votaciones_del_pleno = sel.xpath('//div[@class="col-sm-6 text-center"][2]/p[1]/text()').get()
        votaciones_participa = sel.xpath('//div[@class="col-sm-6 text-center"][2]/p[2]/text()').get()
        votaciones_ausente = sel.xpath('//div[@class="col-sm-6 text-center"][2]/p[last()]/text()').get()
        col_votaciones.insert_one({
                'clave_senador':clave_senador,
                'votaciones_del_pleno':votaciones_del_pleno,
                'votaciones_participa':votaciones_participa,
                'votaciones_ausente': votaciones_ausente
            })

    def parse_asistencias(self,response):
        sel = Selector(response)
        clave_senador = response.url.split('/')[-1]
        tot_registros = sel.xpath('//div[@class="col-sm-3 text-center"][2]/p[1]/text()').get()
        asistencias = sel.xpath('//div[@class="col-sm-3 text-center"][2]/p[2]/text()').get()
        ausencias = sel.xpath('//div[@class="col-sm-3 text-center"][2]/p[3]/text()').get()
        justificadas = sel.xpath('//div[@class="col-sm-3 text-center"][2]/p[last()]/text()').get()
        col_asistencias.insert_one({
                'clave_senador':clave_senador,
                'tot_registros':tot_registros,
                'asistencias':asistencias,
                'ausencias': ausencias,
                'justificadas': justificadas,
            })

    #Tengo que ver como solucionar el Mixed Content Scrapy
    # def parse_iniciativas(self, response):
    #     item = ItemLoader(Iniciativa(),response)
    #     clave_senador = response.url.split('/')[-2]
    #     item.add_value('clave_senador',clave_senador)
    #     item.add_xpath('tot_promovente', 'count(//div[@class="panel-group"][2]//div[@class="panel panel-default"]//p[@class="text-right"]/strong[contains(text(),"Promovente")])')
    #     item.add_xpath('tot_suscrito','count(//div[@class="panel-group"][2]//div[@class="panel panel-default"]//p[@class="text-right"]/strong[contains(text(),"Suscrito(a)")])')
    #     yield item.load_item()
