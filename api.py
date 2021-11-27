from config import Configurator
import requests


def prepare_data(data: dict):
    return {k: v for k, v in data.items() if v is not None}


class Api:
    def __init__(self):
        config = Configurator()
        self.api_host, self.password = config.api()
        self.headers = {"Authentication": self.password}

    def create_photo(self, photo_name, href_preview, href_medium, href_large,
                     photo_description=None, timestamp=None, hidden=None, photo_categories=None):
        """
        Inserts photo to database
        :param photo_name: photo name
        :param href_preview: href of preview size
        :param href_medium: href of medium size
        :param href_large: href of large size
        :param photo_description: photo description
        :param timestamp: timestamp
        :param hidden: hidden flag
        :param photo_categories: photo categories
        :return:
        """
        data = prepare_data({
            "name": photo_name, "href_preview": href_preview, "href_medium": href_medium,
            "href_large": href_large, "description": photo_description, "timestamp": timestamp,
            "hidden": hidden, "categories": photo_categories
        })
        endpoint = self.api_host + "master/create/photo"
        return requests.request("post", endpoint, headers=self.headers, data=data).text

    def modify_photo(self, photo_id, photo_name=None, href_preview=None, href_medium=None, href_large=None,
                     photo_description=None, timestamp=None, hidden=None, photo_categories=None):
        """
        Modify photo info by id. Replace old data with new data.
        :param photo_id: photo id
        :param photo_name: new photo name
        :param href_preview: new href of preview size
        :param href_medium: new href of medium size
        :param href_large: new href of large size
        :param photo_description: new photo description
        :param timestamp: new timestamp
        :param hidden: new hidden flag
        :param photo_categories: new photo categories
        :return: string of json - server response
        """
        data = prepare_data({
            "id": photo_id,
            "name": photo_name, "href_preview": href_preview, "href_medium": href_medium,
            "href_large": href_large, "description": photo_description, "timestamp": timestamp,
            "hidden": hidden, "categories": photo_categories
        })
        endpoint = self.api_host + "master/modify/photo"
        return requests.request("post", endpoint, headers=self.headers, data=data).text

    def get_photo(self, photo_id, include_hidden=False):
        """
        Get photo by id with possibility to get hidden photo
        :param photo_id: photo id
        :param include_hidden: include hidden
        :return: string of json - server response
        """
        data = prepare_data({
            "id": photo_id, "include_hidden": include_hidden
        })
        endpoint = self.api_host + "master/get/photo"
        return requests.request("post", endpoint, headers=self.headers, data=data).text

    def create_category(self, category_name, category_description=None, hidden=None, category_photos=None):
        """
        Inserts category to database
        :param category_name: category name
        :param category_description: category description
        :param hidden: hidden flag
        :param category_photos: list of photos to assign
        :return: string of json - server response
        """
        data = prepare_data({
            "name": category_name, "description": category_description, "hidden": hidden, "photos": category_photos
        })
        endpoint = self.api_host + "master/create/category"
        return requests.request("post", endpoint, headers=self.headers, data=data).text

    def modify_category(self, category_id, category_name=None, category_description=None,
                        hidden=None, category_photos=None):
        """
        Modify category info by id. Replace old data with new data.
        :param category_id: category id
        :param category_name: new category name
        :param category_description: new category description
        :param hidden: new hidden flag
        :param category_photos: list of photos to re-assign
        :return: string of json - server response
        """
        data = prepare_data({
            "id": category_id, "name": category_name, "description": category_description,
            "hidden": hidden, "photos": category_photos
        })
        endpoint = self.api_host + "master/modify/category"
        return requests.request("post", endpoint, headers=self.headers, data=data).text

    def get_category(self, category_id, include_hidden=False):
        """
        Get category by id with possibility to see get category
        :param category_id: category id
        :param include_hidden: include hidden
        :return: string of json - server response
        """
        data = prepare_data({
            "id": category_id, "include_hidden": include_hidden
        })
        endpoint = self.api_host + "master/get/category"
        return requests.request("post", endpoint, headers=self.headers, data=data).text

    def contribute_relation(self, photo_id=None, category_id=None, photo_ids_list=None, category_ids_list=None):
        """
        Create relation of photo with categories or of category with photos
        Depends on input arguments, never pass both pairs of arguments
        :param photo_id: photo_id
        :param category_id: category id
        :param photo_ids_list: photo ids list
        :param category_ids_list: category ids list
        :return: string of json - server response
        """
        data = prepare_data({
            "photo_id": photo_id, "category_id": category_id,
            "photo_ids_list": photo_ids_list, "category_ids_list": category_ids_list
        })

        if bool(photo_id) ^ bool(category_id) and bool(photo_id) ^ bool(photo_ids_list):
            endpoint = f"master/create/relation/{'category' if category_id else 'photo'}"
            return requests.request("post", endpoint, headers=self.headers, data=data).text
        else:
            raise Exception(f"Check input data correspondence. Got dict of not-None input data:\n{data}")

    def get_relation(self, photo_id=None, category_id=None):
        """
        Get categories of photo or photos of category - depends on input arguments, never pass both
        :param photo_id: photo id
        :param category_id: category id
        :return: string of json - server response
        """
        data = prepare_data({
            "photo_id": photo_id, "category_id": category_id
        })
        if bool(photo_id) ^ bool(category_id):
            endpoint = f"master/create/relation/{'category' if category_id else 'photo'}"
            return requests.request("post", endpoint, headers=self.headers, data=data).text
        else:
            raise Exception(f"Check input data correspondence. Got dict of not-None input data:\n{data}")
