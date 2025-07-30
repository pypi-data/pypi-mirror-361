import json



class Image:
    def __init__(self, dictionary):
        self.width = dictionary.get('width', None)
        self.url = dictionary.get('url', None)
        self.height = dictionary.get('height', None)

    def to_json_obj(self):
        dictionary = {}
        if self.width is not None:
            dictionary['width'] = self.width
        if self.url is not None:
            dictionary['url'] = self.url
        if self.height is not None:
            dictionary['height'] = self.height
        return dictionary


class Attribute:
    def __init__(self, dictionary):
        self.cost = dictionary.get('cost', None)
        self.quantity = dictionary.get('quantity', None)
        self.has_sku_or_barcode = dictionary.get('hasSkuOrBarcode', None)
        self.tax = dictionary.get('tax', None)
        self.message = dictionary.get('message', None)
        self.barcode = dictionary.get('barcode', None)

    def to_json_obj(self):
        dictionary = {}
        if self.cost is not None:
            dictionary['cost'] = self.cost
        if self.quantity is not None:
            dictionary['quantity'] = self.quantity
        if self.has_sku_or_barcode is not None:
            dictionary['hasSkuOrBarcode'] = self.has_sku_or_barcode
        if self.tax is not None:
            dictionary['tax'] = self.tax
        if self.message is not None:
            dictionary['message'] = self.message
        if self.barcode is not None:
            dictionary['barcode'] = self.barcode
        return dictionary


class ProductItem:
    __KEY_ADDONS = "addons"
    __KEY_DESCRIPTION = "description"
    __KEY_TYPE = "type"
    __KEY_P_CODE = "p_code"
    __KEY_PRICE = "price"
    __KEY_VENDOR = "vendor"
    __KEY_VARIANT = "variant"
    __KEY_ID = "id"
    __KEY_ATTRIBUTE = "attribute"
    __KEY_TAG = "tag"
    __KEY_SKU = "sku"
    __KEY_KEYWORD = "keyword"
    __KEY_BUNDLE = "bundle"
    __KEY_IMAGE = "image"
    __KEY_ASSIGN_COLLECTION = "assign_collection"
    __KEY_COMPARE_AT_PRICE = "compare_at_price"
    __KEY_MAIN_GROUP_ID = "main_group_id"
    __KEY_PARAMS = "params"
    __KEY_SERVER_ID = "server_id"
    __KEY_VERSION = "version"
    __KEY_GROUP_ID = "group_id"
    __KEY_NAME = "name"
    __KEY_SERVICE_PROFILE_ID = "service_profile_id"
    __KEY_CREATED_DATE = "created_date"
    __KEY_UPDATED_DATE = "updated_date"
    __KEY_CATEGORY = "category"
    __KEY_STATUS = "status"
    __KEY_OPTION = "option"
    __KEY_APP_ID = "app_id"
    __KEY_REFERENCE = "reference"
    __KEY_DATA="data"


    def __init__(self, dictionary):
        self.app_id = dictionary.get(self.__KEY_APP_ID,dictionary.get(self.__KEY_MAIN_GROUP_ID, None))
        self.reference = dictionary.get(self.__KEY_REFERENCE,None)
        self.addons = dictionary.get(self.__KEY_ADDONS, None)
        self.description = dictionary.get(self.__KEY_DESCRIPTION, None)
        self.type = dictionary.get(self.__KEY_TYPE, None)
        self.p_code = dictionary.get(self.__KEY_P_CODE, None)
        self.price = dictionary.get(self.__KEY_PRICE, None)
        self.vendor = dictionary.get(self.__KEY_VENDOR, None)
        self.variant = dictionary.get(self.__KEY_VARIANT, None)
        self.id = dictionary.get(self.__KEY_ID, None)
        self.attribute = Attribute(dictionary.get(self.__KEY_ATTRIBUTE, {}))
        self.tag = dictionary.get(self.__KEY_TAG, None)
        self.sku = dictionary.get(self.__KEY_SKU, None)
        self.keyword = dictionary.get(self.__KEY_KEYWORD, None)
        self.bundle = dictionary.get(self.__KEY_BUNDLE, None)
        self.image = [Image(img) for img in dictionary.get(self.__KEY_IMAGE, [])]
        self.assign_collection = dictionary.get(self.__KEY_ASSIGN_COLLECTION, None)
        self.compare_at_price = dictionary.get(self.__KEY_COMPARE_AT_PRICE, None)
        self.main_group_id = dictionary.get(self.__KEY_MAIN_GROUP_ID, None)
        self.params = dictionary.get(self.__KEY_PARAMS, None)
        self.server_id = dictionary.get(self.__KEY_SERVER_ID, None)
        self.version = dictionary.get(self.__KEY_VERSION, None)
        self.group_id = dictionary.get(self.__KEY_GROUP_ID, None)
        self.name = dictionary.get(self.__KEY_NAME, None)
        self.service_profile_id = dictionary.get(self.__KEY_SERVICE_PROFILE_ID, None)
        self.created_date = dictionary.get(self.__KEY_CREATED_DATE, None)
        self.updated_date = dictionary.get(self.__KEY_UPDATED_DATE, None)
        self.category = dictionary.get(self.__KEY_CATEGORY, None)
        self.status = dictionary.get(self.__KEY_STATUS, None)
        self.option = dictionary.get(self.__KEY_OPTION, None)

    def to_json_obj(self):
        dictionary = {}

        if self.addons is not None:
            dictionary[self.__KEY_ADDONS] = self.addons
        if self.description is not None:
            dictionary[self.__KEY_DESCRIPTION] = self.description
        if self.type is not None:
            dictionary[self.__KEY_TYPE] = self.type
        if self.p_code is not None:
            dictionary[self.__KEY_P_CODE] = self.p_code
        if self.price is not None:
            dictionary[self.__KEY_PRICE] = self.price
        if self.vendor is not None:
            dictionary[self.__KEY_VENDOR] = self.vendor
        if self.variant is not None:
            dictionary[self.__KEY_VARIANT] = self.variant
        if self.id is not None:
            dictionary[self.__KEY_ID] = self.id
        if self.attribute is not None:
            dictionary[self.__KEY_ATTRIBUTE] = self.attribute.to_json_obj()
        if self.tag is not None:
            dictionary[self.__KEY_TAG] = self.tag
        if self.sku is not None:
            dictionary[self.__KEY_SKU] = self.sku
        if self.keyword is not None:
            dictionary[self.__KEY_KEYWORD] = self.keyword
        if self.bundle is not None:
            dictionary[self.__KEY_BUNDLE] = self.bundle
        if self.image is not None:
            dictionary[self.__KEY_IMAGE] = [img.to_json_obj() for img in self.image]
        if self.assign_collection is not None:
            dictionary[self.__KEY_ASSIGN_COLLECTION] = self.assign_collection
        if self.compare_at_price is not None:
            dictionary[self.__KEY_COMPARE_AT_PRICE] = self.compare_at_price
        if self.main_group_id is not None:
            dictionary[self.__KEY_MAIN_GROUP_ID] = self.main_group_id
        if self.params is not None:
            dictionary[self.__KEY_PARAMS] = self.params
        if self.server_id is not None:
            dictionary[self.__KEY_SERVER_ID] = self.server_id
        if self.version is not None:
            dictionary[self.__KEY_VERSION] = self.version
        if self.group_id is not None:
            dictionary[self.__KEY_GROUP_ID] = self.group_id
        if self.name is not None:
            dictionary[self.__KEY_NAME] = self.name
        if self.service_profile_id is not None:
            dictionary[self.__KEY_SERVICE_PROFILE_ID] = self.service_profile_id
        if self.created_date is not None:
            dictionary[self.__KEY_CREATED_DATE] = self.created_date
        if self.updated_date is not None:
            dictionary[self.__KEY_UPDATED_DATE] = self.updated_date
        if self.category is not None:
            dictionary[self.__KEY_CATEGORY] = self.category
        if self.status is not None:
            dictionary[self.__KEY_STATUS] = self.status
        if self.option is not None:
            dictionary[self.__KEY_OPTION] = self.option

        return json.dumps(dictionary), dictionary
